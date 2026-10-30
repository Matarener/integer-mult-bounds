# Independent output updates still permit a cheaper boundary

Prepared by @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
The model is commdata2338's PR2020; Nick Petalas's PR5968 asks the rank-two
question resolved here. This is a scoped written proof, with finite checks,
not a formal proof of integer multiplication.

## Model and statement

There are four arbitrary dirty coordinates `(d0,d1,w0,w1)=(x,y,a,b)` over
a nonzero vector space in characteristic two. Addition below denotes XOR for bits.
A compulsory, indivisible child `(o,s,t)` performs, in order,

1. `d[o] += w[s]`;
2. `w[t] += w[1-t]`.

An adapter is one of the two workspace additions or the four additions from
workspace to output. Each costs one. Finite adapter words are allowed before
the first child and after each child, never within a child. There are no free
gates, output feedback, output mixing, extra coordinates or clean-input premises.

The eager reference undoes each child's workspace addition immediately. An
intermediate observation constrains the indicated output rows to equal that
reference; it does not read or alter workspace, feed back, or incur an operation
in this abstract gate model. At the final boundary all four coordinates must
equal the eager reference. Both comparators may retain noncanonical workspace.

Fix children

```
(0,1,0), (0,0,0), (0,0,0), (1,0,1).
```

Observe both outputs after children 1 and 3, and only `d1` after child 2.
The complete final endpoint is

```
(x,y,a,b) -> (x+b,y+a,a,b).
```

The output-update matrix on `(a,b)` is `[[0,1],[1,0]]`, of rank two. For
q-bit coordinatewise streams with q>=1 it has rank `2q`. Neither output is redundant.

**Theorem.** This partially observed fixed-child contract has exact adapter
minimum **2**. Observing both outputs after every child has exact minimum **3**.
Including all eight compulsory child gates, the minima are **10** and **11**.

## Explicit attaining words

Write `U: w0 += w1`, `L: w1 += w0`, and `D: d0 += w1`.
For partial observation, apply U after child 2 and L after child 3.

| Boundary, including adapters | Actual state | Required eager outputs |
| --- | --- | --- |
| Child 1 | `(x+b,y,a+b,b)` | `(x+b,y)` |
| Child 2, U | `(x+a,y,a+b,b)` | only `d1=y` |
| Child 3, L | `(x+b,y,a,a+b)` | `(x+b,y)` |
| Child 4 | `(x+b,y+a,a,b)` | complete final state |

The only discrepancy at any observed-output boundary would be b in d0 after
child 2; that output alone is hidden there. Both incoming dirty workspace
values are returned exactly, with no copy or erasure.

For full observation, apply U at entry, L after child 1, and D after child 3.
The entry changes workspace to `(a+b,b)` and is charged.

| Boundary, including adapters | Actual state |
| --- | --- |
| Child 1, L | `(x+b,y,a,a+b)` |
| Child 2 | `(x+a+b,y,b,a+b)` |
| Child 3, D | `(x+b,y,a,a+b)` |
| Child 4 | `(x+b,y+a,a,b)` |

All four rows are checked at return. The full comparator is optimized over
the same alphabet, rather than restricted to eager workspace restoration.

## Lower bounds without a search assumption

Both workspace generators U and L are odd permutations of the three nonzero
vectors of `F2^2`. Data adapters leave workspace unchanged. Four compulsory
workspace shears have even parity. Therefore a restoring schedule uses an
even number of workspace adapters. With none, its workspace word is U,U,U,L,
which is nonidentity: `(a,b)` goes to `(a+b,a)`. Consequently any correct
schedule needs at least two workspace adapters. The partial word attains two.

Suppose full observation were possible with at most two total adapters. The
preceding argument forces exactly two workspace adapters and no data adapters.
Subtracting consecutive fully observed output rows shows that children 2, 3
and 4 must each read the incoming a from w0. After child 2, its U changes this
row to `a+w1`. The current workspace matrix is invertible, so its w1 row is
nonzero. At least one workspace adapter is required in the gap between children
2 and 3. The same argument requires one between children 3 and 4.

Both adapters are thus spent in those two disjoint gaps. None is available
at entry or between children 1 and 2. But then child 1 leaves workspace
`(a+b,b)`, and child 2 reads `a+b`, not the required a. This is a contradiction.
Full observation needs at least three adapters; its displayed word attains three.

The argument is about independent formal coefficient rows. Special values
such as b=0 do not invalidate it or establish arbitrary-input correctness.
It also proves the conclusion for nonzero characteristic-two vector spaces: the
allowed coefficients remain in F2 and the same formal identities apply.

## Complete local bill and composition recurrence

The displayed words have the following **complete** gate histograms. Entry,
correction and dirty restoration are included; the four children are retained.

| Gate | Partial word | Full word |
| --- | ---: | ---: |
| `w0 += w1` | 4 | 4 |
| `w1 += w0` | 2 | 2 |
| `d0 += w0` | 2 | 2 |
| `d0 += w1` | 1 | 2 |
| `d1 += w0` | 1 | 1 |
| **Total** | **10** | **11** |

Thus the difference between these two words is one output correction, with
both workspace restoration counts equal. For assigned gate prices u,l,r00,
r01,r10, their exact bills are `4u+2l+2r00+r01+r10` and that expression plus
r01. Optimality is claimed for unit prices only, not for arbitrary weights.

For a literal q-bit stream XOR, define `X(0)=0`, `X(1)=1`, and
`X(q)=X(floor(q/2))+X(ceil(q/2))` for q>=2. There is no cross-bit mixing or
charged tape transport in this model, so `X(q)=q`. The complete fixed-child
bills are `P(q)=8X(q)+2X(q)=10q` and `F(q)=8X(q)+3X(q)=11q`.
Each XOR reads its two operands and writes its destination, giving 20q/22q
scalar reads and 10q/11q writes. Four dirty q-bit banks are occupied; additional
scratch, helper initialization, copying and erasure counts are zero.

For m invocations with this same observation pattern and a complete four-bank
return required at each block boundary, the exact sequential recurrence is
`P_0(q)=F_0(q)=0`,
`P_(m+1)(q)=P_m(q)+10q`, and `F_(m+1)(q)=F_m(q)+11q`.
The all-dirty endpoint makes each invocation legal after the previous one.
This recurrence fixes each block boundary and forbids cross-block resynthesis;
it is not a lower bound when those boundaries or children may be removed.

These are complete local scalar bills, **not** a recursive supplier tariff.
A physical integration must provide child implementations, observations,
native frame alignment, storage ownership, movement, precision and a full
caller invoice. None of those unknown costs is set to zero for the selected
multiplier. The result removes the rank-one limitation of a toy boundary;
it does not discharge a selected framework assumption. **No new kappa.**

## Finite corroboration and search scope

All words with zero, one or two adapters are enumerated, including entry,
repetitions and multiple ordered gates in one gap: counts are 1, 30 and 540.
Nondecreasing gap choices and every ordered gate tuple cover every shorter
schedule exactly once. Coefficient and separately written literal Boolean
engines agree on every boundary of every word for all 16 dirty inputs.
There are 9,136 executions and 18,272 observation-contract checks, plus 48
positive-word executions. This finite replay corroborates the written proof;
it is not a formal proof of the full multiplication theorem.

Discovery used CPython 3.12 `random.Random(57).shuffle` on the lexicographic
list of all 8^4 child chains, filtered for rank-two eager update. It completed
the first three qualifying chains and stopped at the first strict saving
through two adapters with only one hidden output at one cut. RESULT.json
records the exact inspected count and the first witness. This is not a census
of four-call chains, nor a claim of maximum possible saving in that domain.
