# Validation record

Base: `32890bc5de034ab8fc93ac88ead7279a6a416d04`.
Evidence is author-checked with substantial OpenAI Codex assistance.

The final replay has 25 named case groups. An initial run
passed the checks but failed while serializing a bytes-valued observation;
the receipt serializer was corrected to use a return-code/stdout-hex object.
That initial run is not counted as passing published evidence.

An initial full repeat also caught an unlocalized diagnostic mismatch. Twenty
focused diagnostic cycles did not reproduce it, but further bounded probes
failed at cycles 32 and 24 (one based). The retained exception chain localized
the failure to opening the newly published `status.json`: `PermissionError`,
errno 13, no winerror. It was not the requested executable's native error.
The cause of the host's temporary denial is not established. The wrapper now
retries only that read within the existing startup bound, outside the native
error reconstruction. Deterministic transient/permanent denial controls were
added. No diagnostic assertion was weakened and no failing run is counted as
passing evidence.

Registered, source-export, committed-byte and final overlap results follow.
No full scientific or historical suite is needed for this isolated package;
no such replay is claimed.

## Final executable checks

- Native Windows 11 build 26300 / CPython 3.12.0: direct `-I -W error -B`
  and `-I -W error -O -B` runs pass all **25** named case groups. Their entire
  case arrays agree, and each receipt's two implementation hashes match the
  actual committed source candidates.
- `python -B scripts/research_package.py --package research/windows-git-launch-diagnostics`
  passes metadata/source pins and both registered modes, including the nested
  Windows Job Object boundary. Marker: `PASS_REGISTERED_RESEARCH_PACKAGE`.
- After the bounded read retry, a separate 50-iteration repetition of
  `launch_cases` passes all seven diagnostic comparison groups on every
  iteration. This was a local stability probe, not a broader Windows claim.
- Ubuntu/WSL2, CPython 3.12.3: source hashes and all portable report controls
  pass with `PASS_PORTABLE_CONTROLS_WINDOWS_NOT_RUN`. The native-only flag
  rejects on Linux as intended. The portable receipt does not claim native
  process or real-Git execution.

## Coordination and provenance

Canonical main was fetched again before publication and remained
`32890bc5de034ab8fc93ac88ead7279a6a416d04`; relevant guidance and the selected
record had no delta. The final full helper refresh covers 378 open PRs at
06:16 UTC and 4,796 Discussion records at 06:18 UTC on 2026-10-25, with
complete reported pagination. Sparse note coverage still omits 7,401 of
7,402 tracked notes; relevant sources/docs and the ledger were read directly.
An all-state Windows/launch search and a fresh #4681 read supplement it.

Two overlapping diagnostic claims surfaced during the refresh. Comment
[19174028](https://github.com/CrocSwap/integer-mult-bounds/discussions/4681#discussioncomment-19174028)
released diagnostics and moved to owner-death setup; comment
[19174025](https://github.com/CrocSwap/integer-mult-bounds/discussions/4681#discussioncomment-19174025)
released its independent-acceptance offer when its donor cancelled. Their
preliminary missing-executable corroboration is credited, but neither is
claimed as an independent review or dependency of this implementation.
Owner-death and shared-runner adoption remain outside this contribution.

The pending fork snapshot is byte- and blob-bound in VENDOR.json. Its external
publication history is explicitly separate from the canonical SOURCES pins;
no source pin was weakened to obtain a passing executable check.

## Committed source and standalone export

Science/evidence commit: `68f3e912d04d74fbb98b806852007f7231a8b1af`.
All 17 package files pass `check_research_commit.py --check-source-history`;
the canonical Git provenance resolves in publication ancestry at the recorded
base. This history check does not claim ancestry for the separately labelled
external PR5463 snapshot.

The official exporter and archive checker pass for those 17 payloads. Archive
SHA256 on this host is
`1eafc6c49230b8c1f83be35e6c779bbb97141329b6653bc6ed68d16ddaa36c06`;
it is a transport identifier, not a cross-environment compression expectation.
The extracted source has 18 files including its export receipt. All receive
Windows read-only file attributes; directory ACLs were not made read-only.
`git rev-parse --show-toplevel` from the exported package rejects with 128.
Git remains installed for the disposable real-Git fixture repository.

The exported `-I -W error -O -B verify.py --require-windows` run passes all 25
groups in 8.30 seconds. Its **complete parsed receipt equals** the committed
native optimized receipt, with no excluded fields. Every export file hash is
unchanged afterward. This is the actual committed export replay, not merely
a claim that the source could be exported. The later publication commit only
adds these validation facts to this file; executable and evidence bytes stay
equal to the replayed science/evidence commit.

```sh
python -B scripts/check_research_commit.py --package research/windows-git-launch-diagnostics --check-source-history
python -B scripts/export_research_package.py export --package research/windows-git-launch-diagnostics --ref 68f3e912d04d74fbb98b806852007f7231a8b1af --output launch-diagnostics.tar.gz
python -B scripts/export_research_package.py check launch-diagnostics.tar.gz
# Extract into a directory outside any Git checkout, then run its verify.py
# with the native command above. File attributes are an additional local guard.
```

The package preserves Windows CRLF receipt bytes using the predecessor's
attribute policy, while retaining ordinary whitespace checks. `git diff
--check` passes with that scoped policy. Hosted CI is separate from these
local receipts and is not claimed here.
