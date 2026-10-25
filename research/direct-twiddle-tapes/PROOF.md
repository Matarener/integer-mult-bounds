# Direct sequential data tapes for synthetic headers

This is an author-written proof for arbitrary finite shapes. Independent human and formal proof-kernel review are unclaimed. The executable enforces ell<=256 and at most 64 axes. Finite replay corroborates the proof; it does not prove its unbounded quantifiers.

## Contract and actual premises

Let ell>=2, 1<=K<ell and D>=1. Axis i has ell or ell-1 named bits, A in total. For 0<=h<ell, let I be the axes containing position h, d=|I| and n=h+1. The pinned transform source and canonical circuit proof supply the physical named-slot order and function

    S = sum_(i in I) x_(i,h) sum_(v<h) 2^v x_(i,v) mod 2^n,
    E_- = -2^(ell-h) S mod 2^(ell+1),   E_+ = -E_-.

The live circuit.py is the independent layout/output oracle. These three canonical-main files are the complete external mathematical/runtime input closure in SOURCES.json and VERIFY.json. All arithmetic, storage and movement claims below are proved here. No pending theorem is assumed. PR3571 supplies the direct-register algorithmic lead and credit; PR3550 supplies the distinct encoded-program comparison. COMPARISONS.json records their comparison documents outside the input pins.

The physical order lists long-axis top positions, then planes b-1,...,0 where b=(ell-1) mod K, increasing axis inside each plane. Finally it lists the remaining K-bit chunks high to low, increasing axis inside a chunk and descending bit positions inside an axis chunk. Every named bit occurs exactly once. Shape.slots generates this order with shape-only loops and no retained slot table or circuit topology.

This is a family of data-tape programs driven by a supplied immutable shape scheduler. The scheduler supplies named slots, bank offsets and loop endpoints; it receives no address bits. Descriptor parsing, integer counters, participation lookup and instruction scheduling are outside the charged data bill. This is not a complete uniform encoded fixed-tape machine. Python objects, diagnostic counters and receipt generation are also outside the mathematical cell count. No measured Python memory or CPU speed is claimed.

Exactly four Boolean tapes hold the borrowed A-cell address, private P-cell bank, private n-cell little-endian accumulator and ell+1-cell output. All heads start at zero, and private/output cells start zero. Tape.read/write access only the current cell. Tape.move changes a head by one cell; seek performs the corresponding number of unit moves. At most eight transient Boolean values suffice for current input, pending bit, branch, carry, old accumulator bit and expression results. They can be finite control reset when each routine returns. Shape values and diagnostic counts are input independent.

The machine reads each address cell exactly once, in increasing order. Its final head return uses movement only. It emits after the whole address, preserves every borrowed bit, returns all heads to zero and erases both private tapes. It does not accept arbitrary dirty private tapes. The output capacity includes one complete header, not an accumulated stream.

## Streaming arithmetic and restoration

Define a=b when b<=h<ell-1, and a=0 otherwise. Put w=max(a,1) and P=max(1,d*w). Each participating axis owns a w-cell bank segment. Its branch is beta_i=x_(i,h). Exactly lower positions v<a precede this branch physically: at the top round branches lead; at h<b its plane precedes lower planes; otherwise the b extracted low bits precede its branch-containing chunk and every other lower position follows the branch within that axis's chunk or later chunks.

Ignore nonparticipating axes and positions above h. Write v<a into that axis's bank cell v. When its branch arrives, for v=0,...,a-1 read the pending bit, clear it and add beta_i*x_(i,v)*2^v modulo 2^n. Then write beta_i into the segment's first cell. For each later lower position v, read the retained branch and add beta_i*x_(i,v)*2^v. There is no second branch bank.

The accumulator invariant is the sum of exactly those branch/lower products whose two bits have arrived. Before an axis's branch, its segment retains the arrived low prefix. Afterwards its first cell is beta_i and all others are zero. Arrival order makes every read valid, and the updates preserve this invariant. At EOF every term has arrived once, so the accumulator is S.

To add c*2^v, compute c=branch AND bit, then for t=v,...,h read z_t, write z_t XOR c and replace c by z_t AND c. The identity z_t+c=(z_t XOR c)+2(z_t AND c) proves the ripple by induction; final overflow is discarded. For a nondegenerate forward round complement/increment all n bits. At each position inverse=z_t XOR 1, result=inverse XOR carry and next carry=inverse AND carry. This gives -S modulo 2^n. The opposite direction omits negation.

Read accumulator positions h,...,0 into the output, then write ell-h zeros. These ell+1 bits encode E_- or E_+. At h=0 or d=0 every term is zero and negation is omitted, but every input/output cell is still read/written. Finally erase P+n private cells and return their heads, the address head and output head to zero. The normal bill includes every scan and return. No address write occurs.

An injected address-read exception erases the output and performs private/address restoration. This tested fault contract assumes reliable cleanup writes/moves; hardware failure or a second interruption during cleanup is outside scope. Failure/retry counts are separate from the normal bill.

## Exact normal invoice

Let f=1 for a nondegenerate forward round and zero otherwise. There is one masked addition for each of d*h lower bits, with

    L = d * sum_(v=0)^(h-1) (h+1-v) = d*h*(h+3)/2

accumulator ripple positions. Exactly

    AND = d*h + L + f*n,   XOR = L + 2*f*n.

The per-role read/write counts include output and cleanup:

    address: reads A, writes 0;
    bank:    reads d*h, writes 2*d*a+d+P;
    total:   reads L+(f+1)*n, writes L+(f+1)*n;
    output:  reads 0, writes ell+1.

Bank writes are d*a early writes, d*a consumed-bit clears, d branch writes and P cleanup writes. Its reads are d*a pending bits plus d*(h-a) later branches. Accumulator extra reads are optional negation and n emitted bits; extra writes are optional negation and n cleanup writes.

Address movement is 2*(A-1); output movement is 2*ell. For chronological access targets q_1,...,q_m, set q_0=q_(m+1)=0. Exact movement is

    M(q) = sum_(j=0)^m |q_(j+1)-q_j|.

The bank sequence B contains the early writes, pending reads/clears, branch writes and later branch reads in physical arrival order, then 0,...,P-1 for cleanup. This is an explicit finite shape-only sum. Independent expected constructs B by sorting named-bit arrival times without consulting machine head state or data. A read and clear at one cell give identical consecutive targets and add no movement.

Accumulator targets are v,...,h for each addition in arrival order, 0,...,h if f=1, h,...,0 for output and 0,...,h for cleanup. Its exact movement is M of that sequence. If d*h=0, it is 4h. Otherwise let u be the first lower position added: u=0 when a>0, u=b-1 when h=ell-1 and b>0, and u=h-1 otherwise. Then

    M_total = d*h*(h+1) + (2*f+2)*h + 2*u.

The first addition travels zero to u to h, costing h. Subsequent additions at v cost 2*(h-v), giving total d*h*(h+1)-h+2u. Optional negation adds 2h; output adds h and cleanup 2h. With no additions an initial output seek adds the extra h giving 4h. Extracted low positions explain the top-round u=b-1 edge case.

Exact allocated data capacity is

    C = A + P + h+1 + ell+1 Boolean cells,

plus at most eight transient Boolean values. The dummy bank cell is charged even when d=0. Input, output and private tapes are separate. Every count and C depend only on shape/direction, not address values.

## Polynomial bound and source allowance

Let T sum reads, writes, unit moves, ANDs and XORs. Since d*h<=A, d*a<=A, d<=A, P<=A and ell<=A+1, we have L<=A*(ell+2)/2. Nonmovement operations total at most 2*A*ell+11*A+8*ell+1. There are at most 5A bank accesses, so movement with final return is at most (5A+1)*(P-1)<=5*A^2+A. Accumulator movement is at most A*ell+6*ell, including degeneracy. Address/output add at most 2A+2ell. Thus

    T <= 5*A^2 + 3*A*ell + 14*A + 16*ell + 1
      <= 20*(A+ell+1)^2.

C=O(A+ell). Under the source's D*ell=O(p) band, A=O(p), giving O(p^2) charged data work and O(p) data cells. Its explicit exponential comparison bands make r dominate every fixed power of p, so this data work fits its O(rp) per-record allowance. This does not pay unknown costs: encoded scheduler generation/parsing/counters, address enumeration, descriptor movement, packet processing, spectators, dirty restoration and the complete caller remain separate. No numerical cutoff or supplier/kappa follows.

This uses longer sparse ripples than PR3571's full-word register adder and serializes bank access. No faster gate count is claimed. Earlier supplied-circuit interpreters charge programs under different contracts; no total-machine storage superiority is inferred by omitting this scheduler.

## Evidence and remaining work

RESULT.json records 203896 addresses in 700 complete small physical fixtures, 30 wider evaluations through ell=256, fifteen boundary rejections and three actual failed-read restoration/retry cases. Each normal run agrees with direct named-bit arithmetic, authenticated canonical circuit and the independent read/write/move/gate/cell bill. Accumulator movement also agrees with the closed form. Wide zero/one/patterned inputs have identical bills. Ten optimized actual CLI fault groups exercise changed masks, lost pending/branch bits, wrong borrowed returns, uncharged moves, failed erasure, wrong first-position formula, receipt drift and changed/absent source bytes.

No encoded uniform controller, signed-packet/layer consumer, full caller, arbitrary dirty-private contract, native/root/ordinary refinement, full multiplication theorem, human/formal acceptance, supplier or frontier improvement is claimed. Start the next task at ell=8,K=4,h=5 and twelve mixed axes, with an explicit encoded descriptor/consumer contract and whole paid allowance. Stop if those contracts are missing.
