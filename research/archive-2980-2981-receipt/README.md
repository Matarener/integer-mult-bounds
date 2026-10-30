# The 2980/2981 archive keeps its blobs and leaves review open

**Partial. No new exponent.**

The receipt `docs/research/pr-intake-evidence/archives-pr2980-2981.json`
covers two merged pull requests and one shared merge commit,
`86b5e56d4aa0ced955ac7f059eac0c3a5633ca59`.

| PR | Head | Author | Files |
| --- | --- | --- | --- |
| [#2980](https://github.com/CrocSwap/integer-mult-bounds/pull/2980) | `d0aa33af7c20b2ce28ea64d615ff63a164384e4e` | @jwr404 | 7 |
| [#2981](https://github.com/CrocSwap/integer-mult-bounds/pull/2981) | `3d24b92d8ba057b57cb2d480170ec407520e6882` | @petalas | 9 |

All sixteen installed blobs match the tree by git object id, sha256 and
length. Each package directory contains exactly the receipt's paths. Both
decision rows keep `current_head` equal to `reviewed_head`. The closure kind
is `merged_for_archive_only`. Disposition stays `partially_reviewed`.
Mechanism review and required execution stay open. The receipt's own
remaining sentence is the same open review. Its source-retention pass is the
blob statement. This package does not replay the receipt's ancestry claim.

The ledger rows say "partially reviewed" and link
`docs/research/pr-intake-decisions.json`. Those decision records name this
receipt as their verification evidence.

Four predecessor sentences remain in the archived READMEs and are absent
from the receipt and from the two contributor lines:

- `PR2899 emits that callee as a ROOT`
- `PR2809/PR2808 archives`
- `Credit Nick Petalas/PR2920/2909/2896 for the fixed covers and residual geometry,`
- `Chafik Boukhalfa/PR1991`

The contributor file names @jwr404 for #2980 and Nick Petalas (@petalas)
for #2981, each marked source archive.

## What was executed

The checker hashes the receipt, the decisions file, the ledger, the
contributor file and the sixteen archived paths. It does not run either
package verifier and it does not close either pull request.

The selected reproduce command is `make frontier1094-verify`. This checkout
has no `research/community-frontier1094-audit/ASSEMBLY.json`, so
`scripts/research_baseline.py` cannot bind that assembly. The orientation
used here is the two ledger rows.

## Scope and evidence

Original card: `overlap-receipt`, priority revision 6, refined to this
receipt. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the catalogue and the compared files. No
selected frontier file changes.

Upstream checkpoint: `20ecf2891d80b5acf18d980b2164fb44ea7faa90`, priority
revision 6, checked 2026-10-18 06:08 UTC. Catalogue and selected record match
that commit. Handoff discussion #1166, through the PR3562 note at 2026-10-18
05:57 UTC, was published or released work. Draw seed
`1c96b80206e3f5d545684875a27e1d7c`, track `consolidation`, second card
`overlap-receipt`.

## Reproduce

From the repository root, standard-library Python 3.12:

```sh
python3.12 -B research/archive-2980-2981-receipt/verify.py
python3.12 -B research/archive-2980-2981-receipt/test_verify.py
python3.12 -B scripts/research_package.py --package research/archive-2980-2981-receipt
```

The check finishes in a few seconds.

## Open next questions

This receipt's sixteen blobs, two unchanged heads and four README
predecessor sentences are the disposition.

## Credit

#2980 is @jwr404's source archive. #2981 is Nick Petalas's source archive.
The predecessor sentences name PR2899, PR2809, PR2808, PR2920 and PR1991
inside those READMEs.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
