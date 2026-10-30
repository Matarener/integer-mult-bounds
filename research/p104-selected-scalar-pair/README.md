# Six fewer scalar allowance units after P104 sign normalization

One exact replacement removes an ADD macro from both the selected #5599
word and its published #5750 sign normalization. It reduces the latter's
retained real scalar allowance from **219258 to 219252**, adding six units
to Sricharan Vagvala's credited 974-unit saving. It preserves all 748 public
inputs, all helper targets, the eight owned-role slots and every one of the
3447 paid MOVE occurrences. The complete paid and productive rank profiles
are identical, so no new kappa is claimed.

| Pinned word | Events before | Events after | Scalar before | Scalar after |
| --- | ---: | ---: | ---: | ---: |
| Selected #5599 | 25475 | 25474 | 220232 | 220226 |
| Sign-normalized #5750 | 25253 | 25252 | 219258 | 219252 |

Claim type: **exact finite circuit improvement with a scoped all-input
algebraic proof**. Search stopped at this first verified improvement.
Publication overlap checking then identified #5750. The same literal block
survives there, allowing composition without another improvement search.

## The replacement

In `research/p104-helper-subspace-splits/WORD.json.gz`, replace zero-based
events 9751 through 9754, inclusive. The identical block is at events 9627
through 9630 in `research/p104-sign-gauge/WORD.json.gz`:

```text
225 += -234
229 +=  234
227 +=  234
225 += -234
```

with:

```text
225 += -2 * 234
229 +=      234
227 +=      234
```

Every operation uses frame 267. The actual source prefix places all four
roles in that frame. Role 234 remains unchanged, and neither intervening
operation reads role 225. For arbitrary initial values a,b,c,d in roles
225,229,227,234, both blocks therefore return

```text
(a - 2d, b + d, c + d, d).
```

This identity holds over the complex payload space at every tensor width.
The prefix and suffix of the complete word are retained verbatim. Composing
either block with those identical contexts gives the same complete endpoint,
including arbitrary dirty inputs and every helper output. This argument
permits arbitrary native maps outside the block; it does not need to replay
or assume any new identity between those maps.

The new value of each role at each macro boundary already occurs for that
role at some old boundary. In particular, the earlier value a-2d is the old
block's final value. Thus this replacement does not increase the maximum
per-role magnitude at scalar macro boundaries. Internal primitive states,
rounding sites and error propagation are separate questions.

The executable constructor in [verify.py](verify.py) authenticates the source
bytes and replaces only this literal block, in memory. The canonical JSON
hash of the constructed sign-normalized word is
`bc123d9989d919caa48086b19a342fa83d8470d6a56e6ceb8d73b43f4ee84f9d`.
No regenerated gzip container is required.

## Exact cost and unchanged recursive bill

The retained `local.py` scalar tariff charges an ADD with nonzero dyadic
coefficient q, numerator magnitude n and positive denominator d, by

```text
2 * (3 + bit_length(n) - 1 + popcount(n) + bit_length(d) - 1).
```

An ADD with coefficient -1 costs 8; coefficient -2 costs 10. The removed
pair costs 16 and its replacement costs 10. The other two ADDs remain.
The complete scalar allowance consequently falls by exactly six units
for each pinned source. The verifier independently sums this tariff over
the original and replacement in both cases,
including their SCALE, COPY, INIT and CLEAR charges.

Every non-ADD event is retained in its original order, with identical ports,
frames and ownership flags. No additional native map, source acquisition,
helper basis change or allocation is required. Setup and dispatch for a
physical caller still need that caller's own accounting; six units is a
saving in the stated scalar allowance, not a measured runtime saving.

## Evidence and reproduction

From the repository root, using CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -I -B research/p104-selected-scalar-pair/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -I -O -B research/p104-selected-scalar-pair/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/p104-selected-scalar-pair
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/p104-selected-scalar-pair --check-source-history
```

Another CPython 3.12 interpreter may replace the local path. The expected
status is `PASS_P104_SELECTED_SCALAR_PAIR`, with `scalar_saving` equal to 6.
The verifier writes no files. Its stdout receipt binds all five package
files and each compressed and decompressed source hash.

The checks include exact rational four-role matrices and every local prefix,
the actual common-frame cut, identical contexts and non-ADD occurrences,
and complete normalized 756-row coefficient propagation for each source
and its replacement.
Normalization treats MOVE as a chart identification. That last comparison
corroborates the scalar endpoint; it does not compute native Gaussian actions
or phases. The local identity and identical-context proof establish equality
in the presence of the actual unchanged native operations.

Eleven controls per source reject wrong coefficients, sign, source,
destination or frame; a missing fanout; changed helper metadata or paid transport; an
intervening source update or target observation; and a changed source block.
All controls use explicit exceptions and remain active under `-O`.

## Scope, provenance and credit

The source base is canonical main
`19fdb086ea96af9a9f87936a2b888e10af4ed810`, priority revision 8. Exact Git
blobs and SHA256 pins are in [SOURCES.json](SOURCES.json). The selected
record and catalogue are provenance, so subsequent priority updates do not
change this fixed result. The two source words are the only runtime inputs.

This is a changed `p104-side-correction` experiment aimed at the current
complex supplier. Its result is a scalar circuit improvement. No later
supplier word is optimized, and no full selected replay, compiler admission, native
phase replay, rounded multiplier or proof-kernel build is performed.
The selected construction's five framework assumptions remain. Exact
algebraic equivalence does not assert equality of two rounded executions.

This contribution was **produced by Nick Petalas**. Ali Romman supplied the
selected #5599 independent-helper-split word. Pierre-Loic Doulcet supplied
the #5565 commuting-contact lineage; David Arias the coalesced word; Gareth
Davidson its composition; and Cinna Davis the private reuse and productive
controller lineage. The source README retains the full P104, native,
geometry, caller, compiler and pricing attribution.

Cinna Davis's #4692 already supplied commuting-ADD compression and triangle
rewrites for an older 632-public-input word. The commutation method keeps
that credit. Sricharan Vagvala / theon199 supplied the published #5750
sign-normalized word and its 974-unit saving. The new artifact is this
literal six-unit reduction, including its composition with that word.
No predecessor executable is imported or modified. Independent human and
formal proof-kernel review are unclaimed.
Apache-2.0.

## Verification bounds and deviations

All loops are bounded by the authenticated source: at most 25475 events,
1089 frames, 756 symbolic rows and 756 columns per row. The local check uses
four roles and at most four events; there are eleven fixed controls per source.
Reads are capped at 256 KiB compressed and 4 MiB decompressed. No recursion,
dynamic code loading, subprocess, network access or mutable shared state
is used. Functions remain below 60 lines. Warning-strict normal and optimized
execution, Ruff 0.17.2 checks and syntax and indentation diagnostics check
the touched code.

Power of Ten rule 3 deviation: Python and Fraction allocate during this
bounded offline calculation. The exact source hash and the explicit bounds
above constrain live collections; the verifier has no service loop or
unbounded input domain. A fixed-capacity implementation would be needed
before reusing this checker in a streaming or real-time component. The
registered timeout is an additional execution guard, not a proof of a
memory or arithmetic complexity bound.

Rule 9 deviation: the rejection-control helper accepts one of three fixed
checker functions, `local_identity`, `boundaries` or `construct`. This is the
control substitution boundary; no source data selects a callable. Its fixed
call sites and eleven rejection cases constrain and exercise every target.
Replace it with explicit dispatch if the control interface ever accepts
external definitions.

## Open next questions

1. Can a later scalar rewrite eliminate an actual paid frame transition?
   Specify one different block's complete entry and exit frames, and price
   every changed native occurrence. The present scalar saving does not
   change the signed recursive moment; no later block was searched.
2. Does an active successor retain this exact block? Locate it by roles,
   coefficients and frame in one pinned successor, then establish its legal
   boundary. Event indices alone cannot transfer the patch, and successor
   helper bases may differ. No such transfer is supplied or reserved.
