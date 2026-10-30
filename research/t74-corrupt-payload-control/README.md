# The T74 corrupted-word control misses an unchanged payload

**Scoped audit. No new κ.** The selected conditional result stays the record in
`certificates/selected-result.json` (`605457647/200000000000`, decimal
`0.003027288235`). This package does not edit
`research/t74-pivot566-kernel/verify.py` and does not rerun its admission.

## Result

`corrupt()` in that verifier flips one payload byte, recompresses with
`gzip.compress(..., mtime=0)`, and requires the new container digest to equal
the committed pin of `inputs/gauge44-word-566.json.gz`. The bounded hook
counts the control as passed when that assertion fails.

On CPython 3.12 with zlib 1.3 the same recompression of the **unmutated**
payload already misses the pin
`0740b6f33927b9e60c9a7f35e7fcb2fd9ac6e2d3982112428b302a6966a18c73`. The
committed container is 57,411 bytes, header `1f8b0800` with mtime 0 and XFL 2.
Default recompression and levels 1 and 9 all fail to reproduce it. The mutant's
recompression also misses the pin, and it differs from the unmutated
recompression, but the control never reads that difference. Both inputs are
rejected for the same container-digest reason.

Payload equality separates the two:

| Candidate | Container digest equals the pin | Payload equals the committed word |
|---|---|---|
| Committed container | yes | yes |
| `gzip.compress` of the original payload, mtime 0 | no | yes |
| Level-1 recompression, mtime 0 | no | yes |
| One-byte flip at the `corrupt()` index | no | no |

A different compressed byte stream is not a mathematical mismatch. The
immutable container pin stays the identity of the committed file. The
proof-relevant comparison for this control is the decompressed payload.

## Scope

Task card `portable-replay`, priority revision 7, base
`32890bc5de034ab8fc93ac88ead7279a6a416d04`. Scope status is **refined**.

This is item 18 of the ordered eligible list below. It answers the card's
canonical-payload method on one live control. It does not rebuild the
balanced-split archive, does not replace the mtime fixture in
`research/gzip-mtime-payload`, and does not change the selected bit replay
comparison in `research/bit589-gzip-replay`.

Ordered eligible list for session r50. Order: the priority table in
`docs/research/current-priorities.md`, then catalogue cards that are not
already in that table. A row stays while its stated next decision is still
open. Dropped before the cut: work this account already delivered, results
closed on current main, questions covered by an open pull request, and topics
already on a fork `cursor/*` branch. The four 19 October handoffs
(comments 19030045, 19030047, 19030049, 19030053) are dropped on that rule:
the `(w, q, v_N)` consumer, the six-tape L546 bill, and the single-ADD
retiming class are already delivered, and the fresh T385 wrapper is a full
replay outside this session's budget rather than a new catalogue row.

1. `uniform-transfer-audit`
2. `supplier-boundary-audit`
3. `joint-query-controller`
4. `r437-carrier-integration`
5. `p104-side-correction`
6. `independent-moment`
7. `formal-interface-lemma`
8. `bit-helper-contract`
9. `bit-new-register-model`
10. `complex-rank-shape-decoder`
11. `complex-new-helper-inventory`
12. `centre-path-sharing`
13. `coverage-law-change`
14. `connector-alphabet-change`
15. `selected-stock-envelope`
16. `census-pruning-audit`
17. `replay-runtime`
18. This package (`portable-replay`).

`overlap-receipt`, `scope-navigation`, `selected-packing` and
`scalar-to-moment` are later rows. Partial notes on #4100, P104, R437, the
rank-8/u2 slack and the selected stock do not close those cards' stated next
decisions, so the earlier rows stay and this card remains 18.

## Reproduce

From the repository root, CPython 3.12, standard library only:

```sh
python3 scripts/research_package.py --package research/t74-corrupt-payload-control --check-only
python3 -B research/t74-corrupt-payload-control/verify.py
python3 -B scripts/research_package.py --package research/t74-corrupt-payload-control
```

`verify.py` prints

```text
PASS_T74_CORRUPT_PAYLOAD_CONTROL unmutated_recompress_matches_pin=false level1_same_payload=true mutation_changes_payload=true no_new_kappa=true
```

It authenticates the three live inputs, requires the audited `corrupt()`
source text, and checks the table above. Not run: Lean, Docker, the selected
cold replay, and the T74 SymPy admission.

## Open next questions

The successor question is in [TASK.json](TASK.json). Replace `corrupt()` in a
successor of the bounded hook with payload inequality, without treating a
faithful recompression as a corrupted word. The first step is a copy of the
five failure controls that changes only that predicate. The blocker is the
pin of `verify.py` in `PINS.json`; this audit does not rerun the admission
those controls sit inside.

## Credit

The control, the gauge44 word and the committed pin are Marius-Paul
Dumitrean's `research/t74-pivot566-kernel`. The payload-versus-container
convention is `research/gzip-container-reproducibility`. The neighbouring
mtime fixture that left its historical verifier unedited is jwr's
`research/gzip-mtime-payload`. The selected-bit container repair is
`research/bit589-gzip-replay`.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
No independent human review and no formal-kernel acceptance are claimed.
