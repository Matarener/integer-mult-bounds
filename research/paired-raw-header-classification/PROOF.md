# Optimal one-bit headers for paired raw broadcasts

This scoped proof and its finite corroboration were produced by Nick Petalas.
Apache-2.0. Independent human and formal proof-kernel review are unclaimed.

## Contract and result

Let n >= 1. There are 2n independent uniform bits X_0,...,X_(2n-1).
Receiver i demands X_i and initially knows only X_(i xor 1). Sources and
receivers are distinct roles. A central encoder sends the mandatory one-bit
public header h(X), charged two units, even if h is constant. On branch r,
it broadcasts a fixed list of raw source bits, charged one per transmitted
bit. Every receiver receives the list and header. The list, its order and
its length depend only on r. All inputs must decode exactly. Arbitrary
nonlinear h and decoders are allowed. There are no other messages, private
metadata, relays or extra free side information.

This is an abstract matching contract. Its n=5 instance uses the public-header
and singleton-broadcast tariffs of Jerry Chen's PR912 Hurwitz model. It
restricts that predecessor's arbitrary payload alphabet to raw broadcasts.
No geometry with arbitrarily many Hurwitz lines is asserted.

Write P(h) for the set of pairs j such that

    h(x xor e_(2j)) = h(x) xor 1,
    h(x xor e_(2j+1)) = h(x) xor 1                  for every x.

Equivalently, j belongs to P(h) exactly when

    h(x) = x_(2j) xor x_(2j+1) xor g(x outside pair j)

for some Boolean function g. Let C_raw(h) be the least expected charge for
the fixed header h over all allowed branch-dependent raw lists.

**Theorem.** For every n >= 1,

1. C_raw(h) = 2n if and only if P(h) is nonempty.
2. If P(h) is empty, then C_raw(h) >= 2n+1. This one-unit separation is sharp.
3. Every cost-2n code broadcasts each source outside one complete pair exactly
   once on each branch. The omitted pair on each branch belongs to P(h),
   and the two branches can choose any two members of P(h) independently.

List order does not affect decoding. Repetitions can be deleted, so first
work with the set S_r of transmitted source indices. A repeated bit can
never occur in an attaining code, since deleting it strictly lowers expected
charge on its nonempty branch. We count payload sets, not their permutations.

## Fibre capacity

Fix a nonempty header fibre F_r, a transmitted set S, and its omitted
indices U. Let a be the number of pairs with both bits omitted and b the
number with exactly one omitted bit. Thus k=a+b pairs are touched and

    |S| = 2n-2a-b.

Fix the values of X_S. For a singly omitted bit, its receiver's mate is
already fixed, so the decoder permits at most one value for that bit.
For a doubly omitted pair, either bit determines the other through its
receiver's decoder, so at most two pair assignments occur. This conclusion
does not assume independence inside the fibre. Projecting the fibre into
the omitted pairs bounds its size by the product of these local capacities.
There are at most 2^|S| choices of X_S. Consequently

    |F_r| <= 2^(|S|+a) = 2^(2n-k),
    p_r = Pr[h(X)=r] <= 2^(-k).                         (1)

Also the number s=|U| of omitted bits obeys s=2a+b <= 2k.
For k=0 no bits are omitted. The bound applies to every zero-error branch,
including nonlinear decoders and arbitrary correlations caused by h.

## Expected cost and equality

First suppose h is unbalanced, including a constant h. Its larger fibre has
probability greater than 1/2. Equation (1) forces that branch to transmit all
2n source bits. If the smaller nonempty branch touches k>=1 pairs, its
expected saving in raw bits is at most

    p_small s_small <= 2k / 2^k <= 1.

The last inequality follows from k <= 2^(k-1) for every positive integer k.
If the smaller fibre is empty, or touches no pair, its saving is zero.
Therefore every unbalanced-header code has expected cost at least 2n+1.

Now suppose both fibres have probability 1/2. Equation (1) gives k<=1 on
each branch, so at most two raw bits can be omitted per branch. Expected
cost is at least 2n. If a branch omits both bits of a pair, take either
coordinate i of that pair. Two points x and x xor e_i cannot both belong
to F_r: their raw broadcasts and mate bits agree, while receiver i's demand
differs. The edges {x,x xor e_i} partition the whole cube into 2^(2n-1)
disjoint pairs. Since F_r has that exact size, it contains one point from
each edge. Thus h flips under coordinate i on the whole cube. Applying this
to both coordinates proves that the omitted pair belongs to P(h).

If P(h) is empty, neither balanced branch can omit two bits. Each transmits
at least 2n-1 bits, and the cost is at least 2n+1. If cost is exactly 2n,
both branches must omit two bits, so they omit a full pair in P(h).

Conversely choose j in P(h). Broadcast all 2n-2 bits outside j. Every
receiver outside j receives its demand directly. A receiver inside j
computes g from the broadcasts and recovers its demand as

    header xor g(broadcasts) xor its mate bit.

This costs 2+(2n-2)=2n on every input. The same construction works if each
branch selects a different member of P(h). This proves all three claims.

Sharpness of the one-unit separation follows for every n from h(X)=X_0.
Broadcast all bits except X_0. Receiver 0 uses the header; the others read
their raw demands. The cost is exactly 2n+1 and P(h) is empty. There is also
an unbalanced attaining example for every n>=2: let h be the OR of the first
two pair parities. On its probability-1/4 zero branch, omit all four bits
of those pairs. On its other branch transmit every bit. The expected raw
count is 2n-1, giving total 2n+1. Both cases are checked directly at n=3.

## Closed-form classification count

For each pair j, let A_j be the Boolean headers that flip in both coordinates
of j. If a specified set of k pairs has this property, the header is the
XOR of those k pair parities and an arbitrary Boolean function of the
remaining 2(n-k) bits. Hence that intersection has exactly

    2^(2^(2(n-k)))

headers. Inclusion-exclusion counts all optimal headers:

    N_n = sum_(k=1)^n (-1)^(k+1) binom(n,k) 2^(2^(2(n-k))).       (2)

The number with exactly k full parity pairs is

    E_(n,k) = binom(n,k) sum_(j=0)^(n-k)
              (-1)^j binom(n-k,j) 2^(2^(2(n-k-j))).             (3)

For three pairs the new enumeration gives

    E_(3,1)=196518, E_(3,2)=42, E_(3,3)=2,
    N_3=196562.

It also enumerates all sum_k k^2 E_(3,k)=196704 optimal ordered pairs of
branch payload sets and decodes both omitted demands on every input.
The predecessor's two-pair result is cited rather than replayed. Formula (2)
specializes to its 30 headers, but our unrestricted-payload claim does not
extend beyond that predecessor's domain. For n>=3 the theorem here concerns
the stated raw-broadcast contract only.

## Consequence and limits

Allowing the raw payload set to depend on the header creates more optimal
protocols but no additional optimal headers. Every such header already has
an optimal code using the same omitted pair on both branches. To find more
optimal headers at three or more pairs, one must change the payload alphabet
or another stated contract hypothesis. This conclusion does not exclude
cheaper general nonlinear payloads or different physical realizations.

The universal statement rests on the written proof. The finite verifier
corroborates the new three-pair domain with independently computed Boolean
derivatives, literal decoders and exhaustive raw-subset oracles on a declared
sample of headers. It does not enumerate all 2^64 three-pair Boolean headers.
No integer multiplication theorem, new kappa, physical supplier, all-size
compiler, native operator, ownership, precision/tape or analytic admission
is proved. Classical fibre counting and inclusion-exclusion retain their
mathematical credit.
