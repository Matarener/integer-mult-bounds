# R13 notes: dependency-respecting reorder ceilings on the PR4610 round-three word (no new kappa)

Base: PR4610 head 20bb93cd9 (Cao Yifan; same `research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz`
as 9fd59d9b, the later commits only add negative invoices). Worktree `~/imb-r13` (branch `r13-base`).
Frontier: kappa 0.0030217758, raw crossing 0.00302177587078 (reproduced by `tools/price.py`).
#4713 (Dugongue, Word RAM transfer) states the same 0.0030217758 and does not change the paid profile.
Tools: `~/imb-harness/r13/tools/`, run from `~/imb-r13` (python3.14 for the pure tools, venv12 for HiGHS).

## 1. Model (exact native semantics)
From `native_extensions.literal_replay` and `warp_merge.synthesize`:
- Rows are frame-independent. Each scalar op carries one frame. A scalar ADD needs both registers at
  that exact frame. A climb is a strict subspace inclusion and is paid at its dim jump. A warp is a
  fixed G-map with fixed (in, out) frames.
- Given frames on every op, the climbs are determined: per register, the chain of distinct frames.
  The cost is the sum of f(jumps), with f(x) = x^(1-C).

**Exact conflict poset (`tools/poset.py`).**
- Per register, each op has a type:
  - T: ADD target.
  - S: ADD or copy source.
  - X: scale, warp, clear, copy target or centre.
- T/T and S/S pairs commute exactly. `a+=cb` and `d+=ef` commute iff a != f and d != b. Every
  other shared-register pair conflicts.
- 17,701 ops form 11,833 commuting groups, with depth 515.

**Feasibility lemma (any linear extension).** Choose frames so that:
- ops in consecutive conflict groups of a register are nested;
- each register segment (a warp splits a register into segments) uses a chain of frames.

Then the stable topological sort of {conflict edges} plus {per-register frame-order edges} is acyclic.
Every edge is dim-nondecreasing, and a dim-equal cycle would consist only of program-order conflict
edges. So any such assignment is realizable (`tools/realize.py`).
- `realize.py` reproduces the current word exactly: 3290 climbs and the profile
  {1:2201,2:412,3:510,4:127,5:40,8:8}. It passes both retained interpreters on all 632 arbitrary
  columns (`native_extensions.literal_replay` + `verify_buffers.replay`).

**Subspace bounds valid for every linear extension (`tools/poset.py::bounds`).**
- lows(x) is the join of the start frames and the predecessor lows through conflict groups.
- ups(x) is the meet of the final frames and the successor ups.
- C0 ops are pinned; warps are pinned, or relaxed to free same-dim frames.

14,581 of about 17.3k frame-carrying ops are FORCED (lows = ups). Only 2,132 ops have a choice after
fixpoint pruning by forced-chain comparability (`tools/sdom.py`).

## 2. Ceilings (all of them keep the ADD program, the helper census and the 8 centre jobs)

| relaxation | local non-centre cost LB | root ceiling | tool |
|---|---:|---:|---|
| current word | 5253.11699 | 0.0030217759 | price.py |
| forced backbone only, fixed warps (exact LB) | 5244.412 | <= 0.003825 | backbone.py |
| forced backbone dims, free warp frames (exact LB) | 5240.324 | <= 0.004372 | backbone.py |
| poset + dims MIP, free warp frames (HiGHS optimal) | 5249.534 fwd / 5249.528 bwd | 0.0033076 | ceil.py |
| poset + dims MIP, pinned warps (HiGHS optimal) | 5250.467 | 0.0032280 | `PINW=1 ceil.py` |
| poset + dims LP (free warps) | 5247.908 | (lin. +3.8e-4) | ceil.py (LP) |
| exact subspace MIP, domains = op's registers' backbone frames ∪ current | **5253.11699 = current** | 0.0030217759 | construct.py |
| exact subspace MIP, domains = all backbone frames ∪ all current frames (fwd and bwd) | **5253.11699 = current** | 0.0030217759 | `construct.py medium` |
| exact subspace LP, full complete_interval domains (3.03M vars, 341k rows; IPM, P-D err 1e-9) | **5251.946** | lin. <= ~0.003107 (dC <= 8.5e-5) | `LPONLY=1 construct.py forward 0.00302 2400 wide` |

How to read the table:
- The dims MIPs are valid relaxations: every subspace solution projects to one. Their solutions do
  not lift. Greedy lifting of the pinned-warp optimum (`tools/lift.py`) hits 332 clashes: distinct
  same-dim frames get merged, and lower joins exceed the level. So 0.00323 to 0.00331 is an upper
  bound only.
- The exact subspace MIPs (`construct.py`) give a per-register-gap path over nested candidates,
  shared op frames, and dims-monotone conflict hubs. On both restricted domain families, both
  orientations, HiGHS proves (gap 0) that the current word is optimal.
- Conclusion for stages 1 and 2: reordering the existing ADD program (exact commutation) plus
  re-framing with the existing warps gives **no gain on the tested domain families**.
- The remaining large dims gap is an artefact of dropping subspace identity. Same-dim frames of
  different register groups are different subspaces, so they are not shareable.

## 3. Why the fragmentation is forced (blocker for stages 2 and 3)
- Helpers dominate the waste. Current helper climbs are {1:1513,2:201,3:432,4:50,5:12} (cost
  3464.74). Their forced backbone alone is already {1:1247,...} (cost 3458.82). Main x/y waste is
  about 1.4 units each.
- Typical mechanism (helper 300). `h300 += x19` sits in h300's T-group, and x19 is next WRITTEN by
  `x19 += h301` at x19's start line [273]. So ups(h300 += x19) = [273], and h300 must visit dim 1.
  Then `h295 += h300` is forced at dim 2 (430), and so on. Each helper is threaded through a chain of
  rigid co-framed reads and writes.
- Thin visits: 1005 helper intermediate frames carry a single op, and 590 carry two. Removing one
  visit is a 1+1->2 merge worth +3.05e-7 kappa (both orientations).
- Pure commutation cannot move them, because these ops are rigid in EVERY linear extension.
  Stage 3 would need non-commuting rewrites with correction terms. Examples:
  - `A+=cB ; B+=dE  ==  B+=dE ; A+=cB ; A+=-cd E`
  - `A+=cB ; D+=eA  ==  D+=eA ; D+=ec B ; A+=cB`

  Each one adds an ADD with its own co-frame requirement. In the h300 case, the correction
  `h300 += -c h301` can sit at frame 0, but `h300 += x19` then needs a common later frame of h300
  and x19. That cascades through h300's readers (h295, h490, ...), which need x19's contribution
  co-framed. Section 4 tests one-step versions of these rewrites; none gains.

## 4. Wide LP and stage-3 probes
- Full-domain exact subspace LP, forward, fixed warps: optimum 5251.9459 against 5253.1170 current.
  This is a valid bound: any reorder plus re-framing of the existing ADD program saves at most
  1.171 cost units per local (linearized dC <= 8.5e-5, so kappa <= ~0.003107).
  - The integer MIP (3.0M vars) does not get through HiGHS presolve probing.
  - On both restricted families it equals current, with gap 0.
  - The LP slack is presumably fractional path mixing. That is not proven.
- Greedy correction-rewrite screen (`tools/rewrite.py`). Each candidate is a one-step
  non-commuting swap with an exact correction ADD:
  - x is re-framed on A's visited frames;
  - the correction is placed on common visited frames ∪ {empty, full};
  - each candidate is scored by local chain cost, then by full `synthesize`.

  Results: 0 gains on all 1005 single-op helper intermediate visits (forward and backward), and
  0 on all 1466 single-op visits including main x/y registers (forward).
- MIP-reframed correction rewrites (`tools/mipeval.py`, medium-domain exact MIP over the whole
  rewritten program), on a sample of the first helper sites. Each feasible rewrite re-optimizes
  to exactly the current cost (gain 0). The majority are INFEASIBLE: the correction ADD forces an
  empty frame interval (lows ⊄ ups), because it couples two registers with no common admissible
  frame (e.g. `h224+=x0; x0+=x27` gives the correction `h224+=-x27` across two port lines).
  Counts: 36 feasible (all gain 0), 1 MIP-infeasible, 152 interval-infeasible (sample of 30 sites per worker x 5 workers, stopped early).

## Next steps
1. Multi-step correction rewrites. One-step swaps are either infeasible or neutral. A gain needs
   a coordinated rewrite of a whole helper thread, e.g. re-associating the sum carried by one
   helper so that it reads its port lines in nested order. Evaluate with `construct.py` medium
   (~20 s per program) and `realize.py`.
2. Close the LP gap of the full-domain model (1.17 units/local) with a decomposition. Per-register
   gap paths link only through shared op frames, so Lagrangian relaxation of the shared-frame
   rows is natural. This would either prove that the current word is the exact optimum of
   reorder+frame, or locate the fractional slack.
3. Resynthesis of the helper network, which is what the stage-3 brief describes. Fragmentation is
   forced by the order in which each helper's accumulated span grows (port lines in,
   hyperplanes out). A new design must choose helper factorizations whose spans grow in large,
   shared steps.
   - Any accepted single 1+1->2 merge on both orientations is about +3e-7 kappa.
   - Packaging: `realize.py` replay, phase check of new paid pairs
     (`warp-interface-20261022/verify_candidate.phases`), round6 strict compiler.
4. Free warps jointly with reorder: the dims ceiling rises only 0.00323 -> 0.00331.
