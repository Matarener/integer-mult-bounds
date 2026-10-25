# Completing the persistent bank once reduces the matched repair from 3N to 2N

## Exact same prepared physical boundary

This is a refinement of PR3978, head48e2e44d8785be8204d8c4b719850332f4f9abe0.
Its exact PROOF and RESULT are exported unchanged in inputs/. The proposed
chronological global producer remains unproved. We change only the repair at
that predecessor's explicitly prepared cut, with fixed named X/Y owners and
the same two dirty helper banks. No new payload code, changed source input,
free bank exchange or improved global caller is asserted.

Write A_r=A tensor I, A_c=I tensor A for the canonical P104 A=G/2, and
N=104^2=10816. Let U(Q)=[[I,Q],[0,I]], S(Q)=[[I,0],[Q,I]], and
M=U(-A_c)S(A_r). As in3978, original physical input (x,y) is normalized by
u=T^-1 x, with T=diag(C_Uij), K=T^-1, F=C_I and Gphys=diag(F,FK).
The prepared input is Gphys M(u,y); the required output is Gphys J(u,y),
where J=[[0,-I],[I,0]]. This retains the original input tags. It does not
replace the physical source x by the logical normalized source u.

The common-coordinate compensator is

    C = J M^-1 = [[A_r,A_r A_c-I],[I,A_c]]
      = U(A_r-I) S(I) U(A_c-I).

Set D_T=diag(I,T), D_K=diag(I,K). The predecessor's exact physical map is

    Cphys = D_K C D_T
          = U((A_r-I)T) S(K) U((A_c-I)T).

The new word executes the LEFT expression in chronological order:
(1) apply T in place to every persistent Y; (2) execute the three scalar
layers of C in the common F chart; (3) apply K in place to every resulting Y.
Because T(FK)=F and K F=FK, the entrance and exit charts match literally.
The original Y payload need not survive until step3: C is intentionally a
mixed two-bank map. The proof uses only TK=KT=I and the common F commutation;
A_r/A_c are not commuted through T. Both dirty banks are untouched by this
repair. Completion of their preceding paths is still a prepared-cut premise.

The free noncommutative checker verifies the matched endpoint, including
Gphys and diag(K,I) on the original physical input. A separate implementation
compares all columns of old and new maps at varying noncommuting Gaussian
charts. Omitting either boundary conversion or exchanging their order fails.

## Exact boundary primitives and phases

The canonical native certificate supplies the104 odd distinct physical root
labels r_i. The line generators u_ij=r_i tensor r_j are10816 distinct norm-one
81-bit labels. For nonzero u choose a set-bit pivot p, e=2^p, and define

    P_u(a)=a + a_p (u+e)       over F2.

P_u is an involutive invertible binary basis map and P_u(e)=u. Its address
permutation has zero phase. With the retained positive one-coordinate C_p,

    T_u=P_u C_p P_u,
    K_u=X_u P_u C_p P_u.

The finite f=1 formula C_u=((1+i)I+(1-i)X_u)/2 verifies the exact phase:
C_u^2=X_u and C_u^-1=X_u C_u. This formula is used only as a bounded
operator check, not as an implementation that expands a large native child.
The independent checker compares every Gaussian matrix column for all seven
nonzero three-bit u, both directions, and rejects a global phase mutation.
The primary checks P_u^2=I on all81 basis vectors for every actual product
line (876096 binary basis checks).

For f parallel address columns the implementation lifts the outer basis
permutation as P_u tensor I_f and RETAINS one positive C_f child on the
p-coordinate block. The inverse uses the corresponding translation monomial
on all f columns. Tensoring the exact operator identity establishes this
ideal native recipe without expanding2^f terms. Each conversion acts on the
same full physical array volume as3978's copied transform; there is no small-
volume donor shortcut. Binary basis permutation, translation, scalar and
control passes remain paid physical work. This algebraic lifting is not
signed-floor, precision, recovery or recursive supplier admission.

## Complete matched operation invoice

In each upper scalar layer Q=A_axis-I has4992 signed half coefficients per
fiber and zero diagonal. For each donor in the persistent Y bank: halve it,
perform all signed unit additions to the distinct X bank, and double it back
before advancing to the next donor. The lower layer is one X-to-Y unit add
per data position. The second upper layer reads the updated Y fields. No
new initialization, private copy or erasure is needed. All donor rescalings
are restored; the intended mixed endpoint is still C, not the original Y.
Exact integer rows check every208 local input column of this word, and the
separate Gaussian checker executes both upper rescaling words around the
lower layer, with an unrestored-donor failure control.

| Primitive | PR3978 copied route | New persistent full-chart route |
|---|---:|---:|
| Positive rank-one transforms |32448 = 3N|21632 = 2N|
| Unit array ADD/SUB |1049152|1049152|
| Halves |21632 on dead private donors|21632 on persistent donors|
| Restoring doubles |0|21632|
| Private initialization/copy/erase |32448 each|0|
| Peak additional private arrays |1|0|

Thus the positive-child rank bill decreases by10816, exactly one third of
that particular predecessor route. This is a matched prepared-cut operation
comparison, not a scalar/runtime optimum or a lower bound on arbitrary native
factorizations. The explicit new boundary recipes additionally have43264
binary basis permutation passes and10816 inverse translation passes, without
claiming those are physical-cost minima. All scalar additions and rescalings
remain finite paid work, not zero because they carry no positive child rank.

In the declared chart ledger, the new entrance T contributes+N persistent
progress and the final K contributes-N. Net progress remains zero, just as
3978's repair. The in-place route therefore cannot claim the initial lift as
new endpoint progress while dropping the final descent from its bill.

## Complete conditional gate and stop

Retain3978/3954's named global hypotheses:104 row and104 column bare calls,
m=81, W=36608 persistent roles, N initial rank-one anchors; each bare local
call has mass2368 and persistent progress at most2312, even granting the
unproved opposite orientation. All residual native rank tariff is at least
net persistent progress, ranks<=81 and equal physical-role volume1/W.
The most favorable bare bill is2966080 against capacity2965248.
Replacing only the old prepared-cut repair gives

    old lower bill = 2966080+32448 = 2998528,
    new lower bill = 2966080+21632 = 2987712,
    new excess     = 22464 > 0.

All omitted actual preparation, interstage alignment, wrappers, scalar passes,
routing/holding/control/tapes, finite-width/precision/recovery and admission
costs remain unknown nonnegative additions. For0<=a<1, (r/81)^(1-a)>=r/81,
so this favorable complete native gate still fails throughout that range.
Stop dependent native/global construction for the unchanged scaffold.
No selected-frontier or kappa update follows.

A changed raw all-FULL producer, including the new late-delivery work, requires
its own chronological input/exit tags and progress bound. In particular, a
single-axis route returning F T^-1 x does not implement F x on the original
physical source. The apparent anchor credit cannot be claimed by renaming
that normalized field. No such changed producer is incorporated here.

## Remaining obligation and credit

The useful successor is an actual producer that permits one boundary pass to
be absorbed while retaining all original physical inputs, owner returns,
arbitrary dirty helpers and a favorable complete gate. Start with one shared
owner at an actual adjacent call boundary; do not infer availability from the
symbolic prepared cut. This study supplies a cheaper target repair only.

The comparison and original compensator retain Chris R/Clear1nsight's3978
credit, following3954/3940/3882 and the canonical copied-center caller.
Rohan Arun/#1972 owns the native-word/dirty source, Chafik Boukhalfa/#1991 its
native realization, Adam Gall/#1940 delivery, and the underlying E8, compiler,
phase and caller authors retain the attribution listed in README. Prepared
with substantial OpenAI Codex multi-agent assistance. Apache-2.0.
