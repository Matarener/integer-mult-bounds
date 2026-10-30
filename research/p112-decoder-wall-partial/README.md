# P112 decoder wall: what is proved, and the exact open part

**Result (mixed: PROVED / EXACT / CHECKED, with CONDITIONAL parts marked).** For the masked P112 decoder model
(`Σ_k p_k q_kᵀ = I` on every orthogonal-or-equal pair of the 112 P112 lines, any supports, any field of characteristic 0,
cost = Σ `rank_F2 Bd[supp p_k, supp q_k]`), no decoder of cost ≤ 63 exists in the following classes. The coordinate decoder
(8 terms, cost 64) shows the bound 64 is tight wherever it is stated. No new κ.

| | Class | Tag | Replay |
|---|---|---|---|
| (a) | **FULLWALL.** Every decoder with `m ≤ 8` rank-1 terms costs ≥ 64 | PROVED + EXACT (two enumeration codes, independent C count of the orbit census) | `fw` |
| (b) | **INT-M8 / MIX-8.** Rectangles plus Ferrers atoms with `≤ 8` level pieces: no genuine atom, so ≥ 64. Any decoder with a genuine atom has `≥ 9` pieces | PROVED mod CHECKED (kissat UNSAT + drat-trim, two independent generators for the tie step) | `im8` |
| (c) | **CORE3 + CORE-RES.** Nine terms with `rank(PQᵀ) = 8` cost ≥ 64, including R8: every rank-8 completion of the mask is `D·G8·D⁻¹` | PROVED mod inputs listed in PROOF.md §3.1 (FULLWALL-9's `|S| ≤ 2` hand lemma, the core form, Step A of (b)); finite facts EXACT with an independent second code for each | `corea`, `coreb` |
| (d) | **COVERSAT.** `C(T) = 8` (no cost-7 decoder on the 8-line set `T`) for KFAM orbits 0, 1, 3, 4 under the exact-support cover model with Ferrers atoms. **Exact cost, not border cost** | CHECKED-EXACT with certificates: all 15 shards of each orbit closed by kissat UNSAT + drat-trim VERIFIED (re-found by `verify.py`); orbits 1 and 4 use no Groebner no-goods at all, orbit 3 uses two Nullstellensatz-certified 4-cell cores (checked in exact arithmetic). Orbit 2 is **OPEN** (10 of 15 shards closed) | `coversat` |
| (e) | **CT8.** `C(T) = 8` for rank-1 rectangles, all six KFAM orbits (exact decoders only) | EXACT. Orbits 2, 5: one rational LP-dual certificate, stdlib check. Orbits 3, 4: LP + exact DFS, re-run. Orbits 0, 1: hour-long DFS runs, logs + independent auditor logs, **not re-run** by `verify.py` | `ct8` |

## Open part, stated exactly

* **Rank-9 decoders with nine terms.** Nine terms and `rank P = rank Q = 9` (equivalently `rank M = 9`, `M = PQᵀ`). Every frame has a
  rank-1 defect; there are at least two P-classes and two Q-classes of frames. The conjecture "rank-9 completions are `G8` plus one
  rank-1 correction" is false (an exact rational counterexample on an A2 triple of lines).
* **`m ≥ 10` terms.** Cost 63 with ten terms forces a term of cost ≤ 6; cost-5-to-7 rectangles meet every frame, so monotone rows
  (frames, lines, global rank) only reach 18.886 and the proof must use coefficients.
* **Mixed decoders** with a genuine interleaved atom (≥ 9 pieces; smallest case seven rectangles plus one two-level atom). Rectangle
  results bound piece sums, not atom floors.
* **COVERSAT**: orbit 2 (5 of its 15 shards unsolved), and an independent audit of the cut-model encoding for orbits 1, 3, 4.
* **Exact versus border cost.** The cover model's "covered 0 or at least 2 times" clause and the AGLB rows hold only for *exact* decoders, so (d) and (e) bound exact cost, not the cost of eps-degenerate (border-rank) decoders.
* Not covered anywhere: multi-wire terms, coefficient synthesis, any physical realisation.

## What is CONDITIONAL, precisely

1. (c) uses three hand-derived inputs that are not recomputed here (PROOF.md §3.1): FULLWALL-9 §3 (`|supp v| ≤ 2`, audited), the
   rank-8 core form (S9 §4; a hand derivation, with the R8 hypothesis now supplied by item 4 of PROOF.md §3.1, leaving Step A), and the 8-term merged-term bound. Part B of `s4.py` was audited by sampling plus the
   exhaustive `lossy.py` re-check on the special flats; Part A (≈ 490,000 configurations) is cross-checked by an independent
   stdlib code (`xpartA.py`) but was not hand-audited.
2. (d) is certificate-checked. The cut/ratio encoder used for 29 of the 45 shards of orbits 1, 3, 4 was independently audited after the first stage-1 audit (WALL-AUDIT: line-by-line re-derivation of `cutenc.py`/`enc.py` and about 560 pinned-pattern trials against exact rank, 0 mismatches); the audit re-solved no shard. The ratio lemma is proved in PROOF.md §4. Orbit 2 is not claimed.
3. (e), orbits 0 and 1: re-run only through the original logs and an independent auditor's run (`data/ct8_logs/`).
4. Orbit-enumeration steps use pynauty; completeness is cross-checked by an independent C count in (a) and by a second code in (c).

## Further results from the rank-9 work (documented here, **not replayed** by `verify.py`)

Source: the RANK9 card of this research line (its own verifier exited 0; scripts not bundled in this package).
* **R7 (CHECKED).** Every rank-7 completion of the E7 sub-pattern `O(x)` (59 lines) is `D·G8·D⁻¹`, over any characteristic-0 field. No-extra-zeros part: kissat UNSAT with drat-trim VERIFIED; the lattice part has 2-torsion `(Z/2)^4`, handled by an exact sign-twist test; independent mod-p rank code agrees.
* **Gating criterion (PROVED).** `rowspace(M) ⊇ Γ·D2` iff `Q` has the rank-8 core form.
* **LOOSE / PAIR lemmas (PROVED mod R7, CONDITIONAL on one sub-case Z0).** A P-loose line `x` forces `M[:,O(x)] = Λ G8[:,O(x)] D⁻¹`; two orthogonal P-loose lines force the P core form, except in the sub-case `Z0 = {t : λ_t = 0}` (the transposed `d2_x = 0` case), which is open.
* **Tightness at m = 9 (PROVED, 4 lines).** Rank-9 decoders of cost exactly 64 exist (the 64-cost coordinate decoder plus one cost-0 term `(x, N(x))`). So the nine-term wall, if it holds, is tight; no 9-term decoder below 64 is known.
* **m = 9 gating itself is OPEN:** it is not known that every rank-9 decoder has a loose pair or a core-form side. Both loose sets being cliques (e.g. the A2-triple family) is the unresolved case.

## Reproduce

```sh
python3 -I -B research/p112-decoder-wall-partial/verify.py --jobs 4           # all groups: about 49 min wall with 4 jobs
python3 -I -B research/p112-decoder-wall-partial/verify.py --only ct8 --no-ct8-dfs   # stdlib only, under 5 s
python3 -I -B research/p112-decoder-wall-partial/verify.py --only fw,im8 --jobs 2    # etc.
```

Groups: `fw` (a), `im8` (b), `corea`+`coreb` (c), `coversat` (d), `ct8` (e). `--skip-cuts` runs COVERSAT stage 1 only.
Expected final marker: `PASS_P112_DECODER_WALL_PARTIAL`. Saved run: `data/verify_run.log`, `data/receipt.json`.

The orchestrator is standard library only, but the vendored checks are **not**: they need Python ≥ 3.10 with `numpy` and `pynauty`
(`pip install numpy pynauty`; orbit enumeration), a C compiler (`cc`), `kissat` and `drat-trim` (`git clone https://github.com/marijnheule/drat-trim && make`;
set `DRAT_TRIM=/path/to/drat-trim`, and `KISSAT` if kissat is not on `PATH`), and, for CT8 orbits 3 and 4 only, `scipy` and `networkx`
(otherwise those two steps report `SKIPPED`). Missing tools make the run fail unless `--allow-missing` is given. Large DRAT proofs
are not shipped: every CNF is regenerated deterministically, pinned by SHA-256 where the original is available, and solved again;
the one proof that fits (`src/intm8/rigz50.drat.xz`, 4.4 MB) is shipped and checked directly. `src/coversat/shard.py` does one COVERSAT
shard (CNF, kissat, drat-trim) by hand.

Layout: `src/fullwall, intm8, core3, coreres, coversat, ct8` are the vendored scripts (paths made relative); `verify.py` copies `src/` to a
temporary work directory so that generated pickles never touch the tree. `data/` holds certificates and saved outputs.

## Runtime

Saved run (`data/verify_run.log`, `data/receipt.json`): 100 steps, all PASS, wall 2,942 s (49 min) with `--jobs 4` on a shared machine; the sum of step times is 151 min, so a serial run (`--jobs 1`) exceeds an hour. The longest single steps are the COVERSAT cut-model shards of orbits 1 and 4 (up to 24 min each) and FULLWALL's rectangle enumeration (9 min). `--skip-cuts` leaves about 15 min with 4 jobs.

## What CI replays

`VERIFY.json` registers one stdlib-only step (`verify.py --only ct8 --no-ct8-dfs`, about 1 s): the exact rational LP-dual certificates for CT8 orbits 2 and 5.
Everything else (groups `fw`, `im8`, `corea`, `coreb`, `coversat`, and CT8 orbits 3 and 4) needs numpy, pynauty, scipy/networkx, `kissat` and `drat-trim`,
which the runner may not provide, so it is a **local check** with the exact commands under "Reproduce" (about 49 min with `--jobs 4`; saved log and receipt in `data/`).
The shipped 4.4 MB DRAT proof (`src/intm8/rigz50.drat.xz`) is re-checked only by that local run.

Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code.

## Open next questions

(Structured copies are in `TASK.json`.)

1. **Rank-9, nine terms: does it cost ≥ 64?**
   *Why it matters:* it is the smallest uncovered case; a 63-cost decoder would have to live there.
   *First step:* prove the gating lemma that some P- or Q-class of every rank-9 decoder has a row-rigid complement of at least 40 lines
   (random line sets of that size always are, 28 or fewer never). Then the CORE-COMPARISON reduction (P differs from an honest rank-8
   core only on the off-set rows) yields `cost(D) ≥ cost(D°) − #losses`.
   *Blocked by:* a no-extra-zero fact for sub-patterns `L ∖ Λ` (checked by DRAT only for `Λ` = one line and the A2 triple of line orbit 0, 9, 10),
   and the loss count for the sub-case where an off-set row has `d2_x = 0`.
2. **`m ≥ 10`.**
   *Why it matters:* cost 63 allows a term of cost ≤ 6, and none of the cheap-row arguments sees the coefficients.
   *First step:* extend the per-frame defect (`rank M = 8 + rank S_F`, class lemma) to `m = 10`.
   *Blocked by:* no classification of rank-9 completions.
3. **Mixed decoders with ≥ 9 pieces.**
   *Why it matters:* all decoders with a genuine atom live there, whatever their term count.
   *First step:* redo the rank-8-core analysis for seven rectangles plus one two-level atom, using MIX-8.
   *Blocked by:* atom floors are not piece sums (`max_j ≤ floor ≤ Σ_j`).
4. **COVERSAT: audit the cut model; solve orbit 2.**
   *Why it matters:* orbits 1, 3, 4 rest on the cut/ratio encoding, which was independently audited (WALL-AUDIT: line-by-line re-derivation of `cutenc.py`/`enc.py` plus about 560 pinned-pattern trials against exact rank, 0 mismatches; the audit re-solved no shard); orbit 2 would complete the family of five KFAM orbits.
   *First step:* for orbit 2, re-run its five open shards with certified no-goods.
   *Blocked by:* orbit 2 has almost no free cells, so its polynomial systems have about 50 equations.

## Credit

The problem and its framing (is there a masked P112 decoder of cost ≤ 63?), the 16,556-entry two-star support dictionary and the
frame/line/clique rows are due to **1337isnot1337 (Cinna Davis), #5088** (context only; see the sibling package
`p112-dictionary-floor`, which proves that floor for that dictionary). The masked decoder model is DreamingOfClouds / PR717.
The T-block reduction and KFAM orbit sets come from the earlier TWOSIDE and CT8 cards of this research line; COVERSAT, FULLWALL,
INT-M8, CORE3 and CORE-RES build on them. Proofs, enumerations, certificates and this package: **DreamingOfClouds with Claude Opus 5.5 (Anthropic), via
Claude Code**, with independent read-only AI audits of FULLWALL, INT-M8, CORE3, CORE-RES, COVERSAT stage 1 and CT8 orbits 0 and 1
(re-derivations and, where stated, re-runs). No human or formal-kernel proof review. Apache-2.0.
