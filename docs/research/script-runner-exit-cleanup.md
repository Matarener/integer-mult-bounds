# Direct-script completion and descendant cleanup

This is a verifier-engineering correction based on canonical main
`20ecf2891d80b5acf18d980b2164fb44ea7faa90` (priority revision 6). The portable-replay
scope is narrowed to the lifetime of ordinary POSIX descendants launched by
`scripts/run_parallel.py`. It makes no mathematical or selected-result claim.

A script can start a solver with its output redirected to `DEVNULL` and exit
successfully while the solver continues running. Before this correction, the
real CLI printed `PASS all 1 scripts` and returned; a finite child then wrote an
observation file after the runner returned. A failed leader similarly left its
ordinary descendants running. The cancellation path already owned and stopped
active groups, but the normal-completion path discarded that ownership without
stopping the group.

After collecting a leader's output, the worker now stops its POSIX group before
unregistering it. The existing registration lock also serializes this operation
with the controller's cancellation snapshot: whichever path acquires ownership
performs cleanup. A cleanup error retains registration for the controlling
cleanup path and prevents a success report. Existing output blocks and failure
labels are preserved. Other process groups are not signaled.

This builds on [ywz65's direct-script cancellation correction, PR2676](https://github.com/CrocSwap/integer-mult-bounds/pull/2676),
its independent cancellation audit [PR2777](https://github.com/CrocSwap/integer-mult-bounds/pull/2777),
and the existing isolated-test runner's completed-leader cleanup. The new tests
exercise the ordinary successful and failed leader exits that the cancellation
fixtures did not cover. Substantial OpenAI Codex assistance was used in preparing
this contribution for roger-sato; Apache-2.0.

## Reproduce and verify

The five regressions invoke the actual CLI using disposable source fixtures.
Ordinary children and grandchildren close Unix-domain observer connections when
terminated; an unrelated process in its own group must remain alive. The tests
cover success, failure, an already-joined tree, a parent-only cleanup mutant, and
an injected group-signal error. The parent-only mutant must fail the lifetime
observation, and the signal error must produce a nonzero result with both the
original error and the cleanup-retry diagnostic.

Run from the repository root with CPython 3.12:

```sh
python3.12 -W error -B -m unittest discover -s tests -p 'test_script_exit_cleanup.py' -v
python3.12 -O -W error -B -m unittest discover -s tests -p 'test_script_exit_cleanup.py' -v
python3.12 -W error -B -m unittest discover -s tests -p 'test_script_*.py' -v
python3.12 -W error -B - <<'PY'
import unittest
patterns = ['test_script_cancellation.py', 'test_parallel_verification.py',
            'test_parallel_assertions.py', 'test_parallel_memory.py']
suite = unittest.TestSuite(unittest.defaultTestLoader.discover('tests', pattern=p)
                           for p in patterns)
result = unittest.TextTestRunner(verbosity=2).run(suite)
raise SystemExit(not result.wasSuccessful())
PY
```

Local validation used macOS arm64, CPython 3.12.14 and Git 2.54.0. Both focused
runs passed all five tests. On the original runner, the same suite fails three
tests; the joined-tree control and mutant-sensitivity control pass. The combined
script suite passes with nine existing Linux/Windows observer tests skipped on
macOS. The four existing runner modules run 30 tests: 20 pass and ten skip
(those nine observers plus the Windows memory API smoke test). The Ubuntu 3.12
reconciliation workflow now explicitly runs the combined script suite.

## Historical compatibility and limits

The reconciliation92 manifest and frozen runner remain unchanged. The existing
historical adapter admits only the exact new live runner SHA-256
`3e27934d4c5185e44bf88e0bc51cdb0af97286e033feb78494f071cd381b1e35`, while still replaying
the authenticated historical runner
`f046e98e4c296fde954b93b466b7f359be0c05c287d96943e016f0b850587387`.
An independent run of the actual default command in its complete 383-file input
closure passed all 92 pinned trees and 4,564 distinct blobs. An unknown live
runner and a corrupted frozen runner both reject; all original inputs remain
unchanged.

```sh
python3.12 -B scripts/replay_historical_check.py reconciliation92
python3.12 -B scripts/research_package.py --package research/isolated-test-bytecode
python3.12 -B scripts/research_package.py --package research/isolated-descendant-bytecode
python3.12 -B scripts/research_package.py --package research/historical-snapshot-one-pass
```

Both bytecode packages pass every registered command (their declared outcomes
remain `completed` and `partial`, respectively). The snapshot package has a
known baseline failure: its 27 tests yield one failure and one error because the
tooling-ledger adapter does not admit the current `docs/ci-verification.md` hash
`a3711fe12d560fac7726c530b9c8c622182f3d4f231a876c163616e49bd911bc`.
The identical result was reproduced through the registered CLI in an 82-file
closure containing only exact canonical-main bytes. That unrelated admission
list is unchanged by this contribution.

Native Windows lifetime behavior was not changed or verified. Deliberately
detached process groups remain outside the owned-group contract. This change
does not add execution deadlines or require ordinary descendants to finish
their work successfully: it stops them when their owning script finishes.
