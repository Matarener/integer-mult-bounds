# Exact framed XOR endpoint corrections on two tapes

Prepared by Dugongue with substantial OpenAI Codex assistance. Apache-2.0.
This is an informal proof of explicit finite-alphabet machine families.
The new construction has not received a Lean kernel audit or independent
human review. Exact finite transition replays corroborate it.

## 1. Statement, representation and cost convention

Let h ≥ 0, N = 2^h, and 0 ≤ δ < N. For a record vector w define

    (X_δ w)_j = w_(j xor δ),       0 ≤ j < N.

Use two tapes, each with alphabet {0, 1, #, blank}. A framed record vector is

    # w_0 # w_1 # ... # w_(N−1) #,

where every w_j is a finite binary word. Both heads begin at the first #.
Origins may be any integers on their respective tapes. Tape locations outside
the declared windows contain arbitrary symbols. No blank infinite exterior
or clean full output buffer is assumed.

One transition observes both scanned symbols, writes at most one symbol on
each tape and moves each head by −1, 0 or +1. A designated halt state has no
outgoing transition. This is the ordinary synchronous multitape-step
convention. It is not the repository's separate read/write/move event count:
at most six such elementary events occur per transition (two reads, two
writes, two moves). Thus 6T is a conservative event-count conversion.

**Theorem A (borrowed-input copy).** For every h and δ the supplied compiler
produces a finite two-tape machine that, for every framed vector of N equal
width-B words, returns X_δ w in natural record order on the second tape,
preserves the complete input tape, restores both heads, and changes no output
cell outside its declared window. Interior output dirt may be overwritten.
Its exact transition count is

    T_copy = 2NB + 4N + (B+2)Q_h(δ),
    Q_h(δ) = V_h(δ) + 1 + 2 rev_h(δ),
    V_h(δ) = ∑_(j=0)^(N−2) |((j+1) xor δ) − (j xor δ)|,

where rev_h reverses the h mask bits. In particular,

    Q_h(δ) ≤ (h+1)N,
    T_copy ≤ N((h+3)B + 2h + 6).

The online machine uses no counters, address arithmetic or recursive Fourier
oracle. Its generated control has exactly 2(2N+Q_h)+1 states, including halt,
and 16(2N+Q_h) defined transitions. Compilation and stored control are finite
and charged, not free uniformity assumptions. The same machine also permutes
variable-length records, with the exact weighted invoice in section 3.

**Theorem B (in-place correction with restored dirty scratch).** For δ ≠ 0,
the second compiler produces a two-tape machine that transforms the first
framed, equal-width vector in place to X_δ w. It restores an arbitrary dirty
B-bit scratch record on the second tape, restores both heads, and preserves
both exteriors. If k is the highest set-bit index of δ, put

    H_h(δ) = (N−2)2^k + 2N − 2.

Its exact transition count is

    T_inplace = (3N/2)(2B+3) + (B+2)H_h(δ).

For δ = 0 the compiler returns a genuinely halted identity machine with zero
transitions. The in-place construction needs only B+2 scratch cells, including
two separators, but its time may be quadratic in N. The copy construction uses
N(B+1)+1 output cells and has the smaller O(NB(h+1)+N(h+1)) bound. These are
different time/space contracts; neither cost is silently substituted for the
other. B = 0 is admitted by both constructions.

The machine is fixed once h and δ are fixed and works for every B and every
payload. There is a uniform explicit finite compiler for all h, δ. We do not
claim a single fixed-control online machine accepting unbounded h as data at
the displayed cost. In the P112 application h = 9 is fixed.

## 2. Explicit transition templates

The control program is a finite sequence of the following macros. Each macro
has its own entry/scan states and a fixed successor state. Every template is
expanded over the four-symbol alphabet in `machine.py`; there is no hidden
random-access operation in `run`.

R0 starts with tape 0 at a separator. It moves that head right once, scans
binary payload symbols right until the next #, and takes one stationary
transition to its fixed successor. Tape 1 does not move or change. For a
crossed word of length b it costs b+2 transitions. L0 is the left version.
L1 moves left through one record on tape 1 while leaving tape 0 alone, with
the same b+2 count. These macros may read a symbol on the other tape but their
actions are independent of it. They write no tape cells.

C starts with tape 0 at the separator before the desired input word and tape
1 at the separator position for the next output word. It writes # on tape 1
and moves both heads right. For each input bit it writes that same bit to
tape 1 and moves both heads right. On the closing input # it writes # on
tape 1, stays put and enters its fixed successor. Its count is b+2; the input
head now lies at the following separator, not at the copied word's start.

These two-state macros each have 16 defined transitions across entry and
scan states. All input writes are absent. Invalid symbols or missing
separators can block; the theorem's precondition is a well-formed framed
input. Verification uses explicit transition limits for malformed controls.

For in-place work, W swaps one equal-width record on each tape. It moves
both heads right from #, swaps the two scanned bits in each transition and
moves right, then moves both heads left on the closing pair of #. A rewind
state scans the two binary words left to their opening separators and takes
one stationary transition to the successor. The count is 2B+3. Both heads
return to their entry separators. W has three states and 11 defined
transitions. Equal word width is required: mismatched closing separators
block. W never changes a separator or any exterior cell.

The interpreter makes exactly one finite table lookup, bounded-symbol write
and unit move per transition. Its host dictionaries represent tape storage;
they do not supply address jumps to the simulated machine. All arithmetic
that selects the visit order occurs in the finite program generator.

## 3. Borrowed-input permutation and exact travel

Let f(j) = j xor δ. Before output record j, issue enough R0 or L0 macros to
move the input head from its current record separator to separator f(j),
then issue C. The input head is now at separator f(j)+1. After all N copies,
return it to separator 0 with L0 macros and return the output head with N
L1 macros. Every source and output separator lies in the declared finite
windows; the C macro may visit the final closing separator but never passes it.

XOR with δ is a permutation of {0,...,N−1}. Thus every input word is copied
exactly once and the concatenated output is exactly X_δ w. The source is
never written. Every output cell from the initial to final separator is
written, and no other output cell is written. The explicit return scans
restore both heads. This proves the functional and frame statements.

The number of input record crossings outside C is

    Q = f(0) + ∑_(j=0)^(N−2) |f(j+1)−f(j)−1| + f(N−1)+1
      = N + ∑ |Δ_j−1|,

since f(0)=δ and f(N−1)=N−1−δ. Every Δ_j is a nonzero integer, so
|Δ_j−1| = |Δ_j| − sign(Δ_j). If incrementing j flips bits 0 through r,
the sign of Δ_j is positive exactly when mask bit δ_r is zero. This carry
case occurs N/2^(r+1) times. Hence

    ∑ sign(Δ_j) = ∑_(r=0)^(h−1) (1−2δ_r)2^(h−1−r)
                = N−1 − 2 rev_h(δ),

and Q = V_h + 1 + 2 rev_h(δ). This also holds for h=0: Q=1, because the
single C leaves the input head at its closing separator before return.

There is an independent recurrence for V. Let d be the low h−1 bits of δ.
Then V_0(0)=0 and

    V_h(δ) = 2V_(h−1)(d) + J,
    J = 1+2d                 if the top mask bit is zero,
    J = 2^h−1−2d             if the top mask bit is one.

The two halves have identical variation and J is their boundary jump.
Since J ≤ N−1, induction gives V_h ≤ (h−1)N+1, including h=0. Therefore
Q ≤ (h+1)N. Copy and output-return scans cost NB+2N each; input seeks cost
(B+2)Q. This proves the exact and upper-bound times in Theorem A.

For variable lengths b_i, let c_i be the number of input-seek crossings of
the edge between separators i and i+1, including the final return. Then

    T_copy = 2∑ b_i + 4N + ∑ c_i(b_i+2),     ∑ c_i = Q.

`exact_cost` computes these edge counts independently of the transition
table. Equal-width cost is consequently independent of payload values.

## 4. In-place swaps and dirty-scratch restoration

For δ ≠ 0, f is an involution without fixed points. Enumerate the N/2 pairs
(a,b) in increasing a, where b=a xor δ and a<b. For each pair seek a, issue
W; seek b, issue W; seek a, issue W. If their initial contents are A, B and
the scratch content is D, the triple evolves as

    (A,B,D) → (D,B,A) → (D,A,B) → (B,A,D).

Thus the two data records are exchanged and arbitrary dirty scratch is
restored. Each W returns its two heads, so scratch remains at its origin
between operations. Finally return the data head to its origin. Different
pairs are disjoint, proving the exact in-place XOR permutation and both
frame/restoration conclusions. No clean scratch assumption enters the proof.

Let 2^k be the highest set bit of δ. The representatives are exactly the
indices whose bit k is zero; their largest value is N−1−2^k. Their visit
order contributes 2(N−1−2^k) record crossings including entry and final
return. Each pair adds 2(b−a) crossings. Across all representatives, lower
bit contributions cancel, so ∑(b−a) = (N/2)2^k. Consequently

    H = 2(N−1−2^k) + N2^k = (N−2)2^k + 2N−2.

There are 3N/2 W macros costing 2B+3 each and H seeks costing B+2. This
proves Theorem B. The generated in-place control has
2H+9N/2+1 states and 16H+33N/2 defined transitions for δ ≠ 0. Its large
control and traversal cost are explicit; no all-h quasilinear claim is made.

## 5. Endpoint correction, norms and independent streams

For any complex vector v and h-bit labels q, r, let X_q translate its address
coordinates. Then
X_q²=I and X_q X_r=X_(q xor r)=X_r X_q. With

    C_q = ((1+i)I + (1−i)X_q)/2,

the two squared scalar coefficients sum to zero and twice their product
is one, hence C_q²=X_q. All C_q commute because they are linear combinations
of commuting translations. For any finite list E,

    (∏_(q∈E) C_q)² = X_(xor E).

This directly proves the mathematical identity used by PR2297/3480, without
requiring an orthogonal-frame premise. Applying X_(xor E) once more restores
the logical vector. An encoded returned vector satisfying this endpoint
contract can therefore be corrected by Theorem A or B.

No address register is shared between blocks in this argument. If two
different registers each carry X_q, their tensor action is X_q⊗X_q and is
generally not identity, even though q xor q=0. For q ≠ 0 it moves the basis
state (0,0) to (q,q). Thus the argument does not treat PR3480's shared-register
condition as already solved. Instead it provides an explicit separately paid
way to implement each residual translation. It also does not commute a
correction across arbitrary intervening gauges: the linked library contains
an exact counterexample to such commutation.

The machine only rearranges complete bit records. Signed integers, Gaussian
integers and dyadic complex payloads retain their exact encodings. Once an
encoding is interpreted as a vector, X_δ is an isometry for every ℓ^p norm,
including the sup and Euclidean norms, and preserves the distance between
any two vectors in those norms. It adds no numerical rounding or precision
error. A predecessor endpoint error ε remains ε after correction.

## 6. The literal P112 instance and downstream boundary

The 23 mask constants are extracted as data from the exact public PR3480
verifier at `8e6fcaa557d2bff56c914f167e19929b0b656e1f`. Its source is hashed
before AST/literal extraction and is not imported or executed. This package
does not rerun the full selected archive, five-frame cover search, decoder
factorization or local-moment calculation. The universal machine theorem
works for every mask whether or not that application is ultimately admitted.

For N=512 the 23 copy machines have ∑Q=59,384. Applied to separate equal-width
streams their sum of exact transition counts is

    82,936 B + 165,872.

The 23 in-place formulas instead sum to

    2,033,554 B + 4,049,444.

These are sums of isolated two-tape primitive costs. A batch cannot use those
totals to ignore stream acquisition, buffer allocation, storage/owner changes,
framing conversion or enclosing restoration. The copy variant needs a full
owned destination; the in-place variant needs a framed scratch record of
equal width. Mapping the selected native data into either ABI and paying the
whole caller remains open. If each instance had its own disjoint tape pair,
sequential composition would realize the sum directly, but that is a different
fixed tape allocation from the actual native caller and is not silently assumed.

For complex p-grid records encoded by two signed p+2-bit components, B=2p+4
may be substituted only after the caller establishes that exact record format.
The counts are not rank-one-equivalent prices. They do not automatically
remove the predecessor's 23 provisional charges or improve a moment/κ.
Recursive Fourier calls inside these primitives are exactly zero; all local
tape work, compiled control and storage are still charged as above.

## 7. Evidence level and scope

The retained replay checks 252 copy parameter cases through h=5, 85 full
small-space basis cases, all 23 literal h=9 masks, 93 small in-place cases
and one literal h=9 in-place case (δ=19). It executes 1,168,046 unit
transitions, checks exact times, natural output order, genuine halt,
restored heads, complete borrowed-source preservation, restored dirty
scratch and finite dirty-exterior frames. The other h=9 in-place entries
are applications of the proved formula, not executed large tables.

Eight control groups include wrong masks, missing head/scratch restoration,
malformed delimiters, nonunit moves, forbidden input writes, short transition
budgets, separate complex C_E² endpoints, input/receipt mutations and actual
Git-free CLI replay. Normal and optimized registered runs retain explicit
failures. There is no claim of full native supplier execution, all-size
compiler admission, independent human review, new kernel verification,
practical speedup or new multiplication exponent.
