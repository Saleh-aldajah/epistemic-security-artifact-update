# Mechanized safety core (Lean 4) — `DeiSafety.lean`

Machine-checked foundation of the manuscript's §IV. Every theorem below
elaborates green under Lean `4.12.0` with **no `sorry`/`admit`** and an
axiom footprint of at most Lean's built-in `propext` (no
`Classical.choice`, no `Quot.sound`, no custom axioms). The proof kernel
re-verifies every step — correctness of this layer does not depend on
the provenance of the proof script. Re-run: `./check_formal.sh`.

## Spec-fidelity map (mechanized ↔ manuscript)

| Lean item | Manuscript location | What is mechanized |
|---|---|---|
| `EvClass` (`ing/upd/End/act`) | Def. 4 event alphabet | the four event classes |
| `Obs` record | App. A(a) "each predicate depends only on the prefix state at the event" | the per-event snapshot the monitor evaluates (certificate, freshness, label-transition, score, class, protection) |
| `viol1` | App. A(a) viol₁ | protected `act` with bad certificate **or** failed action-time freshness re-check — **both** disjuncts, incl. the WindowValid clause |
| `viol2` | App. A(a) viol₂ | **both** disjuncts: label-raising `upd`/`End` other than by an authorized endorsement, and `upd` assigning a label not dominated by the meet of its inputs |
| `viol3` | App. A(a) viol₃ | protected `act` with aggregator score below τ_c |
| `violFree` | I1 ∧ I2 ∧ I3 over traces | the lifted property: no predicate fires at any prefix |
| `monitor` | Algorithm 1 | prefix truncation at the first firing event (Schneider execution monitor) |
| `violFree_false_of_mem` | Prop. 1 (safety, occurrence form) | a firing event poisons every containing trace |
| `exists_firing_of_violFree_false` | Prop. 1 (finite bad prefix) | every violating trace decomposes into a good prefix + a firing event |
| `violFree_append_false` | Prop. 1 (irremediability) | a bad prefix stays bad under every extension |
| `safety_bad_prefix` | Prop. 1 (A–S bad prefix) | corollary packaging of the decomposition + irremediability pair, with the prefix's linkage to the trace explicit (`t = pre ++ post₀`); the two component theorems are the canonical citations |
| `violFree_monitor` | App. A(c) fact (i) — blocking preserves legality | the truncated trace satisfies the property at every prefix |
| `monitor_eq_of_violFree` | App. A(c) fact (ii) — blocking loses nothing legal | every all-good trace is admitted verbatim |
| `monitor_prefix` | EM-enforcement reading | the monitor emits a prefix of the input (no reordering/injection) |
| `witness_*` (4 theorems) | — | kernel-checked non-vacuity: truncation exactly at a freshness-firing event; verbatim admission of a good trace; the viol₁ freshness disjunct and the viol₂ meet disjunct each exercised in isolation |

**What pins truncation (and what does not).** The two legality facts
(`violFree_monitor`, `monitor_eq_of_violFree`) hold verbatim for a
*filtering* monitor as well — independently kernel-verified during the
fidelity audit. The claim that the monitor is Schneider-style prefix
truncation (halt, not filter) is pinned by `monitor`'s definition,
`monitor_prefix` (the output is a prefix of the input; a filter variant
provably fails it), and `witness_truncate_at_freshness` (the tail is
discarded at the first firing event). Cite those, not the legality
facts alone, for the truncation claim.
| `single_trace_gap`, `sPlus_stable`, `sMinus_unstable`, `gap_no_sound_verdict` | App. A(d) / Prop. 2's abstract core | no verdict of the single observed trace can soundly separate an I4-stable system from an unstable one with identical observations (S⁺/S⁻) |

## Disclosed boundary (what is NOT mechanized)

1. **State evolution.** Certificates, label maps, validity windows, and
   the aggregator are taken as the per-event snapshot (`Obs`), exactly as
   App. A(a) states the predicates. Each snapshot field carries one
   predicate clause — including both viol₁ disjuncts and both viol₂
   disjuncts — so every *clause* of the manuscript's predicates is
   mechanized; what is not mechanized is the *production* of the
   snapshots from runtime state (the memoized-cert computation, the
   meet computation, the clock). Their executable counterparts live in
   `code/dei_monitor/` (conformance separately checked by
   `analysis/theory_validation.py`, V2). The theorems quantify over ALL
   observations, including snapshots no real state could produce, which
   strengthens rather than weakens them.
2. **Infinite-trace safety.** Prop. 1 is mechanized over the
   manuscript's finite decision traces (Def. 4: "a finite sequence").
   The extension to infinite behaviors is the standard
   bad-prefix/compactness argument, stated in the paper's prose; it is
   not mechanized here.
3. **Prop. 2's full 2-safety statement.** The mechanized part is the
   non-monitorability core (identical observations ⇒ no separating
   verdict, with the explicit S⁺/S⁻ exhibit). The Clarkson–Schneider
   framework citation ([39]) stands as in the paper.
4. **The six derived results of the K theory branch** (Prop. 3–6,
   Thm. 1, Cor. 2 as staged in the archive). Not part of the baseline
   submission; not mechanized.

## Assurance statement (for the record)

Constructive, kernel-checked Lean 4 development. Axiom audit (printed at
the end of `DeiSafety.lean`, captured in `lean_check.log`): seven items
depend on no axioms at all; eight theorems depend only on `propext`
(one of Lean's three built-in axioms, introduced by `simp`; accepted as
part of Lean's trusted core). No classical axioms, no custom axioms, no
`axiom` declarations, no `sorry`/`admit`. Toolchain pinned via
`.elan` override to `leanprover/lean4:v4.12.0`. Post-audit revision
(2026-08-11): independent adversarial fidelity review (PASS) drove two
repairs — `viol2` now mechanizes both manuscript disjuncts, and
`safety_bad_prefix` states the prefix linkage explicitly (vacuous
conjunct removed); see the truncation note above.
