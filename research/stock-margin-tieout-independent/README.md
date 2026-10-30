# Independent replay of the PR #2972 stopped-range margin table (no new kappa)

An independently implemented check of the fourteen-stage bootstrap receipt's
cutoff-pair arithmetic published in [PR #2972](https://github.com/CrocSwap/integer-mult-bounds/pull/2972)
(`research/stock-margin-chain`). The replay uses a separate integer-arithmetic
path — its own exact-rational parser and floor division, no `fractions` module
and no import of the audited package's code — and recomputes all 24 published
integers (12 margins `floor(s*L_j - L_{j-1})` and 12 routing rooms
`floor((1-s)*L_{j-1})`) for both recorded branches from the frozen receipt
`research/selected-bootstrap-stock-audit/RESULT.json`, SHA-256-pinned to
`f0bd4f2270826de7b935323e9b4d2e034f69b46205be9535488c4429e95f7917`
(the same bytes #2972 audits).

```sh
python3 -B research/stock-margin-tieout-independent/verify.py
```

Expected (one line):

```text
PASS_STOCK_MARGIN_TIEOUT published_pairs_checked=24 published_controls=2 min_margin_native=2851485324488315 margin_ordering=strictly_increasing_both_branches room_ordering=strictly_increasing_both_branches conservative_dominates_native=all_12_values common_saving_tieout=exact_both_branches floor_split_residual_ones=7/12 s_sensitivity=stable_at_1_unit_moves_at_1e10_units(stage6,7) headroom_minimum={bootstrap:6562783, conservative_bootstrap:6562783} guard=17 null_coefficient_stages=14/14 coefficient=unresolved
```

Python 3.10+. The only input is the pinned receipt. The replay of #2972's own
verifier (`python3 -B research/stock-margin-chain/verify.py`) passes on the
same bytes and reproduces the same table; this package does not reuse its code.

## What this adds beyond #2972

1. **Independence.** #2972 is an author-checked source archive (priority
   revision 6). This package reproduces its entire published table through a
   different implementation path, supplying the independent-arithmetic coverage
   that the archive status did not claim.
2. **Structural facts not asserted by #2972** (all measured on the pinned
   receipt): margins and routing rooms strictly increase across stages
   `j = 2..7` in both branches; the conservative branch strictly exceeds the
   native branch at all twelve values; the floor-split residual
   `r_j = floor(s*(L_j - L_{j-1})) - (margin_j + room_j)` equals 1 at 7 of
   12 stages (the universally valid range is `{0,1}`); the recorded
   `stock_headroom_log2` is strictly increasing per stage with minimum
   `6562783` in both branches, and the guard
   `ceil(log2(8*8194)) = 17` (recomputed by integer search, not floats)
   covers that minimum.
3. **A receipt tie-out.** `common_saving` equals `1 - gaps/stock` exactly
   (as an unreduced rational) in both branches. #2972 reads only
   `gaps/stock`; the earlier stock audit (#2931) enforces this only through
   full regeneration from its producer sources. Here it is verified directly on
   the frozen bytes, strengthening the binding between the receipt's headline
   saving field and the gap that drives the margin chain.
4. **A sensitivity envelope.** Shifting the saving numerator by one
   denominator unit (relative ~2.5e-47) leaves all twelve native margins
   unchanged; a shift of 10^10 units moves exactly the stage-6 and stage-7
   margins (+6,864 and +2,444,877,300). The published integers pin the
   branch saving only to the floor granularity of the receipt, so the exact
   rational, not the printed table, is the right object to bind.

Controls (all rejected as required): a stale-cutoff substitution (stage 7 :=
stage 6), a one-unit perturbation of one stage's stock gap (breaks the
uniformity requirement), a cross-branch saving swap, plus the two positive
published native integers reproduced independently of the table loop.

## What this does not establish

- It does not choose a stock coefficient: all fourteen
  `actual_stock_coefficient` fields remain null (counted: 14/14), exactly as
  #2972 states. No reserve recurrence or routing-width source sentence is
  supplied.
- It is arithmetic on a recorded receipt, not a producer replay: the cutoffs
  are not re-derived from the frozen PR1087 assembler, and the complex `m=73`
  supplier is untouched.
- No kappa, supplier, tariff, certificate, frozen-input or selected-frontier
  change. The selected conditional result remains kappa =
  0.001672660197076918.

## Sources and reproduction

- Input: `research/selected-bootstrap-stock-audit/RESULT.json` (bytes as
  above; this file is the audited revision retained on main).
- Audited predecessor: `research/stock-margin-chain/` (PR #2972, author
  Kumagi @kumagi; its README table supplies the 24 cross-check integers).
- Replay command: the `python3 -B` line above; expect the single
  `PASS_STOCK_MARGIN_TIEOUT` line. Interpreter used: CPython 3.12.
- Cross-evidence: the predecessor's own `verify.py` passes on the same bytes.

## Open next questions

- Which source sentence bounds the width of a stage-j routing call to the
  previous stopped algorithm (the `c_R` bound #2972 names as missing)? Without
  it the stock coefficient stays unresolved even though every cutoff pair lands
  in the previous stopped range. First step: match the retained PR185/PR387
  cover-row text against the smallest routing room 4777557234646 (native).
- Does the conservative-exceeds-native ordering at all twelve published values
  have a structural explanation (larger branch saving at near-equal cutoffs),
  and would it predict signs for a complex-supplier per-stage sequence if one
  were ever recorded? The measured ordering here is finite evidence for the two
  recorded BIT branches only.

## Credit

Predecessor attribution follows PR #2972 and the retained stock-audit lineage.
Produced by Nick Petalas with AI assistance. Independent human and formal
proof-kernel review are unclaimed.
