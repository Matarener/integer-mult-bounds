# Heterogeneous orbit blocks and partial native fusion

This is a scoped theorem about exact Clifford tensor operators and their
volume-weighted recursive charge. It combines operator support with convexity.
It does not bound arbitrary sparse programs, and does not admit a new supplier.

## 1. Source boundary and explicit operation contract

The selected forward events 12806, 12807 and 13402 on target195/donor521 have
the physical boundary

    (x,y) -> (C_f x + B_f y/2, y),   C_f = B_f A_f.

As independently decoded in PR3989 and PR4009, the literal rank-one operators
are A=aI+bR and B=aI+bP, where a=(1+i)/2, b=(1-i)/2,

    R e_t = i^3 (-1)^parity(14&t) e_(t xor30),
    P e_t =     (-1)^parity(96&t) e_(t xor224).

Both Paulis square to I and commute. Their independent translations have128
joint orbits of size4 among512 coordinates. The chart R^r P^p e_t is monomial,
including its phase, and identifies A,B with independent two-point kernels.
The tensor lift has joint orbits of size4^f; identity spectators are permitted.
Every C_f column is nonzero at all4^f coordinates of its joint orbit.

Partition the full V coordinates into disjoint fixed blocks of volumes v_j,
each a union of joint orbits. Thus sum v_j=V. Blocks and all schedules may
depend on f but not on input values. On block j choose a subset K_j of the f
P directions, with k_j=|K_j|. Write B_K for their kernel product and B_J for
the complementary product. The proposed native program is precisely:

    x <- (A_f B_K)x        [normalized rank f+k_j, volume v_j]
    (x,y,z) <- S_K(x,y,z)  [no recursive calls]
    x <- B_J x            [normalized rank f-k_j, volume v_j],

where rank0 means identity, with zero recursive charge. The middle adapter is
required to implement S_K(x,y,z)=(x+B_K y/2,y,z) for every x,y and every
independent arbitrary dirty auxiliary tuple z. Because the first native map
is invertible, requiring the complete boundary indeed forces this adapter
boundary on all states. All B factors and A commute, so the displayed program
has exactly the selected physical output C_f x+B_f y/2.

The adapter permits any finite number of registers of length v_j; invertible
monomial maps within those registers; and shears adding a monomial image of
one register into a distinct register. Every such shear operates on the whole
block and is charged v_j coordinate additions. Source mixtures, donor feedback,
arbitrary order and arbitrary independent dirty auxiliaries are allowed. Every
auxiliary and donor must be restored at the adapter endpoint. There is no
cross-block operation, pre-encoding, reset, free fanout, data-dependent choice,
masked sub-block shear or recursive operation inside S_K. Grant all monomial
maps, routing and helper availability free in the lower-bound relaxation.

The native ranks follow directly from the tensor kernel: the first map acts
on f+k_j independent binary directions and the second on f-k_j; spectators
do not multiply rank. Their actual operand volumes are v_j. Treat existence
of legal physical wrappers, block acquisition and a matching supplier call as
optimistic grants. This proof does not establish those hosting or compiler
obligations, and never counts a concatenated larger operand as volume v_j.

## 2. Coordinate blocks cannot slice a dense joint orbit

If C_f is implemented as a direct sum on a fixed coordinate partition, each
column must remain in its input block. Its4^f nonzero entries occupy its entire
joint orbit. Therefore every such block contains complete joint orbits; splitting
one orbit into smaller coordinate blocks cannot preserve this direct-sum action.
Consequently simply splitting a rank2f call into these blocks leaves the
optimistic charge A sum(v_j)(2f)^p = A V(2f)^p unchanged. A nonmonomial
spectral basis changes this premise and must be charged separately.

## 3. Adapter lower bound, including restored dirt

Let s(w) be the total number of nonzero coordinates over ALL adapter registers.
Monomial maps preserve it. A shear increases it by at most a factor2, because
the new target support lies in the union of its old support and the permuted
source support. Start S_K with x=0, y one coordinate basis vector, and every
auxiliary zero. This specialization is legal even for arbitrary dirty helpers.
Initially s=1; finally the target has2^k nonzeros and the restored donor one,
while every auxiliary is zero. Thus after l shears,

    2^k+1 <= 2^l,    hence l >= k+1.                       (1)

The original adapter is one ADD. The changed adapter therefore incurs at least
k additional block-wide shears, hence at least k v_j extra coordinate additions.
This includes k=0, when the bound is the original single ADD. The conclusion
counts all auxiliary support and does not assume the source remains read-only.
It concerns actual processed volume only because each permitted shear is a
whole-block operation. Applying (1) to masked operations would be invalid.

A direct read-only-donor construction always exists in this relaxed algebra:
expand B_K into2^k distinct signed-XOR monomials, with coefficients
a^(k-|S|)b^|S|. These translations are independent, so every column has exactly
2^k nonzero coefficients. It uses2^k Gaussian monomial-source shears and
restores the donor after every paid source map. This construction is not
asserted optimal among feedback adapters; PR4009 supplies a linear alternative.

## 4. Uniform native and arithmetic invoice

Let 0<alpha<1, p=1-alpha and delta=2-2^p>0. In the inherited optimistic
volume-linear recursive charge, a width r on volume v costs A v r^p for some
fixed A>0, common to every block and f. These charges use the same units
in which one coordinate addition costs one. A different fixed arithmetic
tariff gamma>0 can be absorbed by replacing A with A/gamma. Compared with the original two rank-f calls, the block saving is

    A v Delta(f,k),
    Delta(f,k) = 2 f^p - (f+k)^p - (f-k)^p.                (2)

Define h(t)=2-(1+t)^p-(1-t)^p on[0,1]. Concavity of u^p gives h>=0.
On the open interval,

    h''(t)=p(1-p)[(1+t)^(p-2)+(1-t)^(p-2)] > 0.

By continuity at1, convexity and the chord from(0,0) to(1,delta) give
h(t)<=delta t. Consequently, uniformly for every integer0<=k<=f,

    0 <= Delta(f,k) <= delta k f^(-alpha).                 (3)

Let W=sum_j v_j k_j. Combining (1)-(3), even after granting every source map,
wrapper, helper, precision and routing operation free, the complete optimistic
change relative to the original calls and ADD obeys

    added arithmetic >= W,
    available recursive saving <= A delta f^(-alpha) W.  (4)

If W=0 there is no rank saving. If W>0 and A delta f^(-alpha)<=1, there is no
strict improvement. For every fixed A, this condition holds for all sufficiently
large f. The block volumes, number of blocks, subsets K_j and k_j may all vary
with f: the same bound holds after summing, with no fixed positive block-size
fraction assumption. Uniform asymptotic improvement is therefore impossible
within this orbitwise partial-fusion model. This is a comparison with an
available recursive upper-charge expression, not an optimal-runtime lower bound.
The actual A is not supplied, so no numerical finite crossing is claimed.

The selected alpha is 67018507072324140917/40000000000000000000000, pinned in
the source assembly. The result holds for every0<alpha<1; finite numerical
checks of this instance do not replace the convexity proof.

## 5. What remains open

Cross-block mixing, masked operations inside an orbit, overlapping native
supports, data-dependent schedules, or recursive calls inside the adapter
change the contract. A spectral decomposition also changes the charged basis
interface. Their feasibility and total processed volumes are not bounded here.
No selected profile, claimed kappa or frontier is changed. The practical next
test must exhibit one such changed operation and a complete restored boundary,
then compare its total volume before growing a search.

PR3975 (Gonzalo Mier) supplied the literal sequential handoff. PR3989 and
PR4009 (Clear1nsight, with OpenAI Codex assistance) established its phased
Pauli binding and feedback analysis. Credit Cinna Davis/PR1836, Adam Gall,
Arham Tahir/PR1920, ToikY/PR1924 and the selected PR1094/PR679 lineage for
the related joint-interface and volume lessons. The new statement is the
heterogeneous-volume, all-fractional-cuts invoice (4), within the stated order.
Prepared by Clear1nsight with substantial OpenAI Codex assistance. Apache-2.0.
