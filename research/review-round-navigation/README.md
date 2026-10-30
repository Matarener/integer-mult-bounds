# Review-round navigation

**Navigation repair. No new κ.** Selected conditional κ stays `0.001672660197076918`.

## Scope and evidence

Original card: `scope-navigation`, scope **refined** to one stale sentence on the status page.

`docs/research/current-status.md` said the latest recorded round was the nineteenth reconciliation, and its table cell said that round's review was still in progress. The linked nineteenth review already records **63 merged; 1 closed as superseded; 36 pending.** Intake packages `research/community-efficient2000-audit` through `research/community-efficient2600-audit` are on this main. Round 2200's heading is "final unbatched remainder"; rounds 2300 through 2600 are recorded after it. None of those seven openings validates a scientific claim or a new κ.

The status page now says the nineteenth reconciliation is the last **prose** row in that table, points at the twenty-sixth intake, and copies the nineteenth review's own count into the table. The seven audit READMEs are not rewritten. There is no `community-efficient2000-review.md` through `community-efficient2600-review.md`, and this package does not invent those prose reviews.

This is not a supplier admission, a ledger rewrite, or a selected-frontier change.

## Reproduce

From the repository root, CPython 3.12:

```sh
python3.12 -B scripts/research_package.py --package research/review-round-navigation
python3 -B -m unittest tests.test_research_current_status
```

Expected marker:

```text
PASS_REVIEW_ROUND_NAVIGATION prose_last=1900 intake_last=2600 counts_1900=63_merged;_1_closed_as_superseded;_36_pending. selected=0.001672660197076918 rounds=7 controls=4 no_new_kappa
```

`verify.py` checks the working status page, the pinned nineteenth review, and the seven pinned intake READMEs. Four controls reject the old "latest recorded round" sentence, an in-progress nineteenth disposition, a changed twenty-sixth heading, and a prose review file for round 2600.

Not run: a selected cold replay, Lean, Docker, or a reread of every later intake row.

## Open next questions

1. **Should the prose table grow a row for each intake from 2000 through 2600?** The count lines are already in the audit READMEs. A new row needs a `community-efficientNNNN-review.md` or an explicit decision that an intake README is the review record. This package does not write those reviews. Blocked until a maintainer chooses that record type.
2. **Does `docs/research/research-archive-intake.md` still send publication state only through the nineteenth dispositions file?** That page names `research/community-efficient1900-audit/DISPOSITIONS.json` as the round-disposition authority. Later rounds have their own disposition files. First step: compare one later `DISPOSITIONS.json` with the ledger row for the same PR. Blocked here because editing that index was outside the one stale status sentence.

## Credit

The nineteenth reconciliation and the status-page structure through round 1900 are the existing review records, including the navigation refresh that stopped at that round. Rounds 2000 through 2600 keep their authors' intake text. The sentence repair and the checker are by unpaidmoon, with substantial Cursor Grok assistance. Apache-2.0. No independent human review is claimed.
