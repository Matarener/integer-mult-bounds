# A stateful sweep of synthetic twiddle headers

This is an author-written all-finite-shape proof. Independent human and formal proof-kernel review are unclaimed. Finite executions below corroborate the proof, not its unbounded quantifiers.

## Contract and premises

Let ell>=2, 1<=K<ell, D>=1, and let each axis have ell or ell-1 named bits. Put A equal to their total width. In round 0<=h<ell let I consist of axes containing position h, d=|I| and n=h+1. The retained transform and canonical circuit proof give the physical MSB-first slot order and

    L_i = sum_(v<h) 2^v x_(i,v),  beta_i=x_(i,h),
    S = sum_(i in I) beta_i L_i mod 2^n,
    E_- = -2^(ell-h) S mod 2^(ell+1),  E_+ = -E_-.

The exact runtime oracle is the unchanged canonical circuit.py. These three canonical files, including the circuit's actual mathematical proof premise and frozen transform source, are live inputs in SOURCES.json and VERIFY.json. There is no pending mathematical premise. PR3571/PR3582 supply credited algorithmic context, not an invoked theorem. Their comparison heads are separate in COMPARISONS.json.

The changed input contract is a whole address stream. Start all data tapes blank. Emit headers for physical binary addresses 0,1,...,M-1, with 1<=M<=2^A, and advance the owned address once after every header, modulo 2^A. A whole-cube stream has N=2^A records. This is neither an arbitrary borrowed-address reader nor a shortcut for a noncanonical record order. The source's linear storage scan admits this address order; joining actual packets remains unimplemented.

Four Boolean tapes hold an A-cell little-endian physical-address odometer, a P=max(1,d*n)-cell cache, an n-cell little-endian accumulator and an ell+1-cell MSB-first output. Each participating axis has one contiguous cache word containing its h low bits followed by its branch. Every tape head starts at zero. Only current-cell reads/writes and unit head moves access data. At most twelve transient Boolean values suffice for old/cached bit, branch, sign, carry, operands and intermediate gate results. All growing data reside on the tapes.

A supplied immutable shape scheduler identifies each physical slot and cache offset and supplies loop extents. Its descriptor construction, parsing, integer counters, participation/offset lookup and encoded instruction control are outside the charged data bill and cell bound. Carry stopping uses the current Boolean bit. Python objects, diagnostic counters and invariant/observer inspection are also outside those mathematical counts. This is a family of charged data-tape programs, not a complete encoded uniform machine. The executable caps ell<=256, axes<=64 and M<=4096.

At each output pause an external consumer may read the header, preserving other tapes and returning the output head to its pause position. The bill excludes that consumption, its computation and record movement. Only one header is stored. Materializing the entire stream needs M*(ell+1) output cells in addition. All owned tapes are blank with heads at zero on normal return, including after a partial prefix. Arbitrary dirty initial tapes are not accepted.

## Incremental identity and invariant

At each record boundary, the address is the record number modulo 2^A, every cached bit matches its named address bit, and the accumulator is S. This holds at the all-zero start.

An increment flips trailing one bits to zero, then the first zero to one; at the last address all A bits flip to zero. Process those flips sequentially. If an irrelevant named slot flips, S is unchanged. If a participating lower bit v<h changes from old to 1-old, beta_i is unchanged and

    delta S = (1-2*old) beta_i 2^v.

If a participating branch flips, its low word is unchanged during that individual flip and

    delta S = (1-2*old) L_i.

Update the cached bit and add the indicated signed word modulo 2^n. Several factors may change in one carry chain. Applying these exact single-bit identities in chronological order accounts for their cross terms automatically. In particular it would be wrong to price every flip against the pre-increment cache. At every intermediate flip the cache and accumulator describe the same intermediate address.

The branch update reads its contiguous h-bit low word in increasing order, with a zero top bit. A lower-bit update reads beta once and uses a word with that bit only at v. To add or subtract a word u, set sign=old, carry=sign and for each little-endian position form

    b=u_t XOR sign; mixed=z_t XOR b;
    result=mixed XOR carry;
    next_carry=(z_t AND b) XOR (mixed AND carry).

The carry terms cannot both be one. Thus z_t+b+carry=result+2*next_carry, proving the modular sum by induction. Complementing u and starting carry at one gives subtraction. Each position uses four XOR and two AND gates; no unit-cost integer arithmetic is assumed. Even a zero delta executes the same ripple. This proves the invariant after the increment, including full wrap.

## Output and restoration

For E_+, read S from high to low and append ell-h zero bits. For E_-, negate S in place, emit that same layout, and negate S again. Two's complement at each position uses two XOR and one AND, with initial carry one. Negation is an involution modulo 2^n, so the retained S is restored before any increment. Both directions also work at h=0 or d=0, when S is zero. The output has n+ell-h=ell+1 bits and exactly the required residue.

After observation, overwrite every output cell with zero and return its head. After the final advance, overwrite every cell of all four tapes with zero and return all heads. These cleanup scans and even the redundant final output clear are charged. A consumer exception also triggers that cleanup, assuming reliable cleanup primitives and no second interruption. Failure costs are separate from the normal invoice. The runner is single-use after failure or success.

## Exact flip count and invoice

For increment numbers k=1,...,M, physical little-endian bit j flips exactly when 2^j divides k, including the final whole-cube wrap. Hence

    F(M,A) = sum_(j=0)^(A-1) floor(M/2^j) < 2M,
    F(N,A) = 2N-2,  N=2^A.

Let R be the number of relevant flips, and f=1 for forward output and zero for opposite. If w_j is one when physical bit j is a participating position <=h, then R=sum_j w_j floor(M/2^j). The Boolean invoice is

    AND = 2nR + 2fnM,
    XOR = F + R + 4nR + 4fnM.

F and R additional XORs complement address and cache bits. For reads/writes and movement, independent.py generates the exact access target sequence from shape, record index and divisibility, without machine data, head state or counters. Every consecutive target contributes its absolute distance. Reads/writes at one target are counted separately. Each sequence begins at zero and includes all output and final cleanup scans. This gives an exact finite shape-only invoice for every M, while the identities above give independent closed forms for flips and gates.

The executing Tape.seek performs exactly that many unit moves; read/write count only current-cell operations. The finite comparison checks every per-role reads/writes/moves entry, AND/XOR count, capacity and total. It does not infer equality from timing or Python memory use.

## Uniform linear amortized data bound

P<=A, since each participating n-bit word is contained in its axis. Let X=A+ell+1. One relevant flip has at most 2+h bank operations and at most P+2h bank moves. Its accumulator has 2n accesses, at most 2h moves and 6n gates. Its cache complement adds one gate. This is at most P+13n+3 data operations, bounded by 17X. Irrelevant flips do none of those operations.

The address has F reads, F writes and F XORs. Each increment with q flipped bits has at most 2(q-1) address moves, including the head return, so address work is at most 5F. One header uses at most two negations, n accumulator output reads, ell+1 output writes, ell+1 output-clear writes and four ell output moves. Accumulator moves in those phases total at most 6h, including the first opposite-direction seek. Header work is at most 11n+6h+6ell+2, bounded by 25X. Final clearing uses at most three times the sum of tape extents, hence at most 9X. Therefore

    T <= (17X+5)F + 25MX + 9X
      <= 100MX + 10X,
    C = A+max(1,d*(h+1))+h+1+ell+1 <= 2A+2ell+2.

The loose constants include degenerate shapes and partial prefixes. F<2M proves O(M(A+ell)) data work and O(A+ell) data cells. Each output requires ell+1 writes, so T>=M*(ell+1) in this output contract. No general time optimum is claimed. Under the retained A=O(p), ell=O(p) bands, the whole cube costs O(Np) charged data work, versus O(Np^2) obtained by independently applying the existing per-address data upper bound. This is an amortized asymptotic upper-bound improvement under a changed source contract, not a measured speedup or a strict saving for every finite shape.

## Expansion decision and limits

The retained record scan allowance is O(Nrp). This data module's O(Np) fits it; it does not establish the complete invoice. Proved here are arithmetic, source-order enumeration, charged data movement, normal blank return and a bounded current-header buffer. Supplied shape scheduling is an explicit premise. Encoded scheduler/counters, actual signed-packet consumption, packet spacing/spectators, descriptor leases, arbitrary dirty restoration, native/root/ordinary hosting, analytic recovery and the complete supplier bill are unknown here. Unknowns are not zero. Continue only to one specified caller boundary whose complete allowance is stated; do not launch dependent supplier optimization from this local result alone.

RESULT.json records 480 complete finite fixtures and 110520 headers, 277 partial-prefix headers and 21 wide valid-state transitions through ell=256. The wide transition harness installs a valid state diagnostically without charging initialization and is not a full wide stream replay. Small complete streams agree with independent named arithmetic, the pinned canonical circuit and every exact invoice. Source/hash, arithmetic, movement and erasure mutants fail under optimized CPython. Neither full production GL64/T74 nor human/formal acceptance, supplier admission, kappa or selected-frontier improvement follows.
