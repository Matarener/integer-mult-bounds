# A second entrance cannot use the two unchanged release slots

For both pinned PR4076 words, raising ordinary helper 544 from
`E = span_F2(414,51)` to `P = span_F2(392,37,22)` is incompatible with **every**
monotone scalar frame assignment on the unchanged contact word.  The separating
direction is `22`.  A three-contact path forces it into target 116, whose fixed
terminal frame excludes it.  This rules out the proposed `7 -> 6` width move on
those release slots; there is no admissible local profile delta for that move.

The first result concerns a fixed scalar contact network.  A separate local
theorem below tests a concrete changed release block at the cut before old
B1752.  Deleting or retiming other consumers, changing native maps or changing
target/terminal contracts remains outside both theorems.

## Pins and exact model

The source head is PR4076
`9744f9df268590295a9872b1952c695a678192b9`.  The canonical base recorded for this
investigation is `bb4bccbf42844d2801487450727c2f63e10d1d0f`.
[SOURCE-EXPORT.json](SOURCE-EXPORT.json) binds the nine exported files to their
source Git blobs and SHA256 values.  `independent.py` authenticates this complete
export before reading both `NEW-base.json.gz` and `NEW-extra.json.gz` and checks
their canonical JSON digests from the pinned source `INPUTS.json`.

The binary ambient space is `F2^9`.  A nonzero scalar add has one common frame for
its source and destination.  Successive frames on each register are monotone by
inclusion between native maps.  The exact starts of all registers other than
544, helper terminals, target cut levels, centre entry frames, prelude/native
entry and exit frames, native maps, scalar contact incidences and order remain
fixed.  The scalar gate frames may otherwise be chosen arbitrarily: the old
scalar frames are **not** lower bounds in this calculation.  The unchanged
scalar coefficients are retained, though the short frame obstruction uses only
the nonzero contacts.  Wrapper and private-copy cut operations retain their
source contract and do not provide a frame reset on this path.

## The short written obstruction

Here indices are zero-based indices in each pinned word's `B` list.

| Index | Scalar operator | Forced common-frame propagation |
| --- | --- | --- |
| 683 | `672 += 544/2` | `544 -> 672` |
| 1116 | `672 += 462` | `672 -> 462` |
| 1738 | `116 += 462` | `462 -> 116` |

`22` belongs to `P` and not to `E`.  At B683, monotonicity and the common-frame
rule place `22` in helper 672's frame.  It persists to B1116.  The common frame
at B1116 also places `22` in helper 462's frame, even though 462 is the numerical
source of that add.  This is a frame constraint, so numerical data flow in the
opposite direction cannot evade it.  It persists to B1738 and then to target
116's terminal frame.  No native warp touches 544, 672 or 462 anywhere in either
word.

Target 116 has port `131`, hence terminal frame
`{x : <x,131>_F2 = 0}`.  But `22 & 131 = 2`, so `<22,131>_F2 = 1`.
This is a contradiction.  Extra paid upward frame changes cannot remove the
direction.  The proof holds for arbitrary scalar frame choices and arbitrary
numerical register contents, including all dirty helper values.

There is exactly one dimension-three entrance containing `E` and contained in
the first producer frame `P`: it is `P` itself, since both have dimension three.
The finite census independently enumerates all 127 dimension-three extensions
of `E` in `F2^9`; only `P` is contained in the first producer frame.  Thus no
alternative basis or different third direction inside that producer frame
avoids the obstruction.  The theorem for this entrance is stronger than fixing
the first producer's scalar frame to `P`: it still holds when that scalar frame
is allowed to grow.  Uniqueness of `P` is claimed only under containment in the
inherited first producer frame, not for other third directions with a changed
producer contract.

## Independently built least-frame certificate

Each scalar contact is one vertex; each register's chronological continuation
is a directed containment edge into its next contact.  Starts are fixed source
vertices.  An exact native entry, target cut or centre entry fixes the previous
contact vertex by assigning it that frame as both a lower and upper bound.
Native exits are new fixed vertices, with no invented monotone edge across the
native map.  A terminal vertex permits the actual final upward climb and is
bounded by its fixed terminal frame.  All native maps and inverses are checked
by exhaustive application to the 512 binary vectors.

For a vertex `v`, let `S_v` be its fixed lower seed, and define in chronological
order `L_v = span(S_v union union_{u -> v} L_u)`.  Any feasible assignment
contains `L_v`, by induction.  Conversely, if every `L_v` is contained in its
declared upper bound, the assignment `v -> L_v` satisfies all edges and fixed
boundaries.  A vertex with both seed and upper bound `U` then has value exactly
`U`.  This proves that the algorithm gives the least assignment and that its
upper-bound failures are decisive; it is not merely a failure of a chosen
frame heuristic.  The implementation uses explicit immutable vector sets and
imports no source frame walker, solver, constructor or semantic interpreter.

Both providers produce the same exact constraint result: **7,491 vertices and
12,306 edges**.  The original entrance is feasible.  Raising it changes one
start, 46 scalar contact vertices and four terminal vertices.  Each changed
least frame gains exactly one dimension.  The affected B contacts are

```text
683,684;
1104..1123;
1736,1737,1738,1740,1741,1742,1744,1745,1746,1748,1749,1750,
1752,1753,1754,1756,1757,1758,1760,1761,1762,1764,1765,1766.
```

Their contacted registers are
`109,116,117,180,181,227,229,234,241,316,318,328,462,463,470,471,544,672,673,674,676`.
The first producer B685 and the subsequent producer B686 do not enlarge their
least frames: they already contain `P`.  There is no affected A, restore or
native-exit vertex and no violated native, target-cut or centre upper bound.
Exactly four terminal bounds fail:

| Target | Port | Required least dimension | Allowed terminal dimension |
| --- | --- | --- | --- |
| 116 | 131 | 9 | 8 |
| 117 | 259 | 9 | 8 |
| 180 | 176 | 9 | 8 |
| 181 | 304 | 9 | 8 |

[independent-result.json](independent-result.json) gives every changed vertex's
old and raised basis and every violated upper bound, including all outside
points.  This is the exact least constraint cone, rather than a claimed
optimal paid rank profile.  The formal helper-width change from `9-2` to `9-3`
cannot be admitted with these terminal contracts.

## A concrete late recovery is algebraically exact but still blocked

Now delete the two original releases B683 and B684, and consider a new common
release block immediately before original B1752.  At that cut, write `h0` for
the independent original value of helper 544.  The exact recovery row is

```text
h0 = current544 - current379 + 2*current236 + current395 - current283/2.
```

Two independent derivations establish this identity on both words.  Transport
of the recovery covector changes it only at original indices 685, 686, 801 and
1417.  The last gate is `379 -= 283/2`; the earlier update at B801 is
`379 += 395`.  No native warp meets this covector's support.  Separately, a
forward sparse-row interpreter starts with all 632 live B-entry registers as
independent columns and executes the omitted-release prefix.  Native operators
are retained as formal **noncommuting** words on those columns.  The recovery
linear combination is exactly the unit column `h0`, with every other scalar or
formal-operator coefficient zero.  It does not use clean source or helper values.

Adding one half of this row into 672, and minus one half into 676, takes ten
dyadic scalar adds.  Direct comparison of every row and every formal coefficient
confirms that this block restores the entire old current prefix before B1752.
The original prefix has 4,586 nonzero formal coefficients; the omitted prefix
has 4,584.  The matrix hashes in the certificate are receipts for an actual exact
comparison, not substitutes for coefficient equality.  Untouched private buffer
coordinates extend this prefix identity by the identity map; complete cleanup
and contragredient/native circuit admission are separate obligations.

The exact `h0` column of the omitted prefix at this cut is

```text
current544: +1; current208: -1/2; current177: -1/2.
```

Only 544 is a **non-target** carrier; the two target carriers must not be
discarded.  Neither the prelude, wrappers, initial corrections nor cut reads
helper 544 before B, and no native warp acts on an `h0` carrier in this prefix.
Under any feasible raised-entrance frame assignment, every one of these
nonzero carriers therefore has a frame containing `P`.

Here is the general local obstruction, separate from the finite unchanged-word
DAG computation.  At this particular cut, let a finite replacement block use
only nonzero scalar adds/scales with common scalar frames, allow arbitrary
factorization and additional arbitrary dirty scratch, and contain no native
warp or other frame reset.  Assume every existing nonzero `h0` carrier enters
with a frame containing `P`, and each new dirty input is independent of `h0`.
Then throughout the block,

```text
nonzero h0 coefficient in a register => its frame contains P.
```

This follows by induction: a scalar scale retains the carrier's frame; a
scalar add with a nonzero resulting coefficient has at least one operand with
a nonzero old coefficient, and its common frame contains that operand's frame.
An exact cancellation can remove a numerical coefficient but cannot remove a
previously acquired frame direction.  Consequently any such block restoring
the old prefix must give 672 coefficient `+1/2` on `h0`, forcing `P` into its
frame.  Restoring just this one coefficient is already sufficient.

The unchanged following gates are

```text
old B1752: 672 += 227
old B1753: 227 -= 672/2
old B1754: 181 += 672.
```

There is no intervening native reset on 672.  Hence `22` reaches target 181.
That target's port is `304`, and `22 & 304 = 16` has odd parity, contradicting
its terminal hyperplane.  B1752 is a recipient write, not the first donor
consumer or a claimed latest possible cut.  The statement is confined to this
checked cut and these unchanged subsequent consumers.  It proves no global
retiming obstruction, and leaves changed consumer closures and other entrance
contracts open.

## Arbitrary dirty values and controls

The frame contradiction has no numerical clean-input premise.  As a separate
small semantic control, the checker computes all 25 rational coefficients of
the four-gate block B683..B686 on independent input columns
`(h544,h672,h676,r379,r236)`.  The outputs are

```text
h544' = h544 + r379 - 2*r236
h672' = h672 + h544/2
h676' = h676 - h544/2
r379' = r379
r236' = r236.
```

Deleting a release, flipping its sign, or moving both releases after the two
producers without compensation changes that exact matrix.  The dirty helper
columns are retained; setting them to zero would hide the omitted-release
defect.  This 5-by-5 block calculation does not certify full-word semantic
cleanup, contragredient/native Gaussian behavior or a changed construction.

There are 25 explicit controls: for each provider, the old entrance is
admitted, basis reordering preserves the complete result, a broken B1116
witness contact and a wrong target character are rejected by their named
checks, and deleting exactly the four failing terminal upper bounds makes the
least graph feasible.  The last control changes the mathematical contract
deliberately and demonstrates sensitivity to the decisive bounds.  Each of the
five omitted late recovery sources is rejected by all-column comparison, and
the wrong late release sign fails complete prefix equality, for each provider.
The three local all-column semantic mutations are also rejected.  Unexpected acceptance is
raised outside the caught-exception path.

From the repository root:

```sh
python3 -B research/second-staged-544/independent.py --check research/second-staged-544/independent-result.json
python3 -O -B research/second-staged-544/independent.py --check research/second-staged-544/independent-result.json
```

`--check` consumes the fixed certificate and fails if it is absent or differs.
Only explicit `--output PATH` (or its `--write` alias) generates a certificate.
With no arguments, the checker consumes the retained certificate in this
package.  `--output` accepts an external absolute output path for fresh
checkpoint evidence without editing the source package.

## Scope, dependencies and credit

This combines an all-frame written implication on two fixed finite words, an
exact finite DAG/census check, an all-column prefix recovery identity, and a
written scalar-block implication at one particular cut.  It is not a
formal-kernel proof.  It does not rule out a second staged entrance using a
different cut, changed consumer closures, new native maps or relaxed boundary
contracts; those construction obligations remain with the construction
specialist.  It gives
no admissible supplier, recursive cost or kappa improvement, and no assertion
about native Gaussian phases or owner/outer assembly.

The source words are PR4076's credited staged-entry construction, with PR3945,
PR3949, PR3734 and PR3605 lineage.  The word contract was read from the retained
audit core and binary frame walker credited in
[source4076/NOTICE.md](source4076/NOTICE.md).  This check and derivation were
prepared with substantial OpenAI GPT-6.1 Sol assistance.  No independent human
review is claimed.  Apache-2.0.
