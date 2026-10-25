# Three staged entries and an LP-exact literal fill

Prepared by Rohan Arun with Anthropic Claude assistance. Apache-2.0. The construction reuses the credited staged-entry,
frame, owner and admission machinery listed in NOTICE.md.

## 1. Staged entries are exact rewrites, checked as such

Let `h` be an ordinary helper whose entrance frame is `E_h` and whose early reads add `±h/4` into four registers before
a cut `c`. A staged entry raises the entrance to `E_h + ⟨p⟩`, deletes those reads, and inserts releases after the cut
that realize the same linear map on every live input and dirty private buffer. In PR3949's construction the release
vector is `a = M_c v − e_h` with `v = e_h + w`, where `M_c` is the prefix matrix at the cut and `w` is orthogonal to
every consumer that could still observe it. Releases may land in any register, including another helper; that
extension is what makes the three entries here possible.

No identity is assumed. Each final word passes:

- PR3734/PR3945 hygiene, including the wrapper rule that no wrapper touches an entering or restored helper;
- the Lagrangian frame bill equal to its declared report;
- arbitrary-dirty forward, contragredient and cleanup-boundary semantics (`audit_core`, Sagar Thakrar PR3687);
- in the admission closure, the whole-word interpreter `audit_verify.semantics`, with 632 live inputs, 91 dirty
  buffers, a 723-dimensional matrix, reverse pull-back equal to forward and no buffer-to-live leak. Constructive
  controls must also be rejected: each omitted or sign-flipped release, each old entrance, a wrong bill and a wrong
  slice preimage, 17 per provider;
- fresh five-stage native replay: transport, ledgers, local replay, wrappers, and phases with all-column warp recipes.

The edit is finite literal data (`recipe/RECORD-*.json`). The opcode-level contract is checked independently by
`checks/independent_frames.py`. The B section of each provider loses exactly these twelve reads:

`600 → 183, 202, 175, 123`, `608 → 114, 137, 173, 121` and `609 → 114, 137, 173, 121`, each weighted `±1/4`.

It gains exactly these six releases:

`609 → 121 (+1/2)`, `608 → 137 (−1/2)`, `600 → 202 (−1/2)`, `600 → 602 (−1)`, `608 → 610 (−1)` and `609 → 610 (−1)`.

All other B operators, every A and restore operator, all native lenders and matrices, all returns, ports and removed
registers are unchanged.

## 2. Local bill

With exact optimal frames (`frames_exact.py`, written back and re-billed by `audit_core.frame_bill`), each provider's
local profile changes per call by

`ΔL = +6 H1 + 2 H2 + 5 H3 − 7 H4`,

with rank mass `6 + 4 + 15 − 28 = −3`, exactly the three removed width units. Helpers 600, 608 and 609 each go from
width 8 to width 7, giving inventory `5:28, 6:18, 7:56, 8:93, 9:213`.

## 3. Owner fill attaining the window-free optimum

**Target.** For the new inventory the window-free pattern LP (bins: 241,920 × 8; 161,280 each of 16, 32 and 48)
attains idle `{3: 23328 − 486, 5: 4320 − 2430, 48: 137952 + 486}`. PR3815's class-level Hall LP, with exact Hall
conditions per width over every call interval, gives the same optimum on this clock, so the time windows do not bind
in aggregate. No fill can do better than the window-free LP.

**Integer selection.** Each owner class (owner, capacity, window) keeps PR3945's pattern counts except for:

- exactly 486 changes `(9,9,9,9,9)` → empty in cap-48 bins;
- exactly 2,430 changes `(9,9,9)+5` → a zero-idle cap-32 pattern;
- any number of zero-idle → zero-idle changes among the cap-32 patterns `(9,9,9,5), (9,9,8,6), (9,9,7,7), (9,8,8,7),
  (8,8,8,8)` and the cap-16 patterns `(9,7)` and `(8,8)`.

Per-width global balance is imposed. For every width and every call interval, the slots of classes whose window lies
inside the interval may not exceed the new per-call supply times its length; this is Hall's condition, necessary and
sufficient for an interval transport. Rows are separated lazily and the final solution is re-checked exhaustively over
all 5,250,420 intervals for each width. HiGHS returns an integral selection of 14,904 changed bins in 78 class records (`owner/build/CHANGES.json`).

**Transport.** For each width, every bin owns a fixed number of slots, and each call must receive exactly the new
per-call count within the bin's owner window. This is an interval transport, solved as a min-cost flow with a segment
tree over calls: a slot staying at its old call costs 0 and a moved slot costs 1. Same-call collisions inside a bin
(two widths landing on one call) are repaired by exchanging call times with another bin's slot of the same width.
Same-family children of an owner have pairwise disjoint windows, which the checker asserts, so per-bin distinctness is
the full same-call family condition. Helpers are then assigned to slots per call by width, and offsets become compact
chronological prefixes.

**Result.** 70,876 roles move. `owner/verify.py` (PR3945's walk) checks all 1,321,920 roles in 725,760 bins and
reproduces the target idle exactly.

## 4. Complete profile and root

Starting from PR3945's complete profile, adding `3240·ΔL` and the idle change `{3: −486, 5: −2430, 48: +486}` (rank
mass `+9720 = 3·3240`) gives

`8061120 H1 + 2313360 H2 + 745362 H3 + 330480 H4 + 66690 H5 + 25920 H8 + 138438 H48`.

For `T = 360` the normalized moment `F(κ) = Σ_r n_r r (73/r)^κ − 896·360·73` is continuous and strictly increasing,
since every `r < 73` and every `n_r > 0`. Rational log and exp remainder bounds give `F < 0` at
`0.001730809033576552081734` and `F > 0` at `0.001730809033576552081735`. The same enclosures certify PR3945's
bracket `[0.001730663236534549309146, 0.001730663236534549309147]`. The padded endpoint
`0.001730809033576552081734 − 10^−46 − 10^−70` exceeds PR3945's certified upper bound by more than
`1.45797042002772587·10^−7`.

## 5. Scope

The new construction is the three staged entries, their exact frames, and the literal fill. Ordinary discovery,
parent lift, rebinding and outer release are the inherited engines, run end to end on these words and this fill
(`admission/`). The result stays conditional on the same universal/all-size source, hosting, recovery, tape, precision,
analytic and BIT hypotheses as PR3945. It establishes no unconditional multitape multiplication exponent, no change to
the repository's selected frontier, no new Lean theorem, and no independent human review.
