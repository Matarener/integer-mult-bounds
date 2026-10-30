# Cache-key pilot: finite comparison passed; optimistic nomination rejected

The parent executed the frozen pilot once on 2026-10-28. The guarded command passed, and the driver returned `PASS_FINITE_KEY_COMPARISON_ONLY`. Its predeclared budget screen returned **`REJECT_THIS_OPTIMISTIC_NOMINATION`** for both wall time and CPU. The complete PR5864 >=15% target was not achieved or admitted.

Evidence: [outer guard receipt](../runtime/runs/cache-key-pilot-v1/receipt.json), [driver result](../runtime/cache-key-pilot-v1-artifacts/RESULT.json), [finite controls](../runtime/cache-key-pilot-v1-artifacts/FINITE-CONTROLS.json), and [frozen source manifest](../stages/cache-key-pilot-v1/FROZEN-SOURCE.json). This report interprets those retained receipts; it performs no rerun or independent numerical replay.

The complete cold command, including compilation, loading, finite checks, oracle construction, four samples, comparisons and output persistence, cost **6.573198422 seconds wall and 6.51 seconds CPU**. Sampled peak process-group RSS was **303,071,232 bytes**. The compiler returned zero with empty stdout and stderr; the guarded command had empty stderr, no termination condition, and unchanged inventoried source bytes and modes. The reported CPU is the guard's rounded user-plus-system measurement, including compiler children.

The driver retained all four samples in the frozen B,C,C,B order. Each used fresh cache state and 2,621,440 synthetic lookups: 2,293,760 hits, 327,680 misses, 311,296 FIFO evictions and 16,384 final residents. Each complete ordered ID sequence, hit/miss/eviction flag sequence and 80-operation prefix transcript matched the separate literal Python dict/deque oracle. Both custom samples paid for 26 natural rehashes; baseline custom-rehash counters were zero. The 82 finite-control receipts passed and exercised 50 natural rehashes, including broad numeric/collision/FIFO cases, type rejections, and the declared success/failure reference checks. These are finite checks, not exhaustive allocator-failure or general GC proofs.

| Sample | Wall seconds | CPU seconds |
|---|---:|---:|
| B1 | 0.487316342 | 0.487164264 |
| C1 | 0.357074977 | 0.356983922 |
| C2 | 0.338865159 | 0.338782096 |
| B2 | 0.513840729 | 0.513694743 |

The fixed rule takes the smaller of B1−C1 and B2−C2 separately for wall and CPU. Those synthetic gross savings were **0.130241365 seconds wall / 0.130180342 CPU**. Multiplying their per-call rates by the actual 2,579,750 contribution calls gives only an illustrative transfer of **0.128170075 wall / 0.128110022 CPU seconds**; it is not a measured saving on the actual trace.

| Conditional budget | Wall seconds | CPU seconds |
|---|---:|---:|
| Diagnostic integer gross region + illustrative key saving − provisional 0.5-second reserve | 4.312882651 | 4.311538737 |
| Same generous calculation with the reserve reduced to zero | 4.812882651 | 4.811538737 |
| Necessary 15% saving against the fixed complete baseline | 5.199267809 | 5.170500000 |

Both calculations fail even while assigning **zero retained integer runtime**. The diagnostic integer gross regions include clock overhead and are not measured removable work. The 0.5-second reserve was provisional, not a measured complete future bill; the separate 6.573198422-second cold pilot bill above is real and must remain charged. Actual retained integer cost and complete construction/build/validation costs remain unpriced and nonzero.

This result rejects **this synthetic conditional nomination**. It supplies neither an actual complete-runtime saving nor an upper bound on actual-trace key savings, and it does not establish global impossibility. The pilot omits Fraction arithmetic and descriptors from both inner loops, uses opaque miss IDs, and has no arbitrary callback or general Cache/Event GC interface. Consequently it does not prove literal Fraction-cache API compatibility, callback/GC behavior, or production integration correctness. Private cache cleanup is included in the inner measurements; destruction of returned outputs is paid outside those clocks by the cold command.

No source was changed after execution, no favorable repeat replaced any sample, and no retry, integer-owner construction, GMP provisioning, or new route investigation was performed for this report. The frozen sources and manifest retain their original pre-execution provenance labels; this separate report records the subsequent parent-owned execution.
