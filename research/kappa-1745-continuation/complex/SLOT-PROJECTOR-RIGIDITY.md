# Why changing only the twenty idle frames cannot improve their ranks

This is a scoped obstruction for the retained eight-stream, nine-local-call
operator. It covers simultaneous new orthonormal bases, including replacements
whose cardinalities differ by two. It does not cover new idle event positions,
a changed scalar or local graph, changed helper widths, or additional nonlinear
Fourier-phase corrections.

The operator and event schedule are those authenticated by PR3187 and PR3296,
and rebound to the disputed PR3955 chain by PR4046. The exact source is pinned
in `SLOT-PROJECTOR-RIGIDITY.json`. No supplier or new kappa is claimed here.

## Statement

Retain the chronological scalar/local graph on eight streams and its twenty
idle slots. At slot c, replace the original orthonormal frame A_c by any other
orthonormal frame B_c in F2^73. All simultaneous replacements are allowed.
Keep each local call's normalized operator, but allow inserted Fourier
translations `(-1)^(t dot z)` and changes of scalar signs throughout the graph.
Require the final full operator to equal the original operator for every
Fourier character z, up to final Fourier translations and scalar signs.

Then the orthogonal projector of B_c equals that of A_c for every slot c.
In particular their ranks agree. If the hosted widths and child assignments
are fixed, the idle residual ranks therefore agree as well.

The statement permits the two original zero-rank slots as possible replacement
slots. The certificate shows that they too must retain their zero projector.

## The exact finite certificate

Set all native phase factors to one and reduce scalar coefficients modulo two.
The retained nine local calls become elementary shears on their declared pair;
the nine bridges become two shears each, and the terminal signed exchanges
become swaps. Their product is the 8 by 8 identity over F2.

For every idle slot c, introduce a formal first-order phase on its one stream.
Propagate that perturbation through the entire scalar graph. Its resulting
8 by 8 matrix is a column K_c of a linear map

`K : F2^20 -> Mat_8(F2)`.

`slot_projector_rigidity.py` constructs these twenty columns directly from the
literal execution schedule. It supplies an explicit 20 by 64 left inverse and
checks all 400 entries of `left_inverse * K = I_20`. Thus K is injective. The
receipt records both matrices as bitsets and the exact normalized event list;
the proof does not depend on a floating rank computation or search outcome.

## First order: each slot must preserve its XOR vector

Work in the Gaussian-integer quotient

`R = Z[i] / (i-1)^3`.

Writing epsilon=i-1, the exact Gaussian-integer identity is
`epsilon^2 = -2i`. Because i is a unit, `epsilon^3=-2i epsilon=0` implies
`2 epsilon=0` in R. Multiplying this last relation by epsilon gives
`2 epsilon^2=-4i=0`, so `4=0`. Therefore
`epsilon^2=-2(1+epsilon)=-2=2` in R. Modulo epsilon, every native phase and
every scalar sign is one.

An orthonormal frame A has Fourier phase

`i^Q_A(z)`, where `Q_A(z) = sum_(a in A) (a dot z mod2) mod4`.

Modulo epsilon^2, its phase is `1 + epsilon * Q_A(z) mod2`. The change at
slot c is therefore epsilon times

`(xor A_c xor xor B_c) dot z`.

Inserted translations and scalar sign changes are trivial at this order.
The final operator equality implies that K applied to these twenty linear
functions is zero. Injectivity gives `xor A_c = xor B_c` at every slot.

## Second order: each slot must preserve its projector

The first-order conclusion makes `Q_Bc(z)-Q_Ac(z)` even for every character:
their low binary phase bits agree separately at each slot. Write half their
difference modulo two as f_c(z); equivalently it is the difference of their
second binary phase bits `floor(Q/2) mod2`. It is a polynomial of degree at most two:
the integer expansion of a parity has only its linear and quadratic terms
remaining modulo four.

The relative phase change is now `1 + epsilon^2 f_c(z)`. Any product of this
change with a positive-order term of another native phase vanishes modulo
epsilon^3. Consequently its propagation is governed by the same K, namely the
zeroth-order scalar graph. Simultaneous slot changes have no cross terms at
this order.

Inserted translations contribute linear polynomials in z at this order;
scalar signs contribute constants. Their positions may be arbitrary. They
cannot cancel a nonzero quadratic coefficient. Equating each quadratic
coefficient in the final operator therefore gives

`K * [quadratic coefficient of f_c]_c = 0`.

Injectivity implies that each f_c has no quadratic part. Hence the two phase
quadratic forms at each slot have the same polarization. For an orthonormal
frame,

`Q_A(z+w)-Q_A(z)-Q_A(w) = 2 z^T P_A w mod4`,

where `P_A = sum_(a in A) a a^T` over F2. It follows that
`P_Ac = P_Bc`. Since the vectors are orthonormal, P_A is the projector onto
their span and has rank |A|. The two slot ranks must therefore agree.

## A control that defeats first order but fails second order

The orthonormal frames `{e1,e2,e3}` and `{e1+e2+e3}` have the same XOR vector
and different ranks, three and one. At z=e1+e2, their phase exponents are two
and zero. Their projectors are respectively the 3 by 3 identity and the all-ones
matrix. The supplied control verifies these values exactly. It demonstrates
why the first-order XOR condition alone was insufficient and why the
second-order condition is material.

## What a successful geometry change must now alter

The obstruction depends on the exact slot-to-stream/time map and normalized
scalar/local graph. A common phase on all eight streams commutes through every
scalar shear; new synchronized slots can therefore introduce relations absent
from the current injective map. Moving such a phase out of the present local
calls must still account for their source/target frames, helper widths and any
inverse transforms needed to complete the supplier.

A nonlinear Fourier correction could also change the second-order accounting.
It must be supplied as an actual native operation with its cost. A quadratic
phase is not an ordinary translation and cannot be priced as one by declaration.
The local call phases and shear coefficients are fixed apart from signs.
Replacing a shear coefficient by a multiple of i is outside this statement;
it creates a first-order perturbation in addition to the twenty slot columns.

Credits remain with Nick Petalas, Matarener, Erwan/Claude, Rohan Arun and the
original local/controller/owner construction lineage. This new finite
certificate and argument use substantial OpenAI assistance. Apache-2.0.
