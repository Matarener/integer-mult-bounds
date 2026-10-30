# Conditional κ = 0.00267987 from a complete p6 native controller

This contribution improves the conditional construction of
[PR #4359](https://github.com/CrocSwap/integer-mult-bounds/pull/4359) from
κ = 0.0023 to **κ = 0.00267987**. It follows the native tensor construction of
[PR #4412](https://github.com/CrocSwap/integer-mult-bounds/pull/4412), whose
p3 controller gives κ = 0.00247755, with a larger fully audited p6 controller.
The asserted conditional form is

```
T(n) = O(n (log n)^(1 - 0.00267987)).
```

The new result requires both a complete native binding of the larger word
and a rational paid-rank cutoff. The source factorization alone supplies
neither its physical phase proof nor its compiler/outer admission.

## Construction and evidence

The fixed source controller is `pairs=6, keep_idle_mask=25279`. Give each of
its thirteen local calls 408 distinct arbitrary helper inputs. Retain all
1,344 independent main inputs and all original rank-eight centers. Pay each
main idle window as its whole canonical transform, including its actual
phase translation. The resulting 6,648 productive fields have rank mass
108,769; the complete paid rank mass is 108,257.

[NATIVE.md](NATIVE.md) and [native_inventory.py](native_inventory.py) replay
the exact Laurent controller and bind its physical realization on 105 axes.
They check all 5,824 main contacts and inverses, 1,344 main endpoints, every
whole idle operator and all fresh helper owners. Binary orthogonality and
exact Z4 quadratic polynomials establish the identities for all addresses;
these are not numerical samples. Reversed local orientation and omitted
nonzero endpoint translations are rejected. The deterministic receipt hashes
canonical uncompressed geometry, independently of gzip implementation details.

[TENSOR.md](TENSOR.md) composes complete native words in chronological
lockstep and splits oversized paid jobs on disjoint axes. At tested saving
**0.00267988**, use tensor power 150,000 and cutoff
`floor((19/4)^150000)`. The separate paid rank-one tail condition passes for
this rational cutoff; integer cutoff base four fails. The complete normalized
paid moment is at most `16386003/16408576 < 1`, including the floor surcharge.
The strict separation exponent satisfies `theta < 31/32`.

[ENDPOINT.md](ENDPOINT.md) derives sufficient uniform ambient rank
`N = 2^473129651134046950001`. It recalculates the expanded word's owned stock
and precision constants and admits κ through all nine inherited outer cost
rows, 54 retained predicates and three functional guards. The ordinary BIT
saving remains the source-admitted 0.0027.

[RESULT.json](RESULT.json) records the complete replay and exact inequalities.
A second rational interval implementation independently checks the moment
and tail bounds. The huge tensor and uniform words are specified by finite
algorithms; their instruction lists have not been materialized.

## Reproduction and source provenance

Python standard library only. Normal verification authenticates source bytes,
reruns the native audit and arithmetic, and compares the saved result.

```sh
python3 -I -O -B research/pr4359-p6-fresh/verify.py
python3.12 -B scripts/research_package.py --package research/pr4359-p6-fresh
```

To additionally emit the finite raw native geometry outside the source tree:

```sh
python3 -I -B research/pr4359-p6-fresh/native_inventory.py --output-dir /tmp/p6-native
```

`EXPORTED-SOURCES.json` binds focused unchanged source exports from PR4359
at `da637c87c89482bc4c86be36bd0071b3d400dbed`, the independent interval and
outer-ledger modules from PR4405 at `873d1b3c96a83b701a5c0bba8e37a861e6672fef`,
and the all-fresh native source gate from PR4412 at
`9f0df9bf6f49942faf5f31389e7e387fdfe511b3`. Each copied file is bound to its
original Git blob and SHA256. These unmerged source heads are not represented
as publication ancestry. Standard `SOURCES.json` binds canonical-main task
and selected-result provenance at `12fa8c5`.

## Scope and credit

This is a conditional research construction awaiting review. It retains the
source all-column native contracts, permitted physical operations, analytic
decomposition, fixed-tape model and outer transfer premises. Finite replay
and exact arithmetic do not constitute formal verification of the complete
multiplication theorem. There is no selected-frontier promotion or practical
implementation claim.

Source controller and native construction: @zxv, PR4359. Underlying mixed
flow: Jacob Alan Sussman, Theorem 1G. The interval and outer-ledger sources
retain predecessor attribution. New native geometry, composition proof,
verification and integration were prepared for @1337isnot1337 with substantial
OpenAI Codex assistance. Apache-2.0; original notices remain in copied sources.

## Open next questions

[TASK.json](TASK.json) records feasible next steps: examine a declared larger
controller family and reduce sufficient ranks through sharper rational cutoff
bounds. The inherited BIT saving of 0.0027 is close enough that a substantially
stronger complex word would also need a new BIT admission. No universal
optimality follows from this one fixed controller or the finite menu search.
