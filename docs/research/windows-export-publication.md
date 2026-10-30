# Windows export publication without hard links

The committed-package exporter can finish writing a valid archive and then fail
at `os.link(staging, output)` when its Windows environment prohibits hard links.
Use a same-directory `os.rename` on Windows, where an existing destination is
rejected. Retain `os.link` on POSIX, where `os.rename` would replace a file.
Cleanup tolerates the staging name having been consumed by a successful rename.

This is a tooling portability repair. Archive generation, Git source selection,
receipt fields, hashes, modes and integrity checks are unchanged. There is no
new mathematical claim, supplier admission or kappa improvement.

## Reproduced failure and contract

At canonical main `3f0152a32eeebac0df11946dbd50cabe5a7f7839`, the native Windows
restricted execution environment permits ordinary writes in the workspace but
rejects the exporter's hard-link publication with `PermissionError: [WinError 5]`.
Of the 37 existing exporter tests, 12 fail at that operation (two assertion
failures and ten errors). The original direct-replay test passes outside the
restriction. This is an environment-specific failure, not a claim that ordinary
Windows cannot create hard links.

The new regression injects the unavailable-hard-link error explicitly, making
that condition reproducible on other Windows hosts. It fails against the
original exporter and passes after the repair without invoking `os.link`.

The [Python 3.12 `os.rename` contract](https://docs.python.org/3.12/library/os.html#os.rename)
states that Windows rejects an existing destination. The staging file already
lives in the output directory, so this change requires no cross-volume copying.
Publication happens after the Git stream's final status check and closure of
the archive and writer handles. The initial existence check remains, but the
publication operation also refuses a destination created after that check.
There is no overwrite or copy fallback after a permission failure.

The new five-test module checks:

- Successful, byte-identical repeated exports when hard links are unavailable;
  both integrity and declared-input checking pass.
- Publication receives a complete archive in the destination directory.
- A competing file or directory created at the publication boundary is retained,
  while the export raises `FileExistsError` and removes its staging file.
- A publication error propagates unchanged and leaves no output or staging file.
- An archive-close error prevents publication and removes its staging file.

The existing tests retain Git-free replay, exact binary and unusual Git names,
historical input commits, executable modes, replacement-ref isolation, malformed
receipt/input rejection, existing-output protection and late Git failure.
This is a stable-directory publication contract; it does not provide crash
durability or defend against replacement of parent directories during execution.

## Verification

Host: Windows 11 build 26300, CPython 3.12.10, Git 2.53.0.windows.3,
locale encoding cp1252. Temporary test directories were placed in the writable
workspace using `TEMP` and `TMP`.

From the repository root:

```sh
python -W error -B -m unittest discover -s tests -p 'test_research_export*.py' -v
python -O -W error -B -m unittest discover -s tests -p 'test_research_export*.py' -v
python -B scripts/research_selected_baseline.py
git diff --check
```

The complete exporter suites pass **42 tests, zero skips** in each mode, taking
40.892 and 44.827 seconds in the restricted environment. The selected baseline
passes its binding-only check; it is not a scientific cold replay. The new
test module is included by the existing CI `test_research_*.py` discovery.

A separate session probe outside the restriction exports the same real Git
fixture through the original and changed functions. Both complete receipts and
all 10,240 archive bytes agree. Replacing the Windows publication with
`os.replace` makes the late-destination regression fail; returning without
publishing also makes the complete-publication regression fail. These are
local differential/mutation observations, not hosted-CI evidence.

Original exporter SHA256:
`29d4c4e27ca4580734f92de0a0087c7a8750ab4eefe7c6601729f9f652725138`.
The selected record remains SHA256
`9b8d0eea95b3bf0dfcb7938a732a6439b87a2685dec2a5ab9e525b3b34debbfa`.

POSIX execution, other Windows/Python versions, exFAT and network filesystems
were not tested here. No historical scientific replay or selected-frontier
change is proposed. Hosted CI and external review remain separate.

## Task selection and overlap

Task `portable-replay`, priority revision 8, picker seed
`1c87352aa1fd006e0873d0e6c0a015b1`, scope key `831cc1a3c8f9ff01b197`.
Scope is **refined** to one reproduced export-publication failure; the card's
immutable-source and proof-relevant-content requirements remain in force.
Exporter publication portability removes a concrete barrier to distributing
reproducible research artifacts.

Read AGENTS.md, autoresearch.md and CONTRIBUTING.md on canonical main, then the
handoff thread and active discussions. The reported CI-navigation handoff was
already resolved by #6050 and was not repeated. The current task picker supplied
the verifier-engineering cards. Read the selected #6030 review and ran its
current binding-only orientation; the five framework assumptions remain.

Canonical main was fetched again on **2026-10-29 at 15:08 UTC** and remained
`3f0152a32eeebac0df11946dbd50cabe5a7f7839`. Live all-state PR searches for hard
links, `os.rename`, exporter publication and Windows exports found no equivalent
repair. The nearest exporter work includes #3138, #4579 and #5389; #6165 and
#5973 address different JSON/stdout encoding boundaries.

The required overlap helper was run for the card and the refined terms. It had
no remote cache or `gh` access, and sparse local-note coverage was partial.
Separate GitHub API searches and visible discussion pages supplement that
coverage; they do not establish exhaustive novelty or full discussion history.
No advance reservation was posted for this short session.

## Open next questions

Corroborate the publication tests on POSIX and another supported Windows
interpreter. This checks the retained POSIX link path and Windows API behavior;
start with the complete exporter commands above. The native Windows-only
hard-link-unavailability test intentionally skips on POSIX. Those executions
require the corresponding hosts; they are not implied by this Windows result.

Credit Tekalign's committed exporter (#3138), Mihir Srivastava's native Windows
fixtures (#4579), roger-sato's path and source-integrity safeguards, Ali Romman's
historical-input export (#5389), Douglas Colkitt's replay contract and the
retained contributor lineage. Prepared for josecarlosgonzalezroque-design with
substantial OpenAI Codex assistance, one agent. Apache-2.0.
