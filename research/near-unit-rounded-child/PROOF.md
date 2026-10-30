# Exact producer-to-child contract at one fixed allocation

This scoped binding uses Nick Petalas's PR6228 producer and Jose Manuel's
PR4198/4205 rational generator interface. The retained compensated program,
its error theorem and phase/compiler lineage remain their contributions.
This note proves the exact parameter comparison; finite execution observations
do not constitute a new universal rounded-error proof.

## One emitted term and the actual receiver

Let v=(1,1,1,0)^t, e0=(1,0,0,0)^t and T=L(v), the lower triangular Toeplitz
matrix with first column v. With the nilpotent lower shift Z,
E=T-ZTZ^t=v e0^t. The fourth coordinate is zero padding to the receiver's
required dyadic size m=4. The original size-three example is not accepted by
this receiver. It is not silently passed as a valid physical child.

The original producer emits g0=v/2, a0=2e0^t. PR6228 at p=3 emits
g1=4v/7, a1=7e0^t/4, with c=7/4. Both products equal E entrywise, so
L(gj)U(aj)=T exactly. These are coefficient rows; no extra conjugation is
applied. The precise norms are

```
||g0||^2=3/4,   ||a0||^2=4,
||g1||^2=48/49, ||a1||^2=49/16.
```

PR4205's literal receiver chooses the least power of two
Gamma >= max(1,2*component_l1(a)). For these rows the thresholds are4 and7/2,
so Gamma=4 for both. This satisfies the original norm and scale predicates;
the displacement bound actually computed by the receiver is B_E=3. The new
g contains denominator7, which remains an exact rational input accepted by
this interface. This is not a Gaussian-dyadic native realization.

## A smaller row does not shrink every stage

The retained macro forms P=I+U(a)/Gamma and G=Gamma*L(g), then executes
P; S(G); P^-1; S(-G), with stored paired compensation. Consequently

```
P0=(3/2)I,     G0=2L(v),
P1=(23/16)I,   G1=(16/7)L(v),
G0(P0-I)=G1(P1-I)=T.
```

The actual split-kernel component envelopes of G are6 and48/7, respectively.
Thus the row and P shrink, while the scaled-shear envelope grows by8/7.
The child must approximate G itself; the old proof explicitly disallows
approximating unscaled L(g) and treating Gamma as free. A monotone precision
gain cannot be inferred solely from the smaller row norm.

At the declared inputs (m,r,B_E,R,t,F0)=(4,1,3,2,12,1), the unchanged allocator
has K_G=200 and alpha=24 for both. It depends on those inputs, not the actual
smaller row norm. Hence its complete allocation is identical: child25,
phase77, multiplier71, leaf69 and data49 bits. Gate/layer upper bounds are344
and114; the executed plans each contain264 gates and98 layers. The latter
counts are executable observations, not a bound for arbitrary future inputs.

## Verification and remaining obligation

The adapter authenticates the frozen producer and eight retained caller inputs,
checks exact factor/T reconstruction and the original admission inequalities,
then invokes the unchanged Program. It does not replace the frozen producer
inside its loader or alter coefficient/data rounding sites. Normal and optimized
wrappers compile scientific sources with optimize=0.

The fixed finite observations use eight real basis inputs, eight imaginary basis
inputs, and one mixed complex dirty-bank input of Euclidean norm 2 (squared
norm 4), per program. For each,
the checker distinguishes the unrounded stored-coefficient endpoint, rounded
endpoint, ideal target, source restoration and observed temporary height.
It checks the retained coefficient, arithmetic, total and restoration allowances.
Rounding is nonlinear: passing a basis does not prove an arbitrary-input error
bound. Exact unrounded source restoration also does not imply exact rounded
source restoration. The receipt keeps those facts separate.

The next obligation is a separately justified allocation or physical consumer
that exploits the row bound while accounting for G, entry/setup coefficients,
stored reciprocals, data rounding and delivery. No Full/Gaussian/finite-core
caller, physical tape, coefficient setup tariff or precision saving is supplied
here. The five selected framework assumptions and selected #6030 are unchanged.

AAAmirinu with substantial OpenAI Codex assistance. Apache-2.0.
