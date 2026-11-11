"""Localization assurance and degraded-safe presentation primitives for CZTA.

The reference implementation does not translate content or claim multilingual
semantic parity. It verifies that language, locale, script direction,
jurisdiction, and translation provenance are explicit policy state. Recoverable
assurance failures enter a degraded-safe, advisory-only mode; evidence of a
potentially corrupted transformation is quarantined.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, FrozenSet, List, Tuple


DEFAULT_SUPPORTED_LANGUAGES: FrozenSet[str] = frozenset({"en", "ar"})
DEFAULT_SUPPORTED_LOCALES: FrozenSet[str] = frozenset(
    {"en-US", "en-GB", "en-AE", "ar-AE", "ar-SA", "ar-EG"}
)

# Failures that indicate missing capability or provenance. They can preserve
# operational continuity only through an explicitly downgraded human-review UI.
DEGRADED_SAFE_REASONS = frozenset(
    {
        "localization-source-language-missing",
        "localization-user-language-undeclared",
        "localization-interaction-language-unsupported",
        "localization-source-language-unsupported",
        "localization-safety-policy-language-unsupported",
        "localization-locale-unsupported",
        "translation-provenance-missing",
        "localization-code-switching-languages-incomplete",
    }
)

# Failures that suggest an invalid or potentially tampered transform. These do
# not expose content, even in degraded-safe mode, until an authorized reviewer
# resolves the discrepancy.
QUARANTINE_REASONS = frozenset(
    {
        "localization-script-direction-invalid",
        "translation-step-incomplete",
        "translation-target-language-mismatch",
        "translation-digest-not-transformed",
    }
)


@dataclass(frozen=True)
class TranslationStep:
    """One provenance-preserving translation transform."""

    source_language: str
    target_language: str
    translator_id: str
    translator_version: str
    source_digest: str
    output_digest: str
    quality_gate: str = "pending-human-or-independent-check"

    def as_dict(self) -> Dict[str, object]:
        return {
            "source_language": self.source_language,
            "target_language": self.target_language,
            "translator_id": self.translator_id,
            "translator_version": self.translator_version,
            "source_digest": self.source_digest,
            "output_digest": self.output_digest,
            "quality_gate": self.quality_gate,
        }


@dataclass(frozen=True)
class LocalizationContext:
    """Language and jurisdiction state that must survive the decision path."""

    source_languages: Tuple[str, ...] = ("en",)
    interaction_language: str = "en"
    locale: str = "en-AE"
    script: str = "Latn"
    script_direction: str = "ltr"
    code_switching: bool = False
    jurisdiction: str = "AE"
    safety_policy_language: str = "en"
    user_language_declared: bool = True
    translation_required: bool = False
    translation_steps: Tuple[TranslationStep, ...] = field(default_factory=tuple)

    def as_dict(self) -> Dict[str, object]:
        return {
            "source_languages": list(self.source_languages),
            "interaction_language": self.interaction_language,
            "locale": self.locale,
            "script": self.script,
            "script_direction": self.script_direction,
            "code_switching": self.code_switching,
            "jurisdiction": self.jurisdiction,
            "safety_policy_language": self.safety_policy_language,
            "user_language_declared": self.user_language_declared,
            "translation_required": self.translation_required,
            "translation_steps": [step.as_dict() for step in self.translation_steps],
        }


@dataclass(frozen=True)
class LocalizationDecision:
    """Outcome of the localization assurance gate.

    ``verified`` permits normal governed presentation. ``degraded-safe`` keeps
    the workflow available only for human review of inert original evidence and
    strips automated authority. ``quarantine`` withholds content because a
    transform may be corrupted or tampered with.
    """

    allowed: bool
    mode: str
    reasons: Tuple[str, ...]
    obligations: Tuple[str, ...]
    human_review_required: bool
    automated_trust_badges_visible: bool
    automated_summary_allowed: bool
    tool_execution_allowed: bool
    memory_writeback_allowed: bool
    inert_original_evidence_allowed: bool
    recovery_actions: Tuple[str, ...]

    def as_dict(self) -> Dict[str, object]:
        return {
            "allowed": self.allowed,
            "mode": self.mode,
            "reasons": list(self.reasons),
            "obligations": list(self.obligations),
            "human_review_required": self.human_review_required,
            "automated_trust_badges_visible": self.automated_trust_badges_visible,
            "automated_summary_allowed": self.automated_summary_allowed,
            "tool_execution_allowed": self.tool_execution_allowed,
            "memory_writeback_allowed": self.memory_writeback_allowed,
            "inert_original_evidence_allowed": self.inert_original_evidence_allowed,
            "recovery_actions": list(self.recovery_actions),
        }


def assess_localization(
    context: LocalizationContext,
    *,
    supported_languages: FrozenSet[str] = DEFAULT_SUPPORTED_LANGUAGES,
    supported_locales: FrozenSet[str] = DEFAULT_SUPPORTED_LOCALES,
) -> LocalizationDecision:
    """Evaluate declared localization state without claiming semantic safety."""

    reasons: List[str] = []
    obligations: List[str] = [
        "preserve-language-tags",
        "bind-localization-to-rla",
        "apply-language-matched-safety-policy",
    ]

    if not context.source_languages:
        reasons.append("localization-source-language-missing")
    if not context.user_language_declared:
        reasons.append("localization-user-language-undeclared")
    if context.interaction_language not in supported_languages:
        reasons.append("localization-interaction-language-unsupported")
    if any(language not in supported_languages for language in context.source_languages):
        reasons.append("localization-source-language-unsupported")
    if context.safety_policy_language not in supported_languages:
        reasons.append("localization-safety-policy-language-unsupported")
    if context.locale not in supported_locales:
        reasons.append("localization-locale-unsupported")
    if context.script_direction not in {"ltr", "rtl"}:
        reasons.append("localization-script-direction-invalid")

    language_transition = any(
        language != context.interaction_language for language in context.source_languages
    )
    if context.translation_required or language_transition:
        if not context.translation_steps:
            reasons.append("translation-provenance-missing")
        else:
            obligations.extend(
                ["show-translation-status", "independent-cross-lingual-validation"]
            )
            for step in context.translation_steps:
                if not all(
                    [
                        step.source_language,
                        step.target_language,
                        step.translator_id,
                        step.translator_version,
                        step.source_digest,
                        step.output_digest,
                    ]
                ):
                    reasons.append("translation-step-incomplete")
                if step.target_language != context.interaction_language:
                    reasons.append("translation-target-language-mismatch")
                if step.source_digest == step.output_digest:
                    reasons.append("translation-digest-not-transformed")

    if context.code_switching:
        obligations.extend(
            ["code-switching-segment-labels", "multilingual-injection-scan"]
        )
        if len(set(context.source_languages)) < 2:
            reasons.append("localization-code-switching-languages-incomplete")

    if context.script_direction == "rtl":
        obligations.extend(["rtl-layout-check", "bidirectional-text-safety-check"])

    unique_reasons = tuple(dict.fromkeys(reasons))
    if not unique_reasons:
        mode = "verified"
        recovery_actions: Tuple[str, ...] = ()
    elif any(reason in QUARANTINE_REASONS for reason in unique_reasons):
        mode = "quarantine"
        obligations.extend(
            [
                "withhold-localized-content",
                "preserve-forensic-copy",
                "route-to-authorized-localization-reviewer",
            ]
        )
        recovery_actions = (
            "verify-original-and-transformed-digests",
            "repeat-translation-with-approved-component",
            "obtain-qualified-language-review",
            "re-attest-before-release",
        )
    else:
        mode = "degraded-safe"
        obligations.extend(
            [
                "suppress-automated-trust-badges",
                "mark-manual-verification-required",
                "advisory-only",
                "disable-automated-summary",
                "disable-tool-execution",
                "disable-memory-writeback",
                "show-inert-original-evidence-only",
                "log-authorization-downgrade",
            ]
        )
        recovery_actions = (
            "obtain-qualified-language-review",
            "restore-supported-validator-or-translator",
            "re-run-localization-policy",
            "re-attest-before-automation",
        )

    return LocalizationDecision(
        allowed=mode == "verified",
        mode=mode,
        reasons=unique_reasons,
        obligations=tuple(dict.fromkeys(obligations)),
        human_review_required=mode != "verified",
        automated_trust_badges_visible=mode == "verified",
        automated_summary_allowed=mode == "verified",
        tool_execution_allowed=mode == "verified",
        memory_writeback_allowed=mode == "verified",
        inert_original_evidence_allowed=mode == "degraded-safe",
        recovery_actions=recovery_actions,
    )
