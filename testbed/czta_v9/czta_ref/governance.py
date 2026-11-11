"""Cryptographically enforced governance quorum for CZTA policy changes.

The reference implementation uses explicit Ed25519 co-signatures rather than a
single aggregated threshold signature. This preserves signer identity and role
accountability in the released artifact. Deployments can substitute a reviewed
threshold-signature protocol, such as FROST, while retaining the same m-of-n and
role-diversity acceptance semantics.

Deterministic keys in this module exist only to make the synthetic example
reproducible. They MUST NOT be used in production.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import base64
import copy
import hashlib
from typing import Dict, Iterable, Mapping, MutableMapping, Optional, Sequence, Tuple

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey

from .rla import artifact_digest, canonical_json, private_key_from_seed, public_key_b64


CHANGE_CLASSES = {
    "core-security-invariant",
    "pdp-policy",
    "autonomy-promotion-gate",
    "trust-analytics-threshold",
    "localization-policy",
    "translation-model",
    "signer-registry",
    "quorum-policy",
}


@dataclass(frozen=True)
class GovernancePrincipal:
    principal_id: str
    role: str
    public_key: Ed25519PublicKey
    status: str = "active"

    def as_dict(self) -> Dict[str, object]:
        return {
            "principal_id": self.principal_id,
            "role": self.role,
            "status": self.status,
            "signer": "did:key:ed25519:" + public_key_b64(self.public_key),
        }


@dataclass(frozen=True)
class QuorumPolicy:
    policy_id: str = "czta-governance-root-v1"
    threshold: int = 3
    authorized_principals: Tuple[str, ...] = (
        "gov:security-architect",
        "gov:risk-owner",
        "gov:domain-owner",
        "gov:identity-owner",
        "gov:independent-assurance",
    )
    required_roles: Tuple[str, ...] = (
        "security",
        "risk",
        "independent-assurance",
    )
    governance_epoch: int = 6
    valid_from: str = "2026-07-12T00:00:00Z"
    valid_until: str = "2027-07-12T00:00:00Z"
    protected_change_classes: Tuple[str, ...] = tuple(sorted(CHANGE_CLASSES))
    genesis_root_digest: str = field(
        default_factory=lambda: "sha256:" + hashlib.sha256(b"czta-offline-genesis-root-v1").hexdigest()
    )
    bootstrap_method: str = "offline-root-ceremony"
    threshold_reduction_allowed: bool = False
    quorum_policy_change_requires_all: bool = True
    cooling_period_hours: int = 72

    def __post_init__(self) -> None:
        if self.threshold <= 1:
            raise ValueError("Governance quorum threshold must be greater than one")
        if self.threshold > len(self.authorized_principals):
            raise ValueError("Quorum threshold exceeds authorized principal count")
        if len(set(self.authorized_principals)) != len(self.authorized_principals):
            raise ValueError("Authorized principals must be unique")

    def as_dict(self) -> Dict[str, object]:
        return {
            "policy_id": self.policy_id,
            "threshold": self.threshold,
            "authorized_principals": list(self.authorized_principals),
            "required_roles": list(self.required_roles),
            "governance_epoch": self.governance_epoch,
            "valid_from": self.valid_from,
            "valid_until": self.valid_until,
            "protected_change_classes": list(self.protected_change_classes),
            "genesis_root_digest": self.genesis_root_digest,
            "bootstrap_method": self.bootstrap_method,
            "threshold_reduction_allowed": self.threshold_reduction_allowed,
            "quorum_policy_change_requires_all": self.quorum_policy_change_requires_all,
            "cooling_period_hours": self.cooling_period_hours,
        }

    @property
    def digest(self) -> str:
        return artifact_digest(self.as_dict())


@dataclass(frozen=True)
class GovernanceChange:
    event_id: str
    change_class: str
    target: str
    previous_state_digest: str
    proposed_state_digest: str
    previous_version: str
    proposed_version: str
    governance_epoch: int
    not_before: str
    not_after: str
    rationale: str
    test_evidence_digest: str
    rollback_plan_digest: str
    quorum_policy_id: str = "czta-governance-root-v1"
    emergency: bool = False
    proposed_quorum_threshold: Optional[int] = None
    cooling_period_ends: Optional[str] = None
    signatures: Tuple[Dict[str, str], ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if self.change_class not in CHANGE_CLASSES:
            raise ValueError(f"Unsupported governance change class: {self.change_class}")
        for name, value in {
            "previous_state_digest": self.previous_state_digest,
            "proposed_state_digest": self.proposed_state_digest,
            "test_evidence_digest": self.test_evidence_digest,
            "rollback_plan_digest": self.rollback_plan_digest,
        }.items():
            if not value.startswith("sha256:") or len(value) != 71:
                raise ValueError(f"{name} must be a sha256-prefixed digest")

    def payload(self) -> Dict[str, object]:
        return {
            "schema_version": "1.0",
            "event_id": self.event_id,
            "change_class": self.change_class,
            "target": self.target,
            "previous_state_digest": self.previous_state_digest,
            "proposed_state_digest": self.proposed_state_digest,
            "previous_version": self.previous_version,
            "proposed_version": self.proposed_version,
            "governance_epoch": self.governance_epoch,
            "validity": {"not_before": self.not_before, "not_after": self.not_after},
            "rationale": self.rationale,
            "test_evidence_digest": self.test_evidence_digest,
            "rollback_plan_digest": self.rollback_plan_digest,
            "quorum_policy_id": self.quorum_policy_id,
            "emergency": self.emergency,
            "proposed_quorum_threshold": self.proposed_quorum_threshold,
            "cooling_period_ends": self.cooling_period_ends,
        }

    @property
    def event_digest(self) -> str:
        return artifact_digest(self.payload())

    def as_dict(self) -> Dict[str, object]:
        return {**self.payload(), "event_digest": self.event_digest, "signatures": list(self.signatures)}


@dataclass(frozen=True)
class QuorumVerification:
    accepted: bool
    reasons: Tuple[str, ...]
    valid_principals: Tuple[str, ...]
    valid_roles: Tuple[str, ...]
    threshold: int
    valid_signature_count: int
    governance_epoch: int
    event_digest: str

    def as_dict(self) -> Dict[str, object]:
        return {
            "accepted": self.accepted,
            "reasons": list(self.reasons),
            "valid_principals": list(self.valid_principals),
            "valid_roles": list(self.valid_roles),
            "threshold": self.threshold,
            "valid_signature_count": self.valid_signature_count,
            "governance_epoch": self.governance_epoch,
            "event_digest": self.event_digest,
        }


@dataclass(frozen=True)
class GovernanceContext:
    governance_root_id: str
    quorum_policy_digest: str
    active_policy_event_digest: str
    governance_epoch: int
    quorum_threshold: int
    verified_signature_count: int
    quorum_verified: bool
    genesis_root_digest: str = "sha256:" + hashlib.sha256(b"czta-offline-genesis-root-v1").hexdigest()
    bootstrap_method: str = "offline-root-ceremony"
    protected_targets: Tuple[str, ...] = (
        "pdp-policy",
        "autonomy-promotion-gate",
        "trust-analytics-threshold",
        "localization-policy",
    )

    def as_dict(self) -> Dict[str, object]:
        return {
            "governance_root_id": self.governance_root_id,
            "quorum_policy_digest": self.quorum_policy_digest,
            "active_policy_event_digest": self.active_policy_event_digest,
            "governance_epoch": self.governance_epoch,
            "quorum_threshold": self.quorum_threshold,
            "verified_signature_count": self.verified_signature_count,
            "quorum_verified": self.quorum_verified,
            "genesis_root_digest": self.genesis_root_digest,
            "bootstrap_method": self.bootstrap_method,
            "protected_targets": list(self.protected_targets),
        }


def _utc(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def sign_governance_change(
    change: GovernanceChange,
    principal: GovernancePrincipal,
    private_key: Ed25519PrivateKey,
) -> Dict[str, str]:
    """Create one accountable signature over the canonical change payload."""
    signer = "did:key:ed25519:" + public_key_b64(private_key.public_key())
    expected = "did:key:ed25519:" + public_key_b64(principal.public_key)
    if signer != expected:
        raise ValueError("Private key does not match governance principal")
    signature = private_key.sign(canonical_json(change.payload()))
    return {
        "principal_id": principal.principal_id,
        "role": principal.role,
        "signer": signer,
        "algorithm": "Ed25519",
        "signature": base64.b64encode(signature).decode("ascii"),
    }


def verify_governance_quorum(
    change: GovernanceChange,
    registry: Mapping[str, GovernancePrincipal],
    policy: QuorumPolicy,
    *,
    verification_time: str = "2026-07-12T12:00:00Z",
) -> QuorumVerification:
    """Verify distinct signer, role-diversity, epoch, freshness, and signature rules."""
    reasons = []
    if change.quorum_policy_id != policy.policy_id:
        reasons.append("quorum-policy-id-mismatch")
    if change.governance_epoch != policy.governance_epoch:
        reasons.append("governance-epoch-mismatch")
    if change.change_class not in policy.protected_change_classes:
        reasons.append("change-class-not-protected")

    now = _utc(verification_time)
    if not (_utc(policy.valid_from) <= now <= _utc(policy.valid_until)):
        reasons.append("quorum-policy-outside-validity")
    if not (_utc(change.not_before) <= now <= _utc(change.not_after)):
        reasons.append("governance-change-outside-validity")

    valid: MutableMapping[str, str] = {}
    for row in change.signatures:
        principal_id = row.get("principal_id", "")
        if not principal_id or principal_id in valid:
            if principal_id in valid:
                reasons.append("duplicate-governance-principal")
            continue
        if principal_id not in policy.authorized_principals:
            reasons.append("unauthorized-governance-principal")
            continue
        principal = registry.get(principal_id)
        if principal is None:
            reasons.append("governance-principal-not-registered")
            continue
        if principal.status != "active":
            reasons.append("governance-principal-inactive")
            continue
        expected_signer = "did:key:ed25519:" + public_key_b64(principal.public_key)
        if row.get("signer") != expected_signer or row.get("role") != principal.role:
            reasons.append("governance-signer-metadata-mismatch")
            continue
        try:
            signature = base64.b64decode(row.get("signature", ""), validate=True)
            principal.public_key.verify(signature, canonical_json(change.payload()))
        except Exception:
            reasons.append("invalid-governance-signature")
            continue
        valid[principal_id] = principal.role

    valid_roles = set(valid.values())
    if len(valid) < policy.threshold:
        reasons.append("governance-quorum-not-met")
    missing_roles = set(policy.required_roles) - valid_roles
    if missing_roles:
        reasons.append("governance-role-diversity-not-met")

    # Core invariant changes can never use a unilateral emergency path. An
    # emergency may activate a pre-approved stricter fallback profile, but it
    # cannot redefine the invariant or lower the threshold.
    if change.emergency and change.change_class in {
        "core-security-invariant",
        "quorum-policy",
        "signer-registry",
    }:
        reasons.append("emergency-core-governance-change-prohibited")

    # The genesis root is provisioned out of band. A later quorum-policy
    # update is itself a root-of-trust change: it requires every active current
    # principal, a cooling period, and may not lower the current threshold.
    if change.change_class == "quorum-policy":
        if policy.quorum_policy_change_requires_all and len(valid) < len(policy.authorized_principals):
            reasons.append("full-governance-quorum-required")
        if change.proposed_quorum_threshold is None:
            reasons.append("proposed-quorum-threshold-required")
        elif (
            not policy.threshold_reduction_allowed
            and change.proposed_quorum_threshold < policy.threshold
        ):
            reasons.append("quorum-threshold-reduction-prohibited")
        if not change.cooling_period_ends:
            reasons.append("governance-cooling-period-required")
        elif now < _utc(change.cooling_period_ends):
            reasons.append("governance-cooling-period-active")

    unique_reasons = tuple(dict.fromkeys(reasons))
    return QuorumVerification(
        accepted=not unique_reasons,
        reasons=unique_reasons,
        valid_principals=tuple(sorted(valid)),
        valid_roles=tuple(sorted(valid_roles)),
        threshold=policy.threshold,
        valid_signature_count=len(valid),
        governance_epoch=policy.governance_epoch,
        event_digest=change.event_digest,
    )


def reference_governance_material() -> Tuple[
    QuorumPolicy,
    Dict[str, GovernancePrincipal],
    Dict[str, Ed25519PrivateKey],
    GovernanceChange,
    QuorumVerification,
]:
    """Build deterministic 3-of-5 material for the public reference artifact."""
    principal_specs = (
        ("gov:security-architect", "security", 6101),
        ("gov:risk-owner", "risk", 6102),
        ("gov:domain-owner", "domain", 6103),
        ("gov:identity-owner", "identity", 6104),
        ("gov:independent-assurance", "independent-assurance", 6105),
    )
    keys: Dict[str, Ed25519PrivateKey] = {}
    registry: Dict[str, GovernancePrincipal] = {}
    for principal_id, role, seed in principal_specs:
        private = private_key_from_seed(seed, domain="czta-governance-v6-test-only")
        keys[principal_id] = private
        registry[principal_id] = GovernancePrincipal(
            principal_id=principal_id,
            role=role,
            public_key=private.public_key(),
        )

    policy = QuorumPolicy()
    change = GovernanceChange(
        event_id="gov-change-czta-policy-2.2",
        change_class="pdp-policy",
        target="policy:czta-soc-reference-policy",
        previous_state_digest="sha256:" + hashlib.sha256(b"czta-policy-2.1").hexdigest(),
        proposed_state_digest="sha256:" + hashlib.sha256(b"czta-policy-2.2").hexdigest(),
        previous_version="2.1",
        proposed_version="2.2",
        governance_epoch=policy.governance_epoch,
        not_before="2026-07-12T00:00:00Z",
        not_after="2027-01-12T00:00:00Z",
        rationale="Bind quorum governance, degraded-safe localization, and calibration metadata.",
        test_evidence_digest="sha256:" + hashlib.sha256(b"v6-governance-tests").hexdigest(),
        rollback_plan_digest="sha256:" + hashlib.sha256(b"rollback-to-czta-policy-2.1").hexdigest(),
        quorum_policy_id=policy.policy_id,
    )
    signers = (
        "gov:security-architect",
        "gov:risk-owner",
        "gov:independent-assurance",
    )
    signatures = tuple(
        sign_governance_change(change, registry[principal_id], keys[principal_id])
        for principal_id in signers
    )
    signed_change = GovernanceChange(**{**change.__dict__, "signatures": signatures})
    verification = verify_governance_quorum(signed_change, registry, policy)
    return policy, registry, keys, signed_change, verification


def reference_governance_context() -> GovernanceContext:
    policy, _registry, _keys, change, verification = reference_governance_material()
    if not verification.accepted:
        raise RuntimeError(f"Reference governance quorum is invalid: {verification.reasons}")
    return GovernanceContext(
        governance_root_id=policy.policy_id,
        quorum_policy_digest=policy.digest,
        active_policy_event_digest=change.event_digest,
        governance_epoch=policy.governance_epoch,
        quorum_threshold=policy.threshold,
        verified_signature_count=verification.valid_signature_count,
        quorum_verified=verification.accepted,
        genesis_root_digest=policy.genesis_root_digest,
        bootstrap_method=policy.bootstrap_method,
    )
