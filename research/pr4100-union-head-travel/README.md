# Literal head travel of #4100's sparse-union schedule

**Claim type: a scoped proof audit (per-pass accounting with explicit
constants), checked against an exact-integer multitape simulation of the whole
schedule. No new κ.** This does not accept #4100 and changes nothing in it.

## Object and gap

The object is the radix-distributed sparse-union schedule in #4100's
[vendor/UNION-SCHEDULE.md](../unconditional-batched-crt/vendor/UNION-SCHEDULE.md),
at head `337d04939571a637aeab54a0f58f54fde811663a`. GAUSSIAN.md's
"per-visit union movement" row uses it.

- **Lineage.** Its algorithm text is the PR1731 lineage text; only the
  numbers in §5b changed.
- **What was reviewed.** The merged PR2578 review
  ([`pr1731-union-rect-review`](../pr1731-union-rect-review/README.md))
  checked the operator and volume identities. It explicitly leaves "the
  tape-level realization of the schedule: the variable-length transpose and
  the head accounting" uncovered.
- **What the source asks for.** It names exactly these two as "the places
  that most need an independent review".
- **What the lineage checkers do.** `sched_test.py` and `sched_review.py`
  count list moves. They do not model head positions, rewinds, bit tapes,
  LIFO pops, or the two-pass level realization of the transpose.

**Why it matters.** In #4100's ledger the union row has slack ≈ 0.406, and
the verifier checks this value. A hidden extra factor of `g = p^β` or of
`L = poly(p)` in the head travel would exhaust that slack.

**Outcome: the head accounting of §2.3 holds, including the variable-length
transpose, with explicit constants.**

## Model

Each record has width `RW` cells: a `p`-bit payload plus an `o(p)` header.
Bits take one cell. The simulation uses these tapes:

- **Work tapes** `W1` and `W2` hold `S_r` and `S_(r+1)`.
- **Radix tapes** `Z`, `O`, and the bit tape `Tb`.
- **Zip tapes** `M1` and `M2`.
- **LIFO tapes** for final records and their keep indicators.
- **Dense tapes:** the microbox and the forming scan's indicator bits.

Contents are written from cell 0 with an end marker, and rewinds travel only
the written length, as §2.3 states.

The schedule is exactly §2.1–§2.2:

1. **Forming scan.** One dense scan writes `U` and its indicator bits.
2. **Rounds.** For `r = 1, …, R`:
   - tag each record by its `r`-th smallest flag;
   - apply `⌈log₂ g⌉` stable LSD radix passes;
   - on each axis substream, run the level-by-level lockstep zip, two passes
     per level. Unit ends come from header prefix fields and ordinals; the
     row length is never used.
   - apply `T_f` in place on each line;
   - unzip, then invert the radix passes by replaying `Tb` in reverse;
   - split the stream, sending finished records and the keep bits to the
     LIFO tapes.
3. **Wrap-up.** Pop `rest_r` with `keep_r` for `r = R, …, 1`, then merge
   into the microbox by the indicator bits.

## Results

**Per-round accounting.** A round on `N = |S_r|` records with
`nb = ⌈log₂ g⌉` radix bits and `lev = ⌈log₂ a⌉` zip levels moves at most
the following:

| Step | Cells moved |
| --- | --- |
| Radix distribution | `7·nb·N·RW + nb·N` |
| Each zip or unzip level | `8·N·RW` |
| In-place line sweep and return | `4·N·RW` |
| Segment navigation and final rewind | `2·N·RW` |
| Radix inversion | `8·nb·N·RW + 3·nb·N` |
| Split | `4·N·RW + N` |
| LIFO pop and interleave | `7·N·RW + 3·N` |

That totals `N[(15nb + 16lev + 17)RW + 4nb + 4]`, which is at most
`17·RW·N·(nb + lev + 1) + O(N log g)`.

**Total.** Summing over rounds with `Σ_r|S_r| = Σ_x|F(x)| = Σ_i|U_i|` gives
union movement `O(RW·(log g + log a + 1)·Σ_i|U_i|)`. The dense forming scan
and the final merge add at most `6·V·RW + 4V`. This is §2.3's statement with
the constant 17. The number of rounds does not multiply the cost: round `r`
touches only `S_r`, and each rewind travels only what was just written.

**The variable-length transpose is sound.** For a fixed prefix, every row of
an axis-`f` substream has the same suffix set; this is §2.1's key lemma. A
level's lockstep pass reads `h` records from `M1` and then `n−h` from `M2`,
and both parts end together. Unit ends come from headers, so `b` is never
needed. In the simulation, every extracted group is a complete `E_f`-line:
consecutive ordinals `0..a−1` and one common `z`.

**Line sweep.** It is counted inside the union total here, which is
conservative. #4100 assigns its arithmetic to the boundary row.

## Evidence

`verify.py` uses only the standard library and exact integers, and takes
about 3.6 seconds. In all six cases the result equals the full Kronecker
product exactly, every line check passes, and the volume identity holds.

| `g, L, \|E_i\|` | `V` | `\|U\|` | `Σ\|F\|` | Rounds | Union / bound | Union / (`RW·Σ\|F\|·(nb+lev+1)`) |
| --- | --- | --- | --- | --- | --- | --- |
| 3, 8, [3,2,3] | 512 | 362 | 512 | 3 | 0.939 | 15.13 |
| 4, 6, [2,2,3,2] | 1,296 | 1,104 | 1,944 | 4 | 0.860 | 13.84 |
| 5, 7, [2,3,2,3,2] | 16,807 | 14,807 | 28,812 | 5 | 0.921 | 14.74 |
| 6, 5, [2,2,2,3,2,2] | 15,625 | 15,139 | 40,625 | 6 | 0.875 | 14.00 |
| 4, 5, [4,4,3,4] (dense flags) | 625 | 623 | 1,875 | 4 | 0.989 | 15.92 |
| 6, 5, [1,1,1,1,1,2] (sparse flags) | 15,625 | 12,553 | 21,875 | 6 | 0.842 | 13.48 |

The normalized cost stays between 13.5 and 15.9 from 3 to 6 rounds, for both
sparse and dense flags.

**Controls,** each of which must fail:

- **Dropped round.** Skipping round 2's application changes the result.
- **Mismatched zip chunks.** These break the complete-line check.
- **Stale rewinds** (traveling over everything ever written). These cost
  3.09× (sparse flags) and 1.68× (dense flags), breaking the written bound by
  2.6× and 1.66×. So "rewind over the written length only" is load-bearing.
- **The old per-axis scan of `U`.** It visits `g|U| = 3.44·Σ|F|` records on
  the sparse instance.

**Source binding:** SHA256 pins of UNION-SCHEDULE.md and
`composition-controls.json`, 7 exact source phrases, and the ledger's union
slack.

## Not covered

- The boundary-algebra arithmetic and its batching (a separate row).
- Header widths beyond the stated `O(g log L) = o(p)`.
- Scatter and gather of the dense stages.
- PR1673's inherited window, carving and precision hypotheses.
- The simulation runs at small `g` and `L`. The all-size statement is the
  per-pass accounting above, a counting argument; there is no proof-kernel
  check.

## Reproduce

```sh
python3 scripts/research_package.py --package research/pr4100-union-head-travel --check-only
python3.12 scripts/research_package.py --package research/pr4100-union-head-travel
python3.12 -B research/pr4100-union-head-travel/verify.py
```

The verifier prints `PASS_PR4100_UNION_HEAD_TRAVEL_FINITE`.

## Open next questions

1. **Charge the batched boundary arithmetic's row-field movement on the same
   tapes.**
   - *Why it matters:* this package counts the line sweep conservatively in
     the union total. #4100 charges batched right-hand sides to the boundary
     row, which moves only the polynomial-width row field.
   - *First step:* add a batch tape and count row-field moves per batch of
     lines of width `W` to `2W`.
   - *Blocked by:* nothing.
2. **Bind the header width to the actual record format.**
   - *Why it matters:* the accounting assumes `O(g log L)`-bit flag and
     coordinate headers, plus an ordinal field.
   - *First step:* fix the header layout and check `g log L = o(p)` against
     #4100's `β` and core side `L`.
   - *Blocked by:* nothing.

## Credit

The schedule is from the PR1731 lineage (Jeremy Kothe), as retained in Cinna
Davis's #4100 (OpenAI Codex assistance), on Vlado Vojdanovski's PR1673 outer.
Its operator and volume review is rtyu193-rgb's PR2578, and LeverRank's
`sched_review.py` is credited in the source. This independent tape-level audit
was prepared by Ryanson Jonathan with substantial Claude Code (Claude Opus
5.5) assistance. Apache-2.0.
