# Literal backward native K

Let `A=diag(D,D)` and `C=C_K`. The proved forward word is
`F=A L(C Q^-1)`. Since C is real symmetric and Q is symmetric,

```
F^-T = A^-1 U(-Q^-1 C).
```

Every emitted gate is invertible. There is no CLEAR, COPY, allocation or
owned zero field. If the chronological gates are `E_1,...,E_m`, the matrix
is `F=E_m ... E_1`, and `F^-T=E_m^-T ... E_1^-T`. Thus the same chronological
gate order, with each gate replaced by its inverse transpose, is exact.
This statement does not reverse chronological order.

For a real scalar ADD `destination += c source`, inverse transpose is
`source += -c destination`. For an ordinary unitary monomial M, inverse
transpose is its complex conjugate. The literal P and X factors remain
unchanged; each D factor retains its quadratic coefficient 2 modulo 4 and
negates its Z4 linear coefficients; each scalar phase is negated modulo 4.
The entire chronological monomial factor order remains unchanged.

Each paid child is a product of commuting positive coordinate Gaussians.
On one coordinate `C_plus^2=X` and `C_plus^4=I`, including their scalar
phases. Therefore `C_minus=C_plus X`. A rank-r inverse child is emitted
as the same positive rank-r child followed by the single ordinary X whose
mask is the sum of the r child coordinate vectors. This is a literal
phase identity on all address columns, not only an equality of tableaux.
`backward.py` checks it densely on all columns and all nonempty coordinate
subsets for dimensions 1 through 4, and checks the first physical rank-8
path with fresh sparse Gaussian-integer arithmetic. Every translated
physical path also has its conjugated signed tableau and rank checked.
The all-dimensional result follows directly from the one-coordinate
identity and commuting tensor factors.

Now put `J=diag(Q^2,I)`. Emit input X `Q^-2`, both output-bank `D^2`, and
output X `Q^2`. D and Q act on disjoint address coordinates. The result is

```
J A^2 F^-T J^-1 = A U(-Q C) = B_K.
```

The first diagonal block is `Q^2 D Q^-2=D`; the second is D; the upper
off-diagonal block is `-Q^2 D Q^-1 C=-D Q C`. C is never commuted across Q.
The implementation performs these exact word reductions independently.
Since `Q^2=Q^-2=X_0` and `D^2=X_[1,25)`, every boundary is ordinary. The
consecutive X-bank output masks are literally composed to `X_[0,25)`.

The resulting program retains all 1,024 original fields. The transformed
scalar word acts on independent coordinates obtained by its explicitly
conjugated incoming wrappers and input boundary. Replaying every ADD gives
unchanged Y coordinates and X coordinate `u-K_odd^T v`. The gatewise
inverse-transpose identity, including its ordinary boundary factors,
identifies this logical replay with the stated physical B_K endpoint on
arbitrary independent original ground-chart inputs. No coupled X endpoint
is credited as a separate autonomous Gaussian output.

The paid profile remains 512 children of each width 8,9,15,16 per cube.
There is one new X per child and three boundary X factors per owner port.
The complete per-port ordinary invoice is therefore 76 ADD,15 P,15 D,
13 X,6 phase. The implementation verifies these counts from the literal
stream, including identity opcodes; it performs no COPY or CLEAR.

The transformed X rows have intermediate coefficient l1 at most 8 and
denominator exponent at most 4, while Y rows remain unchanged. All address
factors and boundaries are unitary, so the same factor 8 bounds each field
norm relative to the largest independent original input norm. This remains
a local growth constant rather than a complete caller precision analysis.

At positive field width f, the address maps tensor-lift and a literal
scalar phase theta becomes `i^(f theta)`. The real owner ADD coefficients
are negated and transposed once. The owner K matrix is never raised to a
tensor power. The same generic transformation applies independently to
every cube in the structured all-family forward constructor.

This is a backward K component. It neither produces H nor closes a whole
caller, and gives no precision/storage admission or kappa improvement.
