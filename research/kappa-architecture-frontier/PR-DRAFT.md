# Research: the productive-helper path (#4440 lineage) can't pass κ ≈ .00304 without cheaper helpers

We prove all-length caps and a per-FULL price frontier for rank-eight
productive-helper paths, identifying the local savings needed for further
growth beyond controller-only changes.

Checkpoint: canonical main `32890bc5`; source bills bound
at [#5544](https://github.com/CrocSwap/integer-mult-bounds/pull/5544) `e2a6cce2`, [#5545](https://github.com/CrocSwap/integer-mult-bounds/pull/5545) `18968423`, [#5551](https://github.com/CrocSwap/integer-mult-bounds/pull/5551) `1123635a` and [#5440](https://github.com/CrocSwap/integer-mult-bounds/pull/5440) `c0f52b5b`
(full hashes in [SOURCES.json](SOURCES.json) and [ORIGINS.json](ORIGINS.json)).

## Significance for researchers

We give a stopping rule for controller changes at fixed local cost and a
quantitative target for redesigned providers. A universal ceiling for all native
productive-helper mechanisms would additionally need a lower bound on local debt
over arbitrary legal factorizations; that bound remains open.

## Summary

- **Controller-only search on a fixed local bill is finished.** For the
  rank-eight prefix/suffix path, every length, split and FULL/QUERY mask
  reduces to one strictly convex invoice per FULL count. So each bill has an
  exact all-length cap on raw saving, and it holds for every larger saving.
- **The selected bill has essentially no headroom left.** [#5413](https://github.com/CrocSwap/integer-mult-bounds/pull/5413)'s κ is within
  1.5×10⁻¹¹ of its all-length cap, and [#5468](https://github.com/CrocSwap/integer-mult-bounds/pull/5468)'s refinement is within 10⁻¹².
  Further compiler or precision work on this bill can gain only digits.
- **New local mechanisms get a price test.** With net local debt L(t), a
  favorable path exists exactly when L(t) < v·λ₈(t). Reaching C=.0034 from
  [#5551](https://github.com/CrocSwap/integer-mult-bounds/pull/5551) needs more than **4.91394927369 moment units of net saving per FULL**. That is
  about 0.28% of its net local debt, and about 30× the reduction in the
  required per-FULL discount from [#5413](https://github.com/CrocSwap/integer-mult-bounds/pull/5413) to [#5551](https://github.com/CrocSwap/integer-mult-bounds/pull/5551) at that C.
- **The ~.003 number comes from local debt, not from the path topology.**
  If the neutral bill's eight H8 completion calls were free, the same path
  would allow about .0081. So "productive helpers are stuck at .003" does not
  follow from this work, and this work does not claim it.

## Caps on raw saving

The raw-saving ceiling is the supremum of values C for which the supplier
moment test M_t(P) < M_t(T), t = 1−C, passes. It comes before compiler, BIT and outer
losses, so it bounds κ for the same bill from above.

| Local contract | Claimed κ | Sup of raw saving, all lengths/splits/masks | Best FULL count |
|---|---|---|---:|
| Selected [#5413](https://github.com/CrocSwap/integer-mult-bounds/pull/5413) | .003027288235 | (.00302728824993, .00302728824995) | 18 |
| P104 [#5544](https://github.com/CrocSwap/integer-mult-bounds/pull/5544) | .00304057 | (.00304057807630, .00304057807631) | 18 |
| P104 [#5545](https://github.com/CrocSwap/integer-mult-bounds/pull/5545) | .00304117 | (.00304117181649, .00304117181650) | 18 |
| P104 [#5551](https://github.com/CrocSwap/integer-mult-bounds/pull/5551) | .00304153 | (.00304153116714, .00304153116715) | 18 |
| Neutral bill, eight H8 completions free | none (relaxation) | (.00807671283977, .00807671283979) | 7 |

The P104 rows extend the submitted fixed-p16 crossings to the whole path
family. They take the native circuits as given and do not re-verify them.
The last row is an optimistic relaxation, not a construction. Even this
relaxation misses .01 by more than 21.85 units per FULL.

The universal exchange/convexity reduction builds on
[Ali Romman](https://github.com/aliromman)'s
[#5405](https://github.com/CrocSwap/integer-mult-bounds/pull/5405) and
[Chris R](https://github.com/Clear1nsight)'s independent
[#5409](https://github.com/CrocSwap/integer-mult-bounds/pull/5409). This package
generalizes it to arbitrary ports v, block rank b > 1 and local debt L. The new
parts are the application to P104, the price frontier and the closure result.

## Price frontier for changed providers

Write the optimal invoice with n FULLs as C_n = nL + v·c_n(t), where c_n
depends only on the path geometry and t. Then λ_b(t) = max_n (−c_n/n). A
provider that keeps v, b and the controller contract must cut net local debt
per FULL by more than min_n C_n/n. Each new repair request counts against that
saving. The minimizing n depends only on b and t, not on the local word. Three
rational signs certify it over all n, so no large-controller search is needed.

| Target C | Best FULL count | Net saving needed per FULL from [#5551](https://github.com/CrocSwap/integer-mult-bounds/pull/5551) | From [#5413](https://github.com/CrocSwap/integer-mult-bounds/pull/5413) |
|---|---:|---:|---:|
| .0031 | 18 | .80638594481 | .99667194384 |
| .0033 | 17 | 3.54923453123 | 3.72139618536 |
| .0034 | 16 | 4.91394927369 | 5.07657009697 |
| .004 | 14 | 12.96623724304 | 13.06167562796 |
| .006 | 9 | 38.56153416704 | 38.34368776890 |
| .01 | 5 | 85.66448729816 | 84.53539335470 |

Values are rounded down; the exact outward endpoints are in RESULT.json. Units
are rank-power moments, not ADD counts. For scale, [#5551](https://github.com/CrocSwap/integer-mult-bounds/pull/5551)'s net local debt is
L(t) ≈ 1736 at C=.0034. At C=.006 and C=.01, the 112-port neutral bill needs *less*
saving than the 104-port [#5551](https://github.com/CrocSwap/integer-mult-bounds/pull/5551). P104's advantage near the current crossing
does not persist at every tested target; a changed provider's port count must
be included in the comparison.

**Why .0034:** it is the selected outer contract's admitted BIT budget. With
that budget fixed, a change to COMPLEX alone cannot promote κ ≥ .0034, whatever
the frontier says. This limit belongs to the outer interface. It is not a BIT
impossibility result.

**Why the margins are small:** every completed native profile here has
L(1) = 17v − 48. At t = 1 the optimal invoice therefore has surplus exactly
48n − v: 752 for the selected n=18 invoice and 760 for P104. The positive-C
crossing still depends on how paid and target ranks are distributed.

To price a new autonomous bill (`ports`, `paid`, `helper_targets`):

```sh
python3.12 -B research/kappa-architecture-frontier/verify.py --price PROFILE.json --C 0.0034
```

The command reports exact discount bounds and the all-n certificate. If an
interval sign is ambiguous, or the minimizer lies beyond n=4096, it fails as
unknown. It does not inspect a native word or admit a supplier.

## Closure: what cannot amplify a failed bill

Fix t and take bills that each fail the moment test. None of the following
produces a passing bill:

- disjoint combinations;
- positive scaling;
- declared tensor products;
- exact acyclic typed cancellation;
- charged splitting or completion.

So more tensor depth, batching, repetition or a finer funding grid cannot
rescue a failed bill. A mixture of compatible autonomous providers cannot beat
its best member. None of this covers:

- a new cross-boundary consumer;
- correlated or coded outputs;
- a changed idle law or controller graph;
- an arbitrary native refactorization.

## Relation to other claims

The frontier assumes autonomous outputs, so it neither refutes nor supports
the coded, centre-free p19 proposal
[#5440](https://github.com/CrocSwap/integer-mult-bounds/pull/5440)
(.0033999964). That PR is outside this contract. Its source at `c0f52b5b`
reports `FINDING_PRECOMPILATION_CONTRACT_MISSING` and
`kappa_attached_to_physical_chain: false`. The claim map lists it separately
from admitted results for that reason. The floating-point LP screens in
[#5465](https://github.com/CrocSwap/integer-mult-bounds/pull/5465) are not used
as lower bounds. They cover one word or commutation poset, not a redesigned
native word.

## Evidence and scope

The selected construction, frontier, allocation and queue dispositions remain unchanged.

See [the proof](PROOF.md), [claim map](CLAIMS.md), [exact receipt](RESULT.json),
[source origins](ORIGINS.json) and [validation](VALIDATION.md). The checks use
an independent rational engine written with only the Python standard library:
interval arithmetic on a 2²²⁴ grid, with no floating-point acceptance. The
engine:

- reconstructs every coefficient of four complete source invoices;
- proves six all-length gates that also cover every larger saving;
- proves thirteen all-length discount gates;
- checks 912 small-mask comparisons.

Fourteen rejection controls reject changed source bytes, forged Git trees,
omitted query/idle/helper bills and false admission receipts. They pass in
both normal and optimized Python.

Validation used CPython 3.12.8, registered serial replays and a Git-free,
network-free read-only export (archive SHA256 `c741d2d2…`). The caps are raw
moment theorems under the stated controller and local contracts. Native words
and the five framework assumptions are inherited. This package does not claim
a whole selected replay, a proof-kernel theorem, hosted CI or independent
human acceptance.

## Open next questions

- **Native lower bound at .0034.** Can any legal rank-eight native
  factorization beat [#5551](https://github.com/CrocSwap/integer-mult-bounds/pull/5551) by more than 4.91394927369 units per FULL? A yes needs a
  complete charged word. A no must cover arbitrary factorizations, not one
  poset.
- **Lower [#5440](https://github.com/CrocSwap/integer-mult-bounds/pull/5440)'s coded consumer.** Price its actual native event chain,
  keeping recodings, phases, ownership and all later calls.
- **Change an invariant.** Change one query, idle, state or geometry
  invariant and derive its full optimistic invoice before extending a search.
- **Check the ratio-frontier proof.** Independently check the written proof,
  especially the n=2/3 convexity junction and the J_(n+1)−J_n sign gate. The
  finite controls do not replace this check.

We retain the productive/compiler lineage of
[Cinna Davis](https://github.com/1337isnot1337),
[Cao Yifan](https://github.com/intqwq),
[Dillon Amburgey](https://github.com/dillona),
[Jacob Alan Sussman](https://github.com/jacobalansussman),
[Ali Romman](https://github.com/aliromman),
[Chris R](https://github.com/Clear1nsight),
[Gareth Davidson](https://github.com/bitplane),
[David Arias](https://github.com/DavidAriasC),
[thu-nmrc](https://github.com/thu-nmrc),
[zxv](https://github.com/zxv) and all notices in the unchanged source extracts.
Prepared with substantial OpenAI Codex assistance; Apache-2.0.
