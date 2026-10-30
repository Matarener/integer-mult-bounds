# Validation record

Base 553d26d796fde9871ff2661a49ac7732e945410f. Registered interpreter:
`/Users/aliromman/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3`,
Python 3.12.14 on macOS arm64.

Completed before the final benchmark:

- The unchanged complete selected source passes and matches both saved artifacts.
  Its first cold measurement was 391.93981024995446 s. This single measurement is
  orientation evidence; it is not substituted for the alternating benchmark.
- The uncached quadratic prototype passes the full selected replay in 180.42 s.
  This is not the final implementation or final speedup figure.
- The bounded-cache implementation passes the complete source and all new controls.
  RESULT.json records 39041 state requests,19988992 amplitude entries,21073 cache
  hits and 17968 misses. The cache holds at most 8192 entries.
- The adapter checks compare 1522 literal states and 22700 amplitudes. Changed keys,
  invalid numeric aliases, mutable outputs, capacity and eviction controls pass.
- Three actual source-proof omissions reject. The width-mismatch assertion rejects
  under optimized Python. All 13 assertions in the declared input closure are
  retained as explicit failures in the derived compiler.
- `scripts/research_package.py --package research/selected-quadratic-replay --check-only`
  passes metadata and pins. This is not scientific acceptance.

The serial six-process benchmark passes with identical stdout SHA256
`1975d01770a017b3f0b3a98a54c7c79b887d90ba0a2e1a77c37db05c385fa42b` in every run.
Medians:269.0034654160263 s literal and 98.37080179096665 s new; ratio 2.7345864882513213.
BENCHMARK.json retains every run, source input and implementation digest.

The complete actual-state audit passes: 17,651 distinct inputs and 9,037,312
amplitude entries per original literal interpreter. Both interpreters agree
with every new state numerator, zero and denominator. The trace SHA256 is
`73ac04db73d83151efb474925d48298664cc7490d31bdec7a70dcf79b448f481`.

The canonical-main refresh at de5ec2e7a6074068452f45b1a191b5c72832df4a
read priority 8. At 16:25 UTC, the overlap cache covered all 312 open PRs and
5,110 Discussion records. The only matching active claim was this investigation.
The local scan covered 7,840 main notes at the frozen base. Later main notes
require a separate search before submission.

The scientific commit is `83823449895cb1126c246570b92992d45157fe02`.
The byte/mode preflight and official 53-file export pass. Its sealed export
(including the export manifest) passes both registered commands serially with
Python 3.12.14, `-I -O -B`, empty PATH, no Git, files mode 444 and directories
mode 555. All 54 file bytes and modes remain unchanged. PORTABILITY.json records
the export digest. Separate corruptions of the actual quadratic engine, selected
WORD and native compiler each reject before evaluation and restore exactly.

A second live overlap refresh at 16:35 UTC covers 313 open PRs and 5,114
Discussion records. Only this investigation matches the scoped terms. A separate
Git search of the latest canonical main at de5ec2e7 finds no matching package;
all 31 exact input bytes still match that main. Priority 8 is unchanged.

The checkout is shallow. The optional full-history source-ancestry preflight
is not run. Explicit source bytes and Git blobs, committed export and Git-free
replay are checked. This is an export-availability check, not full Git history.

The standard `scripts/research_package.py --package` runner also passes both
commands under Python 3.12.14 with `PASS_REGISTERED_RESEARCH_PACKAGE`.
Only documentation, TASK wording and the portability receipt change after the
scientific commit. All 12 Python implementation hashes still match BENCHMARK.json.
See the canonical Discussion for the final published head and readback status.
Hosted CI, independent human review and proof-kernel acceptance are separate.
