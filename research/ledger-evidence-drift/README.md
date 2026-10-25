# 539 ledger rows omit the intake path

**Partial. No new exponent.**

The Markdown ledger and the JSON ledger both list 3028 pull requests. The four
disposition counts agree:

```text
incorporated 2064
partially reviewed 902
superseded 2
unreviewed 60
```

Every contributor login and every disposition agrees. On 539 rows, from PR
1365 through PR 3528, `reconciliation_evidence` in the JSON contains
`docs/research/pr-intake-decisions.json` and the Markdown evidence cell does
not. Recorded credit is unchanged.

## What was executed

The checker reads the two committed ledgers. It does not rewrite them.

`scripts/research_baseline.py` needs
`research/community-frontier1094-audit/ASSEMBLY.json`, which this checkout
does not have. The orientation used here is the ledger comparison in PR 3695,
head `ed054d34e21225cf3fc7a6207d7ce1146c62531e`.

## Scope and evidence

Original card: `overlap-receipt`, priority revision 6, refined to this drift.
[TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the selected record and both ledgers. No
selected frontier file changes.

## Reproduce

From the repository root, CPython 3.12:

```sh
python3.12 -B research/ledger-evidence-drift/verify.py
python3.12 -B research/ledger-evidence-drift/test_verify.py
python3.12 -B scripts/research_package.py --package research/ledger-evidence-drift
```

## Open next questions

This drift is the comparison. Rewriting the ledger would leave it.

## Credit

muatfannajm-dot published the ledger comparison.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
