# Full information kernel of the fixed coset block

This is a written linear-algebra proof whose explicit route and coefficient
premises are checked by finite exact computation. It is not a proof-assistant
certificate, a native collector or a multiplication theorem.

## Model and finite premises

Retain the selected calls-0/4 constant-payload model of PR3071/3291/3656. Let G
be the finite cover group acting regularly on its owners. The source at each
owner is an independent vector x(g) in F^112, with F=Q or C. Put

    Sx(g) = R x(g),
    Tx(d) = (1/4) sum_p R[:,p] x_p(d rho_p).

Each rho_p is an involution. Source variations are supported on B=aL, where
L=<rho_0 rho_6,rho_6 rho_85>. The entire later field Tx is required. The old
field Sx and additional scalar linear observations E_B x are available to
unrestricted global decoding. No other source-dependent state is available.
Ordinary target/helper dirt may be arbitrary but is equal in compared
executions. Native common-frame, source-adapter and constant-endpoint premises
are inherited; the equations above are the mathematical interface.

The new checker authenticates the selected-source loader and its complete
declared executable closure. From the literal selected source it obtains:

1. rank R=8, and all 112 routes are distinct involutions on 73 binary
   coordinates, preserving the active 17 coordinates and fixing the other 56.
2. |L|=4080. The exact full port partition by the right cosets L rho_p has
   one class D={0,6,85} and 109 singleton classes. Every one of the 6216
   unordered distinct port pairs is checked, including pairs outside D.
3. R_D has rank two and kernel span u_D=(1,-1,-1). Every singleton column is
   nonzero. Write u in F^112 for this vector extended by zero.

Right-coset equality is tested by rho_p rho_q in L. This uses the regular
group model and the involution premise; it is not equality of ordinary
73-dimensional payload operators in place of regular owners. The active
matrix restriction distinguishes actual group elements because its spectator
block is exactly the identity with no cross terms. No faithfulness claim
about a general group-algebra representation is needed.

PR3656's assertion that no other individual route belongs to the larger
three-generator group would not alone establish premise 2: two routes outside
that group could still have their product in L. The full pair classification
is the additional finite obligation closed here. Neither the support>=15
theorem nor a census of all dependent triples is needed for this new proof.

## Exact common kernel

For inputs supported on B, port p can reach exactly the outputs B rho_p.
These sets are equal within a right-coset class and disjoint between classes,
after the common left translation a. At any output belonging to a singleton
class, Tx(d)=0 forces its sole incoming scalar to vanish because the
associated R column is nonzero. Thus every non-D input coordinate vanishes,
with no restriction assumed on the amplitudes or on how many ports were
initially allowed.

At each g in B, Sx(g)=0 now gives x(g)=lambda(g)u. If d belongs to B rho_0,
its three incoming owners d rho_0,d rho_6,d rho_85 all lie in B. The rank-two
kernel condition for Tx(d)=0 gives

    lambda(d rho_0)=lambda(d rho_6)=lambda(d rho_85).

Taking d=g rho_0 shows invariance under right multiplication by
rho_0 rho_6 and rho_0 rho_85. These generate L, since
rho_0 rho_85=(rho_0 rho_6)(rho_6 rho_85). The right Cayley graph of B=aL
is therefore connected. Consequently lambda is constant on B.

Conversely, a constant multiple of u at every owner of B has zero S field.
Its three possible incoming terms occur together or not at all, and their
R columns sum with coefficients (1,-1,-1) to zero. It also has zero T field.
Therefore

    ker S_B intersect ker T_B = span{1_B tensor u},
    dim(ker S_B intersect ker T_B)=1.

This describes every complex or rational coefficient assignment on all
112*4080 source coordinates of the exact block. It holds on every left
translate aL. It does not determine the smallest support on other blocks,
unions of cosets, or a changed output reader.

## Sharp additional-information minimum and an attaining interface

Let V=ker S_B. Its dimension is 104*4080=424320, and the kernel of T_B|V has
dimension one. Hence rank(T_B|V)=424319. If E_B has fewer than 424319 scalar
linear rows, then dim ker(E_B|V)>1, so some v in that kernel has T_B v!=0.
The executions v and zero have identical S and E observations but different
required T fields. Arbitrary nonlinear postprocessing of the same
observations cannot distinguish them.

The bound is attainable for the declared pure source-field interface, not
only as an abstract rank formula. The source-bound pivot columns of R are

    P=(0,1,2,3,4,5,6,12).

They form an invertible 8-by-8 minor. Of the nonpivot coordinates, u has only
u_85=-1 nonzero. Fix any anchor g* in B and retain:

- x_p(g) for every g in B and all 103 ports p outside P union {85};
- x_85(g)-x_85(g*) for the 4079 nonanchor owners.

These are 420240+4079=424319 linear observations with coefficients 0,+1,-1.
Together with S they determine x modulo a common multiple of 1_B tensor u:
one can set the anchor gauge x_85(g*)=0, determine every nonpivot, and solve
the eight pivot coordinates at each owner. That gauge ambiguity is precisely
the common kernel and therefore does not change Tx.

Merely omitting one raw x_85 read from the complementary reads is insufficient.
It would leave a perturbation u at its single omitted owner unobserved, while its three
distinct routed outputs are nonzero. The differences above are essential.

The indistinguishability lower bound also applies with equal arbitrary dirty
inputs by fixing that dirt in the compared executions. Attainment assumes the
displayed source fields are actually available as the interface states. It
does not supply removal of unknown native dirt offsets, a reversible
implementation of E, literal helper restoration, or a physical decoder.
Nonlinear repair encodings or additional source-dependent state change the
observation model and are outside the result.

## Explicit conditional recursive-cost screen

The original eight rank-eight centre children per owner have rank mass
64*4080=261120. Grant deletion of that entire path, retain the original
width/stock/call normalization, and grant zero cost for every other
acquisition, decoder, routing, storage, restoration, precision and hosting
obligation. These are favorable allowances, not established implementations.

Consider the specified repair implementation that charges at least one
rank-one recursive child for each additional scalar observation. It needs at
least 424319 such children, an excess of 163199 rank units already at zero
saving. More generally, for 0<=a<=1 and the same width m and normalization,
its added unnormalized power sum is at least 424319, while the entire
removed power sum is 8*4080*8^(1-a)<=261120. Thus even the optimistic
replacement is strictly more expensive throughout that range.

At zero saving, a hypothetical per-coordinate rank-mass tariff c would need
c<261120/424319 before any positive overhead; or, at unit tariff, the joint
kernel would need dimension strictly greater than 40*4080=163200. Its actual
dimension is one. This is a decisive stop for the declared rank-one repair
architecture on this exact block. It is not a lower bound on every physical
way to acquire information: compressed higher-rank children, a different
normalization or reader, source-consuming interfaces and other blocks need
their own complete costs. No supplier or kappa improvement is established.

## Credit

Matarener (donor Mark), with Claude assistance, supplied PR3656's coset,
constant witness and full-kernel question. Sagar Thakrar/PR3291 supplied the
authenticated loader; Ross Richardson/PR3071 supplied the observation model
and independent extraction. The retained source lineage includes dcharb78,
Gonzalo Mier, Sudarsh Chaturvedi, Aaron Wang/navinor, ywz65 and the selected
construction authors. This proof and checker were developed by Ross
Richardson with substantial OpenAI Codex GPT-6.1 Sol assistance, including
separate mathematical specialists. These are not independent human reviews.
Apache-2.0.
