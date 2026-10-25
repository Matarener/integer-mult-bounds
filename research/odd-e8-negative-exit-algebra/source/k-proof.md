# A complete native K primitive for every odd-E8 product cube

This constructs the whole block-diagonal three-factor K service, including
the ordinary wrappers that normalize its actual supplied-line interface to
arbitrary ground-chart inputs. It does not produce the cross-cube H service,
install the low-rank F3 decoder, complete an outer caller or claim a kappa.

The construction is a fixed finite structured word for all 14^3 cubes.
`core.calculate((a,b,c))` emits its exact literal instance for any cube.
The default finite phase replay fully emits cube(0,0,0); it does not pretend
to have expanded all 106,774,528 scalar ADDs or executed every phase instance.
The all-family result follows from the generic frame/phase proof below and
the independent all-2,744-cube geometry checks in `family_geometry.py`.

Credits remain with Ali Romman's #5439 odd-E8 geometry, the P112/E8 data,
the PR5464 polarized native phase tools, the original native/Clifford
compiler lineage, and the coded-native-caller real centralizing normalizers.
This assembly and its explicit whole-K contract used substantial OpenAI
Codex assistance. New material is Apache-2.0. No independent human or
proof-kernel acceptance is asserted.

## 1. Actual fields, scalar coefficients and global coordinates

The pinned NORMALIZERS data supply 112 distinct binary q labels and their
root columns. The roots split into fourteen eight-root sign cubes. For a
cube b, put B_b=M_b M_b^T/4 and K_b=I-B_b. Exact rational checks give
K_b^2=I; each row has four entries +-1/2, all joining opposite selector
parities. The two four-port classes each span a three-space with pairing
rank one, and the two three-spaces are orthogonal.

A product cube has 512 owners. Define

    K_odd=(K1+K2+K3-K1 K2 K3)/2.

The three factor matrices commute and square to I. Expanding the square
of their displayed majority polynomial gives I. The scalar K_odd is also
symmetric. Every row has twelve distinct one-factor entries of magnitude
1/4 and sixty-four distinct three-factor entries of magnitude 1/16.
The two support sets are disjoint since each K_b has zero diagonal.
Every nonzero entry reverses total selector parity. Thus each row has
exactly 76 nonzero coefficients and their absolute sum is seven.

The actual product labels are concatenated triples in F2^27. Their global
span U is the 25-space of equal three-block parities. The code records an
explicit orthonormal basis of U, and takes physical coordinates by dotting
against it. This is one global I25 realization, shared by all cubes; no
local-20-to-global-25 free adapter is introduced. Every port has norm one
and differs from the characteristic vector of U. The latter is the raw
all-ones27 vector, whereas each base label has weight three or seven.

For every product cube the two 256-port parity classes span S0,S1 with

    dim S0=dim S1=9,   S0 perpendicular S1,
    rank(B|S0)=rank(B|S1)=1,   dim rad(S0)=dim rad(S1)=8.

Their joint span has dimension ten. `family_geometry.py` checks all
1,404,928 actual norm-one noncharacteristic labels, all 5,488 nine-space
classes and all opposite-reader/source-basis incidences. The restricted
characteristic issue is explicit: every odd q represents the characteristic
functional within S9. The construction never requires a noncharacteristic
vector inside S9, and never tries to orthonormalize this degenerate S9.

Use two independent fields X_p,Y_p per port p. There are no other independent
fields, no owned full-field scratch, no COPY and no CLEAR. Across the family
the product cubes partition the actual owner indices, so no independent
input is duplicated or identified between cube instances.

## 2. Canonical frames for arbitrary degenerate subspaces

All operator products below act rightmost first. The primitive convention is

    C_q=((1+i)I+(1-i)X_q)/2.

Write R=C_[0,25), Q=C_0 and D=C_[1,25), so R=DQ. If the columns of G are
any full binary basis and A=G^-1, put

    K_G=D_J P_G,   J=I+A^T A.

Here the diagonal uses the retained compiler's Z4 quadratic convention.
For the first r columns spanning S, the actual native frame is

    Phi_(G,r)=K_G C_[0,r) K_G^-1.

It is not necessary for the restricted form on S to be nondegenerate.
Its binary symplectic action sends the Z Lagrangian to

    L_S={(x,z): x in S and z+x in S-perp}.

To check this directly, let B=G P_r G^T. On a Z input z the output X part
is x=Bz, and its Z part is z+JBz. Since J=I+G^-T G^-1, the vector formed
by adding x to that output Z part is z+G^-T G^-1 x. Its dot product with
every first-r basis column vanishes. Dimensions give exactly L_S.
The symplectic action of C, and therefore of Phi, is an involution;
the inverse frame has the same Lagrangian image.

Consequently two constructions of the same S differ by a monomial map.
If S is contained in T, their transition has Gaussian rank

    25-dim(L_S intersect L_T)=dim T-dim S.

Indeed their intersection has x in S and z+x in T-perp, hence dimension
dim S+25-dim T. This proves all required rank and zero-rank statements
for every actual cube, not only for the root instance's tableaux.

## 3. Literal source and reader paths

Fix a source parity class S9. All sources in it and all opposite readers
will meet at one and the same literal canonical Phi_S9 word. Each source
q belongs to S9. Its line-to-S9 path costs H8. To emit this path, choose
a full flag whose first vector is q and first nine vectors span S9.
Monomial gauges connect its one- and nine-dimensional frames to the
declared canonical frames, and the only Gaussian child is C_[1,9).

A reader q is orthogonal to S9 and has norm one. Therefore it is outside
S9 and its q-perp24 contains S9. The reader starts at ground, reaches
Phi_S9 by one H9, and leaves it by one H15 to a full flag beginning with
the identical ordered S9 basis and spanning that actual q-perp24.
The emitted word supplies every reader's actual endpoint flag.

The source leaves S9 for canonical full R by one H16. Let

    T_G=R K_G R^-1.

The source-exit word executes K_G^-1, then C_[9,25), then T_G, since

    R Phi_S9^-1=T_G C_[9,25) K_G^-1.

No extra Gaussian is hidden in T_G; its exact monomial phase is given
in section 4. All other gauges are compiled as P/D/X/phase-only words.

At the common cut, directly execute Y_r += K_odd[r,s] X_s for every
nonzero scalar coefficient. The two main banks are independent. X is
never modified by these ADDs, so every source read uses its original
geometric logical value. Every reader retains its arbitrary old value
with coefficient one. There is no need for a rank-one cache or any
owned helper, even though the scalar matrix between the classes is full
rank. The two parity directions use disjoint source/reader field sets
and are executed separately. Every ADD is at an actually identical frame,
not merely between containing or cross-orthogonal subspaces.

The geometric endpoint is exactly

    X_s: Phi_[q_s] u_s -> R u_s,
    Y_r: v_r -> Phi_(q_r-perp)(v_r+sum_s K_odd[r,s]u_s).

Every 512-port cube thus uses 512 children of each of widths 8,9,15,16,
and 38,912 ordinary scalar ADDs, with no helper or owned field.

## 4. Absolute phases without exponential dense columns

The retained signed tableau fixes a Clifford operator up to scalar.
Every low-rank monomial gauge is checked with an exact sparse
Gaussian-integer zero-column evaluation that fixes this scalar as well.
For same-S9 gauges the sparse support remains at most 512: after changing
coordinates, both rank-nine Gaussian portions act inside the same prefix.
The normalization gauges below need at most two one-axis Gaussians.

For any native full basis G, let a_j=G^-1 e_j and set

    d_j=floor(wt(a_j)/2) mod 2.

If q_J is the diagonal's actual Z4 phase, XOR Hamming-weight expansion
modulo four gives

    q_J(y)+wt(G^-1 y)=wt(y)+2d.y mod4.

The quadratic cross terms cancel. For each j, its remaining linear
coefficient is alpha_j+wt(a_j), with alpha_j=(1+wt(a_j)) mod2 in {0,1};
this equals 1+2d_j modulo four. With a=(1-i)/2,

    R^-1|0>=a^25 sum_x i^wt(x)|x>,
    K_G R^-1|0>=Z_d R^-1|0>,
    T_G|0>=(-i)^wt(d)|d>.

Furthermore T_G is monomial: R^-1 takes Z Paulis to the diagonal
Lagrangian {(z,z)}, K_G takes it to {(Gz,Gz)}, and R takes it back to
Z Paulis. Its exact signed tableau plus this absolutely normalized
column determines the emitted P/D/X/phase word universally. No 2^25
state is allocated. `frame_tools.py` retains this analytic anchor.

These generic arguments prove the compiler construction for every cube
and every flag satisfying the verified geometry. Default execution fully
corroborates all actual root-case gauges, including 512 reader-output
full-basis anchors, rather than sampling a few field pairs.

## 5. Real normalizers and virtual-Q entry

The geometric input line service above is not silently assumed free in
the normalized native F_K. We explicitly wrap arbitrary ground inputs.
For each physical q, construct an orthogonal binary G_i taking e0 to q.
If q_0=0 use the even transvection T_(e0+q). Otherwise choose j>0 with
q_j=0 and use T_(ej+q) T_(e0+ej). Such j exists because q is not the
ambient characteristic vector.

For row j of G_i put z_j=(wt(row_j)-1)/2 modulo two and define

    L_i=Z_z P_Gi.

This is a real signed orthogonal monomial. Orthogonality cancels every
quadratic cross coefficient in the weight identity

    wt(G_i^-1 x)-wt(x)=2z.x mod4.

It follows that L_i R L_i^-1=R exactly, including absolute phase.
Checking orthogonality and the 25 linear coefficients proves the weight
identity for all 2^25 addresses; no address sampling is used.

The actual ordinary normalized wrappers are

    input X:  Phi_[q_i] L_i Q^-1,
    input Y:  L_i,
    output X: L_i^-1,
    output Y: D L_i^-1 Phi_(q_i-perp)^-1.

Their monomiality follows from the corresponding line/hyperplane
Lagrangian incidences. Input X's literal defining word has two one-axis
Gaussian factors and is compiled with exact sparse absolute phase.
It is emitted and executed as an ordinary monomial; Q^-1 is virtual
inside this identity, not an additional unpriced Gaussian instruction.

For the potentially high-rank reader-output wrapper let its endpoint
flag be Phi_V=K_v C_[0,24) K_v^-1. The exact low-rank expression is

    D L_i^-1 Phi_V^-1
      =Q^-1 L_i^-1 T_v C_24 K_v^-1,
    T_v=R K_v R^-1.

This follows by C_[0,24)^-1=R^-1 C_24 and [L_i,R]=0. The right side
has only two one-axis Gaussian factors plus phase-complete monomials.
Its signed tableau is checked against the defining left side, and its
absolute phase is compiled from the low-rank expression. Thus no
rank-24 dense zero column is needed and no projective phase is discarded.

## 6. Normalized arbitrary-input endpoint

Let x_i,y_i be the actual independent ground inputs. After input wrappers
the geometric logical values are exactly

    u_i=L_i Q^-1 x_i,     v_i=L_i y_i.

These are invertible functions of the original independent inputs; they
are not being renamed originals or assumed zero. The actual emitted
input-X monomial already puts its physical field at Phi_[q_i]u_i.

Source output followed by its wrapper is

    L_i^-1 R L_i Q^-1 x_i = D x_i.

Reader output followed by its wrapper is

    D y_i + sum_j K_odd[i,j] D L_i^-1 L_j Q^-1 x_j.

Define, at actual field width f,

    (C_K,f)_ij=K_odd[i,j] L_i,f^-1 L_j,f.

The complete normalized operator is therefore

    F_K=diag(D,D) L(C_K Q^-1).

K_odd is a real symmetric involution and the L_i are real orthogonal.
Thus C_K^T=C_K, C_K^2=I and [C_K,R]=0. These facts follow by actual
operator similarity. They do not tensor the whole owner matrix:
scalar K_odd coefficients are applied once, and cancellation of adjacent
L_j,f L_j,f^-1 proves the square identity at every positive width.

All 1,024 geometric original columns are explicitly interpreted in the
root-case word; the incoming-column and outgoing-row factor identities
above imply all 38,912 nonzero normalized operator blocks at once. No
sampling of cross-owner physical operators is used.

The normalized source outputs are autonomous rank-24 D transforms of
their original inputs. Reader outputs remain the specified triangular
coupled transforms. The service is invertible and retains every original
input; a complete outer Gaussian caller and its larger productive jobs
must still be supplied before using any whole-caller target profile.

## 7. All positive widths and complete local accounting

Every single-copy identity includes its absolute phase. Tensor it
columnwise to f positive address columns. P and X lift as binary block
maps, D sums its Z4 phase over the columns, and a single-copy phase theta
becomes i^(f theta). Scalar owner coefficients are applied once per field.
No width-one sum relation has been extrapolated by taking a tensor power
of a sum. This proves the actual physical word and F_K endpoint for every f.

The normalized root case has 512 fields of each X/Y role and profile

    paid {8:512,9:512,15:512,16:512},
    ordinary {ADD:38912,P:7680,D:7680,X:3072,phase:3072}.

There are 42 literal monomial primitives and 76 scalar ADDs per owner,
in addition to its four correctly charged Gaussian paths. These are
nonrecursive work, not zero-work operations. Their address movement,
storage, precision and tape price remain eventual caller obligations.
No helper input, helper target, owned field, COPY or CLEAR is introduced.

For v=112^3=1,404,928, concatenate the cube words in lexicographic order.
The whole-family profiles are

    paid {8:v,9:v,15:v,16:v},
    ordinary {ADD:76v,P:15v,D:15v,X:6v,phase:6v}.

The number of actual main inputs is 2v=2,809,856. The Gaussian rank mass
is 48v. No smaller pairing rank is substituted for any physical child.

At geometric logical opcode boundaries each source row has l1 one and
each reader has its old value plus distinct source coefficients of total
l1 seven. Hence all prefix row l1 values are at most eight, and scalar
denominator exponent is at most four. Physical charts and wrappers are
unitary, so independent input norm at most M gives field norms at most
M for sources and 8M for readers. This is a finite local growth constant,
not a complete recursive rounding-error, precision or outer-admission bill.

Actual mutation controls detect a global phase i despite an identical
signed tableau, a wrong parity S9 frame (requiring rank-two transport),
and omission of a literal K ADD (changing an independent input column).

## 8. Remaining scope

This fills the local K-native construction gate. It does not provide H,
remove H by a global basis change, make the F3 factor totals freely
available, prove a decoder/reader chronology, or close the mixed-Q
E=I-H interface. No whole-caller profit or kappa improvement is claimed.
The earlier planning profile and separated-helper obstruction cannot
be reused as a completed budget for this changed primitive.
