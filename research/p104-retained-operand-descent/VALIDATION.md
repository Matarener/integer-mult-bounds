# Author validation

Date: 2026-10-29 UTC. Host: macOS 26.6.1, arm64. Registered interpreter:
CPython 3.12.13. The package uses only the standard library. No subagents or
independent scientific reviewers performed these checks.

## Completed checks

- The immutable source word and price match their Git blob bytes at PR6144
  head `5ec9b6dafc1ec54e2c0ca0771e8ed032f7888417`. Their sizes, SHA256 hashes
  and Git blob IDs are retained in SOURCES.json. The source archive and every
  file in its dependency chain are authenticated by the direct verifier.
- `construct.py --write` generated the full 22,821-event word.
- `python3.12 -I -B verify.py --write` passed the full chain and wrote RESULT.json.
- `python3.12 scripts/research_package.py --package research/p104-retained-operand-descent`
  passed all registered commands. These include seven gzip and source-integrity
  controls and the complete replay in both ordinary and optimized Python modes.
  Both modes reproduced the exact RESULT.json.
- The separate transpose covers 799 columns and 638,401 coefficients. The native
  checker covers 2,922 distinct maps, exact phases, 208 main adapters and 1,124
  helper normalizers. The complete caller and all price, compiler and outer
  checks passed. RESULT.json lists each semantic rejection control.
- The metadata and source-pin check passed after the metadata update. Runtime
  inputs are inside this package. The two source-head files use the archive
  reader's exact-byte contract; they do not require an unrelated PR branch in
  a clean CI checkout. The generic provenance rows pin main's selected record
  and task catalogue.
- Canonical main and the exact PR6144 head were refreshed before submission.
  Both were unchanged. The latest scoped Discussion claims were read. The
  live GF(4) frame assignment in Discussion 5600 fixes the scalar word and
  expressly excludes changed scalar words. The caller work in 5593 is separate.

## Publication checks

The committed-byte and executable-mode preflight passed at source commit
`531df47159d3f9ee6652c1e0e46305cc30ca841d` for all 18 package files. The official
exporter and its separate archive check passed. The archive SHA256 is
`3f5f6e6a612aa18b28a3a3bd444085e39b3de07055ed09c7f86d124fd285a934`.

The exported package then passed the full optimized Python 3.12.13 replay in
156.311 seconds. Git was absent from PATH. All exported files had mode 0444;
all export directories had mode 0555. Hash and mode inventories before and
after the run matched for all 19 files, including the export receipt.
Status: `PASS_READ_ONLY_GIT_FREE_EXPORT`.

The next commit changes only this validation note and task coordination
metadata. It does not change code, source inputs, the word or RESULT.json.
Hosted CI and independent scientific review remain pending. The optional full
Git-history ancestry preflight is not run: this checkout is shallow, and the
runtime source is retained in authenticated local archives.

## Limits

All five inherited framework assumptions remain. The uniform word at
`N = 2^65807000000000` and the rounded multiplier are not materialized.
The current selected result is not changed. Local verification and source
integrity do not establish independent acceptance or a practical speedup.
