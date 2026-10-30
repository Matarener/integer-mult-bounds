# Dyadic asymmetric H6 pure-bank factors

Status: **local finite construction and positive abstract cost differential;
native frame admission remains open; no new kappa.** All files remain local.
Scientific source pin: `20ecf2891d80b5acf18d980b2164fb44ea7faa90`.

## Construction and coefficient contract

Use the pinned H6 shell of 30,960 unoriented lines in doubled coordinates
`p=(a,b)`, with `|p|^2=16`. There are 1,080 pure lines in each E8 block and
28,800 mixed lines. The old factor is `K=E diag(w) E^T/8192`, with 816 integer
feature columns, 816 arbitrary dirty ordinary centres, and 816 separately paid
private copies of width17. Its private charge is13,872.

For a coordinate `u` in either block, let `g=(u^3-4u)/3`, let `h_1,...,h_7`
be its seven pinned Fano features, and let `t=u|other block|^2` be its trace
feature. Define

```
f(p) = u(|own block|^2-|other block|^2)/16
     = 1_[p is pure in own block] u.
8 f = 2 g + sum_l h_l + 2 t.
g = 4 f - sum_l h_l/2 - t.
```

Replace each of the16 unary input features `g` by `f`, and keep every other
input feature. This is an invertible dyadic basis change: each affected block
has determinant1/4. There are still816 ordinary centres. Its output rows,
expressed as integer numerators with denominator8192, become

```
new f channel:       128 g
each retained h:     4 h -16 g
retained trace:     -3 t -32 g
every other row:     old w E.
```

Every new gather coefficient is an integer on every actual port, and every
scatter coefficient is dyadic. The transformation is compiled into these
static coefficient rows; no unpriced physical basis change is applied to
dirty helpers. `asymmetric.py` checks all665,856 homogeneous polynomial
operator coefficients exactly, with common polynomial denominator96, and
enumerates the coefficients on all30,960 actual ports.

The symmetric orthogonal projection onto the eight pure-block features would
instead have coefficient3/208. Its odd13 denominator is irrelevant to this
asymmetric construction: the input basis changes and the output basis changes
contragrediently.

## Source supports, chronology, arbitrary dirt and restoration

Each pure bank has1,080 ports,135 distinct binary labels of multiplicity8,
binary support span `U` of dimension9, rational coordinate dimension8, and
zero binary radical. These are different ranks. Each source belongs to one
pure bank or is mixed, so no source has to visit both incomparable U9 frames.
The two U9 bases are stored in `ASYMMETRIC.json`.

AtZERO, precompensate all targets by the new scatter rows times arbitrary
centre dirt. Pure sources climb from their actual source lines to their own
U9. The16 selected centres climb ZERO-to-U9 and gather their f totals. All
sources then climb toFULL. The other800 centres climb/gather atFULL. Each
centre takes a cleared, separately paid private copy, moves it from its gather
frame toZERO, scatters its output row, and erases it before the next private
episode. The16 partial centres climb toFULL, all gathers are undone there,
and targets climb to their actual caps.

Write A for the new integer source matrix and B for the new integer scatter
numerator matrix. For arbitrary source x, target y and independent centre
dirt d, the forward scalar word has

```
c=d+A^T x,  y_out=y-Bd/8192+B(d+A^T x)/8192=y+Kx,
c_out=d.
```

The same-order inverse transpose has

```
c=d+B^T y/8192,
x_after_gather=x-Ad-A B^T y/8192,
c_after_private=d,
x_out=x-K^T y,  c_out=d.
```

Private dual episodes gather targets atZERO, ascend to the centre frame,
subtract their value from that centre, and erase. The changed144-column
subword is replayed in both orientations on32 actual ports and208 independent
source/target/helper input columns, with literal common-frame checks and all
private erasures. Eighteen omission/contragredient defects are rejected.
The unchanged672 factor columns inherit their unchanged old word; the full
all-coefficient identity certifies the complete K operator.

## Complete local invoice

The abstract paid paths are:

| Role | Count | Old path | New path |
|---|---:|---|---|
| Pure-bank source |2,160|[16]|[8,8]|
| Mixed source |28,800|[16]|[16]|
| Target |30,960|[16]|[16]|
| Selected ordinary K centre |16|[17]|[9,8]|
| Other ordinary K centre |800|[17]|[17]|
| Selected private copy |16|[17]|[9]|
| Other private copy |800|[17]|[17]|

Thus C decreases from13,872 to13,744. Ordinary bank count, whole-helper widths,
stock, replicas and pads are unchanged. Every newly required source visit is
charged. The full per-stage differential is

```
DeltaH_8=4336, DeltaH_9=32, DeltaH_16=-2160, DeltaH_17=-32.
sum r DeltaH_r=-128; DeltaD=128L.
```

For exponent `b=k+10^-24`, exact positive-series bounds at m49 give changes in
`(pressure-D)/L` of approximately

| k | Change, negative is improvement |
|---|---:|
|.002|−79.65943307239584617746|
|.003|−55.38245424022581778785|
|.005|−6.61430778396813126232|

The sign holds for every positive arity because the complete difference is
`m^b sum_r DeltaH_r r^(1-b)`; changing m multiplies it by a positive factor.
These are local differentials, not a complete H6 or joint supplier moment.

The full all-port scalar census gives6,198,928 nonzero gather incidences,
6,448,528 scatter incidences, and25,294,912 scalar additions. Pinned binary
Horner lowering yields243,600,112 forward and243,602,560 dual component
primitives, improving both old bounds by3,616,928. These counts are before
any real/imaginary doubling and exclude physical frame adapters.

Written whole-K logical prefix l1 bounds are176,641 forward and19,248 dual.
Cleared Horner work is bounded by2,826,256 and307,968 respectively. The largest
reduced scalar numerator is16, and scalar fractional depth above the entrance
grid is10. `ASYMMETRIC.json` gives the complete absolute-sum derivation. These
are exact-word local bounds, without an approximate-child/global rounding
claim.

## Frame obligation and exact compiler entrypoints

Use actual old source representatives `T_line(p)=C_p`, actual target caps
`T_cap(p)=F C_p^-1`, `T_ZERO=I`, `T_FULL=F=C_[17]`. A concrete candidate new
representative is `T_U=canonical_frame(17,U)` with the displayed RREF U9 basis.

Definitions and reusable lowering code are at:

```
/Users/ross/git/math/integer-mult-bounds/research/split-centres-global/vendor/clifford_exact.py
    canonical_frame(n,U), cgate(n,p), fourier(n), lower_child(op)
/Users/ross/git/math/integer-mult-bounds/research/h6-compensation-network/physical_compiler/compile.py
    compile_transition(old,new,expected_rank)
    exact_state, accelerated_zero_state, decode, adapter_count
/Users/ross/git/math/integer-mult-bounds/research/native-source-codes/native_verify.py
    frame(vectors,n) independently states the same general canonical definition.
```

A cheap signed-tableau check was run for every one of the135 distinct pure
labels in each bank. With these exact candidate definitions, every
`C_p -> T_U` has Fourier B-block rank8; `I -> T_U` has rank9 and
`T_U -> F` has rank8. This is only a rank check, without global-phase proof or
serialized native recipes. Each U9 contains the characteristic vector and has
alternating perpendicular8. Therefore the old norm-one endpoint orthogonal
completion theorem alone is insufficient. The next specialist must emit and
independently decode phase-correct two-sided Gaussian monomials for these
transitions and their inverses, check signed tableaus **and** exact global
phase, and price address movements/quadratic/unit phases. The existing
`compile_transition` implements precisely that kind of check. The positive
DeltaH is not admitted until this obligation passes.

## Additional exact screen and limits

`kernel.py`/`KERNEL.json` lift exact integer bases of the complete rational
supported cubic spaces. Matching modular outside-row ranks prove dimensions;
all outside coefficients are checked zero overZ. Root-normal character1 has
dimension57 and union14,016, character0 has dimension24 and union16,944.
Norm-four-normal character0 has dimension64 and actual union14,520.
Their inverse coefficient forms have matching full modular rank57,24,64.
Paying visits to each entire supported-space union still fails the abstract
moment. This does not exclude smaller unions, as the pure-bank construction
demonstrates. The exploratory sampled upper bounds86 and69 were not exact
dimensions; the root-normal character0 upper bound24 is attained.

The finite positive result does not supply a full H6 compensation network,
compatibility with another network's intermediate source frames, exact native
frame recipes, complete physical movement/tape/controller costs, all-size
precision with approximate children, a chronological owner allocation, a
matching BIT supplier, or any improved kappa. Common frames only lift the
scalar proof once their actual operators and paid recipes are fixed. A finite
exhaustive coefficient proof is not a formal-kernel multiplication theorem.

## Reproduction and next obligations

From any working directory, with the pinned source checkout unchanged:

```
/Users/ross/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 /Users/ross/git/math/.research-automation/runs/kappa-major-20261018T1330Z/bulk-partial/screen.py
/Users/ross/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 /Users/ross/git/math/.research-automation/runs/kappa-major-20261018T1330Z/bulk-partial/kernel.py
/Users/ross/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 /Users/ross/git/math/.research-automation/runs/kappa-major-20261018T1330Z/bulk-partial/asymmetric.py
```

Immediate next obligation: independent structural/algebra review of the unit
basis change and full invoice, plus the frame specialist's exact recipe and
phase obligation above. Only after that should an outer supplier specialist
test composition against the actual full H6 schedule and matching BIT moment.
All source and generated artifact hashes are in `MANIFEST.json`.

Attribution: pinned E8 geometry/operator factors are Dominik Scholz's PR606
construction; H6 proposal is DreamingOfClouds's. The preserved H6 compensation
network and finite compiler audits supply the inherited source interfaces.
The new pure-bank asymmetric change, local proofs, invoices and exact finite
computations here were prepared with substantial Codex assistance under Ross's
local-only instruction. No files in the primary or preserved old run were
changed, and no publication/export/push was performed.
