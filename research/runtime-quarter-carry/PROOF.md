# Runtime carry rotation in the original owner

The generic interface has positive canonical binary P,Q,S and C+1, where
0<=C<Q. Tape0 holds a complete Boolean stream in [P] x [Q] x [S] order.
Each marked input head starts on its first bit. The eight private tapes in
kernel.WORK are blank, with heads at their separate origins. These are valid
input premises, not claims about arbitrary occupied work tapes. Other tapes
can contain arbitrary data and are preserved. The two fixed tables perform
x -> x+C mod Q and x -> x-C mod Q. Neither table depends on an input value.

## Literal construction and endpoint

The retained finite counter macro copies and converts each extent, including
C+1, to unary. It restores each input and its own binary work. A local scan
removes one unit from the last count. A simultaneous scan checks C<Q. The
machine transfers C units from the Q counter to an empty counter. This gives
L=Q-C and R=C, at a cost linear in Q. Every overwritten old right marker is
erased. No extra coordinate or dummy Q-sized stream is introduced.

For each prefix p, the forward gather copies the first L complete S-bit records
to bucket A and the last R records to bucket B. Each bucket retains prefix
order. Once the whole source is copied, both buckets and the original owner are
rewound. For each prefix p, the machine consumes R records from B followed by
L records from A into that owner. Thus a record at x<Q-C moves to x+C and a
record at x>=Q-C moves to x+C-Q. Reversing the two gather and two emit segments
gives x-C mod Q. This argument includes C=0, Q=1, all payloads, and all positive
prefix and record lengths. It does not assume a sparse payload.

The owner gets its right marker and returns to its first bit. Each bucket is
consumed, including both of its marker positions at cleanup. The private unary
counts, their markers and binary work are erased by literal backward scans.
Their old tails are already blank. All eight private heads return to their
original origins. P,Q,S,C+1 and their heads are unchanged. The program never
reads, writes or moves the heads on tapes1,6,9,16,17,18. There is no separate
output owner, owner rename, computed address or uncharged interchange.

## Exact generic ledger and tight uniform bounds

Let V=PQS, n(N)=bit_length(N), b(N)=popcount(N), and

    c(N) = 24N - 7b(N) + 15n(N) + 12.

The retained binary-to-unary macro has exactly c(N) transitions. The following
table counts every instruction of either generic orientation. A rewind from
relative head h costs 3h. A record copy costs (11+consume)S+4, except that the
first record saves 3S because its counter already starts at the first unit.

| Region | Transitions |
| --- | ---: |
| Eight private marker checks and writes | 24 |
| Four conversions | c(P)+c(Q)+c(S)+c(C+1) |
| Trim C+1 to C | 6C+11 |
| Q return, compare C<Q, and both returns | 11C+11 |
| Start right length and seek Q end | 3Q+2 |
| Transfer C units | 10C+1 |
| Both complete payload phases | 23V+20PQ+25P+8-3S |
| Endpoint checks, bucket/owner markers and rewinds | 9V+18 |
| Complete private erasure | 4V+4P+4S+4Q+4C+48 |
| Halt | 1 |

Their sum is

    T = c(P)+c(Q)+c(S)+c(C+1)
        +36V+20PQ+29P+S+7Q+31C+124.

For all positive N, c(N)<=44N. For N>=2, n(N)<=N/2+1 and b(N)>=1,
so c(N)<=63N/2+20. For Q>=2, this last upper bound at Q also covers N=1.
Since C+1<=Q and C<=Q-1, it follows that

    T <= 36V+20PQ+73P+45S+101Q+133 <= (565/2)V  (Q>=2).

For Q=1, C=0 and c(Q)=c(C+1)=44. Direct substitution gives

    T <= 36V+93P+45S+219 <= 393V.

Both orientations attain T=393 at P=Q=S=1. Thus393V is a tight uniform
transition bound for these fixed tables, not a lower bound on other algorithms.

Let M=max(n(P),n(Q),n(S),n(C+1)) and B be the sum of these four lengths.
The exact sum of visited intervals, including all nineteen initial head
positions, cleared cells, inputs and markers, is

    W = 2V+P+S+Q+2C+M+B+33.

The source and two buckets contribute2V+6. The four binary inputs contribute
B+8. The unary counts and binary work contribute P+S+Q+2C+M+13. The six
unused tapes contribute one initial head position each. This includes the old
tail of C+1 and the largest intermediate left length Q. Consequently

    W <= 2V+2P+2S+5Q+M+31 <= 43V.

Equality holds in the same one-bit case. Arbitrary translated origins do not
change these interval sizes. Unvisited spectator data is preserved; it is not
counted as newly visited work space.

## Physically supplied quarter code

The linked program has a marked, preserved five-bit LSB-first packet on tape16.
Its integer value is k+16 with -16<=k<=12. This packet is supplied by the caller.
Its production from a low cache is an explicit remaining obligation. The
machine reads all five bits, checks the right marker, rejects values29..31,
returns the code head and enters one of29 finite producer tables. No host value
selects the runtime branch. Direction alone selects one of two fixed programs.

The retained PR5332/5846 producer reads odd positive Q and writes the canonical
descriptor C+1, where C=k*4^-1 mod Q, in owned blank tape14. Its translated
local-instruction proof is retained in inputs/descriptor-PROOF.md. For Q=1 it
uses its explicit branch and writes1. The new generic kernel consumes this
descriptor as a preserved input. A literal eraser then clears the descriptor
and both markers and returns tape14 to its blank origin. The packet on tape16,
all extents, all spectator data and all spectator heads are preserved.

The dispatcher takes36 transitions. A final halt adds one; replaced component
halts and linking gotos both cost one. For n=bit_length(Q), production costs
at most64n+128 and erasure costs at most8n+8. Thus the extra cost is at most
72n+173. When Q>=3, the generic bound above improves to(722/3)V, and this extra
cost is at most(389/3)V. Their sum is(1111/3)V<468V.

For Q=1 the literal producer costs22, the eraser16, and dispatch plus final
halt37, for75 extra transitions. Hence T<=393V+75<=468V. The one-bit case
attains468, for all29 valid packets and both directions. The linked transition
bound468V is therefore tight for these tables.

The code tape adds six visited positions to the generic ledger. For Q=1 the
producer visits exactly the descriptor positions already in that ledger; thus
W<=43V+6<=49V, with equality in the one-bit case. For Q>=3 the generic bound
above gives W<=(59/3)V. Even charging the full producer interval n+4 as extra,
plus the six code positions, adds at most(13/3)V. This gives24V<49V. The tight
uniform visited-space bound is49V. These bounds include erased storage.

## Every released G20 fused carry fits the packet

For each of the111 ports, both released PR5820 bases and both directions, form
the exact rational RIGHT product S. The checker verifies both inverse products.
For each column let D be its common denominator and A_i=D*S_ij. The actual
products have D in{1,4}. For canonical low digits0<=l_i<q and odd q>1, let

    N = sum A_i*l_i,
    t = N*D^-1 mod q,  0<=t<q,
    K = (N-D*t)/q.

K is an integer, and the fused high correction is K/D. If
u=sum min(A_i,0) and v=sum max(A_i,0), then

    (q-1)(u-D) <= N-D*t <= (q-1)v.

Because u-D<0 and K is integral, K>=u-D+1. If v>0, K<=v-1; if v=0,
K<=0. Apply these bounds to each of3552 actual columns. All resulting quarter
codes k=4K/D lie in[-16,12]. This is a uniform envelope for every odd q, every
low row and every high width. It does not assert that each envelope endpoint
occurs at each port. The high modulus Q=q^(w-1) is odd, including Q=1 at w=1,
so the physical producer applies at every width.

The exact split identity

    (l+qh)S = t + q(hS+K/D)

shows why this is the correct high translation after the homogeneous map.
The checker tests the full-width identity by a separate modular product and
binds one actual k=-3, q=5 witness to a complete Q=125 physical rotation. Its
residue is93, which is outside the bounded-translation premise of older leaves.

## Verification and limits

Both independent literal interpreters execute the same serialized tables and
agree on every cell, head, step and visited interval. The complete small tests
include all Boolean payloads through Q=4, all offsets through Q=9, both signs,
nontrivial prefixes and record lengths, all29 packets, Q=1 and Q=125. Exact
generic ledgers are checked for every generic run. Whole-bank inverse tests
and semantic rejection controls test restoration and the declared boundary.
The loops and inequalities above prove the unbounded claims; finite tests
alone do not prove them. RESULT.json records the exact finite coverage.

This is a complete carry leaf at a supplied stream and code interface. It does
not form or select the packet from an actual low cache, stage a whole T word,
commit the new low type, place G20 ROW heads, supply ancestor stock/P3, or close
the full caller invoice. None of the five framework assumptions is discharged.
There is no new kappa claim or selected-frontier change.
