# Exact binary-code exhaustion in bit lanes

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.

## Claim and consumer

Let g_0,...,g_(d-1) be independent vectors in F2^n. Encode each vector as a
nonnegative integer with at most n bits. For 0 <= w <= n, `low_weight_words`
returns every word of their span with Hamming weight at most w, exactly once.
It includes zero. There is no assumption about the code, its minimum distance,
the generator order, or the relation between n and a machine word width.
The input check rejects dependent generators and malformed bounds.

The complete E7 classifier from PR5669 uses this function with n=63, d=27,
and w=12. It checks that zero and exactly 1,638 weight-twelve words remain.
Thus every nonzero word has weight at least twelve and all equality supports
are retained. The bound, equality theorem and all geometric conclusions are
the predecessor's results. This package changes their exact replay method.

## Coefficient partition

Set k=min(batch_bits,d) and L=2^k. Number lanes by integers a in [0,L).
The integer mask has a one at each of those L positions. For each j<k, the
coefficient pattern has bit a equal to bit j of a. The geometric-series
formula in the implementation repeats a block of 2^j zero bits followed by
2^j one bits. Its period divides L. Integer multiplication concatenates
these disjoint blocks; it cannot create a carry between them.

For each coordinate i, XOR the coefficient patterns whose generator g_j
has coordinate i equal to one. Lane a now holds coordinate i of the low
coefficient sum. Gray traversal enumerates every coefficient vector on
g_k,...,g_(d-1) exactly once. At step t>0 it changes the generator indexed
by the least significant one bit of t. Induction gives the usual Gray word
t XOR floor(t/2), a bijection on all high coefficients.

For a fixed high sum h, XOR the full lane mask at coordinate i precisely
when h_i=1. Each lane is now one complete codeword. Every coefficient vector
appears in exactly one batch and lane. Independence makes their images
distinct. No pruning or sampling occurs.

## Weight addition and comparison

For three one-bit operands a,b,c in one lane, set

```text
s = a XOR b
sum_bit = s XOR c
carry_bit = (a AND b) OR (s AND c).
```

The integer identity a+b+c=sum_bit+2*carry_bit holds in each of the eight
cases. Every operation is bitwise, so the same identity holds separately
in every lane. The program keeps carry bits in a separate plane of twice
the weight; it never shifts them into another lane. Two operands use the
same half-adder identity. At each level, these steps reduce the operand
list and send carries to the next level. They terminate with the exact
binary expansion of each lane's Hamming weight.

The comparator scans those planes from high to low. `equal` contains the
lanes whose prefix equals the bound prefix; `less` contains those already
strictly smaller. If the next bound bit is one, zero lanes leave `equal`
and enter `less`. If it is zero, one lanes leave `equal` without entering
`less`. This invariant proves that `less OR equal` contains exactly weights
at most w. The final mask removes all positions outside the finite lane set.
If the bound exceeds the largest representable value, every lane qualifies.

For each retained lane, the program reconstructs the literal XOR of the
chosen low generators and h. This is its exact input word. Zero dimension,
zero width, zero weight, and a bound equal to n follow from the same rules.

## Resource bound and scope

The public batch parameter is an integer in 1..20, with default 16. Input
dimension and width have no fixed cap. The plane storage is O(n*2^k) bits,
in addition to O(nd) bits for generators and elimination. Outputs are yielded
one at a time. The E7 default uses 2,048 batches of 65,536 lanes; it does not
store a 134-million-entry word table.

Each batch uses O(n) Boolean adder operations and O(log(n+1)) comparison
operations on L-bit integers. Input planes require O(nk) such operations.
Literal output reconstruction costs at most d vector XORs per output.
The coefficient space is still exponential in d. This is an exact arithmetic
implementation improvement, not a polynomial algorithm for minimum distance.
Python object overhead and integer operations remain positive costs.

## Full replay boundary

The source archive is retained byte for byte. The derived `classify.py`
differs from the source verifier at only `HERE` and `minimum_supports`.
The first locates the retained archive; the second calls the new engine.
The registered check compares every other Python syntax node exactly.
It then runs the complete derived check and compares every field of the
source receipt. All 63 reflection maps, all 135 frames, rational lift and
quadratic ranks, all 120 ambient slices, omission controls and rejection
controls remain active. There is no runtime replacement of a function and
no cache of source results.

The independent small oracle constructs spans by literal list doubling and
uses integer Hamming weights. It covers all 1,381 independent unordered
generator sets in F2^4, all five weight bounds, and five batch sizes: 34,525
comparisons. Separate tests cover widths through 127, malformed domains,
changed bases, changed bounds and a full changed basis for the E7 code.
These finite checks corroborate the general lane argument above.

## Relevance and attribution

E7 support exhaustion is used in the E8 deletion and quadratic-extension
work. Faster exact replays reduce the cost of checking those certificates
and permit larger bounded code searches. The implementation does not alter
the physical multiplication word, its paid profile or any selected bound.
Complete kappa is unchanged.

Credit Nick Petalas's PR5238 for the geometry, support theorem and binary
code; Ali Romman's PR5669 for the equality classification and complete
consumer; and the source's JoyboyBrian, Josie Elliston, Andrey Mas, Aaron
Wang, Brett Halligan, themilkman216 and DreamingOfClouds lineage. All source
notices remain in the retained archive. Boolean adders and bit-parallel
enumeration are established methods; no literature-priority claim is made.
