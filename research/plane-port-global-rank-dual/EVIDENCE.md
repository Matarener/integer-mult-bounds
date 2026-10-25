# Search evidence for the 224 conjecture

**Heuristic numerical search, not a proof.** Script: [search/real_escape.py](search/real_escape.py).
Raw result lines: [search/results/](search/results/).

## Method

For a group `D` of planes, every term slot has fixed plane supports `(A, R)` with `A, R` subsets of
`D` (for 5-7 planes only sides of 1-2 planes, the whole group and all-but-one). The objective is
the mask residual on fixed cells plus `lam * sum_k t(A_k, R_k) |u_k| |v_k|`, minimised by L-BFGS
with `lam` raised in steps. Survivors are pruned by weight and refitted exactly by least squares.
Whenever the refit is exact (max residual below `1e-9`), the run records the **true** cost: the
sum of tariffs of the actual nonzero supports. The mask is the strict one: free entries between
orthogonal planes. A decomposition of the identity endpoint is also a strict-mask decoder, so
"no escape" here also covers the identity endpoint used by the three- and four-plane rank duals.

Real solutions include every rational one, so a real minimum of `4|D|` excludes all denominators on
that group. The search is local optimisation from random starts and can miss a cheaper decoder.
Where it stops above the baseline, it did not even reach the known decoder, so that line is
weak evidence.

## Results

No run found an exact decoder below `4|D|`.

| Groups | Starts | Reached baseline | Above baseline | Below baseline |
|---|---:|---:|---:|---:|
| 6 open triple classes of `three-plane-rank-dual` | 40 | 6 | 0 | 0 |
| 40 random open quadruples of `four-plane-rank-dual` | 30 | 30 | 10 | 0 |
| 60 most degenerate quadruples (3 of them open) | 30 | 44 | 16 | 0 |
| 23 induced C5s | 15 | 6 | 17 | 0 |
| C5 + 1 most degenerate plane (23) | 15 | 5 | 18 | 0 |
| C5 + 2 most degenerate planes (23) | 15 | 3 | 20 | 0 |

The baselines are 12, 16, 20, 24 and 28. On quadruples the solver usually reaches 16. On 5-7 plane
groups it often stops 2-10 above, so those rows say little beyond "nothing cheap was found".

The open quadruples were sampled with `random.Random(2026).sample` from the 5,584 index-zero
quadruples of `four-plane-rank-dual/CERT-INDEX.bin.gz`. The open triple classes are the six classes
of `three-plane-rank-dual/CERTIFICATES.json` that carry an `f2_minimum_mass` field; one example
triple per class is searched.

## Provenance

The 60 degenerate quadruples and the C5 groups ran on Kaggle with the same search core from the
fork branch `Matarener/integer-mult-bounds:v4-plane-lb`. The C5 run stopped after 49 of 69
groups on an `SVD did not converge` error inside a refit; the refit now skips such a prefix, and the
remaining 20 groups ran separately. The `quads-degenerate` and `c5` modes of `real_escape.py`
reproduce the same group lists. The open-quadruple run used `real_escape.py` from this package on
Kaggle; the open-triple run used it locally.
