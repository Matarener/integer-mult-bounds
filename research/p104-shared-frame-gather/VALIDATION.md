# Validation record

Local-only; 2026-10-26. CPython3.12.8, macOS-26.5.1-arm64-arm-64bit;
standard library only. Substantial OpenAI Codex assistance; no subagents,
independent human or formal-kernel review.

Passed serially:

- Exact byte equality of ten retained runtime files against their original
  pinned Git objects: local predecessor code/maps/source manifest and the seven
  PR5718/native source inputs. The generic metadata pins now resolve the same
  retained copies at this branch's ancestor export commit; scientific replay
  needs neither the predecessor worktree nor foreign Git history.
- `python3.12 -B scripts/research_package.py --package research/p104-shared-frame-gather --check-only`:
  `PASS_PACKAGE_METADATA_AND_PINS`.
- `python3.12 -B scripts/research_package.py --package research/p104-shared-frame-gather`:
  normal and optimized generator receipt comparisons, and normal and optimized
  separate certificate audits pass; `PASS_REGISTERED_RESEARCH_PACKAGE ... outcome=negative-result`.
- Optimized direct replay of both engines in a separate Git-free package copy
  with empty PATH. All21 copied files stayed byte-identical. A certificate
  mutation that undercharged one ingress failed in the separate auditor with
  `Every source-frame ingress charged`; original receipt restored afterward.
  See `results/PORTABLE-REPLAY.json`, including exact commands and environment.
- `git diff --check` and the final committed-byte preflight
  `python3.12 -B scripts/check_research_commit.py --package research/p104-shared-frame-gather`.

Coverage: all3,426 local paid maps; exact744-public/9-owned arbitrary-input
endpoint replay; both536-helper invocation namespaces; all32 raw original
caller columns at each routed port;416 exact phase-polynomial source-binding
checks;1,211 available prefix outputs and465 source-coframe bundles;
all1,090 pinned gather-frame labels, of which478 have appeared before the cut;
316,590 independently recomputed used pair tariffs;1,384 literal relative-map
rank checks; four exact native-map/absolute-phase controls; all1,090 exact
support/budget receipts; complete66,348-job/12,976-target source invoice;
positive nested two-snapshot gather and future/stale/phase/frame/missing-helper/
underpriced-ingress/unknown-cleanup rejection controls.

Scientific RESULT SHA256:
`2bccd5484b3db817c32d4af63be5d7a15d590f328c078e2271e996f050df3338`.

Decompressed CERTIFICATE payload SHA256:
`b25c717de42242242d0f68b3033d5c453eea602164b4f0d69e1c0bd1bdd1006d`.
Compressed container bytes are not the mathematical equality criterion.

Canonical main refreshed again at completion to
`de5ec2e7a6074068452f45b1a191b5c72832df4a`; priority8 and selected .00310045
unchanged. Live overlap is timestamped in the saved snapshots.

No selected cold replay, full native-lowering suite, Lean, Docker, new
compiler/outer scientific replay, formal proof or rounded multiplier was run.
No replacement program, new κ, global P104 barrier, public post or PR is claimed.
Unknown acquisition, retention, normalizer, ordinary, dirty-return and cleanup
costs were omitted only in the favorable exclusion. No new target credit was
assigned. Additional gather frames, source/consumer changes and general
matrix-valued recombination remain outside the result.

The isolated sparse conventional worktree is retained for access to the local
artifact. Managed creation failed for disk space; attaching the fallback was
rejected as unmanaged. A later optional temporary-copy cleanup was blocked by
the command guard; the safe replay omitted that cleanup and retained its own
small temporary copy. No other checkout or predecessor files were changed.
