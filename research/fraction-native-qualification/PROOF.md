# Equivalence and complete-cost obligations

This is a source-bound implementation argument for the frozen PR5848 qualifier, supported by exact finite/actual comparisons and local cold-process measurements. It is not a formal proof of arbitrary Python callbacks, a multiplication theorem or a kappa admission.

## Entry domain and arithmetic

Retain the predecessor's conservative identity-only exact-container/type predicate. For that domain, induction through empty rows, INIT/CLEAR resets, F(1) injections, SCALE and ADD/COPY gives exact Fraction row coefficients. Weights are exact Fractions. Stable standard Fraction operations on exact operands return exact Fractions. Unknown/custom domains retain the checked generic behavior. Native selection additionally requires valid distinct source/destination rows, sufficient source-site metadata, and well-formed exact-Fraction scalar slots; other such cases use the literal original trace so error type/message/order are preserved.

The canonical numerator/denominator property getters are bound to their pure executable shapes, owned member descriptors and ordinary object attribute lookup. Before each trace, identity/code/presence freshness is rechecked. Getter, slot or lookup drift selects the literal original. The miss callback is extracted from raw class MRO dictionaries only after verifying an exact staticmethod descriptor, exact FunctionType, no closure/defaults, the literal original compute code shape and captured builtin abs. A foreign descriptor is not invoked to inspect it. Nonqualifying callbacks select the checked parent path, allowing retained corruption controls to detect altered arithmetic.

Each successful miss computes exactly `value = old + q*v`, `change = abs(value)-abs(old)`, then returns `(value, change*a, change*c, change)`, with the original Python Fraction operations. The native helper does not implement rational arithmetic. Cached values are immutable exact-Fraction tuples under the predecessor's stable-input/runtime premise.

## Complete key and FIFO invariant

The key is `(old_n,old_d,q_n,q_d,v_n,v_d,weight_token)`. Per-trace tokens are assigned injectively to complete `(a_n,a_d,c_n,c_d)` pairs using full Python integer equality after hash comparison, bounded to 16,384 distinct pairs with no recycling. Equal canonical weights share a token; unequal pairs cannot. Metadata is indexed by original source site i, not event position. Event owns q and its canonical key components. Overflow or invalid metadata selects original behavior.

Initially dictionary and fixed ring are empty. Each dictionary entry has exactly one owned ring-key reference, with `used` resident entries and `head` at the next insertion/oldest eviction slot. Hits return an owned reference to the dictionary result and do not reorder the ring. A miss increments the same counters and performs original computation before eviction. At capacity, delete the oldest dictionary key and clear its ring reference; then insert and advance. Failed computation never evicts or caches. If insertion itself fails after eviction, the ring/dictionary remain consistent with a smaller cache, and the error propagates. Counters are bounded against C signed overflow. Per-trace Cache objects are fresh; only code is reused in a process.

## Coefficient-loop correspondence and native ownership

The complete literal source loop is authenticated before replacement. Native apply uses the actual Python dict-items iterator, preserving order and its size/key mutation errors. Each item tuple holds source index/value strongly across callbacks. Each iteration constructs F(0), obtains the destination's old coefficient, gets the exact contribution tuple, performs the three ordered PyNumber_InPlaceAdd updates and updates/removes the destination exactly as the Python loop. Checked score retrieval and strong temporary references remain safe around Python callbacks. Rounded injection, score peaks, witness capture, stream hashing and return structure remain in the unchanged outer source.

Cache owns dictionary, ring, immutable metadata snapshots, callback, descriptors and Fraction class. Event owns Cache and q context. Constructor tokens use checked owned reads, not unchecked reads from a mutable caller list across allocations. Partial initialization, error exits, GC traversal/clear/deallocation and Event-outliving-Cache cases are covered by source review and finite checks. A busy guard rejects reentrant mutation; errors reset it. Descriptor reads stop at the first failure. These defenses protect the packet API; the wrapper's semantic qualification is still required.

The loader authenticates C bytes, copies exactly those bytes into an owned read-only build snapshot and compiles that snapshot. Loaded-code reuse requires the same authenticated source digest. Builds occur in a fresh temporary directory per complete candidate process, with explicit cleanup. Every fresh complete process pays compilation, linking, loading and validation. There is no system installation, persistent compiled-answer cache or native arithmetic shared with the independent integer engine.

## Complete caller and oracle boundary

The new full entry authenticates the complete readonly PR5848 export and changes exactly the sole actual noisy_precision error_trace immediately before the existing Observation wrapper. The separately loaded reference/integer engine, source contract, all reverse checks, 120 finite fixtures, six controls, final receipt and original Observation finite tests remain unchanged. Capture by program length is scoped to this exact frozen source, which calls error_trace once; it is not a general caller-identification rule. The full native output digest and exact cache counters are required in addition to the original complete scientific comparisons.

The new native finite stage runs before the original complete entry in every timed C command. All 964 comparisons / 73 inherited +45 native controls are charged. The four inherited custody checks remain separate registered-verification obligations, just as in the predecessor benchmark. Independent backends do not share mutable caches or answers. Complete normal/O and exported-source replays supplement the finite gate.

## Economics and limits

The immutable-code build is shared only between the new finite stage and actual trace inside one process. The complete outer process is measured with GNU time, so compiler/linker child CPU is included. In six fresh serial B,C,C,B,B,C processes, wall medians are 40.516156 and 32.771297 seconds, CPU medians 40.33 and 32.74 seconds: 19.1155% and 18.8197% saved, passing both declared 15% gates. All observations, source inventories, stdout/stderr and failed harness attempts are retained. This evidence is specific to the frozen fixture and recorded Linux/CPython/GCC environment; inner trace timings, cost models and hosted finite replay are distinct claims.

Static/API review by GPT-6-astra xhigh ran no compiler or numerical replay. Chris R / Clear1nsight with substantial OpenAI Codex assistance performed the single serial numerical execution. Original arithmetic/provenance remains Ali Romman and all retained predecessor authors; see NOTICE. No kappa or selected metadata changes.
