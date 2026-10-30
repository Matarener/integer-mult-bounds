# Method and findings

All statements concern PR3734's BORROW-WORD-43 words (`base` and `extra`), read through PR3734's
`audit_core.py` (frame bill, hygiene) and `audit_verify.py` (arbitrary-dirty semantics).

## 1. The staged entry, exactly

A helper `h` has entrance frame `E` (a subspace of F_2^9) and terminal `FULL`; its hosted width is
`9 − dim E`. Every gate touching `h` must have a frame containing `h`'s current frame. Raising the
entrance to `P = E + span(u)` requires every contact of `h` before its frame contains `P` (the
*blockers*) to disappear. An entering helper may not be read by the zero-frame precondition and
compensation wrappers, nor be a correction source (`audit_core.hygiene`).

Let `M_c` be the scalar map of the program prefix before event `c` (corrections, wrappers, A, cut,
B with warps), with `h` read but not written before `c`. Delete every contact of `h` before `c` (they
must all be reads) and insert releases `r += a_r h` at `c`. For any `w` supported on ordinary
non-restored helpers other than `h`, put `v = e_h + w`. If `a = M_c v − e_h` and no warp or
correction sees a nonzero value of `v`'s trajectory, then the new prefix equals the old prefix times
the input shear `S = I + w e_h*`. Because the completed target map annihilates helper inputs, the
target map is unchanged, and cleanup is regenerated as the literal inverse. PR3605 and PR3734 are
the case `a = w` (`M_c v = v`). A release `r += a_r h` may then slide later, as long as no event
reads, scales or warps `r` or writes `h` in between.

Frames are the only remaining condition. A release gate needs a frame `R ⊇ P + frame(r)` inside the
next frames of both `r` and `h`.

## 2. Candidates (`code/census_blockers.py`, `code/candidates.py`)

- 213 width-9 ordinary helpers: all are read by the compensation wrapper (207) or are correction
  sources (6).
- For 38 width-9 helpers, every blocker is a compensation read before the producer.
- For 54 width-8 helpers, every blocker is a read before the producer: 46 target reads in B,
  24 helper reads in A, and mixed cases.

Each helper admits up to 15 raises `P` with this property, 416 (helper, raise) pairs in total.

## 3. Exact identities exist (`code/scalar_census.py`, float screen)

Strict identities (`M_c v = v`) exist on part of the cut window for 25 width-8 candidates and for all
38 width-9 candidates. The width-9 identities are dense combinations: no two compensation columns are
proportional, and 207 columns span the 112 target coordinates. Every identity used later is
re-checked exactly with fractions (`construct.exact_fixed`).

## 4. Fixed other frames: no construction (`code/pass5.py`)

For each (helper, raise, cut), a register `r` is *compatible* when some slot of its commuting range
hosts `R = P + frame(r)` inside both next frames. The linear program asks for `w` with `a_r = 0`
on every incompatible register (warp and correction functionals included), minimising `Σ|a_r|`.

Results: 24 sampled cuts per helper plus the producer cut, 9,862 cases per provider, none with a
solution (`evidence/FIXED-FRAMES-*.json.gz`).

Validation: on PR3734's parent word the same pass finds 544 at 16 of 72 sampled cuts, with releases
`672 += 544/2` and `676 −= 544/2` before old B693 and PR3734's exact bill. On PR3133's word it finds
644 and 660 with PR3605's donors and coefficients (`evidence/CONTROL-*.json.gz`). Its later placements
give a cheaper local bill than PR3605's, as PR3642's retimings already do.

## 5. Re-solved frames: exact feasibility test

`repair.repair(minimal_B=True)` gives every B and restore gate exactly the join of its registers'
current frames, warps following (`U` = current lender frame, `E` = image). By induction over the
events, every assignment that keeps A, the entrances and the terminals contains it pointwise. The
terminal constraints (target port hyperplanes, restored-helper terminals) are upper bounds, so if
this assignment fails, every assignment fails.

`minimal_all.minimal_all` extends this to A outside the prelude. The last A gate of a target is
forced to the target's cut level, and that of a centre to its centre frame, as `frame_bill` requires.
On PR3734's word both assignments pass, with the same rank mass and a costlier histogram: the
control is that they are not too strict.

- **B windows** (40 width-8 helpers, `code/pass7.py`): 6 cuts, release vectors = pure retiming of
  the early reads plus a greedy sparse strict solution, up to 4 placements per recipient. Out of
  2,160 constructions, only 472 is feasible (4 cuts, same releases); all 1,992 pure retimings are
  infeasible (`evidence/RESOLVED-B-WINDOWS-base.json.gz`).
- **A windows** (38 width-9 and 14 width-8 helpers, `code/pass8.py`): 5 cuts, sparse strict solutions
  with a dense fallback. 414 rows, none feasible. On a sample of the rejections, the failure is a
  target leaving its port hyperplane at the end (33) or exceeding its cut level (27)
  (`evidence/RESOLVED-A-WINDOWS-base.json.gz`).

## 6. Helper 472

- **Construction.** Blocker B31 `130 += 472/2` at frame `[51]`. Producer B538 `472 += 283` at frame
  `span(508,81,51)`. Identity `v = e472 − e624 − e628/2` holds exactly at the producer cut. Releases
  `624 −= 472` and `628 −= 472/2` go just before B538, with entrance `span(429,51)` (width 7).
- **Audit.** Frames are repaired downstream (`repair.repair`) and cleanup is regenerated. Both
  providers pass frame bill, hygiene and semantics (`words/W472-*.json.gz`).
  - Bill: `{1:2455,2:716,3:222,4:104,5:20,8:8}` against PR3734's `{1:2440,2:725,3:224,4:102,5:20,8:8}`.
  - Widths: `{7:54,8:95}` against `{7:53,8:96}`.
- **Cascade.** Nine registers change their climbs: 472, 624, 625, 626, 628 and the partners 426,
  433, 435 and 437. Each partner goes from `{1:7,2:1}` to `{1:9}`.
  - The cause: `429 ∈ P` enters 624 and 628 before their B999 gates at `span(496,68,34,17)`, and
    `span(508,81,51) ∩ span(496,68,34,17) = span(51)`.
  - At the producer cut, among 313 active donors, `{624, 628}` is the only donor set of size three
    or less (`code/donors472.py`).
- **Pure retiming.** Moving the read `130 += 472/2` to just before B538 is scalar-correct but
  frame-infeasible: target 130 passes through `span(290,51)`, outside 472's producer frame.
- **Pricing.** `code/ceiling.py` adapts PR3815's exact dual (same ten-pattern basis, found optimal for
  both inventories by `code/basis472.py`):
  - every owner fill of the 472 inventory and bill has root `< 0.0017305031` (tight to 1e-10);
  - the parent inventory's bracket is `[…740, …741]`, as in PR3734's PROOF.md and PR3815.
  - At PR3862's exponent, the 8→7 price is `0.987736781…`, while 472's local saving is at most
    `0.986194…`.
- **Recovery attempts.**
  - The B-frame optimiser (`code/frameopt.py`) and a parallel session's A+B optimiser leave the bill
    unchanged.
  - A retiming search over 4,200 slots (parallel session, local-only) finds 0 decreases.
  - Strength of the B optimiser: from minimal frames it recovers PR3734's own bill to within two
    rank-1 climbs. An exact frame solve of the 472 word was not run.

## 7. Value scale (ideal fixed-inventory LP, `code/ideal.py`)

| change | Δ ideal ceiling |
|---|---|
| best possible 8→7 or 9→8 (one climb shortened by one) | +4.4e-7 to +4.8e-7 |
| one rank-2 climb split into 1+1 | −1.2e-7 |
| PR3734's 544 signature `{1:+3,2:+1,3:−2}` with 8→7 | +1.6e-7 (realised by PR3734's packing: 2.95e-8) |
| 472 as built | −7.5e-8 |
