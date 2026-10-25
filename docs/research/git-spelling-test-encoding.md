# Portable diagnostics in the exact Git-spelling tests

The exact Git-spelling regression now runs under an ordinary Windows console
environment. Its subprocess explicitly selects the same output encoding as its
capture decoder. This integrates **Arham Tahir's previously published fixture
repair**, then adds controlled ASCII, CP1252 and UTF-8 cases. The production
planner already rejected the alias correctly; its validation rules are unchanged.

## Reproduction and scope

At canonical main `32890bc5de034ab8fc93ac88ead7279a6a416d04`, the command

```sh
python -W error -B tests/test_research_git_spelling.py GitInputSpellingTests.test_unicode_spelling_is_not_normalized -v
```

fails on native Windows with redirected CP1252 output. The test expects the
literal combining accent in `src/cafe\u0301.json`, but Python's stderr renders
that unrepresentable character as the six ASCII characters `\u0301`. Selecting
UTF-8 only in the parent's `subprocess.run(encoding=...)` decoder does not select
the child's writer. A representable CP1252 non-ASCII character can additionally
make that UTF-8 decoder raise `UnicodeDecodeError`.

This was already diagnosed and accompanied by a minimal patch in
[Arham Tahir's public source and evidence](https://github.com/Arham-Tahir64/integer-mult-bounds/tree/de28bf2603348d79f6303b2bf710580ecf3cfa65/research/replay-input-windows-diagnostics).
The patch remained unapplied to the current test. The later
[PR5358 Windows audit](https://github.com/CrocSwap/integer-mult-bounds/pull/5358)
also recorded the failure. This contribution adopts that correction in the
shared test fixture; the diagnosis and original repair retain their credit.

The test helper now sets `PYTHONIOENCODING=<encoding>:strict` only in its child's
environment and decodes with the same encoding. UTF-8 is the default. The
NFC/NFD test runs with three different inherited console encodings and verifies
that the parent setting stays intact. Its default UTF-8 child still requires
the literal rejected path; no normalization or permissive decode is introduced.

A separate test deliberately runs the planner with ASCII, CP1252 and UTF-8
output. Its rejected name contains both U+00E9 and U+1F680, distinguishing raw
CP1252 bytes from escaped characters. The diagnostic assertion applies Python
stderr's `backslashreplace` rendering to the expected name in that selected
codec. Input names and Git objects are never converted or normalized. Every
rejection still requires exit 1, the exact-path diagnostic, empty stdout and
unchanged prior GitHub-output bytes. Correcting only the declaration then selects
the expected consumer for the same Git change.

## Verification

Run the focused module with Python 3.12 and Git:

```sh
python -W error -B -m unittest discover -s tests -p test_research_git_spelling.py -v
python -O -W error -B -m unittest discover -s tests -p test_research_git_spelling.py -v
```

Local results on 2026-10-24:

| Environment | Normal test driver | Optimized test driver |
| --- | --- | --- |
| Windows 11 build 26300, CPython 3.12.0, Git 2.47.1.windows.1; parent stdout/stderr CP1252 | 9 passed, 1 existing skip; 88.039 s | 9 passed, 1 existing skip; 94.040 s |
| Ubuntu/WSL, CPython 3.12.3, Git 2.43.0; fixtures on the Linux temporary filesystem | 10 passed; 16.222 s | 10 passed; 14.560 s |

The Windows skip is the existing test that creates control characters in actual
filenames, which Windows forbids. Both new encoding dimensions run on both
platforms. `-O` applies to the test driver; the existing planner subprocess
command remains `python -B`, and `unittest` assertions remain active.

Three deliberate changes in separate disposable copies all caused exit 1:

- Remove the helper's `env=env`: the inherited ASCII/CP1252 cases fail the
  literal-path assertion.
- Hard-code the capture decoder to UTF-8 while retaining the requested child
  encoding: the explicit CP1252 case raises `UnicodeDecodeError`.
- Replace exact `name in paths` membership with NFC-normalized membership:
  the Unicode-alias test fails because the planner incorrectly returns success.

The working test and runner bytes were compared before and after these controls;
no mutation was retained. The selected source-closure orientation also returned
`PASS_RESEARCH_BASELINE_BINDINGS_ONLY`. It is a metadata check, not mathematical
replay. Native source-reader process ownership, a complete selected cold replay,
other Python versions, independent human review and proof-kernel verification
are outside this contribution.

The existing dependent registration also passes on native Windows and Linux:

```sh
python -B scripts/research_package.py --package research/replay-input-head-spelling
```

It authenticates the historical `836b19bfa309ceafbc8ee32a15e8c4b10dde7e11`
runner, reproduces three old omissions and three current rejections with two
canonical controls, then runs the ten Git-spelling tests and five retained
lexical-input tests. This historical commit was explicitly fetched in the shallow
checkout; the registration needs its source objects. All three registered commands
pass. The Windows spelling stage retains its one existing filename skip.

A scan of all 6,922 tracked top-level `research/*/SOURCES.json` and `VERIFY.json`
files at the base finds one declaration of the changed test, in
`research/replay-input-head-spelling/VERIFY.json`, and no source pin for it.
Nested formats and undeclared imports are outside this inventory. The production
runner's working bytes equal the base blob. The Git diff contains only the test
and this note. Planning that two-file change selects only the existing
`research/replay-input-head-spelling` registration; its frozen manifest is unchanged.

## Sources, coordination and credit

The base runner `scripts/research_package.py` has Git blob
`48fe9feb4699c09e95505d95c327ea998ac8b3a7` and SHA256
`84a45190a6a96c20993a0d4a1045fbf24de660d2e6fef8f8a447bb3d1aa78db6`.
The original test has Git blob `38c2244e1c60c6a86bb39f556284d3def46144c9`
and SHA256 `5b21271c1daacb69f9214a4f6f22282cafbd232bf1a31b8e2e3c5c16f5df4153`.
Only the test and this evidence note change. Frozen packages, source pins,
production code and the selected result retain their bytes; no new kappa is claimed.

Task `portable-replay`, priority revision 7, chooser nonce
`1a24abc3456843077e97beb942187bc5`, scope key `831cc1a3c8f9ff01b197`.
The scope is refined to the documented test portability handoff. The
[canonical claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/2983#discussioncomment-19170236)
records the bounded question and initial overlap. Entry remote coverage included
330 open PR bodies and 4,724 Discussion records with complete reported pagination.
Targeted all-state searches and the prior investigation thread identified the
existing diagnosis and unintegrated patch. Local notes were sparse at entry;
searches do not establish novelty against every diff or unpublished result.

The submission refresh at 22:09 UTC covered all 7,402 tracked in-scope local
notes, 330 open PR bodies and 4,725 Discussion records, with complete reported
pagination and no warnings. Its exact-spelling terms returned the credited
predecessor investigations and package notes. Canonical main was fetched again
and remained `32890bc5de034ab8fc93ac88ead7279a6a416d04`, priority revision 7.

Credit Arham Tahir for the diagnostic audit and proposed encoding repair,
Nick Petalas's [PR3007](https://github.com/CrocSwap/integer-mult-bounds/pull/3007)
for the exact-input guard and behavioral tests, Arham Tahir's PR2994 for the
original alias counterexample, ToikY for the macOS audit, and Nick Petalas,
woklerx, Charles Bethin, Douglas Colkitt and the retained runner contributors.
Integration, encoding controls and this note prepared for Mihir Srivastava with
substantial OpenAI Codex assistance, one agent. Apache-2.0.

## Open next questions

No additional alias census or production change follows from this fixture
defect. The useful next action is maintainer review of this focused integration.
The separate Windows descendant-held-pipe question in PR5358 remains open and
requires its own real-process ownership fixture; these encoding tests do not
address it.
