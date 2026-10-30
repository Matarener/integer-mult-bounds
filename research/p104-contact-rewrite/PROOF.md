# A complete conditional contact rewrite

The claimed value is **kappa = 0.00310676333**. The comparison is the open
PR5651 value 0.00310644469. The increase is 0.00000031864. This construction
keeps the five selected framework assumptions and the helper endpoint
contract. It does not change the selected record.

## 1. Exact sources and composition

The retained export is PR5627 at
`ed4dc88a09a7d201971f6603b8c2074e95dd9c32`. It contains 36 source files and
one export manifest. Authenticate the archive, its complete inventory and
each file before import. Also authenticate the retained PR5644 constructor,
witness, word and the PR5643 word.

First apply the three fixed PR5644 helper relations. Compare the result with
the complete published word. Each relation changes the local paid profile
by `-H1-H5+H6`. All public inputs, targets and owned instructions stay fixed.

Then apply zxv's PR5643 A2 change. Check its entire scalar-program difference
against the published PR5643 word. Locate the same two gates in the PR5644
word. Replace them by the three published gates and rebuild the nested public
paths. The complete local paid change is `H2+H6-H3-H5`. Full replay checks the
composition; numerical headline gains are not added. PR5650 already publishes
this composition, and PR5651 checks it again. Compare with the retained
PR5650 word after rebuilding the same public MOVE order. Each changed order
only swaps consecutive MOVEs on different public fields. The scalar and
owned chronology stays fixed. No new composition result is claimed here.

## 2. The new four-gate identity

Let `c=165`, `h=586`, `s=733` and `x=21`. The old gates are

```text
h <- h - 4s       at frame 597
c <- c + 2s       at frame 597
c <- c - x/2      at frame 652
x <- x + h        at frame 652
```

The first two sites are separated by other operations. The witness checks
that none of the intervening operations reads or writes c, h or s. The two
late gates are consecutive in the scalar skeleton. Operations on x before
the late pair retain their order.

Use these gates instead:

```text
c <- c + h/2     at frame 3
h <- h - 4s      at frame 597
x <- x + h       at frame 652
c <- c - x/2     at frame 652
```

Here frame 3 is `{0}`, frame 597 has basis `[82]`, and frame 652 has basis
`[82,268]`. The new early read uses the old value of h. The new gates are
placed at the old late pair after the two early updates are removed.

Write the values before these updates as c, h, s and x. Both programs give

```text
c_out = c + 2s - x/2
h_out = h - 4s
s_out = s
x_out = x + h - 4s
```

The verifier also compares both full 4 by 4 rational matrices. More generally,
this identity holds for coefficients alpha, beta, gamma and delta when
`beta = alpha*gamma*delta`; the early coefficient is `-gamma*delta`.
The A2 identity and compensated triangle method are prior work. The new
result is this source-bound four-gate schedule and its paid native path.

The new schedule lets c remain in dimension zero until its dimension-two
contact. Its old two rank-one requests become one rank-two request. Every
other paid count has the same value. Thus

```text
new local paid delta = -2 H1 + H2
new local target delta = 0
```

For every `0<t<1`, `2-2^t>0`. The complete caller uses the local word 18 times,
so this new component improves the signed moment by `18*(2-2^t)`.

For this fixed dimension-zero to dimension-two path of c, the new transport
also has the minimum cost among strictly nested subdivisions. Such a path
has either one rank-two step or two rank-one steps. For `0<t<1`, the former
costs `2^t<2`. This local minimum keeps the neighboring contact charts fixed;
it does not restrict a changed scalar graph or a different caller.

## 3. Complete native interface

For a frame V, a field contains its canonical native chart applied to its
logical value. A public MOVE changes between strictly nested frames. Every
ADD and SCALE uses one common chart. COPY uses a cleared owned field. The
new program keeps every owned instruction in its original order.

The first interpreter checks all public and dirty-owned input columns. A
separate dense integer interpreter checks the transposed instruction matrices
in reverse order. The two checks cover 565,504 endpoint coefficients. All 743
public inputs keep their original endpoints. The nine owned roles have eleven
lifetimes and peak occupancy two. They receive no productive target credit.

The native checker binds each paid map, each helper boundary and every main
adapter, including the global phase. The common-chart induction applies at
every positive tensor width. Scalar coefficients stay outside the tensor
power. No tensor power of a sum is replaced by a sum of tensor powers.

The retained physical p16/a7 caller has 18 full forward calls, 15 thin query
sites and 3,120 whole idle jobs. Its 104 ports, 7,488 boundary contacts and
53,248 central-square column checks are retained. Each helper target has its
native normalizers. Every thin query and whole idle remains charged.

## 4. Complete invoice and conditional bound

Relative to PR5627, the local paid change is

```text
-5 H1 + 2 H2 - H3 - 4 H5 + 4 H6
```

The final local paid profile is

```text
{1:2195, 2:458, 3:493, 4:91, 5:159, 6:22, 7:15}
```

The helper profile remains

```text
{1:2, 2:4, 4:91, 5:6, 7:5, 8:16, 9:411}
```

The complete caller has **66,474 paid requests**, **12,958 productive fields**
and rank-mass surplus **760**. All targets from the consumed source remain.
The independent path-length count gives the same invoice.

Two rational interval engines check the signed moment. Its unique raw
crossing lies in `(0.00310676334487,0.00310676334488)`. The derivative bound is
strictly negative on `[0,0.0034]`. This is a ceiling for this fixed invoice,
not for other words or callers. The claim leaves between 1.487e-11 and
1.488e-11 below that crossing. The tested saving is 0.003106763335.

The full retained compiler calculation includes the paid ratio, both tail
ratios, completion, splitting, rounding, complement capacity, logarithmic
threshold and all 54 strict plus four functional outer predicates. It keeps
the ordinary BIT admission 0.0034. `RESULT.json` records the exact constants.
`PRICING-EDITS.json` lists each change from the authenticated price source;
no compiler or outer predicate is removed or weakened.

The local ordinary bound includes every scalar instruction, paid-map route,
helper normalizer, main adapter, boundary contact and owned lifetime. It stays
below 10^7. The complete ordinary allowance stays below 10^9. The retained
finite coefficient, operation and native-rank bounds also cover the new word.
The precision and fixed-tape contracts remain conditional assumptions.

## 5. Scope of the search

The discovery first tried different carriers, paid endpoint extensions,
MOVE-only scheduling, retained histories and scalar contractions. None of
those tested domains gave an accepted paid gain. They are not general lower
bounds and are not needed to verify this construction.

A two-step A2 search found the new identity. The retained `patterns.py`
checks one specific pattern of public scalar dependencies and coefficients,
before frame selection. It finds this one pattern in the composed source
and none in the final word. `verify.py` checks both counts. This census does
not enumerate all scalar identities or legal frame schedules. Other
dependency orders, longer sequences, different callers and new native
providers remain open.

The result is a small complete conditional improvement. It is not evidence
of a large breakthrough or a global maximum. The enormous uniform compiler
word and the complete rounded multiplier are not materialized. The author
checks are not independent scientific acceptance or a proof-kernel theorem.
