# The isolated runner is outside the accepted successor list

**Partial. No new exponent.**

`scripts/run_isolated_tests.py` on canonical main has SHA-256
`ef5035e6216d39569da670f32b2717c870b23c418016fd134cc0a72649fb912a`.
The reconciliation checker admits a predecessor
`96ea543e6c707424afe247e77bd86c82152f90fc76a0773c4232145da5cdf8d1`
and seven later digests. The last accepted digest is
`8f9298eb83184a447ee2dda64a42dfc5a56df08e4affae56f99974cad632713a`.
The current digest is none of those eight values.

## What was executed

The checker hashes the runner and reads the successor entry from
`scripts/verify_pr_reconciliation.py`. It does not edit the list or the runner.

`scripts/research_baseline.py` needs
`research/community-frontier1094-audit/ASSEMBLY.json`, which this checkout
does not have. The orientation used here is the successor gap in PR 3688,
head `3463ba61bd906f8f2c3e9d62c02f8840401e0a0c`.

## Scope and evidence

Original card: `portable-replay`, priority revision 6, refined to this digest.
[TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the selected record, the runner and the
checker. No selected frontier file changes.

## Reproduce

From the repository root, CPython 3.12:

```sh
python3.12 -B research/isolated-runner-successor/verify.py
python3.12 -B research/isolated-runner-successor/test_verify.py
python3.12 -B scripts/research_package.py --package research/isolated-runner-successor
```

## Open next questions

This digest is the gap. Admitting it would leave the comparison.

## Credit

roger-sato recorded that the current runner follows the last accepted digest
`8f9298eb`.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
