# Staged helpers 644/660: native entrance residual under a separate kernel

**Finite native/interface audit; no new kappa, supplier admission or frontier change.**

PR3605 lowers helpers 644 and 660 from width 8 to width 7 by letting them enter
at `span(429,30)` instead of `span(30)`. Its consumers reuse those STAGED
words: #3624, #3626, #3630, #3633 and #3638. PR3687 checked the words as exact
free-operator identities. Its first open question asks whether the **native
phases** of the paired `span(429,30)` entrance hold, checked without the `bw_*`
lineage code. This package answers that question for both providers and both
orientations. The answer is **yes**.

- **The width-7 residual is exact.** Operators are written in product order,
  with the rightmost acting first. The emitted recipe for
  `span(429,30) -> FULL` satisfies `L · F_7 · R = T_FULL · T_E^-1` on all 512
  Gaussian columns, including global phase. The wrapped form
  `L^-1 · T_FULL · T_E^-1 · R^-1 = F_7` and the inverse-transpose form follow
  from it, and both are evaluated as well. The check uses Sagar Thakrar's
  separately written kernel
  `research/frontier1094-recipes-exact-seed76/clifford.py`, which imports no
  repository code. No `bw_*` module takes part in it.
- **The emitted program uses exactly this recipe for 644 and 660.** The
  unchanged producer emits one `pre`/`post` residual wrapper pair at frame
  `[429,30]`, with no terminal field. There is one ordinary `new_to_old` exit
  adapter at FULL and no private buffer, in both orientations. The climbs are
  `[2,1,2,1,1]` for 644 and `[2,2,1,1,1]` for 660. Both sum to 7, and each of
  the ten distinct climb recipes also passes the separate kernel. All 17 direct
  scalar clocks per helper match the source word, including the 8 FULL-frame
  cleanup gates.
- **Only this residual changes.** As a single-change control, the parent PR3133
  words go through the same producer. There, 644/660 enter at `span(30)` with
  width 8, and their first climb is 3 instead of 2. Every climb ends at the
  same frame as in the staged words; only the first climb's start differs.
  Across all 408 helpers, only 644 and 660 change their entrance/terminal pair.
  The serialized residual recipes go from 56 to 57, and the new one is
  `([429,30], FULL)`. Counting the unwrapped cold class `([], FULL)`, which has
  no recipe, the entrance/terminal pair classes go from 57 to 58.

**The retimed and delayed consumer words keep this entrance residual.** Two
later word families move the releases that read 644/660. These are the
RETIMED644-660 words of #3642, which #3653 reuses byte for byte, and the DELAYED
words of #3682. All four consumer words (two families, two providers) go
through the same producer and binding, with PR3605's STAGED words as the
single-change control. The answer is again **yes**:

- 644 and 660 still enter at `[429,30]` with key `137`. The width-7 recipe
  passes the separate kernel on all 512 columns. Each reconstructed
  residual-adapter file equals the STAGED one, so all 57 recipes and 72 warp
  records are unchanged. No helper among the 408 changes its entrance/terminal
  pair.
- In both orientations, 644/660 keep the STAGED emitted structure: one wrapper
  pair at `[429,30]`, one `new_to_old` exit adapter at FULL, no private buffer,
  and the STAGED climb frames and ranks. Apart from the clocks, one thing
  changes: the moved release that reads each helper (`640 += 2*644`,
  `656 -= 660`) now runs at `Q` instead of `[429,30]`. All 17 direct scalar
  clocks and frames per helper match the consumer word. Binding the STAGED word to a
  consumer program is rejected at the scalar/climb clock check. So the binding
  sees the retiming rather than passing for any word.
- The first climb `span(429,30) -> Q` moves from B1045 to B592 (644) and from
  B1085 to B642 (660) in RETIMED. In DELAYED it moves from B1045 to B1043 and
  from B1085 to B1084. Here `Q` is `span(423,65,20,10)` for 644 and
  `span(427,96,24,6)` for 660.
- Only the release donors 640 and 656 change their climbs. Each replaces climbs
  `1,2` by one direct climb `span(30) -> Q` of rank 3, as #3642 and #3682
  describe (H1+H2 -> H3), and both merged climb recipes pass the separate
  kernel.
- Each regenerated `LOCAL-CHECKS.json`, in LF form, equals the receipt that the
  producing PR recorded from its own native run: `11743473…` (#3642) and
  `7ff1aabb…` (#3682). So the programs checked here are the ones those runs
  emitted.

Expected verifier line:

```text
PASS_STAGED_644_660_NATIVE_BINDING providers=2 helpers=644,660 entrance=span(429,30) terminal=FULL residual_width=7 parent_width=8 shared_key=137 climb_recipes=10 recipes=56->57 controls=7x2 single_change=2 both_orientations no_new_kappa consumers=RETIMED644-660,DELAYED consumer_width=7 consumer_key=137 consumer_pair_changes=0 recorded_receipts=4 merged_donor_climbs=2
```

## What the check does

For entrance `E` and terminal `U`, the native residual is `S(E,U) = T_U T_E^-1`.
The source compiler factors it as `S = L F_w R`, where `F_w` is the coordinate
Fourier primitive on the first `w` axes, and `w = dim U - dim E`. Here
`E = [429,30]`, `U = FULL` and `w = 7`; the other two axes are spectators.

1. The verifier runs the pinned `bw_transport.py` and `bw_emit.py` (byte-identical
   to the copies used by the #2979 group audits) on PR3605's two STAGED words.
   It then binds every emitted event of helpers 644/660 to the source word. It
   checks the wrapper entrance, the climb chain from `[429,30]` to FULL, the one
   exit adapter, the event order (wrapper, climbs, exit, cleanup, wrapper) and
   every direct scalar clock.
2. It rebuilds the serialized residual-adapter file with the source compiler,
   and the separate kernel then checks the shared recipe (key `137`) and every
   climb recipe.
3. It runs the parent PR3133 words through the same producer as the
   single-change control above, and checks the parent's width-8 recipe too.
4. It rejects seven residual controls per provider. Three fail at the
   all-column operator check: a global-phase change, the parent's right wrapper
   substituted, and the same-dimension wrong plane `[429,18]`. Four fail at the
   width check: no entrance, the contained line `[429]`, the old entrance `[30]`
   and the parent recipe at the new entrance.
5. It runs each consumer word through the same producer and compares it with
   the STAGED word of the same provider. It requires the recorded `LOCAL-CHECKS`
   receipt, an identical residual-adapter file and identical entrance/terminal
   pairs. For 644/660 it requires the full source-to-emission binding against
   the consumer word, the STAGED recipe key with the kernel check, and the
   STAGED climb frames. It also requires that only the
   donors' climb chains change, each by one merged climb that the kernel
   checks. Binding the STAGED word to the consumer program must be rejected.

The words differ from the STAGED words only where #3642 and #3682 say. This
is a local observation from diffing the words; `verify.py` does not compute it.

- **RETIMED** swaps B591/B592 and B641/B642, and raises each moved release
  `640 += 2*644` and `656 -= 660` to `Q`. It regenerates the cleanup and the
  reported local profile.
- **DELAYED** moves the same two releases to just before old B1045 and B1085,
  at `Q`. It shifts the B cut (and nothing else) of 38 of the 72 warp entries
  by one or two, and regenerates the cleanup and the reported local profile.

`LOCAL-CHECKS.json` comes from `bw_emit.py`, which writes it with `write_text`
and so uses CRLF line ends on Windows. The verifier therefore digests its LF
form. The first two commits recorded the CRLF digest, which a Linux or macOS
replay would not reproduce. The LF digests are the ones that equal the
consumers' recorded receipts.

`test_verify.py` adds corruptions that must fail through the same code paths.
These include a missing `post` wrapper, a wrong wrapper frame, a restored-helper
terminal field, a deleted or mis-ranked climb, and an entry adapter in place of
the exit adapter. They also cover a moved exit adapter, an added private
buffer, a sign-flipped scalar and the wrong orientation. Word, recipe and
source-pin corruptions are covered as well, including a corrupted DELAYED copy.
For the RETIMED base word, the tests check the recorded receipt and that the
RETIMED word does not bind the STAGED program. They then require each consumer
comparison to fail at its own check: a changed STAGED recipe, 644's entrance
swapped with donor 640's (which keeps the recipe set), a deleted non-donor
climb, and a donor that stops at `[429,30]`. One observation came from a wrong
test expectation. `[30,429]`, the same two vectors in the other order, passes
the identity, while `[435,30]`, another basis of the same plane, fails. So the
frame operator depends on the stored basis rather than only on the plane. The
wrong-entrance test therefore uses a different plane, `[430,30]`.

## Sources

The base is canonical main `20ecf2891d80b5acf18d980b2164fb44ea7faa90`, priority
revision 6 (κ = `0.001672660197076918`). [SOURCES.json](SOURCES.json) pins every
input by Git blob and SHA-256.

- **Staged words.** `inputs/STAGED644-660-{base,extra}.json.gz` are byte copies
  of `research/staged-644-660-width-reduction/STAGED644-660-*.json.gz` at PR3605
  head `3efbb5de06a49ffeea6684482f2d3fe48cdca3fb`. The repository's `head:` pin
  must name the live path, so these copies are pinned as provenance rows under
  their original path. The verifier checks the copies' bytes against those pins.
  The hashes also match PR3605's `ARTIFACTS.json`.
- **Consumer words.** These are pinned in the same way, each at its PR head
  under its original path. The verifier requires every pin of a copy to carry
  the same SHA-256.
  - `inputs/RETIMED644-660-{base,extra}.json.gz` are byte copies of
    `research/staged-release-retiming-t530/local-audit/words/RETIMED644-660-*.json.gz`
    at #3642 head `6568db75adbb61437190545f6fef1534c70e91e5`. They are also
    byte copies of
    `research/retimed-t488-composition/local-audit/words/RETIMED644-660-*.json.gz`
    at #3653 head `607a09ff441c79b215a8127a81f4cc70021d0d9b`.
  - `inputs/DELAYED-{base,extra}.json.gz` are byte copies of
    `research/staged-donor-release/lead1-words/DELAYED-*.json.gz` at #3682 head
    `431e6c6023ef352c41696469de7fb614cd4ded8c`.
- **Recorded consumer receipts.** These are #3642's
  `local-audit/receipts/native-{base,extra}/native/local/LOCAL-CHECKS.json` and
  #3682's `evidence/native-{base,extra}/LOCAL-CHECKS.json`, pinned at the same
  heads. The verifier compares each regenerated receipt with the pinned SHA-256.
  It does not read these files.
- **Consumer documents.** #3642's `PROOF.md`, #3653's `README.md` and #3682's
  `PROOF.md` are pinned for the word changes described above. Every other
  statement about these words comes from the word bytes themselves.
- **Parent words.** These are PR3133's `edits/FINAL-WORD-{base,extra}.json.gz`
  on main.
- **Producer and compiler.** These are the retained t74-native-fast
  `bw_transport.py`, `bw_emit.py` and `vendor/clifford/clifford_exact.py`. They
  are producers, not independent evidence.

PR3605's own registered chain already checks the emitted program with the
lineage code. `bw_audit_local.py` checks every residual wrapper, climb and
scalar frame, `bw_adapters.py` checks every entrance recipe, and both rely on
the `bw_gauss` kernel. `check_residual.py` checks the one changed `(E,U)` pair
with the same kernel. What was missing, as PR3687 says, is a check that does
not use that lineage. This package supplies one: the separate kernel for the
identity, plus its own source-to-emission binding. The same holds for the
consumers. #3642's pinned `PROOF.md` says its separate native runs check
ledger, wrapper, phase and warp contracts, and #3682's reports two five-stage
native runs. This package's regenerated `LOCAL-CHECKS` equal the receipts those
runs recorded.

**Local-only cross-check (not part of the registered replay).** The producer's
own `bw_adapters.py` needs numpy. Under Python 3.13.1 and numpy 2.2.2 (not
PR3605's declared numpy 2.5.4), it wrote a `RESIDUAL-ADAPTERS.json` for each
provider. The LF-normalized bytes equal this package's reconstruction:
`a19e744f…` (base) and `c4ddd4db…` (extra). So the recipe checked here is the
one the native chain serializes. On Windows, `bw_adapters.py` writes CRLF
through `write_text`. This cross-check was run on the STAGED words only. The
package's reconstructions for the consumer words are byte-identical to these.

## Reproduction

```sh
python3 -I -B research/staged-644-660-native-binding-audit/verify.py
python3 -I -B research/staged-644-660-native-binding-audit/test_verify.py -v
python3 -B scripts/research_package.py --package research/staged-644-660-native-binding-audit --check-only
python3.12 -Werror -B scripts/research_package.py --package research/staged-644-660-native-binding-audit
```

These use only the Python 3.12 standard library. On a Windows 11 laptop the
verifier takes about 80 seconds (up to three minutes under load) and the tests
about 50 seconds. The PR heads must be present for the provenance pins:

```sh
git fetch --no-tags origin refs/pull/3605/head refs/pull/3642/head refs/pull/3653/head refs/pull/3682/head refs/pull/3687/head
```

## Scope and unchecked obligations

This checks the native entrance of the two changed helpers in the STAGED,
RETIMED and DELAYED words, and the merged donor climbs of the latter two. It
does not check:

- the native phases of the other 56 serialized residual recipes, the 72 warp
  records (240 emitted warp events) or the scalar macros under an independent
  kernel;
- that the moved releases commute with the gates they cross. That is #3642's
  and #3682's argument, and their free-operator checks. This package binds the
  clocks at which the releases are emitted, not the operator they produce;
- any other climb or residual of the donors 640/656;
- owner journals, physical stock, prefix, precision and tape;
- the T740 release, the consumer releases (T530, T488, T360) and their κ;
- the inherited all-size compiler, analytic transfer and BIT hypotheses.

A passing finite audit does not admit a supplier or change the selected record.

## Open next questions

The structured list is in [TASK.json](TASK.json).

1. **Do all 57 serialized residual recipes and 72 warp records pass the
   separate kernel?** Loop `check_recipe` over every reconstructed adapter key,
   and check each warp record as a monomial identity. The STAGED, RETIMED and
   DELAYED adapter files are identical, so one run covers all three families.
2. **Is the complete emitted 644/660 lane phase-exact under an independent
   simulator?** This would need an emitted-event interpreter for the scalar
   macros and warps, compared with PR3687's free-operator endpoint. It would
   also check the moved releases natively.
3. **Which open PRs carry 644/660 words that differ from the STAGED, RETIMED
   and DELAYED bytes?** This package covers exactly those six words. First
   step: list the blob ids of `*644-660*.json.gz` and `DELAYED-*.json.gz`
   files across open PR heads, and run the consumer comparison on any new
   ones.

## Credit

- **Construction:** Ross Richardson's PR3605.
- **Parent words:** dcharb78's PR3133, with the word lineage credited there.
- **Consumer words:** roger-sato's #3642 (RETIMED, reused by rohanarun's
  #3653) and zxv's #3682 (DELAYED).
- **Open question:** Sagar Thakrar's PR3687 posed the question answered here.
- **Separate kernel:** Sagar Thakrar's, from frontier1094-recipes-exact-seed76.
- **Producer lineage:** DreamingOfClouds/PR458, retained t74-native-fast
  (PR2226 notices).
- **Method and code:** adapted from Wentao Li's
  `research/rank7-group-d-native-widths-audit/`, which in turn adapts the
  group A–C audits.

Prepared by Mainzu with substantial assistance from Claude Code (Anthropic,
Claude Opus 5.5). No independent human or formal-kernel review is claimed.
Apache-2.0.
