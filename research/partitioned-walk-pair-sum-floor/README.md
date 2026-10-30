# Pair-sum floor for partitioned independent-walk duals

**Scoped proof and finite certificate in the PR1898 abstract tariff; no new κ.**
This answers open question 2 of Wentao Li's
[PR #2779](https://github.com/CrocSwap/integer-mult-bounds/pull/2779)
(`research/independent-walks-7q-obstruction`): repeated labels inside a
partitioned walk cannot improve on `R=112` at `Q=7`. No such dual covers.
The same argument gives a readout floor for every query count, every label
pattern and any number of walks. It is attained at `Q=8` and `Q=9`.

| Q | Readout floor `R` | Attained? | Tariff floor at `X=0` |
|---:|---:|---|---:|
| 7 | 102 (exact min is 112, below) | no | 470 |
| 8 | **92** | yes, `(0,10)`, `(0,22,5,31,24,20)` | 488 |
| 9 | **80** | yes, `(0,3)`, `(0,18,1,5,11,20,27)` | 502 |
| 10 | 66 | unknown | 512 |
| 11 | 62 | unknown | 542 |
| ≥12 | 62 | — | > 436 from `38Q` alone |

Every entry exceeds the six-query endpoint tariff `436`. Partitioned
independent duals cannot undercut it at any query count or label pattern.

## Model

The model is that of PR #2779's `model.py`, which the verifier imports as a
pinned live input. A restored walk is a slot list `(0,s_1,…,s_{n-1})` over
`F₂⁵` whose closed completion has only nonzero edges. Labels may now repeat and
`0` may be revisited at interior slots. Walk `i` has even-subset table `e_i`.
A partitioned dual has `k ≥ 2` walks with lengths summing to `Q`. Mask `m` costs
`min Σ e_i[a_i]` over `a_1⊕…⊕a_k = m`. For `k = 2` this is the PR #2779 formula,
and the verifier checks agreement on every two-walk control. `R` sums the 31
nonzero masks, and the tariff is `38Q + 2R + 2X`.

## Proof

**Table lemma.** For a walk `w`, `e[v]` is finite iff `v ∈ span(w)`, since an
odd subset can toggle the slot-0 entry. Every finite nonzero value is even and
at least 2, and `e[v] = 2` iff `v` is a nonzero pair sum `s_j ⊕ s_k`. A walk of
length `n` has at most `C(n,2)` pair sums.

**Covering.** A dual covers every mask iff the walk spans sum to `F₂⁵`. Walk
`i` has rank at most `n_i − 1`, so covering needs `Σ(n_i − 1) ≥ 5`, that is
`Q ≥ 5 + k`.

**Q = 7 answer.** Only `k = 2` with `(2,5)` or `(3,4)` can cover, and the bound
is tight. Each walk must therefore have `n_i − 1` linearly independent labels.
A repeated label or interior zero revisit lowers the rank, so such a dual never
covers. The remaining duals are exactly PR #2779's distinct-label duals, for
which that package proves `R = 112`. So `112` is the exact minimum over all
label patterns at `Q = 7`.

**Pair-sum floor.** A nonzero mask costs at least 2. Cost 2 forces one port to
pay 2 and the rest 0, so the mask is a pair sum of one walk. Every other mask
costs at least 4. With `P` the union of nonzero pair sums,
`R ≥ 4·31 − 2|P| ≥ 124 − 2 Σ C(n_i,2)`, and also `R ≥ 62`. Under
`Σ n_i = Q`, `n_i ≥ 2`, `k ≥ 2`, convexity puts the maximum of
`Σ C(n_i,2)` at `(2, Q−2)`, equal to `1 + C(Q−2,2)`. Hence

```text
R ≥ max(62, 122 − (Q−2)(Q−3)).
```

The two witnesses in the table attain this value at `Q = 8, 9`. So `92` and
`80` are the exact minima there over all partitioned duals, with arbitrary
labels and any number of walks.

## Evidence

`verify.py` checks, using PR #2779's `even_table`, `dual_independent_R`,
`valid_restored_walk`, `path_X` and `tariff_qrx`:

- the table lemma on every restored walk of length 2–5 with arbitrary labels
  (924,482 walks);
- the `Q = 7` rank census. 894,660 length-5 walks, of which 624,960 have
  rank 4, all with distinct nonzero labels. 28,861 length-4 walks, 26,040 of
  rank 3, likewise. Every length-2 and length-3 walk has full rank;
- 4,000 seeded random duals with `Q` from 7 to 11, two or more walks and
  arbitrary labels. Covering matches full span and every covering dual (2,456)
  meets both floors. The k-port convolution equals PR #2779's two-port dual;
- the partition maximum for `Q` from 7 to 11, the two witnesses (exact `R`,
  path `X`, tariff), and the tariff floors.

The random controls are sanity checks; the floor rests on the proof above.

## Reproduce

From the repository root:

```sh
~/git/integer-mult-bounds/.venv/bin/python3.12 -B research/partitioned-walk-pair-sum-floor/verify.py
python3.12 -B scripts/research_package.py --package research/partitioned-walk-pair-sum-floor
```

Expected final line:

```text
PASS_PARTITIONED_WALK_PAIR_SUM_FLOOR lemma_walks=924482 q7_full_rank_5walks=624960 q8_min_R=92 q9_min_R=80 min_tariff=470 no_new_kappa
```

The full run takes about 25 s. `--quick` checks the table lemma only up to
length 4.

## Limitations

- This is an abstract-tariff result in the PR1898 five-source alphabet, not a
  physical supplier, a complete multiplication theorem or a κ change.
- The `k ≥ 3` cost rule is the natural min-plus extension of the two-port dual.
  No earlier package defines it.
- Same-walk, transfer-coupled and shared-dirt schedules are outside the scope.
- Path cost `X` is only bounded below by 0. The witnesses have positive `X`.

## Open next questions

1. **Exact minima at `Q = 10, 11`.** The floor gives 66 and 62; a seeded search
   of 200,000 `(2, Q−2)` duals found 72 and 66. Why it matters: it would settle
   whether the pair-sum floor is sharp for every `Q`. First step: an exhaustive
   search over pair-sum-distinct long walks up to `GL(5,2)` symmetry. Blocked
   by: none; the tariff question is already settled there.
2. **Transfer-coupled schedules.** Can the pair-sum count, with the shared
   prefix charged once, bound transfer-coupled duals at every `Q`? Why it
   matters: it would replace the per-shape censuses. First step: bound the
   cost-2 masks of a shared prefix with divergent suffixes. Blocked by: the
   transfer billing rule.

## Credit

Model, two-port dual, tariff and the distinct-label `R = 112` theorem: Wentao
Li, PR #2779, building on Arham Tahir's PR1898 and the lineage credited there.
This package was produced by Nick Petalas. Apache-2.0.
