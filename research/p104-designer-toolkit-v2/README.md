# tk: the P104 designer toolkit (exact pricing, legality, rebuild, generators, floors)

This package claims **no kappa and no new word**. It is the tooling used to design, price, audit and rebuild P104-family words, packaged as one command, `tk`.
Every number it reports is exact arithmetic or a legality replay; CP-SAT (`ortools`) and a C compiler are optional accelerators. It supersedes the
smaller `research/p104-designer-toolkit` (kept frozen) and builds on the swarm's published words and verifiers (credits at the end).

## What is in it
| area | commands / modules | what it does |
|---|---|---|
| exact pricing and legality | `tk price`, `tk check`, `tk accept`, `tk adopt`, `infra/legal.py`, `infra/price_exact.py` | exact invoice and Decimal-50 crossing of a word, every legality violation localised to rule/event/register, the PR's own `price.run` for acceptance, and `tk adopt` which derives a verifier profile (`profiles/*.json`) from a PR head |
| rebuild pipeline | `tk rebuild`, `alignbuild/` | re-derives the skeleton, Y routing, hubs, markets and signal events of #6030 from pinned rule builders (never-lose, each step accepted only at exact kappa); `--post fold,hoist,retain` then applies the constructor passes that give #6144 (fold, hoist) and #6167 (retained-operand stop drop) automatically |
| generators | `tk gen2`, `tk gen3`, `tk synth`, `tk gensearch`, `tk genpipe`, `gen2/`, `synth/`, `genpipe2/3.py` | from-scratch word generation (gen2: markets, Y-route, late stages; gen3: gen2 plus Y-route/primgen/signal stages), spec-space search, never-lose stage pipelines |
| sub-circuit re-solve | `subcirc/`, `surgery/`, `tk anatomy`, `tk bulk`, `tk shipcheck` | per-column I/O specs of #6030 markets, extract/splice of octet columns with bit-exact round trip, anatomy ledgers, whole-corpus tables, shippability check |
| move classes and screens | `tk retime/evretime/reorder/reframe/handoff/split/split2/ibase/a2x/blockmove/relay/pscreen/eval/search/plateau`, `movekit.py`, `prims*.py`, `macros.py`, `ctxmine*.py`, `k2/` | exact neighbourhood screens (CP-SAT retimes, hand-offs, helper splits, primitive basis, macros, mined windows, a C++ SA kernel) |
| floor LPs | `infra/floors_true.py`, `infra/model3.py`, `infra/linwt.py`, `infra/rigidity.py`, `P104-THEORY.md`, `P104-LEMMAS.md` | the LP floors and lemma write-ups (what is proved, refuted and conditional) |

`MAP.md` is the full command reference and module map; `tk <command> -h` documents each flag.

## Quickstart
Python >= 3.12 with `numpy`, `scipy` and `sympy` (required; `mpmath` comes with sympy); `networkx` (the gen2/gen3 generators); `ortools` (CP-SAT commands); a C/C++ compiler (the native replay kernel `native/nativecore.c` and the k2 engine are built on first use). The CI pins are numpy 2.2.6, scipy 1.14.1, sympy 1.13.3.
```sh
python3 -m pip install numpy scipy sympy networkx ortools      # networkx: gen2/gen3; ortools: retime/evretime/reorder/frames
cd research/p104-designer-toolkit-v2
python3 -B tk.py --help
python3 -B tk.py price 6030                   # exact kappa .003125811557911897 and side constraints
python3 -B tk.py check 6167                   # localised legality verdict
python3 -B tk.py diff 6030 6144               # what changed between two words
```
Words are given as a path to `WORD.json[.gz]` or an alias of a word in `words/` (the #6030 lineage and the older lineage words the tests use).

### Reproduce #6030 -> #6144 -> #6167
```sh
python3 -B tk.py rebuild 6030 --sides skeleton,routing,hubs,markets,signal --post fold,hoist,retain --workdir /path/to/work
```
Measured from a clean clone (Apple M3 Pro, one core): the five-side rebuild of #6030 takes about 2 minutes (66 of 67 steps accepted at exact kappa .003125811557911897, the one gap is logged and skipped), `fold` takes about 9 minutes for the three sites it accepts (about 1 to 4 minutes per solve), and `hoist` and `retain` take under a second each.
The chain then ends at kappa **.003128652015904059**, the exact kappa of #6167. The second accepted fold site reaches .003127144482523 (the kappa of #6143), and after `fold,hoist` the kappa is .003128393203271 (the kappa of #6144); `retain` applied to the shipped #6144 word reproduces #6167's program bit for bit (`tests/retain_test.py`). The rebuilt words are not program-identical to the swarm's hand-built words (event layouts differ: 23346 vs 22821 events for #6167); what is reproduced exactly is the legal word's kappa, the pass sequence and the single-site edits.
`--sides skeleton,hubs` is the one-minute smoke (37 steps). Judging intermediate words: the step outputs are judged under the input word's verifier profile (fold/hoist) and under the newest profile of the family (retain, which adds a lifetime), see `alignbuild/api.py` and `rebuild.py`.
Heavy commands run synchronously by default; set `TK_HQ=/path/to/wrapper` (called as `WRAPPER NAME TIMELIMIT argv...`) to route them through a job queue.

### Tests
```sh
python3 -B tests/regress.py --fast      # about 2 minutes: prices, legality + localised mutants, native replay, screens, shipcheck, rebuild smoke
python3 -B tests/regress.py --quick     # the stdlib-fast suite incl. generators, surgery, bulk, rebuild mini chain
python3 -B tests/regress.py --solver    # CP-SAT checks (needs ortools): retime 5551 == #5561 and evretime
python3 -B tests/regress.py --real 5551,5553,5561    # the unmodified PR5545 verifier stack (about 200 s per word)
```
`tests/*_test.py` are the per-module tests that `regress.py` drives; each is also runnable alone.

## Environment and layout
- `TK_WORK` (default: the package directory) holds scratch state: `.cache/`, `out/`, `jobs/`, `ext/`. All are git-ignored. `TK_PYTHON` selects the interpreter used by the `tk` shell wrapper. Nothing sets environment variables at import time.
- `ext/` is where optional inputs and outputs of research drivers live (for example `tk adopt` working copies, search stores, generator run directories). The drivers that need inputs that are not shipped say so and exit.
- `words/` holds the reference words; `profiles/` the verifier profiles (descriptor JSON plus the PR's own `base_local.py` / `pricing.py`, byte-pinned by hash); `inputs/` the byte-pinned PR5545 verifier capsule used unmodified by `--real`.

## Scope and limitations
- Tooling only: no kappa claim, no new word, no proof of a theorem beyond what `P104-LEMMAS.md` states (it separates proved, refuted and conditional items).
- Models are not oracles: retime/evretime/reorder objectives are linearised kappa and the reported kappa is always the exact re-price. Free helper start/final frames are a verifier freedom, not a maintainer-approved contract.
- `rebuild` and the surgery/anatomy tools carry #6030's register/frame numbering in `alignbuild/data/`; other words must share that numbering (the octet class around #6030) or bring their own manifest. Steps that do not solve are logged GAP and skipped.
- Not runnable from a fresh clone (inputs not shipped): `tk gen` (S4GEN window-B trees), `planbuild/plan.py` and `build.py` (plan-search model trees; source only), `hops --recomb`, the BIT-side drivers that need adopted BIT packages, and the k2 engine tests that need unshipped nets (`k2unify_test`, `k2levers_test`, printed as SKIP). `tk adopt` needs network access. `leverbank_test` and `genpipe2_test` need `networkx` (printed as SKIP without it).
- The rebuilt words are legal at the target kappa but not program-identical to the swarm's hand-built words; `retain` on the shipped #6144 word is bit-identical to #6167.
- CI replays `VERIFY.json` (`tests/regress.py --fast`, which includes the rebuild smoke, and `tests/retain_test.py`); the CP-SAT legs need `ortools`, which generic CI lacks, so there the retime is verified from its shipped output.

## Open next questions
1. Can the unshipped model inputs of `planbuild/` (plan-search population, class-break picks) be packaged so `plan.py`/`build.py` run from a fresh clone? Blocked on vendoring the model trees; first step: list the modules the two files import and vendor the minimal closure.
2. Can `fold` (about 3 minutes per accepted site) be made fast enough for generic CI to replay #6030 -> #6144 end to end? First step: profile `alignbuild/iob2.py` on one site and cache the rule matrices.
3. Are free helper start/final frames and the owned-inventory pins part of the caller contract? The toolkit reports gains under the adopted profile's literals, which are conventions, not specification; maintainer review is the blocker. First step: `tk retime 5551 --free starts` and compare with `tk diff`.

## Credits
The tooling reproduces and extends words and verifiers published by the swarm: the #6030 lineage (#6030, #6143/#6144), #5907, #5827, #6167 (aliromman), #6163 (petalas), #6166 (Matarener), and the earlier P104 line #5545, #5551, #5553, #5561, #5599, #5612, #5660. `profiles/*/` and `inputs/` carry those PRs' own verifier sources unmodified.

Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code. Apache-2.0 (repository license).

---

# Command notes

## `tk price WORD [--real] [--wait] [--json] [--no-cache]`
Exact kappa. Fast path (0.4 s, cached in `.cache/` by file sha): `legal.check` -> exact invoice (T,P: 18 calls x helper credits / paid MOVE ranks + the word-independent outer part)
-> Decimal-50 root of `sum (T_r-P_r) r^(1-k)`, the 1e-14 crossing interval, the three tail side constraints (alpha, gamma, delta) and the event/scalar budgets.
For the published aliases it also prints `expected ...: MATCH|MISMATCH` (claims >=14 decimals must be an end of the crossing interval, shorter claims the truncated root).
`--real` runs `real.py` = the unmodified `local.replay`, `reverse_columns`, `native`, the physical caller and PR5551's `pricing.py` with only the census/claim literals patched
(like `infra/realcheck.py`, plus the literal-only `local.py` patch #5553 shipped for words with N != 735 public registers), ~4 min, result cached (`interval`, `crossing_lo/hi`, 54+4 outer checks, per-stage seconds, or the failing stage and its `need` message).
Reference: #5551 .0030415311671457, #5553 .0030428242623657, #5561 .0030814243338015 (real interval [.0030814243338,.00308142433381]).

## `tk check WORD [--native] [--exact] [--wait] [--max N] [--json]`
Legality oracle with localisation; exit code 0 = legal. Fast path ~0.1 s: ALL violations (not just the first) of the real `local.py` rules
(MOVE source/ownership, nested chronological transport, dyadic/common-chart ADD/COPY/SCALE, owned INIT/CLEAR, peak owned = 1, final frames, endpoint rows by random evaluation mod 2^61-1, productive-input and literal-port rules).
Each violation prints the real rule string, the event index and, for event rules, the register **role** (X source / Y target / helper / owned scratch), its current frame, the event that last set that frame,
the source register of an ADD/COPY and its frame, and for nesting errors the offending vectors. End-of-program rules (final frames, endpoint rows, helper nesting, literal ports) list the registers and their last events.
Limit: a wrong *value* (e.g. a corrupted ADD source that still obeys the frame law) is only detected at the endpoint row it corrupts; the event is not identified.
`--native` runs every distinct MOVE frame pair and every helper boundary through the vendored native Gaussian-recipe check (rank == dim gap) in-process (minutes; run it inside an hq job: `$TK_HQ NAME TL python3 -B toolkit/tk.py check W --native`).
`--exact` queues `real.py --upto native` (stages replay / reverse_columns / native; the first rejecting real `need` message is reported).

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
`tk diff 5551 5561`: scalar program identical, 170 MOVEs removed (93 helper, 4 X, 73 Y), 168 helper starts + 23 finals changed, 149 main MOVEs relabelled -- the AUDIT-5561 numbers.

## `tk hops MATRIX [--signed] [--program FILE] [--points vu.pkl] [--json] [--recomb]`
Delivery-program verifier/counter (HOPILP / SIGNHOP). MATRIX (npy/json/text; rows outputs, columns leaves; zeros = support, signs for `--signed`, e.g. `SIGNHOP/Smodel.npy`).
Program lines `hi lo a` (unsigned) or `hi lo keyhex a` (signed) as written by `sa*.cpp` / `rc1.txt` / `srecomb.py`; defaults `HOPILP/rc1.txt` and `SIGNHOP/S.out`.
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


## Gotchas
- `infra/legal.py` was touched once: 'Endpoint rows' / 'Final frames' details now list the register ids (strings only, API unchanged).
- Models, not oracles: `retime`'s objective is the linearised kappa; the *reported* kappa is always the exact re-price. Illegal or frame-unsound words get a WARNING from `price`.
- Conditionality: free helper starts/finals are a verifier freedom, not a maintainer-approved contract (AUDIT-RETIME / AUDIT-5561).

## `tk decompile WORD [--out F] [--no-forms]` / `tk realise DAG [--schedule exact|lazy|FILE] [--drop-helper H,..] [--out F]`
Value-level round trip (TKSYNTH and dag.py): word -> DAG (MOVE-free ops, linear form per value, required outputs, MOVE-hop schedule) -> word. `tk realise` reports value-level errors (undelivered rows, first diverging op per register), then runs the localised `check` and the exact kappa.
`tk decompile 5561 && tk realise 5561` -> LEGAL, kappa .003081424333801543 (identical invoice). `--drop-helper 706` -> 7 undelivered Y rows + Endpoint rows violation.

## `tk reorder WORD [--k K] [--maxm M] [--tl S] [--window LO HI] [--out F] [--inline|--wait]`
Event-ORDER + frame retime (`relat.py`, evlat generalised; COMMREAD lane). Events that commute change places: reads of one register commute, additive writes into one register commute (`ADD(t,s)` = R on s, W on t); SCALE/INIT/CLEAR/COPY and every event touching an owned register are fixed barriers. Per register: I, epochs, F; all frames an epoch-bearing register visits form a chain, dims are monotone across epochs, cost = chain cost through the SET of dims visited (exact y/pay encoding -- the loose version never found anything). Helper starts/finals free, MOVEs re-derived, cyclic global orders cut lazily, result re-checked with `legal.check` and exactly priced; always run `tk check --native` on a gain.
`--window LO HI` pins everything outside the touched events (seconds). Works on N=750 words (#5599). Core: `python -B relat.py WORD OUT.json.gz TL K MAXM [LO HI]` (env HEAVY_THREADS, REORDER_ITERS, REORDER_CAP; diagnostics NOSOLVE=1 identity round trip, FORCE=other.word forces that word's frames). Tests: `tests/regress.py --reorder` (4 checks, also part of `--solver`).
Rediscoveries: `tk reorder 5580 --window 13520 13640` -> OPTIMAL in 3 s, = #5565 Stage A (.003084155550804, identical invoice to `5565A`); `tk reorder 5551 --window 13900 14700` -> .003044088 (+2.56e-6, native-clean) beyond #5565-old's +4.2e-7. Aliases added: 5565 (new cascade word), 5565A, 5565old, 5599.

## `tk split WORD [--apply] [--max N] [--out F] [--public-cap 750|0] [--event-cap 26000] [--free-decay] [--list K]`
#5599's independent helper splits as a move class (SPLITGEN). Screen = vendored package `search.py` (splitvendor/): a non-main helper group with common (initial U, final V), a strictly nested stop F, a pure row a / column b pair at a MOVE cut (aP=c, Sb=d on the group, ab=cd=1, dyadic basis). Each hit is built (`construct.split`), replayed (package `local.replay`), `legal.check`ed and priced exactly with the p5599 profile (decay 39/40); `--apply` greedily applies the best (dkappa, fewest events) and rescans (~40 s/scan, so run in chunks or via cpuq). Gain depends on the rank pair only: [5,4] +1.40e-6, [2,7] +1.08e-6, [8,1] +0.72e-6 (on #5565 level). `tk split 5565 --apply` reproduces #5599 (13 splits, .0031004563072); `tk split 5599n` = 0 hits. Alias `5599n` = current #5599 head 09dd0965 (748 regs). Tests: `tests/regress.py --split` (80 s), `--split-full` (~10 min). Notes: ext/SPLITGEN/NOTES.md.

