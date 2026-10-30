# Residual shared readout: the unchanged target bank cannot realize the gap

2026-10-09. Douglas Colkitt, with OpenAI Codex assistance. Apache-2.0.

**No cheaper word, stronger supplier, or new κ results.** This bounded
follow-up closes two simple implementations of the
[two-line residual contract](../joint-readout-design/REPORT.md): a single
shared transform around the unchanged parallel target bank, and direct
readout at the unconverted residual center frames.

The first exclusion permits arbitrary scalar encoding and decoding. The
second replays literal words on arbitrary data. Neither is a theorem
about all distributed, interleaved readout graphs.

## Contract and accounting

Use the preceding plain triple geometry with local dimension h. There
are `n=binom(h,3)` targets, with final frames `K_T=I-P_T`, and two residual
center lines

\[
 a=e_0+2e_1,\quad b=2e_0+e_1,\quad L_0=P_a,\quad L_1=P_b.
\]

The original arbitrary centers remain untouched. Their dependent copies
have already been moved from `R_j` to `L_j`, costing two width-(h-2)
children. These copies do not add independent role volume.

Write `D_F` for the physical partial-address permutation at projector F.
In physical coordinates the required target output is

\[
 D_{K_T}\left(y_T+U_{T0}D_{L_0}z_0+U_{T1}D_{L_1}z_1\right),
 \qquad U_{Tj}=\mathbf1_{j\in T}.
\]

All displayed arrays are arbitrary; scalar payload is F2 for the bit
application. Q payload is also checked as a local algebra control.
Ordinary residual readout transforms each center copy to zero, with two
width-one children, and then transforms each target once by `D_KT`.
The preceding rational **address-matrix discrepancy** has only one rank
of excess. That lower bound remains correct, but need not be achievable.

## Single shared transform around one target bank

Consider this relaxed model:

1. Arbitrary scalar pointwise mixers and dependent copies are free.
2. The target operations form a single parallel bank of the unchanged
   operators `C_T=D_KT`. For a stronger exclusion, allow their linear span
   on any input, without charging extra repetitions of these operators.
3. One additional full-volume transformation acts on one mixed array,
   either before the entire bank or after it.

This is more permissive than requiring all scalar gates to have compatible
frames. It does **not** allow another target-transform layer, split target
paths, arbitrary packing of several independent full arrays into one
array, or smaller-volume multistream primitives.

Let `B` be the scalar linear span of `I` and the `C_T` as operators on
arrays. Take the required target/center operator matrix modulo B:

\[
 E_{Tj}=[U_{Tj}C_TD_{L_j}]\quad\text{in the operator quotient by }B.
\]

An extra early operation on `sum_j alpha_j z_j`, possibly also including
arbitrary target inputs, contributes

\[
 E_{Tj}=F_T\alpha_j
\]

after the parallel bank and final scalar decoding. Here `F_T` may be any
operator allowed by the relaxed model, while `alpha_j` is a scalar.
Thus its two operator-valued columns must be scalar proportional.

They are not. Pick an exclusive target containing 0 but not 1. Its row
is `(nonzero,0)` in the quotient. A target containing 1 but not 0 has
row `(0,nonzero)`. For such a target, `L_j` is nested in `K_T`, so

\[
 C_TD_{L_j}=D_{K_T-L_j}.
\]

This partial transform has width `h-2`, whereas the bank transforms have
width `h-1` and the identity has width zero. It is a distinct address map
outside the span B. Both columns are therefore necessary. This proves
that **one extra early transform cannot work**, irrespective of its width.

An extra late transform produces a single new array. Scalar decoding can
only add scalar multiples of that array to different target outputs.
Consequently all operator-valued rows of E must be scalar proportional.
The same two exclusive targets disprove this. In the finite controls,
the row rank is actually 9 at `h=5` and 16 at `h=6`, so a construction
using only late extra transformations needs at least that many new array
outputs. These counts are specific to this parallel-bank model.

### Why distinct address operators are independent here

The calculation concerns operators on arbitrary arrays, not ranks of the
address matrices themselves. A finite set of distinct invertible rational
linear address maps admits an address whose images are all distinct:
avoid the finite union of kernels of their pairwise differences. A delta
input at that address separates the resulting array permutations. Thus
the operators are linearly independent, over either Q or F2 payloads.

The script additionally supplies a finite-address witness modulo 1009:
23 distinct operators have 23 distinct images at `h=5`, and 41 have 41
distinct images at `h=6`. All denominators are invertible. These witnesses
check the operator-span calculation directly; they are not a fixed-tape
implementation theorem.

This explains the apparent discrepancy with the earlier one-rank floor.
That floor concerns **rank differences of address frames**. Here we need
to implement several distinct **permutations of arbitrary arrays**. A
linear dependence in the former does not identify the latter.

## Literal alternative: send targets to unconverted centers

Choose a subset of residual centers to transform to zero. Read those
copies into targets at zero. For each remaining required center, move the
target to `L_j`, add the unchanged center copy there, and finally move to
its prescribed `K_T`. Every relative transform and final alignment is
charged. Original centers remain untouched; no target is assumed clean.

All four copy subsets are replayed at `h=5,6`, over Q and F2. These words
are correct. They do not save work:

- An exclusive target can visit its required line within its final cap,
  replacing a width-(h-1) child by widths 1 and h-2. Its rank is unchanged,
  but its recurrence moment increases.
- A target containing both 0 and 1 cannot do this. For either residual
  line, `rank(K_T-L_j)=h`. Visiting one unconverted line costs widths
  1 and h, two more ranks than the original width h-1.
- Visiting both lines costs widths 1, 2, h, four extra ranks.

There are `h-2` common targets. If k of the two centers are converted to
zero, the total residual rank is exactly

\[
 n(h-1)+k+2(h-2)(2-k).
\]

For `h=5`, including the two paid width-three peeling children:

| Converted centers | Residual rank | Complete rank |
|---|---:|---:|
| Both | 42 | 48 |
| One | 47 | 53 |
| Neither | 52 | 58 |

The original, unpeeled copied readout has rank 48. Even converting both
residual lines to zero is worse in the moment: it splits each original
width-four center child into widths three and one. At the illustrative
coarse-bit saving 0.08 and ambient dimension `3h`, exact enclosures show
that every tested complete word has a strictly larger moment than the
unpeeled original. This includes all peeling, readout and target movement.

The formula-only `h=23` control gives excess residual ranks 2, 43, 84 for
two, one, zero converted centers respectively. It is not a dense replay
or a substitution into the selected supplier.

## Decision and remaining scope

The bounded diagnostic is complete. Do not continue searching scalar
encoders around this unchanged single target bank: the exclusion already
allows arbitrary such mixers. Do not treat the joint address-rank gap as
an achievable saving, and do not replace copied readout with the direct
target words above.

A surviving proposal must change a premise: for example, interleave
target transformations and readout so intermediate target work is shared,
use a different full invocation with characteristic-dependent cancellation,
or supply a genuinely cheaper volume contract. The first possibility
must still satisfy the previous strict child-moment budget. These are
unresolved mechanisms, not recommendations for an unrestricted search.

The practical admission rule for another round is an explicit short
interleaved word or a new accounting identity explaining which paid
children it removes. Merely selecting more internal frame matrices is
insufficient. No general impossibility of the two-line contract, finite
networks, or a larger κ has been established.

## Reproduction

```sh
python3 -B research/residual-shared-readout/audit.py --check research/residual-shared-readout/certificate.json
python3 -B -m unittest discover -s research/residual-shared-readout -p 'test_*.py'
make selected-record-check
```

The certificate contains exact physical replay results, complete child
histograms, rational moment enclosures and finite-address separating
witnesses. Tests include a positive control where a single shared transform
does work after both frames and demands are made identical, then verify
that restoring either original distinction defeats that construction.
