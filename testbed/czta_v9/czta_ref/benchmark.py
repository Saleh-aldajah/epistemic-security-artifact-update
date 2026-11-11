"""Run the CZTA reference benchmark and emit submission artifacts."""
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
import statistics
from typing import Dict, Iterable, List, Mapping, Sequence, Tuple

from .pipeline import BaselinePipeline, ControlConfig, CZTAPipeline, Outcome
from .rla import private_key_from_seed
from .scenario import Episode, generate_suite


def wilson(successes: int, n: int, z: float = 1.96) -> Tuple[float, float]:
    if n == 0:
        return (float("nan"), float("nan"))
    p = successes / n
    denom = 1 + z * z / n
    center = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt((p * (1 - p) + z * z / (4 * n)) / n) / denom
    return (max(0.0, center - half), min(1.0, center + half))


def percentile(values: Sequence[float], q: float) -> float:
    if not values:
        return float("nan")
    ordered = sorted(values)
    pos = (len(ordered) - 1) * q
    lo = math.floor(pos)
    hi = math.ceil(pos)
    if lo == hi:
        return ordered[lo]
    return ordered[lo] * (hi - pos) + ordered[hi] * (pos - lo)


def outcome_row(system: str, out: Outcome) -> Dict[str, object]:
    return {
        "system": system,
        "episode_id": out.episode_id,
        "attack_type": out.attack_type,
        "adversarial": out.adversarial,
        "allowed": out.allowed,
        "unsafe_action": out.unsafe_action,
        "correct_outcome": out.correct_outcome,
        "detected": out.detected,
        "policy_decision": out.policy_decision,
        "warning_count": len(out.warnings),
        "warnings": "|".join(out.warnings),
        "selected_source_ids": "|".join(out.selected_source_ids),
        "lineage_completeness": round(out.lineage_completeness, 6),
        "replay_success": out.replay_success,
        "signature_valid": out.signature_valid,
        "calibrated_confidence": round(out.calibrated_confidence, 6),
        "latency_ms": round(out.latency_ms, 6),
    }


def summarize(system: str, outcomes: Sequence[Outcome]) -> Dict[str, object]:
    adversarial = [o for o in outcomes if o.adversarial]
    benign = [o for o in outcomes if not o.adversarial]
    attacks = sum(o.unsafe_action for o in adversarial)
    benign_allowed = sum(o.allowed and not o.unsafe_action for o in benign)
    detected = sum(o.detected for o in adversarial)
    low, high = wilson(attacks, len(adversarial))
    b_low, b_high = wilson(benign_allowed, len(benign))
    latencies = [o.latency_ms for o in outcomes]
    return {
        "system": system,
        "episodes": len(outcomes),
        "adversarial_episodes": len(adversarial),
        "benign_episodes": len(benign),
        "attack_success_count": attacks,
        "attack_success_rate": attacks / len(adversarial),
        "attack_success_ci95_low": low,
        "attack_success_ci95_high": high,
        "benign_acceptance_count": benign_allowed,
        "benign_acceptance_rate": benign_allowed / len(benign),
        "benign_acceptance_ci95_low": b_low,
        "benign_acceptance_ci95_high": b_high,
        "adversarial_detection_rate": detected / len(adversarial),
        "mean_lineage_completeness": statistics.fmean(o.lineage_completeness for o in outcomes),
        "replay_success_rate": statistics.fmean(1.0 if o.replay_success else 0.0 for o in outcomes),
        "signature_valid_rate": statistics.fmean(1.0 if o.signature_valid else 0.0 for o in outcomes),
        "median_latency_ms": statistics.median(latencies),
        "p95_latency_ms": percentile(latencies, 0.95),
    }


def by_attack(system: str, outcomes: Sequence[Outcome]) -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []
    for attack in sorted({o.attack_type for o in outcomes}):
        group = [o for o in outcomes if o.attack_type == attack]
        successes = sum(o.unsafe_action for o in group)
        allowed = sum(o.allowed for o in group)
        detected = sum(o.detected for o in group)
        low, high = wilson(successes, len(group))
        rows.append(
            {
                "system": system,
                "attack_type": attack,
                "episodes": len(group),
                "unsafe_actions": successes,
                "attack_success_rate": successes / len(group),
                "ci95_low": low,
                "ci95_high": high,
                "allowed_rate": allowed / len(group),
                "detection_rate": detected / len(group),
            }
        )
    return rows


def write_csv(path: Path, rows: Sequence[Mapping[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        raise ValueError("No rows to write")
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def run(out_dir: Path, seed: int, attacks_per_type: int, benign: int) -> Dict[str, object]:
    episodes = generate_suite(seed=seed, attacks_per_type=attacks_per_type, benign=benign)
    baseline = BaselinePipeline()
    benchmark_key = private_key_from_seed(seed)
    fixed_timestamp = lambda _episode: "2026-07-11T00:00:00Z"
    czta = CZTAPipeline(
        private_key=benchmark_key,
        timestamp_provider=fixed_timestamp,
    )
    baseline_out = [baseline.process(ep) for ep in episodes]
    czta_out = [czta.process(ep) for ep in episodes]

    outcome_rows = [outcome_row("baseline", o) for o in baseline_out] + [outcome_row("czta", o) for o in czta_out]
    summary_rows = [summarize("baseline", baseline_out), summarize("czta", czta_out)]
    attack_rows = by_attack("baseline", baseline_out) + by_attack("czta", czta_out)

    ablations = {
        "full_czta": ControlConfig(),
        "without_source_gate": ControlConfig(source_gate=False),
        "without_prompt_gate": ControlConfig(prompt_gate=False),
        "without_semantic_gate": ControlConfig(semantic_gate=False),
        "without_tool_broker": ControlConfig(tool_broker=False),
        "without_taint_tracking": ControlConfig(taint_tracking=False),
        "without_lineage_gate": ControlConfig(lineage_gate=False),
        "without_presentation_gate": ControlConfig(presentation_gate=False),
    }
    ablation_rows: List[Dict[str, object]] = []
    for name, config in ablations.items():
        pipeline = CZTAPipeline(
            config=config,
            private_key=czta.private_key,
            timestamp_provider=fixed_timestamp,
        )
        outputs = [pipeline.process(ep) for ep in episodes]
        for row in by_attack(name, outputs):
            if row["attack_type"] != "benign":
                ablation_rows.append(row)

    out_dir.mkdir(parents=True, exist_ok=True)
    write_csv(out_dir / "episode_outcomes.csv", outcome_rows)
    write_csv(out_dir / "system_summary.csv", summary_rows)
    write_csv(out_dir / "attack_type_results.csv", attack_rows)
    write_csv(out_dir / "ablation_results.csv", ablation_rows)

    example = next(o.attestation for o in czta_out if o.signature_valid and o.allowed)
    (out_dir / "signed_rla_example.json").write_text(json.dumps(example, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    report = {
        "benchmark": "CZTA model-independent reference-monitor microbenchmark",
        "seed": seed,
        "attacks_per_type": attacks_per_type,
        "benign_episodes": benign,
        "total_episodes": len(episodes),
        "systems": summary_rows,
        "scope": "Synthetic policy/lineage invariant testing; not an LLM, human-subject, or field-deployment evaluation.",
        "reproducibility": "Episodes, policy outcomes, test key, timestamp, and signed example are deterministic for the seed; wall-clock latency is environment-dependent.",
    }
    (out_dir / "benchmark_summary.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="prototype/results")
    parser.add_argument("--seed", type=int, default=20260711)
    parser.add_argument("--attacks-per-type", type=int, default=180)
    parser.add_argument("--benign", type=int, default=420)
    args = parser.parse_args()
    report = run(Path(args.out), args.seed, args.attacks_per_type, args.benign)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
