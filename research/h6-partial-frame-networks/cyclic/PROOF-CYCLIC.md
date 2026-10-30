# Cyclic mixed readers on fixed H6 subfamilies

This package replays exact common-frame words for actual H6 subfamilies with
`r=2,...,7`, compares two reader schedules, and reconstructs 4,800 disjoint
six-port modules on the 28,800 root-product ports. The positive result is a
logical arbitrary-input circuit with checked binary frame incidences. It
does not provide the missing physical phase/adapter compiler, a rounded
supplier, a physical ownership schedule, or a new multiplication bound.

The source geometry/factorization is credited to Dominik Scholz / PR606;
the alternate H6/Walsh proposal to DreamingOfClouds / Discussion1167; and
the complete compensation/encoder audit to PR1830 and its predecessor
lineage. The retained local constructions are `mixed_rectangle.py`,
`cyclic_mixed.py`, `dynamic_cyclic.py`, and `module_tiling.py` from the
historical complex-alternative investigation. All are preserved byte for
byte in `frozen/`. Substantial OpenAI Codex assistance; Apache-2.0 ancestry.
The scientific Git pin is `20ecf2891d80b5acf18d980b2164fb44ea7faa90`.
`ORIGINS.json` records every original and dependency byte hash.

## Exact input and frame contract

Scalars lie in `Z[1/2]`, acting on arbitrary complex vectors. Every ordinary
source x, target y, K centre c, and compensation reader h is arbitrary and
independent; correlated inputs are consequently allowed. Private streams
alone have the separately stipulated cleared-work interface.

The address space is the actual 17-bit binary space. A frame is represented
by a canonical binary row basis. A CLIMB must move from a contained
subspace to a containing subspace. ADDs require exactly the same current
basis on source and destination. Sources begin at their actual rank-one
address lines; y, c, and h begin at ZERO. Sources, c, and h finish at FULL;
y finishes at the rank-sixteen cap perpendicular to its address.

The replay tracks logical coefficients relative to those declared frames.
Thus restored c and h mean their initial logical values at the specified
final FULL frames. They do **not** mean raw physical return to the initial
ZERO-frame representatives. Historical statements using “literal
restoration” must be read with this correction. No choice of actual
Clifford representatives, no global phase identification, and no free
physical adapter is proved by a binary subspace inclusion.

The new receipt preserves full ordinary-column matrices, every emitted
event, each register's rank path, and exact logical prefix norms and dyadic
denominator depths. There are `4N` independent ordinary columns in each
cyclic case, `N=2r`, and fourteen in the precursor rectangle. This is a
coefficient proof for arbitrary ordinary inputs, not testing random inputs.

## Geometry and coefficients of the cyclic family

In ordinary E8 coordinates choose `a_g=e_0-e_(g+1)`,
`beta=e_0+e_1`, and `gamma=e_0-e_1`. The two ports in group g are
`(a_g,beta)` and `(a_g,gamma)`. The programs retain doubled integer
coordinates, the exact cubic kernel

```
K_ij = (t_ij^3 - 4 t_ij)/48,    C = I-K,
C = (J_r-I_r) tensor (1/16)[[-5,1],[1,-5]].
```

The exceptional Gram-three coefficient is therefore included. The
source-faithful binary fit constructs the 17-bit labels and verifies
their parity against every actual Gram entry in each fixture. For each
group let U_g be the plane spanned by its two labels. Define cyclic arcs

```
F(g,k) = U_g + ... + U_(g+k-1),       1 <= k <= r-1.
```

The exact finite geometry verifies dimension `k+1`, inclusion in both
target caps of group `g+k`, and nesting of consecutive arcs. Source
group j has nested inclusive visits `F(j-d,d+1)`, for
`d=0,...,r-2`. These are actual subspace checks on the retained labels,
not dimension-only promises. The construction covers exactly `r=2,...,7`;
an abstract use at other sizes would first need these same hypotheses.

The eigenvalues of C are `-(r-1)/4`, `1/4`, `-3(r-1)/8`, and `3/8`,
with multiplicities 1, r-1, 1, r-1, respectively. They are nonzero and
none is one. Hence both C and the restricted `K=I-C` have full rank N.
The rank test here is specific to these displayed block matrices; it is
separate from the published odd-polynomial and Smith results, which this
package neither reproduces nor claims as new.

## Complete mutable-reader word

Allocate two dirty readers per group, initially `h_g^+=d_g^+` and
`h_g^-=d_g^-`. At depth d, advance that pair to `F(g,d+1)` and advance
source group `g+d` to the same frame. Perform the four unit signed ADDs

```
h_g^+ += x_(g+d,0) + x_(g+d,1),
h_g^- += x_(g+d,0) - x_(g+d,1).
```

This executes real successive reads of original source groups. Every
source is unchanged as a logical value, and its visits are nested. After
`r-1` reads, reader g contains all sources except group `g-1` in its two
signed channels. All sources then reach FULL.

Only target pair `t=g-1` receives reader g. Its decoder is

```
y_(t,0) += -h_g^+/8 - 3h_g^-/16,
y_(t,1) += -h_g^+/8 + 3h_g^-/16.
```

Before either target leaves ZERO, subtract these same decoder coefficients
of the original reader dirt. Writing L for the accumulated input mixing
and R for this decoder gives exactly `RL=C` on every coefficient.

The intervening restricted-K word is also explicit. At ZERO precompensate
`y -= Kc`; move each ordinary c to FULL and gather `c += x`. For each
centre, create a cleared private stream, copy c, descend privately to ZERO,
scatter its actual K column, and clear the private stream. Undo the centre
gathers at FULL. All targets remain at ZERO through this step. This pays N
ordinary centres and N separate rank-seventeen private episodes; it is not
an unpriced clean-input K macro.

Each target then climbs once to the final reader arc, receives its decoder
contribution, and finishes its cap climb. Each h climbs to FULL and
subtracts exactly the original source combination it accumulated. Algebra
on all ordinary columns gives

```
(x,y,c,d) -> (x, y+(K+RL)x, c, d) = (x,y+x,c,d).
```

The static predecessor instead loads each reader from one source group
and sends that unchanged packet through the other target groups. Its
separate L and R, all target visits, and full ordinary endpoint are
replayed too. Both words include the same complete restricted-K episode.

For the scalar inverse transpose, each logical ADD `dst += q src`
becomes `src -= q dst` in the same chronological order. A private forward
episode collapses to a logical shear from c to y. Its separately defined
dual starts cleared at ZERO, gathers the weighted targets, ascends to FULL,
subtracts from c, and clears there. This proves the ordinary dual endpoint
`(x,y,c,d) -> (x-y,y,c,d)`. It does not apply inverse transpose to a
destructive CLEAR, and does not assert arbitrary entering private data.
Helpers may change at intermediate dual cuts. The same chronological
scalar dual is distinct from any unproved physical frame/phase lift.

A separate closed-block matrix product checks both ordinary endpoints
without parsing the scalar event stream. The original four-port,
two-reader precursor is also rerun, including its fourteen arbitrary input
columns, incomparable-plane control, and 300/312 component bills.

## Complete finite costs and a decision-relevant comparison

For reduced `q=a/2^d`, the inherited cleared-work Horner price is
`p(q)=3+floor(log2(abs(a)))+popcount(abs(a))+d`, with `p(0)=0`.
Signs are absorbed into signed ADD coefficients and do not change this
price. This is a scalar lowering cost convention, not a replay of its
coefficient temporary states. Real and imaginary components cost separately.

The mutable paths, per role, are:

| Role | Number | Rank increments |
| --- | ---: | --- |
| Source | N | `1` repeated r-1 times, then `17-r` |
| Target | N | `r,16-r` |
| Ordinary compensation reader | N | `2`, then `1` repeated r-2 times, then `17-r` |
| Ordinary K centre | N | `17` |
| Private K episode | N | `17` |

All ranks are paid abstract frame-transition ranks, not a fresh physical
native compiler invoice. The total is `83N`, of which `17N` is separate
private K rank. Compensation has no private episode. The complete
component scalar bills are

```
mutable: N(54r-1) forward, N(54r+2) dual;
static:  N(72r-37) forward, N(72r-34) dual.
```

The same accepted complete-invoice predicate checks these formulae and
the paid cancelling-pair controls. Logical prefix L1 maxima and denominator
depths are freshly retained for each orientation. They omit Horner
temporaries and physical frame norms, so are not a whole-program precision
or approximate-child error theorem.

There is a useful strict tradeoff. Mutable readers save
`18N(r-2)` component primitives in **each** orientation. However, compared
with static readers at the same stock and arity, their paid abstract
rank-profile pressure increases whenever `r=3,...,7` and `0<b<1`.
To see this, the static source path is `[1,15]` and target path is
`[2,1 repeated r-2 times,16-r]`. The helper and both K-role paths are
unchanged. Cancelling all equal roles, all rank-one visits, and final
target increments leaves the signed histogram

```
Delta H = N( [17-r] + [r] - [15] - [2] ),
sum_j j Delta H_j = 0.
```

Therefore the dynamic-minus-static pressure is

```
N m^b ((17-r)^(1-b) + r^(1-b) - 15^(1-b) - 2^(1-b)).
```

For `f(t)=t^(1-b)`, the function `f(t)+f(17-t)` is strictly increasing
for `2<t<8.5`: its derivative is `f'(t)-f'(17-t)>0`, since f is
strictly concave. Thus r2 ties and r3 through r7 are strictly worse in
this pressure measure. The complete emitted histograms are checked to
have exactly this difference. One exact rational-interval witness per r
at `m=81`, `b=.002+10^-24` supplements the all-parameter written proof.
This comparison changes the choice between these two words: scalar
savings alone do not justify the mutable schedule when the rank-profile
inequality is binding. It is not a complete physical supplier ordering.

## The actual 4,800-module tiling

The explicit forty disjoint acute triples partition the 120 canonical
a-root lines. Each triple has signs sigma making its pairwise inner
products +1. The b-root involution changes the second nonzero coordinate
of an integer root, or the last four coordinates of a spinor root. It
gives sixty disjoint orthogonal pairs. For every triple, b-pair and
`epsilon in {-1,+1}`, take

```
(a_i, epsilon sigma_i b_z),    i=0,1,2; z=0,1.
```

The 4,800 resulting six-port sets partition exactly source IDs
`2160,...,30959`; the 2,160 pure ports are excluded. Their binary labels
are independent of epsilon. The receipt emits every one of the 2,400
distinct label/plane/arc cases, all 4,800 signed module records, and the
complete untiled ID list. Every one of the 172,800 within-module ordered
coefficients and address parities is freshly verified. All 2,400 frame
cases pass the actual rank-two/rank-three/cap/nested-source checks.

The module compensation is `Sigma C_3 Sigma`, where Sigma repeats the
triple sign on each pair. In the standalone complete word, conjugating
every logical register group by Sigma preserves the cost because it
changes only ADD coefficient signs. For the global compensation sum,
use `L'=L Sigma`, `R'=Sigma R`; this gives `R'L'=Sigma C_3 Sigma`
without changing the global K factor. Its signs are paid signed
coefficients, not free unrecorded physical sign gates.

Let D be the disjoint module compensation sum. It handles exactly 115,200
nonzero ordered entries: 57,600 each of absolute coefficients 1/16 and
5/16. The exact residual set consists of odd-Gram ordered pairs lying
outside a common six-port module. The pinned exhaustive Walsh receipt
supplies the inherited full counts; subtracting the newly checked module
counts leaves 480,222,720 entries, including 3,306,240 exceptional and
476,916,480 unit-numerator entries. That full pairing census is not
freshly enumerated here.

## Explicit residual completion and its limitations

There is a specified abstract completion using one old edge helper for
every residual entry. At ZERO precompensate K, module and residual dirt.
Load each edge helper while its original source still occupies its
initial line. Execute the disjoint module source gathers, reach FULL,
and run the unchanged inherited 816-centre K while all targets remain
ZERO. Deliver the modules on their rank-three final arcs and complete
the target cap climbs. Residual edge helpers then deliver at those caps,
reach FULL and undo their source gathers. Every required source line is
inside its residual target cap. The complete logical map is
`y_out = y_in + (K+D+(C-D))x = y_in+x`, with restored
ordinary logical dirt at the declared final frames. The separately
defined dual K episodes give the same-order scalar dual.

This is a specified and counted full-domain stream, not an emitted or
executed billion-event circuit. It inherits the old full K coefficient
and support certificates. The paid paths are `[1,1,14]`, `[3,13]`, and
`[2,1,14]` on tiled sources, targets, and module readers; untiled data
retain `[16]`. Residual readers use `[1,15,1]`. All 816 ordinary K
roles and private rank 13,872 remain separate.

Using the full K scalar bounds from the pinned K inventory, the complete
scalar component count is 11,794,300,560 forward and
11,794,303,008 dual. Against the stated all-edge completion, this saves
1,209,600 component primitives. There remain 480,251,520 ordinary
compensation roles. The complete L5 histogram includes idle work and all
helper padding; its .002 normalized moment exceeds one. Thus this
fallback does not close the desired rank-profile inequality.

The original residual lower bounds are retained within their exact
interfaces. Since every `I-D` module block is invertible and the pure
block is identity, `rank(I-D)=30960`. The inherited 816-centre factorization gives `rank(K)<=816`, hence
`rank(C-D)>=30144`. If all residual dependence uses a private-return
interface, even ideal rank-one episodes require total private rank at
least 44,016; its coverage deficit is negative at every L. Under arbitrary
coefficient redesign confined to these disjoint modules with zero
own-group blocks, `rank(I-D)>=11760`, hence residual rank at least 10,944.
The retained exact logarithmic bound rules out the separately stipulated
favorable private-residual .002 invoice at every positive L. Neither
statement is a bound on mutable ordinary residual networks or overlapping
module constructions.

The original optimistic whole-domain profile tables are also rerun with
all K roles, padding, idle blocks and strict child caps. Their passing
rows are conditional rank/stock screens; they do not construct a
full-domain incidence network. The exact positive-series oracle is
executed from authenticated source, but its unrelated standalone audit
main is not called.

## Reproduction, controls and source adaptation

Run the standard-library checker with an absolute fresh output path:

```
python3 check.py --output /absolute/external/path/CHECKS.json.gz
python3 -O check.py --output /absolute/external/path/CHECKS-optimized.json.gz
```

The source directory and origins manifest default relative to this
checker. Every input buffer is captured and authenticated before any
source execution. The full K factor and scalar bounds are inherited from
its authenticated receipt; their constants are explicitly bound, but its
large factor certificate and pricing program are not reexecuted.
Historical modules execute captured strings compiled
with `dont_inherit=True,optimize=0`; there are no runtime Git calls or
path imports of historical modules. The only executable adaptations
replace loaders/Git/provenance path access, route historical output to a
temporary directory, and add complete ordinary matrices to replay
results. No historical mathematical predicate is removed. Original and
executed-source hashes identify the adaptations. The outputs are combined
in a deterministic receipt; final output uses exclusive creation.

Fresh controls match the intended production error type and exact guard,
rather than accepting any ValueError. They include all meaningful
historical event omissions, actual endpoint and equal-current-frame
check deletions, and cancelling paid ADD pairs that preserve the full
endpoint but fail the shared complete-invoice guard. Deleting only that
invoice guard must make the rejection oracle fail. A redundant r2 static
helper frame marker is explicitly accepted and checked to leave the full
receipt unchanged. Tiling controls duplicate an actual emitted port and
change an actual module sign, then exercise the same emitted partition
and coefficient predicates and their deletions. Coefficient failures
retain exact source/output witnesses.

The fresh outputs are also compared by complete typed JSON projection to all
five original receipts: only the newly added ordinary-column matrices are
removed, and the rectangle's absolute provenance path is normalized to the
explicit portable path. No numerical or mathematical field is ignored.
Large original receipts use gzip transport with both raw and transport byte
hashes; their exact original bytes are recovered before comparison. The
historical notes are retained solely as provenance, not as fresh validation
of their unrelated published results.

The original inequality-only historical diagnostics are retained as
history and rerun, but are not counted as the new defect-sensitive
controls. Normal and optimized complete receipt equality, final hashes,
and the precise package file set are recorded separately. Local replay
does not assert hosted CI, formal-kernel verification, native phases,
physical scans, ownership, coefficient-temporary precision, approximate
children, BIT composition, or an outer multiplication theorem.
