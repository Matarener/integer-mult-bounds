# Sharp one-pass storage for whole-high child batches

This scoped proof was produced by Nick Petalas. Apache-2.0.

## Contract

Let n,L,s be positive integers. An input stream consists of independent
symbols x[u,l,a], in lexicographic order (u,l,a), where 0<=u<n,
0<=l<L and 0<=a<s. A dispatcher must emit exactly those symbols in
lexicographic order (l,u,a). It has one forward input pass and one
append-only output. It may pause either stream, and may pass an arriving
symbol directly to output. Emitted output cannot be read, overwritten,
or used as scratch. There is no other external storage or side channel.

Fix any finite alphabet Sigma with cardinality A>=2. Storage means retained
payload information. Every payload-dependent buffer, register, control state,
cursor or address is charged. Fixed schedule counters carry no payload
information and are separate overhead. At a fixed input cut, a retained-state
family of cardinality A^b requires at least b alphabet-symbol equivalents,
or b*log2(A) bits. An unbounded integer cell does not have unit capacity here.
This convention permits arbitrary lossless encodings; it does not assume
that the dispatcher stores literal symbols. Timing is not an external channel.

## Theorem

The least possible worst-cut retained payload capacity is exactly

    B = (n-1)(L-1)s.

A fixed schedule attains B with B literal symbol slots and deterministic
address/control overhead. Thus the result also gives the exact slot bound
in the usual indivisible-record buffer model. It is not a physical tape-time
bound, a native-cell bound for infinite alphabets, or a supplier theorem.

## Lower bound

Consider the cut after the first n-1 complete input cycles, immediately
before reading the final cycle. The n=1 or L=1 case has B=0 and needs
only the nonnegativity bound, so assume n,L>=2.

The dispatcher has not seen x[n-1,0,0]. Correctness for every independent
payload prevents it from emitting that symbol before reading it. Since
output order is fixed, no symbol with l>0 has been emitted yet.

Fix every l=0 symbol and every final-cycle symbol to one alphabet element.
Vary independently the B symbols with u<n-1 and l>0. There are A^B such
inputs. All already emitted output symbols have the same value. The
output length can vary, but any payload-dependent output cursor is part
of the charged retained state.

Two different choices cannot give the same retained state at this input cut.
Otherwise the unread suffix is identical, as are the already emitted output
and its cursor. Determinism would give identical remaining output. Correct
outputs differ at an l>0 symbol, a contradiction. Consequently at least
A^B retained states are required. This counts compressed representations
and payload-dependent control as well as explicit buffers.

The statement is for exact deterministic dispatch. It does not assert a
bound for randomized approximate recovery or a write-only output channel
that also communicates hidden timing information to another controller.

## Attaining schedule

During the first n-1 cycles, emit the l=0 chunk as it arrives and retain
every l>0 chunk. The retained size after k whole cycles is k(L-1)s,
so it never exceeds B. On the final cycle, emit its l=0 chunk directly.
For l=1,...,L-1 in order, first emit and release all retained chunks of
that type in increasing u order, then read and directly emit its final-cycle
chunk. No new retained symbols are required. The buffer ends empty.

There are nLs input reads and nLs output writes. This counts stream
events only. Accessing the retained chunks in the required order may
require physical movement, indexing or extra tapes, which are unpriced.
For n=1 or L=1, input already has the required order and direct bypass
uses zero payload slots.

## Delayed-cover substitution

Ali Romman's PR #5829 at f1e522fc26371617ed60dea3c4609d422d491d2e supplies
the declared whole-high batch address contract. We cite that contract; we
do not replay its address proof. In its notation, at depth j<D the parent
row index is b=U*H^j+A, with U=U'*(L*H)+l*H+h. Include the complete
body index r of size R. Reading the canonical parent order means reading

    (U', l, h, A, r).

Emitting each complete child in its declared b' order means emitting

    (l, U', h, A, r).

The theorem applies with

    n_j = T*(L*H)^(D-j-1),
    s_j = H^(j+1)*R,
    V_j = n_j*L*s_j = T*(L*H)^D*R/L^j.

Its exact payload capacity is therefore

    B_j = (T*(L*H)^(D-j-1)-1)*(L-1)*H^(j+1)*R
        = ((L-1)/L)*(1-1/n_j)*V_j.

The high fields remain in s_j. They are not discarded or treated as fixed
payloads. With L=2,H=2,T=1,D=2,j=0,R=1, the parent has 16 symbols
and the exact buffer is 6 symbols. For fixed L>1 and increasing n_j,
the buffer fraction tends to (L-1)/L. A sublinear buffer in V_j cannot
implement this particular one-pass, sequential-child interface in that limit.

This does not refute #5829's O(V_j) local-space premise. It supplies a
necessary term for one implementation of its still-open dispatcher. Multiple
independently writable child streams, another input pass, random access,
interleaved child execution or a changed parent order can evade the contract.
No assertion is made that the current caller requires this interface.

## Finite evidence and implementation limits

The verifier executes literal streams, an independent output-prefix cut
oracle and a minimax dynamic program over every legal read/emit interleaving
for every permutation through length seven. It checks the closed form on
all n,L,s in {1,...,8}, actual binary payloads on a declared complete small
domain, injective binary cut states, algebraic cover substitutions, and
subcritical and malformed-input rejection. The universal claim follows
from the preceding proof, not from the finite bounds.

The Python code is a simulator, not a measured physical buffer implementation.
Its input, output log and optional snapshots are checker instrumentation.
Only the simulated retained dictionary contributes to its reported payload
peak. It deliberately contains no predecessor imports or scientific replay.

Power-of-ten rule 3 deviation: CPython and its standard library allocate
managed objects dynamically, including integers and checker logs. Streams
are validated at at most 4096 symbols with signed 64-bit payloads. Production
simulation dictionaries, logs and snapshots have at most 4096 entries each;
the scheduling oracle is called only through size seven, with at most 64
cells. Cut-state sets have at most 1024 states of at most ten pairs each.
All search loops have explicit finite ranges, functions are below 60 lines,
and checks raise normally under optimized Python. Warning-strict normal and
optimized runs provide the available interpreter diagnostics. A physical
fixed-capacity implementation and its allocator diagnostics remain future work.
