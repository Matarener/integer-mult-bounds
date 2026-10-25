# No cost-20 word for the mixed S4 tuple on four or five roles

**Scoped finite exclusion (negative result); no κ, supplier or native
claim.** The setting is the formal `F2[S4]` register model of PR2583 and
PR2998, with adjacent prices `(s1,s2,s3) = (2,1,2)`, free `GL_r(F2)`, all
roles dirty and spectators restored. Here no circuit of paid cost at most 20
realizes

    diag([2143], [3142], [4231], [2143])        on exactly 4 roles,
    diag([2143], [3142], [4231], [2143], 1)     on 5 roles (one dirty spectator).

An explicit direct word of cost `21 = 4+5+8+4` realizes the tuple role by
role and leaves a spectator untouched. The per-target costs are the direct
distances of PR2583/PR2998, and `verify.py` rechecks the word exactly. So
**the four-role and five-role optima are both exactly 21**. The static
coordinate-cut LP, which prices each letter by its cut charges, gives 20 for
every r (PR2998), so it is not attained on at most five roles. In decision
terms, this mixed tuple has **no joint saving over separate words at width
<= 5**: only two or more dirty spectators could still realize the cut value
20. Six or more roles were not searched, so this is **not** a theorem that the
optimum is 21 with arbitrary workspace.

## What is inherited and what is new

Inherited, and restated with proof in [PROOF.md](PROOF.md) for completeness:

* **Normal form (section 1).** Free scalar maps are pushed to one end by
  conjugation, and augmentation forces the trailing scalar map to be `I`.
  This is Ross Richardson's PR1989 argument, reused in PR2583.
* **Count consequence (section 4).** PR2583 proves
  `cost >= sum_i L(t_i)` with `L = inv + c1 + c3`, for any number of dirty
  roles, which gives 20 here. PR2998's open question already observes that a
  cost-20 word would have exactly twelve paid letters and eight exterior
  letters, and PR2998 and PR3408 both propose examining that equality.
  Section 4 spells out the resulting split: label counts exactly `(4,4,4)`,
  with the inv, c1 and c3 cuts all tight.

New here:

* **The window lemma, used for pruning (section 3).** For any cut potential
  and any prefix `P_j` of a word with label counts n, it gives
  `Phi(T) - c.(n-m_j) <= phi(P_j) <= c.m_j`. When the cut is tight
  (`c.n = Phi(T)`), the potential is fixed exactly at every prefix.
* **The exhaustive target-end search and the r = 4 and r = 5 exclusions
  (section 5).** Peeling letters off T, over every binary rank-one idempotent
  at every step, the windows prune hard. The whole r = 4 tree has 1,839,762
  window-feasible nodes and dies at depth 8 with zero words. The r = 5 tree,
  searched over 7 symmetry-orbit representatives of the first peeled (last)
  letter, has 240,056 nodes and also dies at depth 8.
* **Three-target sub-tuple values (section 6).** Exact LPs over all `2^24`
  regular coordinate cuts give LP 15 for `(4231,2143,2143)` and LP 16 for
  `(2143,3142,4231)`. Both sub-tuples cost their direct values 16 and 17 on
  three roles, by transfer from the four-role result and by direct r = 3
  searches. So `(4231,2143,2143)` already shows an integer gap between the
  cut LP and the circuit optimum on three roles. No claim is made that this
  is the first such gap in the model. Ross Richardson's two-cut theorem
  gives exact sum tariffs, with arbitrary dirty roles, for every tuple drawn
  from 20 of the 24 targets; it excludes 2143, 2413, 3142 and 3412. Both
  gapped sub-tuples, and the full tuple, contain excluded targets.

PR2998 (Arham Tahir) and PR3408 (Nick Petalas) showed that coordinate cuts,
and natural/edge subspace cuts, stop at 20; neither searched for words. This
package adds no new cut class.

## Reproduce

Python 3.12+ and the standard library suffice. From the repository root:

```sh
python3 -I -B research/s4-mixed-tuple-tight-word-search/verify.py
```

Expected last line:

```
PASS_S4_MIXED_TUPLE_WINDOW_SEARCH no cost-20 word on r=4 or r=5 roles (recorded searches); r=6+ not searched
```

The default replay takes about two minutes. It runs five checks:

1. It recomputes the count consequence from exact cut values.
2. It builds an explicit cost-21 direct word (cheapest word per target by
   Dijkstra on S4: 4, 5 and 8), multiplies it in exact frozenset `F2[S4]`
   arithmetic and compares it with T.
3. It replays the separately written explicit-matrix search
   (`independent.py`): both whole r = 3 sub-tuple trees, the first three
   r = 4 depths (56, 1904, 28562) and the r = 5 depth-1 count (56). Each is
   compared with the recorded primary runs.
4. It checks a two-role control, `diag([4231],[2143])` at counts (3,2,2).
   The unpruned frozenset brute force counts 146 words, and the pruned
   primary engine recorded 146. `independent.py` leaves 150 full-depth
   window survivors, of which exactly 146 equal T in exact arithmetic, and
   104 of those 146 words use a mixing idempotent. So pruning lost no
   solution on an instance where mixing gates matter.
5. It runs scalar controls: 4312 at counts (1,3,1) has one word, and 4231 at
   (1,3,1) has none, as PR2998's precedence argument requires.

**The default replay does not re-derive the exclusion itself** (depths 4 to 8
of the r = 4 and r = 5 trees); its PASS line says "(recorded searches)".
Only `verify.py --full` does. It needs g++ with OpenMP, recompiles
`search.cpp` and `indep.cpp`, replays the complete r = 4 and r = 5 searches
in both engines, and replays the sub-tuple cut LPs
(`cutlp.cpp` and `lp.py`, about 10 MB and seconds). Everything is compared
with RESULT.json. `verify.py --self-test` checks that perturbed recorded
values are rejected.

`independent.py` reports full-depth *window survivors*, an upper bound on
words, because it does not check the endpoint. Zero survivors means zero
words; `verify.py` rechecks survivors exactly where it counts words.

## Evidence and its limits

* **Primary engine (`search.cpp`).** Group-algebra elements are 24-bit masks.
  Gates are applied by right multiplication, and the windows are computed in
  the natural and ordered-pair modules. Runs:
  * r = 4: all 360 first peeled letters, node counts
    `56, 1904, 28562, 207168, 571536, 648720, 381816, 0`. This took 187 s
    on 3 threads.
  * r = 5: `7, 238, 3571, 25940, 72256, 85622, 52422, 0`, over the
    representatives of the 56 depth-1 survivors. This took about 3 minutes.
* **Second engine (`indep.cpp`).** It multiplies explicit F2 matrices in the
  natural and ordered-pair representations and uses no group-algebra masks.
  It reproduces both trees node-for-node: all 360 first letters at r = 4,
  and the same 7 representatives at r = 5 (same gate indexing). So each
  exclusion rests on two engines in this package; see RESULT.json.
* **Positive control at r = 4.** Replacing 4231 by 4312 gives a tuple whose
  direct words cost 20 with counts (4,4,4), and the same engine finds a
  cost-20 word (RESULT.json `controls`). The word it prints depends on thread
  order and is block-diagonal (`u = v = e_i` in every gate), that is, a
  direct word. This control therefore shows only that the windows keep direct
  words at full scale. The control that exercises mixing gates is the r = 2
  one above.
* The r = 5 symmetry reduction uses `GL_2(F2)` on the two `2143` roles
  together with `w0`-conjugation, which swaps s1 and s3. PROOF.md section 5
  shows that it is sound. The r = 4 run uses no symmetry.
* **Review.** AI review passes in the same loop, not human review, re-ran
  parts of this. One rebuilt `search.cpp` and reproduced the r = 4 RESULT
  line. One ran the in-package `indep.cpp` on the r = 5 representatives
  and got the same node counts. Another wrote its own engine from the model,
  after reading these sources, so it is not a blind rewrite. That engine reproduced the r = 4 tree
  and the r = 5 representative tree node-for-node, recomputed the 7 orbits of
  the 56 r = 5 depth-1 survivors (sizes 2, 6, 6, 6, 12, 12, 12), and ran
  left-end peeling at r = 4: a different tree of 1,727,645 nodes that also
  dies at depth 8 with zero words. That engine is not part of this package.

Local environment: CPython 3.14.4 and g++ 15.2.0 (Ubuntu, x86_64). The
default, `--self-test` and `--full` replays and `scripts/research_package.py
--check-only` pass. `--full`, including the r = 5
second-engine run, took 16.5 minutes on a shared 4-CPU machine.
The 3.12-pinned registered hook was not run, because no 3.12 interpreter was
available. Its two commands are the default and `--self-test` replays above.

Assumptions inherited from predecessors: the model of PR2583/PR2998 and the
cut-rank lemma of PR1941/PR1966/PR1989. The finite search was not
formally verified.

Unresolved obligations:

* the case of six or more roles (arbitrary workspace);
* a uniform written invariant explaining why the window tree dies;
* any native realization, routing or ownership invoice, bit supplier or κ.

## Open next questions

1. **Does a second spectator (r >= 6) allow cost 20?** Coordinate cuts allow
   20 for every r, so only extra workspace can still realize it. A yes would
   be the first known restored-spectator saving in this weighted model.
   First step: widen `search.cpp`'s block rows to 64 bits (the inv block has 6r = 36
   columns at r = 6, so the engine refuses r > 5), then run it at r = 6
   (6048 gates per step) with the first-peeled-letter symmetry, which at
   r = 6 could be enlarged by `GL_2(F2)` on the two spectator roles. For scale
   only: the r = 4 tree has about 33K nodes per surviving first peeled letter and the
   r = 5 tree about 34K per representative. The r = 6 cost is unknown (four
   times as many gates per step, wider blocks, possibly a larger tree), so
   any runtime estimate is a rough guess. This needs a separately budgeted
   run, with the five-point expansion decision posted in Discussion #2570
   first.
2. **Is there a uniform stronger-than-cut obstruction?** An all-r argument
   would give the arbitrary-workspace 21 theorem that PR2998 left open. First
   step: find which window, and which block, kills every depth-8 extension of
   the 381,816 depth-7 survivors at r = 4. Then try to state that window as a
   chronological rank inequality valid for every r.

## Sources and credit

Base: canonical main `20ecf2891d80b5acf18d980b2164fb44ea7faa90`, priority
revision 6. [SOURCES.json](SOURCES.json) pins the inputs with git blobs and
SHA256. Claim and canonical thread:
[Discussion #2570](https://github.com/CrocSwap/integer-mult-bounds/discussions/2570#discussioncomment-19027763).
The task did not come from a #1166 handoff.

Credit:

* Arham Tahir (Arham-Tahir64): PR2998, head `3aa400ed59`,
  `research/s4-two-premium-cut-envelope`. Supplied the sharp coordinate-cut
  value 20, the attaining potential `f_0`, the scalar precedence argument,
  this open question, and the twelve-paid / eight-exterior equality
  observation that section 4 makes explicit.
* Nick Petalas (petalas): PR2583, head `715f558e04`, the two-register model,
  the bound `cost >= sum_i L(t_i)` with `L = inv + c1 + c3`, and the two-role
  weighted census (all 47 open pairs additive on two roles); PR3408, head
  `8ed0087a75`, the subspace-cut boundary and the same equality route.
* Ross Richardson (RossRichardson): PR1966 and PR1989, the normal form
  (PR1989 proof); the `s4-permutation-cut-cone` archive (Discussion #2570,
  retained under PR2998's `predecessor/`), whose two-cut theorem gives exact
  sum tariffs for tuples from 20 of the 24 targets, and whose enumeration of
  the complementary cuts of the regular S4-set covers the same cut family
  as the `2^24`-cut LP here.
* Adam Gall: PR1941, the cut-rank lemma.
* David Arias (DavidAriasC): PR2738, head `833b8e05bb`,
  `research/coxeter-root-tariff`: exact Coxeter tariffs with arbitrary dirty
  workspace for class-dependent prices, and the unequal-conjugate-price
  question that the (2,1,2) line continues.

Related work, no code imported: PR2577 (starship-s), the one-premium
adjacent-swap tariff that PR2998 cites as complementary; and the earlier
exhaustive word searches in the same dirty-role `F2[S4]` model, PR1720,
PR1734, PR1749 and PR1801 (opened by 1337isnot1337; packages
`s4-two-target-cycle-seed6e525`, `s4-double-transposition-seedb270`,
`s4-noncommuting-threecycle-r4-seeda27b` and
`s4-mixed-v4-double-transposition-seed0cdbb4`).

Prepared by Sagar Thakrar (thakrarsagar) with substantial AI assistance from
Claude (Anthropic, Claude Opus 5.5). All engines and checks were written in
the same AI-assisted session. They are several implementations by one
author, not independent human review. Apache-2.0.
