# Twisted helper exits: no target-to-helper feedback gain at any fixed 3+3 or five-register exit, plus an every-word contamination-charge lemma

**Scoped proof plus finite certificates. No new supplier, no κ effect, no selected-frontier change.**

1. **Lemma (every word; written proof in [PROOF.md](PROOF.md)).**
   * *Setting:* `H` helpers and `Y` targets, dirty inputs, unit-cost directed
     XORs. `P = P_{H,Y}` is the restricted (no target→helper) group, and it
     contains every exit `[[T,0],[K,I]]` (identity target block). An exit is
     *twisted* when `T != I`; `T = I` exits are the untwisted shears.
   * *Construction:* for any word `w` of length `L` whose product `M` lies in
     `P`, an explicit tracking construction outputs a restricted word computing
     exactly `M`. Its length is `L - f_v + c(w)`.
     * `f_v` counts the feedback gates the construction absorbs.
     * `c(w)` is an explicit contamination charge (see below).
     * The tracked state is a contamination matrix `Z` plus a virtual
       register labelling.
   * *The charge:*
     * A nonsingular contaminated read `y_i ^= h_a` (`Z[a,i] = 0`, with
       `Z_a`, `Z[:,i]` not both zero) costs `|Z_a| + |Z[:,i]|` extra.
     * A singular read (`Z[a,i] = 1`) costs `|Z_a| + |Z[:,i]| - 2` extra.
     * A read with `Z_a = 0` and `Z[:,i] = 0` is *clean* and costs nothing
       extra. "Non-clean" means contaminated or singular.
     * Restoring the final labelling costs 3 per swap.
   * *No invertible-target-block hypothesis.* A frame read off the current matrix alone
     would need an invertible target block, which fails after `h ^= y; y ^= h`.
     The singular-read step handles this by exchanging the roles of one helper
     and one target.
   * *Corollaries:*
     * If every read is clean, deleting all feedback gates gives a restricted
       word: `d_P(M) <= L - f`.
     * Any strict feedback advantage needs every minimum unrestricted word to
       have `c(w) >= f_v + 1 >= 2`, so it must contain a non-clean
       (contaminated or singular) read. This is only a necessary condition:
       35 minimum words below already satisfy it at exits with no advantage.
     * *Positive control:* feedback does help at some non-exit elements of
       `P`, so the exit condition (target block `D = I`) is load-bearing. In
       the five-register model exactly 120 elements of `P` have
       `d_full = d_P - 1`: 60 in `P_{2,3}` and 60 in `P_{3,2}`, none an exit
       (all have `D != I`); `P_{1,4}` and `P_{4,1}` have none. Corollary 2
       holds on a minimum word of each (`f_v >= 1`, a non-clean read and
       `c >= f_v + 1`); `numpy_crosscheck.py` asserts all of this.
2. **3+3 decision (finite certificate).**
   * All **85,504** exits `[[T,0],[K,I_3]]` with `T in GL_3(F2) \ {I}` were
     checked. There is **no strict feedback advantage**: `d_full = d_P` for
     every exit.
   * The common minimum has distribution
     `1:6, 2:96, 3:744, 4:3,594, 5:11,463, 6:23,948, 7:29,259, 8:15,438, 9:956`
     (maximum 9).
   * The 512 `T = I` shears are PR1306's census. They are cited, not
     re-claimed; the run agrees with it (0 advantage).
3. **Five-register shapes (finite certificate).** There is no strict advantage
   for any of the **333,552** twisted exits in the new shapes:

   | Shape | Twisted exits | Maximum minimum (twisted) | Settled `T = I` shears also run |
   |---|---:|---:|---:|
   | 2+3 | 320 | 6 | 64 (PR1306) |
   | 3+2 | 10,688 | 8 | 64 (PR1306) |
   | 4+1 | 322,544 | 10 | 16 (PR2567 `Y = 1` lemma) |

   The run also covers the 16 already-settled 1+4 exits (all `T = I`, PR2567),
   so 333,712 exits in total; it agrees with the settled cases (0 advantage).

**Decision informed.** PR1868 question 3 asks whether target-to-helper
feedback helps a replacement helper contract at fixed twisted exits.

* *Closed here:* the fixed-exit question in PR1306's model for the 3+3 shape
  (the 3x3 twisted case PR2494 left open) and for the twisted five-register
  shapes 2+3, 3+2 and 4+1. With PR2494's `H + Y <= 4` census, this covers
  every twisted shape with at most five registers.
* *Not closed:* the twisted 2+4, 4+2 and 5+1 shapes and anything larger; the
  actual seed02 D boundary (at least 3 helpers and 99 targets), where only
  Corollary 2's necessary condition applies; the C-absorption pricing in
  question 3; and the twisted-versus-restored exit comparison.
* There is no κ effect either way, because the bit side does not bind
  (`research/r439-twisted-star-absorption-seed02`).
* *Context only:* open PR #2721 (geckods) argues the framed transfer does not
  use the no-target-feedback clause. This package is distinct and does not
  depend on it; if that clause is relaxed, this result says feedback buys
  nothing at fixed exits in these shapes.

## What is new

* Predecessors cover only these cases:
  * ywz65's `research/bit-twisted-feedback-four-registers` (PR2494):
    `H + Y <= 4`.
  * PR1306 / PR1557 / PR1706 and rtyu193-rgb's
    `bit-zero-frame-feedback-to-8-registers`: untwisted `T = I` shears, plus an
    `H = 1` / `Y = 1` lemma.
* Why now: PR1868 question 3 explicitly asked for the 3x3 case and PR2494
  left it open; this package closes it with two independent exact methods.
  The lemma explains the result structurally and certifies all but 35 of the
  333,712 greedy five-register minimum words directly; the five-register
  census is a 30-second byproduct of the same run. (PR2494's "new lead"
  condition asks for a favourable candidate word; none is claimed here.)
* New here:
  * the every-word charge lemma (including singular steps);
  * the twisted 3+3 domain;
  * the twisted five-register shapes 2+3, 3+2 and 4+1.
* PR1306's substitution lemma is a different statement and is not reused.

## Method and independence

* **3+3, primary (stdlib, `independent33.py`).**
  * Encoding: column-major.
  * Restricted minima: right-multiplication meet-in-the-middle with restricted
    balls `B^P_6 x B^P_3`. This is exact up to 9, and every exit has a word of
    length at most 9.
  * Unrestricted minima: `B_5 x B_3` in `GL_6(F2)`. This is exact up to 8, so
    `d_full >= 9 = d_P` for the 956 exits with `d_P = 9`.
  * Orbit reduction: helper/target relabelling (S3 x S3), 3,478 classes.
* **3+3, second method (`numpy_crosscheck.py`, numpy==2.5.4).**
  * Restricted minima: dense BFS over all 14,450,688 elements of `P_{3,3}`.
  * Unrestricted minima: row-major left multiplication against `B_4 x B_4`.
  * Its own orbit canonicalisation also finds 3,478 classes.
  * Both methods report the same class count, the same histograms and zero
    strict advantages. Per-class results are not cross-joined between the
    two scripts. `independent33.py` asserts that its restricted balls stay in
    `P_{3,3}`, so it stands alone even though `d_full = d_P`.
* **Five registers.** Dense BFS over all 2^25 matrices (`GL_5`: 9,999,360
  elements) and over each parabolic.
* **Corroborating the lemma.** The construction is run on one greedy
  (first-gate) minimum unrestricted word per five-register exit (333,712
  words). In 35 of the 4+1 words it meets a non-clean read, and each of those
  has `c = f_v + 1`. So the lemma is not tight on them: it outputs a restricted
  word of length `L + 1`, and those 35 exits are decided by the census
  (`d_P = d_full = L`), not by the lemma. Which words are non-clean depends on
  the greedy choice. `verify.py`'s `lemma_words = 15,028` counts the words
  ending in `P` (6,628 + 8,400); the 2,800 free words check only the per-gate
  invariant.
* All arithmetic is exact over F2. The 3+3 and five-register minima are global
  minima: BFS uses unit weights and runs to exhaustion, and MITM splits every
  word of length at most `a + b` at position `a`.

## Reproduce

From the repository root (Python 3.12; the registered replay installs only the pinned numpy):

```sh
python3.12 scripts/research_package.py --package research/bit-twisted-feedback-contamination-lemma --install-deps
```

Expected lines:

* `PASS_TWISTED_FEEDBACK_CONTAMINATION_LEMMA exits33=86016 twisted=85504 classes=3478 strict_feedback_advantage=0 max_restricted_min=9 lemma_words=15028 controls=5`
  from `verify.py` (stdlib, about 40 s).
* `PASS_TWISTED_FEEDBACK_NUMPY_CROSSCHECK twisted33=85504 classes=3478 five_register_exits=333712 twisted5=333552 strict_feedback_advantage=0 lemma_words=333712 nonexit_advantage_controls=120`
  from `numpy_crosscheck.py` (about 35 s, under 0.5 GB RSS).

Run locally with system Python 3.14 (stdlib), and numpy 2.5.4 in a scratch venv.

**Negative controls** (in `verify.py`; each must fail in the stated way):

1. `h^=y; y^=h` makes the target block zero, so no frame can be read off the
   matrix there, yet the construction covers the double-swap word with two
   singular reads.
2. Naively deleting feedback from `h^=y0; y1^=h; h^=y0` gives the wrong map.
3. The charge is necessary on that word: `L - f = 1 < d_P = 2`.
4. A forged extra gate fails replay.
5. A self XOR is rejected.

## Scope, inherited assumptions and unresolved obligations

* *Model:* PR1306's algebraic model of fixed register labels, dirty inputs and
  unit-cost XORs. There are no free permutations, COPY/ERASE, frames or extra
  registers.
* *What is compared:* fixed exits `(T,K)`. Twisted and restored exits are not
  interchangeable.
* *What remains open:* physical continuation and absorption of `T`, R439
  substitution, chronology across nonzero frames, hosting, precision/tape,
  all-size compilation and native supplier replay. There is no general
  no-feedback theorem beyond the lemma's statement, and no frontier change.
* *Review:* the lemma has no formal (Lean) proof. Review was by AI passes in
  the same loop only; there was no human review.

## Open next questions

1. **Removing a non-clean read at zero net cost.** `c <= f_v` already fails
   for some minimum words: the 35 greedy 4+1 words have `c = f_v + 1`, yet
   their exits have equal-length restricted words. Is there a local rewriting
   rule that turns a minimum word with a non-clean read into a restricted
   word of the same length, at least for one-target (`Y = 1`) twisted exits
   at every `H`? That would extend the decision beyond five registers.
   Such a rule must use `D = I`: no zero-cost rule exists on all of `P`,
   because 120 non-exit five-register elements have a strict feedback gain.
   * *First step:* for each of the 35 words, align it with a restricted
     minimum word of the same length and extract the local rewrite.
   * *Blocked by:* no candidate rule yet; the census only certifies lengths.
2. **Seven registers.** Does a strict advantage first appear at seven
   registers (3+4, 4+3)? Only a concrete word would reopen the PR1868 feedback
   question. A larger negative census alone is not justified by this result.

The structured versions are in [TASK.json](TASK.json).

## Sources and credit

* *Pins:* base commit `20ecf2891d80b5acf18d980b2164fb44ea7faa90` (priority
  revision 6). Exact Git blobs and SHA-256 pins are in
  [SOURCES.json](SOURCES.json):
  * four-register README `9ce21f23…`;
  * to-8 README `a67a6b18…`;
  * r439-twisted-star-absorption-seed02 README `ddd5b484…`;
  * the selected record `bb2eaa58…`, which is PR1094 and unchanged.
* *Predecessor PRs (authors and heads checked with `gh`):*
  * **ywz65** (PR2494, head `80fea4ae`): four-register twisted census.
  * **Sagar Thakrar** (PR1868, head `6b222d01`): twisted-helper contract and
    question 3.
  * **@commdata2338** (PR1306, head `0d4c0069`): model, substitution lemma,
    MITM and the 3x3 `T = I` census.
  * **Hanson Sun (@bbMisk)** (PR1557, head `15e0987e`): 3x4 census.
  * **rtyu193-rgb** (PR1706, head `dc6a2599`): 4x4 census; and PR2567 (head
    `d28ac97c`), the to-8 package with the `H = 1` / `Y = 1` lemma and
    duality.
* *No reuse:* no predecessor code is imported or changed.

Prepared by Sagar Thakrar (thakrarsagar) with substantial AI assistance from Claude (Anthropic, Claude Opus 5.5). Apache-2.0.
