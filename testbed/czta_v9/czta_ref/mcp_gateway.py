"""Zero-trust Model Context Protocol (MCP) gateway reference checks.

The implementation is intentionally local and protocol-model-level. It checks
security-context continuity, audience binding, per-request authorization,
least-privilege scopes, tool-surface minimization, token freshness, redirect
integrity, and the prohibition on token passthrough. It does not implement an
OAuth authorization server or an MCP transport.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import FrozenSet, List


@dataclass(frozen=True)
class MCPRequestContext:
    session_id: str
    initiating_user_id: str
    tenant_id: str
    agent_id: str
    tool_id: str
    resource_audience: str
    token_audience: str
    scopes: FrozenSet[str] = field(default_factory=lambda: frozenset({"tool:execute"}))
    required_scope: str = "tool:execute"
    allowed_tools: FrozenSet[str] = field(
        default_factory=lambda: frozenset({"edr-control", "cve-lookup", "log-query"})
    )
    authorization_epoch: int = 1
    expected_authorization_epoch: int = 1
    token_expires_in_seconds: int = 300
    token_passthrough: bool = False
    redirect_uri_exact_match: bool = True
    server_origin_trusted: bool = True


@dataclass(frozen=True)
class MCPDecision:
    allowed: bool
    reasons: List[str]
    obligations: List[str]


def authorize_mcp_request(
    ctx: MCPRequestContext,
    *,
    expected_tenant_id: str,
    expected_agent_id: str,
    expected_user_id: str,
) -> MCPDecision:
    """Evaluate a call as a new authorization decision, not a session grant."""
    reasons: List[str] = []
    obligations = [
        "validate-json-schema",
        "record-transaction-digest",
        "bind-result-to-rla",
    ]

    if ctx.tenant_id != expected_tenant_id:
        reasons.append("mcp-tenant-mismatch")
    if ctx.agent_id != expected_agent_id:
        reasons.append("mcp-agent-identity-mismatch")
    if ctx.initiating_user_id != expected_user_id:
        reasons.append("mcp-user-context-mismatch")
    if ctx.resource_audience != ctx.token_audience:
        reasons.append("mcp-token-audience-mismatch")
    if ctx.required_scope not in ctx.scopes:
        reasons.append("mcp-insufficient-scope")
    if ctx.tool_id not in ctx.allowed_tools:
        reasons.append("mcp-tool-not-exposed")
    if ctx.authorization_epoch != ctx.expected_authorization_epoch:
        reasons.append("mcp-stale-authorization-epoch")
    if ctx.token_expires_in_seconds <= 0:
        reasons.append("mcp-expired-token")
    if ctx.token_passthrough:
        reasons.append("mcp-token-passthrough-forbidden")
    if not ctx.redirect_uri_exact_match:
        reasons.append("mcp-redirect-uri-mismatch")
    if not ctx.server_origin_trusted:
        reasons.append("mcp-untrusted-server-origin")

    if ctx.required_scope not in ctx.scopes:
        obligations.append("step-up-authorization")
    return MCPDecision(allowed=not reasons, reasons=reasons, obligations=obligations)
