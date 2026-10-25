# Encoded shape control for direct synthetic twiddles

This is an author-written proof for every finite valid shape. Independent human
and formal proof-kernel review are unclaimed. The executable limits ell to
2..32 and the number D of axes to 1..16. Its finite checks corroborate the
argument and do not prove its unbounded quantifiers.

## Boundary and conclusion

Let ell>=2, 1<=K<ell, 0<=h<ell and D>=1. Axis i is long or short, with ell or
ell-1 named Boolean positions. Put A equal to their total number of positions,
I={i:h<ell-(not long_i)}, d=|I|, n=h+1,

    b=(ell-1) mod K,
    a=b if b<=h<ell-1, and a=0 otherwise,
    P=max(1,d*max(a,1)), M=A+ell+1.

The borrowed finite-alphabet descriptor is

    ^ 1^ell # 1^K # 1^h # flags # direction # $

where flags is a nonempty L/S word and direction is - or +. Its interior length
is N=ell+K+h+D+6. The caret and dollar symbols are left and right delimiters.
Descriptor capacity is N+2. The borrowed A address bits are in the source's
physical named-slot order. The output and private data tapes start blank. This
is a valid-input contract; arbitrary dirty private tapes and transactional
recovery after hardware/interruption faults are not supplied.

There is a uniform machine on 26 fixed tapes over fixed finite alphabets that
reads every address bit once in increasing physical order, returns the borrowed
address and descriptor unchanged with both heads at zero, emits the ell+1-bit
MSB-first residue

    E = sign * 2^(ell-h) * sum_(i in I) x_(i,h) sum_(v<h) 2^v x_(i,v)
        modulo 2^(ell+1),

and erases every private data/counter cell and returns all heads to zero. Here
sign=-1 for direction - and +1 for direction +. It uses no supplied circuit,
slot list, axis table, participation table or program tape.

Its exact allocated tape capacity is

    Cdata = A+P+n+ell+1,
    C = Cdata + 21*(N+4) + N+2 = Cdata+22N+86 <= 90M

finite-alphabet cells, plus constant finite control. Four tapes are Boolean
data tapes, 21 are binary counter tapes with two delimiter symbols, and one is
the borrowed descriptor. If all symbols are encoded as bits, two bits per
counter cell and three per descriptor cell suffice. This gives

    Cbits = Cdata+42*(N+4)+3*(N+2) <= 182M

bits, plus constant finite control. Eight data Boolean registers suffice.
No Python object-memory, byte count or CPU speed comparison is claimed.

For the tariff that counts each tape read, write, unit move and explicit data
AND/XOR once, the constructive upper bound is

    T <= 5000*M^2*(N+4) <= 20000*M^3.

The executable reports the actual data, counter and descriptor tape actions.
Each remaining finite-control transition is bounded by a constant per such
action or macro entry, so the complete transition count is O(M^3). The displayed
numeric tariff is not an exact total finite-control transition count.

## Actual premises and retained predecessor

The canonical input PROOF.md supplies the exponent formula and named-slot
interpretation, and circuit.py supplies an independent executable oracle. The
underlying transform text supplies the physical order and asymptotic comparison
bands. These three inputs are authenticated by SOURCES.json and declared in
VERIFY.json. The canonical circuit is never imported by the producer.

PR3582 is the actual algorithmic/proof predecessor for early-bit bank reuse and
direct data operations. Its exact PROOF.md and tapes.py are retained without
changes, with commit, path, Git blob and SHA256 in PREDECESSOR.json. They are
available in a Git-free export. They are not misclassified as an unrelated
comparison and no foreign Git object is required. The argument below reproves
the arithmetic, access and uniform-control implications used here.

## Counter implementation and uniform initialization

Each counter contains W=N+2 little-endian bits between distinct left and right
delimiters. To initialize one from blank, write its left delimiter, and scan the
borrowed descriptor from caret through dollar, writing one zero bit for each
actual symbol. Write the counter's right delimiter and return both heads by
delimiter scans. Repeat this fixed operation for the 21 named counter roles.
Thus the counter width is determined by actual descriptor symbols. It is not
supplied as a shape oracle. Every initializer access is charged.

A counter increment/decrement is a little-endian carry/borrow scan through its
right delimiter, followed by a return scan. Comparison reads two counters in
parallel, retaining only the relation at the highest different bit seen so far.
Copy writes each source bit. Addition/subtraction use their standard Boolean
carry/borrow transition with one carry bit. All these operations return their
heads to the left delimiter. Each takes at most 14*(W+2) tape actions. Zeroing
and final erasure fit the same bound. Final erasure clears the right delimiter,
returns while the left delimiter remains, then clears the left delimiter.

All counter values during execution are at most M. For example, a bank base can
reach P after the last axis; a pointer never exceeds its tape's last cell; the
erasure index can reach the exact extent. Other values are bounded by ell or A.
Since M<=N^2 and 2^(N+2)>N^2 for these descriptors, no valid run overflows. The
carry/borrow identities and comparison invariant prove every counter operation.

The simulator's preallocated list lengths and loop fuel are boundary checks and
diagnostics. No decoded counter value, Python head index, input bit, list of
named slots or arithmetic on an address value controls the schedule. Marker
tests and counter comparisons end all successful loops before their diagnostic
fuel bounds. Removing those guards gives the same finite-transition machine
on every valid input. The Boolean/counter dictionaries and opcode lookup each
have a fixed number of entries. A Python callback stack is not a physical tape.
Suspended axis scans have fixed nesting depth and constant finite state.

The host admission function checks the descriptor grammar, executable caps and
address extent before starting the simulator. A valid-input theorem needs no
oracle for these tests. A uniform validator can scan the fixed grammar, count
the unary fields and flags, and compare K, h and ell on the same counter tapes.
No executed physical invoice for malformed host admission is claimed here.

## Recovering the schedule from the descriptor

The actual parser increments ell, K and h from their unary fields. Repeated
subtraction of K from ell-1 computes quotient q and remainder b. Counter
comparisons compute a and stride=max(a,1). A descriptor flag scan computes the
bank extent P, charging its dummy cell when d=0. Another counter holds n=h+1.

Each axis sweep returns the descriptor head to caret, scans through the first
three separators, and reads L/S flags until the next separator. No flag vector
is copied. A counter base advances by stride precisely at participating axes.
There are three schedule phases.

1. At v=ell-1, consume one slot for each L flag.
2. At v=b-1,...,0, sweep every flag and consume its slot.
3. Starting at upper=ell-2, repeat q chunks. Compute lower=upper+1-K. Sweep
   flags and consume v=upper,...,lower for each axis, then subtract K from upper
   when another chunk remains.

This is exactly the canonical order: long top slots, extracted low planes, then
chunk-major high-to-low chunks with axis order and descending bits inside each
axis chunk. Each named position appears once. Top-round participation is the
actual L flag; in lower rounds all axes participate. Both the base and v are
reset at their specified loop boundaries. In particular, short axes do not
create holes in the top-round bank addressing.

The controller emits a member of a fixed 80-symbol data instruction alphabet
at each data action. Instructions read/write a named Boolean register on a
named tape, move a named tape one cell, or perform one of eight fixed Boolean
register actions. They contain no integer operand, pointer or source index.
Production execution dispatches each instruction immediately and retains none.
The verifier can collect the stream for replay; that diagnostic program storage
is outside the producer's C bound and is disabled by default.

To seek a data position, compare its binary position counter with the target,
move one cell toward the target, update the position counter, and repeat. Every
physical data move and every counter access is charged. Address progression
uses one right move before each slot after the first. There is no reread while
returning the address head.

## Arithmetic and final restoration

For an active axis, exactly the v<a positions arrive before its h branch bit.
Store these in its stride-cell segment. On branch arrival, read and clear
pending cells in increasing v, accumulate their masked contributions, and reuse
the segment's first cell for the branch bit. Later lower positions read that
retained branch. Other positions need no data work beyond their input read.

To add branch*bit*2^v modulo 2^n, set carry to branch AND bit and ripple through
accumulator positions v,...,h. At a bit old, write old XOR carry and retain
old AND carry. The identity old+carry=(old XOR carry)+2*(old AND carry) proves
the ripple. The accumulator therefore equals the sum of precisely the products
whose branch and lower bit have both arrived. At EOF it is S modulo 2^n.

For direction -, when h>0, complement and increment all n accumulator bits.
Unlike PR3582, this implementation also performs that harmless negation in an
empty top round. The result is still zero; its extra accesses/gates are charged.
Direction + and h=0 omit the negation. Read accumulator positions h,...,0 into
the output, followed by ell-h zeros. This is sign*2^(ell-h)*S modulo 2^(ell+1).

Counter-controlled scans erase all P bank cells and all n accumulator cells.
Seek every data head to zero, return the descriptor head by its caret delimiter,
erase each of the 21 counters including its delimiters and reset the Boolean
registers. The persistent Boolean one is finite control in its initial state.
The output remains, and the borrowed address and descriptor were never written.
This proof concerns successful valid-input execution. It does not claim a
failure/retry restoration contract.

## Data invoice and full polynomial bound

Let f=1 exactly when h>0 and direction is -. There are d*h masked additions and

    L=d*h*(h+3)/2

accumulator ripple positions. The exact Boolean counts are

    AND=d*h+L+f*n, XOR=L+2*f*n.

The exact read/write totals are

    address: reads A, writes 0;
    bank: reads d*h, writes 2*d*a+d+P;
    total: reads L+(f+1)*n, writes L+(f+1)*n;
    output: reads 0, writes ell+1.

For the chronological access positions t_1,...,t_s on a tape, set both endpoints
to zero. Its exact movement is sum |t_(j+1)-t_j|. checks.py independently builds
these access sequences from canonical named slots. Counter motion is additional
and is measured directly by the sequential counter implementation.

For completeness, a generous bound on the data tariff is 30M^2. Indeed P<=A,
d*h<=A, d*a<=A, n<=ell and L<=A*(ell+2)/2. Bank read/write accesses are at most
5A, so its movement is at most (5A+1)*(P-1). Accumulator movement is at most
A*ell+6ell by summing the sparse ripples, optional negation, output and cleanup.
The other movements are 2*(A-1)+2ell. Summing these with the displayed read,
write and gate totals gives the bound, including the extra empty-round negation.

Here is a conservative static count of the controller macros. Outside seeks,
parsing/division uses O(N+ell+D) macros. The top, low-plane and chunk passes
have A input events, at most d*a pending events, d*h contributions and L ripple
positions. Each event uses at most 30 counter macros. Finish/cleanup adds at
most 10*(ell+P+n+1), and fixed initialization/erasure has 42 counter roles.
These quantities give fewer than 100M^2 non-seek macros, with setup/erasure
separately bounded by 42*14*(W+2). A seek uses two counter macros per actual data
move and one final comparison. There are at most 30M^2 data moves, and fewer
than 10M^2 seek invocations from the displayed access totals and four returns.
Thus seeks use at most 70M^2 macros. Charging at most 14*(W+2) per macro, plus
descriptor sweeps and the data tariff, stays below 5000M^2*(W+2). Descriptor
sweeps need at most a constant times N*(ell+1) actions and are included.

Finally W+2=N+4<=4M. The exact capacity formula and P<=A give C<=90M and the
binary encoding bound 182M. All bounds concern mathematical tape cells and
primitive actions, not Python allocation, timings or an optimized constant.

## Source allowance and remaining join

Under the retained D*ell=O(p) source band, A=O(p), ell=O(p), and N=O(p). The
complete descriptor/counter/data producer therefore has O(p^3) transitions and
O(p) tape cells. For fixed 0<epsilon<1 with d_source<=b_d*p^epsilon and
r>=2^(a_r*p/d_source), log2(r)>=(a_r/b_d)*p^(1-epsilon). Consequently r
eventually exceeds every fixed power of p, and this producer fits the source's
asymptotic O(rp) per-record exponent-production allowance. This gives no explicit
cutoff or optimized quadratic total-machine claim.

The output is one header. Address enumeration, coefficient packets, signed
rotations, truncation, spectators, caller reservations, dirty caller return and
the complete layer/root invoice remain separate. This is a uniform encoded
header-producer implication, not a complete transform or supplier admission.
It establishes no new multiplication exponent and changes no selected frontier.
