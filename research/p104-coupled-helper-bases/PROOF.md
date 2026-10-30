# Coupled helper bases and productive handoffs

## Statement and source

This construction changes the complete P104 invoice. The conditional claim
is kappa = 0.00309980, tested at 0.0030998005. The predecessor claim is
0.00308189 in [PR #5580](https://github.com/CrocSwap/integer-mult-bounds/pull/5580).
Its exact source commit is `6efa248cf456d6101d757e9d09ba29711d18a13a`.
[SOURCES.json](SOURCES.json) binds the source bytes. The selected record
stays at 0.003027288235.

Six helper boundary basis changes remove seven paid transports per local
call. Nine coupled handoffs add nine independent helper inputs without
adding a paid transport. The 104 main shears, their literal native ports,
the caller and all eight owned paths remain fixed. Each new helper is an
arbitrary independent input. None is initialized as zero.

This result uses the five inherited framework assumptions: native
all-column realization, owned erasure, uniform compiler closure, precision
and fixed-tape execution, and analytic recovery. It also uses the inherited
free helper endpoint contract. It is an author-checked conditional bound,
not independent scientific acceptance or a change to the selected frontier.

## Chart convention

A field at frame F represents an abstract row in the chart C_F. A MOVE
changes its native chart and preserves its abstract row. An ADD or SCALE
acts on abstract rows only when all operands share the declared chart.
Scalar coefficients are dyadic. SCALE coefficients are dyadic units.

The source word has main endpoint matrix M and identity helper endpoints.
M is the direct sum of 104 invertible shears and the helper identity.
Every construction step preserves this form, with one more identity factor
for each new input. The exact endpoint replay tests arbitrary inputs, not
just inputs with zero helper values.

## Boundary basis change

Choose a helper h after its last source read. At a cut in frame F, suppose
free additions from fields at F change its row to

```text
c h + sum(a_j h_j),  j != h.
```

The inputs h and h_j are helpers at one common input frame S, and c is a
dyadic unit. Prepend `h += -(a_j/c) h_j` at S. At the cut, do the stated
cancellation and scale h by 1/c. The row is now exactly h. Delete all
later instructions with destination h and retire it at F. There is no
later source read of h. The final helper map on every input remains the
identity, so the added input basis change does not change other outputs.
The full endpoint check independently confirms this conclusion.

The same construction can be applied to the transpose of the logical
word. Reverse the order, transpose ADD, interchange INIT and CLEAR, and
reverse each MOVE. A COPY into a zero owned field can be written as ADD
before this transpose. Transpose the changed word back. This changes a
helper's initial boundary. It does not add an inverse local call to the
physical caller. Every final public MOVE is ascending, every owned MOVE
is descending, and the final native replay checks all maps and phases.

The six fixed changes are:

| Helper | Orientation used to construct the change | Cut frame |
| --- | --- | --- |
| 652 | Transpose | 120 |
| 341 | Forward | 240 |
| 596 | Transpose | 1053 |
| 668 | Transpose | 1051 |
| 684 | Transpose | 1049 |
| 649 | Transpose | 597 |

[WITNESS.json](WITNESS.json) gives the exact event cuts, cancellation rows
and helper boundary relations. Cuts refer to the current word at each
step. The constructor derives these relations again from the prefix.
It checks frame availability, helper support and the last-read condition.

## Coupled handoff lemma

Take a cut with no live owned field. Let A be its public prefix matrix and
B its suffix matrix. Then B A = M. Both square matrices are invertible.
Let G be a set of helpers with the same initial frame S and final frame T.
Choose a common cut frame F with S strictly contained in F and F strictly
contained in T.

Choose a row v and a column u supported on public fields at F. Require

```text
v u = 1,       a = v A,       b = B u,
support(a), support(b) contained in G,       a b = 1.
```

Pick a helper field p in G that is at F. Construct scalar matrices R on
G and J on the fields at F such that

```text
a R = e_p^T,   R e_p = b,
v J = e_p^T,   J e_p = u.
```

The supplied witnesses have dyadic unit pivots. `basis` emits ADD and SCALE
operations for each matrix and checks the exact pairing. The inverse is
the reversed instruction list with negated ADD coefficients and inverse
SCALE coefficients. All operations at each boundary share one chart.

Because b has only helper support, M b = b. The equations B A b = b and
B u = b imply A b = u. Thus the transformed prefix J^-1 A R has first
row e_p^T and first column e_p. It is a direct sum of the scalar 1 on p
and a map on the remaining fields. The transformed complete map is
R^-1 M R = M, since R acts only on helper coordinates. Consequently the
transformed suffix R^-1 B J also has the isolated identity factor on p.

Execute R at the input, the original prefix, and J^-1 at the cut. Retire
p at F. Supply a new independent public input n at F. Use n in place of
p in J, the suffix and R^-1 at the output. The retired output is the old
input p. The new output is the new input n. Every other helper and main
output is unchanged. This proves the arbitrary-input identity and the
independence of both productive targets.

The scalar basis matrices act on whole fields, with coefficients outside
the tensor power. At every positive tensor width, common-chart scalar
operations and the exact native chart identities give the same abstract
row identity. The finite native recipe checks include the tensor rule;
no tensor power of a scalar coefficient is substituted for that coefficient.

The old target rank dim(T)-dim(S) becomes two positive target ranks
dim(F)-dim(S) and dim(T)-dim(F). No MOVE is inserted. R and its inverse
use only helpers with one common boundary chart. J may mix main and
helper fields at the cut; its inverse and the isolated-channel argument
restore the exact main contract. There is no owned COPY at any cut.

The nine cuts are:

| Retired field | Frame F | New target ranks |
| --- | --- | --- |
| 61 | 306 | 4, 5 |
| 432 | 516 | 4, 5 |
| 572 | 603 | 2, 7 |
| 345 | 391 | 2, 7 |
| 14 | 462 | 2, 7 |
| 3 | 424 | 2, 7 |
| 76 | 252 | 2, 7 |
| 224 | 267 | 8, 1 |
| 400 | 477 | 8, 1 |

Fields 3, 14, 61 and 76 are helpers in this source word. The source removed
their original ports. They are not among the 104 retained main ports.

The checker recomputes v A and B u from the complete prefix and suffix,
checks their helper support, checks every cut chart, and replays the full
word after each step. It also checks the final transpose with dense integer
rows and binary denominators, separately from the sparse Fraction replay.

## Exact gain and complete bill

Write H_r for one rank-r job and let g(a,b) denote
a^(1-kappa) + b^(1-kappa) - (a+b)^(1-kappa). This is strictly positive
for a,b > 0 and 0 < kappa < 1.

The local paid change from PR5580 is `-2 H1 - H4 - 4 H5`.
The local target change is

```text
2 H1 + 5 H2 + 7 H4 + 2 H5 + 5 H7 + 3 H8 - 15 H9.
```

Thus the increase in the complete target-minus-paid moment is

```text
18 * [7 g(4,5) + 5 g(2,7) + 3 g(1,8) + g(1,4)] > 0.
```

The rank masses of both local profiles fall by 26. Their difference is
unchanged. This exact identity also distinguishes the construction from
more digits of the same root.

| Quantity | PR5580 | This construction |
| --- | ---: | ---: |
| Local public inputs | 735 | 744 |
| Local helper targets | 527 | 536 |
| Local paid jobs | 3454 | 3447 |
| Local paid rank mass | 6013 | 5987 |
| Local events | 25140 | 25472 |
| Complete productive fields | 12814 | 12976 |
| Complete paid jobs | 66852 | 66726 |
| Complete target rank mass | 242010 | 241542 |
| Complete paid rank mass | 241250 | 240782 |
| Rank-mass surplus | 760 | 760 |

The complete caller has 18 forward local calls, 15 rank-one query shears
per port, and 3120 whole idle jobs. Maximum paid rank is 72 and maximum
target rank is 145. The physical event invoice is checked against the two
controller path lengths and a third count in the verifier.

All eight owned paths remain. They use one field at a time and have total
local paid rank 56. The new public inputs are charged as productive fields,
including both native normalizers for each helper. The native checker
also covers every paid map and all 208 main adapters, with exact signed
Pauli images and absolute phases. The physical caller checks its contacts,
routes, central squares, target phases and whole idle phases.

The local real scalar allowance is 220332. The route allowance is 5175000.
Their sum is below 10000000. The full nonrecursive bound is 184647552,
below 1000000000. This includes local scalar work and routes, the owned
operations, thin queries, caller boundaries and the retained layout terms.
The scalar growth bound remains 2^(16*26000). The actual local native
rank sum 5987 is used in the tensor growth bound.

## Comparison with the released parallel split component

[PR #5599](https://github.com/CrocSwap/integer-mult-bounds/pull/5599), head
`0644592d421b375c221045954fdf13932575ffa8`, independently uses the same
input/cut/output basis mechanism. Its author released the 15-split component
for composition. The present package credits that work and makes no claim
of exclusive method discovery. The six paid-boundary changes remain a
separate construction component.

The parallel word has 750 public inputs, 542 local helper targets, 66852
complete paid calls and 13084 complete productive fields. Its exact raw
crossing is (0.00309839352211, 0.00309839352212). Its local targets are
`{1:4, 2:5, 4:90, 5:10, 7:5, 8:18, 9:410}` and its paid profile is the
PR5580 profile. Relative to that word, this construction has local changes

```text
targets: -2 H1 - 3 H5 - H9
paid:    -2 H1 - H4 - 4 H5.
```

The complete signed-moment gain is therefore exactly `18 * g(4,5) > 0`.
The raw gain lies in (0.00000140768321, 0.00000140768323). The claimed
endpoint increases by 0.00000141. It also removes 108 productive fields
and 126 paid calls from the complete bill. The comparison checker binds
that exact word, replays its arbitrary inputs, recounts its full invoice
and isolates its crossing. It does not repeat that package's native and
compiler checks or count them as independent review.

The nine handoffs here and the 15 parallel splits are not additive gains.
This package retains its fully verified smaller construction. Any different
combined word still needs its own full replay and compiler bounds.

## Compiler and outer transfer

Two exact rational moment engines check the endpoint. The complete
compiler retains power 1024, cutoff 17, floor 18, tail offset 1/5,
reserve 1e-10 and tail decay 0.97. The logarithm power increases from
1000 to 1024. The old logarithm power fails the complement-capacity test
at the new endpoint; the checker records this negative control.

The checker verifies all three tail ratios, completion, splitting,
rounding, shifted exits, complement capacity, the initial range and the
finite integer threshold. It rejects the preceding integer threshold.
The ordinary BIT contract remains 0.0034. All 54 strict and four
functional outer predicates must be positive. The old cutoff, insufficient
BIT contract and old complete invoice also fail their control tests.

The raw crossing lies in (0.00309980120533, 0.00309980120534). Its increase
over the parent crossing lies in (0.00001790623666, 0.00001790623668).
The headroom above the claimed endpoint is between 1.20533e-9 and
1.20534e-9. The finite threshold is N = 2^707182000000000, with integer
test exponent 50513 and gap 1/14000000000.

The exact interval bounds are in [RESULT.json](RESULT.json). A rational derivative bound proves a
unique crossing on [0,0.0034]. That interval is the funding ceiling only
for this fixed invoice under the retained BIT cap. No optimum for other
words, helper bases, controllers or suppliers is claimed.

The enormous uniform word and a complete rounded multiplier are not
materialized. The replay and algebraic lemmas do not discharge the inherited
framework assumptions. Independent scientific review remains required.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
The retained sources preserve their original notices and predecessor credit.
