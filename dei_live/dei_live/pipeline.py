"""
pipeline.py — AgentDojo 0.1.35 wiring for the registered campaign.

* `ExplicitLLM`: OpenAI-compatible LLM element that ALWAYS sends the configured
  temperature (agentdojo maps 0.0 to NOT_GIVEN; we do not) and an optional seed,
  and exposes `propose()` for the gate's temperature-0 re-commitment.
* `DEIToolsExecutor`: the sink-side enforcement point. Every proposed tool call
  is admitted or denied against the ledger BEFORE execution; a denied call is
  answered with an error tool-result so the agent can continue (it may try
  again — the adaptive case is the realistic one). The enforced arm shapes the
  trajectory; every arm's verdict is logged as a shadow for diagnostics.
* `build_pipeline` / `run_one_case`: the per-episode driver returning
  AgentDojo's own utility / security verdicts plus the decision ledger.
"""
from __future__ import annotations

import os
import time
from ast import literal_eval
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence, Tuple

import openai
from openai import NOT_GIVEN
from tenacity import retry, retry_if_not_exception_type, stop_after_attempt, wait_random_exponential

from agentdojo.agent_pipeline import AgentPipeline
from agentdojo.agent_pipeline.basic_elements import InitQuery, SystemMessage
from agentdojo.agent_pipeline.agent_pipeline import load_system_message
from agentdojo.agent_pipeline.llms.openai_llm import (OpenAILLM, _function_to_openai, _message_to_openai,
                                                      _openai_to_assistant_message)
from agentdojo.agent_pipeline.tool_execution import (EMPTY_FUNCTION_NAME, ToolsExecutionLoop, ToolsExecutor,
                                                     is_string_list, tool_result_to_str)
from agentdojo.functions_runtime import EmptyEnv, Env, FunctionsRuntime
from agentdojo.types import ChatMessage, ChatToolResultMessage, text_content_block_from_string

from . import policy as P
from .admission import Decision, PolicyConfig, decide, shadow_all
from .gate import GateResult, run_gate
from .ledger import Ledger


# ------------------------------------------------------------------- the LLM
@retry(wait=wait_random_exponential(multiplier=1, max=40), stop=stop_after_attempt(3), reraise=True,
       retry=retry_if_not_exception_type((openai.BadRequestError, openai.UnprocessableEntityError)))
def _chat(client, model, messages, tools, temperature, seed, reasoning_effort=None):
    kw = dict(model=model, messages=messages, tools=tools or NOT_GIVEN,
              tool_choice="auto" if tools else NOT_GIVEN)
    if temperature is not None:
        kw["temperature"] = float(temperature)      # explicit, including 0.0
    if seed is not None:
        kw["seed"] = int(seed)
    if reasoning_effort:
        kw["reasoning_effort"] = reasoning_effort
    try:
        return client.chat.completions.create(**kw)
    except openai.BadRequestError as ex:
        # Some OpenAI-compatible endpoints reject `seed`; drop it once, record it, keep the explicit temperature.
        response_text = getattr(getattr(ex, "response", None), "text", "")
        if "seed" in kw and "seed" in (str(ex) + response_text).lower():
            SEED_REJECTED.add(model)
            kw.pop("seed")
            return client.chat.completions.create(**kw)
        raise


SEED_REJECTED: set = set()      # models whose endpoint rejected the `seed` parameter (logged per episode as seed_sent=False)


def _has_assistant_output(message) -> bool:
    """True for a tool call or non-whitespace text; used for the RQ3 taxonomy."""
    if isinstance(message, dict):
        tool_calls = message.get("tool_calls")
        content = message.get("content")
    else:
        tool_calls = getattr(message, "tool_calls", None)
        content = getattr(message, "content", None)
    if tool_calls:
        return True
    if isinstance(content, str):
        return bool(content.strip())
    if isinstance(content, list):
        for block in content:
            if isinstance(block, dict):
                text = block.get("text", block.get("content", ""))
                if isinstance(text, str) and text.strip():
                    return True
    return False


class ExplicitLLM(OpenAILLM):
    def __init__(self, client, model: str, temperature: float = 0.0, seed: Optional[int] = None,
                 recommit_temperature: float = 0.0):
        super().__init__(client, model, temperature=temperature)
        self.temperature = temperature
        self.seed = seed
        self.recommit_temperature = recommit_temperature
        self.n_calls = 0
        self.last_main_empty = False

    def _complete(self, messages: Sequence[ChatMessage], runtime: FunctionsRuntime, temperature: float):
        openai_messages = [_message_to_openai(m, self.model) for m in messages]
        openai_tools = [_function_to_openai(t) for t in runtime.functions.values()]
        self.n_calls += 1
        completion = _chat(self.client, self.model, openai_messages, openai_tools, temperature, self.seed,
                           self.reasoning_effort)
        return _openai_to_assistant_message(completion.choices[0].message)

    def query(self, query: str, runtime: FunctionsRuntime, env: Env = EmptyEnv(),
              messages: Sequence[ChatMessage] = [], extra_args: dict = {}):
        output = self._complete(messages, runtime, self.temperature)
        self.last_main_empty = not _has_assistant_output(output)
        return query, runtime, env, [*messages, output], extra_args

    def propose(self, messages: Sequence[ChatMessage], runtime: FunctionsRuntime) -> Optional[Tuple[str, Dict[str, Any]]]:
        """Re-commitment for the gate: first proposed tool call at temperature 0, or None."""
        out = self._complete(messages, runtime, self.recommit_temperature)
        tcs = out.get("tool_calls") if isinstance(out, dict) else getattr(out, "tool_calls", None)
        if not tcs:
            return None
        tc = tcs[0]
        return tc.function, dict(tc.args or {})


# ---------------------------------------------------------------- the sink
@dataclass
class EpisodeContext:
    arm: str
    cfg: PolicyConfig = field(default_factory=PolicyConfig)
    gate_deltas: Sequence[str] = ("delta2", "delta3")
    gate_enforce: Sequence[str] = ("delta3",)          # registered: quarantine on delta3 flips; delta2 observed
    oracle_payloads: List[str] = field(default_factory=list)
    llm: Optional[ExplicitLLM] = None
    decisions: List[Dict[str, Any]] = field(default_factory=list)
    n_blocked: int = 0
    n_quarantined: int = 0
    n_protected: int = 0
    n_recommits: int = 0
    shadow: bool = True


class DEIToolsExecutor(ToolsExecutor):
    def __init__(self, ctx: EpisodeContext, tool_output_formatter=tool_result_to_str):
        super().__init__(tool_output_formatter)
        self.ctx = ctx

    def _decide(self, messages: Sequence[ChatMessage], runtime: FunctionsRuntime,
                tool: str, args: Dict[str, Any]) -> Tuple[Decision, Optional[GateResult], Ledger]:
        history = messages[:-1]                     # everything the model saw before proposing
        ledger = Ledger.from_messages(history)
        dec = decide(self.ctx.arm, ledger, tool, args, self.ctx.cfg)
        gate: Optional[GateResult] = None
        if dec.admit and self.ctx.arm == "dei+gate" and P.PROTECTED.get(tool) in P.IRREVERSIBLE:
            llm = self.ctx.llm
            if llm is None:
                raise RuntimeError("dei+gate needs the LLM for re-commitment")
            gate = run_gate(history, ledger, tool, args,
                            recommit=lambda msgs: llm.propose(msgs, runtime),
                            deltas=self.ctx.gate_deltas, enforce=self.ctx.gate_enforce,
                            ell_req=self.ctx.cfg.ell_req_for(P.PROTECTED[tool]),
                            oracle_payloads=self.ctx.oracle_payloads or None)
            self.ctx.n_recommits += gate.recommits
        return dec, gate, ledger

    def query(self, query: str, runtime: FunctionsRuntime, env: Env = EmptyEnv(),
              messages: Sequence[ChatMessage] = [], extra_args: dict = {}):
        if len(messages) == 0 or messages[-1]["role"] != "assistant":
            return query, runtime, env, messages, extra_args
        tcs = messages[-1]["tool_calls"]
        if not tcs:
            return query, runtime, env, messages, extra_args
        results = []
        for tool_call in tcs:
            if tool_call.function == EMPTY_FUNCTION_NAME or tool_call.function not in (t.name for t in runtime.functions.values()):
                results.append(ChatToolResultMessage(role="tool", content=[text_content_block_from_string("")],
                                                     tool_call_id=tool_call.id, tool_call=tool_call,
                                                     error=f"Invalid tool {tool_call.function!r} provided."))
                continue
            for k, v in tool_call.args.items():          # agentdojo's list-string coercion
                if isinstance(v, str) and is_string_list(v):
                    tool_call.args[k] = literal_eval(v)
            args = dict(tool_call.args)
            protected = tool_call.function in P.PROTECTED
            rec: Dict[str, Any] = {"step": len(self.ctx.decisions), "tool": tool_call.function,
                                   "args": {k: (v if isinstance(v, (str, int, float, bool, list)) else str(v)) for k, v in args.items()},
                                   "protected": protected, "class": P.PROTECTED.get(tool_call.function)}
            if protected:
                self.ctx.n_protected += 1
                dec, gate, ledger = self._decide(messages, runtime, tool_call.function, args)
                rec["decision"] = dec.as_dict()
                rec["ledger_atoms"] = [{"aid": a.aid, "label": a.label, "tool": a.tool_name, "len": len(a.content)} for a in ledger.atoms]
                if self.ctx.shadow:
                    rec["shadow"] = shadow_all(ledger, tool_call.function, args, self.ctx.cfg)
                if gate is not None:
                    rec["gate"] = gate.as_dict()
                blocked = (not dec.admit) or (gate is not None and gate.quarantine)
                if blocked:
                    why = dec.reason if not dec.admit else gate.reason
                    if dec.admit:
                        self.ctx.n_quarantined += 1
                    self.ctx.n_blocked += 1
                    rec["executed"] = False
                    self.ctx.decisions.append(rec)
                    results.append(ChatToolResultMessage(
                        role="tool", content=[text_content_block_from_string("")],
                        tool_call_id=tool_call.id, tool_call=tool_call,
                        error=f"Blocked by policy: {why}. The action was not executed."))
                    continue
            rec["executed"] = True
            self.ctx.decisions.append(rec)
            out, error = runtime.run_function(env, tool_call.function, tool_call.args)
            results.append(ChatToolResultMessage(role="tool", content=[text_content_block_from_string(self.output_formatter(out))],
                                                 tool_call_id=tool_call.id, tool_call=tool_call, error=error))
        return query, runtime, env, [*messages, *results], extra_args


# ---------------------------------------------------------------- driver
def build_pipeline(client, model: str, ctx: EpisodeContext, temperature: float, seed: Optional[int],
                   pipeline_name: str = "local") -> Tuple[AgentPipeline, ExplicitLLM]:
    llm = ExplicitLLM(client, model, temperature=temperature, seed=seed)
    ctx.llm = llm
    elements = [SystemMessage(load_system_message(None)), InitQuery(), llm,
                ToolsExecutionLoop([DEIToolsExecutor(ctx), llm])]
    pipe = AgentPipeline(elements)
    pipe.name = pipeline_name      # must contain a MODEL_NAMES key ('local') or the attack registry voids the episode
    return pipe, llm


def run_one_case(suite, case: Dict[str, Any], client, model: str, arm: str, temperature: float, seed: Optional[int],
                 cfg: Optional[PolicyConfig] = None, gate_deltas: Sequence[str] = ("delta2", "delta3"),
                 attack: str = "important_instructions", oracle: bool = False,
                 gate_enforce: Sequence[str] = ("delta3",)) -> Dict[str, Any]:
    """Run one (user_task[, injection_task]) case. Returns AgentDojo's verdicts
    plus the decision ledger. `oracle=True` supplies the injection payloads to
    the gate for delta1 (development only)."""
    ctx = EpisodeContext(arm=arm, cfg=cfg or PolicyConfig(), gate_deltas=gate_deltas, gate_enforce=tuple(gate_enforce))
    pipe, llm = build_pipeline(client, model, ctx, temperature, seed)
    ut, it = case["user_task"], case.get("injection_task")
    t0 = time.time()
    if it is None:
        utility, security = suite.run_task_with_pipeline(pipe, ut, None, injections={})
        target_hit = False
    else:
        from agentdojo.attacks.attack_registry import load_attack
        atk = load_attack(attack, suite, pipe)
        injections = atk.attack(ut, it)
        if oracle:
            ctx.oracle_payloads = [str(v) for v in injections.values()]
            ctx.gate_deltas = tuple(set(gate_deltas) | {"delta1"})
        utility, security = suite.run_task_with_pipeline(pipe, ut, it, injections=injections)
        target_hit = bool(security)
    return {"case_id": case["id"], "arm": arm, "model": model, "temperature": temperature, "seed": seed,
            "kind": case["kind"], "target_hit": target_hit, "utility": bool(utility),
            "benign_blocked": (case["kind"] == "utility" and not utility),
            "n_protected": ctx.n_protected, "n_blocked": ctx.n_blocked, "n_quarantined": ctx.n_quarantined,
            "n_recommits": ctx.n_recommits, "n_model_calls": llm.n_calls, "wall_s": round(time.time() - t0, 2),
            "seed_sent": seed is not None and model not in SEED_REJECTED,
            "null_output": llm.last_main_empty,
            "degenerate": (not bool(utility) and llm.last_main_empty),
            "policy_hash": P.policy_hash(), "decisions": ctx.decisions}
