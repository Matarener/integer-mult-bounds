# Fresh scientific replay

The exact attached base was fully materialized (78,395 regular files), the
previous 3,214-path cumulative overlay was applied, and the new scopes were
copied into a separate checkout. `BASE-MATERIALIZED.json`,
`PRIOR-APPLIED.json` and `NEW-SCOPES-SNAPSHOT.json` record those operations.

`CRITICAL-REPLAY.json` records a full successful replay of **23 stages** and
comparison of **59 regenerated artifacts**. Logs are in
`critical-replay-logs/`. No reconstruction stage was skipped. The completed
native words, compiler, BIT bridge, semantic closure, explicit ranks and
independent outer audit were regenerated in that separate checkout.

Comparison ignores only `runtime`, `runtime_seconds`, `elapsed_seconds` and
`seconds` fields, plus exact old-to-fresh hashes of those regenerated
artifacts when they appear as source references. Every other mathematical
field must agree with the delivered canonical artifact. The receipt retains
both original and regenerated hashes and whether their bytes agree exactly.

The first complete run passed every scientific stage but its comparison
wrapper requested a combined `RESULT-all.json` summary absent from the
canonical checkpoint, which instead has three named summaries. The wrapper
was corrected to rerun the helper, H and logger stages separately. The full
successful run above includes those reconstructions again. The initial
wrapper failure is preserved in
`INITIAL-REPLAY-SUMMARY-NAMING-FAILURE.json`.

The pre-replay scope snapshot was taken before final documentation and later
isolated H probes were added. The final `SOURCES.json` binds the complete
delivered scope. `record_claim.py` also verifies that every canonical artifact
and scientific source used by the successful replay remains byte-identical.

This is a fresh finite and quantitative replay, not formal verification of
the universal written arguments. The astronomical winning uniform words
remain algorithm-defined and unmaterialized. The isolated exploratory H
branch has separate checks and does not support the reported 0.0023 claim.
