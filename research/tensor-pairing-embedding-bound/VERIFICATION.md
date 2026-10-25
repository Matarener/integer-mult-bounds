# Verification receipt

Local environment: CPython 3.12.14, macOS arm64. No third-party dependencies.
Evidence was produced on 2026-10-19 UTC. The scientific inputs are pinned in
SOURCES.json; publication-head transport is checked separately.

Passed:

1. The assigned card's existing `complex-local-word-ceiling/verify.py` example:
   `PASS_COMPLEX_LOCAL_WORD_CEILING`, ceiling approximately
   `0.00169005410908900006`. This is predecessor orientation, not a new bound.
2. New direct replay, both `-I -B` and `-I -O -B`:
   `PASS_TENSOR_PAIRING_EMBEDDING subsets=65536 pairings=12544 rank_only_max=12 common_root_max=8 abstract_labels=9 controls=7 no_new_kappa`.
3. `scripts/research_package.py --package research/tensor-pairing-embedding-bound`:
   metadata/source pins and both registered commands pass,
   `outcome=negative-result`. Metadata acceptance is not mathematical review.
4. Separate AI review independently recomputed the principal-rank census and
   displayed root Gram, constructed a different nine-label witness, and checked
   the universal argument's assumptions. Integration review separately
   authenticated all retained input Git/SHA256 hashes, the archive/payload,
   extracted ports, and the AST-only source binding. No actionable finding.
   These are assisted-author checks, not independent human review.
5. Optimized relocation from `/` in a fresh temporary root containing only this
   package and its declared selected archive passes and writes no files.
   Changing the committed upper bound to nine is rejected with `committed
   result mismatch`; appending executable text to the retained tensor source
   is rejected with `source digest mismatch` before parsing or execution;
   changing one archive byte is rejected before decoding. Restoring original
   bytes passes again. The source checkout remains unchanged throughout.

The selected-record SHA256 remains
`bb2eaa58647b353f88d0aec2eafb9d30df1be53589231b23e12ceef3e4bad129`.
Canonical-main checkpoints at session entry and 03:43:14 UTC both resolve to
`20ecf2891d80b5acf18d980b2164fb44ea7faa90`; relevant guidance, priority revision6,
selected record and ledger are unchanged. The final prepublication PR snapshot
at 03:44:41 UTC contains631 distinct open PRs, including drafts, from all seven
pages. PR3895 and PR3566 retain their frozen heads. Discussion coverage is
manual and incomplete; no novelty certificate is claimed.

The system `python3` is older than the declared runtime and does not support
`int.bit_count`; accepted runs use the stated CPython3.12.14 runtime. No
repository-wide historical suite, selected construction cold replay, hosted
CI result, proof-assistant proof or physical supplier implementation is
claimed by this local receipt. Hosted status belongs to the exact public PR
head and must be checked separately.
