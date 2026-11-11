# Bibliography annotations removed from the submission .tex

The NDSS version carried reviewer-facing verification notes inside the
`\bibitem` entries ("Verified against the arXiv record on ...", descriptive
parentheticals, version/date stamps). `build/assemble.py` strips them so the
reference list reads as a normal IEEE bibliography. The stripped text is
preserved here, keyed by citation key, so nothing is lost and the notes can
be re-checked before camera-ready.

Legend: **kept** = the entry as it now appears in `main.tex`; **removed** =
the text that was cut.

## `liao2026provenance`

**kept:** J.~Liao, ``Auditing provenance sensitivity in LLM agent action selection,'' 2026, arXiv:2607.20827.

**removed:** Matched source-authority interventions over 450 controlled tasks with coalition-interaction diagnostics; the method is stated as an evaluation, not a guardrail.

## `babu2026gistcmtf`

**kept:** R.~S.~Babu and R.~Shukla, ``GIST-CMTF: Goal-state inference for causal minimal tool filtering in LLM agents,'' 2026, arXiv:2606.16813.

## `pona2025acf`

**kept:** E.~Pona, M.~Kazemi, Y.~Du, D.~Watson, and N.~Paoletti, ``Abstract counterfactuals for language model agents,'' in \emph{Advances in Neural Information Processing Systems (NeurIPS)}, 2025; also arXiv:2506.02946.

## `camel`

**kept:** E.~Debenedetti, I.~Shumailov, T.~Fan, J.~Hayes, N.~Carlini, D.~Fabian, et~al., ``Defeating prompt injections by design,'' 2025, arXiv:2503.18813; IEEE SaTML 2026.

## `cxi`

**kept:** I.~Santos-Grueiro, ``Context-to-execution integrity for LLM agents,'' 2026, arXiv:2607.06000.

**removed:** Verified against the arXiv record on 17 July 2026 (deterministic admission gate binding field, effect, and invocation authority to one action manifest; 720 AgentDojo episodes / 1{,}739 calls; 400-episode code-agent benchmark, zero observed escapes).

## `guardagent`

**kept:** Z.~Xiang et~al., ``GuardAgent: Safeguard LLM agents by a guard agent via knowledge-enabled reasoning,'' 2024, arXiv:2406.09187; ICML 2025.

## `argus`

**kept:** S.~Weng, Y.~Feng, J.~Zhang, X.~Xie, J.~Yu, and J.~Liu, ``ARGUS: Defending LLM agents against context-aware prompt injection,'' 2026, arXiv:2605.03378.

**removed:** S.~Weng, Y.~Feng, J.~Zhang, X.~Xie, J.~Yu, and J.~Liu, ``ARGUS: Defending LLM agents against context-aware prompt injection,'' 2026, arXiv:2605.03378 (influence provenance graph; verifies decisions justified by trustworthy evidence pre-execution).

## `ray2026enforced`

**kept:** S.~Ray, ``What can be enforced? A theory of certified runtime safety for tool-using agents,'' 2026, arXiv:2607.22868.

**removed:** Verified against the arXiv record on 2 August 2026.

## `romanchuk2026semantic`

**kept:** O.~Romanchuk and R.~Bondar, ``Semantic laundering in AI agent architectures: Why tool boundaries do not confer epistemic warrant,'' 2026, arXiv:2601.08333.

**removed:** Verified against the arXiv record on 2 August 2026.

## `louck2026tmanm`

**kept:** Y.~Louck, ``Securing LLM-agent long-term memory against poisoning: Non-malleable, origin-bound authority with machine-checked guarantees,'' 2026, arXiv:2606.24322.

**removed:** Verified against the arXiv record on 2 August 2026.

## `ztmcp`

**kept:** S.~Mishra, ``ZT-MCP: A zero-trust security architecture for MCP-connected AI agents,'' 2026, ResearchGate preprint, doi:10.13140/RG.2.2.36042.53445.

**removed:** Verified against the ResearchGate record on 2 August 2026.

## `kodathala2026aiauthz`

**kept:** S.~V.~Kodathala, ``aiAuthZ: Off-host, identity-bound authorization for AI agents,'' 2026, arXiv:2607.05518.

**removed:** Verified against the arXiv record on 2 August 2026.

## `melon`

**kept:** K.~Zhu, X.~Yang, J.~Wang, W.~Guo, and W.~Y.~Wang, ``MELON: Provable defense against indirect prompt injection attacks in AI agents,'' in \emph{Proc.\ ICML}, 2025; also arXiv:2502.05174.

**removed:** Verified against the arXiv record on 2 August 2026.

## `agentsentry`

**kept:** T.~Zhang, Y.~Xu, J.~Wang, \emph{et al.}, ``AgentSentry: Mitigating indirect prompt injection in LLM agents via temporal causal diagnostics and context purification,'' 2026, arXiv:2602.22724.

**removed:** Verified against the arXiv record on 2 August 2026.

## `causalarmor`

**kept:** M.~Kim, M.~Parmar, P.~Wallis, \emph{et al.}, ``CausalArmor: Efficient indirect prompt injection guardrails via causal attribution,'' 2026, arXiv:2602.07918.

**removed:** Verified against the arXiv record on 2 August 2026.

## `oob`

**kept:** LaunchSafe Research, ``Adaptive evaluation of out-of-band defenses against prompt injection in LLM agents,'' 2026, arXiv:2606.26479.

**removed:** LaunchSafe Research, ``Adaptive evaluation of out-of-band defenses against prompt injection in LLM agents,'' 2026, arXiv:2606.26479 (systematizes CaMeL/FIDES/Progent/RTBAS/Conseca/FORGE as Biba $+$ reference monitor $+$ least privilege; flags static-benchmark validation and under-specified provenance base).

## `qu`

**kept:** W.~Qu, M.~Xu, P.~Wang, S.~Zhai, J.~Zhang, and D.~Song, ``Securing LLM agents need intent-to-execution integrity,'' 2026, arXiv:2605.16976.

**removed:** Verified against the arXiv record on 17 July 2026 (position paper; Tool/Instruction/Judgment/Data-Flow Integrity).

## `shen`

**kept:** Z.~Shen, ``Neither layer alone: Epistemic integrity requires hierarchical joint design for long-running AI agents,'' 2026, arXiv:2606.04017, posted 1 June 2026.

**removed:** Verified against the arXiv record on 17 July 2026 (AEI as first-class architectural constraint via an explicit model--harness interface contract; ``interface volatility'').

## `greshake`

**kept:** K.~Greshake, S.~Abdelnabi, S.~Mishra, C.~Endres, T.~Holz, and M.~Fritz, ``Not what you've signed up for: Compromising real-world LLM-integrated applications with indirect prompt injection,'' in \emph{Proceedings of the 16th ACM Workshop on Artificial Intelligence and Security (AISec)}, 2023.

## `abdelnabi`

**kept:** S.~Abdelnabi and E.~Bagdasarian, ``AI agents may always fall for prompt injections,'' 2026, arXiv:2605.17634.

**removed:** S.~Abdelnabi and E.~Bagdasarian, ``AI agents may always fall for prompt injections,'' 2026, arXiv:2605.17634 (impossibility-style argument for in-band robustness).

## `agentdojo`

**kept:** E.~Debenedetti, J.~Zhang, M.~Balunovi\'c, L.~Beurer-Kellner, M.~Fischer, and F.~Tram\`er, ``AgentDojo: A dynamic environment to evaluate prompt injection attacks and defenses for LLM agents,'' in \emph{NeurIPS Datasets and Benchmarks}, 2024.

## `benchtax`

**kept:** M.~Q.~Li, B.~C.~M.~Fung, B.~Li, H.~Ismail, and F.~Iqbal, ``Taxonomy and consistency analysis of safety benchmarks for AI agents,'' 2026, arXiv:2605.16282.

**removed:** M.~Q.~Li, B.~C.~M.~Fung, B.~Li, H.~Ismail, and F.~Iqbal, ``Taxonomy and consistency analysis of safety benchmarks for AI agents,'' 2026, arXiv:2605.16282 (consolidates ASB, AgentDojo, InjecAgent, WASP, MCP-SafetyBench, memory/RAG benchmarks).

## `mcpspec`

**kept:** Model Context Protocol contributors, ``Model context protocol specification,'' Specification revision 2025-11-25 (authorization framework), 2025.

## `owaspmcp`

**kept:** OWASP Foundation, ``OWASP MCP top 10 (beta),'' 2026; Tool Poisoning listed (MCP03).

**removed:** Cited alongside the current MCP specification's authorization section (spec rev.\ 2025-11-25).

## `mcpdpt`

**kept:** M.~Rostamzadeh, S.~Narula, N.~Birhan, M.~Ghasemigol, and D.~Takabi, ``MCP-DPT: A defense-placement taxonomy and coverage analysis for MCP security,'' 2026, arXiv:2604.07551.

**removed:** M.~Rostamzadeh, S.~Narula, N.~Birhan, M.~Ghasemigol, and D.~Takabi, ``MCP-DPT: A defense-placement taxonomy and coverage analysis for MCP security,'' 2026, arXiv:2604.07551 (layer-aligned taxonomy organizing attacks by enforcing component).

## `biba`

**kept:** K.~J. Biba, ``Integrity considerations for secure computer systems,'' MITRE Corporation, Tech.\ Rep.\ ESD-TR-76-372, 1977.

## `denning`

**kept:** D.~E. Denning, ``A lattice model of secure information flow,'' \emph{Communications of the ACM}, vol.~19, no.~5, pp.~236--243, 1976.

## `clarkwilson`

**kept:** D.~D. Clark and D.~R. Wilson, ``A comparison of commercial and military computer security policies,'' in \emph{IEEE Symposium on Security and Privacy}, 1987.

## `goguen`

**kept:** J.~A. Goguen and J.~Meseguer, ``Security policies and security models,'' in \emph{IEEE Symposium on Security and Privacy}, 1982.

## `myersliskov`

**kept:** A.~C. Myers and B.~Liskov, ``A decentralized model for information flow control,'' in \emph{ACM Symposium on Operating Systems Principles (SOSP)}, 1997.

## `prov`

**kept:** W3C, ``PROV-DM: The PROV data model,'' W3C Recommendation, 30 April 2013, 2013.

## `shafer`

**kept:** G.~Shafer, \emph{A Mathematical Theory of Evidence}. Princeton University Press, 1976.

## `dung`

**kept:** P.~M. Dung, ``On the acceptability of arguments and its fundamental role in nonmonotonic reasoning, logic programming and n-person games,'' \emph{Artificial Intelligence}, vol.~77, no.~2, pp.~321--357, 1995.

## `alpern`

**kept:** B.~Alpern and F.~B. Schneider, ``Recognizing safety and liveness,'' \emph{Distributed Computing}, vol.~2, no.~3, pp.~117--126, 1987.

## `schneider`

**kept:** F.~B. Schneider, ``Enforceable security policies,'' \emph{ACM Transactions on Information and System Security}, vol.~3, no.~1, pp.~30--50, 2000.

## `bauer`

**kept:** A.~Bauer, M.~Leucker, and C.~Schallhart, ``Runtime verification for LTL and TLTL,'' \emph{ACM Transactions on Software Engineering and Methodology}, vol.~20, no.~4, 2011.

## `pnueli`

**kept:** A.~Pnueli and A.~Zaks, ``PSL model checking and run-time verification via testers,'' in \emph{International Symposium on Formal Methods (FM)}, 2006.

## `mop`

**kept:** F.~Chen and G.~Ro\c{s}u, ``MOP: An efficient and generic runtime verification framework,'' in \emph{ACM OOPSLA}, 2007.

## `hyperprops`

**kept:** M.~R. Clarkson and F.~B. Schneider, ``Hyperproperties,'' \emph{Journal of Computer Security}, vol.~18, no.~6, pp.~1157--1210, 2010.

## `finkbeiner`

**kept:** B.~Finkbeiner, C.~Hahn, M.~Stenger, and L.~Tentrup, ``Monitoring hyperproperties,'' \emph{Formal Methods in System Design}, vol.~54, pp.~336--363, 2019.

## `stucki`

**kept:** S.~Stucki, C.~S\'anchez, G.~Schneider, and B.~Bonakdarpour, ``Gray-box monitoring of hyperproperties,'' in \emph{International Symposium on Formal Methods (FM)}, 2019.

## `tracessurvey`

**kept:** Y.~Wang et~al., ``From agent traces to trust: A survey of evidence tracing and execution provenance in LLM agents,'' 2026, arXiv:2606.04990.

**removed:** Y.~Wang et~al., ``From agent traces to trust: A survey of evidence tracing and execution provenance in LLM agents,'' 2026, arXiv:2606.04990 (provenance taxonomy: static schema vs.\ runtime provenance; Support/Depend-on/Contradict/Update/Invalidate relations).

## `controlroadmap`

**kept:** M.~Phuong, E.~Jenner, L.~Simon, L.~Ho, R.~Shah, S.~Farquhar, and S.~Coull, ``AI control roadmap / three layers of agent security,'' Google DeepMind report and blog, 18 June 2026.

**removed:** M.~Phuong, E.~Jenner, L.~Simon, L.~Ho, R.~Shah, S.~Farquhar, and S.~Coull, ``AI control roadmap / three layers of agent security,'' Google DeepMind report and blog, 18 June 2026 (defense-in-depth for potentially misaligned internal agents; zero-trust north star; 15 system-level defenses).

## `seger`

**kept:** E.~Seger, S.~Avin, G.~Pearson, M.~Briers, S.~\'O h\'Eigeartaigh, and H.~Bacon, ``Tackling threats to informed decision-making in democratic societies: Promoting epistemic security in a technologically-advanced world,'' The Alan Turing Institute, Tech.\ Rep., 2020.

## `prisma`

**kept:** A.~C. Tricco et~al., ``PRISMA extension for scoping reviews (PRISMA-ScR): Checklist and explanation,'' \emph{Annals of Internal Medicine}, vol.~169, no.~7, pp.~467--473, 2018.

## `gwet`

**kept:** K.~L. Gwet, ``Computing inter-rater reliability and its variance in the presence of high agreement,'' \emph{British Journal of Mathematical and Statistical Psychology}, vol.~61, no.~1, pp.~29--48, 2008.

## `cohen`

**kept:** J.~Cohen, ``A coefficient of agreement for nominal scales,'' \emph{Educational and Psychological Measurement}, vol.~20, no.~1, pp.~37--46, 1960.

## `wilson`

**kept:** E.~B. Wilson, ``Probable inference, the law of succession, and statistical inference,'' \emph{Journal of the American Statistical Association}, vol.~22, no.~158, pp.~209--212, 1927.

## `artifact`, `bhagwatkar2025firewalls`, `agentdyn` (new in the S&P version)

`bhagwatkar2025firewalls`: R. Bhagwatkar, K. Kasa, A. Puri, G. Huang, I. Rish, G. W. Taylor,
K. Dj Dvijotham, A. Lacoste, "Indirect prompt injections: Are firewalls all you need, or
stronger benchmarks?" arXiv:2510.05244 (v2, 23 March 2026). Verified against the arXiv
record on 27 October 2026 (scoring-rule and implementation defects in AgentDojo; a
three-stage cascade attack whose Stage 1 is AgentDojo's `tool_knowledge` attack, Stage 2
second-order semantic templates, Stage 3 an adaptive LLM attacker). CORRECTION 1 Nov 2026: an
earlier annotation attributed a "Braille-encoded important-instructions attack" to this paper;
the arXiv v2 full text contains no such attack, and the manuscript's RQ4 second attack family is
now the benchmark's own `tool_knowledge` attack, cited as the cascade's Stage 1.

`agentdyn`: H. Li, R. Wen, S. Shi, N. Zhang, Y. Vorobeychik, C. Xiao, "AgentDyn: Are your
agent security defenses deployable in real-world dynamic environments?" arXiv:2602.03117
(v3, 7 May 2026). Verified against the arXiv record on 27 October 2026 (60 open-ended
tasks, 560 injection cases, helpful third-party instructions).

`artifact`: placeholder anonymized repository URL (anonymous.4open.science). Replace with
the real anonymized link before submission; the Availability section cites it.
