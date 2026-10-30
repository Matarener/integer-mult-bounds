# Toolkit: exact pricing, legality oracle and free-endpoint retime for P104-family words (no kappa)

This package claims **no kappa and no new word**. It ships the designer tooling behind the recent P104 retime line as one command, `tk`, with a regression suite
that reproduces the published numbers of PR5551, PR5553 and PR5561 and the retime PR5551 -> PR5561. Everything is exact arithmetic or a legality replay; the only
solver (CP-SAT) is optional.

| command | what it does | reproduces |
|---|---|---|
| `tk price WORD [--real]` | exact invoice and Decimal-50 root of a word, crossing interval, side constraints, budgets; `--real` = the unmodified PR5545 verifier stack with only census/claim literals patched | #5545 .0030411718, #5551 .0030415312, #5553 .0030428243, #5561 .0030814243 (and starts-only .0030768800); real-stack intervals identical to the published ones |
| `tk check WORD` | fast legality oracle listing ALL violations with rule string, event, register role and frame | the shipped words are legal; three mutants are localised (bad MOVE, wrong final frame, corrupted ADD) |
| `tk retime WORD --free ...` | exact-lattice CP-SAT retime with named freedoms (needs ortools) | `retime 5551 --free starts,finals` = #5561 (170 stops deleted) |
| `tk evretime WORD` | event-level retime with free ADD placement (needs ortools) | #5561 -> .003081500768 (+7.6e-8) |
| `tk diff A B` | what changed between two words (events, stops, helper spans, invoice) | 5551 -> 5561: scalar program identical, 170 MOVEs removed, 168 starts + 23 finals changed |
| `tk sens WORD` | kappa marginals of the exact invoice | P104CLEAN table on #5545 (+7.25e-5 per paid rank-1 per call, ...) |
| `tk pricer [--synth]` | rank-r owned-pivot pricing generalising PR5392's price.py / verify.py | PR5392 RESULT byte for byte; rank-8 synthetic +7.2248e-5 / +1.4449e-4 |
| `tk hops MATRIX` | delivery-program verifier / hop counter | unsigned 916, signed 2797 |
| `tk gen` | S4GEN/GENX hub-partition generator (workspace only, not runnable in this package) | 921 hubs, native chain cost, filter 0/0 |

Run from the repository root with Python 3.12: `python3 research/p104-designer-toolkit/tk.py price 5561`, or `python3 research/p104-designer-toolkit/tests/regress.py --quick`.
Nothing is written into the checkout (cache and outputs go to a temporary directory; `TK_WORK` overrides).

## Files
- `tk.py`, `tkcommon.py` and one module per command; `infra/` = `legal.py` (legality oracle), `price_exact.py` (exact invoice / root), `lattice_retime.py`, `dims_relax.py`, `native_pair.py`; `pricer/` = `price_r.py`, `verify_r.py`, `synth.py`.
- `words/`: the five words the suite uses (PR5545, PR5551, PR5553, PR5561, PR5561 starts-only), byte-identical to their PRs (hashes in `SOURCES.json`).
- `inputs/pr5545-source-closure.tar.gz` (the byte-pinned PR5545 capsule, used UNMODIFIED by `--real`) and `inputs/pr5551-pricing.py`; `data/` = the SIGNHOP / HOPILP fixtures of `tk hops`.
- `tests/regress.py`: the regression suite (`VERIFY.json` runs it).
- `tk gen` and `tk hops --recomb` need research-workspace trees that are not shipped here; the suite skips them. The CP-SAT checks (`--solver`) need `ortools`, which generic CI does not provide: there the retime
  is verified by its output instead (`tk diff` of the shipped PR5551 and PR5561 words, exact price and legality of both), and `--solver` re-derives it where ortools exists.

Heavy commands (`--real`, `retime`, `evretime`, `check --exact`) run synchronously in package mode (in the research workspace they are queued through its job queue); `--wait` is then a no-op.

## `tk price WORD [--real] [--wait] [--json] [--no-cache]`
Exact kappa. Fast path (0.4 s, cached in `.cache/` by file sha): `legal.check` -> exact invoice (T,P: 18 calls x helper credits / paid MOVE ranks + the word-independent outer part)
-> Decimal-50 root of `sum (T_r-P_r) r^(1-k)`, the 1e-14 crossing interval, the three tail side constraints (alpha, gamma, delta) and the event/scalar budgets.
For the published aliases it also prints `expected ...: MATCH|MISMATCH` (claims >=14 decimals must be an end of the crossing interval, shorter claims the truncated root).
`--real` runs `real.py` = the unmodified `local.replay`, `reverse_columns`, `native`, the physical caller and PR5551's `pricing.py` with only the census/claim literals patched
(like `infra/realcheck.py`, plus the literal-only `local.py` patch #5553 shipped for words with N != 735 public registers), ~4 min, result cached (`interval`, `crossing_lo/hi`, 54+4 outer checks, per-stage seconds, or the failing stage and its `need()` message).
Reference: #5551 .0030415311671457, #5553 .0030428242623657, #5561 .0030814243338015 (real interval [.0030814243338,.00308142433381]).

## `tk check WORD [--native] [--exact] [--wait] [--max N] [--json]`
Legality oracle with localisation; exit code 0 = legal. Fast path ~0.1 s: ALL violations (not just the first) of the real `local.py` rules
(MOVE source/ownership, nested chronological transport, dyadic/common-chart ADD/COPY/SCALE, owned INIT/CLEAR, peak owned = 1, final frames, endpoint rows by random evaluation mod 2^61-1, productive-input and literal-port rules).
Each violation prints the real rule string, the event index and, for event rules, the register **role** (X source / Y target / helper / owned scratch), its current frame, the event that last set that frame,
the source register of an ADD/COPY and its frame, and for nesting errors the offending vectors. End-of-program rules (final frames, endpoint rows, helper nesting, literal ports) list the registers and their last events.
Limit: a wrong *value* (e.g. a corrupted ADD source that still obeys the frame law) is only detected at the endpoint row it corrupts; the event is not identified.
`--native` runs every distinct MOVE frame pair and every helper boundary through the vendored native Gaussian-recipe check (rank == dim gap) in-process (minutes).
`--exact` queues `real.py --upto native` (stages replay / reverse_columns / native; the first rejecting real `need()` message is reported).

## `tk retime WORD --free LIST [--pin mainstops] [--tl S] [--out F] [--wait]`
Exact-lattice retime of a fixed circuit (event order, operands and per-register MOVE counts fixed): CP-SAT over a subspace of F2^9 for each ADD-equal-frame cluster inside [sum of pinned frames below, intersection of pinned frames above],
strict nesting on register chains, helper credit rank >= 1, objective = linearised kappa; the realised word is re-checked with `legal.check` and re-priced exactly. `--free` names what may change (everything else is pinned to the input word's span):
`starts` helper initial frames, `finals` helper final frames, `stops` equal-frame stops may collapse (MOVE deleted; implied by starts/finals), `mainstops` main-register intermediate frames (free by default, accepted for clarity), `mainends` X-final / Y-initial.
The literal ports (X initial, Y final) are never free. `--pin mainstops` keeps main intermediate frames as in the input.
`tk retime 5551 --free starts,finals` -> OPTIMAL in ~5 s, kappa .0030814243338015 = #5561 (170 MOVEs deleted). `--pin mainstops` -> .0030672308 (-1.4e-5): the 149 main-stop relabels forced by shared ADD charts carry that gain.
Output word: `out/<alias>__<freedoms>.json.gz`; log in `jobs/NAME.log` (`RESULT {...}` line with status, ceiling, kappa, gain, moves deleted).

## `tk diff A B [--json]`
Events aligned by (op, register, coefficient) ignoring frame labels (difflib); reports sizes, kappa both ways, paid-call and credited-helper-rank histogram changes, fields/calls/surplus, events added/removed by op and register role,
MOVE stops deleted/added per role, whether the scalar program is identical, aligned events whose frame *span* changed, endpoint changes per role and helper start/final dimension histograms, budget slack.
`tk diff 5551 5561`: scalar program identical, 170 MOVEs removed (93 helper, 4 X, 73 Y), 168 helper starts + 23 finals changed, 149 main MOVEs relabelled.

## `tk hops MATRIX [--signed] [--program FILE] [--points vu.pkl] [--json] [--recomb]`
Delivery-program verifier/counter (HOPILP / SIGNHOP). MATRIX (npy/json/text; rows outputs, columns leaves; zeros = support, signs for `--signed`, e.g. `SIGNHOP/Smodel.npy`).
Program lines `hi lo a` (unsigned) or `hi lo keyhex a` (signed) as written by `sa*.cpp` / `rc1.txt` / `srecomb.py`; defaults `HOPILP/rc1.txt` and `SIGNHOP/S.out` (package copy `data/S.txt`).
Checks cancellation-freeness (each node = disjoint union of two children given by an affine functional; children leaves or program nodes with the induced normalised sign pattern; every row present), then prints
HOPS (non-leaf nodes), ROLES (= hops - outputs; cap 400), RESTORES (= 4 x hops, SIGNHOP model constant) and dead nodes. Reference: unsigned 916 (590 lower bound), signed 2797 in file (best fixed DAG 2704, pool bound 2521).
`--recomb` queues the CP-SAT recombination (`SIGNHOP/srecomb.py`, 1 h, 4 threads) for `Smodel.npy` only.

## `tk evretime WORD [--k K] [--maxm M] [--tl S] [--out F] [--wait]`
Event-level exact retime with FREE ADD PLACEMENT (MODELERR2 `ev_lat.py`, now `evlat.py`): every ADD/COPY event has its own frame variable (candidates = native frames of nodes within +-K on its partners' timelines plus the L/U anchor bounds;
with `--maxm M` all subspaces between L and U when dim(U/L) <= M), MOVEs are re-inserted wherever consecutive frames differ; the realised word is re-checked with `legal.check` and re-priced exactly.
`tk evretime 5561 --k 2 --maxm 0` -> OPTIMAL (about 10 s), exact kappa .003081500768 (+7.6e-8); `--maxm 3` FEASIBLE .003081518091 (+9.4e-8): stop placement is free but worth little on this word.

## `tk sens WORD [--calls N]`
Marginals of the exact invoice (P104CLEAN `sens.py` on any word): kappa change per call for one paid rank removed, paid merges, credit hand-off splits `a+b`, ...  `tk sens 5545`: one rank-1 paid per call = +7.25e-5, a 4+5 hand-off = +1.356e-6, nine ones = +4.35e-6.

## `tk pricer [--synth]`
Rank-r owned-pivot pricing (PRICE8 `pricer/price_r.py`, `verify_r.py`): PR5392's `price.py` / `verify.py` with the pivot rank r_q as a parameter. Plain run = `verify_r.py` with all r_q = 9, which reproduces PR5392's published RESULT byte for byte (about 25 s);
`--synth` = `synth.py`, one or two relations owned at rank 8: crossing .00309953590148 (+7.2248e-5) and .00317177354692 (+1.4449e-4), a ceiling on the crossing, not a word. Reads the unmodified `research/native-transpose-owned` (package mode: sibling directory; `TK_NTO` overrides).

## `tk gen [full0] [--realise]`
Workspace-only (needs the S4GEN tree and the #4610 window-B inputs; `TK_WORKSPACE`). Rebuilds the hub partition of window B from chains alone (no layout input): 921 hubs (native 929), chain cost equal to native 4010.092015, forward/backward support misses 0/0 (about 1 s). `--realise` also runs realise6 through hq (about 220 s, published REALISE OK).

## Regression test
`tests/regress.py --quick` (20 s; also sens and, in the workspace, gen): price (#5545, #5551, #5553, #5561, #5561s), check (legal + three localised mutants), diff, hops (916, 2797, tampered program rejected).
Flags: `--solver` = `retime 5551 --free starts,finals` (== #5561, same invoice) and `evretime 5561` (needs ortools), `--pricer` = verify_r and the rank-8 synthetic, `--real 5551,5553,5561` = the unmodified real verifier stack (about 200 s per word), `--full` = everything (28 checks).

## Gotchas
- `infra/legal.py` was touched once: 'Endpoint rows' / 'Final frames' details now list the register ids (strings only, API unchanged).
- Models, not oracles: `retime`'s objective is the linearised kappa; the *reported* kappa is always the exact re-price. Illegal or frame-unsound words get a WARNING from `price`.
- Conditionality: free helper starts/finals are a verifier freedom, not a maintainer-approved contract.

## Independent audit
None: this is tooling. Each command is checked against the published number it wraps; no independent human or proof-kernel acceptance is claimed. Free helper start/final frames remain a verifier freedom, not a maintainer-approved contract.

## Credits
PR5544/5545 (aliromman) and PR5551 (thu-nmrc) for the P104 word line and the verifier stack; PR5553 for the hand-off word; PR5392 (aliromman) for `native-transpose-owned`; PR5472 (GamingPuzzled) for the hand-off precedent. All predecessor credit retained.

Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code.

## Open next questions

- Are free helper start and final frames admissible in the P104 caller contract? Both `retime` and `evretime` assume the verifier's freedom; the toolkit reports it but cannot decide it.
- Can the CP-SAT retime be made deterministic (single worker, fixed seed) so the suite can regenerate PR5561 in generic CI?
- Can `tk check` identify the event behind a wrong ADD value (today it is localised only to the endpoint row it corrupts)?
- Can the hub-partition generator (`tk gen`) be packaged with its #4610 inputs so the window-B check runs in CI?
