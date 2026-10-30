# Selected JSON: a source-preserving UTF-8 replay

The pinned `scripts/verify_selected_result.py` reads the selected record,
certificate and source manifest with the platform default codec. On native
Windows CPython 3.12.10 (`cp1252`, UTF-8 mode off), a valid UTF-8 U+211D in
any one of those JSON documents raises `UnicodeDecodeError`. A valid UTF-8
`supplier/preuve-é.txt` path instead becomes mojibake and fails file lookup.

This package reproduces both failures, verifies **`-X utf8` on the unchanged
checker** as an immediate remedy, and tests the three explicit-encoding reads
in [UTF8-READS.patch](UTF8-READS.patch) only in private temporary copies.
It adds no mathematical claim or new kappa.

## Result and source boundary

The audit starts from canonical main
`721c03822c421b7f7fcbb2598993b947c4d88419`, priority revision 8. Its exact input
is SHA256
`d6b305eac5b9bdb8172c469ad30a1655a60fa0aceac8b1bf610e1b73f51babd8`.
[SOURCES.json](SOURCES.json) pins the Git blob and task/selected-record provenance.

The selected `certificates/frontier6030-source.json` itself pins this checker.
Applying the patch directly would break that source closure. This contribution
therefore leaves the checker, selected manifest, scientific sources and frontier
unchanged. The current selected metadata passed its normal binding-only baseline
in this session: **the demonstrated failures use complete synthetic metadata
fixtures, not a claim that the current selected result fails.**

The tested unchanged-source invocation is:

```sh
python3 -X utf8 -B scripts/verify_selected_result.py
# The current baseline also calls that checker in the same interpreter:
python3 -X utf8 -B scripts/research_selected_baseline.py
```

`-X utf8` selects the decoding mode; it does not disable source hashing or modify
any input. The three-line explicit-read candidate avoids changing the whole
interpreter's default encoding, but needs a maintainer-approved source transition
or a successor entry point before integration.

## Reproduce the bounded audit

Python 3.12 and the standard library suffice. From the repository root:

```sh
python3 -B scripts/research_package.py --package research/selected-json-utf8-replay --check-only
python3 -B scripts/research_package.py --package research/selected-json-utf8-replay
```

For a Git-free export, run:

```sh
python3 -B research/selected-json-utf8-replay/verify.py
```

Expect `PASS_SELECTED_JSON_UTF8_REPLAY tests=8` followed by the native-locale
flag and `no_new_kappa`. The runner registers ordinary and optimized audit
drivers. The child checker deliberately runs with assertions enabled in both
cases, because its CLI rejects `-O` by contract.

The eight test methods cover:

- An ASCII positive control under the legacy, unchanged UTF-8 and candidate modes.
- Separate U+211D failures at the record, certificate and manifest read boundaries.
- Successful replay of each boundary using both remedies.
- Exact Unicode inventory-path spelling and the legacy lookup failure.
- Invalid UTF-8 byte `0xff`: the legacy codec accepts it as U+00FF; both remedies
  reject it at every boundary. Certificate digests are recomputed for this
  fixture, so rejection tests encoding rather than a stale hash.
- Source corruption and a whitespace-only certificate byte change: both remedies
  still reject, with the original inventory and certificate diagnostics.
- Native cp1252 CLI execution without any encoding mock, when that host is
  available. This method is explicitly skipped on other native locales.

The portable codec control changes `io.text_encoding` only in an isolated child
process, models cp1252 when UTF-8 mode is off, and respects the explicitly enabled
UTF-8 mode. The native run independently checks that model. All fixture files
are written as bytes; source copies and child stdout/stderr are checked as bytes.
No package or pinned input is modified during replay.

## Task, overlap and scope

The expertise-based `verifier-engineering` picker suggested `portable-replay`
with nonce `269949e813c9ca9d693f6a23b2d0d0c2`. [TASK.json](TASK.json) records the
refined scope, original card, stop rule and next questions. This is a bounded
interpreter mismatch, within the card's allowed variations.

The newest visible handoffs in Discussion #1166, onboarding #1163, active
Discussions and targeted all-state PR searches were read. The repository's
`find_overlap.py` was also run, but its remote refresh could not run because
`gh` was unavailable; the sparse checkout omitted most local research notes.
The connector searches were bounded, and the visible Discussion page was not
a complete comment corpus. These checks do not establish exhaustive novelty.

[PR #5973](https://github.com/CrocSwap/integer-mult-bounds/pull/5973) repairs
invoice stdout byte binding; it is a separate issue and is not duplicated here.
[PR #2531](https://github.com/CrocSwap/integer-mult-bounds/pull/2531) repairs a
Lean-literal decoder, [PR #1834](https://github.com/CrocSwap/integer-mult-bounds/pull/1834)
repairs status-test reads, and [PR #2554](https://github.com/CrocSwap/integer-mult-bounds/pull/2554)
handles console output labels. They establish the encoding-portability precedent;
this contribution adds a pinned three-boundary selected-checker audit and a
verified invocation that preserves its selected source hash.

No native-operator replay, supplier admission, full multiplication theorem,
global locale audit or source-policy transition is established. The five
inherited framework assumptions remain. Local finite checks are author-checked
evidence, not independent human or proof-kernel acceptance.

## Open next questions

1. Integrate explicit UTF-8 reads without invalidating frozen source closures.
   First inventory current and historical consumers of the checker, then choose
   a successor entry point or an explicit source transition. The blocker is that
   maintainer policy decision, not the three-line change itself.
2. Run these exact fixtures on a native UTF-8 POSIX host and another supported
   Windows Python version. Report native-only skips separately. Those environments
   were unavailable locally; the portable codec model is not a substitute for
   claiming those native executions.

## Credit

The selected-checker logic and its source-binding contract are Douglas Colkitt's
with the retained contributors. The current productive-helper baseline is Mihir
Srivastava's; the codec precedents above retain their original authorship.
Prepared for `josecarlosgonzalezroque-design` with substantial OpenAI Codex
assistance in investigation, implementation, testing and writing. One agent,
no subagents. New work is Apache-2.0; original notices remain intact.
