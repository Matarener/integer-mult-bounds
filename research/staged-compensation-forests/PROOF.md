# A same-matrix forest and restored helper-basis replacement for C01

This is a finite exact compensation construction for the two PR3605 providers
at `3efbb5de06a49ffeea6684482f2d3fe48cdca3fb`. It replaces only their
`compensation` fields. The original 5,736 additions cost 31,214 cleared-work
primitives per real component. A signed target forest costs 13,716, the exact
minimum in the specified target-only forest class. Adding 88 disjoint signed
helper changes produces 2,288 additions at cost **10,633 per real component**.
This strictly improves the preserved C01 rank-basis proposal on this same
matrix, whose 3,214 additions cost 17,334. No recursive cost or kappa changes.

The forest and two-sided mechanisms are established prior methods. The result
here is their exact source-specific application, complete same-matrix price,
literal restored word, and independently reviewable source bindings. Published
prices for different CK, X4 and U8 matrices are not comparators for this C.

## Exact source and arbitrary-input contract

The original compressed blobs are
`research/staged-644-660-width-reduction/STAGED644-660-{base,extra}.json.gz` at
the PR3605 head above. Their SHA256 values are respectively
`735c540b1fe29d0ceeb4d2f304ec941e5f2bd3bc92bafc8cce2b4f9a67a3b653` and
`886338fc32da14f3389a82c8120a1bcf9c5e2f0ec3e9b2d377fdae809e1d977f`.
Their exact compensation matrices agree. Each has 112 target rows, 207
nonzero helper columns, and coefficients in one eighth of the integers.

Let y be the actual target registers 112 through 223. Let h be the 207 active
helper coordinates, in their actual raw register identities. Both y and h are
arbitrary and independent on entrance. All remaining live coordinates are
arbitrary spectators. The required local map is

    (y,h) -> (y+C h,h).

The full source word has 632 arbitrary live inputs and 91 private cleanup
buffers with the inherited zero entrance/exit contract. The compensation
replacement never touches a private cleanup buffer. It uses no new helper,
copy, source query, native warp or recursive child. No helper starts clean by
assumption.

Every active helper is absent from both `start_extra` and `helper_final`.
This is not inferred just from the old compensation's reads. At the source pin,
`bw_transport.py` lines 158-167 give ordinary helpers default start frame zero
and final frame FULL, overridden precisely by those two dictionaries. Lines
339-348 enforce zero frame for compensation. `bw_emit.py` lines 72-83 execute
compensation before entry adapters and identify wrapped helpers using nonzero
entrance or nonFULL terminal frames. Consequently all chosen helper shears
operate on available, unwrapped frame-zero coordinates. Targets also have
zero entrance at this interface. The 207 helper identities and every selected
pair are recorded in `artifacts/DESIGN.json`.

These source-code conditions establish the local frame premise. This work does
not claim that a fresh complete native emitter/phase run has been performed.
Native admission remains a dependent obligation. The separate whole-word
reviewer supplies a companion scalar, primitive-price and numerical audit;
its source bindings and exact covered domains must accompany any integrated claim.

## Signed target forest and its exact class minimum

For a rooted signed target forest, each nonroot t has one parent p(t) and
sign s_t in {-1,1}. Define

    (T y)_t = y_t - s_t y_p(t),

with unchanged roots. Prepare these unit shears deepest-first, preserving the
original parent row until every child has read it. Restore by reversing the
preparation list and negating each coefficient. The resulting matrix T is
unit triangular in a depth ordering and invertible over the dyadic rationals.
At the prepared cut the correct residual is D=T C, with rows
`D_t=C_t-s_t C_p(t)`. These are immutable original rows of C, not a sequentially
updated parent row. Omitting preparation or reversing its chronological order
is rejected by actual arbitrary-input operator checks.

For a reduced nonzero coefficient q=a/2^d, define

    p(q)=3+floor(log2(abs(a)))+popcount(abs(a))+d; p(0)=0.

This counts one initial work clear, binary Horner source accumulations and
doublings, d halvings, one signed target accumulation and one final clear.
The coefficient work may enter arbitrarily and is erased by the two charged
clears. Real and imaginary components execute the same real-coefficient word
and are charged separately. A unit shear has component cost four, hence a
prepared/restored forest edge costs eight.

Put `P(r)=sum_j p(r_j)`. Add one superroot *. The graph has a root edge
`(*,t)` of price P(C_t) and two signed edges between every unordered pair t,u,
with price `8+P(C_t-s C_u)`. The sign-symmetric tariff makes the latter prices
independent of the edge's eventual orientation, since
`C_u-s C_t=-s(C_t-s C_u)`.

Every target forest extends to a spanning tree by joining its roots to *.
Conversely, deleting * from a spanning tree gives components each with exactly
one former neighbor of *, providing their roots. This is a bijection preserving
the complete residual-plus-two-adapter cost. Thus a minimum spanning tree
solves exactly the single-parent signed-unit target-forest problem.

The complete graph has `112+2*binom(112,2)=12,544` edges. The deterministic
Kruskal construction orders by price, then actual endpoint identities and sign.
It attains 17 roots and 95 forest edges, with maximum target edge depth 15.
All 12,544 cycle inequalities are checked: each graph edge costs at least the
largest selected edge on its unique tree path. This is a certificate of the
spanning-tree minimum by the usual cycle-exchange argument. A separate Prim
traversal of the complete priced graph yields the identical 13,716 price. That
Prim traversal shares the complete edge price list; it is an algorithmic
cross-check, not a second arithmetic implementation.

The claimed optimum is only for these signed-unit single-parent target forests
with independent coefficient lowering. It excludes multiple parents, general
dyadic target shears, helper transformations, shared coefficient work,
alternative lowerings and surrounding-boundary folding. In particular it is
not a lower bound for the subsequent two-sided construction.

## Disjoint helper construction on the transformed matrix

For each chosen ordered pair (a,b) with sign s, prepare `h_a += s h_b`. Every
helper occurs in at most one of the 88 selected pairs. Therefore their unit
shears commute, square-zero cross-terms vanish, and their product H has inverse
obtained by negating the signs. The correction matrix must be

    E = T C H^-1.

For one pair its only changed column is `E_b=D_b-s D_a`. All pair prices are
computed from D=T C, rather than the original C. The complete signed pair
saving is

    sum_t [p(D_tb)-p(D_tb-s D_ta)] - 8.

There are exactly `207*206*2=85,284` ordered/sign candidates; 951 have positive
complete savings. Sort by decreasing saving, then actual (a,b,s). One greedy
pass accepts a candidate exactly when neither helper has been used. This
selects 88 disjoint pairs with total saving 3,083 per real component. Disjointness
makes the savings additive because each chosen pair changes a distinct column
and no pair changes another pair's donor column.

This is a fully specified construction, not a maximum-weight matching claim,
not a joint target/helper optimum, and not an alternating search. No wider
search was performed after finding this useful bounded candidate.

The complete chronological word is

    y <- T y
    h <- H h
    y <- y + E h
    h <- H^-1 h
    y <- T^-1 y.

For arbitrary y and h it returns
`T^-1(T y+T C H^-1 H h)=y+C h`, with h literally restored. Thus the original
panel and replacement are equal before any surrounding noncommuting native
operator is composed. Every other field of both complete source words remains
identical as a JSON value. No commutation of surrounding warp letters is used.

The literal inverse reverses every gate and negates every ADD coefficient,
therefore implements `(y,h)->(y-C h,h)`. For a logical ADD gate
`A=I+q e_t e_s^T`, its inverse transpose is `A^-T=I-q e_s e_t^T`.
Apply these dual gates in the same chronological order. This yields the panel
`(y,h)->(y,h-C^T y)`. The helpers change at that dual panel boundary; their
whole-program endpoint obligation cannot be inferred from the forward panel's
unchanged-helper statement. Logical gates are dualized before primitive
lowering. Destructive work clears are not asserted to be invertible.

## Complete same-matrix price

| Compensation | Target basis ADDs, both ways | Helper basis ADDs, both ways | Residual ADDs | Total ADDs | Primitives per real component |
| --- | ---: | ---: | ---: | ---: | ---: |
| Original C | 0 | 0 | 5736 | 5736 | 31214 |
| Preserved rank basis | 112 | 0 | 3102 | 3214 | 17334 |
| Signed target forest | 190 | 0 | 2644 | 2834 | 13716 |
| Forest plus disjoint helpers | 190 | 176 | 1922 | 2288 | 10633 |

The new residual costs 9,169 per component, the target preparation/restoration
760, and the helper preparation/restoration 704, totaling 10,633. Thus the
complete finite compensation saving is 3,448 logical ADDs and
`2*(31214-10633)=41,162` real primitives. It saves 13,402 real primitives over
the preserved rank basis and 6,166 beyond the same-C target-forest floor.
The logical ADD count and coefficient-dependent primitive bill are different
quantities; the latter includes every basis gate and every coefficient read.

`price_replay.py` independently emits and executes the actual binary-Horner
microcircuit for all 21 coefficients used across the four panels. It checks
arbitrary source, target and private-work inputs and the required zero work
output. It obtains all four prices by summing literal primitive-list lengths,
without invoking the designer's tariff function. Its receipt is `artifacts/PRICES.json`.
The historical rank-basis panel's decompressed SHA256 is
`9f242abd5d2ed46a2e95dad46449d1d77c6fec330b5e0db6b324ac93fe756e62`.

The inherited recursive histogram remains
`{1:2439,2:726,3:224,4:102,5:20,8:8}` and helper-width inventory remains
`{4:26,5:2,6:18,7:52,8:97,9:213}`. The replacement adds no recursive child,
non-scalar event or helper role. This finite scalar change does not improve
the recursive moment.

## Comparison with the broader PR1080 method

PR1080 at `803e080e181229a3af2196b7a13615c9d81ae10d` already supplies signed
helper forests and alternating two-sided MST refinement for historical U8.
Its baseline is a different 112-by-216 matrix with 6,320 nonzeros, quarter-grid
coefficients and cost 34,728. The exact canonical source was extracted from its
pinned archive and checked against decompressed SHA256
`24db880b7dab31e6af4eec8a1aba1bbbae29cd50d9a7b77cf0e9b571b3e5ae7c`.
The present matrix has 207 active columns and genuine eighth-grid coefficients,
so signed row/column permutations cannot identify the two matrices.

One fixed recipe-transfer check was performed, without an optimization search.
Its final frozen target forest, applied to the current C, costs **22,548** per
component. A literal register-ID transfer of the helper forest touches four
currently removed helpers (494,495,507,519), 14 helpers with nonzero entrances,
and 16 with nonFULL terminals. It is therefore not an admitted free-wrapper
substitution under the current source contract. The full offending sets and
actual eighth-grid witnesses are in `artifacts/PR1080-COMPARISON.json`. Historical
canonical numbering is not a supplied physical-role correspondence to the
current raw register identities: a paid remapping or other correspondence
would be a new obligation. No general change-of-basis equivalence obstruction
is claimed. The prior 7,930 U8 price is not a bound or candidate price for C01.

This comparison credits the stronger preexisting mechanism rather than claiming
novelty for two-sided factorization. Applying its broader alternating class to
this new C remains outside the present bounded construction.

## Executed exact domain and unresolved obligations

`construct.py` checks original versus each candidate on every one of the 632 live
input columns, under forward, literal inverse and inverse-transpose operators,
in both source providers. All complete words preserve non-compensation JSON
fields. Nine actual operator mutations each fail in all three orientations:
omitted target preparation/restoration; wrong target preparation order;
omitted helper preparation/restoration; helper-preparation sign; residual sign;
target-restoration sign; and stale original-C injection. Each rejection has a
specific differing row/column coefficient. The omitted-target-preparation
control also passes the 520-column projection omitting arbitrary target inputs,
showing why that incomplete projection would be insufficient.

The design and price checks concern exact rational scalar maps. Complete
supplier numerical prefixes are handled by the separately bound companion
audit. Rounded precision, source/tape access and finite native-phase admission
remain separate dependent obligations. Component
endpoint equality and fewer operations alone prove no bound on intermediate
magnitude or denominator growth. Neither the historical 192-bit allowance nor
an old whole-word prefix receipt is transferred automatically. This note does
not claim an all-size compiler, physical supplier, new owner allocation,
analytic transfer, full multiplication theorem, selected-frontier change, or
formal-kernel proof.

## Sources and credit

The actual source is dcharb78's PR3133 lineage and Ross Richardson's PR3605;
the preserved C01 rank-basis proposal is only the same-matrix comparator.
Credit Oscar Fennell PR759 for the forest/superroot method, Sricharan Vagvala
PR749 for rational target pairs and PR967 for bit helper stars, @dd-hemant PR816
for signed rational forests, David Awad PR807 for helper-basis factoring, Ross
Richardson PR917 and PR932 for exact two-sided and X4 forest applications, and
Stephan Arrington (@steph4n-gh), with the disclosed Google DeepMind Antigravity
assistance, in PR1080 for arbitrary-depth helper forests and alternating refinement.
PR961's target-only dyadic forest analysis concerns its own historical input.
The inherited Gauge44, native, cold-helper, source-recovery, compiler and
precision attributions remain those of the pinned source packages. No code or
numeric saving from a different matrix is treated as interchangeable evidence.

Prepared with substantial OpenAI Codex assistance. Separate AI mathematical
review is not independent human review. New material is Apache-2.0 under the
repository license. Exact source and output hashes accompany this proof.

## Open next questions

A fresh native compilation is needed for an integrated native supplier claim.
The separate whole-supplier scalar/numerical replay must be bound to these
exact replacement bytes. A larger signed helper-forest or
nonunit alphabet could further improve this matrix, but its paid restoration,
precision and source contracts must be recomputed. The present result provides
one useful fully restored candidate without claiming those broader optima.
