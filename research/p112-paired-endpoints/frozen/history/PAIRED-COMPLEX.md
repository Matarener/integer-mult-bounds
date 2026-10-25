# Paired complex endpoints and original-dimensional partners

Status: exact paired endpoint and signed B4 identities; an explicit original
9-dimensional partner geometry and individual dirty contact witnesses. A
compatible cheap whole local word, owner realization and improved supplier
remain open. The endpoint is not itself a cost improvement.

The scientific checkout pin is
`20ecf2891d80b5acf18d980b2164fb44ea7faa90`. The source port and signed recipe
files are under
`research/kernel92-frame-composition/vendor/pr531/inputs/data-base`:

| File | SHA256 |
|---|---|
|split-centres/CANONICAL-WORD.json.gz|addf598581d2a20e13d0c18110607515ad90b06125616a2349e53a47bb5b6c80|
|split-centres/GLOBAL-TEMPLATE.json.gz|5b913207775fcd87090cfa8776e8bd2bb872426923345fe1a1a4e1ea84bfae2c|
|work/complex-nine-native/DATA-PHASES.json|c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa|

## Chosen exact phase gauges

Write X_v for address translation by v in F2^n. The actual native line gate is

```
C_v^s = ((1+s i)I+(1-s i)X_v)/2,       s=+1 or-1.
```

It fixes the uniform vector and satisfies `(C_v^s)^2=X_v`. Let U be a
nondegenerate subspace with an orthonormal basis. Define a chosen phase
representative

```
T_U = H diag(i^wt(P_U x)) H,
```

where P_U is its binary orthogonal projector and H is normalized Walsh
Hadamard. For an orthonormal basis u_j this is the product of actual native
`C_(u_j)^(s_j)`, with s_j=+1 for wt(u_j)=1 mod4 and s_j=-1 for wt(u_j)=3 mod4.
Orthogonality cancels the quadratic cross terms in weight modulo4.

This T_U is not generally the literal retained compiler's `canonical_frame(U)`.
`canonical_gauge_audit.py` binds the difference explicitly with the actual
compiler
`research/kernel92-frame-composition/vendor/pr531/vendor/clifford/clifford_exact.py`,
SHA256 `2982ead07721e83358dc67c6f49c2b4c16a236a6bebdfd72f58221be1f5d0962`.
For all 112 partner pairs it emits456 rank0 left-monomial gauges, checks their
complete Clifford tableaus and exact Gaussian scalar phases, and lowers both
actual paired residuals to rank7 children. These are real wrappers whose
scalar/address work still has to be charged in a complete local word.

In particular the retained native source gate uses C_p with sign+1. If
wt(p)=3 mod4, passing to chosen T_P requires the explicit translation X_p.
`CANONICAL-GAUGES.json` records every such adapter; omission controls reject
the unadjusted phase. No canonical frame is silently identified with T_U.

## Paired residual and off-diagonal

Take orthogonal nondegenerate spaces P,Q,R with direct sum the full local
space. In the principal case dim(P)=dim(Q)=1 and dim(R)=7. Set source
entrance E_x=P, source terminal U_x=P+R=Q-perp, target entrance E_y=Q and
target terminal U_y=Q+R=P-perp. Then the actual chosen-gauge residuals are

```
T_(U_x) T_(E_x)^-1 = T_R,
T_(U_y) T_(E_y)^-1 = T_R.
```

Thus both wires have two genuine spectator directions. An exact dirty shear
would give the forward local block

```
T_R [[1,0],[K,1]],             K=T_Q T_P^-1.
```

Its off-diagonal is

```
T_(I-P) T_P^-1 = T_I T_P^-2 = T_I X_c(P),
```

independent of Q; c(P) is the characteristic vector, the sum of any
orthonormal basis. More generally `T_U^2=X_c(U)` and
`K^-1=X_(c(P)+c(Q)) K`. The backward shear therefore needs sign-1 and the
listed address-translation conjugation. Its reverse diagonal is still T_R.

These are operator identities on every input field, including arbitrary
source and target values. They supply no dirty helper word by themselves.

## Signed nine-call identity

Use four pairs. Let a forward local call add Kx to y, and a backward call add
`-K^-1 y` to x. The actual retained B4 recipe alternates forward/backward
orientations with bridge coefficients

```
1,-1,1,-1,1,-1,1,1,1.
```

It ends each pair at `(-K^-1 y,Kx)`. The usual pair swap/sign and terminal
translations X_c(P) on the forward route and X_c(Q) on the reverse route
convert both off-diagonal factors to T_(P+Q). The nine disjoint residual
directions then supply the remaining full transform.

`paired_endpoint.py` checks the B4 identity over Z[z,z^-1], and separately
executes exact Gaussian native convolution kernels in finite address models.
It checks local 9-dimensional projector kernels at every one of the112
retained ports, with common rank2 and rank3. Its complete native B4 models use
residual dimension1, so their global dimensions are11 and12, covering16,384
and32,768 independent input columns. They are explicit small native models,
not an execution of the actual65- or56-dimensional supplier. The written
operator identity applies to arbitrary numbers of orthogonal residual axes.
All scalar phases are retained; no projective equality is used.

Omitting the backward translation, reversing the wrong sign or omitting the
terminal translation produces an explicit nonzero Gaussian coefficient in
`ENDPOINT.json`. The Laurent model has separate sign/inverse controls.

## An order3 partner map within h=9

Let O have binary columns

```
451,454,453,31,55,47,248,440,376.
```

With c=511, exact enumeration checks

```
O^T O=I,       O^3=I,       O+O^T=I+c c^T.
```

All112 retained ports p satisfy p dot Op=0. Therefore Q_p=Op provides a
distinct orthogonal unit partner inside the original ambient dimension9.
It preserves the whole port Gram pattern. This avoids an uncharged
9-to10-dimensional helper-volume increase; it does not preserve the old
408-helper scalar construction.

For every one of the5,824 old correction edges p_s dot p_t=0, there is an
individually legal nondegenerate common contact frame F containing p_s and
Q_t and lying in `Q_s-perp intersect p_t-perp`. The exact rank histogram is

```
rank1:104,       rank2:2912,       rank3:2808.
```

When p_s dot Q_t=1, the two-dimensional span has radical p_s+Q_t. The emitted
rank3 extension must pair with that radical and leave Q_t non-characteristic;
both conditions are checked. Omitting the extension fails nondegeneracy.

For one isolated edge coefficient a and arbitrary helper d, a legal word is

```
y_t -= a*d at Q_t;
h += x_s; y_t += a*h; h -= x_s at F.
```

It restores h and adds a*x_s to y_t. The source and target share F, so this
is an actual all-input scalar contact. It is not a simultaneous construction
for many contacts: their shared source and target frame paths must nest.

The alternative helper contract `E=Q_t -> U=I-Q_s` has actual residual
`T_(Q_s+Q_t)^perp`, rank7, whenever Q_s and Q_t are orthogonal. This is a
genuine two-spectator helper boundary, but assigning a separate helper to every
edge is unaffordable even before source-access or decoder costs. Removing the
104 direct scalar contacts still leaves5,720 helpers of width7:

```
helper mass >= 5720*7 =40040;
data mass   = 224*7  = 1568;
total       >=41608 per local call.
```

At common rank2 the core dimension is65, productive W/call remains896/9,
and its zero-rate capacity is `65*896/9=58240/9`, about6,471.11. The literal
edge family fails this favorable fully charged screen before any COPY,
remainder or wrapper costs. A compressed factory is necessary; old helper
inventory cannot be relabeled as an edge implementation.

For one fixed O and a source-batched all-edge delivery/restore order, the
exact triangular-zero DP has maximum8 early-clean sources. Its witness is
`93,27,87,60,59,57,101,6`;259,479 states are checked. This is only that
source-batched model. Arbitrary edge interleaving, other partner maps and
changed correction factories are outside the result.

## Reproduce and unresolved interface

```sh
python3 -B .research-automation/runs/kappa-3605-successor-20261018T0940Z/major-frontier/helper-boundary/paired_endpoint.py
python3 -B .research-automation/runs/kappa-3605-successor-20261018T0940Z/major-frontier/helper-boundary/order3_geometry.py
python3 -B .research-automation/runs/kappa-3605-successor-20261018T0940Z/major-frontier/helper-boundary/canonical_gauge_audit.py
```

All output is retained beside the scripts. These are finite exhaustive checks
plus the written operator argument, not a proof-kernel theorem. A positive
cost claim still needs one ordinary dirty word with these entrance/terminal
gauges, source gathers, all canonical/native wrappers, changed compensation,
literal inverse cleanup, full histogram, whole-helper chronological owners,
physical stock, precision and all-size Fourier/outer transfer. None of those
unknown bills is treated as zero.

New material was prepared with substantial OpenAI Codex assistance. The
actual line/compiler conventions and B4 source recipe belong to the retained
PR425/433/523/531 and supplier ancestry, with notices retained in their
source files. No independent human or proof-kernel certification is claimed.
New material is Apache-2.0.
