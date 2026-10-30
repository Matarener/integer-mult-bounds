# Eight partial Pauli centres and a paid cyclic refinement

This contribution proves an exact logical gather/scatter identity with arbitrary
ordinary input dirt, reconstructs its finite binary-frame data, and prices one
compatible refinement of the fixed disjoint rank-three cyclic tiling. The
refinement exists, but its complete differential power bill is adverse at the
three tested exponents. It does not supply a native phase compiler, a rounded
supplier, a physical controller, or a new multiplication bound.

The scientific snapshot is `20ecf2891d80b5acf18d980b2164fb44ea7faa90`.
`ORIGINS.json` records the unchanged historical inputs and the explicitly
adapted code. Geometry/factorization credit remains with the preserved source
authors, including Dominik Scholz and the H6 proposal by DreamingOfClouds.
This proof, the independent compatibility construction, and the portable audit
were prepared with substantial OpenAI Codex assistance. The noncubic-rank and
Smith-theorem scopes already published separately are not claimed here.

## 1. Exact model and boundary

Work over dyadic rationals, or over their complexification componentwise. A
register at frame A has physical value `T_A ell`, where `ell` is its logical
value. The assumed frame family has fixed invertible representatives: a move
A to B executes exactly `T_B T_A^-1`, and every scalar ADD uses identical
representatives on its two operands. For the accounting in this contribution,
a nested move A to B has the inherited tariff `dim(B)-dim(A)`; repeated moves
are separately charged. Private descent has the same dimension-difference
tariff. These are explicit historical model premises. They do not follow just
from binary containment, and this audit does not compile these degenerate
frames into native Fourier children.

There are eight ordinary centres c, arbitrary logical source values x,
arbitrary target values y, and arbitrary centre dirt d. Sources start at their
one-dimensional binary labels, while targets and centres start at ZERO.
Sources and centres finish at FULL; each target finishes at its prescribed
16-dimensional cap. Restoration of c means restoration to logical d at FULL.
Its physical final value is `T_FULL d`, not its physical ZERO entrance value.
No uncharged raw helper-return tail is inferred.

The private output interface is assumed explicitly: make a private snapshot
of a centre at U, descend to O contained in U, scatter from that unchanged
snapshot at O, then erase the private copy. O is either ZERO or W below.
The same-order dual uses a cleared private readout at O, gathers from the
targets, moves it to U, subtracts it from the centre, and erases it. This is a
separate private interface, not the inverse transpose of a destructive CLEAR
primitive. Clear, copy or readout, weighted ADDs, and erase are all charged.
An emitted native implementation of this interface is outside this result.

## 2. The selected eight columns and their complete support

Use the pinned ordering of the 120 canonical doubled E8 root lines. For a
mixed port `(a,b)` define

```
q(b) = sum(j=0..7) (-1)^(j mod 2) b_j^2,
E_i(a,b) = a_i q(b),             0 <= i < 8.
```

These features vanish on the pure ports. They do not depend on the relative
sign of the b block. In `e8_sections.evaluate_operator_centers`, the first 112
columns are pure cubics. Each following coordinate contributes one unary,
seven Fano, 35 traceless symmetric Pauli, and one trace column. The first
nonidentity Pauli parameter is `(shift,character)=(0,1)`. Thus these are
exactly columns `120+44i`, each of weight 1 and denominator 8192. This binding
is a direct translation and inspection of the preserved evaluator, not an
execution of its NumPy-based complete 816-column implementation. The new
checker recomputes the selected polynomial values and the index arithmetic.

The selected b-line indices are

```
3,4,7,10,13,15,16,18,21,23,26,28,31,33,35,36,38,40,
107,109,111,114,116,118.
```

On them q is +8 or -8; it vanishes on the other 96 lines. There are therefore
`120*24*2=5760` supported physical ports. The receipt contains every supported
port, its source identifier, sign, 17-bit label, and eight feature values.
Each individual feature has 3744 nonzeros: 3072 of absolute value 8 and 672
of absolute value 16.

The exact common support space and its orthogonal complement are

```
U = (65537,33024,16640,8192,4352,2048,1024,513,
     129,65,33,17,9,5,3),
W = (66303,53504).
```

The checker exhausts the 17-bit orthogonal complement: `dim U=15`,
`U^perp=W`, `dim W=2`, and `W` is contained in U. In particular U is
degenerate, with restricted pairing rank 13. Every supported source line is
contained in U and every supported target cap contains W. Independently
forming the eight individual feature-support spans gives U in all eight
cases, so the union space is not concealing a cheaper individual support
space for this fixed group.

There is also a fresh, narrowly scoped support obstruction. Evaluate all 35
nonidentity symmetric Pauli quadratic forms on the 120 canonical root lines.
Their rational evaluation rank is 35; restriction to the 96 complementary
lines has rational rank 34. Hence the space of these quadratic evaluation
functions supported on the selected 24 lines is exactly one-dimensional.
It contains q and is therefore precisely its span. This rules out simply
choosing additional independent quadratic directions with this same support
inside this 35-dimensional family. It is not a lower bound for other feature
families or other schedules.

## 3. Arbitrary-dirt factor law and its same-order dual

Write E for the full selected feature matrix and D=8192. All expressions in
this section are logical values. In the forward word execute

```
y <- y - E d/D                      at ZERO,
c <- d + E^T x                     gather at U,
y <- y + E c/D                     through the private U-to-O interface,
c <- c - E^T x                     at FULL.
```

The second and last lines are the actual additions to the initially dirty c.
Their combination restores c to d. Substitution in the two target lines
gives `y <- y + E E^T x/D`, for arbitrary x, y, and d. All contributing source
lines can enter U, and all contributing targets can enter O, so every ADD
uses one common frame representative. The moves to FULL and target caps
are explicit and separately charged.

For an ADD `dst += v src`, logical inverse transpose is
`src -= v dst` in the same chronological order. Applied to the four logical
blocks, with the separate dual private readout, this gives

```
c <- d + E^T y/D,
x <- x - E c,
c <- c - E^T y/D,
x <- x + E c.
```

Thus `x <- x - E E^T y/D`, y is unchanged, and c is restored to d. This is
the same-order logical inverse transpose. It is not a reversal of the frame
climbs or a claim that the raw map has unchanged entrance and exit gauges.

In physical coordinates the forward source-to-target block is
`T_cap(t) (E E^T/D)_(t,s) T_line(s)^-1`, and the diagonal source and centre
blocks include their declared endpoint transports. This statement follows
from the fixed-representative invariant, conditional on that frame model.

For an independently inspectable finite diagnostic, the checker reconstructs
the historical 19 actual ports, their 46 independent ordinary input columns
(19 x, 19 y, eight c), the complete event list, and every final rational row.
It runs both orientations at O=ZERO and O=W. The receipt explicitly records
the column order. These are four complete finite operator replays with
arbitrary dirt, not clean-input tests. The full 5760-port identity follows
from the displayed factor law and exhaustive support/frame checks, not a
claim to have executed a dense 5760-port matrix replay.

## 4. Private, scalar, and standalone visit bills

Each selected ordinary centre has path `[15,2]` instead of `[17]`. Its private
descent costs 15 for O=ZERO and 13 for O=W, instead of 17. The eight private
descent totals are 120 and 104. In the inherited full 816-centre K context,
the private rank sum changes from 13872 to 13856 or 13840. The other 808
centres are unchanged; this is not a new validation of their full word.

Standalone supported sources have path `[14,2]` instead of `[16]`. Radical
output also changes each supported target from `[16]` to `[2,14]`. ZERO output
leaves the target path `[16]`. There are no new ordinary centre roles or pads.

For nonzero reduced `v=a/2^d`, use the inherited cleared-work scalar tariff
`p(v)=3+floor(log2 |a|)+popcount(|a|)+d`. The absolute numerator choices give

```
p(8)=7, p(16)=8, p(8/8192)=14, p(16/8192)=13.
```

The selected forward word therefore costs, before real/imaginary doubling,

```
8 * [2*(3072*7+672*8) + 2*(3072*14+672*13) + 3]
  = 1,258,008.
```

The final 3 charges private clear/copy/erase. In the dual, the centre/readout
unit ADD replaces copy and costs four, adding three per centre: 1,258,032.
The full K scalar figures 247217040 and 247219488 are inherited unchanged
background, explicitly labelled as such in the receipt; this checker does
not execute the full background scalar stream.

The complete selected logical subword has forward prefix row norm 35329 and
dual prefix row norm 152, with dyadic depth 10. The forward maximum is
`1+3072*8+672*16`. The dual maximum is exhaustively evaluated over all 120
canonical a and all eight-centre prefixes k, including k=0:

```
1 + 8*sum(i<k)|a_i| + (3/8)*sum(z in roots)|sum(i<k) a_i z_i| = max 152.
```

The formula accounts for the remaining dirty-centre columns and the exact
partially accumulated source-output row. Centre rows and private readouts
are bounded by the corresponding gathers. These are logical subword bounds;
they do not price coefficient temporary rows, bound physical frame norms,
or establish a whole-supplier rounding precision contract.

## 5. Actual compatibility with the fixed cyclic tiling

The fixed tiling has 40 acute a-triples, 60 orthogonal b-pairs and two signed
modules per pair, hence 4800 disjoint six-port modules. The checker parses the
unique literal TRIPLES assignment from the authenticated historical source,
reconstructs its signs and b-involution, and emits all 2400 distinct binary
frame cases. Their canonical JSON digest (sorted keys, compact separators,
no trailing newline) is

`90b0a4049066b6eb08ab223ba03d8f9af95bbe688a09c4ee5c7f586ad1fdd46b`.

This exact full array is the cross-contract object shared with the independent
cyclic package; a digest alone is not substituted for array reconciliation.

The involution preserves the selected b support: exactly 12 b-pairs, hence
960 signed modules and all 5760 selected physical ports, are affected. The
remaining 3840 signed modules are unchanged. For every affected port the
actual source's final three-dimensional arc is contained in U. Its original
source path `[1,1,14]` can therefore be refined to `[1,1,12,2]`, inserting U
after its last cyclic gather and before FULL.

For every affected target the existing three-dimensional delivery arc A has
`dim(A intersect W)=1`. Thus W is not contained in A, and a monotone
`ZERO -> W -> A` path is impossible. This is the concrete obstruction to
declaring the target W visit already paid by the unchanged cyclic word.

Set `J=A+W`. Every one of the 5760 cases has `dim J=4` and `J` is contained in
the receiving target cap. A compatible radical refinement is

```
target: ZERO -> W2 -> J4 -> cap16,       increments [2,2,12],
reader: ZERO -> plane2 -> arc3 -> J4 -> FULL17,
                                             increments [2,1,1,13].
```

The module reader and target now share exactly J at delivery. The previous
target increments were `[3,13]`; the previous reader increments were
`[2,1,14]`. Every extra reader move is charged. ZERO private output needs no
target/reader refinement, but still pays the source U insertion. The receipt
contains all 1440 selected triple/pair/group joins, each with multiplicity
four for the two group ports and two signed modules.

Here is a valid global chronology within the inherited logical frame model:

1. Execute all ZERO dirt precompensations for K, cyclic modules, and residual
   edge helpers. Load residual edge helpers at the original source lines
   before any source leaves those lines.
2. Execute the original cyclic gathers at the required planes and arcs.
   Logical source values remain immutable. Each selected source then enters
   U, where the selected eight ordinary centres gather, before the sources
   move on to FULL.
3. With sources at FULL, perform the unchanged 808-centre gathers and ZERO
   scatters. Finish every ZERO output needed by those centres before any
   affected target enters W. The selected ZERO-output variant also scatters
   here. The selected radical-output variant scatters after affected targets
   enter W. Selected centres move to FULL and clean up using FULL sources.
4. For affected radical modules, move readers from their arc to J and targets
   from W to J, then execute the original cyclic delivery coefficients.
   Unaffected modules retain their original delivery frames.
5. Move targets to their caps and deliver the preloaded residual edge helpers
   there. Restore ordinary readers/centres logically at FULL using the
   unchanged FULL source values. Their physical endpoint residuals remain
   declared, rather than being silently replaced by raw restoration.

This chronology changes no scalar coefficient, ordinary role, or stock. It
establishes the required common frames for the specific construction; it is
not a general result about arbitrary edge interleavings or native schedules.
The same chronology supports the logical same-order dual because the
common-frame and private-readout contracts hold in that orientation too.

## 6. Complete changed-role histograms and signs

Let H_r denote one rank-r event. All unchanged events, scalar work, and stock
cancel in the comparison. The centre/private contribution is

```
ZERO:    8*(2 H15 + H2 - 2 H17),
radical: 8*(H15 + H2 + H13 - 2 H17).
```

For the actual cyclic refinement the additional source contribution is
`5760*(H12+H2-H14)`. Radical output further contributes

```
target: 5760*(2 H2 + H12 - H3 - H13),
reader: 5760*(H1 + H13 - H14).
```

Consequently the complete differential histograms are

```
ZERO:
  5760*(H12+H2-H14) + 8*(2 H15+H2-2 H17),

radical:
  5760*(H1+3 H2+2 H12-H3-2 H14)
  + 8*(H15+H2+H13-2 H17).
```

Their rank masses are -16 and -32. Rank mass alone does not determine the
concave power bill. At exponent beta the differential moment is

`m^beta * sum_r deltaH_r * r^(1-beta)`.

For the fixed unsplit histogram, `m^beta>0` preserves its sign for every m>0.
For the full H6 invoice asserted here, restrict to admissible odd L>=3,
m>=49, whose half-width cap is at least 34. All recorded ranks at most 17
then fit without cap splitting. The L=1 capped bill is not checked.

The following m=49 intervals are displayed as decimal approximations only;
the receipt stores rigorous rational lower and upper endpoints at the exact
listed beta. Positive means more expensive.

| beta | ZERO standalone | ZERO paid cyclic | radical standalone | radical paid cyclic |
| --- | ---: | ---: | ---: | ---: |
| .002 | 53.7998503675 | 50.4954366332 | 107.496538805 | 123.026676735 |
| .003 | 88.8945552816 | 83.9366685567 | 177.634095887 | 201.033060078 |
| .005 | 159.475575170 | 151.208233483 | 318.691883816 | 358.037780064 |

The standalone differential replaces each supported source `[16]` by
`[14,2]` and, for radical output, each supported target `[16]` by `[2,14]`.
Those bills are also complete for their stated changed roles. Neither
standalone nor this actual cyclic refinement is a cost improvement at the
tested exponents, despite the lower rank mass.

## 7. Conditional sharing threshold, without free transport

For a different compatible word that has already paid some *identical* U/W
visits, define

```
d(beta) = 14^(1-beta)+2^(1-beta)-16^(1-beta) > 0,
g(beta) = the centre/private differential from Section 6.
```

If exactly n of these visits must newly be paid, this coarse fixed-visit
comparison improves precisely when `g(beta)+n*d(beta)<0`. The following
strict integer thresholds are certified on both neighboring integers:

| beta | ZERO maximum new of 5760 | ZERO minimum already paid | radical maximum new of 11520 | radical minimum already paid |
| --- | ---: | ---: | ---: | ---: |
| .002 | 1314 | 4446 | 2637 | 8883 |
| .003 | 871 | 4889 | 1752 | 9768 |
| .005 | 518 | 5242 | 1044 | 10476 |

These are conditional arithmetic thresholds, not a compatibility certificate
for a word supplying those visits. The tested cyclic word has no existing
U15 source visit or W2 target visit. Its actual compatible refinement has the
different, fully paid histogram above and fails the improvement screen.

For every rational exponent p/q used in these comparisons, the checker
constructs integers a with
`a^q <= r^p*10^(35q) < (a+1)^q`. This encloses the power between consecutive
35-digit rationals; a floating approximation only seeds the integer search
and is not part of the acceptance condition. Interval signs, the ratio
enclosure, and both neighboring integer signs are checked exactly.

The receipt separately certifies persistence of the signs and integer
thresholds at `beta+10^-24`. Since every profile rank is at most 17,
`log r<3`; over the intervening interval each coefficient changes by at most
`3*sum_r |deltaH_r| r * 10^-24`. The strict interval margins exceed this
bound, including the newly paid visit multiples at both threshold neighbors.
This does not assert that the displayed decimal values at beta are identical
to the values at the shifted exponent.

## 8. Reproduction, controls, and evidence boundary

Run the checker with a new absolute output path outside this directory (and
outside an overridden `--inputs` directory):

```
python3 -I -B check.py --output /absolute/external/new-receipt.json
python3 -I -O -B check.py --output /absolute/external/new-optimized-receipt.json
```

Only Python's standard library is required. Every source input is read once,
authenticated by SHA-256, and retained as captured bytes. Only the adapted
`geometry.py` is executed; it is compiled from those captured bytes with
`optimize=0`. Historical modules are preserved unchanged and never imported.
There are no ambient Git reads, NumPy dependencies, or bytecode-cache loads.
Outputs are opened exclusively, and no existing path is overwritten.

The complete receipt includes all support ports, all 2400 tiling frame
cases, all selected joins, all four exact diagnostic operator matrices and
their ordered input columns, separate visit histograms, rational power
intervals, and every negative-control result. It is compared byte-for-byte
under normal and optimized Python. The package inventory records the final
source and artifact hashes.

The 28 semantic defects actually executed are omissions of dirt prefix,
gather, private scatter, cleanup, source-U entry, and centre-U entry in both
orientations and both output variants (24); omitted target-W entry in both
radical orientations (2); the impossible unpaid `W -> old arc` target move
(1); and omission of the added reader invoice (1). Each must fail at its
intended named production predicate. The checker then runs the same defect
again with only that named predicate disabled, outside the rejection catch,
and requires successful completion. This gives 28 executed guard-deletion
sensitivities as well as 28 intended rejections. It does not claim each guard
alone covers every source, invoice, or runtime fault.

Finite computation, written all-input identities, and implementation
admission remain distinct. The support, 35-column rank restriction, fixed
tiling census, rational inequalities, and 46-column diagnostics are finite
exact computations. The arbitrary-dirt factor identity and chronology are
written proofs under the declared frame/private interfaces. A native
phase-correct implementation for degenerate U/W, literal raw helper return,
physical source access, stock/owner allocation, full precision propagation,
and a joint asymptotic supplier remain separate obligations.
