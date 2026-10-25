# Third-hub extremal charge

Scoped answer to the second question in
[discussion #1166, comment 19021149](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19021149):
after the single-hub two-bearing charge, does one further hub add two-bearing
rows beyond `dxy` and `gtxy`, or repeat the twelve-unit `K3,2` excess?

**Result.** On the complete extremal table, a third hub does add crossed
two-bearing rows, and it does not repeat the twelve-unit excess. In the relaxed
literal actual-reader model the minimum charges are 48, 128 and 256 at one, two
and three hubs. The excesses over the one-unit baseline are 8, 24 and 48, which
is \(4h(h+1)\) for \(h \le 3\). The same families force excess at least
\(4h(h+1)\) for every larger \(h\). No new \(\kappa\). Selected \(\kappa\) stays
`0.001672660197076918`.

At three hubs the table has 104 rows. Twenty-four of them cost 2. Twelve of
those twenty-four are five-query readers that each use two hubs. The twelve-unit
figure remains the minimum of the different 21-premise `K3,2` certificate, which
this package recomputes as charge 54.

## Evidence

`PROOF.md` gives the pairing for the three families and the determinant that
makes each crossed five-query set a minimal reader. `verify.py` enumerates the
extremal table by rational row reduction. `independent.py` repeats that census
with integer cross-multiplication and does not import `verify.py`.
`test_controls.py` checks that the two ranks agree on every two-hub mask, that
the one-hub triple is minimal of cost 2, that the full two-hub charge 128 is not
the 21-premise charge 54, that dropping one forced third-hub row breaks the
census, and that the two minors in `PROOF.md` equal \(-2\).

## Reproduction

From the repository root, Python 3.12:

```sh
python3.12 -B scripts/research_package.py --package research/p112-third-hub-extremal
```

Direct checks:

```sh
python3.12 -B research/p112-third-hub-extremal/verify.py
python3.12 -B research/p112-third-hub-extremal/independent.py
python3.12 -B research/p112-third-hub-extremal/test_controls.py
```

Expected tokens: `PASS_THIRD_HUB_EXTREMAL`,
`PASS_THIRD_HUB_EXTREMAL_INDEPENDENT`,
`PASS_THIRD_HUB_EXTREMAL_CONTROLS`. Local runs finished in a few seconds each.
Not run: Lean, Docker, a selected cold replay, hosted CI, and the \(h=4\) census.

## Scope

Task `uniform-transfer-audit`, scope **changed**. The card asks for one
all-size, compiler, precision, hosting or restoration implication. The live
handoff instead asks whether the two-bearing mechanism of the single-hub star
persists after another hub is added. This package takes that second question.
It does not reprove the one-hub minimum as its result; the charge 48 appears
only as the \(h=1\) case of the same census.

Base `bb4bccbf42844d2801487450727c2f63e10d1d0f`, priority revision 6.
Open PR #4124 answers the first question in the same comment, the one-hub
charge. This package does not import it. Open PR #3698 is the 21-premise
two-hub minimum of 54, recomputed here as a control and not replaced.
The ordered eligible-handoff list for this session is in the pull-request body.

## Credit

The one-hub star and its extremal table are Nick Petalas's PR3573. The second
hub and the 21-premise certificate are Nick Petalas's PR3583. The relaxed row
model and the charge 54 are Nick Petalas's PR3698. That chain retains Philippe
Van Velzen's expanded identity, ctoth's coverage question and the actual-reader
lineage. The third-hub census and the excess count are by unpaidmoon, with
substantial AI assistance (Cursor Grok 4.7). No independent human or
proof-kernel review is claimed.

## Open next questions

1. Does the excess stay equal to \(4h(h+1)\) for every hub count, rather than
   only through three hubs? The inequality is already proved for every \(h\).
   Equality needs the extremal table. The first step is the same subset census
   at \(h=4\), where there are \(2^{15}\) query masks. Nothing mathematical
   blocks that pass; this session stops at the third hub named in the handoff.
2. Does any three-hub extremal row survive a characteristic-two support
   transfer? The first step is to test PR3573's GF4 shape on one crossed
   five-query reader. It is blocked as a charge statement because PR3591 moves
   support obstructions, not this row cost, and a failed transfer would not by
   itself raise the pair floor.
