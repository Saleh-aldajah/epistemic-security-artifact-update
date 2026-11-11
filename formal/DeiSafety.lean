/-
  DeiSafety.lean — mechanized safety core of the DEI reference monitor.

  Scope (faithful to the manuscript's finite decision traces, Def. 4):
    * App. A(a)'s per-event violation predicates, BOTH viol₁ disjuncts
      (memoized certificate + action-time freshness re-check);
    * Prop. 1's safety claim: violation is prefix-determined and
      irremediable (bad-prefix existence + persistence);
    * App. A(c) fact (i)  — blocking preserves legality  (soundness);
    * App. A(c) fact (ii) — blocking loses nothing legal (transparency);
    * App. A(d)'s abstract single-trace gap (Prop. 2's S⁺/S⁻ core).

  Deliberately NOT mechanized (boundary disclosed in README):
    state evolution (memoized-cert computation, label maps, windows),
    the infinite-stream form of safety (standard compactness argument),
    and the six derived results of the K theory branch.

  Assurance intent: constructive throughout; `#print axioms` at the end
  must report "does not depend on any axioms" for every theorem.
-/

namespace Dei

/-- Event classes of the decision-trace alphabet (Def. 4). `End` is
    capitalized because `end` is a Lean keyword. -/
inductive EvClass where
  | ing   -- ingestion (admitted; no predicate fires)
  | upd   -- belief update (label assignment)
  | End   -- endorsement (label-raising by rule)
  | act   -- action
  deriving DecidableEq, Repr

/-- Per-event observation: the prefix-state snapshot the monitor evaluates
    at a candidate event (App. A(a): "each predicate depends only on the
    prefix state at the event that would violate them"). -/
structure Obs where
  cls         : EvClass
  prot   : Bool  -- action class ∈ C_prot (meaningful for act only)
  certBad     : Bool  -- some support belief's memoized certificate is bad (viol₁ disjunct 1)
  staleWin    : Bool  -- some support root's validity window has lapsed at action time (viol₁ disjunct 2)
  raiseUnauth : Bool  -- label-raising upd/End other than by an authorized endorsement (viol₂ disjunct 1)
  meetViol    : Bool  -- upd assigns a label not dominated by the meet of its inputs (viol₂ disjunct 2)
  belowTau    : Bool  -- aggregator score below τ_c at the required label (viol₃)
  deriving DecidableEq, Repr

/-- App. A(a): the per-event violation predicates. -/
def viol1 (o : Obs) : Bool :=
  o.cls == EvClass.act && o.prot && (o.certBad || o.staleWin)

def viol2 (o : Obs) : Bool :=
  ((o.cls == EvClass.upd || o.cls == EvClass.End) && o.raiseUnauth)
    || (o.cls == EvClass.upd && o.meetViol)

def viol3 (o : Obs) : Bool :=
  o.cls == EvClass.act && o.prot && o.belowTau

def viol (o : Obs) : Bool := viol1 o || viol2 o || viol3 o

/-- A decision trace is a finite sequence of observations (Def. 4). -/
abbrev Trace := List Obs

/-- The lifted property: no violation predicate fires at any prefix.
    Defined recursively (rather than via `List.all`) so that every proof
    below is a one-page induction with no library-lemma dependence. -/
def violFree : Trace → Bool
  | []      => true
  | o :: t  => !viol o && violFree t

/-- Algorithm 1's behavior: admit events until the first firing one, then
    truncate (suppress the event and halt). Prefix truncation, exactly
    Schneider's execution monitor for a safety property. -/
def monitor : Trace → Trace
  | []     => []
  | o :: t => if viol o then [] else o :: monitor t

/-- Boolean coercion helper: from `b = false`, the negation is true. -/
theorem neg_eq_true_of_eq_false {b : Bool} (h : b = false) : (!b) = true := by
  simp [h]

/-- Safety, occurrence form: a firing event poisons every trace containing
    it — the violation is prefix-determined and no later event repairs it. -/
theorem violFree_false_of_mem {t : Trace} {o : Obs}
    (hm : o ∈ t) (hv : viol o = true) : violFree t = false := by
  induction t with
  | nil => exact absurd hm (by simp)
  | cons x xs ih =>
    have hm' : o = x ∨ o ∈ xs := List.mem_cons.mp hm
    cases hm' with
    | inl h =>
      subst h
      simp [violFree, hv]
    | inr h =>
      by_cases hx : viol x = true
      · simp [violFree, hx]
      · have hxf : viol x = false := by
          cases vx : viol x <;> simp_all
        have := ih h
        simp [violFree, hxf, this]

/-- First-bad-event decomposition: any violating trace has a good prefix
    followed by a firing event. (The "finite bad prefix" of Prop. 1.) -/
theorem exists_firing_of_violFree_false {t : Trace} (h : violFree t = false) :
    ∃ pre o post, t = pre ++ o :: post ∧ viol o = true ∧ violFree pre = true := by
  induction t with
  | nil => simp [violFree] at h
  | cons x xs ih =>
    by_cases hx : viol x = true
    · exact ⟨[], x, xs, rfl, hx, rfl⟩
    · have hxf : viol x = false := by
        cases vx : viol x <;> simp_all
      have hxs : violFree xs = false := by
        have : violFree (x :: xs) = violFree xs := by
          simp [violFree, hxf]
        rw [this] at h; exact h
      obtain ⟨pre, o, post, ht, hv, hp⟩ := ih hxs
      refine ⟨x :: pre, o, post, ?_, hv, ?_⟩
      · rw [ht]; rfl
      · simp [violFree, hxf, hp]

/-- Irremediability: a bad prefix stays bad under every extension.
    Together with the decomposition above, this is the safety property
    in Alpern–Schneider form over finite traces. -/
theorem violFree_append_false {pre : Trace} (ext : Trace)
    (h : violFree pre = false) : violFree (pre ++ ext) = false := by
  induction pre with
  | nil => simp [violFree] at h
  | cons x xs ih =>
    by_cases hx : viol x = true
    · simp [violFree, hx]
    · have hxf : viol x = false := by
        cases vx : viol x <;> simp_all
      have hxs : violFree xs = false := by
        have : violFree (x :: xs) = violFree xs := by
          simp [violFree, hxf]
        rw [this] at h; exact h
      have := ih hxs
      simp [List.cons_append, violFree, hxf, this]

/-- Bad-prefix corollary of Prop. 1: every violating trace has a finite
    prefix OF THAT TRACE all of whose extensions violate — the
    Alpern–Schneider bad prefix, with its linkage to the trace explicit.
    (Substantively this is the decomposition
    `exists_firing_of_violFree_false` composed with irremediability
    `violFree_append_false`; the two component theorems are the
    canonical citations.) -/
theorem safety_bad_prefix {t : Trace} (h : violFree t = false) :
    ∃ pre post₀, t = pre ++ post₀ ∧ violFree pre = false ∧
      ∀ ext : Trace, violFree (pre ++ ext) = false := by
  obtain ⟨pre, o, post, ht, hv, _⟩ := exists_firing_of_violFree_false h
  have hb : violFree (pre ++ [o]) = false :=
    violFree_false_of_mem (by simp [List.mem_append]) hv
  refine ⟨pre ++ [o], post, ?_, hb, fun ext => violFree_append_false ext hb⟩
  rw [ht]
  exact (List.append_assoc pre [o] post).symm

/-- App. A(c) fact (i): blocking preserves legality — the truncated trace
    satisfies the property at every prefix. (Soundness of the monitor.) -/
theorem violFree_monitor (t : Trace) : violFree (monitor t) = true := by
  induction t with
  | nil => rfl
  | cons x xs ih =>
    by_cases hx : viol x = true
    · simp [monitor, hx, violFree]
    · have hxf : viol x = false := by
        cases vx : viol x <;> simp_all
      have h1 : monitor (x :: xs) = x :: monitor xs := by
        simp [monitor, hxf]
      have h2 : violFree (x :: monitor xs) = true := by
        simp [violFree, hxf, ih]
      rw [h1]; exact h2

/-- App. A(c) fact (ii): blocking loses nothing legal — every trace that
    satisfies the property at every prefix is admitted verbatim.
    (Transparency of the monitor.) -/
theorem monitor_eq_of_violFree {t : Trace} (h : violFree t = true) :
    monitor t = t := by
  induction t with
  | nil => rfl
  | cons x xs ih =>
    have hx : viol x = false := by
      have : violFree (x :: xs) = (!viol x && violFree xs) := rfl
      rw [this] at h
      cases vx : viol x <;> simp_all
    have hxs : violFree xs = true := by
      have : violFree (x :: xs) = (!viol x && violFree xs) := rfl
      rw [this] at h
      simp [hx] at h
      exact h
    have h1 : monitor (x :: xs) = x :: monitor xs := by
      simp [monitor, hx]
    rw [h1, ih hxs]

/-- The monitor emits a prefix of the input (no reordering, no injection):
    the truncation reading of EM-enforcement. -/
theorem monitor_prefix (t : Trace) : ∃ post, monitor t ++ post = t := by
  induction t with
  | nil => exact ⟨[], rfl⟩
  | cons x xs ih =>
    by_cases hx : viol x = true
    · refine ⟨x :: xs, ?_⟩
      simp [monitor, hx]
    · have hxf : viol x = false := by
        cases vx : viol x <;> simp_all
      obtain ⟨post, hp⟩ := ih
      refine ⟨post, ?_⟩
      have h1 : monitor (x :: xs) = x :: monitor xs := by
        simp [monitor, hxf]
      rw [h1]
      have : (x :: monitor xs) ++ post = x :: (monitor xs ++ post) := rfl
      rw [this, hp]

end Dei

open Dei

/-- Non-vacuity witnesses (kernel-checked computations): a freshness-firing
    event truncates the trace exactly before itself; an all-good trace is
    admitted verbatim; the freshness disjunct of viol₁ is exercised. -/
def oGood : Obs :=
  { cls := EvClass.act, prot := true, certBad := false,
    staleWin := false, raiseUnauth := false, meetViol := false,
    belowTau := false }

def oStale : Obs := { oGood with staleWin := true }

/-- A meet-violating update (viol₂ disjunct 2 in isolation). -/
def oUpd : Obs :=
  { cls := EvClass.upd, prot := false, certBad := false,
    staleWin := false, raiseUnauth := false, meetViol := true,
    belowTau := false }

theorem witness_truncate_at_freshness :
    monitor [oGood, oStale, oGood] = [oGood] := rfl

theorem witness_pass_verbatim :
    monitor [oGood, oGood] = [oGood, oGood] := rfl

theorem witness_freshness_disjunct :
    viol1 oStale = true ∧ viol2 oStale = false ∧ viol3 oStale = false :=
  ⟨rfl, rfl, rfl⟩

theorem witness_meet_disjunct :
    viol2 oUpd = true ∧ viol1 oUpd = false ∧ viol3 oUpd = false :=
  ⟨rfl, rfl, rfl⟩

/-- App. A(d): the abstract single-trace gap behind Prop. 2. A system
    exposes one observed trace; its I4-stability is a property of its
    hidden decision behavior. No verdict of the observed trace alone can
    soundly separate two systems with identical observations. -/
structure Sys where
  observed : Trace
  decide   : Nat → Nat
  input    : Nat

/-- I4-style stability over a perturbation family (Def. 8, ε = 0). -/
def Stable (s : Sys) (deltas : List Nat) : Prop :=
  ∀ δ ∈ deltas, s.decide (s.input + δ) = s.decide s.input

theorem single_trace_gap (V : Trace → Bool) (s₁ s₂ : Sys)
    (h : s₁.observed = s₂.observed) : V s₁.observed = V s₂.observed := by
  rw [h]

/-- The S⁺/S⁻ exhibit: identical observed traces; S⁺ stable, S⁻ flips
    under the unit perturbation (plant removal). -/
def tObs : Trace := [oGood]

def sPlus : Sys :=
  { observed := tObs, decide := fun _ => 1, input := 0 }

def sMinus : Sys :=
  { observed := tObs, decide := fun d => d, input := 1 }

theorem sPlus_stable : Stable sPlus [1] := by
  intro δ _
  rfl

theorem sMinus_unstable : ¬ Stable sMinus [1] := by
  intro h
  have hc := h 1 (List.mem_singleton_self 1)
  simp [sMinus] at hc

/-- Hence no single-trace verdict is sound for both systems: flagging the
    laundering trace flags the honest one. -/
theorem gap_no_sound_verdict (V : Trace → Bool) :
    ¬ (V sPlus.observed = true ∧ V sMinus.observed = false) := by
  rintro ⟨h1, h2⟩
  have h := single_trace_gap V sPlus sMinus rfl
  rw [h1] at h
  rw [h2] at h
  exact Bool.noConfusion h

/- Zero-axiom audit: every theorem below must print
   "does not depend on any axioms" or at worst Lean's built-in
   propext (no Classical.choice, no custom axioms, no admits). -/
#print axioms Dei.violFree_false_of_mem
#print axioms Dei.exists_firing_of_violFree_false
#print axioms Dei.violFree_append_false
#print axioms Dei.safety_bad_prefix
#print axioms Dei.violFree_monitor
#print axioms Dei.monitor_eq_of_violFree
#print axioms Dei.monitor_prefix
#print axioms witness_truncate_at_freshness
#print axioms witness_pass_verbatim
#print axioms witness_freshness_disjunct
#print axioms witness_meet_disjunct
#print axioms single_trace_gap
#print axioms sPlus_stable
#print axioms sMinus_unstable
#print axioms gap_no_sound_verdict
