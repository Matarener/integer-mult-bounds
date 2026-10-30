# Triple-source connector steps do not lower the five-source query floor

**Negative bound for one charged alphabet extension; no new κ.** Selected κ
stays `0.001672660197076918`.

The pair-source package attains 72 complete queries on the five-source
all-31-nonzero-mask connector batch, and asks whether a triple-source call
`B_{jkℓ}` can push the source path down to length 8 or 9. It cannot. The
obstruction is the prefix set, not the step weights. Every closed walk whose
pairwise prefix differences include all 31 nonzero masks has length at least
10, for steps of weight 1, 2, 3, 4, or 5. The batch therefore costs at least
`62 + 10 = 72` queries. Weight-at-most-2 calls already attain 72, so charging
a triple call as one query plus three source-leaf accesses does not improve
that query bill.

On any covering closed walk of length 10 that uses a step of weight at least
2, the source-leaf bill at prices `(1, 4, 10, 16, 28)` is at least 120 after
assigning the repeated source to the cheapest price. The published pair-call
word meets 120. A triple does not undercut it.

## Contract

The fixed interface is the one in
`research/universal-connector-boundary`: five immutable sources, one
arbitrarily dirty connector, and 31 nonzero output rows, each read twice.
The connector is restored at completion. Prefix differences of the source
walk are the available masks.

The added operation is a triple-source call

```text
B_{jkℓ}: z += B_j x_j + B_k x_k + B_ℓ x_ℓ
```

one query record and three coefficient/source accesses. It is not free. The
same prefix argument also covers weight-4 and weight-5 steps. No selected
caller, native layout, or supplier admission is claimed.

## Argument

Let `P` be the set of source-prefix values on a closed walk of `L` steps.
The last prefix repeats the first, so `|P| <= L`. Distinct nonzero
differences need `C(|P|, 2) >= 31`. Thus `|P| >= 9`, because
`C(8, 2) = 28 < 31`, and `L >= 9`.

Differences are translation-invariant, and every nonempty set has a
translate containing `0`. It is enough to inspect the `C(31, 8) = 7,888,725`
nine-point sets that contain `0`. None of them satisfies `P XOR P = F_2^5`.
The largest number of distinct nonzero differences is 28, which is 29 masks
once the automatic zero difference is counted. That is the same maximum
coverage 29 reported for nine-point sets by
`research/connector-pair-source-path-seed2cdb`. Therefore `|P| >= 10` and
`L >= 10`.

Two scans produce the same count, cover count, maximum, and checksum: an
index odometer, and `itertools.combinations`. Neither imports the
predecessor verifier.

A coordinate hyperplane has only 15 nonzero vectors. A covering walk
therefore uses every source a positive even number of times, so the
incidence total `W` is at least 10. On a walk of length 10, `W = 10` only
when every step has weight 1. One step of weight at least 2 forces
`W >= 11`, and even multiplicities force `W` even, hence `W >= 12`. The
only five even parts of 12 that are all at least 2 are `(2, 2, 2, 2, 4)` up
to order. Pairing multiplicity 4 with price 1 costs

```text
4*1 + 2*(4 + 10 + 16 + 28) = 120.
```

Step weight is at most 5, so `W <= 50` on a length-10 walk. Every admissible
multiplicity type with even total from 14 through 50 costs at least 122.

The published prefixes `{0, 2, 3, 5, 8, 10, 13, 15, 26, 30}` cover all 31
nonzero masks. Deleting any one of them destroys that cover. This checks the
length-10 side of the same difference test; it does not rerun the
predecessor's dirty-map replay.

## What this does not show

The census is a finite exclusion in `F_2^5`, not a classification of every
connector program. It does not decide whether some length-10 walk that uses
a triple attains leaf bill 120. It does not rerun the 945 weight-1 pairing
census, and it does not need that census: the query floor never uses it.
Six sources, delivery cuts, frames, and a physical caller remain outside
this contract. Unknown native costs are not zero. There is no new κ.

## Reproduce

From the repository root, CPython 3.12, standard library only. The census
took about 70 seconds on the recording host; the manifest allows 240.

```sh
python3.12 -B scripts/research_package.py --package research/connector-triple-query-floor
```

Expected:

```text
PASS_CONNECTOR_TRIPLE_QUERY_FLOOR sets=7888725 covering=0 max_nonzero=28 max_masks=29 queries=72 leaves=120 no_new_kappa
PASS_REGISTERED_RESEARCH_PACKAGE research/connector-triple-query-floor outcome=negative-result
```

## Credit

The five-source paired-readout model and the 74-query fixed alphabet are
Ross Richardson's `research/universal-connector-boundary`. The 72-query
pair-call word, the nine-point census target, and open question 1 are Aaron
Wang's `research/connector-pair-source-path-seed2cdb`. The all-tariff
formula for the old alphabet is Adam Gall's. New census, length bound, and
leaf comparison by unpaidmoon, with substantial AI assistance (Cursor Grok
4.7). Apache-2.0. No independent human or proof-kernel review is claimed.

## Open next questions

1. Does any closed length-10 walk that uses one triple-source step attain
   source-leaf bill 120 on prices `(1, 4, 10, 16, 28)`? The query floor does
   not depend on the answer; a witness would show the leaf bound is sharp
   inside the larger alphabet. First step: search multiplicity type
   `(4, 2, 2, 2, 2)` with exactly one weight-3 step and check prefix
   coverage. Nothing structural blocks that search. It is larger than this
   session's census, and a failure would not reopen length 9.
2. For six sources, counting already gives `|P| >= 12` at every step weight,
   because `C(11, 2) = 55 < 63`. Does a 12-point difference basis exist?
   That decides whether the query floor sits at `2*63 + 12` before any walk
   constraint. First step: a structure theorem or a symmetry-reduced census
   of 12-point sets in `F_2^6`. The unrestricted binomial count blocks a
   direct copy of this package's scan.
