# Productive-helper paradigm digest (R12, 2026-10-22)

Base for all numbers: PR4610 head 9fd59d9b08ec (worktree ~/imb-r12, branch pr4610).
Frontier: #4610 kappa 0.0030217758 (round6 compiler tightening of the round-three word);
raw crossing (0.00302177587077, 0.00302177587078). #4635 (Word RAM) 0.0030217754 is lower.
Selected main still 0.00302015 (#4470 / joint-helper-lattice).

## 1. Accounting (how kappa is computed)
- Saving C solves M(C) = sum_k T_k k^(1-C) - sum_r P_r r^(1-C) = 0 (T = productive targets, P = paid
  recursive jobs, ranks = Gaussian ranks / axis counts). kappa = slightly below the raw root after the
  strict compiler (paid tensor completion #4416, splitting at c^v, higher-moment tails #4433,
  v=1024, c=20, b=21, u=1/5, contraction reserve now 1e-11; finite integer threshold j, H, N=2^H).
- Code: research/kappa-round6-compiler-tightening-20261022/arithmetic.py
  `assemble(local)` builds (T,P) from the p16 controller: for each physical event
  LOCAL -> T += helper census H, P += local paid profile N; QUERY_SHEAR -> P[1] += 112;
  IDLE(stages) -> P[8*len] += 224; diagonal term -> T[1+8*sum] += 112.
  Exact intervals: research/higher-moment-strictification/verify.py (E.moment),
  second engine research/kappa-rebuild/architecture/mixed_target_probe.py.
- Quick float pricer: ~/imb-harness/r12/tools/moment.py (run from ~/imb-r12 with python3.14 -B);
  marginals: ~/imb-harness/r12/tools/marg.py.
- Current invoice (PR4610 round3): local paid N={1:2201,2:412,3:510,4:127,5:40,8:8} (3298 jobs,
  mass 5327); helpers H={4:28,7:7,8:47,9:326} (408, mass 3471). Controller p16, a=7 prefix pairs,
  18 LOCAL (full native), 15 QUERY_SHEAR, 15 IDLE, 90 ADD, 16 SIGNED_SWAP; ambient rank 145.
  T={4:504,7:126,8:846,9:5868, 17..65 step 8: 448 each, 73:224, 145:224};
  P={1:41298,2:7416,3:9180,4:2286,5:720,8:144, 16..64 step 8: 448 each, 72:224}.
  10,928 productive fields, 64,404 paid calls.
- Rank-mass ledger (KEY INVARIANT): surplus sum T k - sum P r = 752 =
  35840 (diagonal 177408 - idle 141568) - 18*1856 (local deficit) - 1680 (queries).
  Local deficit 1856 = 224*8 (main D_s transverse work) + 64 (eight paid rank-8 owned-centre jobs,
  no productive credit). Helper/native MILPs (#4470,#4610,#4672) move helper and paid mass
  TOGETHER (deficit unchanged); gains are purely concave redistribution.
- Linearization: M ~ 752 - C*S, S = sum T k ln k - sum P r ln r; dM/dC = -247222 at root.
  Marginal dC per local-type change (x18 copies): remove one paid rank-1: +7.28e-5;
  free helper rank +1 (8->9): +7.2e-5 (but violates mass invariant); paid 4+4->3+5: +5.5e-8;
  merge paid 1+1->2: +3.05e-7; split helper 9->4+5: +1.35e-6; drop the 64 centre charge: C~0.00806 (#4659).

## 2. Structure
- Native local word: research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz
  (canonical: v=112 ports, h=9, 632 start/final columns, 4429 frames, 72 warps, 180 warp edges;
  programs forward/backward 21449 ops). 408 helpers arbitrary independent inputs; 1 owned centre
  reused sequentially (8 centre calls, rank 8 each).
- Controller (#4440 query-thinned): paired path, 2p+1 stages, full native at {0,2p} u odd, other
  stages replaced by rank-one query shears S_y(Q^-1)/S_x(-Q) (1 paid rank-1 per port); idles drop
  thin-stage multipliers. Code: research/query-thinned-controllers/controller.py (keep_mask,
  thick_stages, inventories, replay_events); p16 pinned in research/joint-helper-lattice/
  {CONTROLLER.json, verify.py:controller16}.
- Boundaries: exact rational L A R = diagonal check over Laurent coefficients (32x32), verify.py.
- LP column generation / controller discovery (#4359): research/kappa-rebuild/architecture/
  {controller_menu_search.py, mixed_forest_search.py, mixed_target_probe.py, controller_tariff.py};
  DP over native/thin stages: research/kappa-hybrid-controller/search/direct_stage_dp.py.
- Helper/native MILPs (#4610): research/kappa-round3-warp-20261022/{line_free_milp.py,
  helper_line_milp.py, both_boundary_milp.py} (HiGHS, 1.6-2.0M vars, --operator all --seconds 180).
- Hyperplane-retiming min-cut search (#4672): pr4672 research/hyperplane-retiming/search/*.py.

## 3. Admission checks (what a new supplier must pass)
all-632-column arbitrary-input replay both orientations (two interpreters); exact Clifford
admission of changed native G maps with absolute phase on 512 columns; warp classes; helper
boundaries; controller Laurent factorization; two rational moment engines; strict compiler +
54 outer predicates; mutation controls. Registered replay:
`python3.12 -B scripts/research_package.py --package research/<pkg> [--check-only]`
(PR4610 packages themselves were run with python3.14; joint-helper-lattice is registered).

## 4. Levers already used / closed
Used: productive helper jobs + mixed balance (#4359), paid target padding (#4416), native tensor
strictification (#4412), p6 native controller (#4414), query thinning p17->p16 (#4440), helper
retiming (#4441), contact span (#4447), joint helper entrance/exit lattice MILP (#4470),
joint helper entrances + native maps (#4610 round3), compiler reserve 1e-9 -> 1e-11 (#4610 round6),
helper621 chart (#4626, does not combine), hyperplane retiming (#4672, round-two only; its
round-three screen found nothing).
Closed (proved no gain): any pair count / split / full-vs-thin mask with fixed profile (#4658 p<=64
exact, #4659 all p: root < 0.0030217759); independent idle factors (#4664); idle-free binary
controllers (#4666); paid symmetric phase changes on 4610 word (#4696); typed A/B quotient (#4654
-> #4660, #4674 surcharge >= 8*7^-C); ambient quotients (#4596/#4629/#4633 closed, #4655);
centre rank floor 64 under monotone chart retiming (#4700); scalar trace compression no moment
change (#4692). Active (1337isnot1337, today): centre interface (#4694 640-field, #4698 helper
normal form) -- the 64-per-local centre charge is the dominant waste.
