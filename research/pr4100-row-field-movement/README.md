# Boundary-arithmetic row-field movement

**Scoped layout lemma. No new κ.** The selected conditional result stays
`0.001672660197076918`. This does not accept #4100.

## Scope and evidence

Card `uniform-transfer-audit`, refined to one caller. #4100's Gaussian text
says the one exposed polynomial row field is padded by a factor below two,
moved at `O(log p)` times the boundary volume, and removed before the next
axis, so the pad does not accumulate as `2^g`. The same movement is
PHASE-LAYOUT's short-field transpose, and UNION-SCHEDULE step 5 charges it
to the boundary-algebra row rather than to the union head travel. PR #4327
audits that head travel and leaves this batching row open.

[PROOF.md](PROOF.md) proves, for every positive integer size in the
hypotheses:

- `M(a) = 2^{ceil(log2 a)}` satisfies `a ≤ M(a) < 2a`.
- When the right-hand-side count is at least the batch width `W`, those
  right-hand sides partition into batches in `[W, 2W]` with no added cells.
  A shorter final batch adds fewer than `W` cells, not `O(1)` record moves.
- The lockstep transpose of the padded field uses `ceil(log2 a)` stages and
  two passes per stage. Forward movement is exactly `2 · ceil(log2 a) · M(a) · N`,
  which is strictly less than `4 · ceil(log2 a)` times the real boundary
  volume when `a ≥ 2`. The stage count does not depend on the spectator length.
- Deleting the pad before the next axis keeps every axis multiplier below two
  and returns the final multiplier to one. Retaining a length-3 pad on each
  axis multiplies the volume by `(4/3)^g`.

`verify.py` recomputes the padding inequality for `a = 1..65536`, the batch
partition for `W = 1..64` and `R = 0..512`, and the schedule on twelve shapes.
The worst executed forward ratio is `2048/144`. A three-axis tensor of length
`3` peaks at `36` records and returns to `27`. Two rejection controls fail
closed: a pad of length `3` is not `8`, and six retained length-3 pads are
not a factor below two.

The Strassen count, the carving that produces `O(V d W^{τ-1}/B)`, conditioning,
and the #4100 ledger remain inherited. #4100 names both `τ = 45/16` and
`τ_eff = 2 + 10^{-64}`; this lemma does not choose between them.

## Reproduce

From the repository root, on CPython 3.12:

```sh
python3.12 -B scripts/research_package.py --package research/pr4100-row-field-movement --check-only
python3.12 -B scripts/research_package.py --package research/pr4100-row-field-movement
```

The registered command is `verify.py`. It uses the standard library and reads
the three pinned prose inputs. Expected first line:

```text
PASS_ROW_FIELD_MOVEMENT padding_strictly_below_two=true zero_added_cells_when_R_ge_W=true small_batch_added_cells_lt_W=true forward_passes_per_stage=2 max_forward_moves_over_real_volume=2048/144 stage_count_depends_only_on_row_length=true removal_peak_below_two=true retained_three_length_g6=(4/3)^6>2 page_scans_equal_batch_count=true no_new_kappa=true
```

## Open next questions

1. **Carry the move count into the ledger term.** The layout bound is
   `O(log a)` times the boundary volume. It becomes #4100's
   `O(V d W^{τ-1}/B)` only after the exposed length is identified with the
   carving parameters `W` and `B`. First pin `|E_i|` and `μ` at the #4100
   balance and substitute Lemma 3. Blocked here because the carving program
   is not replayed.
2. **Fix the boundary exponent.** GAUSSIAN.md uses `τ = 45/16` for the
   seven-product paragraph, while UNION-SCHEDULE section 4 uses
   `τ_eff = 2 + 10^{-64}`. The movement lemma can be copied into the ledger
   only after one of those is the stated exponent. First compare those two
   sentences with the generated ledger at head
   `337d04939571a637aeab54a0f58f54fde811663a`. Blocked here because that
   ledger is a different program, and PR #1731's rectangular exponent is a
   different caller.

## Credit

The layout sentences are from the capped phase-cell audit (Vlado Vojdanovski,
PR #1673, and the contributors named there) and from Cinna Davis's #4100
Gaussian and union-schedule text. PR #4327 (Ryanson Jonathan) audited the
union head travel and marked this batching row as separate. PR #1731's
review (the rectangular exponent and the operator identity) says partial-batch
padding is negligible and is not this level count.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
No independent human review and no formal-kernel acceptance are claimed.
