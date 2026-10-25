# A paid tagged-bank realization of every retained signed line

This supporting result closes the representation mismatch identified in #4042,
under an explicit supplied-window contract. It supplies a constructive bit-tape
upper bill. It does not attach the abstract recursive H1 tariff to this direct
Gaussian implementation, or establish an affordable complete decoder.

## Actual event and source boundary

The frozen #4106 word starts its native subsequence at event 4:
`line W0 0 +1`, whose q is 11. Its first negative line is event 1705:
`line Z10 76 -1`, whose q is 448. The q=19 negative event discussed in #4042
belongs to the old #4015 ordering and is not this first #4106 negative event.

The authenticated canonical line-normalized native receipt gives the recipe
for every port and sign. For a nonzero q in the low nine coordinates, choose
its least set bit p, and let B have columns q followed by the ordinary basis
columns other than e_p in increasing order. The native recipe is

    P_(B,delta) C_e0 P_(B^-1,0),

where P_(A,b) sends input address x to Ax XOR b. The expression means first
P_(B^-1,0), then the positive coordinate
Gaussian, then the left output permutation x -> Bx XOR delta, with delta=0
for positive sign and delta=q for negative sign. To avoid ambiguous operator
order, the implementation below uses this input/output description. At tensor
depth lambda it applies independently on each factor. Coordinates 9 through
72 are identity spectators in B.

The Gaussian coefficient identity is checked against every one of 512 basis
columns for every actual occurrence. All 224 calls are covered: 120 positive,
104 negative, 216 distinct (port,sign) recipes; 208 recipes occur once and eight
occur twice. The earlier receipt's event numbers are not reused as current
occurrence indices. This is literal source coverage plus the tensor-product
identity, not extrapolation from a few numerical fixtures.

## Conditional external contract

Fix n>=1, lambda>=1, W>=2, M>=1 and 0<q<2^n. Put
N=2^(n lambda), S=MN, d=n^2+n lambda and L=d+2W+2. For the source application
n=73, with q supported in the first nine coordinates. The data tape contains
one left fence, S owner-major records in the tagged router format, and one
right fence. Each record has d tag bits, a colon, W little-endian signed real
bits, W little-endian signed imaginary bits, and a semicolon. All N addresses
of each owner occur contiguously in lexicographic tag order. The source
`oracle.key` serializes address bits low-to-high and sorts the resulting strings.
Consequently record position j has address chi(j), the reversal of all n lambda
bits of j. Treating j itself as the address changes this ABI. Owner tags and
payloads may be arbitrary and correlated. Valid tag content/order is an entry
premise; this adapter neither enumerates the owner set nor checks its closure.

Supply six additional exclusive, discardable windows on six separate physical
tapes: two of NW bits and four of NW/2 bits. They may start with arbitrary
binary contents. All seven heads begin at their separately supplied origins;
tape exteriors and every spectator tape/head may be arbitrary. The six windows
must not alias any live query, output, borrowed bank or other active storage.
Their old values are discarded under ownership, not restored as dirty loans.

The common component grid is fixed throughout the call. Every numerator of
every executed Gaussian must be even as an integer on that grid and within
signed W-bit range. The decoder precision proof must establish this premise
for its own entry grids and intermediate values. Arbitrary bounded floating
inputs do not satisfy it automatically. The axis program performs exact integer
halving, has no arithmetic rounding error under this premise, and does not
non-destructively establish its own admission conditions.

The program returns the signed q-line tensor action in the same tagged data
window. It leaves all tags and fences unchanged, clears all six temporary
windows to binary zero, returns every head to its entry origin, and preserves
all exteriors and spectators. Its program family is nonuniform in
(n,lambda,W,M,q,sign). In particular this statement does not supply an all-size
compiler, a program-loader invoice, or uniform finite control independent of
these parameters. The finite unrolling contains no payload-valued indices or
unbounded payload registers; each payload action is a literal tape read, write
or unit move. Nonuniform addressing is paid through the moves described below.

## Construction and correctness

Let rho be the tensor permutation B^-1 on the N addresses, chi the tag-order
bit reversal just defined, and let
Delta be the concatenation of lambda copies of q for the negative sign, zero
for the positive sign. Process one owner at a time.

1. In increasing tagged record order j, with actual address x=chi(j), read every
   real/imaginary payload bit and write it at address rho(x) on its corresponding raw component tape.
   Every intervening head position is traversed by charged unit moves. No tag
   is written. Return both raw heads to their origins.
2. Invoke the authenticated #3884 positive `axis_kernel` on address axes
   0,n,...,(lambda-1)n, sequentially. Its two data tapes and four scratch tapes
   are exactly the six supplied windows. Each call returns its heads and zeros
   the scratch. Its proven preconditions and 32NW cell-action invoice remain
   explicit inherited premises.
3. In increasing tagged record order j, with x=chi(j), read raw address
   rho(x XOR Delta), write its
   bits to the tagged payload, and overwrite each consumed raw bit with zero.
   Both insertion orders are permutations, so every raw bit is read once after
   its last use and cleared once. Return the two raw heads to their origins.

After the last owner, return the tagged head to its origin. The raw windows
are reused serially across owners; storage is not multiplied by M. The
composition is precisely the source right wrapper, positive Gaussian tensor,
and signed left wrapper. Replacing the negative left offset by zero changes
an attainable nonconstant fixture's endpoint; it is not a harmless phase label.

A data write can touch only that owner's payload positions. Raw and scratch
accesses stay within their reserved intervals by the #3884 footprint and the
permutation range. Unit moves may visit one-past positions but never read or
write them. Thus the argument applies to arbitrary dirty exteriors; sentinel
fixtures corroborate only finite instances. No tape origin relocation, second
head on the tagged tape, or payload address lookup is free.

The tagged router's clean buffers are blank-symbol windows, whereas this
adapter returns binary zero windows. They are not silently interchangeable.
A caller sharing those physical buffers must separately implement and charge
blank-to-binary initialization and binary-to-blank restoration, or reserve
these six binary windows apart from the router's three clean buffers. This
statement takes the latter explicit allocation contract. Seven tapes suffice
for the native adapter; a combined router/native setup may reserve four more
axis windows beyond the router buffers or use a separately charged conversion.

## Exact cell-action invoice

For a permutation pi of 0,...,N-1 define V_W(pi) as the total distance of the
raw head route

    0 -> pi(0)W -> ... through that word's W bits -> pi(1)W
      -> ... through all N words -> 0.

In particular, with a_j=pi(j)W,

    V_W(pi) = a_0 + N(W-1)
              + sum_{j=0}^{N-2} |a_(j+1)-a_j-(W-1)|
              + a_(N-1)+(W-1).

This includes both origin legs and every within-word move. It is a finite exact
parameter expression, not a runtime oracle. Set alpha(j)=rho(chi(j)) and sigma(j)=rho(chi(j) XOR Delta).
The two component streams incur 2M[V_W(alpha)+V_W(sigma)] adapter moves.

The tagged head makes an extraction scan, rewinds to the first payload of that
owner, makes an insertion scan, and then proceeds to the next owner. The
first payload is d+2 cells from the global origin, consecutive owner blocks
are NL cells apart, and the last payload bit is SL-1. Summing these distances
including the final origin return gives exactly

    A_tag = 4SL - 2M(d+3) - 2.

The complete seven-tape cell bill is

    READ  = (4+6 lambda) SW,
    WRITE = (6+6 lambda) SW,
    MOVE  = 20 lambda SW + A_tag + 2M[V_W(alpha)+V_W(sigma)],
    TOTAL = (10+32 lambda) SW + A_tag
            + 2M[V_W(alpha)+V_W(sigma)].

The inherited Gaussian contribution is exactly 32 lambda SW. Extraction costs
2SW tagged reads and raw writes; insertion costs 2SW raw reads, tagged writes,
and raw zero writes. The extra WRITE term restores the raw windows. Dropping
that cleanup fails the returned-zero contract on a nonzero fixture.

Reserved cells are SL+2+4NW: the tagged bank, two NW data windows, and four
NW/2 scratch windows. This count includes tags, fences and the existing bank;
additional workspace is 4NW bits. Code/control storage and a uniform loader are
not included; finite control has only bounded bit/carry values for each fixed
compiled program. To obtain a literal transition bill under a control model
charging administrative no-op transfers separately, add the actual compiled
handoff/halting overhead. The exact expression above deliberately claims cell
actions, matching #3884's meter, not an unsupported universal transition count.

This fully paid reference removes the specific tagged/interleaved versus
split/raw ABI incompatibility. Its potentially large permutation variation and
extra private storage prevent interpreting the result as an affordable recursive
child. Pricing it at an abstract H1 cost would displace work. The root ledger
must compare this cell bill under the same physical model as the alternative,
and keep acquisition, scalar updates, cover maps, caller conversion, native
usage multiplicities and complete output/consumer obligations visible.

## Executed evidence and limits

`realization.audit(authenticated_axis_module)` executes the inherited axis
program inside the new metered adapter. Seven fixtures include translated
origins, arbitrary dirty binary scratch, multiple owners, two tensor factors,
nonconstant real and imaginary payloads, q=19 of the old #4042 example, and the
actual q=11 positive / q=448 negative #4106 first calls on all 512 low-coordinate
addresses. Every counted action is compared against the complete formula;
all endpoints are compared with a separately ordered exact rational direct
C_q oracle. Meaningful controls remove the signed affine offset, omit raw cleanup, and
omit the tagged address-bit reversal; they fail endpoint/restoration before
count checks. Fixtures use actual lexicographically sorted source-format tags.

The tensor/basis proof gives the parameter scope. Finite fixtures do not execute
the 2^73 full-cover payload, certify source owner closure, prove the caller owns
these windows, or admit a recursive supplier. The code intentionally receives
its inherited #3884 module only after the central verifier authenticates the
pinned bytes. Consequently the axis implementation/proof is shared evidence,
not a second independent axis implementation. No human or formal-kernel
acceptance is claimed.

Credit Clear1nsight/#3884 for the signed-bit axis; Dugongue/#3394 for the tagged
owner-cover format and routing contract; #4042 for the precise ABI separating
example; ywz65/#2707, Arham Tahir/#2681, Ali Romman and the native Clifford
lineage for the signed source recipe; Nick Petalas/#3303 and ToikY/#3652 for
separately scoped depth/numerical evidence. New adapter/proof prepared with
substantial OpenAI Codex assistance, Apache-2.0.

## Why this particular adapter is not a favorable physical route

At the source dimension n=73, q is confined to the first nine coordinates.
The highest raw address bit n lambda-1 is an identity spectator under rho and
is absent from Delta. For each even record j, chi(j+1) differs from chi(j)
only in that highest bit. Therefore alpha(j+1)-alpha(j), and likewise the
sigma difference, has magnitude N/2. The transition from the last bit of one
word to the first bit of the next costs at least NW/2-W+1. There are N/2
such adjacent pairs, giving

    V_W(alpha), V_W(sigma) >= N^2 W/4 - NW/2 + N/2,
    raw adapter MOVE >= M N^2 W - 2MNW + 2MN.

This is a quantified lower bound on this exact sequential-tag/direct-raw
reference schedule, whose full bill above is constructive. It explains why
summing an inexpensive Gaussian axis bill with free transposes is unsound.
It is not a lower bound on every possible native realization: stable radix
reordering, a raw layout adapted to tag order, different signed-butterfly
pairing and extra tapes can change this route class. Those alternatives need
their own full memory/control/cleanup bills. The implementation implication
closed here is representation compatibility with a paid upper bill; the
remaining construction decision is affordability or a better layout mechanism.
