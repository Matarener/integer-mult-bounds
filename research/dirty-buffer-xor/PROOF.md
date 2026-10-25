# A restored dirty-buffer space–time tradeoff for XOR endpoints

Dugongue, with substantial OpenAI Codex assistance. Apache-2.0.
This is a complete informal construction and proof in the stated tape model;
the finite replays are supporting evidence, not a replacement for the proof.

## 1. Exact sufficient contract

Fix integers h ≥ 0, N = 2^h, 0 ≤ δ < N, 0 ≤ r ≤ h and R = 2^r.
The payload width B ≥ 0 is arbitrary and is **not** a compiler parameter.
On tape 0 the caller supplies

`# w_0 # w_1 # ... # w_(N−1) #`,

where every w_j is an arbitrary B-bit word. On tape 1 it supplies a
separately framed bank of R arbitrary B-bit words. Both heads start on their
first `#`. Origins are arbitrary and independent. Everything outside these
windows is arbitrary, including further delimiter symbols. Delimiters inside
the windows are part of the supplied representation; no cleanliness is assumed
of either bank's payload.

**Theorem 1 (constructive tradeoff).** The compiler in machine.py produces a
literal two-tape transition table over {0,1,#,blank} which, for every such B
and every payload and dirty bank, reaches its first genuine halt with

* tape 0 holding the same representation with word j equal to the original
  w_(j xor δ);
* the entire tape 1 unchanged, including every borrowed dirty bit;
* both heads at their original positions and both exterior frames unchanged.

Writing S = {k : bit k of δ is 1}, its exact transition count is

\[
 T_r(δ,B)=N(B+2)\sum_{k\in S}\left(5+2^{\max(k-r,0)}\right).
\]

For δ = 0 the sum is empty: the initial state is already the halt state,
and T = 0. A nonidentity program only scans the first
C = min(R, 2^floor(log₂ δ)) scratch records. Thus its total visited interval
cardinality is at most (N+C)(B+1)+2. This counts the two active windows,
not an infinite ambient tape or a charge for acquiring the borrowed bank.

In particular, borrowing at most N/2 dirty records gives

\[
 T_{h-1}(δ,B)=6N\,\mathrm{wt}(δ)(B+2)\le6Nh(B+2)\quad(h\ge1).
\]

This closes the quadratic-time/one-dirty-record limitation of PR3879 by
providing an explicit larger-space alternative. It does not assert that the
native multiplier has such a bank available, or that acquiring it is free.

## 2. Literal local templates

Every macro has an entry state, a scan state and a following entry. There is
no integer register, array index, loop counter or random access in the online
runner. All repetitions below are unrolled by the compiler into states.

**Lemma 2 (single-head record seek).** `R0` and `L0` move tape 0's head to
the following or preceding record delimiter, preserve all cells and tape 1's
head, and take exactly B+2 transitions. The entry transition moves one unit;
the next B transitions cross bits; the final transition reads the delimiter
and changes state with zero movement. Interior delimiters encountered on a
seek are precisely the next boundary, so arbitrary exterior markers are
irrelevant when the prescribed route stays inside the bank. ∎

**Lemma 3 (paired forward exchange).** `S` starts on two record delimiters,
moves both heads right, swaps each pair of scanned bits, and ends at the next
two delimiters. It takes B+2 transitions. Its entry and exit cases require
two delimiters and its bit cases require two binary symbols. Consequently,
on equal-width valid inputs it exchanges exactly the two records and
preserves every delimiter. ∎

**Lemma 4 (paired rewind).** `L` seeks one record left on both tapes without
writing. It also takes B+2 transitions and has the same equal-width
precondition. This is the leftward version of Lemma 2 on both heads. ∎

**Lemma 5 (chunk exchange).** Executing c copies of `S`, followed by c
copies of `L`, exchanges c consecutive records on tape 0 with the first c
records of tape 1. Both heads return to their entry delimiters. The time is
2c(B+2). Each `S` exchanges one distinct corresponding pair; the rewind
writes nothing. Hence the assertion follows by induction on those c forward
steps and c rewinds, with no reversal of record or bit order. ∎

## 3. Dirty restoration and one address bit

**Lemma 6 (three chunk exchanges).** For arbitrary equal-size chunks A, B
and D, exchanging (A,D), then (B,D), then (A,D) gives

\[
 (A,B,D)\to(D,B,A)\to(D,A,B)\to(B,A,D).
\]

Thus A and B are swapped and D is restored independently of its contents.
This is the classical three-swap identity used at record granularity by
PR3879; the new construction applies it to streamed chunks, rather than
rewinding the dirty bank after each individual record. ∎

Fix k ∈ S, K = 2^k and c = min(K,R). Both K and c are powers of two, so
c divides K. Partition the data into consecutive blocks of 2K records.
In each block, split both halves into aligned c-record chunks. For every
offset t ∈ {0,c,...,K−c}, pair the chunks starting at

\[
 a=\mathrm{base}+t,\qquad b=a+K.
\]

Move the data head to a. Perform Lemma 5 with the dirty prefix, seek K
records right, perform Lemma 5 again, seek K records left and perform Lemma 5
a third time. Lemma 6 swaps the desired pair, restores the dirty prefix and
leaves the data head at a. All chunk pairs are disjoint and cover both
halves. Their combined effect is therefore address XOR by 2^k.

After processing the chunk starts in increasing order, explicitly seek to
the final data delimiter at N and return to the first delimiter. These paid
scans give the same exact closed invoice even for the last chunk. They do
not depend on the contents. Scratch is restored after **each** chunk pair,
so it may be safely reused throughout this stage and every later stage.

**Lemma 7 (one-stage exact invoice).** There are N/(2c) chunk pairs.
Their exchanges cost

\[
 (N/(2c))\,3\,2c(B+2)=3N(B+2).
\]

The excursions a → a+K → a cost NK/c record seeks in total.
The increasing traversal of all a's, the final advance to N and return
to zero cost exactly 2N additional seeks: the positive increments telescope
to N and the final return has length N. Thus this stage costs

\[
 N(5+K/c)(B+2).
\]

Every seek is inside [0,N] in record-boundary coordinates; chunk exchanges
stay within their paired chunks and the first c scratch records. ∎

## 4. Assembly, control size and frames

**Lemma 8 (bit composition).** Address XOR by distinct bits commutes, and
their composition is XOR by δ. Each stage begins and ends with restored
heads and scratch. Lemma 7 therefore composes without an unpaid positioning
or clearing step. Summing and using K/c = 2^max(k−r,0) proves the time and
endpoint assertions of Theorem 1. Identity uses no stage. ∎

For an exact controller invoice, let

\[
 A=N\sum_{k\in S}(2+2^{\max(k-r,0)}),\qquad
 P=3N\,\mathrm{wt}(δ),\qquad M=A+P.
\]

There are A single-head macros and P paired macros. Every macro costs B+2,
so M is the coefficient of B+2 above. The implementation allocates exactly
2M+1 states, including the unique halt, and 16A+6P transition entries.
For each single seek there are 4 valid entry pairs, 8 bit scan pairs and
4 delimiter exit pairs. For each paired macro there is 1 entry pair,
4 bit pairs and 1 exit pair. The halt has no outgoing entry. All moves are
−1, 0 or 1. This proves both the finite-alphabet realization and its exact
control size. Compilation is a finite uniform algorithm on (h,δ,r); its
output/controller size is explicit and is **not** a free fixed-control
online interpreter for unbounded h. Compilation and storage must be included
if a caller changes these parameters online.

The local scans in Lemmas 2–5 prove footprint confinement at every prefix.
No step outside a window is needed even when B = 0. No transition writes
blank or a new delimiter; only `S` writes, and it exchanges two binary bits.
Thus the frames are unchanged and arbitrary independently shifted origins
work. This directly proves the new machine's frame property. The shared
MultitapeLocality and MultitapeFrameRule sources provide the corresponding
general locality/composition precedents, but no unconstructed Lean run is
being cited as a formal certificate for this machine.

## 5. Resource order and endpoint use

**Corollary 9 (monotone resource tradeoff).** Increasing r weakly decreases
T_r for every δ and B, because each summand 2^max(k−r,0) weakly decreases.
At maximum useful r = h−1 every set bit costs exactly 6N(B+2). At r = 0,
the deliberately streamed schedule uses one dirty record and has the exact
larger bill N(B+2)(5 wt(δ)+δ). It need not beat PR3879's different
single-record schedule. The package reports both predecessor and new costs;
the improvement is a choice with additional borrowed space, not dominance
at equal space. ∎

**Corollary 10 (exact operator endpoint).** Write X_δ f(j)=f(j xor δ).
For the PR2297/PR3480 operator
C_q=((1+i)I+(1−i)X_q)/2, direct expansion using X_q²=I gives C_q²=X_q.
The X_q commute, hence C_E² = X_(xor E). Theorem 1 realizes this residual
permutation, or its inverse (the same permutation), on each separately
framed encoded output bank. It neither requires all 23 PR3480 outputs to
share one register nor commutes a correction across an arbitrary gauge.
It preserves every ℓ^p norm and permutes coordinate errors exactly, so it
adds no numerical rounding. The endpoint operator equation comes from the
predecessors; the new result is the charged dirty-buffer realization. ∎

Converting a standard read/write/move event tariff to this transition model
costs at most six such events per transition: two reads, two writes and two
unit moves. This is an upper bound, not the multiplier's recursive tariff.

The 23-mask table in RESULT.json is the sum of **isolated** invocations at
N = 512, for each scratch capacity 1,...,256. It does not assume simultaneous
residency, free acquisition, a native rank-one price, or a free scheduler.
All 23 maximum-buffer instances are actually executed at B = 9 with distinct
payload labels for all 512 source addresses; the other
production rows use the universally proved exact formula. Missing native
layout, encoding and full caller integration prevent any new κ claim.
