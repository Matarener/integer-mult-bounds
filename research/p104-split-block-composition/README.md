# Exact block-chart optimum and PR5756 audit

This package proves a fixed-block optimum for **all 8,283,458 canonical
subspaces of F2^9**. It also independently reproduces the complete word and
conditional saving **κ = .00311313795** published in PR5756. The composition
and saving belong to PR5756. This package adds the optimization theorem and
source-bound audit. It does not change the selected frontier.

The rank-four chart is the unique optimum for every `0 < C <= .01`, and in
fact up to a formal tariff switch near `.124775`. At the published κ, a change
to even one of the 18 independent local block charts exceeds the complete
caller's margin. Thus a larger gain needs a different scalar assignment,
several intermediate charts, or a changed helper contract. More precision in
the same root is not a new result.

## Exact source audit

PR5756 is frozen at `a1b338e5d9271b541f2a198f4fc19cefc565feed`.
The independently constructed word equals its word after removal of only the
schema label. The local, native, physical and complete-price receipts agree.
The correct complete count is **13390 productive fields and 66852 paid calls**.
The 12958 fields in the PR body at audit time are stale prose; its JSON agrees
with 13390.

The immediate source is PR5751 at
`8483f9a679d06c1e270141dbc686a7e76e7a7522`. It supplies all 23 paid meeting
splits and retains flyingviper's PR5718. The exact eight block edits are from
Joel Pulikkan / GamingPuzzled's PR5739 at
`b93d749a0a895d260e87887170af5162bda461a4`. Each source run occurs once in the
PR5751 word, and chart 1090 is free. `construct.py` checks these facts before
it applies the edits. It also reproduces PR5739 on that source's PR5713 word.
The older seventeen-split checkpoint remains frozen as provenance and is
not imported by the final verifier. No helper-split discovery is claimed.

The final word has 767 public inputs, nine owned labels, eleven owned
lifetimes, peak owned storage two and scalar allowance 224138. Its local
profiles are:

| Kind | Exact profile |
| --- | --- |
| Paid | 2220 H1 + 454 H2 + 492 H3 + 93 H4 + 174 H5 + 6 H6 + 15 H7 |
| Helpers | 24 H1 + 5 H2 + 92 H4 + 7 H5 + 6 H7 + 37 H8 + 388 H9 |

The complete caller has 18 local calls, 15 query shears, 3120 whole idle jobs
and rank-mass surplus 760. Its raw crossing is strictly inside
`(.00311313797336, .00311313797337)`. The published value leaves between
2.336e-11 and 2.337e-11 below that ceiling. The retained compiler and outer
checks pass under the same five inherited framework assumptions.

## Native rank formula

Let W be a binary subspace of dimension r in V = F2^9. The source canonical
Gaussian chart has the Pauli image space

```
L(W) = {(x,z): x in W and z+x in W_perp}.
```

Here is a derivation from the source chart. Extend the basis of W to an
invertible matrix G. Let E select its first r columns, and put
`Q = I + G^-T G^-1`. The source chart is `K F_r K^-1`, where
`K = D_Q P_G`. Its image of a Z vector satisfies
`x = G E G^T z` and `z_out+x = G^-T (I+E) G^T z`. These vectors lie in W
and its orthogonal complement. The image has dimension nine, so this gives
the entire stated space. The source F_r is its Gaussian rotation; the proof
uses its actual Pauli action.

For any A and B, the intersection of these image spaces has dimension
`dim(A intersect B) + 9 - dim(A+B)`. Therefore the native rank is

```
d(A,B) = dim A + dim B - 2 dim(A intersect B).
```

`optimal_tariff.py` checks the formula against the actual native engine on
134 source-derived representatives and all 2412 boundary ranks. This is a
check of the general algebraic proof, not an enumeration of every subspace.
Phases do not change ranks. The selected complete word receives a separate
full phase replay.

## The 67 nested charts

Keep the scalar assignment, all other charts and both changed helper endpoints
fixed. The eight incoming spaces U_i have dimension three. Their sum L has
dimension four. The outgoing spaces are seven copies of V and one space U
of dimension eight, with `L <= U <= V`. The original nested contract is
`L <= F <= U`. Its 67 choices have rank counts 1, 15, 35, 15 and 1.
The changed helpers run from zero to F and from F to V. For d = dim F,

```
P_d = 8 H_(d-3) + 7 H_(9-d) + H_(8-d)
T_d = H_d + H_(9-d)
S_d = T_d - P_d,   H_r = r^(1-C),   H_0 = 0.
```

An identity boundary is omitted and has zero recursive cost. All scalar
operations assigned to F use the same chart. `native_interval.py` checks all
1206 native boundary ranks and rejects a rank-three nested relaxation.

The paid profile at rank four strictly majorizes the profiles at ranks five,
six and seven. Their target profiles majorize the rank-four target profile.
`TARIFF.json` gives every integer balancing transfer. Concavity proves that
rank four strictly wins over these three ranks for `0 < C < 1`.
The remaining difference is

```
S_4 - S_8 = 2*5^(1-C) - 8^(1-C) - 2.
```

Its derivative divided by `5^(1-C)` strictly decreases. Exact endpoint signs
prove one maximum and one interior zero. The zero lies in
`(.14739606083204, .14739606083205)`. Below it rank four wins; above it rank
eight wins. At zero all 67 charts tie by rank mass. At the switch only the two
endpoint charts tie. At C = 1 the rank-eight chart wins.

The complete caller's five raw crossing intervals are:

| Rank | Number of charts | Raw crossing interval |
| --- | --- | --- |
| 4 | 1 | (.00311313797336, .00311313797337) |
| 5 | 15 | (.00311114702998, .00311114702999) |
| 6 | 35 | (.00311049778387, .00311049778388) |
| 7 | 15 | (.00311102091727, .00311102091728) |
| 8 | 1 | (.00311301604454, .00311301604455) |

Exact interval arithmetic also proves a negative whole-invoice derivative
on `[0,.0034]`. Each stated raw crossing is unique in that interval.

## All canonical charts

Now permit any single canonical subspace F of V. Charge every incoming,
outgoing and helper rank, even for a nonnested transition. This is a broader,
optimistic recursive tariff model. It does not supply physical admission for
every such choice.

For f = dim F <= 8, choose an f-dimensional F' inside U such that
`F' intersect L` contains `F intersect L` and has dimension `min(f,4)`.
This is possible by basis extension inside L and then U. It cannot increase
any incoming rank or the outgoing rank to U. It leaves both helper ranks and
all seven outgoing ranks to V unchanged. If f >= 4, it reduces the problem
to the 67 nested charts. If f <= 3, it reduces the problem to F' inside L.

All 67 subspaces of L are enumerated. For ranks 0, 1, 2 and 3, the largest
numbers h of incoming spaces that contain F' are respectively 8, 4, 2 and 1.
Every other incoming intersection has dimension f-1. Thus the best profiles
at these four ranks are

```
P_f = h H_(3-f) + (8-h) H_(5-f) + 7 H_(9-f) + H_(8-f)
T_f = H_f + H_(9-f).
```

Rank nine has one chart, V, with `P_9 = 8 H_6 + H_1` and `T_9 = H_9`.
Explicit positive decompositions in TARIFF.json prove `S_9 > S_f` for every
f from zero to three and every `0 <= C <= 1`. They use monotonicity and
`3 H_2 >= H_6`, which follows from concavity. Only ranks four, eight and
nine remain.

Write t = 1-C. The remaining two differences are

```
S_9 - S_4 = 9^t - 8*6^t + 6*5^t + 7
S_9 - S_8 = 9^t - 8^t - 8*6^t + 8*5^t + 5.
```

Both strictly increase with C. Divide their t derivatives by `6^t` and bound
the positive convex exponential sums by their endpoint maxima. For the
second difference, also use `(4/3)^t log(8) >= log(8)`. The four strict
rational log bounds are in TARIFF.json. Both differences start at -2 and end
positive, so each has one zero. Their zero intervals are
`(.12413664498287,.12413664498288)` for rank nine versus eight and
`(.12477498342317,.12477498342318)` for rank nine versus four. Both precede
the nested switch. Rank eight therefore never wins the global envelope.

Let C_g be the unique root in the stated rank-nine versus rank-four interval.
The complete global classification is:

- At C = 0, the 67 nested charts tie and all other charts lose.
- For `0 < C < C_g`, the unique optimum is L, of rank four.
- At C = C_g, L and V tie.
- Above that switch through C = 1, the unique optimum is V, of rank nine.

The switch is a block tariff threshold, not a multiplication exponent.
The Gaussian binomial count gives 8,283,458 subspaces. The proof covers all
of them by the reduction; it does not claim that all were enumerated.

## Complete-caller consequence

At κ = .00311313795, the full raw margin is less than .000005666. Every
alternative best-rank chart has a per-local loss greater than .0016427276.
A rank-four chart other than L increases at least one boundary rank by two;
its loss is at least `9^(1-κ)-7^(1-κ)`, which is also greater than the full
margin. The lower-rank charts are dominated by rank nine. Therefore a change
to any one local chart already makes the raw margin negative. Additivity
extends this conclusion to every mixture of independent chart choices across
the 18 copies. Shared queries, changed helper fields and cross-call corrections
are outside this fixed contract.

## Verification and limits

Run `python3.12 -B scripts/research_package.py --package
research/p104-split-block-composition` from the repository root. VERIFY.json
registers normal and optimized runs of the primary verifier, native interval
check and global optimizer. VALIDATION.md records the exact runs and export
checks. The primary replay checks all 776 arbitrary scalar inputs, separate
transpose audits, owned lifetimes, 2927 distinct native maps with phases,
the complete physical caller, both moment engines, compiler, 54 strict and
four functional outer checks. Source authentication has actual byte-corruption
controls. Retained archives and notices are unchanged.

The result does not cover arbitrary Clifford coframes, different scalar
assignments, multiple intermediate charts, shared helper inputs, changed
chronology or unpriced corrections. Five inherited all-size assumptions,
independent scientific review and hosted CI remain separate obligations.
The optional full-history ancestry preflight was not run in this shallow
checkout. No selected-frontier change, merge or closure is performed.

## Open next questions

1. Can a different scalar allocation or several intermediate charts improve
   the complete signed invoice? Name the changed boundary contract first.
2. Can shared queries or a changed helper contract beat the independent-copy
   bound? Charge the added native maps, restoration and owned operations.
3. Does an independent reviewer accept the source word, the chart reduction
   and the inherited all-size assumptions?

Ali Romman with substantial OpenAI Codex assistance. No subagents. Apache-2.0.
All predecessor credit is retained in NOTICE and frozen source archives.
