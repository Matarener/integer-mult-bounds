# Gate-operand parity in Lean: the all-size agreement contract, kernel-checked

**Formal interface lemma; no new κ.** The selected κ stays
`0.001672660197076918`. This package machine-checks the exact gate-operand
agreement contract of the PR589 checker/exporter boundary: the bounded census
and informal coefficient argument of
[PR #3738](https://github.com/CrocSwap/integer-mult-bounds/pull/3738)
(itself answering [PR #3696](https://github.com/CrocSwap/integer-mult-bounds/pull/3696)
open question 1 in the [#2977](https://github.com/CrocSwap/integer-mult-bounds/pull/2977)/[#3004](https://github.com/CrocSwap/integer-mult-bounds/pull/3004)
supplier-boundary cascade) is replaced here by an all-size Lean 4 theorem with
its kernel axiom report.

```lean
theorem GateParity.sym_eq_exp_iff_contract (d : Nat) (srcs : List Nat) :
    Contract d srcs ↔ ∀ v : Nat → Bool, sym d srcs v = exp d srcs v
```

## The two operators, exactly

Over registers `Nat` and initial values `v : Nat → Bool`:

| operator | pinned source | Lean definition |
|---|---|---|
| `sym` (checker) | `research/e8-bit-p111-tuned/code/xcheck_p.py`, gate run lines 252-255: `acc = 0; for s in srcs: acc ^= val[s]; val[d] ^= acc` | `fun r => if r = d then bxor (v d) (xfold (srcs.map v)) else v r` |
| `exp` (exporter) | `research/e8-bit-carrier-skeleton/code/bit/export_records.py`, `run`: `for s in srcs: rec.append((1,d,s,1,f,ph))`, replayed as one sequential `ADD(d, s)` per source | `srcs.foldl (step d) v` with `step d x s = fun r => if r = d then bxor (x d) (x s) else x r` |

Both are one gate `(d, srcs)`; `xfold` is the XOR fold of a boolean list.

## The contract

```lean
def Contract (d : Nat) (srcs : List Nat) : Prop :=
  d ∉ srcs ∨ ∃ p t, srcs = p ++ (d :: t) ∧ d ∉ t ∧ ∀ r, EvenCount (p.count r)
```

Spelled out: the destination is absent from the source list, or the list splits
at the destination's last occurrence with every register occurring an even
number of times in the prefix `p` and no destination in the suffix `t`. The
prefix condition covers the destination itself: `EvenCount (p.count d)` is the
"odd destination multiplicity" clause of the census contract, and the remaining
clauses are the pre-last-occurrence evenness statement. This is exactly the
contract measured in `research/gate-operand-parity-contract` (PR #3738); here it
is proved for every register count and every source list, and cross-checked by
that package's finite census.

## What is machine-checked, and what is not

Machine-checked (Lean 4.21.0 core, no Mathlib, `lean/GateParity.lean`):

- **Main theorem** `sym_eq_exp_iff_contract`: agreement on every valuation iff
  `Contract`, for all `d` and all `srcs`.
- `exp_dest_free`: destination-free source lists always agree (the case used by
  every one of the selected tuned word's 5,472 D/A/B/C gates).
- `exp_split_d`: over a split `p ++ (d :: t)` with `d ∉ t`, the exporter state at
  `d` is the XOR fold over `t`.
- `allEvenCount_xfold`: if every register occurs an even number of times in a
  list, the XOR fold of any valuation over that list is `false` (the pairing
  argument, as strong induction on length).
- `xfold_indicator`: the XOR fold under the indicator valuation of `r` is the
  parity of `r`'s multiplicity; this supplies the divergent valuation whenever
  the contract fails.
- Kernel axiom reports (printed by the build):
  `sym_eq_exp_iff_contract` depends on `[propext, Classical.choice, Quot.sound]`;
  the four supporting lemmas on `[propext, Quot.sound]`. No `sorryAx`; the
  verifier also rejects `sorry`, `axiom`, `unsafe`, `partial`, `opaque`,
  `native_decide` and `run_tac` tokens in the proof source.

Not established here:

- No supplier, tariff, hosting, precision, all-size/compiler or selected-chain
  change; no new κ; no selected-frontier change. This is a boundary lemma, not a
  multiplication theorem.
- The Lean statement formalizes the two operators as functions; it does not
  replay the exporter or the checker, and the gate-list/record-stream counts of
  the pinned word remain PR #3738's and PR #3696's measurements.
- The finite census below corroborates the statement binding; the all-size
  claim is carried only by the kernel proof.

## Bounded finite cross-check

`verify.py` includes an independent standard-library implementation of both
operators and of the contract predicate, and requires, for every `(d, srcs)`
pair with 4 registers and source lists of length `≤ 4`, that agreement *on all
16 valuations* coincides with the predicate: **1,364 pairs, 708 agreeing, 656
diverging, 100 % match**. This is a statement-binding check of the Lean
definition, not a proof; it deliberately uses a domain disjoint from the
published census domain (6 registers, length ≤ 4).

## Reproduce

Standard-library mode (this is the registered command; no Lean required, and it
does not claim Lean ran):

```sh
python3.12 -B research/gate-operand-parity-lean/verify.py
python3.12 -B research/gate-operand-parity-lean/test_package.py
```

Expected:

```text
PASS_GATE_OPERAND_PARITY_LEAN pins=2 targets=5 census_pairs=1364 census_agreements=708 census_divergences=656 contract_matches=1 lean_kernel=not_run
PASS_GATE_OPERAND_PARITY_LEAN_CONTROLS controls=6 positive_total=120
```

Kernel mode (a fresh Lean build of the all-size theorem and its axiom reports):

```sh
python3.12 -B research/gate-operand-parity-lean/verify.py --lean <path>/bin/lean   # pinned Lean 4.21.0
```

Expected:

```text
PASS_GATE_OPERAND_PARITY_LEAN_KERNEL pins=2 targets=5 census_pairs=1364 census_agreements=708 census_divergences=656 contract_matches=1 lean=4.21.0 axioms=Classical.choice,Quot.sound,propext sorry_free=true
```

The package's own dispatched workflow
(`.github/workflows/gate-operand-parity-lean.yml`) downloads the checksum-pinned
official Lean 4.21.0 release and runs the kernel mode plus the rejection
controls; its hosted result is the CI certification of the kernel claim.

## Credit

Prepared by Nick Petalas with AI assistance, under Apache-2.0.
Predecessor credit: Wentao Li's PR #3696 (gate-operand export parity; its open
question 1), the PR #2977/PR #3004 scatter cascade and the `#2992`/`#3273`/`#3346`
successors, PR #3738 (the bounded census and exact contract this package
formalizes), eumemic's pinned symbolic checker (`xcheck_p.py`) and Dylan Crow's
pinned record exporter (`export_records.py`), which the two Lean definitions
follow line for line.

## Open next questions

1. **Reordered exporters.** The contract depends on the destination's last
   occurrence, so an exporter that sorted or reversed a gate's sources would
   have a different, recomputable condition. Relevance: a successor schema that
   reorders sources could move the boundary. First step: state the reordered
   operator and adapt the proof's split point. Blocked by: no current exporter
   reorders sources.
2. **A shared formal layer with the scatter schema.** The scatter contract (all
   positive multiplicities odd) is a different object settled by
   `scatter-parity-contract-audit` and its successors. Relevance: one kernel
   argument could cover both boundaries. First step: formalize the scatter
   read/write pair and relate it to the same XOR-fold lemma. Blocked by: the
   scatter record shape is not the gate shape and needs its own definitions.
