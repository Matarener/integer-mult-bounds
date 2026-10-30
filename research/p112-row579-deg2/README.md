# Row 579 [7^8,4,4,4,3]: DEG2 (conjecture C6), the last open row of the one-sided ledger

No kappa claim, no window, no supplier word.  Pure finite combinatorics on the E8 root lines, a follow-up to #3154 (`research/p112-reduction-to-conjectures`, commit 708f0ad89), in the line of #2832, #2985, #3049, #3074.

## What this package contains
- **Ledger:** `data/ledger4_consolidated.csv` = #3154's `ledger3_consolidated.csv` with row 579 changed from CONDITIONAL(C6=DEG2) to KILLED: **603/603 KILLED** (recomputed by `verify.sh`). The row-579 kill is unconditional within the stated assumptions (Lemma F / mask model; both DEG2 implementations give six-sets = 0).
- **Row 579 chain:** Theorem K5 (K579T: no five sevens with an A4 pair pattern have |U| <= 28; impl A `base.py/a3e.c/cover.py/ext.py`, impl B `b5.c`); Lemmas K5^- and K5^-2 (R579b: five sevens with exactly one, or exactly two vertex-sharing, non-root pairs die; impl A `km_a.py/km_a2.py`, impl B `b5m.c/b5m2.c`) give at least 6 non-root pairs among the 28; the list of possible non-root types (`types.c`: D7 14, E6A1 23, E6 24, A7 25, D6 26, every other support >= 31, regenerated; `AUD-2/pairmin.c`, the independent minimum-leftover check over all pairs of 7-flats); **DEG2** (no seven carries two non-root pair directions) makes the non-root graph a matching, e_N <= 4 < 6, contradiction.
- **DEG2 closure** (`MODEL.md` = written proof that the mask model is a sound relaxation of Lemma F): impl A `checks/DEG2A` (`quad.c`, `ext.c`, `geomN.py`; 4-seven survivors only for La-orbit reps 1 and 8 (3464 / 3105), 5-seven sets 2448 / 3672, **six-sets 0**; all 10 reps, in chunks) and impl C `checks/DEG2C` (`d2fix.c`, the FIXED oracle; an oracle bug in the first impl C was found and fixed, see `MODEL.md`).
- `PROOF_MAP.md` (claim -> check), `checks/<CARD>/NOTES.md`, `MANIFEST.sha256`.

## Impl C rerun (former slot, now filled)
**impl C fixed rerun: six-set count 0 over 64 rc=0 shards covering every (h_ab type, L_0-orbit-rep shard) exactly once; controls found configurations at K=3 and K=4; oracle 400/400 vs impl A.** Details: `checks/DEG2C/coverage.py` (coverage table; K=6, MODE 0, the 5 types D7/A7/E6A1/E6/D6; 33 shards at NS=8, 27 at NS=32, 4 at NS=128; 10 timed-out or killed outputs are listed and not used, their residues are tiled by finer shards), `checks/DEG2C/run_d2fix.sh` (controls; FULL rerun of all 64 shards), oracle validation in `checks/DEG2C/NOTES.md` (VERIFY section: `d2fix` vs impl A's cover oracle on 200 planted + 200 perturbed sets, agreement 400/400; the old scalar-flag oracle disagrees on 79/400).

## Credit and what this completes
- conorholds' #3166 closed C7 (the d = 0 sliver). With C6 (this package) the whole one-sided case K2 (L120 suffices, via #3074) is complete: the ledger is 603/603 KILLED.
- C5 (two-sided FINITE beta R = 7, p = 4) is not touched here; petalas's C5 work (#3158 to #3185) is progress on it. The two-sided case K1 still depends on C1-C5.

## How to check
`PYTHON=/path/to/python3 bash verify.sh [outdir]` (Python >= 3.11 with numpy, cc).  Default run: manifest, ledger recomputation, K579T impl A -> R579b chain, K579T impl B, types.c, DEG2 impl A (five-set and six-set stages from the recorded 4-seven survivors, plus one quad-stage chunk per surviving rep), a few minutes, <= 3 processes, each process under `timeout 1200`.  `FULL=1 bash verify.sh` adds `checks/full.sh`: pairmin (all non-root types), all quad-stage chunks of all 10 reps against the recorded DONE lines, and the impl C controls (the DEG2 impl C jobs are run with `checks/DEG2C/run_d2fix.sh WORKDIR deg2`, shards of <= 1150 s).

## Honesty box
- DEG2 as a relaxation is a *mask-level* statement (necessary conditions only), so zero is a valid kill and a positive count would only be an upper bound.
- Impl A's reps 2 and 4 quad stage (12 chunks each, 0 survivors) were produced in this package's preparation run (`checks/DEG2A/rec/R2_*`, `R4_*`) because the earlier records for those reps were not kept; reps 0, 3, 5, 6, 7, 9 are from the earlier recorded runs; all are rerun by `FULL=1`.
- The K579T impl A harness fixes of #3154 (SIZEONLY=1; multiset comparison of slices because rep ids depend on mask order) are used.
- The DP/LP and other inputs of #3154 are unchanged; this package re-proves nothing of #3154 except the row-579 chain.
