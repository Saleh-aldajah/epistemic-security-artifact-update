"""Non-human identity and bounded-autonomy primitives for CZTA.

The reference types operationalize two current governance patterns without
making vendor-specific deployment claims:

* an agent is a first-class, tenant-scoped workload identity with an accountable
  human sponsor and a reusable blueprint; and
* autonomy is an explicit authority envelope. The four labels mirror the CSA
  Agentic Trust Framework (Intern, Junior, Senior, Principal), while promotion
  evidence is recorded separately through five gates.

These objects are policy inputs. They do not by themselves establish trust.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
from typing import Dict, FrozenSet


AUTONOMY_LEVELS = ("intern", "junior", "senior", "principal")
PROMOTION_GATES = (
    "performance",
    "security_validation",
    "business_value",
    "incident_record",
    "governance_signoff",
)


@dataclass(frozen=True)
class AgentIdentity:
    agent_id: str = "agent:czta:soc-reference"
    tenant_id: str = "tenant:research"
    sponsor_id: str = "role:soc-duty-manager"
    blueprint_id: str = "blueprint:incident-response-junior-v1"
    issuer: str = "urn:czta:identity-registry"
    credential_fingerprint: str = ""

    def __post_init__(self) -> None:
        if not self.credential_fingerprint:
            material = (
                f"{self.agent_id}|{self.tenant_id}|{self.sponsor_id}|"
                f"{self.blueprint_id}|{self.issuer}"
            ).encode("utf-8")
            object.__setattr__(
                self,
                "credential_fingerprint",
                "sha256:" + hashlib.sha256(material).hexdigest(),
            )

    def as_dict(self) -> Dict[str, str]:
        return {
            "agent_id": self.agent_id,
            "identity_type": "non-human-agent",
            "tenant_id": self.tenant_id,
            "sponsor_id": self.sponsor_id,
            "blueprint_id": self.blueprint_id,
            "issuer": self.issuer,
            "credential_fingerprint": self.credential_fingerprint,
            "status": "active",
        }


@dataclass(frozen=True)
class AutonomyEnvelope:
    level: str = "junior"
    domain: str = "soc-incident-response"
    permitted_capabilities: FrozenSet[str] = field(
        default_factory=lambda: frozenset(
            {
                "read:evidence",
                "recommend:containment",
                "request:edr-control.quarantine-host",
            }
        )
    )
    human_approval_required: bool = True
    promotion_gates: Dict[str, str] = field(
        default_factory=lambda: {
            "performance": "not-assessed",
            "security_validation": "prototype-tested",
            "business_value": "not-assessed",
            "incident_record": "synthetic-only",
            "governance_signoff": "not-granted",
        }
    )
    revocation_state: str = "active"

    def __post_init__(self) -> None:
        if self.level not in AUTONOMY_LEVELS:
            raise ValueError(f"Unsupported autonomy level: {self.level}")
        missing = set(PROMOTION_GATES) - set(self.promotion_gates)
        if missing:
            raise ValueError(f"Missing promotion gates: {sorted(missing)}")

    def allows(self, capability: str, *, human_approved: bool) -> bool:
        if self.revocation_state != "active" or capability not in self.permitted_capabilities:
            return False
        if self.level == "intern":
            return capability.startswith("read:")
        if self.level == "junior":
            # Junior agents may prepare or request actions, but execution must
            # remain subject to explicit human approval.
            if capability.startswith(("recommend:", "request:")):
                return True
            return human_approved
        return True

    def as_dict(self) -> Dict[str, object]:
        return {
            "framework_profile": "CSA-ATF-compatible",
            "level": self.level,
            "domain": self.domain,
            "permitted_capabilities": sorted(self.permitted_capabilities),
            "human_approval_required": self.human_approval_required,
            "promotion_gates": dict(self.promotion_gates),
            "revocation_state": self.revocation_state,
        }
