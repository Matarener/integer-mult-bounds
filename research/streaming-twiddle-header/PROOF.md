# A one-pass producer with necessary early-prefix memory

This is an author-written all-size proof. Independent human and formal proof-kernel review are unclaimed. The executable admits ell in 2..256 and one to 64 axes. Its finite checks do not prove the unbounded quantifiers below.

## Function, source and contract

Let ell>=2, 1<=K<ell, and let D>=1 axes each contain ell or ell-1 named bits. For 0<=h<ell, let I contain the axes with a bit at position h, and put d=|I|, n=h+1 and b=(ell-1) mod K. The retained transform source's combined-twiddle equation and layout prescribe

    beta_i = x_(i,h),
    k_i = sum_(v=0)^(h-1) 2^v x_(i,v),
    S = sum_(i in I) beta_i k_i mod 2^n,
    E_- = -2^(ell-h) S mod 2^(ell+1),  E_+ = -E_-.

The pinned canonical circuit proof derives the named-slot interpretation and injectivity of the narrow modulus. These two source texts are actual mathematical premises. The pinned circuit.py is an independent layout/output oracle, not a runtime dependency of the producer. All three are canonical-main inputs in SOURCES.json.

The source's physical MSB order consists of long-axis top bits, then low planes b-1,...,0 with increasing axes inside each plane, then width-K chunks in decreasing chunk order with increasing axes inside each chunk. Bits descend inside each axis chunk. Thus a lower bit that physically precedes its branch is exactly a bit v<b when b<=h<ell-1. Define

    a = b, if b<=h<ell-1;
        0, otherwise.

The reader consumes this physical address once, left to right, then outputs the complete exponent. It cannot reread the prefix or release input-dependent write-only output before the stated cut. Include every input-dependent tape, head, control state and readable early output in the lower-bound state. Shape-only descriptors and positions cannot distinguish two prefixes at the same cut. Randomized error, prefix-dependent supplied programs, consumer interaction and early-output protocols change this contract.

The producer is a uniform register algorithm from the shape and incoming bits. The data bound counts explicitly sized mathematical bit registers, separately from the shape description, input-independent control, input/output and diagnostic receipts. The Python execution uses objects and is not a measurement of packed RAM or fixed-tape storage. The proof below also describes a Boolean implementation with bounded bit temporaries. No tape-movement invoice is inferred from it.

## Exact early-prefix lower bound

Suppose 1<=b<=h<ell-1. All D axes participate, so d=D and a=b. Cut after the long-axis tops and all d*b low-prefix bits. No branch bit has been read. The prefix determines independent integers

    u_i = sum_(v<b) 2^v x_(i,v),  0<=u_i<2^b.

Long-axis tops are irrelevant because h<ell-1. The residual S function is

    sum_i beta_i (u_i + 2^b z_i) mod 2^(h+1),

where z_i consists of the unread bits b,...,h-1. Every u vector occurs. Equal u vectors give equal functions. To distinguish u and u' choose one axis j on which they differ, set only beta_j=1 and all other branch and lower suffix bits to zero. The outputs differ by u_j-u'_j modulo 2^(h+1). This difference is nonzero since its absolute value is below 2^b<=2^h. Multiplication by 2^(ell-h) and either sign preserve the distinction. Hence there are exactly

    N = 2^(d*b)

residual functions at this literal physical cut, and every reader in the stated contract needs at least d*b bits of distinguishable state. This is exact at that cut, without assuming that every unread suffix is realized by a particular consumer.

For ell=8,K=4,h=5, twelve axes including three long axes give b=3. The cut follows 3+12*3=39 physical bits. Its exact count is 2^36=68719476736, and 36 state bits are necessary although S has only six bits. This count is a theorem instance. The executable enumerates full prefix/suffix functions only on its smaller fixtures.

## Streaming construction and invariant

For h>0 and d>0 allocate a bank of d words of w=max(a,1) bits and an n-bit little-endian accumulator C. Initialize them to zero. An immutable participation map relates physical axes to bank indices. The physical-slot generator has only shape-dependent loop indices and stores no address word or circuit topology.

1. Ignore nonparticipating axes and positions above h.
2. When v<a arrives, write its bit into position v of that axis's bank word. Its branch is still unread.
3. When branch beta_i arrives, add beta_i times the bank word into C modulo 2^n. Then replace the entire bank word by beta_i. If a=0 the word was zero, so this scheduled addition changes nothing.
4. When a<=v<h arrives, add x_(i,v)*beta_i*2^v to C modulo 2^n, using the retained bank bit.

Each lower slot is in exactly one of steps 2 and 4. The source order proves that step 2 always precedes its branch and step 4 always follows it. For h=ell-1 the long-axis branches occur in the first prefix. For h<b the branch plane precedes its lower planes. For b<=h<ell-1 all early low planes precede the branch-containing chunk, and every remaining lower bit of that axis follows its branch. This covers mixed shapes and every round.

After each input symbol, an axis whose branch is unread stores precisely the lower-prefix bits read for it. An axis whose branch is read stores precisely beta_i. The accumulator is the sum of all terms whose branch and lower bit have both arrived, modulo 2^n. The transition rules preserve this invariant directly. At EOF every term is complete and C=S. Negate C in place for E_-, emit its n bits MSB first, then emit ell-h zeros. For E_+ omit the negation. This outputs exactly ell+1 bits. Finally clear C and every bank word. The Python implementation resets these mathematical registers on both success and input failure. It claims no secure erasure of Python object copies.

For h=0 or d=0, consume the physical input and return zero without data registers. These cases still check input shape, bits and EOF.

## Data space and Boolean work

At input-symbol boundaries the construction has exactly the following allocated data capacity, independent of input values:

    B = d*max(a,1) + h+1,  if h>0 and d>0;
        0,                 otherwise.

Replacing a pending word by its branch reuses that word's existing bits. It does not add a second d-bit branch bank. In the lower-bound domain a=b>=1, B=d*b+h+1. Thus the construction's data capacity is within h+1 bits of the necessary whole-machine state at the early cut. This is an additive comparison, not a claim that B is the exact optimal peak state count. In particular no d-bit lower bound is asserted for a=0 or for degenerate rounds.

The executable's add_bits performs a fixed n-step ripple. At position v, read the existing bank bit or current input bit by fixed wiring, mask it by the branch/enable bit, and use the full adder

    q = left XOR right,
    sum = q XOR carry,
    next_carry = (left AND right) XOR (q AND carry).

The carry terms cannot both equal one. The truth table gives left+right+carry=sum+2*next_carry. Induction gives addition modulo 2^n, discarding final overflow. There is one masking AND and five adder gates per position, including the final discarded carry. Every participating axis schedules one branch addition and h-a later lower-bit additions, whether enabled or disabled. Hence the executed Boolean gate bill is exactly

    J = d*(h-a+1),
    G_+ = 6*(h+1)*J,
    G_- = G_+ + 3*(h+1),

for the nondegenerate case, and zero otherwise. The in-place complement/increment negation uses three gates per position. These are logical AND/XOR evaluations only. They exclude register reads/writes, clearing, input/output, descriptor handling and head movement. An exact gate count is not a full physical tariff or measured speedup.

The Boolean implementation needs at most eight scratch bits beyond B for the current input, carry, adder operands, mixed value and expression temporaries. Word extraction is a read of an existing bank cell at a shape-determined position, not a copied word register. Pending-bit writes and bank replacement take O(a+1) bit operations per axis; accumulator work takes O((h+1)*J), final output O(ell+1), and clearing O(B). If A is the physical address length, total random-access bit work is O(A+(h+1)*d*(h-a+1)+d*a+ell)=O(A*(h+1)+ell). The output may be emitted from the accumulator in place; storing it additionally costs ell+1 bits.

The shape includes D long/short bits and integer parameters. Its schedule can use counters of O(log(A+ell+D+2)) bits and an O(D log(D+2))-bit participation map, or compute participation by shape-only scans. These costs are separate from B and cannot be omitted from a total-machine claim. The executable uses a Python map and generator for them. No per-address circuit program is supplied. A fixed-tape lowering, self-delimiting descriptor parser and control/storage/movement invoice are not implemented here.

## Evidence, predecessor boundary and remaining obligations

RESULT.json records every complete physical fixture and residual-function case. The physical replay consumes a nonindexable iterator, checks exactly A bit reads and one EOF observation, and compares every output with both a direct named-bit formula and the authenticated canonical circuit. Separate exhaustive physical prefix/suffix tables check the lower-bound count. Wide fixtures include modular overflow, both signs, mixed top participation and integers above 2^53. Every such integer in JSON is an exact decimal string. Boundary controls reject invalid shapes, malformed/truncated/trailing streams and wrong theorem domains. Optimized CLI fault controls target lost low bits, missing branch masks, lost branches, carry propagation, state counts, cleanup, gate bills, input source bytes and the evidence receipt.

PR3559's author-checked later canonical-cut classification is contextual predecessor work, not a proof premise or imported runtime source. It did not classify this earlier cut or implement a producer. PR3550's supplied-program, reread interpreter addresses a different boundary. This package gives an actual direct streaming register producer and necessary early-prefix information. It does not compare physical runtimes with either package.

No signed coefficient-packet/layer join, mutable source ownership, dirty-workspace contract, fixed-tape compiler, address enumerator, native/root/ordinary supplier, all-size multiplication theorem, analytic transfer, kappa gain or selected-frontier update follows. The next useful step is a paid tape lowering or one actual packet-round consumer with explicit source preservation, spectators, heads, buffers and restoration. The producer's abstract register bound does not discharge those costs.
