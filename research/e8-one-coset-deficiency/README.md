# Uniform E8 one-coset budget and the two-sided rank-nine COPY floor

The new core result is a uniform deficiency budget for arbitrary finite,
pairwise nonproportional families in one outside-code direction on full E8.
It supplies the missing term-count-independent packing step and implies **COPY ≥ 72** for every
exact decoder `PQᵀ = N₀ = G/2` whose two actual factor ranks are at most nine,
with any finite number of terms. Both results hold over **every scalar field
of characteristic different from two**. The binary COPY table is the fixed
canonical dense table, defined before scalar field reduction.

The genuinely two-sided consumer is the `(s,t)=(1,1)` cell, where both actual
factor ranks are nine. The one-sided dimension-nine and sparse dimension-ten
corollaries below are scoped cases of the existing **L120** programme, which
asks for minimum basis cost at least 72 for every scalar space containing C.
They are proved here directly, including in odd characteristic, without
assuming that programme's conditional completion chain.

The floor is attained by the ordinary eight-term frame and by an explicit
**normalized rank-(9,9), ten-term** decoder. Its per-term costs are
`(1,7,9,9,9,9,9,9,9,1)`. Thus the result closes the first genuinely two-sided
ten-term exact-decoder branch, including all proportional-merge exits.
It does not assert the unrestricted masked P120 floor or change κ.

A further consequence closes a specific **rank-(10,8)** family, over the same
fields and with any finite term count: if one factor lies in `C` and the other
in `C + span(δ_a,δ_b)` for two root-coordinate unit vectors, then COPY is at
least 72. [SPARSE-PAIR.md](SPARSE-PAIR.md) derives this from the uniform theorem
by classifying all deficient projective rays in those extensions. Weight-at-most-seven
vectors lie in the two-dimensional coordinate space; weight-at-most-eight
vectors lie in a four-dimensional space. Every ten-vector basis therefore
costs at least `1+1+8+8+6·9=72`. A sheared rank-(10,8) equality construction
is pairwise nonproportional on both sides, so its rank and ten terms survive
proportional normalization. This is a sparse-pair result, not an arbitrary
two-direction theorem.

## The theorem and its consumer

Let `C` be the eight-dimensional scalar E8 root-evaluation code. The binary
root labels span `Λ = F₂⁹`; for a coefficient vector `p`, let `w(p)` be the
binary rank of the labels on its nonzero support. If `λ ∉ C` and the nonzero
vectors `p_i ∈ C + Kλ` are pairwise nonproportional, then

```text
Σ_i (9 − w(p_i)) ≤ 9.
```

Each nonzero vector in `C` has weight nine. The theorem applies to arbitrary
families in one extension, rather than a prescribed frame or actual-basis
catalogue. Its proof uses the annihilators of the binary support spans. Three
finite E8 rank facts force compatible binary characters to be independent;
grouping a putative relation by annihilator then proves that all these
annihilators form a direct sum in a nine-dimensional space.

For the consumer, alternating proportional merges preserve exactness and
never increase COPY or either factor rank. Only zero-factor terms are
discarded; nonzero cost-zero atoms are retained. After normalization write
the ranks as `8+s, 8+t`, with `s,t ∈ {0,1}`. The two deficiency budgets and
the binary pairing inequality give

```text
COPY ≥ 9m − 9s − 9t ≥ 72,
```

where the last step is Sylvester's `m ≥ 8+s+t`. Recomputing the ranks after
merging includes exits to rank `(9,8)`, `(8,9)` and `(8,8)`.

In particular every exact ten-term decoder whose two factors both leave `C`
is covered: Sylvester forces both ranks to be nine. A cheaper two-sided exact
decoder would need at least eleven terms and a factor of rank at least ten.

Every equality case also has necessary rigidity after normalization:
`m=8+s+t`, both deficiency budgets saturate, and every term's annihilators
are orthogonal across the two factors. On each rank-nine side, its
annihilators decompose all `Λ` into mutually orthogonal nondegenerate summands.
[PROOF.md §7.2](PROOF.md#72-necessary-structure-of-every-equality-case) proves
these conditions; they do not constitute a scalar coefficient classification.

## Proof, certificates and controls

[PROOF.md](PROOF.md) gives the complete written argument, normalization,
sharp constructions and field transfer. The finite evidence is separated from
that universal argument:

| Evidence | What it checks |
|---|---|
| [CERTIFICATE.json](CERTIFICATE.json), [geometry.py](geometry.py) | Nine single-character types and 100 forbidden ordered-pair profiles, with 109 explicit integer 8×8 minors. Every determinant is a power of two. |
| Integral reflection identities | Eight generators implement the full S9 profile action on standard doubled roots over `Z[1/2]`: 960 signed root images and 512 matrix-entry checks. This avoids reducing the rational A8 isometry in characteristic three. |
| [independent.py](independent.py) | A separately written reconstruction starting from D8 plus half-roots, deriving its own binary labels and checking all 511 characters and 130,305 unordered pairs by modular full-rank witnesses or exact integer elimination. |
| Complete F3 families | All 6,561 coefficient choices in each of four sparse one-coset families; their total deficiencies are 9, 9, 9 and 7. Also checks weight nine for all 6,560 nonzero scalar codewords. |
| Model binding | All 120 root lines, 14,400 scalar Gram pairs, and the full binary pairing/quadratic-color transport agree between the two constructions. |
| [fixtures.py](fixtures.py) | Eight entrywise exact rational factorizations, all costing 72; strict normalized `(9,9)` equality; merges on both sides, cancellation, zero-factor removal and rank drops. The same eight factorizations are checked over F3, F5 and F7. |
| Semantic controls | Reject omitted terms, wrong target scaling, a changed factor sign, and deletion of a genuinely nonzero cost-zero atom. |
| [controls.py](controls.py) | Reject 14 certificate corruptions at specified gates, including a valid full-rank minor of determinant 768 that fails the odd-field unit condition; accept a different valid signed minor; separate binary from rational rank; exhibit dependent fake cliques if either binary edge condition is omitted. |
| Scope controls | Repeated proportional vectors violate the unqualified family bound; six nonproportional rays in two outside directions have total deficiency 42, so doubling the present budget is invalid. |
| [sparse_pair.py](sparse_pair.py) | Separate dense-table reconstruction; both complete 29,524-ray F3 sparse-pair spaces; exact deficient-ray classifications and weight-filter ranks; planted F5/F7 controls. Six sheared equality fixtures remain rank-(10,8) with zero merges; six original equality fixtures are positive controls that merge twice to rank-(8,8). Omitted reader compensation fails the exact product check. |

The full independent pair-rank histogram is `0:255, 6:3360, 7:35640,
8:91050`. The certificate supplies sufficient full-rank witnesses, without
depending on that complete histogram. Failed modular rank never establishes a
rational deficiency; an explicit rank-drop control exercises that distinction.

These are two internal implementations and AI-assisted source reviews, not
independent human certification. [FORMAL.md](FORMAL.md) records six checked
Init-only Lean declarations for the abstract binary clique argument, its
concrete nine-bit addition/dot-product laws, and the final natural-number
budget implication. The E8
instantiation, annihilator/dimension assembly, field transfer and COPY consumer
remain written mathematics rather than a formal proof-assistant theorem.

## Reproduce

No Python dependencies or compilation are required for the registered replay.
From the repository root, with CPython 3.12:

```sh
python3.12 -B scripts/research_package.py --package research/e8-one-coset-deficiency --check-only
python3.12 -B scripts/research_package.py --package research/e8-one-coset-deficiency
```

Direct replay also works from a source export with the declared inputs present:

```sh
python3 -I -B research/e8-one-coset-deficiency/verify.py
```

Normal execution checks the scientific source inventory before loading the
package modules, authenticates the declared input bytes, recomputes all finite
evidence and compares it with [RESULT.json](RESULT.json). Package modules are
compiled from their current source bytes, bypassing stale bytecode. The replay
uses explicit checks and supports `-O`. It does not rewrite receipts. The
explicit `--emit` option regenerates both deterministic certificate and result
after an intentional source change; such a change requires a fresh replay.

The registered Python replay does not invoke Lean. [FORMAL.md](FORMAL.md)
gives the separate Lean 4.21.0 command and the exact formal boundary. Run
resource-intensive jobs serially; no whole-project build is needed.

## Relation to prior work and coordination

This answers the uniform compatibility/packing question left by
[PR1224](https://github.com/CrocSwap/integer-mult-bounds/pull/1224)
(joaqcoo), rather than just replaying its pair census. It extends
[PR1248](https://github.com/CrocSwap/integer-mult-bounds/pull/1248)
(mightyOil)'s fixed A8-frame budget; its compatible-edge independence argument
is a method ancestor of the clique proof. It also extends the fixed A7+A1 family of
[PR2062](https://github.com/CrocSwap/integer-mult-bounds/pull/2062) (adamgall).
[PR1633](https://github.com/CrocSwap/integer-mult-bounds/pull/1633)
(bbMisk) supplies the factor-excess-rank framework and two-sided ten-term
normal form; the rank and merge arguments needed here are rederived.

The model and COPY accounting retain the E8 decoder lineage of PR446/PR717
(DreamingOfClouds), PR968 (themilkman216) and PR1077 (woklerx).
[PR2854](https://github.com/CrocSwap/integer-mult-bounds/pull/2854)
is a punctured-P112 rank-nine floor, which does not imply this full-root result.
The exact-N₀ reduction in
[PR2832](https://github.com/CrocSwap/integer-mult-bounds/pull/2832)
does not preserve factor ranks and hence cannot turn this theorem into a
general masked-realization floor. The special joint-query packing in
PR3549/PR3569 does not supply this arbitrary-family theorem.

DreamingOfClouds's [PR2816](https://github.com/CrocSwap/integer-mult-bounds/pull/2816)
already studies singleton root swaps and two coordinate pieces in the P112
low-excess correction setting; PR2862 gives a historical lift-floor baseline.
The sparse-pair corollary retains that geometric credit and proves its stated
full-E8, all-odd-field, all-term contract directly from the uniform budget.

CubeJerry's [PR3095](https://github.com/CrocSwap/integer-mult-bounds/pull/3095)
already certifies full rank of every full-E8 character complement over every
characteristic different from two using power-of-two minors (fact 1 here),
and asks about L120 in odd characteristic. The present finite certificate
reconstructs that premise and adds the forbidden-pair facts and orbit action;
fact 1 and its odd-characteristic validity are not claimed as new.
philippeVV's credit-at-most-nine argument for restricted clean lift families
in [Discussion 1587](https://github.com/CrocSwap/integer-mult-bounds/discussions/1587)
is adjacent antecedent work, rather than the arbitrary-family theorem here.

The active two-sided consumer is
[PR3154](https://github.com/CrocSwap/integer-mult-bounds/pull/3154)'s
ARCHITECT node C-prime: this closes its exact `(1,1)` cell for every term
count. Its G2 discussion explicitly requests an “m-free deficiency budget”.
The one-sided `(1,0)` and `(0,1)` branches and the sparse-pair extension are
dimension-nine and specified dimension-ten cases of node B-prime / L120.
For the exact-decoder list in
[Discussion 1587](https://github.com/CrocSwap/integer-mult-bounds/discussions/1587),
the coverage is the nine-term P120 item and the ranks-at-most-nine slice of
`m>=10`; its higher-rank and other realization questions remain open.

The broader characteristic-zero one-sided programme is documented by
[PR3074](https://github.com/CrocSwap/integer-mult-bounds/pull/3074)'s sufficiency
of L120 and [draft PR3191](https://github.com/CrocSwap/integer-mult-bounds/pull/3191)'s
conditional completion claim. At the 2026-10-18 19:29 UTC refresh,
PR3191 head `9c9e094d0fb665db8a3aaa4f9bce1c95c0c6e14b` still has an
unfilled implementation slot. conorholds' merged
[PR3166](https://github.com/CrocSwap/integer-mult-bounds/pull/3166) supplies C7
within that programme. If its full L120 conclusion is established, it includes
these one-sided characteristic-zero slices; it does not supply this package's
arbitrary-family theorem or the two-sided `(1,1)` floor. G2 with one side of
arbitrary larger rank and C-prime's higher-excess branches remain outside scope.
This package uses none of the pending catalogue, retraction, C1–C5 or global
master-floor premises. [SOURCES.json](SOURCES.json) pins the reused proof inputs
and the historical selected record/catalogue at base `20ecf289`.

The original card and scope change are retained in [TASK.json](TASK.json).
An overlapping-task search is advisory, not a novelty proof. This candidate
has been prepared locally under a no-publication instruction; no public claim
or Discussion reservation was made. Current overlap evidence must be refreshed
before any authorized submission.

## Limits

The result concerns full E8, fixed dense binary COPY accounting and exact
`N₀`. It does not cover arbitrary masked realizations, punctured alphabets,
or arbitrary factors with two outside-code directions. The restricted
singleton-pair extension is covered by SPARSE-PAIR.md. It does not settle the global
P120 master floor, unrestricted one-sided ten-term `(10,8)` factorizations,
supplier admission, physical parking or a multiplication exponent.
Characteristic two is excluded. The all-odd-field theorem follows from the
unit minors and reflection identities, rather than inference from three
finite-field examples. The sparse-pair extension follows from that theorem,
not extrapolation of its F3 census.

## Open next questions

1. **Two outside directions.** Study an actual rank-(10,9), eleven-term
   exact identity. This is the next possible cheaper two-sided branch, but
   the six-ray counterexample prevents replacing nine by eighteen in the
   present family theorem. A coupled replacement for the direct-sum budget
   is needed before claiming a generalization.
2. **Complete formalization.** Instantiate the checked binary clique core
   with the E8 labels, then connect the certified root spans, annihilators,
   dimension bound and Sylvester/COPY consumer. These bridges remain open;
   exploratory broad Mathlib imports exceeded a conservative local memory
   watchdog. The published formal claim is limited to the checked Init core.

Prepared by conorholds, with substantial OpenAI Codex assistance, including
GPT-6.1 SOL agents at xHigh. New work is Apache-2.0; predecessor credits are
retained above. No independent human peer review is claimed.
