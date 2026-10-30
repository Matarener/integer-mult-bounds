# All-address implication for the emitted local word

All matrices in this proof use exact rational entries. Each source frame gives
orthogonal row families B and A, with lengths r and8-r. Let W have columns B
followed by A. The checker verifies orthogonality, both inverse identities and

```
P = W diag(I_r,0) W^-1,   P^2=P,   P^T=P.
```

It does this for all636 used frames. Both W and its inverse are retained in the
denominator census. For every one of2,367 directed query descriptors (s,t,k),
let lo,hi order the frame dimensions. The checker verifies

```
0<k<8, dim(hi)-dim(lo)=k,
P_lo P_hi = P_hi P_lo = P_lo,
R=P_hi-P_lo, R^2=R, R^T=R.
```

It computes bases of the row spaces of R and I-R. Their combined transpose V
is invertible, and `V^-1 R V=diag(I_k,0)`. Both inverse products are checked.
Thus k is the actual residual rank, not a frame label or a modular trace.
The denominator census includes V and its inverse.

## Native maps and modulus guard

For a paired address x with16 entries, define d_i=x_i-x_(15-i), i=0,...,7.
The source native involution H_P sends

```
x_i       -> x_i       - (P d)_i,
x_(15-i)  -> x_(15-i)  + (P d)_i.
```

It preserves each paired sum and sends the difference vector to `(I-2P)d`.
Since P is idempotent, H_P is an involution. The two nesting identities give

```
(I-2P_t)(I-2P_s) = I-2R,
H_R = H_(P_t) H_(P_s).
```

The verifier checks the first identity with actual rational matrices for every
directed query. The paired sum/difference calculation proves the second, with
its order. Addition and subtraction recover both halves when2 is invertible.

Let D be the least common multiple of2 and all denominators in the frame,
residual and normalizer matrices and their inverse/rank witnesses. The complete
census gives D=12. All checked identities hold in Z[1/D], so they reduce modulo
any integer q>1 coprime toD. Inverses remain inverses; each residual remains
conjugate to its stated diagonal projection. This gives a sufficient explicit
guard, including the source calibration moduli101 and10201. It does not assert
that a prime dividingD must fail: a chosen rank witness can add a denominator.
The source's wider prime-selection and native-contract hypotheses remain.

## Chronological induction on arbitrary functions

Treat every entry field, including each dirty owned field, as an independent
function with values in F2. Transport by an address permutation M means
`(T_M F)(x)=F(M^-1 x)`; thus `T_M T_N=T_(MN)`. A field at frame f has a
normalized representation as a sum of its entry functions transported by
`H_f H_(entry frame)`, with coefficients in F2. Every current coefficient row
is stored exactly as a bitmap.
For an owned entry with no frame, no frame map can read it before its first clear;
the current-frame checks enforce this, and the clear removes its coefficient.

A query s->t replaces H_s by H_t using the checked identity above. At an ADD,
both operands must actually have frame f, so their common H_f factors permit
exact XOR of their coefficient rows. A zero row implies the whole function is
zero because the representation is valid for arbitrary independent entries.
It permits ZERO_Q or zero initialization. ERASE removes a whole coefficient row
only on an owned field. These rules preserve the representation at each event.

After all14,794 events, every frame equals the source's exit frame. The685-row
matrix is zero on all48 owned outputs and dirty input coefficients. On public
outputs it is the identity, with the specified111 shears from columns0..110 to
rows111..221. The checker compares every row exactly. Therefore the source local
endpoint holds as an operator on arbitrary functions, not only at sampled
addresses or on one scalar input vector. The forward source frames and the
involution formula also determine the adjoint; no finite-prime extrapolation is
used. Global composition and physical pricing are outside this local statement.

## Target normalizers and charges

For frames506 and508, both products of the emitted forward and inverse matrices
are exactly I. Conjugating P by these matrices gives a diagonal rank4 projection
or its complement. Both rank4 halves therefore have the stated coordinate
normalization. All entries fit the declared denominator4. The old matrices have
38 nonzero coefficients in both directions combined, used72 times on two address
halves: `38*72*2=5472`. The new matrices have76, used36 times on two halves:
`76*36*2=5472`. Total10,944 is the exact coefficient count, not a proof of its
physical tape tariff or the remaining global fees.

## A discriminating probe control

The two published address points have difference vectors whose first three
entries are (-22,-17,-13) and(-87,-60,-12). The vector
`v=(-192,289,-53,0,0,0,0,0)` is orthogonal to both. Put
`R=v v^T/123194`. It is a nonzero rank-one orthogonal projection. H_R is a
nonidentity involution and fixes both complete address points. The denominator
is invertible modulo101 and10201, so both modular calibrations also pass for
this false identity candidate. H_R changes the first coordinate unit vector.
The exact matrix/column test rejects it. The control supplies a concrete reason
to retain the algebraic obligations; it alleges no error in the source program.
