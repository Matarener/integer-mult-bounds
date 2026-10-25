# Exact root closure, cube cover and Weyl physical lift

Let M112 be the retained actual integer root rows, all norm squared4. Add
r_(112+i)=2e_i. The supplied binary labels q for the additional roots are
7,25,42,52,76,82,97,127. The verifier checks every14,400 pair: all q are
norm one and distinct, and for i!=j, real root inner product nonzero is
equivalent to binary q_i.q_j=0. All real roots have squared norm4.

For each actual root r, reflection sends s to s-(s.r)r/2. Every coefficient
is integral, and the reflected vector equals one of the120 retained roots
up to sign. The120 projective root actions are exact involutory permutations.
The complete Gram M^T M is60I8, checked on all64 entries.

An original eight-root support cube has C_b=M_b M_b^T/4 with C_b^2=2C_b.
Reflection preserves its Gram up to root row signs, preserving this identity.
The verifier nevertheless checks every9450 orbit cube directly. Trace C_b=8
then gives rank4. K_b=I-C_b is a symmetric involution, zero diagonal, with
four signed-half entries per row, whose graph is complete bipartite4-by4.
For both actual q parity classes it verifies rank3 of the binary span and
orthogonality of the two spans. It does not assume that a Weyl transformation
preserves the old four-coordinate support grouping.

Algorithm X uses the finite9450-cube orbit and searches the smallest
uncovered root column. The emitted15-cube cover is verified by sorting all
120 covered port indices and checking each appears once. Each selected cube
also retains its root-reflection route from an original cube. No search
failure or floating point judgment is involved: a full exact cover is output.

For every selected block, C_b M_b=2M_b, hence K_b M_b=-M_b. Concatenating
blocks gives KM=-M. Since K is symmetric, KC=CK=-C. Together with K^2=I
and C^2=15C this proves

    (K+C/14)(K+C)=I.

The program independently checks all14,400 actual K^2 and KC blocks and all
960 KM entries. This changes the whole owner scalar code; it does not make
Q^-1 E Q ordinary or solve the negative terminal bank.

For the physical lift put c=511 and u=q_r+c. Every actual u has weight2 or6.
The binary transvection O_r=I+u u^T is orthogonal and maps

    q_s -> q_s+(1+q_s.q_r)(q_r+c),

which is checked against every actual real-root permutation action. If
u.x=1, its Hamming-weight change is wt(u)-2wt(u&x), divisible by4 because
wt(u)=2 mod4 and the overlap is odd. Otherwise x is unchanged. Thus O_r
preserves weight modulo4 at every address. The exact full Gaussian kernel
only depends on the weight of the address difference modulo4, so the
ordinary permutation P(O_r) commutes with R9 including scalar phase.
All61,440 address congruences,120 signed tableaux and120 exact zero columns
are checked with the retained Gaussian-dyadic Clifford compiler.

To reach a new axis root choose an actual old root s and reflection r with
s_r(s)=the new root up to sign. Set L_new=P(O_r)L_old. This is an emitted
ordinary word, commutes with R9 exactly and maps the central line to the
new q line. For canonical own-line Phi_q and hyperplane Phi_(q-perp), the
four forward wrappers are

    Phi_q L Q^-1,  L,  L^-1,  D L^-1 Phi_(q-perp)^-1.

Each is compiled to literal P/D/X/phase, with its signed tableau and
absolute zero column checked. There is no hidden paid Gaussian in a wrapper.

Every single-address-column identity lifts columnwise to all positive field
widths; a scalar phase i^theta becomes i^(f theta). Each owner coefficient
is applied once outside this tensor power. Nothing tensors an owner sum.
The explicit cube partition supplies the generic source line->S3->R and
reader ground->S3->q-perp flags, with Gaussian ranks2,6,3,5 respectively.
Actual phase-native emission is a separate successor package.
