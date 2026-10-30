# Implementation and review decisions

The exit predicate is one independently reviewable register-producer result with source closure, exact evidence, committed-byte and Git-free checks. The selected frontier and frozen inputs are outside scope. The external session decisions.tsv records checkpoints and original diagnostics.

Build the Lever shaped the decision to keep a direct producer and independent rerunnable formula/circuit/residual checks. Prove It Works requires actual iterator consumption, observed Boolean calls, source/receipt faults and committed Git-free replay. Power of Ten shapes the limits below.

## Ten-rule inspection

| Rule | Decision and evidence |
|---|---|
| Structured flow | No recursive calls. The producer consumes a finite generated schedule; finally resets bank and accumulator on success and exceptions. Control fixtures preserve original bytes in finally. |
| Bounded loops | Shape enforces ell<=256, D<=64 and 1<=K<ell. A<=16384. Adder/negation loops have at most256 steps. Small fixtures enforce A<=10. Physical enumeration visits at most1024 addresses per fixture; prefix/suffix products together visit at most1024 complete addresses per case. Wide checks have63 shapes, two signs and three addresses. Control fixtures have at most20 package files, three external inputs and eleven CLI calls, each bounded by120 seconds. |
| Capacity | The register payload has d*max(a,1)+h+1 bits, or zero in degenerate rounds, plus the proved eight scratch bits. Managed Python execution allocates objects dynamically and does not implement packed-bit or fixed-capacity memory. Bounds on shapes, source sizes, circuit gates and finite fixture extents bound live objects. Residual tables retain at most1024 output values per case. No numerical Python heap measurement is claimed. |
| Function size | Functions stay within roughly60 physical lines, measured by the session AST review. Responsibilities are shape validation, schedule, one transition, adder, output, producer, and independent checks. |
| Invariants | Explicit exceptions survive -O. Bit inputs, bank ranges, accumulator bits, exact iterator reads/EOF, direct/circuit equality, residual classes, observed gate counts, private reset and full receipt equality are checked. |
| State scope | Input values occur only in the caller-owned iterator, one current bit, the bank, accumulator, transient gate operands and final output. The participation map, schedule indices, addition/gate counters and shape are input-independent. Verifier oracles and receipts are outside the producer's register claim. |
| Contracts | Shape is validated at construction. The producer rejects missing/non-bit/trailing input. Library helpers accept trusted internal bit/register arguments. Invalid shapes and theorem domains reject. Subprocess exit codes, timeouts, byte-copy writes and source identities are checked. |
| Metaprogramming | The only dynamic code compilation authenticates the exact canonical circuit.py bytes before compiling them as an independent oracle. No generated program controls the producer. The source module has no transitive project imports. |
| Indirection | Ordinary Python method dispatch has bounded visible targets: Shape, Gates and the supplied iterator. The producer itself has no callback registry. The iterator is trusted to implement sequential next; the tests use a nonindexable, nonrewindable iterator and count its reads. |
| Diagnostics | Run CPython3.12 with -I -Werror -B, registered replay, optimized CLI controls, ruff E4/E7/E9/F and AST function-size inspection. The session report records exact results and executed HEADs. No Lean, native compiler, Docker or selected full cold replay is claimed. |

## Explicit deviations and boundaries

Rule 3, fixed memory. Python, dataclasses, generators, arbitrary-precision integers and oracle evaluation require managed allocation. This deviation covers the bounded executable and finite verifier, not a claim that Python realizes the bit-register space bound. Shape/fixture/source limits bound live data; the proof specifies the separate Boolean register algorithm. A packed or tape backend must establish its own allocation, control and movement bounds before a physical memory claim.

Rule 8, dynamic compilation. verify.py authenticates exactly three declared inputs and compiles one bounded canonical Python module from checked bytes to avoid stale bytecode substitution. This is restricted to the independent layout/circuit oracle. Source corruption/absence controls and registered input pins verify the boundary. Remove this compilation if the oracle is replaced by an equivalently source-authenticated static interface.

Rule 9, method dispatch. Gates methods count real logical operations. The input iterator is a supplied boundary object. Both have explicit lifetimes inside one produce call and finite schedule bounds. Arbitrary iterator side effects or external input buffering are outside the claimed reader implementation. A fixed-tape backend must replace this boundary with its own read/EOF contract.

Register cleanup means resetting the mathematical bank and accumulator. Python object references, diagnostic receipts, final output and allocator copies are not secure-erasure guarantees. A failed iterator can leave a traceback; boundary tests inspect the producer frame to check that its counted registers were reset.

The gate bill counts explicit AND/XOR evaluations. Bit indexing, fixed wiring, bank writes/replacement, initialization/clearing, output, shape/control and memory accesses remain separately charged by the asymptotic register-work proof. No physical supplier cost is zero by omission.
