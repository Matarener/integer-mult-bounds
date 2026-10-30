# MAP -- command reference and module map of the P104 designer toolkit

Paths are relative to this directory. Labels: LIVE (wired into `tk`), PLUGIN (screen reachable via `tk pscreen`), LIBRARY (imported by others), RESEARCH (model or negative result), DEAD (superseded).

## 1. Purpose and how to test
`tk` is the one tool for working on P104-family words (the integer-multiplication-bounds line; kappa is the exact crossing of the word's invoice). It adopts a swarm PR as a *verifier profile*, prices and legality-checks any word exactly, screens a word with every known move class (retime, hand-off, split, the primitive basis P0-P15, macros, context-mined windows), runs searches and from-scratch generators, and decides whether a generated word is shippable. It imports the single sources of truth in `../infra/` (`legal.py`, `price_exact.py`, lattice code) and the PR's own verifier stack (via `tkstack`/`accept`), so a fix there is a fix here. Entry: `toolkit/tk` (bash wrapper) or `python3 toolkit/tk.py`. Words are paths to `WORD.json[.gz]` or aliases (`words/<alias>.json.gz`, e.g. `5827`, `5811`, `5907`-profile family).

Tests (Python >= 3.12 with numpy):
- `tests/regress.py --fast` (HYGIENE, Oct 27): <=2 min single core (~80 s measured idle): price x5, fastnative, nincr, gensearch, pscreen registration, `screen_smoke --fast` (every screen still EXECUTED, 0.4x budgets, ~37 s), primmine/clsfix/learned/shipcheck, canon_test, import_env_test --fast, check x5 + 3 localised mutants. It is a SUBSET of --quick, not a replacement; run --quick before any ship/PR claim. Add `--time` to any regress run to print the seconds each check took (profile). --quick profile (idle, s): FASTSITES 95, screen_smoke 60, incr 36, admit 36, synth FRONTGEN/helper generators ~150 total, 4x accept ~58, split 32, fastnative 15, check --native 12; typically 9-10 min idle, more under load.
- `tests/regress.py --quick` (stdlib-fast, now ~90 checks incl. admit, incr, nincr, prims, macros, ctxmine, screen_smoke --quick; minutes, not the 20 s of the README era). Other flags: `--solver` (needs ortools), `--pricer`, `--reorder`, `--split`, `--split-full`, `--real 5551,5553,5561` (real stack, ~200 s/word), `--full`. Default = quick+solver+pricer.
- Per-module tests live in `tests/*_test.py` (one per module); heavy ones take `--heavy`/`--full`. `tests/*fuzz*`, `dq_diff.py`, `sedit_diff.py`, `rebuild_diff.py` are differential checkers against the reference path.

## 2. Command reference (`tk --help` lists 31 subcommands; global `--profile NAME` overrides profile resolution)
Heavy work (CP-SAT, real stack) is queued through `$TK_HQ` (<=4 jobs machine-wide); add `--wait` (bounded poll) or `--inline`. Never wrap in shell loops. Details of the first 12 are in README.md.

| cmd | one line | key flags |
|---|---|---|
| `price WORD` | exact kappa (0.4 s, cached by sha), side constraints, budgets | `--real` (unmodified real stack via hq, ~4 min) `--json` `--no-cache` `--wait` |
| `check WORD` | legality oracle, ALL violations localised; exit 0 = legal | `--native` (every frame pair; use hq) `--native-ref` (unmodified vendor kernels, ~150 s, no pair cache) `--exact` `--stack` (also run the profile's own local.py; reports MODEL_GAP) `--max N` `--json` |
| `retime WORD` | exact lattice retime of a fixed circuit (CP-SAT) | `--free starts,finals,stops,mainstops,mainends` (required) `--pin mainstops` `--tl` `--out` |
| `reframe WORD` | exact frame re-assignment (`frames.assign`), never worse than the input | `--k` `--maxm` `--tl` `--out` `--inline` |
| `evretime WORD` | event-level retime, free ADD placement | `--k` `--maxm` `--tl` `--out` |
| `reorder WORD` | event-ORDER + frame retime (commuting events swap) | `--window LO HI` `--k` `--maxm` `--tl` `--inline` |
| `handoff WORD` | successor hand-off screen (tail retarget, multi-partner, scratch, relabel) | `--apply` `--classes` `--top` `--threshold` `--selftest` |
| `split WORD` | #5599 independent helper splits, screen + greedy apply | `--apply` `--max` `--public-cap 750\|0` `--event-cap 26000` `--free-decay` `--list K` |
| `split2 WORD` | two-boundary split (#5718) -- movekit class | class flags below |
| `ibase WORD` | paid interior bases R=I+qE_ab (#5678) -- movekit class | class flags below |
| `a2x WORD` | A2 paid rank exchange (#5643/#5650) -- movekit class | class flags below |
| `blockmove WORD` | block reframe to a lower-dim chart (#5739) -- movekit class | class flags below |
| `relay WORD` | relay/temporal reroute by exact span (#5713/#5605/#5612; spansolve) -- movekit class | `--opt terms=4 sole=1 nbest=2 engine=dfs\|cpsat ids=i,j free=1` |
| `diff A B` | what changed between two words (events aligned ignoring frames, invoice histograms) | `--json` |
| `sens WORD` | kappa marginals of the exact invoice | `--calls N` `--json` |
| `hops MATRIX` | delivery-program verifier/counter (HOPILP/SIGNHOP) | `--signed` `--program` `--points` `--recomb` |
| `pricer` | rank-r owned-pivot pricing (PRICE8); `--synth` rank-8 ceiling | `--pivots` `--synth K` |
| `gen [full0]` | S4GEN/GENX hub partition of window B (workspace only; `TK_WORKSPACE`) | `--realise` |
| `decompile WORD` / `realise DAG` | word <-> value DAG round trip (dag.py) | `--schedule exact\|lazy\|FILE` `--drop-helper H,..` |
| `adopt PR` | derive + validate + register the verifier profile of a swarm PR (`profiles/PR.json`) | `--head SHA` `--pkg DIR` `--alias` `--no-accept` `--list` `--refetch` `--json` |
| `accept WORD` | real `price.run` acceptance with cached native pairs (seconds when warm) | `--native-ref` `--json` |
| `eval WORD...` | bulk pipeline: check --native + accept + price + screens iterated to a fixed point | `--jobs` `--screens a,b,..` `--rounds` `--accept full\|fast` `--no-pipeline` `--candidates DIR --threshold K` `--results F.jsonl` `--tl` `--word-timeout` |
| `bulk CORPUS_DIR` | BULKEVAL: whole-corpus table. Per word: price, check --native, shipcheck (base = newest adopted profile with the word's public count, else 6030), gapmap vs #6030 (per-side R0 ledger), anatomy --no-lifetimes -> append-only `results.jsonl`, resumable by content sha; writes `results.summary.md/.csv` sorted by kappa | `--out F` `--jobs 2` `--steps a,b` `--only ids` `--force` `--summary-only` `--lifetimes` `--ref 6030` `--hq` (ONE hq slot, 2 worker procs) |
| `plateau WORD` | neutral-network plateau walks + screens from each point | `--measure` `--budget CPUH` `--seed` `--dip` `--run-id` `--cpuq` |
| `search` | greedy\|beam\|anneal\|lns over plugin classes + screens; SQLite store; resumable | `--from` `--strategy` `--classes` `--budget` `--evaluator incr\|full` `--relax` `--frontier` `--report` `--s2s` `--cpuq` |
| `synth` | word synthesis from specs: `--spec-from/--gen/--roundtrip/--random N`, `--front-gen` (FRONTGEN) with `--back star\|gray\|dilworth\|grouped`, `--helpers ladder\|shared\|hub\|mainhub\|joint\|ptrie\|cse\|k2\|learned`, `--no-gap`, `--strict-bounds` | `--anchor` `--seed` `--store` `--cpuq` |
| `gensearch` | spec-space search over the generator (random\|evo\|halving) | `--strategy` `--minutes` `--report` `--plan` `--cpuq` |
| `genpipe SRC` | generate -> P14 -> P15 -> P2/P3 -> frames -> compact -> admit, never-lose stages | `--stages` `--budget` `--stage-tl` `--run-id` `--no-relax` `--cpuq` |
| `shipcheck WORD` | is a generated word shippable as a package; literals to change + precedent | `--base 5827` `--real` `--json` |

Movekit class flags (`split2 ibase a2x blockmove relay`): `--apply` (greedy apply best edits, write `--out`), `--steps`, `--max-sites`, `--shard i/n`, `--results F`, `--edit JSON` (apply exactly one edit, print exact kappa), `--list N`, `--exact-top N`, `--opt k=v`.


## 3. Module map by layer
Notes column = file with the details (all under toolkit/). "Status" = key result or state at Oct 27.

### 3.1 Verification, pricing, profiles
| file | purpose | status |
|---|---|---|
| `check.py`, `../infra/legal.py` | fast all-violations legality oracle | LIVE; `legal.py` touched once (register ids in two detail strings) |
| `price.py`, `../infra/price_exact.py` | exact invoice -> Decimal-50 root, tail constraints, budgets | LIVE; matches published claims to 1e-14 |
| `real.py`, `accept.py`, `tkstack.py` | real stack; seconds-warm real `price.run`; PR's own vendored stack driven by data profile | LIVE |
| `adopt.py`, `adopt_validate.py`, `profiles/*.json` | `tk adopt`: fetch PR head read-only into `TKAUDIT/src/g.git`, derive + validate profile | LIVE; 22+ adopted profiles (5551 .. 5907, `bit5512`, `bit5708`) |
| `tkcommon.py` | paths, hq submit, profile resolution, native-pair selection | LIVE |
| `fastnative.py`, `fastnative_cmp/` | numpy replacement of the vendored native pair checker, bit-identical | LIVE default; `--native-ref` = reference |
| `admit.py` | exact ADMISSIBILITY oracle (events, scalar, raw, alpha/gamma/delta, tail) beyond legality | LIVE (regress, eval) |
| `shipcheck.py`, `shipreal.py` | shippable-as-package check; derived literal-patched real stack | LIVE; no generated word shippable as-is |
| `diff.py`, `sens.py`, `hops.py`, `pricer.py`+`pricer/` | diff, marginals, delivery programs, rank-r pricing | LIVE |
| `dag.py`, `decompile.py`, `realise.py` | value DAG round trip | LIVE; no kappa |
| `bitword.py`, `bitval.py`, `bitadapt.py`, `bitworker.py`, `bitmut*.py` | BIT-side (G20) word model, exact value, adopt/price/accept/check, isolated PR-stack runner, oracle-vs-PR mutant validation | LIVE for BIT; 841/841 mutants agree |

### 3.2 Incremental evaluation
| file | purpose | status |
|---|---|---|
| `incr.py` | IncrWord: ~128-event chunks, `try_edit/commit`, 7-9 ms/edit vs 220-450 ms full | LIVE; fuzzed by `tests/incr_fuzz.py` |
| `native/nativecore.c`, `native/nincr.py` | C inner loop of IncrWord, bit-identical | LIVE but OFF unless `TK_NATIVE_CORE=1`; rebuild `python -c "import native.nincr as n; n.build(True)"` |
| `dq.py`, `movekit.py` (`quick`/`quick_full`), `sedit.py` | delta-quick site pricing; plugin framework; edit objects | LIVE; `quick_full` is the reference |
| `wsearch/evalincr.py`, `pools.py` | incr evaluator hook + incremental site pools for search | LIVE (`--evaluator incr` default) |
| `frames.py` | the one exact frame-assignment routine (`tk reframe`, used by genpipe, realise) | LIVE |

### 3.3 Move primitives (value-preserving; MOVEs are re-derived by `View.rebuild`; frames are parameters)
Defined in the original lane notes (not shipped) (sec. 0/1, with the 20-row PR decomposition table), the original lane notes (not shipped).
| tag | semantics (one line) | file | notes |
|---|---|---|---|
| P0 | free normalisation: coalesce equal-(t,s) ADDs, drop zeros, cancel inverses; P0' sibling merge | prims/prims_extra | PRIMITIVES, MOREPRIMS |
| P1s / P1c | strict commute / move an ADD past a conflicting event inserting the Steinberg correction (`[A,B]=[B,A,C]`); SCALE/COPY/INIT/CLEAR are barriers | `prims.py` | PRIMITIVES |
| P2 | re-time free variables: event chart, helper start/final, stop collapse | `prims.py`, retime/evretime | PRIMITIVES |
| P3 / P3x(P3') | conjugate a window by T=I+qE_ab (exact inverse) / inject-and-undo with the undo SOLVED in available values (spansolve) | `prims.py`, `ibase.py`, `relay.py` | PRIMITIVES |
| P4 (r/t/c) | register split (same/distinct bases), temporal hand-off, copy chain; merge not implemented | `split.py`, `split2.py`, `handoff.py` | PRIMITIVES |
| P5 | move a same-chart block to a new lower-dim chart | `blockmove.py` | TKMOVES |
| P6 | inject + undo with undo solved (joint/single/exact relay modes) | `prims.py` -> `relay.py` | MACROS |
| P7 | RETIRE: public helper -> owned scratch (role change) | `prims_role.py` | P7ROLE, SPLITRETIRE |
| P8 | owned courier/bridge: `acc` (accumulate group) and `ret` (return) | `prims_extra.py` | MOREPRIMS, P8GAP (KMAX bug fixed: #5811 has a 6-ADD group) |
| P9 | SCALE hop (P1 through SCALE with coefficient rescale) + COPY/SCALE fuse | `prims_extra.py` | MOREPRIMS |
| P10 | owned-lifetime chart / main endpoint reframe | `prims_extra.py` | MOREPRIMS (all neutral) |
| P11 | split one ADD into two placed apart | `prims_extra.py` | MOREPRIMS (null) |
| P12 | Weyl exchange of two co-framed registers over a window (3 transvections) | `prims_extra.py` (`sites12`) | MOREPRIMS |
| P13 | late-cut hand-over with solved compensation (generalises split2; #5786 mechanism) | `handover.py` | LATECUT |
| P14 | helper alias: redirect a victim's reads to an equal-X-content keeper | `alias_core.py`, `prims_alias.py` | ALIAS |
| P15 | P14 jointly with re-ordering of the readers' source reads | `prims_alias2.py` | SRCREORDER |
| PM1/PM2/PM3 | fused mined macros: Steinberg move (PM2: two) then P8 courier on the touched region; PM3 = P3 conjugation fused with the P8 sites of the conjugated window | `prims_mined.py` | PRIMMINE |
| PM4 | read redirect through a transvection pair `R=ADD(t<-x,a); x+=b y; y+=c x (bc=-1)` => `W1;W2;ADD(t<-y,a/c)` (half Weyl, the one non-basis mined rule) | `prims_mined.py` | PRIMMINE, GADGET2 |
| RSPLIT | remote Steinberg split: a read A moves earlier, its correction C lands anywhere the source is unchanged (even inside an owned lifetime). Explains #5827 (+5.8048e-7) | `automacro_rsplit.py` | AUTOMACRO |
| CTX windows | real-context window superoptimisation (H/T/SH/CC hops; CJ P3-conj, redirect, coef split/merge in v2) | `ctxmine*.py`, `ctxmine*_lift.py`, `*_scan.py` | CTXMINE, CTXMINE2 |
| classifier | `cls.search` over all linearisations + reverse; basis {P0,P1s,P1c,P3,P6,P8,P9,P12-half} complete for programs <=7 events; GADGET2: all 18 cap-limited rules decompose | `ext/PRIMMINE/cls.py` (outside toolkit) | PRIMMINE, CLSFIX, GADGET2 |
Other: `autodec.py` + `automacro_mine.py` (decompose real base->PR diffs into primitives, mine recurring macros; no macro recurs outside P5-repeat/P8-bundle/RSPLIT -- AUTOMACRO), `splitretire.py` (P4+P7 macro ceiling +1.66e-4 gross, net 0 -- SPLITRETIRE; RESEARCH), `spansolve.py`/`relaycomp.py` (exact span solver, compensated relay layer -- TKRELAY).

### 3.4 Macros and screens
| file | purpose | notes |
|---|---|---|
| `macros.py` | macro library + guided primitive search (P6 inject-undo, ...) | MACROS |
| `pscreen.py` | registers every primitive/macro as a `tk eval` screen; sets listed in sec. 2 | P8GAP |
| `eval.py` | bulk pipeline, fixed-point screen rounds, candidate files | TKBULK |
| `ibase.py`, `a2x.py`, `blockmove.py`, `split2.py`, `relay.py` | movekit classes (plugin protocol `name/prepare/sites/scalars`; `update_sites`, `span`, `defer_regen` hooks) | TKMOVES, TKRELAY |

### 3.5 Searches
| file | purpose | status |
|---|---|---|
| `wsearch/drive.py`, `canon.py`, `store.py`, `guide.py` | `tk search`: greedy/beam/anneal/lns, canonical trace hash, SQLite lineage store | LIVE; #5756, #5718 are local optima of the four movekit classes |
| `wsearch/plateau.py` | `tk plateau` neutral-network walks | LIVE; 0 improving on #5811/#5812 (~6.9k neutral steps, scoped) |
| `bitsearch.py`, `bitscreen.py`, `bitprims.py`, `k2bit_search.py` | BIT-side search/screens/primitives (zrel/p1c/p0/pair), k2net walk on BIT | RESEARCH: no legal improving BIT edit |

### 3.6 Generators (`synth/`, `tk synth`, `tk gensearch`, `tk genpipe`)
All from-scratch words so far reach ~.0016 (about 51% of the frontier) and none is admissible under strict literals.
| file | what | result |
|---|---|---|
| `spec.py gen.py repair.py sample.py` | spec -> DAG -> word, repair, knob sampler | roundtrip OK; best = the anchor |
| `frontgen.py`, `backgen.py`, `backgen_measure.py`, `data/` | unhinted front end + dim-0 junk; back-end sign network (star/gray/dilworth/grouped) | star .0010212 |
| `helpershare.py`, `hubgen.py`+`hubsa.cpp`, `hubladder.py`+`.cpp`, `mainhub.py`+`.cpp`, `sharedsum.py`, `jointfeed.py`, `partialtrie.py`, `flaggen.py`, `hybrid.py`, `climbbuild.py` | helper-network designs (sharing, hubs, ladders, mains-as-hubs, linear CSE, joint feeders, partial-root tries, flag plans, swarm helpers + generated mains, constructive climbs) | best .0015482 (ss2); hybrid impossible as a gain; climbbuild stays 0.29-0.38 entries/R0 vs swarm 0.68 |
| `residual.py`, `rlever.py`, `rlever_sign.py`, `learned*.py` | residual carriers, signal-count lever (r*=8), mined design rules | R0 law input; rules fix skeleton not value layer |
| `s2s.py` | state-to-state window synthesis; also the event-budget compaction pre-pass (K2PUSH: frees ~5k events on #5827/candidate) | kappa-neutral |
| `compact.py` | post-pass event/scalar compaction | LIVE in genpipe |
| `gensearch/` | spec-space search | spec space exhausted ~.00125 |
| `genpipe.py` | pipeline orchestration | best jf_V0 .0016073 |
Generated-word results: COMPRESS (generic rewrites +0.2-0.5% only), GAPMAP (component attribution of generator vs swarm gap), UNITGEN (unit comparison P104 vs P108/P112; model), E4CONV/ROOTARCH/SIGNCODE(2)/FRAMEAUDIT/NETLB/MAINLADDER/SIGNOBS/LATTICEDESIGN/RELAYLAT (lower-bound and architecture analyses; RESEARCH, no code in tk).

### 3.7 k2net (rendezvous-program SA kernel; engine is C++ outside toolkit)
| file | purpose | notes |
|---|---|---|
| `ext/KERNEL2/{k2.cpp,k2net.inc,k2search.inc,k2grow.inc}` | engine: state = explicit rendezvous event program; K2_NET/K2_SEARCH=census\|sa; weights K2S_W; `k2grow.inc` only with `-DK2GROW` | KERNEL2, K2SEARCH, BLOCKGROW |
| `synth/kernel2.py`, `synth/kernel2net.py` | python glue + net encode/decode (`helpers: k2`); `kernel2_test.py` encode test (#5811 R0 7988.73) | KERNEL2 |
| `synth/k2search_validate.py` | net -> word realiser, legal, exact contract replay, price_exact | K2SEARCH |
| `ext/K2PUSH/` | event-pressure (EVPEN/EVT), HOP, multi-reader variants; binaries `k2p*`, `k2h*` | K2PUSH |
| `toolkit/k2/k2phi.inc` (+10 hook lines in k2search.inc, `k2/k2phi.hooks.patch`) | law-derived potentials + shaped k2 search, all runtime flags, DEFAULT OFF (flag-off bit-exact): F0..F5 rung slack/free rungs/blocked/drain/event slack/R0; D0..D3 delivery readiness (mvKill's precondition); (a) `K2S_PHI=1 K2S_PHITAU` neutral tie-break, (b) `K2S_PHIA` annealed shaping, (c) `K2S_PHILA=200` READY-KILL LOOK-AHEAD (RNG-paired with blind, takes a ready rung kill only if exact kappa rises), (d) `K2S_PHISEG` segment tie-break on D; logging `K2S_FLOG`/`K2S_FSNAP` | the original lane notes (not shipped). LIVE flags; (c) is the only arm that beats blind (time-to-first-improvement, 5/65 pairs earlier, 0 later; +15% wall) |
| `toolkit/potentials.py` | word-level potentials for generator look-ahead: `score(w)` (rung slack == C++, event slack, lifetime/idle/handoff/market R0 ceilings, shared sub-sums/brackets), `side_slack(w)` (admit gamma/delta), `delivery(w)['D0_ready']` (exact kill-ready R0, the look-ahead term) | the original lane notes (not shipped). LIBRARY (lifetime/idle/market read 0 on dim-0-load/dim-9-restore words; see notes) |
Result: #5811/#5827 are strict local optima of every single k2 move; plateau SA found +5.22e-7 (shipped as #5907).

### 3.8 BIT side (G20 words)
`bitword.py` (model, oracle, emit), `bitval.py` (exact value), `bitadapt.py` (adopt/price/accept/check, profiles `bit5512`, `bit5708`), `bitprims.py`/`bitsearch.py`/`bitscreen.py`, `synth/k2bit.py` + `k2bit_search.py` (k2net encode gap 0 on #5708/#5512; moves stay on the plateau), `bitceiling.py` and `mrf_ac.py` are scratch scripts (no docstring, hard-coded paths) -- DEAD. Notes: BITADAPT, BITPRIMS, K2BIT, CTRL2BIT (controller e=2 KILL, scoped sampled UB).

### 3.9 Automation and ship tooling
- Stale/duplicate files: `*.bak-*`, `prims_alias2.py.b`, `tk.py.bak-*`, `regress.py.bak-*` are editing backups -- DEAD, do not import.

## 4. Invariants and gotchas
1. **Env guard.** Search-mode switches `TK_FREE_BOUNDS` and `TK_NATIVE_CORE` must come only from the user's environment or a search driver's own `main`. `tk.py` snapshots both at start and `_restore_user_env` after parser/screen registration, because a leaked `TK_FREE_BOUNDS` once made `tk check` skip inventory bounds. Convention for new code: no env mutation at import. Reality check: `alias_core.py`, `macros.py`, `prims_mined.py`, `splitretire.py` still do `os.environ.setdefault('TK_FREE_BOUNDS','1')` at import time (tk.py's restore neutralises it for `tk`; direct `import` in your own script does not). `automacro_rsplit.py` guards with `__name__=='__main__'`, `prims.py`/`pscreen.py`/`ctxmine*_scan.py`/`genpipe.py` set it only in their CLI entry.
2. **Profile resolution** (`tkcommon.profile_of`): `--profile`/`TK_PROFILE` > adopted data profile whose word FINGERPRINT (sha1 of initial/final/program) equals this word (EXACT match first, so adopting a newer PR never changes how an older PR word resolves) > data profile with `auto` > built-in legacy family (`default`, `p5599`, `p5612`, `p5660`) > newest adopted profile of the same family (public, owned_fields, retired roles) > `default`. A word of an unknown family is no longer silently `default`. Fingerprints are only known for aliases that exist in `words/`. Data profiles drive `legal.profile_params` through `TK_VERIFIER_PROFILE`; `use_profile` restores the env.
3. **Bounds are conventions, not SPEC.** Event cap (26000 in all adopted profiles, convention A41), scalar cap 10^7 (coupled to raw `18*10**7`), public/owned inventory pins (they change every few PRs) and tail literals are package literals. `TK_FREE_BOUNDS=1` (infra/legal.py:52) skips event/inventory bounds for search; a shipped candidate MUST be re-checked under the real profile (`tk check`, `tk accept --native-ref`, `tk shipcheck`). Only the pending #5830 proposes a raised event bound (27504); CAPVALUE: our #5907 word is shippable as-is. `admit.py` separates REAL constraints (alpha, gamma, delta < 1, theorem) from literal ones.
4. **Fast native vs `--native-ref`.** Default native pair check is `fastnative` (numpy, bit-identical on 7 words, pair cache `.cache/nativepairs/`); `--native-ref` / `TK_NATIVE_REF=1` runs the unmodified vendor kernels (~150 s, no cache) and is the standard for ship claims. The pair cache was poisoned once by `incr_fuzz.py`'s FakeN (124 fake entries; removed -- the original lane notes (not shipped)): never let fuzzers write the shared cache.
5. **Exact vs model.** `retime`/`evretime`/`reorder` objectives are linearised kappa; the REPORTED kappa is always the exact re-price. RETIMEGAP: separately differenced T/P weights created ~3e-4 curvature artefacts (fixed); treat a model gain with exact gain 0 as an artefact. `quick` is a filter, `movekit.evaluate`/IncrWord is the judge; unpriced greedy can end illegal after 100+ accepts (SRCREORDER).
6. **R0 law.** helper net weight R0 = k*(D ln D - sum r ln r); empirical `1/kappa = 130.27 + .02364*(R0eq + 380*(owned_paid-56))` (ENDANATOMY refit, 11 words, kappa +-5e-5 rel; supersedes c=131.2 which absorbed #5907's staging), where R0eq = public tax + STAGED OWNED-DESCENT ENTROPY. **Owned staging law (OWNEDRANK):** the invoice charges every owned MOVE of rank r at the public weight (P_r += 18, no credit), so a staged owned descent costs its jump entropy `D ln D - sum r_i ln r_i` in R0-eq even though paid units stay 56 (splitting a rank-7 descent 4+3 costs 4.78, 4+1+2 costs 6.69; #5907 total 40.15 = 8 descents/20 moves; r104 0; m2 9.56); `gapmap.owned_staging` computes it and its 'owned (O)' row now equals it (was the per-register-id tax, 6.17 on #5907). Test: `tests/gapmap_test.py` (law vs `tk price` on 5907/r104/m2, 2e-4). A gap table that omits it misreads our-vs-swarm by 40 R0 and the levels of old-law predictions by up to 3e-3; so dkappa/dtax ~ -kappa^2*.02364 ~ 2.3e-7 per tax unit at the frontier. One OWNED rank unit costs ~300 tax units (~+2.4% kappa per owned rank), i.e. owned relays are ~100x dearer than helpers. A MODEL, calibrated on 3-4 points; use it to rank designs, then price exactly (HUBGEN, LATTICEDESIGN).
7. **Event cap.** Every generated word exceeds 26000 events (36-63k; compaction gets K2 best to 28.2k). Extra events are the binding resource for k2/SA moves (BLOCKGROW: cap 25999/26000 starves SA; HOP/s2s free ~5k events). Each P8 costs +3 events, P7 +4..6, P12 +3..4, relay edits +3..30.
8. **Classifier linearisation.** `cls.nf` keeps only the lex-min topological order of the commutation trace; P1c/P3 windows must be contiguous, so classify over ALL linearisations (cap 200) and both directions (fwd/rev) -- CLSFIX. Earlier "unresolved" counts (192) were an artefact; the original lane notes (not shipped) top block supersedes the lower counts.
9. **Blind-spot lessons.** Site finders with small caps miss real tricks (P8 KMAX=3 vs #5811's 6-ADD group; prims window indexing is S-index, not program-index -- use `prims.prog_to_S_window`). Prepared573 words (#5612/#5613) are refused by View/movekit/dag; #5751 (767 public) violates the shared 750 bound: use `--relax`. #5795 is not adoptable (adopt fails 'Role index'). Words in `words/` can be older heads than the PR (words/5565).
10. **Owned operands.** `prims.p1_apply` refuses ADDs with owned operands (`pub` guard) -- why plain `prims` cannot reach RSPLIT; owned registers are P1 barriers; step 1 of RSPLIT is exactly neutral so greedy never takes it. Kappa is not monotone along a decomposition (dips of 7e-7 precede gains).
11. **Hygiene.** Heavy jobs run directly (or through the optional `$TK_HQ` wrapper); python/CP-SAT thread counts capped; PR-stack runs use isolated `python3.12 -I -B`; GitHub access is read-only (fetch into `TKAUDIT/src/g.git`, no worktrees).
12. **Negative results are scoped.** Each NOTES verdict names its construction (e.g. "greedy per-reader builders", "single-step", "sampled UB"). Do not read "dead" as "impossible"; read the scope line first.
13. **Side check tail (TKHYG2).** Never call `X.side` directly: use `tkcommon.side_of(T,P,profile_of(w)[1])` so the adopted (c,b,u) tail is applied (legacy 17/18/.2 gives false FAIL on #5907/#5827). Converted: price, movekit, incr, evalincr, split, legalize, retime, evlat, relat; guarded by `tests/side_tail_test.py`.
14. **gapmap attribution (TKHYG2).** `gapmap.py` default is the jump-level CUT table (R0 of jumps ending <=c vs >c, cuts 3..7); the mid-dim band table (bottom/centre/top) is not a cut and misattributes - it is behind `--bands`. Older the original lane notes (not shipped) band rows carry that caveat. `tests/gapmap_test.py`.
15. **First non-swarm word (B0POLISH, Oct 27).** Three screens silently refused SIGFUSE b0 (and would refuse any from-scratch word): (a) `tkcommon.side_of` applied the adopted PR tail (c,b,u) -> side FAIL on every site, so prims/macros reported "0 exact-legal"; with `TK_FREE_BOUNDS=1` it now falls back to `X.tail_feasible` (best free tail) and tags `free_tail`; (b) `eval.verify` rejected the word ("side/native/crosscheck failed"): under `TK_FREE_BOUNDS` it now judges the side test by `admit.best` (new-value literals allowed; `free_literals` in the record); (c) `--accept full` runs the real stack and always fails "Public inventory bound" on a new-pin word: use `tk eval --accept fast --no-accept-each`. Open (k2/ not edited by this lane): `k2/screen.py` discards a legal SA gain when `tk accept --native-ref` says "Public inventory bound"; workaround `K2SA_NATIVE_REF=0` (then vet with `tk check --native` + shipcheck). Also `tk handoff` on a 23k-event word exceeds eval's subprocess timeout (eval records ERROR, other screens continue).
16. **k2sa native-ref convention fallback (GEN2POLISH, Oct 27).** `k2/screen.py`: when `tk accept --native-ref` refuses a k2sa gain ONLY with the public/owned inventory literal (`inventory_only(na)`; a convention on new-pin words, gotcha 15), the screen falls back to `native_check_free(path)` = `tk check --native` in a child with `TK_FREE_BOUNDS=1`, accepted iff exit code 0 AND `: LEGAL (` AND `0 bad` AND no `ILLEGAL` (the first version tested `'LEGAL' in stdout`, which also matches `ILLEGAL`). Any other refusal (native pair, side, crossing) still rejects. `K2SA_NATIVE_REF=0` is no longer needed. Test: `tests/k2screen_fallback_test.py` (in regress --fast). `tk gen2 --stages polish` (the original lane notes (not shipped)) = purex2 -> k2sa -> eval(evretime,retime) on o1y, TK_FREE_BOUNDS only in the child env.
17. **handoff B-class frame tracker (SPEED, Oct 28).** `handoff.enumerate_B` tracked register frames from MOVEs only; owned registers get their frame from INIT (and lose it at CLEAR), so on every frontier word since #5811 (5811, 5827, 5907, 6030 + head variants) it hit `fr[None]` and crashed -> `tk eval` recorded 'no applied word' and the hand-off screen silently contributed nothing. Fixed: INIT/CLEAR tracked, frameless sources skipped; candidates unchanged on the 39 words where the old code ran. Test `tests/handoff6030_test.py` (`tk eval 6030 --screens handoff`, rc 0; in `regress --quick`). Lesson: a screen whose subprocess fails must be visible in the eval record as an ERROR, not as 'no output'.

## GENPIPE2: `genpipe2.py` + `gen2/` (copies of RELAYTOP, SIGFUSE/B, JOINTFRAMES, MARKETS, PUREX code; lane dirs untouched).
- Pipeline (data flow is not linear): relaytop -> allh_d3 (.0025498, stand-alone ancestor) | routeb -> b0 (.0029001; 8 roots as sources + sigfuse.fuse_share) -> ylate -> yl1 (.0029031) | order (route B with sink-grouping order 51,30,45,75,120,102,85) -> o1 (.0029461) -> ylate -> o1y (.0029494) | purex2 on **o1** (`--dims 4,8 --xstops`) -> r104. Late births (ylate) and early ends (purex) are alternatives today: r104 is the pre-ylate base. polish (k2sa) is optional and not wired.
- Stage contract: input word (or none) -> `OUT/NAME.json.gz` + `NAME.canon.json.gz` + one line in `OUT/stages.jsonl` (exact `tk price` kappa, file/content/canon sha, events, side, params); `--expect` fails on a kappa difference > 1e-13. Identity of a word = sha256 of the decompressed JSON (gzip headers carry a time stamp, so file shas of regenerated words differ).
- Gotchas: allh_d3 needs the SORTED direction list (the b0 order gives .0025422); r104 comes from o1 not o1y; gen2 modules import each other by bare name (driver uses subprocesses); env (TK_FREE_BOUNDS) only inside main.
- **Conventions are not constraints.** Public bound (968 here), event cap 26000, scalar cap and tail literals are package conventions (sec. 4.3); the real checks on a generated word are: VALUE (symbolic replay, undelivered []), NATIVE (fastnative / `--native-ref`, 0 bad pairs), SIDE at an admissible tail (`tkcommon.side_of`/`admit.best`, sec. 4.13/4.15), and `tk shipcheck` (r104: needs new-value literals, admissible True). `tk check` flags only the public-inventory literal on these words.
- Tests: `tests/genpipe2_test.py --fast` (stage smoke, in `regress.py --fast`) and `--chain` (full chain bit-exact, in `--quick`).

## SURGERY tooling (Oct 27, SURGPREP. TOOLING only, no kappa claim
Multi-level edits that rebuild one octet's bottom-to-top column of a frontier word (base: #6030 = `words/6030.json.gz`, kappa .00312581155791). `toolkit/surgery/` (no env at import):
| file | role |
|---|---|
| `swlib.py` | octet-owner partition of all public registers (14 octets + POOL), event classification, exact invoice slice + R0 (tax) share, value fingerprints (`trace`, `xparts`) |
| `extract.py WORD --octet K\|pool [--out COL]` / `--summary` | column file (registers, internal events with original index t, interface events in/out with x-part + numeric fingerprints, local frame table, accounting) |
| `splice.py WORD COL --octet K [--out NEW] [--validate] [--retarget-inventory]` | re-wire a (rebuilt) column into the word; `tk check` oracle with the base profile pinned, exact kappa/side/budgets, interface pins, inventory deltas |
| `validate.py BASE NEW --column COL` | SPAN5 x-part span law (dims 1..8) + JR chart law, restricted to the frames the column visits (base vs new) |
Test: `tests/surgery_test.py [--fast\|--full]` (in `regress --fast`): extract+splice of the unchanged column reproduces #6030 BYTE-EXACTLY (canonical bytes, kappa, 0 pin mismatches) for all 14 octets + pool; relabel/shrink layouts; negative control. Pin: profile 6030 fixes public=770, so any change of the register count fails `tk check` unless `--retarget-inventory` (shipcheck literal).

## BULKGEN additions (Oct 28, BULKGEN: `tk rebuild` and `tk anatomy` = the bulk-eval foundation (TOOLING, no kappa claim)
`toolkit/alignbuild/` consolidates the five pinned rule builders as COPIES (lane dirs untouched) behind one interface; nothing imports a lane dir, no env at import.
| file | was | role |
|---|---|---|
| `skeleton.py` (+ `routing.py`) | SKELORIGIN `sb.py` (COMPOSE copy) + YROUTE `yb.py` | skeleton park stops of one low-reader octet, then yb rebuilds the Y reads (fused: `routing` selects the skeleton steps) |
| `hubs.py` / `hubs_owned.py` | HUBRULES `hubbuild2.py` / OWNEDHUB `hubbuild3.py` | octet-frame hubs O_r (public; `--owned` for 240/243/1090/1091) |
| `markets.py` / `markets_full.py` | MKTCOMPACT `fullbuild.py` / FULLWORD `fullbuild3c.py` | dual-cone markets G_r with the compact tail (10 / all 14 duals, gate+proxy flags for f1031/f117) |
| `sigside.py` | COMPOSE/SIGPIN `sigb.py` | root feeds / reads (`--freebounds`: convention literals only) |
| `rp.py life.py mktbuild.py fcls.py tiling.py data/y1,y4.pkl` | SURGERY, ALIGNLAW, SKELCLASS, SKELGEN, YREADORIGIN | libraries and the (source, reader-Y) incidence, copied |
| `api.py`, `data/manifest_6030.json` | new | `kappa_of`, `step`, `rebuild`; the plan (octets/frames/duals/roots, order, flags) |
| `anatomy_core.py`, `endanat.py` | ALIGNLAW life/attrib, ENDANATOMY anat, HUBCOST ledger, gapmap | per-side ledger functions |
- `tk rebuild WORD [--sides skeleton,routing,hubs,markets,signal] [--out F] [--workdir D] [--manifest M] [--resume] [--no-checks] [--max-events 26000] [--json]`: runs the verified FULLWORD order (skeleton 12 octets -> 10 public hubs -> tie octets 5,12 -> 13 more hubs (4 owned) -> 10 compact duals -> 4 gated duals -> 16 signal steps), each step in its own process on the previous output, accepted only if LEGAL at the INPUT word's exact kappa (|dk|<1e-13, `tk price`); a failing step is logged GAP and skipped. Exit 0 iff the final word has the input kappa exactly, is legal, has <= --max-events events, SPAN5/JR 0 (surgery/validate.py --all) and native 0 bad. Stage time (after REBUILDSPEED): full chain ~3 min (was ~45-65 min); run via `$TK_HQ`. On #6030 it reproduces FULL_final (kappa .003125811557911897, 23333 events). SCOPE: ids in the default manifest and the y1/y4 incidence are #6030's; a word outside that numbering needs its own manifest/incidence (steps that do not solve are GAP, never silently wrong).
- `tk anatomy WORD [--no-lifetimes] [--no-cache] [--json]`: per-side ledger of ANY word (seconds; the exact end replay of section 3 is ~40 s on #6030 and cached by content sha in `alignbuild/out/cache`, #6030's cache shipped in `alignbuild/data`): (1) R0 by class + law kappa (gapmap.components, EXACT); (2) skeleton/mains: X and Y main tax and park stops; (3) lifetimes by mechanism: markets / twins (hub ends) / other ends / signal and other births with enabling-stop cost and net lo..hi (ALIGNLAW attrib, bit-identical to attrib6030 on #6030); (4) hub ledger per octet frame (HUBCOST ledger as a function, reproduces O-net 117.90, cpy 233.51, NET 351.41, d8 67.55); (5) signal (H signal R0, owned staging, hub d8 column); (6) copies (52 pure crossing copies, COPY events). Classes are tiling-relative (fcls): valid for the octet class around #6030.
- Tests: `tests/alignbuild_test.py --fast` (7 s; in `regress --fast`: anatomy numbers above + a 2-step `tk rebuild` at exact kappa) and `--quick` (the full rebuild of #6030; in `regress --quick`, so run `regress.py --quick` via hq, ~70 min longer than before).

## BULKEVAL additions (Oct 28, BULKEVAL: `tk bulk` + CORPUS = the bulk-eval table (TOOLING, no kappa claim)
- `ext/CORPUS/`: `build_corpus.py` (idempotent; adds only new content shas) -> `words/<id>.json.gz` + `manifest.jsonl/.csv` (id, kind swarm|gen, source PR#/lane, pr, head, package, sha = sha256 of the decompressed JSON[:16] (= genpipe2.content_sha), file_sha, events, public, claimed_kappa from the PR's RESULT.json, origin, aliases). Swarm = every distinct `research/p104-*/WORD.json.gz` blob in `TKAUDIT/src/g.git` (read-only git) attributed to the PR whose head is the introducing commit (else the lowest PR containing it) + `toolkit/words` leftovers; gen = the curated `GEN_PATTERNS` list (best_px, best_lb, r104 variants, SKELGEN/OCTETGEN/FULLWORD/GENPIPE2/... outputs). To add words: append a path to `GEN_PATTERNS` (or drop WORD.json.gz into any dir; `tk bulk DIR` also accepts a plain directory) and re-run.
- Run: `tk bulk ext/CORPUS --out ext/CORPUS/results.jsonl --hq` (one hq job; 2 worker threads each driving child `tk` processes, so <=2 heavy at a time; ~16 s/word, dominated by `check --native`). Re-running skips shas whose steps are all OK (failed steps retry; `--force` redoes). Table: `results.summary.md` (top-N + all) and `results.summary.csv`; per-side columns R0_X/R0_Y/R0_O/R0_Hsig/R0_Hbot/R0_Hmid/R0_Htop (gapmap components of the word itself), dR0_ref, hubNET (anatomy; tiling-relative to #6030), native (ok / FREE-ok = legal only under TK_FREE_BOUNDS in the child / BAD), ship verdict, d_claim_ppm.
- Test: `tests/bulk_test.py [--fast]` (2-word corpus #6030 + #5551: all steps, exact kappa, gapmap self-gap 0, sorted summary, resume, --only/--force; `--fast` = no native, 6 s, in `regress --fast`; full ~40 s in `--quick`).

## RESIDTOOL additions (Oct 28, RESIDTOOL: joint signal+residual re-solve of fused relays (TOOLING + SEARCH)
Code `ext/RESIDTOOL/` (venv python -B, no env at import; heavy runs via `$TK_HQ`, THREADS=1).
- `jr.py WORD [edits] [--free R[:frames][:lo-hi]] [--free-cop] [--src-sym ..] [--only-frames ..] [--pairs-dropped] [--partial] [--stage-h] [--absorb-only]`: exact linear-algebra re-solve (SURGERY `rp.joint3` quotient solve mod 2^31-1 + SELF/SCALE candidates + dyadic-preferring column retries + own Newton loop + REALISED end-of-program repair `end_block_fix`; final truth `legal.check` + exact kappa) that frees BOTH signal and residual (x-content) events of a register set while the rest of the word is the fixed contract. Edits: `--end H[:F]`, `--drop-helper H`, `--kill-stop R:J`, `--rehost S:JS:F`, `--addstop R:F:T1`, `--strip-reads H`, `--drop-events T,..`, `--roundtrip R:LO-HI` (validation). STATUS is SOLVED_LEGAL / NO_SOLUTION_IN_SCOPE (first-order only, NOT a proof) / NO_CONVERGENCE / ENDER_NOT_CLEANABLE / CAPPED / ILLEGAL; a capped run is never a pass; a gain is written with `--out` only if kappa rises. No stop-search (iob2's new-stop candidates are not re-implemented).
- `stage1.py WORD h,..` (= `jr.clean_ender`): EXACT slot-level pure test whether an ended helper can regain row e_h (classes CLEAN / TWIN_LAW / NO_HOLDER / NO_SPAN). `spantest.py` (all-times necessary condition, `--strip`), `defect.py` (defect left by a pure deletion), `census.py` (exact chain-tax ceilings of fused-relay helpers; `census_r245g.txt`), `batch.py WORD CASES OUT.jsonl` (one jr.py subprocess per case line; cases_*.txt).
- Test: `python3 -B ext/RESIDTOOL/test_jr.py` (inline: null reproduces r245g kappa .0031283932032711292 exactly, L1 round trip re-derives 716's last two events at diff 0, xcap guard reports CAPPED) + the three hq checks it prints (free-only, L2 round trip with end_block_fix, SURGERY positive control `ctrl470.json --kill-stop 470:1` -> kappa .0031258115579118617).

## GENUPGRADE: lemma wires into the generators (TOOLING, all opt-in, defaults byte-identical)
- `tk gen2 --lawprune`: purex2 `--lawprune --dyfix`. On a purex2 failure the named enders are dropped (Exit Lemma L2: a non-0-born e_h holder; slot law L1: inconsistent joint solve) and the Z block is completed by the exact PB5 dyadic factoriser (`gen2/dyadic.py`, copy of planbuild `_decompose`) when the heuristic Euclid is stuck (det is 1, so it always exists). A config that solves is untouched (r104 content sha a691733502945e0a with the flag).
- `tk gen2 --gshape taxW`: rt.build greedy gain with the exact chain-tax marginal (Lemma 4) instead of 4 x births. Model R0 ties/loses (8823.6 vs 8821.8): kept as a knob only.
- `tk gen2 --stages ...,fold`: R-FOLD census + RULEMINE fold.py on the last word (0 sites on every gen2 word).
- `tk rebuild WORD --post fold,hoist`: constructor passes after the exact-kappa chain: R-FOLD (RULEMINE fold.py) then H-HOIST (`alignbuild/hoist.py`, NEW: automated gauge stop drop, the IOROOT2 hand prep.py edit). Each accepted only if LEGAL with kappa strictly up; writes OUT.post.json.gz. Rebuild(#6030)+fold+hoist = r245g kappa .0031283932032711292 exactly (EXACT on FULL_final, chain_242, f1049).
- `python -B alignbuild/hoist.py WORD OUT [--dry]`: H-HOIST alone (sites, legality, exact kappa per site). Bulk driver for paired off/on generator runs: `ext/GENUPGRADE/gubulk.py`.

## GEN3 additions (Oct 28, GENHUBS: `tk gen3` = gen2 + Y-route stage (GENERATOR scaffold + lever)
- `tk gen3 [--out DIR] [--stages gen2,yroute,signal,post,screens] [--from WORD] [--seed --gauge --order-dirs --d3-dirs] [--yroute-max N] [--yroute-tries N] [--yroute-census-only] [--post-passes fold,hoist] [--screens evretime,retime] [--list]` (genpipe3.py).
  Each stage reads the newest earlier stage word in --out (or --from WORD), writes OUT/<stage>.json.gz + an exact price line in OUT/stages.jsonl, never-lose.
  gen2 = `tk gen2 --lawprune` (routeb,ylate,order,purex); yroute = Y-MEET lever (ext/GENHUBS/ymeet.py census -> sites.py cases -> RESIDTOOL jr.py `--end L:F --addstop y:F:T1 --stage-h`,
  greedy via ymeet_apply.py direct construction + jr repair, kept only if LEGAL and kappa up); signal = ledger record only (gen2's route-B signal is built inside gen2; no splice tool exists);
  post = rebuild.post fold,hoist; screens = tk eval with TK_FREE_BOUNDS=1 in the child env only. Heavy stages (gen2, yroute with jr, screens): $TK_HQ.
- Helpers in ext/GENHUBS/: invoice.py (per-register R0 invoice by class), ymeet.py (Y-MEET census + model greedy), sites.py (jr cases), endprobe.py (Exit-Lemma
  ender-cleanability pre-test per site, ~0.4 s/site), ycensus.py (Y-only helper span census).
- Test: `python3 -B ext/DESIGNER/toolkit/tests/gen3_test.py` (~2 s, ALL PASS).

## PRIMGEN additions (Oct 28-29, PRIMGEN: gen3 stage `primgen` = Y-routing + fan-out landing (O1 relaxed), opt-in
- `tk gen3 --stages primgen[,yroute,signal,post,screens] [--seed --gauge --order-dirs] [--primgen-aware] [--primgen-dims 4,8|1,2,..,8]`: REPLACES the gen2 stage. gen2's route-B bottom,
  then FANLAND (ext/PRIMGEN/fanland.py): exact greedy over 'readers stop at the piece frame g (any dim) and read the piece there' vs gen2's landing copies, every candidate
  priced by a full landing re-solve (11 ms); realised by `PRIMGEN/primgen_rb.py` (route_b.main unchanged, model swapped in-process), then purex2 --xstops --lawprune --dyfix. ~12 s.
  Model delta = word delta EXACTLY (-68.170732 on b0). On gen2's o1 path the lever is purex's Q ender at equal tax and the two exclude each other per Y (Exit span):
  plain = -4.0e-6 kappa vs r104 (seed 0); `--primgen-aware` = 0 sites. Not a generator gain; kept as the O1-relaxed reference stage.
- Diagnostics: `PRIMGEN/lifet.py` (lifetime term L of THEORY 1.3, keep-stop convention), `PRIMGEN/o0census.py` (mains-as-relays / cancellation features a rect model cannot express:
  r245g X<-H 297, X peels 59, Y<-Y 116, Y<-X 110; gen2 41 / 0 / 0 / 12), `PRIMGEN/gmodel.py` (reader-group sinks at any dim; loses by R2), `PRIMGEN/pgbulk.py` (paired bulk, hq).
- SPAN stage (coordinator redirect): `tk gen3 --stages span [--from PRE_PUREX_WORD]` = PRIMGEN/spanrelay.py (X mains as relays with exact peels; census xrelay.py, holder test xr_holder.py, construction xrelay_apply.py) then purex2. Never-lose; 6-config sample 4 wins / 2 ties, mean +7.8e-7. Wall: 0-3 holder sites per gen2 word vs a ~-490 R0 model ceiling.
- Test: `python3 -B ext/DESIGNER/toolkit/tests/primgen_test.py` (~12 s, ALL PASS); gen3_test.py now expects 7 stages (gen2, primgen, span, yroute, signal, post, screens).

## RETAINOP additions (Oct 28, RETAINOP: R-RETAIN = the retained-operand stop drop of swarm PR #6167 (GENERATOR, EXACT, opt-in)
- `alignbuild/retain.py WORD OUT [--max N] [--skip ROOT:FRAME,..] [--census] [--dry]`: census (middle stop of s whose events are all reads; readers' extra stop must pay; stranded operands retained by INIT/COPY/ADD/CLEAR) + exact apply + IncrWord judge (LEGAL, kappa up), greedy with re-census. r245g -> W6167 bit-identical (model +1.116 = word delta); W6167: 0 sites.
- Wiring (flags only): `tk rebuild WORD --post fold,hoist,retain`; `tk gen3 --stages retain` (stage 'retain' after 'post', STAGES now 8; `--post-passes ...,retain` also works); `tk bulk CORPUS --steps retain --out F --hq` (opt-in step; words with accepted sites -> CORPUS/retain/).
- Test: `tests/retain_test.py` (3 s, ALL PASS). Tools: `ext/RETAINOP/{census.py,widescan.py}`. Backups *.bak-retainop.

## SIGGEN additions (Oct 29, SIGGEN: gen3 SIGNAL stage (contract + floor + exact per-root re-solve), opt-in
- Code `ext/SIGGEN/` (venv python -B, no env at import): `contract.py WORD [--floor] [--out C.json]` (generic signal I/O contract + SIGFLOOR floor generalised; r245g/W6167 gap 5.27 = SIGFLOOR),
  `sgb.py` (SIGPIN sigb + `--couriers --f0 --relocate --exclude --free-bounds`), `siggen.py IN OUT` (feeds then reads per moving root family, never-lose), `feedplan.py WORD [--residual-only]`
  (CP-SAT restricted feed-cover price; NOT a lower bound), `acct.py WORD` (per-register direct-contact signal invoice: feed climbs / pure couriers / reader stops).
- Wiring: `tk gen3 --stages signal --siggen [--from WORD]` (genpipe3.py, backup .bak-siggen; default signal stage unchanged). Test: `tests/siggen_test.py` (6 s, ALL PASS).
- Results: W6167 re-derived at its exact kappa (16/16 steps); p1oF / m12 / g2best: 0 gain (feeds re-derived identically, no courier deletable) -- from-scratch signal is at the
  optimum of its contract; the 1.5-2k is skeleton (no whole-root feed carriers, c_k distribution through the mirrored top). Contract JSON format for PRIMGEN: the original lane notes (not shipped)
