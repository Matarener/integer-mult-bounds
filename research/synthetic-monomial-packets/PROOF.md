# Signed coefficient packets for a synthetic monomial

This is a data-boundary implementation of the retained source's exact signed
rotation. The source already states its algebra and linear scan cost. The new
result is a bit-level sequential interpreter, its explicit role and movement
invoice, and its failure/restoration contract. It supplies one part of the
inter-round boundary left by PR3493. It does not implement a T74 round.

## Contract and coefficient identity

Fix a power of two r >= 2, a component width w >= 3, and n >= 1 polynomial
records. A record contains r consecutive Gaussian coefficients. Each
coefficient contains a real signed w-bit word followed by an imaginary signed
w-bit word. Each word is MSB first, in two's complement. A separate controller
supplies one integer exponent E_a for each record, in the current address order.
No coefficient word is the minimum signed integer -2^(w-1).

Let E_a = q*r+s with 0 <= s < r. Since y^r=-1, multiplication by y^E_a sends
the last s coefficients to the front with sign (-1)^(q+1), and sends the first
r-s coefficients to the back with sign (-1)^q. Both components of a Gaussian
coefficient receive the same sign. Reducing E_a modulo 2r preserves these
signs, including negative exponents. No frequency or record-address permutation
is involved. The inverse is the same program with headers -E_a.

`MonomialPackets.run` first scans each complete input record into a prefix
buffer of 2(r-s)w bits and a suffix buffer of 2sw bits. It emits the suffix,
then the prefix, applying exactly these signs. The buffers have separate heads
and capacity 2rw each. A w-bit word buffer preserves MSB component order.

To negate a word, scan its bits from right to left with carry initially one.
At each bit b, write (1-b+carry) modulo two and propagate the quotient by two.
This computes complement plus one modulo 2^w. For every permitted signed word
x, -x lies in the signed w-bit range, so the resulting word represents exactly
-x. The preliminary scan rejects 100...0. This excludes the sole signed
overflow case, even for a header that would not negate that particular word.
All other signed words are permitted, a larger domain than the disk contract.

Consequently the output represents J_E f, where each record is multiplied by
y^E_a in Z[i][y]/(y^r+1). The proof covers every finite n,r,w in this family.
The executable deliberately limits n <= 128, r <= 64, w <= 128 and |E_a| < 2^63.
Those resource limits constrain the replay, not the algebraic statement.

## Disk format and rounding

If a grid coefficient is 2^-p*(x+i*z) in the unit disk, then |x|,|z| <= 2^p.
The source's w=p+2 format represents both endpoints and excludes the overflow
word -2^(p+1). It therefore admits every required negation. A uniform two's
complement format with p+1 bits cannot represent +2^p, so p+2 is minimal for
the entire closed disk. This is a format fact, not a new transform bound.

Signed coefficient permutations preserve the maximum coefficient norm. Since
truncation toward zero is odd, Q_p J_E = J_E Q_p. Thus a forward completed
round may truncate the parallel butterfly once and then run this exact packet
operation, preserving the source's result and error. An opposite round applies
J_E^-1 before its parallel butterfly and truncation. The adapter adds no
rounding error and no width growth.

For a source named-slot round at h, the required supplied headers are

    E_a = -sum_i (2r/2^(h+1))*b_i*sum_(v<h) 2^v*x_(i,v)  modulo 2r,

with only participating axes in the sum. `checks.py` derives this list from the
retained positional plan. Production encoded header generation is outside this
result. The lower bits are named axis slots, not the low physical address bits.

## Data roles, movement and restoration

Write L=2rw and N=nL. Five data roles suffice, including the borrowed N-bit
source and returned N-bit output. The two record buffers and word buffer add
2L+w cells. Total data capacity is 2N+2L+w. Control headers and counters are
separate and are not counted as data roles or tape space here. Allocation
occurs before execution. The interpreter never grows a data tape during run.

Every interpreter read, write and unit head step increments the operation
counter. A take or put costs two. Rewinding costs the actual head distance.
The initial output blank scan costs 3N. Copying input into the two buffers costs
4N. Emitting one component costs at most 20w, including copying to the word
buffer, validating, optional negation, copying to output, and clearing the word.
The two buffer rewinds cost at most L per record. Clearing both record buffers
costs at most 7L per record, including their entry head positions. These record
operations cost at most 32N. The final source/output head returns cost 2N.
Final private clearing costs at most 6L+3w. Hence successful execution costs
at most 37N+6L+3w data operations. The executable checks the looser public bound

    64N + 16L + 16w + 8n.

This counts data-tape operations only. Host header arithmetic, interpreter
dispatch and control storage are excluded. It is neither a measured CPU bound
nor a complete fixed-tape producer/caller invoice. A future encoded controller
must pay those charges explicitly. Arbitrary integer inputs do not become a
constant-time source of per-record headers.

The source tape receives no writes and its head returns to entry on every
started call. On success, output head is zero and all three private roles are
blank. On a data error after work starts, finally clears the partial output and
all three private roles and returns the source head. Rejection of a descriptor,
extent or occupied output before work starts makes no data change. Reuse after
a started failure is checked. Reuse after success requires the caller to clear
the returned output. Cancellation or arbitrary external mutation of private
roles is not an advertised recovery contract.

## Evidence boundary

The proof above establishes the unbounded mathematical family. Finite replay
enumerates all non-overflow signed values at widths 3 through 8, r in {2,4,8},
and exponents from -2r-1 through 2r+1. Mixed-header fixtures exercise 128 records,
r=64, 128-bit words, and signed 62-bit headers. Eight complete forward/opposite
transform fixtures use actual packet operations between rational parallel
butterfly rounds. They check the retained exact transform on inputs divisible
by M, and its completed-round component error on general grid inputs.

The butterfly is a rational oracle. Layout moves use the retained indexed
engine. The replay supplies neither a physical butterfly implementation nor
an encoded header producer. No source theorem defect, new transform algorithm,
supplier, new kappa or selected-frontier change is claimed.
