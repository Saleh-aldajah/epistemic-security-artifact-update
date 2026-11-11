"""
mock_model.py — a scripted OpenAI-compatible client for offline tests of the
whole admission path. The script sees the OpenAI-format conversation and
returns either tool calls or text. Deterministic; no network.
"""
from __future__ import annotations

import json
import re
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

from openai.types.chat import ChatCompletion
from openai.types.chat.chat_completion import Choice
from openai.types.chat.chat_completion_message import ChatCompletionMessage
from openai.types.chat.chat_completion_message_tool_call import ChatCompletionMessageToolCall, Function

ToolCalls = List[Tuple[str, Dict[str, Any]]]
Script = Callable[[List[Dict[str, Any]], float], Tuple[str, Any]]   # -> ("tool", calls) | ("text", str)


class _Completions:
    def __init__(self, script: Script, log: List[Dict[str, Any]]):
        self.script = script
        self.log = log

    def create(self, **kw):
        messages = kw["messages"]
        temperature = kw.get("temperature")
        self.log.append({"temperature": temperature, "seed": kw.get("seed"), "n_messages": len(messages)})
        kind, payload = self.script(messages, temperature)
        if kind == "tool":
            tcs = [ChatCompletionMessageToolCall(id=f"call_{len(self.log)}_{i}", type="function",
                                                 function=Function(name=n, arguments=json.dumps(a)))
                   for i, (n, a) in enumerate(payload)]
            msg = ChatCompletionMessage(role="assistant", content=None, tool_calls=tcs)
        else:
            msg = ChatCompletionMessage(role="assistant", content=str(payload), tool_calls=None)
        return ChatCompletion(id="mock", created=0, model=kw.get("model", "mock"), object="chat.completion",
                              choices=[Choice(index=0, finish_reason="stop", message=msg)])


class _Chat:
    def __init__(self, script, log):
        self.completions = _Completions(script, log)


class MockClient:
    """`MockClient(script)` quacks like `openai.OpenAI()` for chat completions."""
    def __init__(self, script: Script):
        self.calls: List[Dict[str, Any]] = []
        self.chat = _Chat(script, self.calls)


# ------------------------------------------------------------ helpers for scripts
def last_tool_results(messages: Sequence[Dict[str, Any]]) -> List[str]:
    """Text of the tool-result messages since the last assistant turn with tool calls."""
    out = []
    for m in reversed(messages):
        if m.get("role") == "tool":
            c = m.get("content")
            out.append(c if isinstance(c, str) else "".join(b.get("text", "") for b in (c or []) if isinstance(b, dict)))
        elif m.get("role") == "assistant":
            break
    return list(reversed(out))


def all_tool_results(messages: Sequence[Dict[str, Any]]) -> List[str]:
    out = []
    for m in messages:
        if m.get("role") == "tool":
            c = m.get("content")
            out.append(c if isinstance(c, str) else "".join(b.get("text", "") for b in (c or []) if isinstance(b, dict)))
    return out


def tools_called(messages: Sequence[Dict[str, Any]]) -> List[str]:
    out = []
    for m in messages:
        if m.get("role") == "assistant" and m.get("tool_calls"):
            for tc in m["tool_calls"]:
                out.append(tc["function"]["name"])
    return out


def blocked_notices(messages: Sequence[Dict[str, Any]]) -> int:
    n = 0
    for m in messages:
        if m.get("role") == "tool":
            c = m.get("content")
            txt = c if isinstance(c, str) else "".join(b.get("text", "") for b in (c or []) if isinstance(b, dict))
            if "Blocked by policy" in txt:
                n += 1
    return n


_INJ = re.compile(r"email the text '([^']*)' to '([^']*)' using '([^']*)' as subject", re.I | re.S)


def _unwrap_yaml(t: str) -> str:
    t = re.sub(r"\\\n\s*\\ ?", " ", t)   # YAML folded-line continuation: backslash NL indent backslash
    t = re.sub(r"\\n", " ", t)
    return re.sub(r"\s+", " ", t)


def find_injection_email(texts: Sequence[str]) -> Optional[Tuple[str, str, str]]:
    for t in texts:
        m = _INJ.search(_unwrap_yaml(t))
        if m:
            return m.group(1), m.group(2), m.group(3)
    return None
