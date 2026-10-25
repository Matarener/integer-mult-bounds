# P8 exterior-family floor at the fixed three-role embedding

## Combined theorem and division into ranks

For the fixed targets, six-query dictionary and exact endpoint below,
every rational h on the 112 physical ports has full-group invoice at least
18, with equality. The three target indicators are independent, so adjoining
h has rank either three or four. This file proves the rank-four case;
[RANK3-PROOF.md](RANK3-PROOF.md) separately proves the rank-three case with
its full additional reader freedom. Together they cover all rational h.

## Rank-four theorem

Fix the canonical indicators c0,c1,c2 on physical port pairs `[0,67]`,
`[7,64]`, `[1,75]`, in groups 17/18, 29/30, 31/32, respectively. Let h be any
rational vector on all 112 physical scalar ports such that
E=[c0,c1,c2,h] has rank four. Form the six queries

```
h, c1+c2+2h, c0+c2+h, c0+c1+h, 2c0+c1+c2, c0+h.
```

Every rational reader matrix that reconstructs the exact canonical endpoint
c0*c0^t+c1*c1^t+c2*c2^t has full-group invoice at least 18. This minimum is
attained, for example by h=-e_67 and the star readers in `README.md`.
Consequently **no rank-four exterior h can give a saving with this fixed
query dictionary and embedding**. This quantifier covers all rational
coefficient values and h outside the six marked ports. An exact reduction of
all rational coefficients justifies the finite-coverage proof below.

The theorem concerns this one fixed physical embedding and exact endpoint.
It does not cover another added point/query dictionary, other geometries,
or changed allowed-free strict-fit entries. This rank-four argument alone
does not cover all readers when E has rank only three. Eighteen rank-three
source patterns below are retained with the same coefficient-reader equations
as a relaxation used in the rank-four proof. The complete rank-three reader
freedoms are handled separately in RANK3-PROOF.md.

## Coefficient-reader equations forced by rank four

Let A be the 4x6 query coefficient matrix in `README.md`, so Q=EA. The
canonical endpoint columns at a port belonging to target j equal E e_j;
all other endpoint columns are zero. Since E has rank four, each target
reader r must satisfy A r=e_j. Every other reader column must lie in ker A
and may be replaced by zero without increasing any group support or cost.
Thus only the six marked output ports need be retained, with two independent
copies of each singleton demand e0,e1,e2. These equations are independent
of h and remain sufficient even if a source-support reduction collapses E.

## Exhaustive source-support dominance, not a value grid

For a marked source port belonging to target j, write x for its h value.
Its six query entries are as follows:

| target | q0 | q1 | q2 | q3 | q4 | q5 | possible special x |
|---|---|---|---|---|---|---|---|
| c0 | x | 2x | 1+x | 1+x | 2 | 1+x | 0,-1 |
| c1 | x | 1+2x | x | 1+x | 1 | x | 0,-1/2,-1 |
| c2 | x | 1+2x | 1+x | x | 1 | x | 0,-1/2,-1 |

Outside these listed values every x-dependent entry is nonzero. Replacing
such an x by zero therefore only deletes entries and keeps the constant
entries unchanged. Every listed value is retained separately: no possibly
useful zero pattern is lost. At an unmarked source port all query entries
are scalar multiples of h at that port (q4 is identically zero), so setting
that h coordinate to zero also only deletes entries.

Do this independently at every source port. The first three columns of E
stay unchanged, and every retained reader still satisfies A r=e_j, hence
the exact endpoint stays unchanged. Every query support shrinks, so the
complete physical source-group support shrinks and every term tariff is
nonincreasing. The transformed E may have rank three; that causes no
problem because the old coefficient-reader identities remain valid.
A lower bound for all transformed patterns under those retained identities
is therefore a lower bound for every original rank-four h.

There are exactly 2^2*3^4=324 retained patterns on the six marked source
ports. The replay stores twice x as integers in alphabets
`[0,-2],[0,-2],[0,-1,-2],[0,-1,-2],[0,-1,-2],[0,-1,-2]`.
This is a complete quotient by query zero patterns. It includes 306 rank-four
and 18 rank-three patterns; rank is three precisely when both copies of each
of the three target marks have equal h values.

## Exact reader-support and tariff optimization

For every source pattern, the same exact coefficient-reader equations apply.
The complete minimal supports from all 64 query-subset tests per demand are

```
e0: [33,14,19,50,60]
e1: [40,22,15,27,39,53]
e2: [36,26,15,23,43,57].
```

Replacing a reader by a minimal-support exact solution contained in its old
support cannot raise any full-group cost. Each listed support supplies such
a solution. The two copies of each demand are independent, so there are
5^2*6^4=32,400 reader-support cells per source pattern, covering all rational
readers subject to the forced equations.

The replay builds all 4096 physical source/reader union tariffs for the six
fixed groups. It authenticates the canonical cover and binary labels using
the two foundational SHA256 pins in `SOURCES.json`. It also checks every
single-group source and reader monotonicity inequality. Only 27 distinct
source tariff rows occur. The 324 source patterns induce 160 distinct ordered
six-query tariff tables; identical tables have exactly the same support
optimization and can be reused without losing orientation or query labels.

For each distinct table, complete branch and bound uses the monotone partial
invoice and the maximum of each remaining group's cheapest single addition.
Every such value is a valid lower bound for every completion; increments
are never added across different unassigned groups. A feasible reader is
retained as incumbent. Pruning at a bound equal to the incumbent excludes
only candidates that cannot improve it. Thus the returned value is an exact
minimum, not merely a feasible upper bound.

The 160 exact solves visit 13,089 branch nodes in total. Every source pattern
also receives an explicit reader witness, actual reader-group masks, and
term costs. The replay reconstructs each witness with rational elimination,
checks its 36 marked physical endpoint entries (all other source and output
entries are zero by construction), and independently sums the tariffs.

## Results

| exact minimum | number of source patterns |
|---:|---:|
| 18 | 10 |
| 21 | 10 |
| 22 | 13 |
| 23 | 24 |
| 24 | 25 |
| 25 | 60 |
| 26 | 182 |

The global minimum is 18. Six of its ten source patterns have rank four,
so the bound is attained inside the stated theorem's scope. The 260 patterns
using at least one -1/2 root have minimum at least 21; none contributes a
saving. This latter observation is a finite subclass result, not a claim
about arbitrary coefficient normal forms elsewhere.

The primary replay regenerates all 324 rows and every exact witness. Its compact
[RESULT.json](RESULT.json) records the complete ordered minimum-row digest,
histogram, source/rank/reader coverage counts, and the six rank-four attaining
patterns. The digest includes every twice-h tuple, coordinate rank, ordered
source masks and minimum; it does not replace coverage regeneration. Rows are
ordered by the Cartesian product of alphabets `(0,-2),(0,-2)` followed by four
copies of `(0,-1,-2)`. The canonical encoding is `json.dumps(rows, sort_keys=True,
separators=(",", ":"), ensure_ascii=True).encode("ascii")`, hashed by SHA256.

`verify.py` is standalone and authenticates the two scientific inputs directly.
It derives the affine root classes and minimal readers, rebuilds all physical
tariffs, regenerates the complete family, and compares its compact receipt.
Default replay is read-only; `--write-receipt` explicitly regenerates it. The
proof of the rational-family reduction above remains a written argument;
the finite coverage and optimization stages are exactly replayed. This is not
a proof-assistant formalization or an independent human review.

## Independent replay and boundary controls

[The independent proof audit](INDEPENDENT-PROOF.md) accompanies the standalone
`independent_check.py`. It imports no producer code and exhausts all 10,497,600
source-stratum/minimal-reader cells without branch-and-bound pruning. It
independently reconstructs the physical binary tariffs, rational minimal
readers and exact endpoints, and records the same canonical minimum-row digest
in [INDEPENDENT-RESULT.json](INDEPENDENT-RESULT.json). Both arithmetic methods
produce the stated histogram and the original/reduced costs 21/18.

Each of the six finite rank-four strata attaining 18 has a unique minimizing
minimal-reader pattern, all omitting q1 and q4. This statement concerns these
six strata after the source and outside-reader reductions. It is not a claim
about every unreduced exterior h or reader. In the retained rank-three
relaxation h=-c0, there are 25 tied minimal-reader patterns, 24 using q1 or q4.

Meaningful controls exercise the scope boundaries. Omitting the -1/2 source
root loses a q1 cancellation that x=0 cannot dominate. With h=0, the physical
query q5 alone recovers c0 although A e5=e0+e3, showing why the retained
coefficient-reader equations are incomplete for a separately posed rank-three
problem. Deleting an h coordinate outside the marked ports preserves exact
recovery while dropping coordinate rank from four to three. The independent
checker additionally rejects an underpriced invoice and a corrupted reader,
and checks the two fixed witnesses on all 112^2 physical endpoint entries.

## Source attribution and remaining obligations

The coefficient representation is classical P8, with the three marks and
five original queries given by Choe, Oxley, Sokal and Wagner,
[Homogeneous Multivariate Polynomials with the Half-Plane Property](https://www.math.lsu.edu/~oxley/ycjoasdw.pdf),
Example 11.8 equation (11.6) and Appendix A.4 equation (A.1). The sixth query
q5=c0+h is the particular added point studied here. The literal P8 matrix
uses rational entries 2; it is not silently replaced by a ternary sign matrix.
The independent checker verifies its 70 maximal minors and a characteristic-two
obstruction as background; neither that obstruction nor representability
alone implies a tariff saving.

The target cover, labels and complete-group invoice retain the source
attribution in [README.md](README.md) and the exact pins in
[SOURCES.json](SOURCES.json). The earlier five-query/three-mark P8 restriction
is already covered by the upstream p112-triad-matroid-boundary result.
The added ninth point is the particular extension analyzed here.

Other added points, marked triples, physical placements, rank-three
extra-reader freedoms and changed strict fits are outside the theorem.
No native schedule, dirty-state restoration, storage, all-size supplier or
improved multiplication bound is supplied. Prepared by flyingviper with
substantial OpenAI Codex assistance and separate AI-agent checks. Apache-2.0.
