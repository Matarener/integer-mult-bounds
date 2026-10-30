# Exact adaptation and postrun boundary

Historical local checker SHA256: `e2c42f6f5db304067661ec3d54e6c94ebf7bc2fa82d4c8ded7f714cdcb461aa3`.

Qualified portable verifier: `bce6cdf82cb1492d209c241670df894548a485b89622a39851f26352f61e999b`.

Qualified controls: `9e9e14f995b47afb13d48a21cdd4c68750ef121a91b00298dd1e5de7a9df697c`; fixtures: `494736481a4722b76ca94584df74fec1f58d54d62abe86a4b11ec89da5421c5b`.

The named scientific constants/classes/functions in ADAPTATION.json, including Audit and the input/coefficient parser, retain their exact source bytes from the local checker. Their scientific-core manifest hash is `6c2de9fa2d5714e7501c308d06492e5bf251c6e9bd341efff0e4f6629c0d2974`. The local-to-portable wrapper replaced workspace-specific custody/registration paths with one explicit data argument and active WORD/LICENSE/NOTICE authentication, and removed private paths from output. Its exact private diff was sealed; the private removed lines are not distributed publicly.

V2 added a separate control harness without changing that verifier. It authenticates and compiles raw verifier bytes, avoiding cached verifier bytecode; authenticates the original before in-memory derivatives; compares the full scientific projection; and requires exact intended predicates/sites. All 12 controls have now passed their registered phase. The prospective-only fixture has original 715/747 in 598 and prospective 715 in 3. The coefficient-only 11202 positive fixture is distinct from the unmodified historical-projection comparison. The minimal 340 fixture tests its precise later stability boundary. No assert-only acceptance or source-file mutation is used.

Normal and explicit `-O` direct runs reproduce all 17 historical scientific fields, SHA256 `8ad201fe2ce3ebcbb0a081774790fd4511d3ecce1b5b5c1cee3dd9bde033895c`. Agreement is reproduction, not a new independent checking method. Root's recorded outcome and separate static AI postrun review support only the fixed causal/typed scope; that reviewer did not execute a further replay or reread WORD.

This final-publication revision changes documentation, evidence and metadata only. The verifier, controls, fixtures, historical reference, scientific core and retained input pins remain byte-for-byte unchanged from qualified V2. Frozen preparation-time UNRUN notices in hash-bound code/fixtures are retained as historical input labels; current execution evidence is stored separately. V1 and V2 local artifacts remain preserved. No new scientific run, source decode, export, Git or upstream action occurred during this revision.

The implementation/publication identity and final byte/history/generic/CI/render checks remain root-owned and pending. Generic/export/hosted passes are not inferred from direct qualification. No new kappa or broader native/caller/price admission follows.
