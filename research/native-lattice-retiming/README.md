# Conditional κ = 0.00300120 (71.9× smaller uniform-rank exponent)

**Submission authorized by the user after review on 21 October 2026.**

A changed native paid profile raises the conditional multiplication saving to
**κ = 0.00300120** and specifies sufficient uniform rank
**`2^2299850000000`**. The κ gain over
[PR4441](https://github.com/CrocSwap/integer-mult-bounds/pull/4441) is modest:
`0.00000015` (about 0.005%). The exponent of its sufficient uniform rank falls
by **71.88×**. At PR4441's unchanged κ=0.00300105, the rank can instead be
**`2^249900000000`**, a **661.53×** exponent reduction.
These are sufficient mathematical template sizes, not practical speedups.

The submission refresh found concurrent [PR4447](https://github.com/CrocSwap/integer-mult-bounds/pull/4447),
which uses the same B/480 contact and paid profile and declares κ=0.00300123.
This contribution retains the reviewed κ=0.00300120 and supplies the smaller
paid-tail and uniform-template bounds above, with a separate discovery path.
No unique-discovery or strongest-κ claim is made.

This builds on my selected [0.0023 construction](../kappa-0023-productive-jobs/README.md),
my [higher-moment/logarithmic compiler](../higher-moment-strictification/README.md),
and Cinna Davis's new query-thinning and fresh-helper constructions
([PR4440](https://github.com/CrocSwap/integer-mult-bounds/pull/4440),
[PR4441](https://github.com/CrocSwap/integer-mult-bounds/pull/4441)).
Both pending source heads are pinned; they are author-checked conditional
claims, not independently accepted frontier updates. The selected record stays
0.0023. The new work retains their native/all-column, owned-erasure, whole-job,
precision, analytic, fixed-tape, prime and exact-recovery premises.

## The actual construction change

At phase B, persistent scalar ordinal 480, the forward ADD is
`L90 += L253`. Its old common frame has basis `[258,133,82,45]`.
Replace it by the three-dimensional subspace with basis `[45,133,336]`.
It is the old space intersected with the hyperplane orthogonal to binary
vector 2. Apply the same frame change at the literal inverse-transpose ADD in
the backward word. Scalar order, coefficients, warp contacts, main boundaries,
helper boundaries and all eight complete centers remain those of PR4441.

Direct ascending transports before and after the changed contact give:

| Local resource | PR4441 | New word |
| --- | ---: | ---: |
| Paid rank 1 | 2253 | 2254 |
| Paid rank 2 | 515 | 514 |
| Paid rank 3 | 445 | 444 |
| Paid rank 4 | 102 | 103 |
| Paid rank 5 / rank 8 | 40 / 8 | 40 / 8 |
| Productive helper widths | 26×4, 2×5, 29×7, 42×8, 309×9 | same |

Thus the net paid change is `H2+H3 → H1+H4`. For every real `0<t<1`,
strict concavity gives `1+4^t < 2^t+3^t`. This changes the raw paid profile;
it is not an extra decimal extracted from the same root. Counts, rank mass,
all 408 autonomous helpers and owned-center inventory remain fixed.
The complete 19-native-call p17 word makes this substitution 19 times, while
retaining all 16 copied queries and 3,584 whole idle jobs. It has 11,560
productive fields, 69,273 paid jobs and rank surplus 800.

[PROOF.md](PROOF.md) gives the retiming and conditional transfer argument.

`native.py` executes the changed word in both orientations with two retained
interpreters, with all 632 persistent inputs arbitrary and the owned center
arbitrary on entry then legally cleared. Each new physical edge is lowered
and decoded including its absolute phase. The unchanged helper boundaries
and old-edge phase certificates are inherited with exact source pins.

## Complete conditional transfer and smaller rank

Exact rational intervals place the changed raw root in

```
0.0030012390170 < C_root < 0.0030012390173.
```

The verifier proves strict decrease on `[0,.01]`; no global mechanism ceiling
or uniqueness outside that interval is claimed. It tests `C=.00300122` and
uses chronological power 675, paid cutoff `18^675`, target floor `22^675`
and higher-moment offset `u=3/25`. Both original-paid and completion tails
are included. The explicit rational bounds are

```
alpha < 1−19/10^9,  gamma < 491/500,  delta < 391/400,
1/(1+675×19/10^9) + 2(491/500)^675 + 2(391/400)^675 < 1.
```

This pays strict target completion and splitting. The logarithmic compiler
uses contraction `15/16` and power 160; it checks both initial-range and
complement-capacity inequalities and an exact integer final-rank inequality.
The smaller previous grid rank fails that inequality. Every suspended
instance owns its own center and matching program. Whole-job adapters remain
around each replacement. The huge product/uniform words are specified
algorithmically, not materialized.

The source stronger BIT admission 0.0034 and atom power 0.004 are retained.
All nine outer rows, 54 current strict predicates, four functional guards and
63 legacy predicates pass at the new κ. The same-κ comparison also executes
the complete current outer ledger. The complete raw nonrecursive budget
remains 10^9 records, including scalar, query, route and boundary allowances;
fixed precision and stock constants follow the inherited finite-list
prescription with these changed finite ranks.

## Literature and discovery

[LITERATURE.md](LITERATURE.md) evaluates five papers from the original 0.0023
list and records the failed routes. Causal lifting suggested respecting the
actual availability constraints; catalytic workspace suggested a joint-boundary
experiment. Neither theorem is imported. The successful experiment generates
new frame subspaces instead of restricting every move to old frame labels.
The final accepted move does not consume catalytic or unpaid workspace.

Optional discovery needs C++20 and writes only to a new output directory:

```sh
python3.12 -B research/native-lattice-retiming/discover.py --output /tmp/new-lattice-discovery
```

Scientific replay is standard-library Python and needs no optimizer:

```sh
python3.12 -B scripts/research_package.py --package research/native-lattice-retiming
```

[VALIDATION.md](VALIDATION.md) records the completed checks and exact source
heads. [NOTICE.md](NOTICE.md) retains attribution. No Lean, Docker, selected
promotion or historical all-suite replay is part of this contribution.

## Open next questions

- Can simultaneous moves to different frame labels remove more paid moment?
  The current single-label and line/hyperplane experiments are not global
  optimization certificates. Start with a complete charged local word.
- Can an accumulating native interface share a query across multiple targets?
  Dumas–Grenet suggests a distribution pattern; actual intervening Fourier
  progress, arbitrary dirty baselines and restoration still need pricing.
- Can the changed profile support a materially larger κ through a different
  native graph or controller alphabet? Parameter retuning cannot cross this
  profile's recorded root; a changed paid or productive interface is needed.
