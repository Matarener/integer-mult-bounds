# Complete tariff consequences and unpriced obligations

The source is PR5599 at `09dd0965711ca7eeb169057a420abab1c9052137`.
Its exact local paid and independent-helper histograms are retained in
`sources/p104-result.json`. Their net rank mass is 1720 per full call.
This section includes every term of the declared recursive star tariff.
It does not assign zero cost to a missing physical implementation.

## 1. The entire recursive profile

Let g be the number of leaves, q the number of coupled ports per binary
block, and R the total thin matrix rank per block. Scale to 104 native ports.
The signed target-minus-paid moment at exponent t is

```text
M(g,R/q;t) = 208 H_(8g+1) + 208g H_9
            + 2g helpers - 2g paid - 104(R/q) H_1,
H_r = r^t.
```

The first term is the core target. The second term is every leaf target.
Every full call retains the complete paid profile and independent helpers.
Every thin rank unit costs one rank-one query. The proof permits a favorable
fractional block count when it derives a lower bound; actual constructions
must use integer blocks or provide the missing mixed block contract.

The linear margin is `96g+208-104(R/q)`. This formula is a complete recursive
tariff for this declared algebraic comparison. Native frame realization and
nonrecursive obligations remain distinct.

## 2. A uniform ceiling for one or two coupled ports

The chronological theorem gives

```text
R/q >= 4 + (2/q) ceil((g-2)/3).
```

For q<=2, this is at least `4+(g-2)/3`. Define

```text
C(t) = 208*9^t + 2 sum helpers_r*r^t - 2 sum paid_r*r^t.
```

For all g>=3, the moment therefore satisfies

```text
M <= 208(8g+1)^t + g(C(t)-104/3) - 1040/3.                     (1)
```

Take saving `alpha=8/3125=.00256`, so `t=3117/3125`. The function
`y -> y^t` is concave on positive y. Its tangent at `8*32+1=257` bounds
the right side of (1) by `s*g+c`, where

```text
s = 1664*t*257^(t-1) + C(t) - 104/3,
c = 208*257^(t-1)*(1+256*alpha) - 1040/3.
```

Exact integer-power intervals give `s<0` and `c<-7`. The interval endpoints
are in RESULT.json. Thus **every integer leaf count g>=3 loses at .00256**
for q<=2, even in the favorable fractional relaxation.

After equal ranks are cancelled, positive terms have rank at least eight
and negative terms have rank at most seven. If the margin is negative at
t0, its margin at any `0<=t<=t0` is at most `8^(t-t0)` times that negative
margin. Consequently every saving from .00256 through 1 is rejected.
This is a family-wide tariff ceiling, not a root search on a finite range.
In particular this family cannot reach selected kappa .00310045.

The two smaller positive leaf counts also lose. At g=1 or g=2, the static
rank K=2d already requires R/q>=4. Their linear margins are -112 and -16.
Separated ranks then reject every concave moment. Thus the stated ceiling
covers every positive leaf count, not only the long callers.

For the requested g=31,q=2 case, R>=28. Its 104-port bill therefore needs
at least 1456 rank-one thin queries, instead of the proposed 520. For the
old g=127,q=1 case, R>=88 instead of ten. Both complete optimistic profiles
are recorded. Additional nonnegative charges cannot repair their loss.

## 3. A complete binary endpoint as a control

WORD31.json gives a real 31-leaf binary word with 62 full calls and 16 thin
maps of rank eight on each two-port block. Its full normalized endpoint is
proved in COMMUTING.md and checked without expansion into 2^31 terms.
At 104 ports it uses 52 blocks and 6656 rank-one thin queries. All source
full-call helpers and paid terms remain in its profile. Its linear margin
is -3472, and the same separated-rank argument rejects every concave moment.
It is a positive operator control with a negative complete recursive price.

This is not the requested five-rank-two word. The theorem proves that such
a word cannot exist under the paired-star contract.

## 4. Larger coupling and the remaining obligations

At 31 leaves, five rank-q maps require q>=20. Using q=26 divides the 104
ports. Its optimistic moment is positive at saving .0035. The smaller
13-leaf, q=8, five-rank-eight profile is positive at .0034. Exact intervals
are saved. Neither profile has a supplied word. COMMUTING.md proves that
neither can use commuting full-call projectors. A larger scalar field with
all maps linear over that field is not a substitute for this missing word.

| Obligation | Status in this package |
| --- | --- |
| Chronology of the requested 31-leaf/five-rank-two word | Excluded by PROOF.md |
| Every coefficient of the 31-leaf control word | Proved and exactly replayed |
| Source full-call paid and helper profiles | Pinned complete source input |
| Thin query tariff | Charged by actual rank, or by a proved lower bound |
| Native realization of new coupled frames | Unknown; no zero-cost assumption |
| Owned and borrowed state, input reads and dirty compensation | Unknown for new frames |
| COPY, CLEAR, retained values and complete restoration | Unknown for new frames |
| Physical routes, tapes, precision, stock and uniform compiler | Unknown for new frames |
| Outer transfer and a new complete kappa | Not supplied |

PR5701 gives separate characteristic-zero trace qualifications for direct
square-zero lifts of the static PR5681 construction. This package does not
repeat or bypass them. A positive binary word must still receive its actual
native contract and a complete physical bill before it can improve kappa.

Credit the PR5599 tariff, PR5673 profile, and all retained P104/helper/native/
compiler contributors. The new cost conclusion uses the chronological bound
in this package. Ali Romman with substantial OpenAI Codex assistance.
Apache-2.0.
