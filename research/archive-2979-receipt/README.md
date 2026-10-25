# PR 2979's 112 archived blobs match canonical main

**Partial. No new exponent.**

PR 2979 by aigent-marius (@mdumitrean) is archived at head
`be191346391661f4d35fc0d1508d0a6029572576`. The intake archive lists 112
files under `research/rank7-joint-endframes`. Each installed oid equals the
blob of that path at the pinned base. The decision's reviewed head and
current head are that same commit. The merge commit is
`30f016dd79ee6a23c40d7dab44a9466c148c42dd`.

The ledger row says partially reviewed. The decision disposition is
`partially_reviewed`, the closure is `merged_for_archive_only`, and both
scoped mechanism review and required execution are false. The archive's own
retention record says the blobs are exact and the original head is in the
ancestry. A compare of that head with main was status `ahead`, behind by 0.
The contributor line names the pull request as a source archive.

Blob agreement is source retention. It is not a mechanism review and it does
not admit the author-claimed kappa.

## What was executed

The checker reads the archive, the decision record, the ledger row and the
contributor line, then compares each listed oid with `git rev-parse` at the
pinned base. It does not replay the rank-7 word and it does not close the
pull request.

`scripts/research_baseline.py` needs
`research/community-frontier1094-audit/ASSEMBLY.json`, which this checkout
does not have. The orientation used here is the ledger row for PR 2979.

## Scope and evidence

Original card: `overlap-receipt`, priority revision 6, refined to this one
archive. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the archive, the decisions, the ledger and
the contributor file. No selected frontier file changes.

## Reproduce

From the repository root, CPython 3.12:

```sh
python3.12 -B research/archive-2979-receipt/verify.py
python3.12 -B research/archive-2979-receipt/test_verify.py
python3.12 -B scripts/research_package.py --package research/archive-2979-receipt
```

## Open next questions

These 112 blobs are this archive's disposition. Another pull request would
leave this receipt.

## Credit

The contributor line names aigent-marius (@mdumitrean) for PR 2979. The
archive records that head and the 112 paths.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
