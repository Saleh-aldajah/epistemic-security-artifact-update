"""Bounded adaptive trust analytics for CZTA.

Analytics may summarize dynamic telemetry, but hard policy remains the reference
monitor. Every post-policy adjustment is monotone: it can preserve or make a
decision more restrictive, never relax a deterministic denial or requirement.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List


# Larger values are more restrictive. This executable ordering is the inverse
# of the paper's permissiveness order, but it implements the same lattice.
DECISION_ORDER = {
    "allow": 0,
    "constrained-allow": 1,
    "dual-control": 2,
    "corroborate": 3,
    "degrade": 4,
    "quarantine": 5,
    "deny": 6,
}

ACTIONABLE_DECISIONS = frozenset({"allow", "constrained-allow", "dual-control"})


@dataclass(frozen=True)
class TrustAssessment:
    risk_score: float
    risk_band: str
    signals: List[str]
    model_id: str = "bounded-telemetry-score-v1"
    advisory_only: bool = True


def tighten_to(base_decision: str, required_decision: str) -> str:
    """Return the more restrictive of two decisions.

    This helper is used for analytics *and* localization outcomes. It is the
    executable counterpart of ``Tighten`` in Algorithm 1 and prevents a
    degraded-safe state from rewriting an existing deny or quarantine into the
    less restrictive ``degrade`` state.
    """
    if base_decision not in DECISION_ORDER:
        raise ValueError(f"Unknown policy decision: {base_decision}")
    if required_decision not in DECISION_ORDER:
        raise ValueError(f"Unknown required decision: {required_decision}")
    return max((base_decision, required_decision), key=lambda d: DECISION_ORDER[d])


def decision_allows_action(decision: str) -> bool:
    """Whether a decision may reach the MCP authorizer or action surface."""
    if decision not in DECISION_ORDER:
        raise ValueError(f"Unknown policy decision: {decision}")
    return decision in ACTIONABLE_DECISIONS


def assess_trust(
    *,
    source_rejection_fraction: float,
    support: float,
    disagreement_count: int,
    warning_signals: Iterable[str],
    tainted: bool,
    provenance_complete: bool,
    tool_authorized: bool,
) -> TrustAssessment:
    signals = list(dict.fromkeys(warning_signals))
    score = 0.0
    score += 0.25 * min(1.0, max(0.0, source_rejection_fraction))
    score += 0.25 * (1.0 - min(1.0, max(0.0, support)))
    score += 0.10 * min(1.0, disagreement_count / 2.0)
    score += 0.10 * min(1.0, len(signals) / 4.0)
    score += 0.15 if tainted else 0.0
    score += 0.10 if not provenance_complete else 0.0
    score += 0.15 if not tool_authorized else 0.0
    score = min(1.0, round(score, 6))
    band = "low" if score < 0.25 else "guarded" if score < 0.50 else "high" if score < 0.75 else "critical"
    return TrustAssessment(risk_score=score, risk_band=band, signals=signals)


def tighten_decision(base_decision: str, assessment: TrustAssessment) -> str:
    """Return a decision that is never less restrictive than ``base_decision``."""
    if base_decision not in DECISION_ORDER:
        raise ValueError(f"Unknown policy decision: {base_decision}")
    proposed = base_decision
    if assessment.risk_score >= 0.75:
        proposed = "quarantine"
    elif assessment.risk_score >= 0.50:
        proposed = "corroborate"
    elif assessment.risk_score >= 0.25:
        proposed = "dual-control"
    return tighten_to(base_decision, proposed)
