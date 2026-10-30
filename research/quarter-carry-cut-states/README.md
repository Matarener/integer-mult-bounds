# Exact retained state for serialized rational-shear carries

Scoped written mathematical proof with finite corroboration, produced by Nick
Petalas. No new kappa is claimed.

A rational shear has source low digit x, later target low digit y, radix q,
coefficient A/D and high modulus Q. If all of x must be read before any of y,
with no reread or early output, the exact minimum number of distinguishable
states after reading x is

```text
g = gcd(A,q),  d = q/g,  e = Q/gcd(A/g,Q)
R = 1                    if Q=1
R = d * min(g,e)         if Q>1
```

This counts all retained information, including controller and head state.
It permits arbitrary lossless encodings. An explicit class label attains the
bound. The domain is q>=2, Q>=1, arbitrary integer A, positive D and
gcd(D,qQ)=1. [PROOF.md](PROOF.md) gives the exact output contract and proof.
The result counts information at one cut, not total workspace or physical time.

For a quarter shear, odd q>=3 and high width w>=2, R=q. At q=257 the verifier
checks 257 distinct response functions and every pair of source/target digits.
Nine binary bits are necessary at the cut although the integer carry takes
only the eight values -3 through 4. A finite final packet does not by itself
supply a constant-state producer in this access order. At w=1 the high
correction is zero and needs one state. Producing the exact integer carry is
a different contract: it needs q states whenever A is nonzero.

## Connection and scope change

Ali Romman's [PR #5849](https://github.com/CrocSwap/integer-mult-bounds/pull/5849)
at `35ee8364ccfe54d6d5ec154fbf74993624b0a0d4` supplies a complete original-owner
rotation from a caller-supplied packet and explicitly leaves its production
from the low cache open. [PR #5841](https://github.com/CrocSwap/integer-mult-bounds/pull/5841)
at `58a032ffafc2c5d08b8f53c2e98657b75c48379d` supplies the fused carry algebra.
These predecessor results are cited, not audited or replayed here. Their
runtime programs are not imported and their physical costs are not recertified.

The `bit-helper-contract` card is changed from a new helper/target moment
improvement to a sharp information obligation for one explicit carry-producer
interface. This helps decide whether a proposed serialized cache layout can
produce its packet with constant retained state. It does not assert that the
released G20 word uses this layout, or instantiate this scalar quarter-shear
fixture as one of its actual ports. The selected frontier is unchanged.

## Reproduce

From the repository root, using the local interpreter:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/quarter-carry-cut-states/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -O -B research/quarter-carry-cut-states/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/quarter-carry-cut-states
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/quarter-carry-cut-states --check-source-history
```

Any CPython 3.12 interpreter can replace that local path. Only the standard
library is needed. Normal and optimized checks print
`PASS_QUARTER_CARRY_CUT_STATES` inside a generated JSON receipt bound to all six
package files. No receipt is handwritten or stored as an authoritative result.

The verifier enumerates all admissible q=2..25, Q=1..16, A=-24..24, D=1..8
systems, plus every odd q=3..65 and w=1..6 for the quarter corollary and the
complete q=257,w=2 fixture. Its independent oracle applies the rational shear
directly modulo qQ and extracts the high digit. It compares every response,
checks every attaining label, counts the integer-packet response classes, and
constructs a separating target digit for every pair in the q=257 fixture.
Nonunit collapse, zero coefficient, negative coefficient, Q=1, invalid input
and incorrect constant-packet interpretations have explicit controls.

The default replay is read-only and Git-free. Git is required only by the
repository's provenance and publication preflights. [SOURCES.json](SOURCES.json)
pins the catalogue and selected record as historical provenance at the base
commit. The predecessor links are scholarly context, not executable inputs or
unmerged Git-history dependencies.

## Limits and implementation checks

No literal tape producer, complete cache layout, source admission, erasure,
routing, native caller, precision/stock or all-size multiplication theorem is
proved. All five selected framework assumptions remain. Interleaved access,
source rereads, early output, precomputed cache summaries and amortized joint
packet production are outside the lower bound. Human and formal proof-kernel
review are unclaimed.

The verifier has fixed finite census loops, no recursion and explicit
parameter/radix limits. Python allocates dynamically, a managed-runtime
Power-of-Ten deviation. At most O(257^2) response entries are live, and parameter
integers have at most 4096 bits. The proof itself has no such finite bound.
Warning-strict normal/optimized execution and in-memory compilation supply the
available language diagnostics. No separate static type checker is installed on PATH.
Checks use explicit exceptions and remain active under optimization.

## Open next questions

1. Can a concrete low-cache layout interleave the relevant source and target
   digits and avoid this serialized-cut storage? This determines whether the
   obstruction applies to an actual packet producer. Start with one explicitly
   ordered pair of low-digit streams and charge every reread and erasure.
   A literal caller/cache layout is the blocker.
2. What is the joint cut-state count when one retained source digit serves
   several rational-shear packets? Shared information could make separate
   per-packet charges too large. Start by quotienting the tuple of two response
   functions. A declared joint output and access contract is needed.

## Credit

New proof and verifier produced by Nick Petalas. Credit Ali Romman for the
PR #5849 packet-production question and PR #5841 fused carry contract,
JoyboyBrian for the retained descriptor/affine-shear work, Tekalign for the
carry-stream predecessors, and the retained ROW/native/tape contributors.
The state-equivalence proof uses the classical deterministic one-way
communication method; modular arithmetic and that method are not claimed as
new. New material is Apache-2.0. No predecessor files or credit lines change.
