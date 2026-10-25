# Single-hub two-bearing charge

Scoped answer to the open question in
[discussion #1166, comment 19021149](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19021149):
does the two-bearing-query mechanism from the PR3583/PR3698 literal
actual-reader model appear in a factorization of the exceptional single-hub
star of PR3573, where a hub-dependent transfer still works?

**Result.** Yes, on exactly four of the twenty extremal rows. The relaxed
row model has minimum charge **48** against baseline **40**. The excess of
**8** is the four reader rows `E dxy`, `E gtxy`, `F dxy` and `F gtxy`, each
forced to cost 2. The other sixteen rows attain cost 1. PR3573's GF4 map
still preserves all 128 oriented subset implications, so this is not a
transfer obstruction. No new κ. Selected κ stays `0.001672660197076918`.

The coordinate-functional count is larger than this minimum: `dthx` and
`dthy` contain three mark-bearing queries, but a non-coordinate evaluator
sees only `d` and pays 1. The mechanism that survives the PR3698 relaxation
is the pairing on `dxy` and `gtxy`, not every mark-bearing pair.

## Evidence

`PROOF.md` contains the pairing argument. `verify.py` rederives the extremal
table from the six columns, searches the row model, checks the witness, and
replays the GF4 map. `independent.py` does not import it: minors and Cramer's
rule replace row reduction, and GF4 is `{0,1,2,3}`. `test_controls.py`
rejects a broken `dxy` reader, a substituted `y` image, and the collapse of
the strict `dthx` count onto the relaxed cost.

One attaining per-query split in `WITNESS.json`, for `g,d,t,h,x,y`, is
`[0, 20, 4, 8, 6, 10]`. The total 48 is the minimum. That split is not
claimed to be the only one.

## Reproduction

From the repository root, Python 3.12:

```sh
python3.12 -B scripts/research_package.py --package research/p112-single-hub-two-bearing
```

Direct checks:

```sh
python3 -B research/p112-single-hub-two-bearing/verify.py
python3 -B research/p112-single-hub-two-bearing/independent.py
python3 -B research/p112-single-hub-two-bearing/test_controls.py
```

Expected tokens: `PASS_SINGLE_HUB_TWO_BEARING`,
`PASS_SINGLE_HUB_TWO_BEARING_INDEPENDENT`,
`PASS_SINGLE_HUB_TWO_BEARING_CONTROLS`. Local runs finished in well under
a second each. Not run: Lean, Docker, a selected cold replay, and hosted CI.

## Scope

Task `uniform-transfer-audit`, scope **changed**. The card asks for one
all-size, compiler, precision, hosting or restoration implication. This
session takes the explicit single-hub handoff instead of redrawing a card.
The finite charge is the missing comparison with the two-hub excess of 12.
It does not admit a supplier.

Base `bb4bccbf42844d2801487450727c2f63e10d1d0f`, priority revision 6.
The PR3573 and PR3698 heads are on `petalas/integer-mult-bounds` and are not
objects of this repository, so the six columns are restated from PR3573's
published star and rederived here. Overlap at 2026-10-20T02:23Z covered 814
open PR bodies and 2642 discussion records. The single-hub factorization was
still the open question in comment 19021149. PR #4113 quotes that question
and reviews a different tensor-pairing bound.

## Credit

The star, the extremal table and the GF4 map are Nick Petalas's PR3573.
The row model, the charge, and the two-bearing mechanism are Nick Petalas's
PR3583 and PR3698. That chain retains Philippe Van Velzen's expanded
identity, ctoth's coverage question and the actual-reader lineage. New
enumeration and pairing by unpaidmoon, with substantial AI assistance
(Cursor Grok). No independent human or proof-kernel review is claimed.

## Open next questions

1. Does one further independent hub add two-bearing rows beyond `dxy` and
   `gtxy`, or repeat the twelve-unit `K3,2` excess? The first step is to
   write the third hub's queries the way PR3583 added `k,z,w` and rerun this
   row model on the new extremal table. Blocked by the absence of a
   charge-transfer lemma: PR3591 moves support obstructions, not this charge.
2. Can the working GF4 map be lifted to a characteristic-zero literal
   factorization whose charge is strictly below 48? The first step is one
   explicit portwise lift, or a proof that every lift pays at least 48.
   Blocked by the gap between a support transfer and an evaluated Gram
   factorization. A failed lift would not by itself raise the pair floor.
