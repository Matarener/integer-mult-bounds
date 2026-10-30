# Native replay of the selected-inventory repair

**A fixture portability correction and independent native replay of PR2947.**
The archived source-inventory traversal, its assertions, production scripts and
selected frontier are unchanged. This contribution closes one replay blocker
in the [existing investigation](https://github.com/CrocSwap/integer-mult-bounds/discussions/2946).
It does not adopt the repair into production or replay a multiplication supplier.

## Failure and correction

On macOS, the unmodified
[`selected-inventory-fail-closed/verify.py`](../selected-inventory-fail-closed/verify.py)
runs 59 groups; 58 pass and `test_complete_inventory_and_entry_budget` errors
with `ValueError: Package symlink escapes root`. The fixture uses
`root = Path(td)` under the aliased `/var/folders/...` temporary directory.
The helper resolves a descendant to `/private/var/folders/...` and checks it
against that unresolved root. Every production `check()` call already resolves
its package root before invoking this helper.

The [one-line patch](fixture.patch) changes only that fixture assignment to
`root = Path(td).resolve()`. [fixture_adapter.py](fixture_adapter.py) applies
the exact byte substitution in memory after authenticating the original test
source. It rejects changed or already-adapted inputs. No archived file is edited.
The traversal's containment check and all test assertions remain intact,
including the exact three-entry limit, the failing two-entry limit, invalid
limits and the zero-entry empty-directory control.

## Scope and evidence

[SOURCES.json](SOURCES.json) pins the archive, predecessor checker, retained test
suites and selected inputs at canonical main
`20ecf2891d80b5acf18d980b2164fb44ea7faa90`, priority revision 6.
[TASK.json](TASK.json) records the handoff and the narrowing from adoption to
this first native replay blocker. The selected baseline command passed at entry.

The local matrix on macOS 26.3.1 arm64, uid 501, produced these results with
both **CPython 3.12.14 and 3.14.7**; exact versions and receipts are in
[EVIDENCE.json](EVIDENCE.json):

| Temporary root / replay | Original groups | Result |
| --- | ---: | --- |
| Canonical root, unmodified archive | 59 | all pass, zero skips |
| Explicit directory alias, unmodified archive | 59 | only the budget fixture errors |
| Explicit alias, corrected replay | 59 | all pass, zero skips |
| Explicit alias, corrected replay under `-O` | 59 | all pass, zero skips |

Five additional control groups pass normally and under `-O` on both versions.
They reproduce the alias-only error, retain the canonical-root positive control,
reject a disabled entry limit, reject changed/already-adapted fixture bytes,
reject traversal-source drift before compilation, and reject skipped, failed
or incomplete suites. The replay requires all 59 original groups to execute
and pass without skips. The archive's source/proof/link, permission, actual CLI,
injected I/O and restoration controls are retained.

## Reproduce

From a full checkout, standard library only:

```sh
python3.12 -I -B research/selected-inventory-native-replay/test_adapter.py
python3.12 -I -B research/selected-inventory-native-replay/verify.py
python3.12 -I -O -B research/selected-inventory-native-replay/test_adapter.py
python3.12 -I -O -B research/selected-inventory-native-replay/verify.py
```

The replay takes about five seconds locally. It prints the archive's original
`tests=59 skipped=0` marker followed by `PASS_SELECTED_INVENTORY_NATIVE_REPLAY`.
The first command constructs a temporary directory alias explicitly, so it also
checks the failure on hosts whose default temporary root is canonical.
Use a POSIX account that cannot bypass directory permissions and supports
directory symlinks and FIFOs; unsupported fixtures fail this complete replay.

The dedicated [native workflow](../../.github/workflows/selected-inventory-native-replay.yml)
runs these commands on Ubuntu and macOS for changes to this contribution and
by manual dispatch. Its path filter is not a complete transitive dependency
invalidation service. Like its predecessor, this package has no generic
`VERIFY.json` registration. All scientific files are enumerated and hashed by
the unchanged selected checker during each replay. Inputs must remain stable
during execution. This is source-binding evidence, not a concurrent-writer
snapshot, full supplier replay, theorem validation or new kappa.

Hosted results, when available, must identify the tested head separately from
the local receipts. Native Windows and independent human review are unclaimed.

## Open next questions

The production-adoption handoff remains open. Start with the exact current
consumer pins of `scripts/verify_selected_result.py` and
`scripts/research_baseline.py`, then choose a successor entry point or explicit
historical overlay and replay its affected consumers. The older handoff's two
named audits are not a complete current dependency inventory. Adoption and
source-pin compatibility review are outside this fixture-only change; the
structured question is in [TASK.json](TASK.json).

## Credit

Nick Petalas supplied PR2947's traversal, 59-group replay and the failure model;
this contribution corrects one fixture and adds native evidence. Douglas
Colkitt supplied the selected checker; Mihir Srivastava/PR841 supplied primary
proof guards; yssite/PR959 supplied link closure; Arham Tahir/PR2793 supplied
the separate path-reuse prototype. Aaron Wang and Wentao Li retain their
consumer-audit credit, and the selected construction retains its full supplier
lineage. New adapter, controls and packaging by Arham Tahir with substantial
OpenAI Codex assistance. Apache-2.0. This replay is not maintainer acceptance.
