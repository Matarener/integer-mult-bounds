# Encoded fixed-round twiddle diagonal on a full positioned cube

This is an author-written, source-relative proof for every finite admitted
shape. Executable examples corroborate it; they do not formally verify its
unbounded quantifiers. The supplied cube is already in the retained transform
layout. The result is the complete diagonal for one fixed round, including
address enumeration, packet transport and reusable-machine cleanup.

## Contract and exact endpoint

Let $\ell\geq2$, $r=2^\ell$, $1\leq K<\ell$, $0\leq h<\ell$, and let the
$D\geq1$ axis flags be long or short. Axis $i$ has $a_i=\ell$ or
$a_i=\ell-1$ address positions. Put $A=\sum_i a_i$ and $N=2^A$.
The unchanged PR3593 descriptor specifies these fields and a direction.
The width descriptor is a framed unary encoding of $w\geq2$.

The full source is a framed stream `@(^bits$)^N!`: the notation means $N$
consecutive packets, not literal exponent or parentheses characters. Each
packet contains $r$ Gaussian coefficients in increasing coefficient order,
real component before imaginary component, with each component a signed
$w$-bit two's-complement word in MSB-first order. Thus a packet has
$B=2rw$ payload bits. The descriptors, allocation extents and stream agree;
borrowed heads begin at zero and private storage is allocated blank before
the paid initialization. Distinct
physical roles have separate backing storage. Every component that this
particular diagonal negates must have a representable negation. This excludes
the signed minimum at those positions, without excluding it where no negation
is requested. Arbitrary malformed tapes and interrupted-run recovery are
outside the successful-execution theorem.

For the physical address of packet $j$, write $x_{i,v}$ for its named slot
$(i,v)$. Define

$$
E_j=\sigma 2^{\ell-h}\sum_{i:h<a_i}x_{i,h}
                   \sum_{v<h}2^v x_{i,v}\pmod {2r},
\qquad 0\leq E_j<2r,
$$

where $\sigma=-1$ for the forward direction and $+1$ for the opposite.
If the input polynomial packet is $f_j\in\mathbb Z[i][y]/(y^r+1)$, the
output at the same physical record position is exactly $y^{E_j}f_j$.
There is no rounding or coefficient reordering outside this packetwise
signed rotation. The full source and borrowed descriptors are preserved;
the full output is retained; heads return to their origins and auxiliary
data are erased as specified by the implementation's boundary contract.

## Physical order comes from the source

The foundational convention is
`upstream/build/sections/02-streams.tex`, lines 17--23: arrays are stored
lexicographically with the first coordinate most significant, and addresses
are implicit in stream positions. The retained transform source
`06-transforms.tex`, lines 236--239, starts with axis-major slots and
decreasing $h$ within each axis. Lines 243--274 extract the listed prefix
slots and transpose the remaining chunks; the resulting permutation $L$
moves a record at address $x$ to address $Lx$, preserving its polynomial
suffix. Consequently the first physical named slot is the most significant
bit of the sequential record index. This is also the explicit input
convention in `research/synthetic-twiddle-circuit/PROOF.md`.

For $b=(\ell-1)\bmod K$ and $q=\lfloor(\ell-1)/K\rfloor$, the prefix is
the long-axis top slots in axis order, followed by slots at
$v=b-1,\ldots,0$ with axis order inside each $v$. The suffix is chunk-major,
then axis-major, then decreasing bit position inside each chunk. In the
source's actual $\ell=6,K=2$, long/short example (lines 278--282), the order is

$$
(1,5),(1,0),(2,0),(1,4),(1,3),(2,4),(2,3),
(1,2),(1,1),(2,2),(2,1).
$$

Thus $A=11$ and the pass visits all $2048$ physical record positions.
No address permutation is charged as free here: positioning by $L$ is an
input premise. At the forward or opposite round boundary the source's
lines 373--380 identify the named branch/lower bits used in the displayed
exponent. The proof does not supply the butterflies that establish that
boundary.

## Enumeration, pairing and exact arithmetic

The pass derives unary $\ell$ and unary $A$ through scans of the actual
descriptor. For each long flag it appends $\ell$ units to the latter; for
each short flag it appends $\ell-1$. These are physical scans, not a host
decoded shape controlling execution. It initializes the actual producer
address tape to $A$ zero bits using that unary extent.

Before iteration $j$, maintain that the address tape is the MSB-first
encoding of $j$, the full-source head is at packet $j$, and exactly the
first $j$ result packets have been appended. The source packet is copied
by primitive accesses to the same reusable framed buffer. The unchanged
PR3593 controller reads the actual address and actual descriptor and emits
its actual header tape. Its proved endpoint is $E_j$ above, with borrowed
heads returned and its private bank, accumulator and counters erased.
The unchanged PR3611 consumer receives that very header tape and buffer.
It supplies the exact signed rotation, restoring its borrowed inputs and
erasing its private working tapes.

For completeness, write $E_j=e r+s$, $0\leq s<r$, $e\in\{0,1\}$.
The consumer moves the last $s$ coefficients to the front with sign
$(-1)^{e+1}$ and follows them by the first $r-s$ coefficients with sign
$(-1)^e$. This is precisely reduction of $y^{E_j}f_j$ modulo $y^r+1$.
The sign premise makes every two's-complement negation exact. The case
$s=0$ is a signed copy, including the empty moved segment.

The pass copies the complete framed result to the full output, physically
clears reusable result and packet storage, and advances the source past its
packet delimiter. Binary carry starts at the rightmost address bit and
returns the address head. For $j<N-1$ it changes $j$ to $j+1$; on the
all-one word it resets every bit to zero and reports wrap. Thus the loop
visits every address once and terminates after precisely $N$ packets.
The closing full-stream marker agrees with that wrap under the admission
contract. Induction proves both the endpoint and the absence of skipped,
duplicated or mismatched packets.

## Reuse and paid restoration

Reuse means the same physical tapes, not allocating a fresh controller or
consumer at every record. PR3593's first constructor physically initializes
its 21 counter tapes by descriptor scans; these actions are part of the
invoice. Each successful controller execution erases those counters,
including their delimiters. The pass rearms those same tapes by paid scans
of the descriptor and resets the single finite `first` flag. Its Boolean
registers already have their documented reset values. Host allocation
dimensions only admit capacities and diagnostic bounds.

The consumer's private prefix, suffix, word and countdown tapes are cleared
by its existing successful-return contract. Its retained output is copied
and physically cleared, including the allocation guard, before the finite
one-shot flag is rearmed. The producer header is physically erased after
every consumption. The reusable
source buffer and unary work tapes are likewise restored by scans. Returning
the full input and output heads is a traversal of the actual streams and
is included in the cost. No head index is assigned as a substitute for
movement and no host-sized loop supplies the execution schedule.

## Work and asymptotic source allowance

The physical access tariff counts each tape read, write and unit move.
Explicit Boolean operations and control gates are recorded separately and
included in the combined action invoice. This is not a claim that a Python
instruction or every finite-control transition is exactly one gate. The
fixed finite-control implementation has a constant transition overhead per
recorded action or macro entry, giving the same asymptotic bound.

For an exact stock count, put $n=h+1$, let $d_h$ be the number of
participating axes, and set $a=b$ if $b\leq h<\ell-1$, otherwise $a=0$.
Write $P=\max(1,d_h\max(a,1))$ and let
$Q=\ell+K+h+D+6$ be the producer descriptor's interior length.
The unchanged producer has 26 physical tape roles and capacity

$$C_{\rm producer}=A+P+n+\ell+1+22Q+86.$$

The pass adds exactly 12 physical roles: full input and output, unary $A$
and unary $\ell$, the width descriptor, the reusable source packet, and
the consumer's six private tapes. Producer address/header/descriptor tapes
are shared by identity rather than duplicated; consumer borrowed roles
are views of these existing tapes. The two full streams each have
$2+N(B+2)$ cells. The unary tapes have $A+2$ and $\ell+2$ cells,
the width descriptor has $w+2$, the packet buffer has $B+2$, and the
consumer private tapes have $3B+w+2\ell+20$ altogether. Thus there are
exactly 38 distinct physical tapes, of total capacity

$$
C=C_{\rm producer}+2N(B+2)+4B+2w+A+3\ell+32.
$$

Excluding the explicitly retained full input and output gives auxiliary
capacity $C_{\rm producer}+4B+2w+A+3\ell+28=O(rw+p)$ under the bands
below. These are finite-alphabet tape cells, not Python memory bytes.
All alphabets have fixed size, so fixed binary symbol encodings change
this bound only by a constant factor. The full output is intentionally
materialized and is not concealed in the auxiliary bound.

Let $p$ obey the retained source bands $D\ell=O(p)$, $\ell=O(p)$ and
$w=O(p)$. Then $A=O(p)$ and the producer descriptor has length $O(p)$.
The producer costs $O(p^3)$ per address, including initialization and
restoration. The consumer, packet copying and reusable-buffer clearing
cost $O(rw+\ell)$ per packet. Enumeration costs $O(A)$ per increment even
without exploiting amortized carry. Descriptor-derived unary setup and
counter rearming fit the polynomial term. Final full-stream head returns
cost $O(Nrw)$. Hence total work is

$$O\bigl(N(rw+A+p^3)\bigr).$$

For fixed $0<\epsilon<1$ and positive constants $a_r,b_d$, the additional
retained bands $d_{\rm source}\leq b_d p^\epsilon$ and
$r\geq2^{a_r p/d_{\rm source}}$ imply
$\log_2r\geq(a_r/b_d)p^{1-\epsilon}$. Thus $r$ eventually exceeds every
fixed power of $p$, in particular the power needed to absorb $p^3$ into
$rp$. The complete diagonal therefore costs $O(Nrp)$ eventually. No
numerical cutoff or optimized constant follows from this argument.

## Attribution and limits

The transform text already supplies the diagonal formula and split/merge
arithmetic. The synthetic-twiddle circuit package supplies the named-slot
interpretation. Nick Petalas's PR3593 supplies encoded header production;
PR3611 supplies the physical signed packet consumer, building on the
retained signed-packet lineage. The present contribution joins those
unchanged operators through encoded full-cube enumeration, physical stream
transport and same-tape reuse. Source pins and notices accompany the package.

The executable retains PR3593's finite limits $2\leq\ell\leq32$ and at
most 16 axes. Full-cube replay is practical only for small admitted shapes;
it is evidence for the construction, not exhaustive verification of the
general theorem. This result does not supply a complete transform, truncated
layer, layout constructor, butterfly, caller reservation, rounded recursive
precision theorem or complete multiplication invoice. It changes no selected
frontier or multiplication exponent.

## Open next questions

Bind this fixed-round pass to an actual butterfly round with its full
source/output format and paid movement. Then account for truncated domains,
spectators and the complete retained transform schedule without replacing
the physical cube-order contract by an uncharged permutation.
