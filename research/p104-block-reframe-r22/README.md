# One block moved from a dim-8 chart to a new dim-4 chart on PR5713's P104 word: conditional kappa .00310927386

Complete conditional kappa **.00310927386** (claim line, tested at .003109273865). The exact raw crossing is in
(0.00310927387521, 0.00310927387522). That is **+1.216e-7** over the raw crossing 0.0031091522456 of
[PR5713](https://github.com/CrocSwap/integer-mult-bounds/pull/5713) (Ali Romman, claim .00310915222), the newest
P104 head when this was written.

**Conditional on** exactly the assumptions of PR5713 and its inherited P104 line, including free helper endpoints
(PR5561, audited in PR5567). This word changes one helper start and one helper final. The selected record is not changed.
No independent human or proof-kernel acceptance is claimed.

## What changes

The change is a large-neighbourhood step of R22's exact reorder+re-frame MIP. All scalar operations outside one
window of about 1,000 consecutive operations are pinned. Inside the window, every chart within dimension gap 4 of
the operation's bounds is allowed. One window of the sweep over PR5684's word found this step. It applies unchanged
to PR5713's word, because PR5713 only edits contacts elsewhere.

- 96 scalar operations on registers 41, 42, 106, 400, 401, 403, 405, 410 and 741 used to run on chart 477
  (dim 8). In the new word:
  - 88 of them run on a new chart 1090 = span[265, 194, 164, 75] (dim 4);
  - 8 of them run on chart 127 (dim 9).
- Helper 741 now starts on 1090 instead of 477.
- Helper 405 now ends on 1090 instead of 477.
- No scalar instruction, coefficient, order, owned lifetime, main endpoint or port changes.

Per local call: paid MOVE jobs H1 +1, H4 +1, H5 -1 (66348 -> 66366 paid calls in all); helper credits
H1 -1, H4 +1, H5 +1, H8 -1. The moment gain comes from the helper credits. The rank-mass surplus is unchanged at 760,
and there are still 12958 productive fields.

## Check

```
python3 -W error -B research/p104-block-reframe-r22/verify.py          # compares with RESULT.json
python3 -W error -B research/p104-block-reframe-r22/verify.py --write  # regenerates RESULT.json
```

`verify.py` runs these checks:

1. **Source pin.** It pins PR5713's `WORD.json.gz` (SHA256).
2. **Regeneration.** It regenerates `WORD.json.gz` from that word with `construct.py` and `EDITS.json`. Each hunk
   replaces one unique event run, and hunks are disjoint. It also appends one chart and changes two helper endpoints.
3. **Boundary.** Existing charts are unchanged, only free helper endpoints change, and every other word field is
   unchanged.
4. **Order.** The scalar order is trace-equivalent: every dependent pair keeps its order.
5. **PR5713's own stack.** It runs PR5713's unmodified stack through its three nested source exports:
   - exact replay;
   - every dense transpose column;
   - every native map and phase;
   - the complete physical caller;
   - PR5713's `pricing.py`, where only the four literals in `LITERALS` change: claim/tested kappa, previous claim
     and the paid-call total.
6. **Controls.** Six controls are rejected:
   - old helper start;
   - block op on the old chart;
   - missing block MOVE;
   - unpaid query;
   - extra target credit;
   - read swapped after a dependent write.

## Attribution

All retained checkers, words and pricing are by the PR5713 authors and their sources; see `NOTICE`.
PR5713 itself builds on our PR5684. R22 search tools are on branch `r22-p104-reframe-optimum`. The
large-neighbourhood windows are set with `WIN=lo:hi` in `poset104.domains`.

Joel Pulikkan (GamingPuzzled) with Claude Opus 5.5 (Anthropic) via Claude Code. Apache-2.0.
