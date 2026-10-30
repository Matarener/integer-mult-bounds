# Independent audit of PR3605's staged 644/660 words

PR3605 replaces eight early raw helper writes with four later donor releases,
so that helpers 644 and 660 drop from width 8 to width 7. This package checks
that change with a separately written exact interpreter, using the unchanged
parent words as the single-change control. **The changed words pass at head
`3efbb5de` for both providers**: they are exact identities, their cleanup is the
literal inverse, and their binary frames give exactly the claimed profile and
widths. A pass makes these words an independently checked local input for the
open staged-width chain that reuses them unchanged. It does not cover the
retimed words of #3642/#3653/#3682, the native phases of the new entrance
frame, or any owner journal. Those remain load-bearing.

Reproduce (standard library, about 1–2 min):
`python3 -I -B research/staged-644-660-independent-audit/verify.py && python3 -I -B research/staged-644-660-independent-audit/root.py`

In detail, the changed `base` and `extra` words are exact arbitrary-dirty
identities in both orientations, with 632 independent inputs and 91 private
buffers. Their chronological binary frames give the local profile
`{1:2433,2:724,3:228,4:102,5:20,8:8} -> {1:2439,2:726,3:224,4:102,5:20,8:8}`
and the helper widths `8:99 -> 97`, `7:50 -> 52`. For PR3605's fourth claim,
the root, the check is narrower: exact arithmetic confirms the published
PR3605 and PR3148 root brackets **on their published histograms**, and recounts
PR3605's idle histogram from its aggregate owner witness, with the witness's
windows taken as published.

This is a finite exact **audit** of one local supplier change. It makes no κ
claim and no frontier change, and it admits none of the PRs named below. It
does not check native Gaussian phases, owner journals, complete admission or
the inherited all-size hypotheses (see Scope). The selected record stays
`0.001672660197076918`.

## What was audited

Audited object: RossRichardson's
[PR3605](https://github.com/CrocSwap/integer-mult-bounds/pull/3605), head
`3efbb5de06a49ffeea6684482f2d3fe48cdca3fb`, package
`research/staged-644-660-width-reduction`. In its two words, eight early raw
helper-to-target writes (old `B184..187` for helper 644, `B216..219` for 660)
are replaced by four donor releases at `span(429,30)`: `640 += 2*644` and
`496 -= 2*644` before old B599, and `656 -= 660` and `520 -= 2*660` before
old B647. Helpers 644 and 660 then enter at `span(429,30)` instead of `span(30)`
and keep FULL terminals. The single-change control is dcharb78's unchanged
[PR3133](https://github.com/CrocSwap/integer-mult-bounds/pull/3133) parent words
(`51eb9c4e`, byte-identical on main). The root control is Jeremy Diviney's merged
[PR3148](https://github.com/CrocSwap/integer-mult-bounds/pull/3148) (`f2927a4b`).

**Who consumes these words** (GitHub API, 2026-10-18, heads re-checked before
submission):

- *Unchanged reuse.* #3624 `515a7c44`, #3626 `659fd5e7` and #3633 `72c268f1` add
  word blobs `dc6d321b`/`78e7b2bb` and record blobs `042dbc69`/`67f04ae3`. The
  same blobs sit inside #3638 `d62e1acd`'s vendored `PR3624-SOURCE.tar.gz` and
  #3630 `bcac7fe0`'s `PR3605-SOURCES.tar.gz`. For these PRs, the audited words
  are the supplier words.
- *Parent only.* #3642 `044d24f1` (roger-sato, T530) and #3653
  `607a09ff` (rohanarun, T488, vendoring #3642) carry the same STAGED blobs, but
  their claims run `RETIMED644-660` words (`d69125e0`/`f3c580b0`). #3682
  `431e6c60` (zxv, T360) also vendors the STAGED blobs and runs its own
  `DELAYED` words (`7ccd0962`/`3f1fb471`), which apply the same two commuting
  release retimings to different bytes. **None of these retimed words is
  checked here**; only their STAGED parent is. #3653 and #3682 report the same
  endpoint, the highest among these staged-width claims.

PR3605's own semantic check runs the pinned inherited interpreter
(`audit_local.py`). This package supplies a separately implemented check of
the STAGED words. It does not check any of these PRs' own owner journals or
roots. Concurrent work, none of which re-implements the word semantics:

- #3659 (jwr404) adds the published PR3605 T740 histogram and compares its
  root with 0.00173 and the selected κ; #3661 does the same for the T450
  allocation.
- #3677 (jwr404) checks only the arithmetic of the published RETIMED profile
  (rank mass 5,135, lower moment), not the RETIMED words.
- #3681 (roger-sato, `9f781394`) replays the complete PR3605 wrapper with a
  fresh retained bootstrap. It runs the inherited code, native chain included,
  so it is a full replay but not an independent check. It is not reviewed here.

This package's distinct parts are the independent word semantics, the PR3148
delta attribution, the aggregate-witness recount and the sensitivity analysis.

| Quantity (each provider) | PR3133 parent (control) | PR3605 changed word |
|---|---|---|
| Local profile | `1:2433, 2:724, 3:228, 4:102, 5:20, 8:8` | `1:2439, 2:726, 3:224, 4:102, 5:20, 8:8` |
| Helper widths | `4:26, 5:2, 6:18, 7:50, 8:99, 9:213` | `4:26, 5:2, 6:18, 7:52, 8:97, 9:213` |
| Inputs / private buffers | 632 / 91 | 632 / 91 |
| Forward (dirty buffers), dual, reverse pull-back | PASS | PASS |
| Cleanup equals the literal inverse | yes | yes |

Per call, the profile changes by +6 rank-1, +2 rank-2 and −4 rank-3 children
(local rank mass −2). The change is confined to exactly six registers, and
each register's change equals PROOF.md's written invoice:

- pivots 644/660: +1 rank-2, −1 rank-3;
- first donors 640/656: +1 rank-1, +1 rank-2, −1 rank-3;
- second donors 496/520: +2 rank-1, −1 rank-2.

Applying either helper's edit alone keeps the identity and moves the profile by
+3 rank-1, +1 rank-2 and −2 rank-3 children. The two helpers' shares are
therefore separable and additive.

## Method and independence

The registered verifiers (`audit_core.py`, `verify.py`, `root.py`) import only
the standard library. Nothing is imported or copied from the audited authors'
code (the PR3133/PR3605 producers, cleanup generators or the inherited
`audit_local.py`). The word format and contract were read from those pinned
sources. `root.py`'s aggregate legality checks re-implement, without importing
it, every check of PR3605's `owners/verify_aggregate.py` except the two derived
from the source template (the literal T37 order, and the window classes and bin
counts computed by `owner.windows`).

The checks are not independent of every earlier audit, though.
`audit_core.py`'s frame bill and free-word structure re-implement, without
importing, Arham Tahir's merged `coupled-carrier-independent-audit/verify.py`.
That includes the point-set spans, the warp-frame and lifted-frame checks,
target levels keyed by register, and the dual symbol naming. The two audits
therefore share a reading of the contract. The optional cross-check below
imports the inherited auditor on purpose.

- **Identity, algorithm 1 (forward values).** Each register's value is
  propagated as exact rational combinations of `(input, reduced free-group word)`.
  Warps are independent invertible free symbols. All 632 live inputs **and the
  91 private buffers** are independent symbols, so the buffers are dirty.
  - The check requires `y_t -> y_t + x_t` with every other live input restored,
    and no buffer contribution in any live register.
  - With dirty buffers, every buffer is returned unchanged in both orientations.
  - At the cleanup boundary, targets are sheared, and the 91 restored helpers
    equal their own inputs and are read nowhere else.
- **Dual.** The contragredient circuit is run separately with independent `K^-T`
  symbols and must give `x_s -> x_s - y_s` with clean buffers.
- **Identity, algorithm 2 (reverse pull-back).** The program is processed
  backwards on covectors, with words growing on the right. The resulting
  723 × 723 symbolic matrix at return must equal algorithm 1 entry for entry.
  A separate pull-back of the pre-cleanup program must satisfy the same
  boundary contract.
- **Frames.** Subspaces of `F_2^9` are stored as 512-point masks. Each gate's
  frame must contain the current frame of every register it touches. The checks
  also cover:
  - the frame maps of all 72 warps;
  - centre descents, target levels and end frames;
  - the inherited structural rules: dyadic scalars, power-of-two scales, and
    wrapper and correction access.

  The lifted-Lagrangian action is also computed for every warp. For an
  invertible warp it follows from the frame-map check, so it only checks the
  implementation and adds no evidence. The profile and widths are derived from
  the frame chains; report fields are compared only afterwards.
- **Reconstruction.** Each changed word is rebuilt from the parent using only
  PROOF.md's prose.
  - Every field except cleanup must equal the shipped word.
  - Cleanup must equal the independently derived literal inverse.
  - Canonical and compressed digests must match PR3605's records.
  - The declared edit record must equal the prose.
- **Second method (written argument).** Two parts of PROOF.md are checked
  symbolically:
  - `P_new = P_old S1 S2` holds on **every register** at the boundary after the
    old-B647 releases, and the S matrices change exactly the four donors and the
    eight tabled targets;
  - the two four-row target tables hold exactly at old B599 and B647, every
    other target has zero columns, and each table kills its `v`.

  A per-register frame invoice is also computed and compared with PROOF.md's
  written per-pivot histograms.
- **Contract fidelity (optional; not in the registered replay).**
  `crosscheck_inherited.py SEED TRIALS` compares this package's forward and dual
  verdicts with the inherited interpreter on random mutants of the `base` word.
  That interpreter is pinned by SHA256 in the script and in SOURCES.json. The
  mutants flip, drop or swap B gates, change coefficients, flip or drop cleanup
  gates, drop or flip corrections, and shift warps. Seeds `3605 40` and `44 60`
  gave 200 of 200 agreeing verdicts. This script imports the inherited auditor,
  so it checks that the contract was read correctly. It is not independent
  evidence.

## Required-failing mutants (19 per provider, all as predicted)

| Mutant | Outcome |
|---|---|
| Omit one of the four releases (cleanup regenerated) | identity fails at targets: 644→640 `135,162`; 644→496 `135,220`; 660→656 `141,196`; 660→520 `141,171` |
| Flip one release sign, or both signs of one helper | identity fails at targets |
| Add releases but keep the raw target writes | frame containment fails at B184; identity fails at `162,171,196,220` |
| Entrance `span(429,30)` alone on the parent | frame containment fails at B184 (helper 644) |
| Releases at frame `[30]` | frame containment fails at the first release |
| Parent cleanup on the changed word | identity fails at donors `496,520,640,656` (no buffer is left dirty) |
| First 644 cleanup gate removed | identity fails at 19 helper registers `225…644` (no buffer is left dirty) |
| Keep the old `[30]` entrance | identity holds; profile = changed word + 2 rank-1 children (`{1:2441,…}`); rank mass and widths return to the parent's `8:99, 7:50` |
| Drop the restore-210 frame edit | identity and bill unchanged (that edit is bill-neutral) |
| 644-only or 660-only edit (restore-210 edit not applied; bill-neutral) | identity holds; profile `{1:2436,2:725,3:226,…}`, widths `7:51, 8:98` |

The old-entrance mutant shows that, within these words, the entire rank-mass
saving of 2 comes from the entrance frame. With the old entrance, the staged
releases leave local rank mass unchanged. The physical legitimacy of the
`span(429,30)` entrance therefore rests on the native wrapper identity
`L^-1 T_F T_P^-1 R^-1 = C_[7] ⊗ I_[2]` (PR3605 `check_residual.py`, pinned in
SOURCES.json but not run). Every consumer above shares that identity, and it is
not independently checked here (open question 1).

## Root brackets and attribution

`root.py` uses `M(b) = Σ_r r·H[r]·(73/r)^b / (73·663040)` (PR3605 DERIVATION.md)
on the published complete histograms.

- **Primary engine:** outward-rounded exact rational interval arithmetic, using
  atanh/Taylor series with explicit remainders on a `2^-320` grid.
- **Second engine:** 70-digit decimal Newton iteration.
- **Third check, preparation only:** python-flint 0.9.0 arb at 400 bits
  reproduced both `M(C)-1` and `M(D)-1` to all printed digits. It is not part
  of the shipped replay.

| Histogram | Published bracket | Confirmed 30-digit bracket |
|---|---|---|
| PR3605 | `[0.001730006549538841847005, …006]` | `[0.001730006549538841847005854305, …306]` |
| PR3148 | `[0.0017297774946785970118869, …870]` | `[0.001729777494678597011886903656, …657]` |

The root delta is `+2.29054860244835118950648e-7` to `…650e-7`. Both
histograms have the same rank mass, `48,165,120 = 65088·740`. The
decomposition is `H = 6660·L + I`. The local change is +6 rank-1, +2 rank-2
and −4 rank-3 children per call. The idle change is
`{1:+996, 3:−617, 4:+1, 5:−3083, 6:+3, 48:+616}`.

Swapping one component at a time moves the root by about ±9.7e-5 (hybrids
0.0018266 and 0.0016331). Both hybrids violate the coverage law below (rank
mass 48,165,120 ∓ 13,320), so this split is bookkeeping, not a measure of
fragility.

**Recount from the aggregate owner witness.** `root.py` recounts PR3605's
published aggregate integer witness
(`owners/AGGREGATE-INTEGER-FLOW.json.gz`, vendored).

- Over its 1,491,840 bins, `idle = capacity − pattern width` reproduces `I`
  exactly.
- Its role flow meets the per-call demand
  `20 × {4:26, 5:2, 6:18, 7:52, 8:97, 9:213}` (the audited widths) for all 333
  macro-calls.
- It passes every check of PR3605's `verify_aggregate.py` (reimplemented)
  except the two derived from the source template: record types and ranges,
  no duplicate records, pattern records filling every declared bin (S × bins),
  open/closed windows, supply equal to flow, per-call demand, the per-copy
  group capacity, the complete paid rank mass, and its own inventory and
  profile fields. Not reimplemented: the literal T37 order, and whether the
  declared window classes and bin counts equal those `owner.windows` derives
  from the template.
- The capacity balance `35,804,160 = mass(I) + 6660·3279` holds, so
  `mass(I) = 13,966,020`.
- Six controls are rejected, each for its expected reason (asserted, as
  `verify_aggregate.py` does):
  - the parent widths, against the witness's inventory field;
  - the parent widths with that field also set to them, rejected by the
    per-call width demand;
  - a deleted pattern record, and a duplicated one;
  - a deleted role-flow record;
  - a role on an excluded lower window endpoint.

The witness's source windows are taken as published. The literal journal of
2,717,280 helper roles (6660 × 408) and its chronology are not re-derived here.

**How fragile is the gain?**

- *Coverage law.* Every complete histogram here obeys `Σ r·H[r] = 72W + 64N`
  (W = 663,040, N = 6,660; inherited, see Scope). `root.py` checks both
  histograms meet it at 48,165,120, and that both words have the same per-call
  constant (local rank mass − helper width units = 1,856), which forces total
  owner capacity 54W = 35,804,160, the witness's. So a wrong capacity, bin
  count or added/dropped child breaks the law; the ±1-child shifts in
  `ROOT-RESULT.json` (rank-48: `∓3.498e-7`) are slopes of law-violating
  histograms only.
- *Mass-conserving errors.* Let `m = Σ_{ΔH[r] > 0} r·ΔH[r]` be the rank mass
  an error moves. If the removed mass sits at published ranks (at most 48,
  checked by `root.py`) and every true rank is at least 1, linearity and
  `(73/48)^b ≤ (73/r)^b ≤ 73^b` give `ΔM(b) ≤ m·c(b)`, with
  `c(b) = (73^b − (73/48)^b)/(73·663040)`; since `M` increases in `b`,
  `m < (1 − M(b0))/c(b0)` keeps the root above `b0`. This inequality is a
  written argument; its thresholds are exact-interval computations: an error
  can **cancel the gain over PR3148 only if it moves more than 4,678 units**,
  and take the root below 0.00173 only above 133. Both are nearly attained:
  98 rank-48 → 48 × rank-1 relabels (4,704 units) and 3 relabels (144 units)
  are the fewest that do. Smaller errors still change the gain's size (one
  relabel: `∓2.35e-9`; one width-8 role moved to an empty capacity-48 bin:
  `−2.73e-10`).
- *Where the risk is.* PR3605 and PR3148 differ by 97,186 moved units:
  66,600 from the per-call word change and 30,586 from idle/owner repacking,
  including 616 extra empty capacity-48 bins (29,568 units). So small
  accounting slips cannot cancel the gain, but a window or journal legality
  failure could, because the idle/owner repacking the gain depends on moves
  6.5 times the threshold. The open risks are the native residual (open
  question 1) and window and journal legality (questions 3 and 4), not more
  digits of the root.

## Scope, inherited assumptions and unrun obligations

Checked here:

- the finite free-operator identity for arbitrary independent inputs, with
  warps as free invertible symbols;
- the binary-frame chronology and bill;
- the cleanup;
- the PROOF.md factorization, tables and invoice;
- arithmetic on two published histograms, and the aggregate-witness recount.

The free-operator proof uses inverse cancellation only, so it applies to the
actual invertible warps.

Not checked:

- native Gaussian/Clifford phases and the rank-7 residual `C_[7]⊗I_[2]` on 512 columns;
- the `RETIMED644-660` words of #3642/#3653 and the `DELAYED` words of #3682;
- the owner source windows and the literal T740 owner journal (the idle profile is recounted only from the aggregate witness), and every consumer's own owner journal and root;
- the PR3605 conditional release and full fresh-bootstrap wrapper replay requested in Ross's #1166 handoff (#3681 claims this replay with the inherited code; not reviewed here);
- physical/prefix/outer release, precision, the inherited all-size hypotheses H1–H5 and the formal kernel.

The binary-frame contract is taken from the inherited format. It is not
derived from first principles. The coverage law `Σ r·H[r] = 72W + 64N` for
this template (the PR1012 deficit form, as used in
`research/complex-queue-ceiling-census`) is likewise inherited and cited, not
re-derived: `root.py` only checks that the published histograms meet it, and
the mass-changing/mass-conserving classification above depends on it. Gzip streams are not compared; payloads and
pinned byte digests are.

## Reproduce

From the repository root, with Python 3.12 or later and the standard library only:

```sh
python3 -I -B research/staged-644-660-independent-audit/verify.py
python3 -I -B research/staged-644-660-independent-audit/root.py
```

Expected output:

- `verify.py`: two `CHECKED` lines, then
  `PASS_INDEPENDENT_STAGED_644_660_WORD_AUDIT`;
- `root.py`: `PASS_EXACT_MOMENT_BRACKETS`.

Together they take about 1–2 min, depending on machine load.

Both compare against the committed receipts `RESULT.json` and
`ROOT-RESULT.json`; `--write` regenerates a receipt deliberately. Failures
raise explicit exceptions, also under `-O`.

Both commands passed directly on CPython 3.14.4 under `-I -B` and `-I -O -B`,
and `research_package.py --check-only` passed. The generic runner
(`python3.12 scripts/research_package.py --package
research/staged-644-660-independent-audit`) needs Python 3.12. That version
was not available here, so the runner has not been executed.

## Sources

Base main `20ecf2891d80b5acf18d980b2164fb44ea7faa90`, priority revision 6.

- **Snapshots.** PR3605 is unmerged, so its two words, two edit records, its
  conditional-release `CLAIM.json` and its aggregate owner witness are
  byte-preserved in `inputs/`. [SOURCES.json](SOURCES.json) records their
  source path, commit, Git blob and SHA256, which `verify.py` checks.
- **Main inputs.** The PR3133 parent words and PR3148 `CLAIM.json` are read
  from main; their blobs equal those at the predecessor heads.
- **Read, not executed.** These PR3605 files are pinned the same way:
  PROOF.md, staged_pair.py, check_scope.py, verify.py, DERIVATION.md,
  check_residual.py and owners/verify_aggregate.py.
- **Provenance rows.** Arham Tahir's audit `verify.py` and the inherited
  `audit_local.py` are also pinned.

## Open next questions

The structured list is in [TASK.json](TASK.json).

1. **Do the native phases of the paired `span(429,30)` entrance hold?** Every
   consumer shares this obligation, and the whole width saving rests on it. It
   needs an independent check of the rank-7 residual on all 512 Gaussian
   columns, without the `bw_*` lineage code. #3681's full wrapper replay runs
   the inherited native chain, so independence is the open part.
2. **Are the retimed words correct?** These are the `RETIMED644-660` words of
   #3642/#3653 and the separately built `DELAYED` words of #3682. First step:
   run this package's interpreter on each, with the audited STAGED words as the
   single-change control. Check the identity, the claimed per-invocation change
   (−2 rank-1, −2 rank-2, +2 rank-3 children), unchanged widths and
   release-retiming mutants. This is cheap and is now the most
   decision-relevant local check.
3. **Is each live consumer's own owner journal legal?** These are T450
   (#3624), T530 (#3626), T488 (#3633), T360 (#3638), the retimed T530/T488
   (#3642/#3653) and the retimed T360 (#3682); #3630 is a ceiling bound, not
   an allocation. Where a consumer's histogram is checked against the coverage
   law, as here, the same argument applies: the window bounds and literal
   chronology decide legality, and an owner error can cancel that consumer's
   gain only by moving more rank mass than its own threshold.
4. **Are PR3605's own T740 owner windows legal?** PR3605's own κ is already
   superseded by its consumers, so this is lower priority. The remaining check
   is the 333 source windows of the aggregate witness. First step: derive the window classes from the T37
   source template without the retained `owner.windows` routine, and compare
   them with the witness's `groups`.
5. **Is the restore-210 frame edit needed?** It is bill- and identity-neutral
   here. Does any native stage require it?

## Credit and provenance

- **Construction:** RossRichardson's PR3605.
- **Parent words and coupled folds:** dcharb78's PR3133.
- **T740 owner/cap root control:** Jeremy Diviney's PR3148.
- **Word lineage:** the credited predecessors are retained as recorded in those
  packages: PR2857, PR2908/2917, Marius-Paul Dumitrean's PR2979, Jeremy
  Kothe's PR3015 and PR3042.
- **Frame-bill and free-word structure:** Arham Tahir's
  `coupled-carrier-independent-audit/verify.py` (Apache-2.0). `audit_core.py`
  re-implements it without importing it (see Method).
- **Root model:** the PR3531 arithmetic lineage, as credited in PR3605.

Prepared by Sagar Thakrar (thakrarsagar) with substantial AI assistance from
Claude (Anthropic, Claude Opus 5.5). No human or formal-kernel review is claimed.
Apache-2.0.
