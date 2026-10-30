# Actual-key pilot: complete capture passed; conditional nomination rejected

The parent executed the frozen actual-key pilot once on 2026-10-28. The guard returned `PASS`; the driver returned `PASS_ACTUAL_KEY_COMPARISON_ONLY`. Its predeclared screen returned **`REJECT_THIS_ACTUAL_KEY_CONDITIONAL_NOMINATION`** for both wall time and CPU. This provides no admission of the complete PR5864 >=15% target, integer-owner construction, GMP provisioning or full cache integration. The earlier failed synthetic nomination remains closed.

Evidence: [outer guard receipt](../runtime/runs/actual-key-pilot-v1/receipt.json), [driver result](../runtime/actual-key-pilot-v1-artifacts/RESULT.json), [capture receipt](../runtime/actual-key-pilot-v1-artifacts/CAPTURE-RECEIPT.json), [finite controls](../runtime/actual-key-pilot-v1-artifacts/FINITE-CONTROLS.json), and [frozen source manifest](../stages/actual-key-pilot-v1/FROZEN-SOURCE.json). This report interprets bounded retained metadata; it performs no rerun, corpus replay or new hypothesis test.

The full original qualifier, using its original cache with the diagnostic capture hook, retained its Fraction operations, callbacks, counters and complete signed-witness checks. It passed the frozen receipt: 25,984 events, 799 coordinates, 120 finite fixtures, six source controls, coefficient scale 55, all actual witness rows equal, and source result digest `cc7739703ed23532d187949c8507d09c13ac4c152e07a930f0087cde0d7a3d98`. The actual Fraction output retained digest `954c7448ff74d78753828e9623ad44c46da9e5ce459420b6e50a5d47294250b9`.

Every one of the **2,579,750 actual seven-field keys** was captured in order, with 3,587 weight tokens. The complete corpus was persisted as [actual-keys-v1.pickle.gz](../runtime/actual-key-pilot-v1-artifacts/actual-keys-v1.pickle.gz): **7,945,691 bytes**, SHA-256 `660e3f8d6dcd147c97a5691feab301e558cc70097c7d4c3d00e4f116482d2699`. Bounded streaming readback checked all values and their order. Replay used the original captured objects; the archive preserves arbitrary-width signed integer values/order and does not promise cross-block object identity.

The four fresh-state B,C,C,B replays each matched the separate literal dict/deque oracle for every ordered result ID, hit/miss/eviction flag and 80-operation/final-partial prefix. Their statistics also matched the original actual cache: 2,252,966 hits, 326,784 misses, 310,400 FIFO evictions and 16,384 residents at capacity 16,384. Both custom samples paid for 23 natural rehashes; baseline custom-rehash counters were zero. The 82 finite-control receipts passed and exercised 50 natural rehashes. These controls are finite, not exhaustive allocator-failure or general GC proofs.

| Actual-key sample | Wall seconds | CPU seconds |
|---|---:|---:|
| B1 | 0.477255588 | 0.477131657 |
| C1 | 0.307855024 | 0.307762678 |
| C2 | 0.313469836 | 0.313226221 |
| B2 | 0.474210388 | 0.474076689 |

The predeclared smaller paired B−C difference was **0.160740552 seconds wall / 0.160850468 CPU**. This is a measured difference for the source-specific actual-key-only replay, with no call-count extrapolation. Both inner arms omit descriptors, Fraction arithmetic and miss callbacks and use opaque miss IDs, so this difference is not a measured complete-verification gain.

| Conditional engineering budget | Wall seconds | CPU seconds |
|---|---:|---:|
| Earlier integer gross anchor + measured actual-key-only difference − provisional 0.5-second reserve | 4.345453128 | 4.344279183 |
| Same calculation with the reserve reduced to zero | 4.845453128 | 4.844279183 |
| Necessary 15% saving against the fixed complete baseline | 5.199267809 | 5.170500000 |

Both calculations fail despite assigning **zero retained integer runtime**. The earlier integer gross anchor comes from a different run and includes diagnostic clock overhead; it is not an achieved saving or a same-run removable-cost bound. The reserve is provisional and unmeasured. Real retained integer runtime and complete future integration/build/validation costs remain unpriced and nonzero. This result rejects this actual-key conditional nomination; it supplies no actual complete-runtime gain, actual-trace upper bound or global impossibility result.

The authoritative cold bill was **42.639824143 seconds wall / 42.54 seconds CPU**, including the original qualifier, capture, both cold builds, finite controls, full corpus persistence/readback, oracle, all four samples and output persistence. CPU is the guard's rounded user-plus-system measurement including compiler children. Sampled peak process-group RSS was **437,825,536 bytes**, within the unchanged 1-GiB cap. The command had no termination condition or stderr; source bytes and modes remained unchanged. The key compiler returned zero with empty stdout/stderr. One explicit collection after every original qualifier check was charged outside replay timings, retained all keys and changed no GC policy; it is not credited as an optimization.

The retained runtime artifact tree contains **135,724,869 bytes**, including the corpus, oracle and every trial's complete outputs. No sample was discarded, no retry occurred, and no additional execution or investigation was performed for this report. The useful result is the complete source-specific corpus and reproducible negative conditional-budget evidence. Candidate integration with the literal Fraction callback/API, ownership and general GC behavior remains unproved and unadmitted. Frozen sources and manifests are unchanged; this separate report records the subsequent parent-owned execution.
