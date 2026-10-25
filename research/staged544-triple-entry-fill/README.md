# Three staged helper entries on the PR3945 staged544 supplier

This package stages three more helpers on PR3945's terminal-width5 staged544 words, re-solves the exact frames, and
builds a new literal T360 owner fill for the narrowed inventory. Helpers 608, 609 and 600 each get one extra entrance
dimension. Each loses its four early quarter-weight reads, and two exact releases are inserted after a common cut. Each
of the three helpers then drops from width 8 to width 7. The literal T360 owner fill is rebuilt so the freed width
lands in larger idle blocks, which gives the window-free pattern-LP optimum for the new inventory. The new complete
moment root lies in

**[0.001730809033576552081734, 0.001730809033576552081735]**.

The conditional outer endpoint is the lower bound minus `10^−46 + 10^−70`:

`κ = 0.001730809033576552081734 − 10^−46 − 10^−70`,

which is **+1.4579704200277·10^−7 above PR3945** (+0.0084%). It inherits the same source, hosting, analytic and
multiplication-model hypotheses as PR3945. No unconditional multiplication exponent, selected-frontier change or Lean
formalization is claimed.

| | PR3945 | this package |
|---|---|---|
| local profile per call | `{1:2482, 2:712, 3:218, 4:109, 5:20, 8:8}` | `{1:2488, 2:714, 3:223, 4:102, 5:20, 8:8}` |
| helper widths 5/6/7/8/9 | 28 / 18 / 53 / 96 / 213 | 28 / 18 / **56 / 93** / 213 |
| owner idle | `{3:23328, 5:4320, 48:137952}` | `{3:22842, 5:1890, 48:138438}` |
| complete profile | `{1:8041680, 2:2306880, 3:729648, 4:353160, 5:69120, 8:25920, 48:137952}` | `{1:8061120, 2:2313360, 3:745362, 4:330480, 5:66690, 8:25920, 48:138438}` |
| root lower bound | 0.001730663236534549309146 | **0.001730809033576552081734** |

## What changed

**Words** (`recipe/`, `inputs/`). Each staged entry follows PR3949's staged-entry construction, extended so that
releases may land in any register (including other helpers): raise the helper's entrance to a hyperplane-compatible
frame P, delete its reads before the cut, and insert releases `a = M_c(e_h + w) − e_h`, with `w` in the kernel of every
later consumer. After all three entries, the exact frame optimum (the repository's `frames_exact.py`) is written back
into A/B/restore and cleanup is re-derived literally. `recipe/RECORD-*.json` are source-guarded literal records:
ordered slice preimages, entrance preimages, warp identity/map preservation, and canonical hashes of the source and
target words. `recipe/staged_entries_applier.py` replays them without any solver. B loses 12 reads and gains 6
releases. A and restore keep their operator sequences, and returns, ports, removed set and native lenders/matrices are
unchanged.

| helper | entrance | deleted reads (B) | releases |
|---|---|---|---|
| 608 | `[45] → [97,45]` | into 114, 137, 173, 121 (±1/4) | −1/2 into 137; −1 into helper 610 |
| 609 | `[45] → [97,45]` | into 114, 137, 173, 121 (+1/4) | +1/2 into 121; −1 into helper 610 |
| 600 | `[45] → [127,45]` | into 183, 202, 175, 123 (±1/4) | −1/2 into 202; −1 into helper 602 |

**Owner fill** (`owner/`). The window-free LP and PR3815's class-level Hall LP both give the same optimum for the new
inventory: 486 more empty cap-48 bins, 2,430 fewer idle-5 bins and 486 fewer idle-3 bins. The obvious repacking is not
attainable on this clock: every idle-5 bin's window ends by call 265, and 2,493 calls hold all 96 eights in cap-8 bins.
The fill was built in three steps. First, an integer program chooses per-class zero-idle pattern changes subject to
exact per-width Hall conditions. Then each width is moved by a min-cost interval transport. Finally, same-call
collisions are repaired. Relative to PR3945's literal fill, 70,876 of 1,321,920 roles change (owner, child, port).
`owner/MOVES.json.gz` lists them, and `owner/build_fill.py` regenerates the fill from PR3945's bytes with the standard
library only.

## Replay

Python 3.12, standard library only, from the repository root:

```sh
python -B research/staged544-triple-entry-fill/verify.py
python -B research/staged544-triple-entry-fill/checks/independent_frames.py --controls
python -B research/staged544-triple-entry-fill/checks/exact_root.py --controls
python -B research/staged544-triple-entry-fill/owner/verify.py
python -B research/staged544-triple-entry-fill/owner/build_fill.py
python -B research/staged544-triple-entry-fill/test_verify.py
python -O -B research/staged544-triple-entry-fill/test_verify.py
python -B research/staged544-triple-entry-fill/admission/authenticate.py
```

- `verify.py` reconstructs both words from PR3945's words and runs hygiene and the Lagrangian frame bill. It also runs
  the arbitrary-dirty forward, dual and cleanup-boundary semantics of the retained `audit_core`, and authenticates the
  fresh native receipts.
- `checks/independent_frames.py` reuses PR3945's standard-library GF(2) walker. It checks the declared deletions,
  releases and entrances, the profile delta and the inventory, with 10 mutation controls.
- `checks/exact_root.py` uses rational log/exp enclosures to certify the new root bracket and PR3945's bracket, and
  shows that the padded endpoint beats PR3945's upper bound (4 controls).
- `owner/verify.py` runs PR3945's owner walk over every role of both PR3945's fill and the new fill. It checks source
  windows, family distinctness, compact offsets, capacity, idle and the complete histogram. Controls include restoring
  any narrowed width, which must overflow an exactly packed bin.
- `admission/authenticate.py` authenticates the complete inherited ordinary/outer release run described below.

Fresh native phases need NumPy (about 3–6 minutes per word here):

```sh
python -B research/staged544-triple-entry-fill/native/run_native.py research/staged544-triple-entry-fill/inputs/NEW-base.json.gz new-native-base
python -B research/staged544-triple-entry-fill/native/run_native.py research/staged544-triple-entry-fill/inputs/NEW-extra.json.gz new-native-extra
```

Both five-stage runs passed on the exact gzip inputs (`evidence/NATIVE-*.json`).

**Complete admission.** `admission/full_replay.py` rebuilds PR3945's exact 666-file closure from the pinned predecessor
archive, using PR3945's own terminal generator and source patches. It adds the six staged-entry files (672 total),
reruns both native providers fresh, and runs the inherited admission engine end to end on these words and this fill.
That covers owners, parent lift, rebinding, discovery, outer ledger and independent outer check, and release. The only
engine edits are PR3945's: source-profile commit, manifest and file count, plus frozen-SPEC control counts. The
retained receipts are in `admission/`.

```sh
python3.12 -B research/staged544-triple-entry-fill/admission/full_replay.py --work /fresh/external/path
```

## Credit

The staged-entry mechanism is Ross Richardson's PR3605 (staged entrance, literal cleanup) and dataisfire's PR3734
(staged544 supplier, retained source closure, `stage544_applier`). The general census and assembler are
ChaloupeMusic / Erwan Secousses' PR3949, and the attained T360 clock and fill are PR3815, with PR3638 lineage. The
terminal-width5 words, owner walk, independent frame walker, rational root enclosures, native runner and admission
adaptation are Dugongue's PR3945. Exact frame solver: Marius-Paul Dumitrean (`rank7-skip-restore-optimum`). Audit core
and semantics: Sagar Thakrar (PR3687) and roger-sato (PR3693). zxv PR3682 supplies the comparison claim. Independent
audits of PR3945 by #3969, #3987 and #3994 were read. NOTICE.md lists the full lineage. New staged entries, owner-fill
construction, checks and integration: prepared by Rohan Arun with Anthropic Claude assistance. Apache-2.0. No
independent human review is claimed.

## Open next questions

- **A fourth entry?** The window-free LP shows that a fourth 8→7 narrowing loses: k = 4 prices at −9.06·10^−8 because
  the Y-type eight-slot sinks ((9,8,8,7), (8,8), (8,8,8,8)) give only about 3.33 helpers' worth of capacity. Is there a
  staged entry with a different width move (9→8, 7→6) or a different sink that still pays?
- **Other triads.** Helpers 600/601/602 and 608/609/610 form release triads: each release lands in the third member,
  and only two of a triad stack. Are there more such triads among the remaining width-8 helpers? Start with the
  general staged-entry search on these words.
- **Different repack.** The fill realizes the LP optimum, but only after moving 70,876 roles. Is there a smaller move
  set, or a clock change, that admits a cheaper narrowing schedule?
