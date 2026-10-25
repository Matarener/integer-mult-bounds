# An unpaired exact ADDRESS normalizer and its common conjugate

Source pin: `20ecf2891d80b5acf18d980b2164fb44ea7faa90`. The scripts
`orthogonal_source_normalizer.py` and `conjugated_reflection.py` preserve
their native source/compiler hashes in their JSON receipts.

Credit and overlap: the generic even-linear lift/cocycle warning belongs
to Chris R / Clear1nsight's [PR3987](https://github.com/CrocSwap/integer-mult-bounds/pull/3987),
head `fc536202fdaa924158789a5ef59ac079bbe21922`. ToikY's
[PR4002](https://github.com/CrocSwap/integer-mult-bounds/pull/4002), head
`d593941ea0a4926021cba9d01fe60500579e464f`, gives exact normalized lifts,
signed words and mandatory anticommuting-C phase tags. The typed
`P_A Z_z` specialization here is not claimed as a new generic
normalization theorem. The distinct local obligation is its actual typed
source cut, full independent columns and inverse, native-cut rank,
fresh-progress tradeoff, and fully paid caller resource. The overlap was
read from the root's saved 10:32 board intake; no scientific pin is moved.

For j completed old planes, with p/q chunks of length f in each plane,
let D multiply an address by `i^(sum p bits - sum q bits)`. The actual
old native product is exactly

    G_old = product_(l=0..j-1) N_l = i^j D^-1 H_all D.

Here H_all is ordinary normalized Walsh. On one bit,
`Hp=e^(-i pi/4) S^-1 H S` and `Hq=e^(+i pi/4) S H S^-1`.
The non-Gaussian scalars cancel within every p/q pair; each N_l retains
its one literal i. Thus the displayed identity has no missing f phase.

For any binary orthogonal A (`A^T A=I`), its literal ADDRESS operator P_A
commutes with Walsh, as follows directly from the kernel `(-1)^(x.y)`.
Consequently `R_A=D^-1 P_A D` is an exact monomial normalizer of G_old
for every f. This establishes native admission with explicit Gaussian
phases, without relying on a finite tableau to certify a tensor family.

The useful choice needs three complete old planes. Order their six chunks
as `(p0,q0,p1,q1,p2,q2)`, and put

    v=(1,1,1,0,1,0),     A=I+v v^T.

Its weight is four, so `v^T v=0`, `A^2=A^T A=I`. The same binary map is
applied separately at every bit position. Write d(x) for the typed p-minus-q
weight and d_v for its restriction to the support of v. If `v.x=1`, then

    d(x)-d(Ax)=2 d_v(x)-2 = 0 mod 4;

if `v.x=0`, the difference is zero. Therefore the useful normalizer is
**literally bare ADDRESS**: `R_A=P_A`. No Gaussian phase scan is needed.
It is involutive and uses only completed old coordinates.

At stage j>=3, put Fpast equal to the completed fresh product and Fnew to
the product after the new fresh plane. Starting with two arbitrary fields
in the common Fpast chart, the literal word is

    source=N0 source; source=R source; target+=source;
    source=R^-1 source; source=Pj source; target=Tj target.

Because `[R,N0 Fpast]=0`, its full two-column matrix is exactly

    Fnew * [[Pj,0],[N0 R,I]].

The source code Pj, raw target coefficient, source cross coefficient, and
fresh coverage are retained, with phase. The inverse reverses the word,
uses target subtraction, and inverts each unary operator; it requires no
zero field or helper. Its bill is the original two native-2f queries, one
delivery ADD and one source ADDRESS, plus two ADDRESS R scans. Both new
scans are paid. This is a changed cross kernel, not a completed caller.

This R escapes the old whole-plane marked-residual proof. In the physical
X-character basis it takes the character with all q0 bits set to the
character with all p0,p1,p2 bits set. Thus a configuration with one marked
plane residual is sent to three marked residuals, for every f. The actual
64-point character sum at f=1 gives coefficient exactly +1, and the written
bitwise identity gives the all-f lift. Pair-gauge phases cannot remove
nonzero leakage.

By contrast the balanced support `(p0,q0,p1,q1)` is a negative control.
Its typed R is `Z_v P_A`; on characters it maps
`w -> w+(v.w+1)v`. With the residual mark `(p=0,q=1^f)`, it fixes an owner
inside its support and flips only unmarked virtual bits when the owner is
outside. It commutes with the marked C. The balanced reflection must not
be promoted as an escape. Its quartic kernel check is distinct from the
unpaired kernel; no claim `(N0 R)^2=-I` is made for the useful R.

There is a further cheaper conjugation resource. Let `A_f=N0 R N0^-1`.
The global factor in `N_f=i^(1-f) N_1^tensor f` cancels in conjugation,
so `A_f=A_1^tensor f` after bitwise regrouping. The one-bit A has native
B-rank two. Its exact selected-native lowering is saved in
`CONJUGATED-REFLECTION.json`; tensoring the literal monomial/native/
monomial equality implements A_f with one native-2f child and two fixed
bitwise monomial adapters, not two N queries. Its B-rank is exactly 2f,
and `A_f^2=I`. ADDRESS and quadratic Gaussian phase scans for both adapters
remain paid. The direct actual recipe checks cover f=1,2,3, including
global phase, while the tensor proof covers every f>=1.

In particular, with scalar bank shear E12 and
`B_R=E12 diag(I,R) E12^-1`,

    Ad_diag(N,N)(B_R) = E12 diag(I,A_f) E12^-1.

The right side costs one H2, two scalar ADD scans and the two monomial
adapters. Both independent bank columns and the literal inverse are
checked in the phase-sensitive tensor algebra. This does not itself
cancel a persistent factory or establish a supplier, stock surplus,
all-size transfer, precision bound, owner allocation, or tape bound.
