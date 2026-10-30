# Retention of the eight selected-frontier source pulls

**Overlap receipt. No new κ and no ledger edit.** The selected conditional
exponent stays `605457647/200000000000`.

## Result

On main `32890bc5de034ab8fc93ac88ead7279a6a416d04`, the first eight entries of
`certificates/selected-result.json` `source_prs` are 5413, 5414, 5402, 5407,
5398, 5400, 4610 and 5241. Each recorded head is an ancestor of that main.
Every `research/` path named in those ledger rows is present at the pull-request
head and byte-identical there and on this main.

The selected execution closure is a different object from that archive
retention. `certificates/frontier5413-source.json` lists 1,245 paths. All
1,245 hashes match the files on this main. Its three package roots are the
incorporated pulls 5407, 5413 and 5414. The trees of 5398, 5400 and 5402 are
not in that closure.

| PR | Ledger disposition | Research tree vs its head | Selected-record role |
|---|---|---|---|
| 5413 | incorporated | identical | audited source head of the selected certificate |
| 5414 | incorporated | identical | `audit_pr` / `audit_head` |
| 5407 | incorporated | identical | one of the three closure roots |
| 5402 | partially reviewed | identical | named source; no autonomous credit for the eight coupled outputs |
| 5398 | partially reviewed | identical | named source; author evidence not replayed in the ledger row |
| 5400 | partially reviewed | identical | named source; same unresolved archival sentence as 5398 |
| 4610 | incorporated | identical | previous frontier; `selected-result.json` has since changed |
| 5241 | incorporated | identical | previous admission; same certificate change |

5398 and 5400 still say that archival publication does not admit a supplier,
an outer theorem, or an improved κ. The promotion text for 5413 says the final
`+5×10^-12` over #5398/#5400 is compiler/outer headroom of the selected
exponent, not a new recursive-price saving. Both sentences are in the pinned
files. This receipt does not choose between them and does not mark either row
incorporated.

4610 and 5241 also name `certificates/selected-result.json`, which differs from
both heads, and `docs/research/pr-intake-evidence/pr4610/PROOF-REVIEW.md`, which
is absent at both heads and present now. Those two paths are successor records.
They are not edits of the retained research trees. Every one of the eight
GitHub closures is `merged_for_archive_only`.

## Scope

Task card `overlap-receipt`, priority revision 7, base
`32890bc5de034ab8fc93ac88ead7279a6a416d04`. Scope status is **refined**.

The card asks what content and credit of one small named set has been retained.
The set is the selected certificate's eight-pull prefix. Scope stays inside
disposition, byte identity and the published credit sentences.

Ordered eligible list for session r38, rebuilt on 2026-10-25 against that
main. Open handoffs from the 19 October index come first. A closed smallest
task is dropped; a distinct remainder stays. Priority-table rows whose stated
next decision is still open come next. Catalogue cards that are not already
those rows follow, skipping cards the 23 October rebuild had already dropped
and rows closed on this main or covered by an open pull request.

1. A caller that accepts `(w, q, v_N)` without restoring the original source
   slots (comment 19030045; open question 1 of
   `research/p104-role-exchange-caller-audit`).
2. The cost of placing L561 on the four scratch windows before
   `L546 -= L561` (comment 19030049; open question 1 of
   `research/qq16-l546-head-move`). The head-move bill itself is on main.
3. `BIT.md` weighted leaves and fast header routes at the new `c`
   (`uniform-transfer-audit`). The `2^{-4p}` sentence, the row-field pad, the
   uniform evaluator and the continuation-stack bound are already delivered.
4. The fixed-tape visit count of one blank-return of the 9,475-row R437
   parent (`r437-carrier-integration`; open question 1 of
   `research/r437-parent-spectator-blank`).
5. `coverage-law-change` on the current selected construction. The older
   #1094 screens are not a constraint on this selection.
6. This package.

Dropped before the cut: the T385 wrapper, closed by
`research/t385-r437-copy-audit`; the retiming handoff; the four-provider
rebind, on main in `research/mixed-provider-admission`; the matched
park/restore bill, covered by open #4167; the #4091 equivalence, on main in
`research/fourth-entry-ceiling-transfer` and #5280; `p104-side-correction` as
its own row, because item 1 is that consumer; and the catalogue cards dropped
in `research/rank8-u2-entrance-obstruction` (`formal-interface-lemma`,
`bit-helper-contract`, `bit-new-register-model`,
`complex-rank-shape-decoder`, `centre-path-sharing`,
`connector-alphabet-change`, and the stock, census, replay, packing and
scalar-itinerary cards). Work already delivered by this account is excluded,
including every pull through #5281 and the fork `cursor/*` branches named in
the session note.

## Reproduce

Python 3.12, standard library only, from the repository root. The eight
recorded heads must be present in the local Git object store.

```sh
python3 -B research/frontier-source-retention/verify.py
python3 -B scripts/research_package.py --package research/frontier-source-retention
```

Expected line:

```text
PASS_FRONTIER_SOURCE_RETENTION prs=8 identical_paths=26 manifest_files=1245 partial_but_named=5398,5400,5402 certificate_moved_after=4610,5241 no_ledger_edit=true no_new_kappa=true
```

The checker hashes all 1,245 manifest paths, compares each integration path
with `git diff` under `GIT_NO_REPLACE_OBJECTS=1`, and rejects a forged
`incorporated` label on 5398 and a one-path manifest mismatch. Not run: the
frontier replay, Lean, Docker, and any edit of `docs/research/pr-ledger.json`.

## Open next questions

1. Should a maintainer leave the 5398 and 5400 rows partially reviewed, given
   that their unresolved sentence still denies an improved κ, while the
   selected promotion uses them as the base of a `5×10^-12` headroom term?
   The first step is to quote those two sentences together. This package
   cannot edit the ledger.
2. Which fields of `certificates/selected-result.json` changed after the 4610
   head `20bb93cd990d2ff683e4d0fc56b87a42cd5d3296`? The receipt only shows that
   the file differs. The first step is a key-wise diff. The blocker is that
   this checker does not interpret the successor certificate.

## Credit

The ledger rows, the promotion note and the contributor map are the
maintainer intake records for Chris R / Clear1nsight (#5398, #5400, #5407,
#5413, #5414, #5241), Dillon Amburgey / dillona (#5402) and Cao Yifan /
intqwq (#4610), with the lineages those records already name. This package
does not replay their mathematics.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
No independent human review and no formal-kernel acceptance are claimed.
