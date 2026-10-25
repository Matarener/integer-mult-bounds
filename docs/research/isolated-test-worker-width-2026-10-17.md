# Isolated test replay worker width (2026-10-17)

## Question and scope

On the current 12-CPU-affinity host, does limiting the isolated test replay to
six workers preserve the test set and avoid the deadline-test failures seen at
the host-wide default? This is a local runtime and reliability measurement. It
does not change the selected construction or its conditional `κ`.

The measured source base is current main
`6f100d4bb5083f8c35d96fd95a539811c62f245c` (task card `replay-runtime`,
priority revision 6).
The runner is unchanged (`scripts/run_isolated_tests.py` SHA256
`88d738d3c1e8eb9bd580d9dc2f40b0421975e46013ce09bd6833d97a8600789d`). The
sorted inventory `tests/test*.py` has 178 files; its SHA256 is
`239713f3663532592f4399c21d3fe782a83d6356b5cbd7b91d67a2da541d4d96`, computed
over newline-joined basenames with a final newline. The interpreter was CPython
3.14.8. `TMPDIR` pointed to writable scratch under `/home` because `/tmp` could
not accept this user's writes during the run.

## Result

One full run at each width used the same test inventory and runner:

| Command | Wall time | Modules | Exit | Failed modules |
|---|---:|---:|---:|---|
| `python3 -B scripts/run_isolated_tests.py` (12 workers on this host) | 265.109 s | 178 | 1 | `test_historical_check.py`, `test_isolated_test_deadlines.py`, `test_pr_reconciliation.py` |
| `python3 -B scripts/run_isolated_tests.py --workers 6` | 286.056 s | 178 | 1 | `test_historical_check.py`, `test_pr_reconciliation.py` |

In this pair, six workers took 7.9% longer, but `test_isolated_test_deadlines.py`
completed instead of timing out under suite load. This is one uncontrolled pair
on a shared host; it is numerical evidence, not a general runtime bound or a
promise that six workers are optimal on other machines. The result supports a
reliability/runtime tradeoff only; it does not show a speedup.

Evidence status:

- **Proved from the pinned runner source:** for a fixed discovered file list,
  changing worker width does not change module membership, the command for a
  module, or the completion-receipt condition.
- **Measured once per width:** the wall times and full-suite outcomes in the
  table above. These observations do not prove a runtime inequality for future
  runs or other hosts.
- **Not established:** a generally faster worker width, a general deadline
  reliability guarantee, a new mathematical bound, or a change to selected
  `κ`.

The same `test_isolated_test_deadlines.py` module passes by itself (7 tests).
Its short per-module budgets are sensitive to contention in the full suite.
The isolated command `python3 -B -m unittest discover -s tests -p
test_isolated_test_deadlines.py -v` passed all 7 tests on the pinned checkout.
Both full runs still fail `test_historical_check.py` because the current live
hashes of `docs/ci-verification.md` and `scripts/run_isolated_tests.py` are not
listed among the frozen historical package's accepted live successors. Both
also fail `test_pr_reconciliation.py`: its accepted-successor control reports
an integrated-source digest mismatch for `scripts/run_isolated_tests.py`, and
current family decisions disagree with PR-ledger closure records for multiple
PRs (for example, the missing-closure control sees the historical archive
closure for PR #620). These are separate source/ledger consistency gaps; this
measurement does not repair or validate them.

## Why the width change preserves coverage

The runner discovers `files = sorted((ROOT / 'tests').glob('test*.py'))`
before passing the list to `run_modules`. For fixed `files`, that function
clamps only the worker count and calls
`ThreadPoolExecutor.map(run_one, enumerate(files))`. Enumeration is a
bijection from list positions to files; `map` invokes `run_one` once for each
input and returns results in input order. The width is used only as the
executor's `max_workers`. Each invocation therefore retains the same module
arguments and exact completion-receipt check. This is a source-level proof of
coverage preservation, assuming the discovered list and source tree do not
change during a run; it says nothing about the test outcomes or timings. On
this checkout, the relevant runner regression tests passed (10/10), including
all-module reporting, concurrency, ordering, and completion checks.

No cache or evidence reuse was introduced by this comparison. At the pinned
base, each invocation uses the runner's private temporary receipt and
bytecode-prefix behavior, then removes its temporary directory; the comparison
adds no cache invalidation rule. A separate open change, [PR #3348](https://github.com/CrocSwap/integer-mult-bounds/pull/3348),
updates child-process bytecode-cache policy in the same runner. This report
does not measure that pending source change; repeat the pair after it lands
before applying these numerical observations to a newer base.

## Reproduce

On a checkout of the pinned source, set `TMPDIR` to a writable scratch
directory and run both commands above. The default command uses the runner's
host CPU count. The second command is an opt-in six-worker measurement; this
report does not change the repository's existing `verify-tests` Make target.

## Open next questions

- Repeat paired widths on an otherwise idle host before treating the runtime
  difference as stable.
- Reconcile the historical accepted-live hashes and the current PR-ledger
  projections, then rerun the full suite for an all-green result.
