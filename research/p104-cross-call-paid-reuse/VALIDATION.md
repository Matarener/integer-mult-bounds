# Verification record

Local-only, 2026-10-26. Substantial OpenAI Codex assistance; no subagents or independent human/formal review.

Environment: CPython 3.12.8, macOS-26.5.1-arm64-arm-64bit; standard library only. Initial exploratory replay also passed under CPython3.14.5. Final scientific checks use3.12.8.

Passed serially:

- `python3.12 -B scripts/research_package.py --package research/p104-cross-call-paid-reuse --check-only`: `PASS_PACKAGE_METADATA_AND_PINS`.
- `python3.12 -B scripts/research_package.py --package research/p104-cross-call-paid-reuse`: both normal and optimized full receipt comparisons pass; `PASS_REGISTERED_RESEARCH_PACKAGE ... outcome=negative-result`.
- Optimized direct replay from a new Git-free directory, with empty PATH and a separate bytecode namespace: `PASS_VERSIONED_CROSS_CALL_SCOPED_HANDOFF_NO_NEW_KAPPA`. All 16 copied package files remained byte-identical. Diagnostic elapsed time 16.877s. This file was added after that portable replay; it is not a scientific input.
- Exact source-copy equality to all seven origin Git objects, then registered metadata pins.
- `git diff --check`.

Coverage: two physical invocation bindings, all3426 local paid rows each, all753 source/owned endpoint columns, all536 independent helper columns per invocation,416 actual native phase identities,7976 independently interpreted cache-cost tableaus,997 independent17-axis alignment tableaus, all512 first-centre native basis columns, every strict-saving separately aligned cache subset in the stated model, the full66348-job/12976-target invoice, constructive two-version and two-cache discovery controls, stale-helper/future-access/unpaid-retag/wrong-global-phase controls.

Scientific RESULT SHA256: `acbb686ebfb739253318c574a72692ab061e2c0d680fab380549e3cb7fc97ab5`.

Decompressed QUERY-MAPS payload SHA256: `4e1cbf2c933eed697dc0f256d0da1c6980b685baabcd74a6e3ee844ab0676a49`. Compressed container bytes are not the mathematical equality criterion.

No selected cold replay, full native-lowering replay, Lean, Docker, compiler/outer scientific replay, formal proof or rounded multiplier was run. No new cache program, kappa gain, public post or PR is claimed. Joint intermediate-frame transport, noncanonical matrix-valued combinations, new reads and changed consumers remain outside this certificate. New retention/read/route/restoration/cleanup costs remain unknown; optimistic zero costs were used only to reject the declared delivery model.
