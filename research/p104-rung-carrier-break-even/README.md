# Break-even price of a carrier for a third frame-593 rung removal

**Scoped negative result in the raw-moment relaxation; no new κ.**

DreamingOfClouds's open [PR #6030](https://github.com/CrocSwap/integer-mult-bounds/pull/6030)
removes helper 470's frame-593 rung, the twin of #5907's helper-468 removal, and
notes that removing helper 469's or 471's rung is exclusive with both "unless a
new carrier of that content is added". This package prices that escape route.

Grant a third removal for free, with exactly #6030's per-LOCAL profile delta
again (paid ranks 1 −2, 2 +1, 3 −2, 4 +1, 6 +1, 7 −1, 8 +1; credited helper ranks
1 −1, 2 +1, 3 −1, 6 +1, 7 −1, 8 +1, each times the 18 LOCAL invocations). Then:

- With a free carrier, the raw crossing would rise from
  (.00312581155791, .00312581155792) to (.00312633419236, .00312633419237),
  a gain of at least 5.2263e-7.
- **One added paid call of any rank 1..145, anywhere in the complete invoice,
  defeats it.** For each of those 145 ranks the edited profile's crossing is
  certified below #6030's lower endpoint. One added rank-1 call alone moves
  #6030's crossing to (.00312167101310, .00312167101311). That loss is at least
  7.92 times the free repeat's gain.
- A carrier inside the local word is paid once per LOCAL. One added paid call
  per LOCAL, of any rank 1..145, also defeats the repeat. One rank-1 call per
  LOCAL moves #6030's crossing to (.00305129298944, .00305129298945).

So a carrier is useful only if its paid cost is zero, or if it also earns
productive target credit or enables further savings worth more than one paid call.
A twin-sized rung removal cannot fund a single extra paid Gaussian call.

## Claim type and scope

This is a **finite certificate** about hypothetical profile edits in the raw
moment model `Σ_r T_r r^(1-k) − Σ_r P_r r^(1-k)` that #5827/#5907/#6030 bisect. It
is not a word, not a construction, and not a complete multiplication theorem.
The free third removal is a hypothesis: no rung removal for helpers 469 or 471
is constructed, and its true delta may differ. The tail ratios, compiler and outer
checks that a complete bill also needs are not evaluated. They only add
conditions, so they cannot rescue an edit that already fails the raw crossing.
The analysis does not cover a carrier that also adds productive targets.

The profile is copied as a literal from #6030's `RESULT.json` at head
`772dd10a5859a1d15f4851feb371519789213ad8`
(`research/p104-helper470-twin-rung-removal/RESULT.json`, SHA256
`84fcbe2a0b64307b5703c363408042bdd91555b0419509aa50daa43b3b1924ad`), whose
`complete_cost.targets` and `complete_cost.paid` it reproduces. That PR head is
not on main, so it cannot be a Git pin here. As positive controls, the
verifier reproduces #6030's published crossing enclosure and, after removing
the stated delta once, #5907's enclosure (.00312528909884, .00312528909885). It
also checks the published counts: 13,444 targets, 66,834 paid calls, rank surplus 760.
These are consistency checks of this package's pricing, not a review of either PR.

Signs are certified with Python's correctly rounded `Decimal` `ln`/`exp` at 60
digits and an explicit relative error allowance of 10^-50 per moment. Every
checked sign must clear that allowance. Three damaged profiles must be rejected.

## Reproduce

From the repository root, with CPython 3.12 and the standard library:

```sh
python3.12 -B research/p104-rung-carrier-break-even/verify.py
python3.12 -B scripts/research_package.py --package research/p104-rung-carrier-break-even
```

Expected last line: `PASS_P104_RUNG_CARRIER_BREAK_EVEN`. It runs in about one
second. `--write` regenerates `RESULT.json`.

## Open next questions

- Can a carrier for the content of sources 703/704 be a productive helper itself,
  so its target credit offsets its paid call? This matters because that is the
  only escape this package leaves. First step: name the helper rank and the
  frame at which helper 469 or 471 would read it. Then price target plus
  paid deltas with this verifier's `edit`/`crossing` before building a word.
- Is there an existing paid call in #6030's word whose content could carry 703
  or 704 to frame 593 without adding a call? This would be a zero-cost carrier.
  First step: list the helpers live at frame 593 that read 703 or 704. Blocker:
  this package does not parse the word.

## Credit

Produced by Nick Petalas. The rung removals and the profile are by
DreamingOfClouds (#6030, #5907). They edit Ali Romman's #5827 word and its lineage
back to #5565, whose credit is retained in those packages. The raw moment
crossing follows the pricing of that line. Apache-2.0.
