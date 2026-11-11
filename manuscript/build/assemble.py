#!/usr/bin/env python3
"""Assemble the S&P version of main.tex from hand-written parts plus edited
blocks of the original NDSS source. Every replacement on an original block is
asserted, so a silent mismatch cannot slip through."""
import re, sys, pathlib

# Layout (relative to this file):  build/assemble.py, build/parts/*.tex,
# build/original_ndss_main.tex (the NDSS source blocks are spliced from here),
# and ../main.tex is the output. Run:  python3 -I build/assemble.py
HERE = pathlib.Path(__file__).resolve().parent
ORIG = (HERE / "original_ndss_main.tex").read_text().split("\n")
P = HERE / "parts"
OUT = HERE.parent / "main.tex"

def lines(a, b):                     # 1-indexed inclusive
    return "\n".join(ORIG[a-1:b])

def rep(s, old, new, count=1, where=""):
    n = s.count(old)
    assert n >= 1, f"[{where}] not found: {old[:70]!r}"
    if count == 1:
        assert n == 1, f"[{where}] expected 1 match, found {n}: {old[:70]!r}"
    return s.replace(old, new)

def rename_invariants(s):
    """In ORIGINAL blocks, \\Ifour meant the counterfactual bound -> now \\Ifive;
    the enforceable fragment I1--I3 -> I1--I4."""
    s = s.replace("\\Ifour", "\\Ifive")
    s = s.replace("\\Ione--\\Ithree", "\\Ione--\\Ifour")
    s = s.replace("\\Ione \\wedge \\Itwo \\wedge \\Ithree", "\\Ione \\wedge \\Itwo \\wedge \\Ithree \\wedge \\Ifour")
    s = s.replace("\\Ione\\wedge\\Itwo\\wedge\\Ithree", "\\Ione\\wedge\\Itwo\\wedge\\Ithree\\wedge\\Ifour")
    s = s.replace("$\\Ione$--$\\Ithree$", "$\\Ione$--$\\Ifour$")
    return s

# ---------------------------------------------------------------- figure: boundary (1003-1041)
fig = rename_invariants(lines(1003, 1041))
fig = rep(fig, "(a) \\Ione--\\Ifour: safety --- enforced online by truncation", "(a) \\Ione--\\Ifour: safety --- enforced online by truncation", where="fig")
fig = rep(fig, "(b) \\Ifive: 2-safety --- audited offline on witness pairs", "(b) \\Ifive: 2-safety --- audited offline on witness pairs", where="fig")
fig = rep(fig, "(Cor.~\\ref{cor:decomp}). (a)~\\Ione--\\Ifour{}: a single-trace\nmonitor detects the bad prefix and truncates. (b)~\\Ifive{}",
          "(Cor.~\\ref{cor:decomp}). (a)~\\Ione--\\Ifour{}: a single-trace\nmonitor detects the bad prefix and truncates. (b)~\\Ifive{}", where="fig")

# ---------------------------------------------------------------- Algorithm 1 (2233-2275)
alg = lines(2233, 2275)
alg = rep(alg, "\\caption{\\DEI{} reference monitor: event admission (enforces\n$\\Ione \\wedge \\Itwo \\wedge \\Ithree$ by truncation;\nProp.~\\ref{prop:safety}).}",
          "\\caption{\\DEI{} reference monitor: event admission (enforces\n$\\Ione \\wedge \\Itwo \\wedge \\Ithree \\wedge \\Ifour$ by truncation;\nProp.~\\ref{prop:safety}).}", where="alg1")
alg = rep(alg, "\\Require event $\\epsilon$; state $(\\ell, P, \\cert, \\pi)$; policy\n$\\Pi = (\\lmin, \\lreq, \\tau, \\Cprot)$",
          "\\Require event $\\epsilon$; state $(\\ell, P, \\cert, \\vals, \\pi)$; policy\n$\\Pi = (\\lmin, \\lreq, \\tau, \\bindpol, \\Cprot)$", where="alg1")
alg = rep(alg, "  \\State $\\ell(b') \\gets \\ell_{\\mathrm{prop}}$;\\;\n  $\\cert(b') \\gets \\bigwedge_{x \\in X} \\cert(x)$ \\Comment{$O(|X|)$, memoized}",
          "  \\State $\\ell(b') \\gets \\ell_{\\mathrm{prop}}$;\\;\n  $\\cert(b') \\gets \\bigwedge_{x \\in X} \\cert(x)$;\\; $\\vals(b') \\gets \\mathsf{extract}(b')$ \\Comment{$O(|X|)$, memoized}", where="alg1")
alg = rep(alg, "\\Comment{\\Ione; freshness per Def.~2}", "\\Comment{\\Ione; freshness per Def.~\\ref{def:evidence}}", where="alg1")
alg = rep(alg, "  \\If{$S(\\support(a), \\lreq(c(a))) < \\tau_{c(a)}$}\n    \\State \\textbf{block} \\Comment{\\Ithree: insufficient support}\n  \\EndIf",
          "  \\If{$S(\\support(a), \\lreq(c(a))) < \\tau_{c(a)}$}\n    \\State \\textbf{block} \\Comment{\\Ithree: insufficient support}\n  \\EndIf\n"
          "  \\ForAll{$s \\in \\bindpol(c(a))$ with $\\args(a)(s)$ defined}\n"
          "    \\If{$\\neg\\,\\exists b \\in \\support(a):\\; \\args(a)(s) \\in \\vals(b) \\wedge \\ell(b) \\sqsupseteq \\ell_{\\bindpol}(c(a), s)$}\n"
          "      \\State \\textbf{block} \\Comment{\\Ifour: unbound argument}\n"
          "    \\EndIf\n"
          "  \\EndFor", where="alg1")

# ---------------------------------------------------------------- bibliography (1853-2090) + new entries
bib = lines(1853, 2090)
bib = rep(bib, "\\begin{thebibliography}{37}", "\\begin{thebibliography}{51}", where="bib")
new_items = r"""
\bibitem{artifact} Anonymous, ``Epistemic security artifact: reference
monitor, reference semantics, Lean~4 mechanization, review ledger, and
campaign logs,'' anonymized repository,
\url{https://anonymous.4open.science/r/epistemic-security-artifact-AF35/}.

\bibitem{bhagwatkar2025firewalls} R.~Bhagwatkar, K.~Kasa, A.~Puri,
G.~Huang, I.~Rish, G.~W.~Taylor, K.~Dj~Dvijotham, and A.~Lacoste,
``Indirect prompt injections: Are firewalls all you need, or stronger
benchmarks?'' 2025, arXiv:2510.05244 (v2, 23 March 2026). Verified
against the arXiv record on 27 October 2026 (scoring-rule and
implementation defects in AgentDojo; Braille-encoded
important-instructions attack that bypasses a firewall defense).

\bibitem{agentdyn} H.~Li, R.~Wen, S.~Shi, N.~Zhang, Y.~Vorobeychik, and
C.~Xiao, ``AgentDyn: Are your agent security defenses deployable in
real-world dynamic environments?'' 2026, arXiv:2602.03117 (v3, 7 May
2026). Verified against the arXiv record on 27 October 2026 (60
open-ended tasks, 560 injection cases, helpful third-party
instructions).

\end{thebibliography}"""
bib = rep(bib, "\n\\end{thebibliography}", new_items, where="bib")

# strip reviewer-facing verification notes and descriptive annotations from bibitems (kept in BIB_ANNOTATIONS.md)
def _strip_item(item):
    m = re.search(r"Verified\s+against", item); i = m.start() if m else -1
    if i >= 0:
        j = item.rfind(".", 0, i)
        item = item[:j+1]
    item = re.sub(r"\.\s*Matched source-authority.*$", ".", item, flags=re.S)
    item = re.sub(r"\s+\((?:[^()]|\([^()]*\))*\)\s*\.\s*$", ".", item)      # trailing parenthetical annotation
    item = re.sub(r"\.\s*Cited alongside the current\s+MCP specification's authorization section.*$", ".", item, flags=re.S)
    item = re.sub(r"\s*\(v\d, [^)]*\)\.", ".", item)                          # (v2, 23 March 2026).
    return item.rstrip()
_items = bib.split("\n\n")
bib = "\n\n".join(_strip_item(it) if it.lstrip().startswith("\\bibitem") else it for it in _items)
assert "Verified against" not in bib, [l for l in bib.split("\n") if "Verified" in l][:3]


# ---------------------------------------------------------------- Appendix: proof details (2144-2230)
pf = rename_invariants(lines(2144, 2230))
pf = rep(pf, "the dependency graph $P$, and, for each observed belief $b$, a\nmemoized root certificate",
         "the dependency graph $P$, for each observed belief $b$ its recorded\nvalue set $\\vals(b)$, and a memoized root certificate", where="pf")
pf = rep(pf, "All three\nconditions below are decidable from the prefix state at the event\nthat would violate them.",
         "All four\nconditions below are decidable from the prefix state at the event\nthat would violate them.", where="pf")
pf = rep(pf, "$\\mathsf{viol}_3(\\sigma[..k])$ iff $\\epsilon_k = \\ev{act}(a)$\nprotected and $S(\\support(a), \\lreq(c(a))) < \\tau_{c(a)}$. Each\npredicate depends only on $\\sigma[..k]$.",
         "$\\mathsf{viol}_3(\\sigma[..k])$ iff $\\epsilon_k = \\ev{act}(a)$\nprotected and $S(\\support(a), \\lreq(c(a))) < \\tau_{c(a)}$;\n"
         "$\\mathsf{viol}_4(\\sigma[..k])$ iff $\\epsilon_k = \\ev{act}(a)$ protected\nand some bound slot $s \\in \\bindpol(c(a))$ with $\\args(a)(s)$ defined\n"
         "has no $b \\in \\support(a)$ with $\\args(a)(s) \\in \\vals(b)$ and\n$\\ell(b) \\sqsupseteq \\ell_{\\bindpol}(c(a), s)$. Each\npredicate depends only on $\\sigma[..k]$.", where="pf")
pf = rep(pf, "driven by $\\mathsf{viol}_j$\n(Fig.~\\ref{fig:boundary}a).", "driven by $\\mathsf{viol}_j$.", where="pf-fig")
pf = rep(pf, "enforcement cost is the per-event predicate evaluation measured in\nTable~\\ref{tab:overhead} and Appendix~\\ref{app:refsem}.",
         "enforcement cost is the per-event predicate evaluation measured in\nTable~\\ref{tab:overhead} and Appendix~\\ref{app:refsem}; the\n$\\mathsf{viol}_4$ test adds set membership on recorded value sets and\nchanges neither fact.", where="pf")
pf = rep(pf, "differential harness of \\S\\ref{sec:falsifiability}.", "differential harness of \\S\\ref{sec:falsifiability} and, before dispatch, as the gate of \\S\\ref{sec:gate}.", where="pf")

# ---------------------------------------------------------------- Appendix: crosswalk table (2113-2140), add corpus share
cw = rename_invariants(lines(2113, 2140))
cw = rep(cw, "\\caption{Crosswalk from the registered charting classes (\\S\\ref{sec:taxonomy}) to the invariants each attack must violate.\n``Ref.\\ suite'' = violated as predicted in the executable reference semantics (Appendix~\\ref{app:refsem}: 10/10, no\ncoverage counterexamples, no false positives on honest baselines), a semantics check distinct from the\nlive-deployment campaign of \\S\\ref{sec:redteam}. Marked scope boundaries are pre-declared, so success against them is\n\\emph{not} a coverage counterexample.}",
         "\\caption{Crosswalk from the registered charting classes (\\S\\ref{sec:taxonomy}) to the invariants each attack must violate, with each class's share of the 552-record core corpus.\n``Ref.\\ suite'' = violated as predicted in the executable reference semantics (Appendix~\\ref{app:refsem}: 10/10, no\ncoverage counterexamples, no false positives on honest baselines), a semantics check distinct from the\nlive measurements of \\S\\ref{sec:eval}. Marked scope boundaries are pre-declared, so success against them is\n\\emph{not} a coverage counterexample. The mapping was frozen before any campaign was scored against it; \\Ifour{} secondaries are not part of the registered mapping.}", where="cw")
cw = rep(cw, "\\begin{tabularx}{\\textwidth}{@{}>{\\raggedright\\arraybackslash}p{2.9cm} c c >{\\raggedright\\arraybackslash}p{3.1cm} >{\\raggedright\\arraybackslash}X >{\\raggedright\\arraybackslash}p{2.2cm}@{}}\n\\toprule\nCharting class & Prim. & Sec. & Derived mechanism & Predicted refutation signal & Status \\\\",
         "\\begin{tabularx}{\\textwidth}{@{}>{\\raggedright\\arraybackslash}p{2.7cm} r c c >{\\raggedright\\arraybackslash}p{2.9cm} >{\\raggedright\\arraybackslash}X >{\\raggedright\\arraybackslash}p{2.0cm}@{}}\n\\toprule\nCharting class & Share & Prim. & Sec. & Derived mechanism & Predicted refutation signal & Status \\\\", where="cw")
shares = {
 "misinformation \\& disinformation & ": "misinformation \\& disinformation & 29.2\\% & ",
 "hallucination \\& factuality failure & ": "hallucination \\& factuality failure & 25.0\\% & ",
 "prompt injection \\& jailbreak & ": "prompt injection \\& jailbreak & 17.0\\% & ",
 "provenance or identity tampering & ": "provenance or identity tampering & 5.6\\% & ",
 "retrieval \\& knowledge poisoning & ": "retrieval \\& knowledge poisoning & 4.2\\% & ",
 "(retrieval boundary case) & ": "(retrieval boundary case) & --- & ",
 "data or model poisoning/backdoor & ": "data or model poisoning/backdoor & 3.4\\% & ",
 "confidence or trust manipulation & ": "confidence or trust manipulation & 3.4\\% & ",
 "tool or agent hijacking (incl.\\ MCP tool-description poisoning) & ": "tool or agent hijacking (incl.\\ MCP tool-description poisoning) & 2.9\\% & ",
 "drift, staleness, or benign reliability failure & ": "drift, staleness, or benign reliability failure & 0.2\\% & ",
 "no adversarial mechanism (control/eval.) & ": "no adversarial mechanism (control/eval.) & 9.1\\% & ",
}
for k, v in shares.items():
    cw = rep(cw, k, v, where="cw-share")

cw = rep(cw, "terminates in no evidence atom (Def.~5)", "terminates in no evidence atom (Def.~\\ref{def:i1})", where="cw-def")
cw = rep(cw, "admitted evidence (Def.~2); or accumulated", "admitted evidence (Def.~\\ref{def:evidence}); or accumulated", where="cw-def")

cw = rep(cw, "composes beneath (\\S\\ref{sec:rugpull})", "composes beneath (\\S\\ref{sec:redteam})", where="cw")

# ---------------------------------------------------------------- Appendix: reference semantics text (2320-2342) + Table VII (2343-2372)
rs = rename_invariants(lines(2320, 2342))
rs = rep(rs, "reference implementation of Definitions 1--9:", "reference implementation of Definitions~\\ref{def:policy}--\\ref{def:dei}:", where="rs")
rs = rep(rs, "enforcing \\Ione--\\Ifour{} with receipt-based $O(1)$ root\nverification,", "enforcing \\Ione--\\Ifour{} with receipt-based $O(1)$ root\nverification (the \\Ifour{} slot check is the one in the v9 gateway of \\S\\ref{sec:czta}),", where="rs")
rs = rep(rs, "Table~\\ref{tab:refsem} reports the results:\nthe monitor blocks", "The results: the monitor blocks", where="rs-tab7")
rs = rep(rs, "the \\Ifive{} harness flags\nan injection-obeying decision function (with concrete witness\npairs) while clearing a guarded one;",
         "the \\Ifive{} harness flags an injection-obeying decision function\n(21 perturbation pairs per decision function; 71\\,\\% invariance, 6\nwitness pairs) while clearing a guarded one (100\\,\\% invariance, 0\nwitnesses);", where="rs-tab7")
rs = rep(rs, "Thirteen property tests\nadditionally confirm each per-invariant admit/block case and that\nblocking preserves trace legality (the executable content of\nProposition~\\ref{prop:safety}(ii)).",
         "Thirteen property tests\nadditionally confirm each per-invariant admit/block case and that\nblocking preserves trace legality (the executable content of\nProposition~\\ref{prop:safety}(ii)). At workload scale on the\nsmall-model development driver, the \\Ifive{} harness ran 60 checks (12\ntasks $\\times$ 5 pre-registered $\\Dirrel$ families) with verdict\ninvariance 86.7\\,\\% (52/60; Wilson $[75.8, 93.1]$) and action\ninvariance 68.3\\,\\% (41/60; $[55.8, 78.7]$); reordering was fully\ninvariant (12/12) and inject-then-ignore the sharpest family (7/12).\nSince the monitor is deterministic given a support set, every flip is\na grounding-stability property of the agent under task-irrelevant\nedits, which is the reason the live-model evaluation of\n\\S\\ref{sec:eval} is needed to exercise it against a capable agent.", where="rs")
tab7 = rename_invariants(lines(2343, 2372))
tab7 = rep(tab7, "\\quad Memoized \\Ione{} check, cost span over $256\\times$ depth & $1.42\\times$ \\\\", "\\quad Memoized \\Ione{} check, cost span over $256\\times$ depth & $1.42\\times$ \\\\", where="tab7")

maturity = r"""
\begin{table}[!htb]\centering\footnotesize
\caption{Evidence maturity: what is measured versus registered-pending.
No claim in the contribution set depends on a row marked
\emph{registered}; rows marked \emph{pending} are the runs of
\S\ref{sec:eval} whose designs are deposited before execution.}
\label{tab:maturity}
\setlength{\tabcolsep}{4pt}
\renewcommand{\arraystretch}{1.12}
\begin{tabularx}{\linewidth}{@{}>{\raggedright\arraybackslash}X >{\raggedright\arraybackslash}X l@{}}
\toprule
Claim & Basis & Status \\
\midrule
\Ione--\Ithree{} EM-enforceable & Prop.~\ref{prop:safety}; Lean~4 kernel check & \textbf{proved} \\
\Ifour{} EM-enforceable & Prop.~\ref{prop:safety}; Lean~4 kernel check & \textbf{proved} \\
\Ifive{} not single-trace enforceable & Prop.~\ref{prop:hyper} & \textbf{proved} \\
Choice laundering admission-undetectable & Cor.~\ref{cor:ratgap} & \textbf{proved} \\
Monitor overhead (replacement-2, A0/A1/A2) & Keycloak + MCP, 3 rates$\times$3 restarts & \textbf{measured} (v4 deposit) \\
Reference-semantics coverage 10/10, 3/3 honest & constructed suite (App.~\ref{app:refsem}) & \textbf{measured} (semantics check) \\
Authorization-layer checks & live gateway: 3 prevented, 1 detected-not-prevented, 1 boundary & \textbf{measured} \\
Pilot grid (protected-tool filter): ASR 0.45 $\to$ 0.05; benign cost unresolved & gemini-2.5-flash, $n{=}40$/arm; $n{=}24$/arm & \textbf{measured} (development) \\
Rationalization counterexample and oracle-gate quarantine & development probes, small-model driver & \textbf{measured} (existence) \\
Baselines B1--B3 & seven-arm registered campaign & \textbf{measured} \\
Gate value on choice laundering; $\mathit{fp}$, $\mathit{miss}$ & registered probes + oracle; limits reported & \textbf{measured} \\
Powered utility cost (RQ3) & 291 pairs per contrast, MID 10 points & \emph{pending} \\
Generality (RQ4) & registered design; AgentDyn not run & \emph{pending} \\
\Ifour{} in \texttt{czta\_ref} & v9 implementation & \textbf{implemented} \\
\bottomrule
\end{tabularx}
\end{table}
"""

# ---------------------------------------------------------------- Appendix: mechanism predicates + proofs (2376-2626)
mp = rename_invariants(lines(2376, 2626))
for old, new in [
    ("Appendix~A(a)", "Appendix~\\ref{app:proofs}(a)"),
    ("App.~A(a)", "App.~\\ref{app:proofs}(a)"),
    ("App.~A(b)", "App.~\\ref{app:proofs}(b)"),
    ("App.~A(c)", "App.~\\ref{app:proofs}(c)"),
    ("App.~A(d)", "App.~\\ref{app:proofs}(d)"),
    ("Appendix~A(c)", "Appendix~\\ref{app:proofs}(c)"),
]:
    mp = mp.replace(old, new)
assert "App.~A(" not in mp and "Appendix~A(" not in mp
mp = rep(mp, "By Definition~11 there is a prefix", "By Definition~\\ref{def:mech} there is a prefix", where="mp")
mp = rep(mp, "registered anchor extension of \\S III-C", "registered anchor extension of \\S\\ref{sec:taxonomy}", where="mp")
mp = rep(mp, "Algorithm~1 evaluates\n$\\mathit{viol}_1$, $\\mathit{viol}_2$, $\\mathit{viol}_3$ on every\ncandidate event",
         "Algorithm~\\ref{alg:monitor} evaluates\n$\\mathit{viol}_1$, \\ldots, $\\mathit{viol}_4$ on every\ncandidate event", where="mp")
mp = rep(mp, "By Assumption~1,\n$\\epsilon_{k^{*}}$ is mediated by the gateway", "By Assumption~\\ref{asm:mediation},\n$\\epsilon_{k^{*}}$ is mediated by the gateway", where="mp")
mp = rep(mp, "Assumptions~1--2, the latter placing", "Assumptions~\\ref{asm:mediation}--\\ref{asm:recorded}, the latter placing", where="mp")
mp = rep(mp, "Algorithm~1 suppresses an event only when a\npredicate fires on it", "Algorithm~\\ref{alg:monitor} suppresses an event only when a\npredicate fires on it", where="mp")
mp = rep(mp, "That is the executed witness of Appendix~B:", "That is the executed witness of Appendix~\\ref{app:refsem}:", where="mp")
mp = rep(mp, "distinct from the live-deployment\ncampaign of \\S V-E, and the evidence", "distinct from the live measurements\nof \\S\\ref{sec:eval}, and the evidence", where="mp")
# Corollary 2 proof: restrict the existence construction to A_beta(S0)
mp = rep(mp, "The compromised model selects the injection-chosen protected\naction $a^{*}$ with $c(a^{*}) = c_0$ and commits $\\mathit{act}(a^{*})$\nwith $\\mathit{support}(a^{*}) = S_0$, issuing no $\\mathit{upd}$\nabove the meet and no $\\mathit{end}$.",
         "The compromised model selects the injection-chosen protected\naction $a^{*} \\in A_{\\bindpol}(S_0)$ with $c(a^{*}) = c_0$---so every\nbound argument of $a^{*}$ is named by some $b \\in S_0$ at the label\n$\\bindpol$ requires---and commits $\\mathit{act}(a^{*})$\nwith $\\mathit{support}(a^{*}) = S_0$, issuing no $\\mathit{upd}$\nabove the meet and no $\\mathit{end}$.", where="mp-cor2")
mp = rep(mp, "and $S(S_0, \\lreq(c(a^{*}))) =\nS(S_0, \\lreq(c_0)) \\geq \\tc$, so $\\neg\\mathit{viol}_3$. Every\nprefix of $\\sigma^{*}$ is therefore $\\mathit{viol}$-free,",
         "$S(S_0, \\lreq(c(a^{*}))) =\nS(S_0, \\lreq(c_0)) \\geq \\tc$, so $\\neg\\mathit{viol}_3$; and every bound\nslot of $a^{*}$ is named by a belief in $S_0$ at the required label by\nthe choice $a^{*} \\in A_{\\bindpol}(S_0)$, so $\\neg\\mathit{viol}_4$. Every\nprefix of $\\sigma^{*}$ is therefore $\\mathit{viol}$-free,", where="mp-cor2")
mp = rep(mp, "not by $S_0$'s evidence: the \\S\\ref{sec:definition}-H(2) shape.", "not by $S_0$'s evidence: the faithfulness gap of \\S\\ref{sec:limitations}(2).", where="mp-cor2")
mp = rep(mp, "granularity (\\S\\ref{sec:definition}-H(3)) leaves the certificates and", "granularity (\\S\\ref{sec:limitations}(2)) leaves the certificates and", where="mp-cor2")
mp = rep(mp, "Instantiate\nProposition~2's construction (App.~\\ref{app:proofs}(d)) with $\\epsilon = 0$ and the\n$0/1$ metric of Def.~8,",
         "Instantiate\nProposition~\\ref{prop:hyper}'s construction (App.~\\ref{app:proofs}(d)) with $\\epsilon = 0$ and the\n$0/1$ metric of Def.~\\ref{def:i5},", where="mp-cor2")
mp = rep(mp, "exactly as stipulated in\nProposition~4---and $\\delta_1$ is plant removal:", "exactly as stipulated in\nProposition~\\ref{prop:gatesound}---and $\\delta_1$ is plant removal:", where="mp-cor2")
mp = rep(mp, "such a detector would be exactly a single-trace monitor of an\n$\\Ifive$-fragment, contradicting Proposition~2.", "such a detector would be exactly a single-trace monitor of an\n$\\Ifive$-fragment, contradicting Proposition~\\ref{prop:hyper}.", where="mp-cor2")
mp = rep(mp, "the pre-registered differential\nharness (\\S\\ref{sec:definition}-E) or the decision-local gate\n(\\S V-G; Def.~10 below).",
         "the pre-registered differential\nharness (\\S\\ref{sec:falsifiability}) or the decision-local gate\n(\\S\\ref{sec:gate}, Algorithm~\\ref{alg:gate}).", where="mp-cor2")
mp = rep(mp, "\\begin{proof}[Proof of Corollary~2 (rationalization-gap impossibility)]", "\\begin{proof}[Proof of Corollary~\\ref{cor:ratgap} (rationalization gap)]", where="mp-cor2")
mp = rep(mp, "\\begin{proof}[Proof of Theorem~1 (crosswalk soundness)]", "\\begin{proof}[Proof of Theorem~\\ref{thm:crosswalk} (crosswalk soundness)]", where="mp-thm1")
mp = rep(mp, "satisfies the $\\epsilon = 0$ $\\Ifive$-fragment for $\\delta_1$,", "satisfies the $\\epsilon = 0$ $\\Ifive$-fragment for $\\delta_1$,", where="mp")
# the S^+ / S^- event streams: both also satisfy I4 by construction; say so once
mp = rep(mp, "$D$ receives identical observed prefixes under both systems, so its\nverdict on the final commitment is identical under both.",
         "Both streams satisfy $\\mathit{viol}$-freedom for $j \\in \\{1,2,3,4\\}$ by the\nchoice $a^{*} \\in A_{\\bindpol}(S_0)$. $D$ receives identical observed prefixes under both systems, so its\nverdict on the final commitment is identical under both.", where="mp-cor2")

mp = rep(mp, "evidence atom (Def.~5(i))---the formal shape of a fabricated claim---so", "evidence atom (Def.~\\ref{def:i1}(i))---the formal shape of a fabricated claim---so", where="mp-def")
mp = rep(mp, "identity does not verify against the trusted root, Def.~2), so", "identity does not verify against the trusted root, Def.~\\ref{def:evidence}), so", where="mp-def")
mp = rep(mp, "(Def.~2 evaluates $\\att(e)$ against the current time), so", "(Def.~\\ref{def:evidence} evaluates $\\att(e)$ against the current time), so", where="mp-def")
mp = rep(mp, "within their attestation validity windows (Def.~2)---with $S(S_0,", "within their attestation validity windows (Def.~\\ref{def:evidence})---with $S(S_0,", where="mp-def")
mp = rep(mp, "(Def.~3), so $\\neg\\mathit{viol}_2$;", "(Def.~\\ref{def:beliefs}), so $\\neg\\mathit{viol}_2$;", where="mp-def")
assert "Def.~2" not in mp and "Def.~3" not in mp and "Def.~5" not in mp and "Def.~8" not in mp
# shorten the granularity sentence chain in the Cor 2 existence proof
_g0 = mp.index("Granularity: the certificates and the score")
_g1 = mp.index("(ii)~\\emph{Necessity.}")
mp = mp[:_g0] + "Granularity: the certificates, the score, and the binding test are\nfunctions of the attestation status, labels, weights, and recorded\nvalues of the cited evidence, all of which are genuine, so no\nrefinement of label or provenance granularity changes them; and the\nnecessity argument below is granularity-independent, since its two\nsystems emit the same refined stream.\n\n" + mp[_g1:]
# shorten the "proved content vs empirical support" paragraph of the Thm 1 proof
_p0 = mp.index("\\emph{Proved content vs.\\ empirical support.}")
_p1 = mp.index("\\end{proof}", _p0)
mp = mp[:_p0] + "\\emph{Proved content vs.\\ empirical support.} What is proved is the\nimplication in both directions for every trace over $\\Tr$. What is\nempirical is that actual attack instances charted as class $K$ realize\n$\\mathrm{Mech}_K$, i.e., that the predicates are non-vacuous and\ncorrectly named row by row: on the instrumented reference suite the\npredicted invariant fired on 10/10 constructed instances and no\npredicate fired on the 3/3 honest baselines (Appendix~\\ref{app:refsem}),\na semantics check distinct from the live measurements of\n\\S\\ref{sec:eval}.\n" + mp[_p1:]

assert "Def.~10" not in mp and "Definition~11" not in mp and "Proposition~2" not in mp and "Proposition~4" not in mp
assert "Assumption~1," not in mp and "Algorithm~1 " not in mp

# ---------------------------------------------------------------- Appendix: gate probe table (2899-2913) and red-team table (2946-2970)
gt = rename_invariants(lines(2899, 2913)).replace("\\begin{table}[t]", "\\begin{table}[!htb]")
gt = rep(gt, "\\caption{Rationalization probes under the gate (existence, not rates).}", "\\caption{Development probes under the oracle gate (small-model driver; existence, not rates). Both laundering follows are \\Ifour-catchable (Remark~\\ref{rem:residual}); the registered choice-laundering probes of \\S\\ref{sec:rq2} are the pending test of incremental value.}", where="gt")
rt = rename_invariants(lines(2946, 2970)).replace("\\begin{table}[t]", "\\begin{table}[!htb]")
rt = rep(rt, "(\\S\\ref{sec:rugpull})", "(\\S\\ref{sec:redteam})", where="rt")

appendix = "\n".join([
    "\\appendices",
    "\\section{Proof Details}\n\\label{app:proofs}",
    pf,
    "\\section{Charting-Class to Invariant Crosswalk}\n\\label{app:crosswalk}\nThe full crosswalk table, with per-class mechanisms, refutation signals, and corpus shares, is included in the anonymized artifact rather than printed here.\n",
    "\\section{Mechanism Predicates and Proofs of Theorem~\\ref{thm:crosswalk} and Corollary~\\ref{cor:ratgap}}\n\\label{app:t1c2}\n" + (P / "90_appendixB.tex").read_text().replace("Table~\\ref{tab:crosswalk}", "Appendix~\\ref{app:crosswalk}"),
    "\\section{Executable Reference Semantics and Evidence Maturity}\n\\label{app:refsem}\n" + (P / "93_appendixD.tex").read_text(),
])

# ---------------------------------------------------------------- assemble
parts = ["00_preamble.tex", "01_intro.tex", "02_background.tex", "03_definition.tex", "04_czta.tex", "05_gate.tex", "06_eval.tex", "07_related_end.tex"]
body = "\n\n".join((P / p).read_text() for p in parts)
body = rep(body, "%%ALG1%%", alg, where="assemble-alg1")
doc = body + "\n\n" + bib + "\n\n" + appendix + "\n\n\\end{document}\n"
assert "\\input{results_macros}" in doc
OUT.write_text(doc)
print("wrote", OUT, len(doc.split("\n")), "lines; PENDING markers:", doc.count("\\PENDING{"))
