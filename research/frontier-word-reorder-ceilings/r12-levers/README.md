# R12 notes: lever screens on the PR4610 round-three productive-helper supplier (no new kappa)

Base: PR4610 head 9fd59d9b08ec (Cao Yifan), word `research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz`,
p16 query-thinned controller (`research/joint-helper-lattice/CONTROLLER.json`), pricer
`research/kappa-round6-compiler-tightening-20261022/arithmetic.py::assemble`.
Frontier: kappa 0.0030217758; raw crossing 0.00302177587078 (reproduced in floating point by
`tools/moment.py`). Tools are in `~/imb-harness/r12/tools/` and run from `~/imb-r12`.
All bounds below are floating-point screens. None is an exact certificate unless stated.

## 0. Accounting facts used by every screen
- M(C) = sum T_k k^(1-C) - sum P_r r^(1-C); dM/dC = -247,222 at the root, so a moment change
  dM gives dC = dM/247,222.
- Rank-mass surplus is 752 = 112*(2 + 30 windows - 15 thin) - 18*64. The local deficit is
  1856 = 224*8 (main transverse) + 64 (eight paid rank-8 owned-centre transports). In every
  admitted chain step (#4470, #4610, #4672) the helper and paid masses move together. All gains
  since #4470 are concave redistribution at fixed mass.
- Native semantics (from `kappa-rebuild/complex/native_extensions.py::literal_replay`):
  - Every paid job is a `climb` of one register to a strictly larger F2^9 chart. Its rank is
    the dimension jump.
  - A scalar ADD needs both registers at the identical frame.
  - Warps are free G-map transports.
  - Helper credit is final dim minus start dim.
  - Every one of the 632 registers climbs in 3-9 steps; this fragmentation is the entire
    concave loss.

## 1. Productive re-ranking (lever 1): dead
Finishing a rank-k helper as rank 9 adds 9-k rank mass to the targets. The mass invariant
means it must add at least 9-k paid mass. With #4416 padding semantics (one paid job on the
missing axes), the change is dM = f(9) - f(k) - f(9-k) < 0 by strict subadditivity of
x^(1-C).
- Per local type (x18): 4->9 costs -0.334 (dC -1.35e-6); 7->9 and 8->9 also lose.
- Paying with rank-one jobs loses more. 8->9 with one rank-one job gives dM = 17.83 - 18 < 0.
- The opposite move, splitting rank-9 helpers, wins (+1.35e-6 for 9->4+5). That would need
  a helper whose output is a product of independent fields, which no native form currently
  provides.
- A re-ranking gains only if completion costs less paid mass than the rank it adds. That
  would be a new circuit, not a completion.

## 2. Controller length scaling (lever 2): dead with the fixed local profile
- #4658 (Cinna Davis): exact, p <= 64, all splits, all native/thin subsets: C < 0.003022.
- #4659: all p, all binary full/query masks: best raw crossing is in
  (0.0030217758, 0.0030217759), attained by the existing p16.
- In closed form (my derivation), surplus(p) = 112(p+1) - 64(p+2) = 48p - 16. The growth of
  S = sum T k ln k - sum P r ln r outruns it beyond p16.

## 3. Query-thinning of idles and adapters (lever 3): dead or covered
- Idles are already maximally merged paid jobs of rank 8*len. Replacing an idle of rank 8s by
  rank-one queries costs 8s*f(1) - f(8s) > 0.
- Independent idle factors: #4664. Idle-free binary controllers: #4666. Typed A/B quotient
  query interfaces: #4660 and #4674 (surcharge >= 8*7^-C).
- Thin stages are already priced by #4659.

## 4. New screens: chart/order ceilings for the redistribution lever
All of these keep the helper census, endpoint dims and the eight centre jobs.

| relaxation | what is freed | ceiling (raw root) | tool |
|---|---|---:|---|
| single climb per register | everything except register masses | 0.0071457 | consolidate.py |
| keep ADD graph, free order + frames (dims only) | scalar order, warps | 0.0071108 | stab.py |
| fixed per-register order, decoupled registers | frames, warps, coupling of ADD levels | 0.0063826 | regdp.py |
| fixed global order, coupled, dims only (free warps) | frames/warps only | LP: local paid cost >= 5297.54 vs 5316.72 current (saving <= 19.18/local, linearized root <= ~0.0044) | dimlp.py |
| current admitted word | (none) | 0.0030217759 | moment.py |

How to read the table:
- The first three rows show that the add graph and per-register order constrain little.
- The binding constraint is the coupling: both ends of an ADD share one frame, under
  monotone climbing in a common time order.
- Row 4 is the right relaxation for "new warp gauges / native maps at fixed scalar order".
  The gap between rows 4 and 5 is what exact-frame rigidity (available G maps) costs.
- A full MILP on row 4's model (170k binaries, 516k rows; LP via HiGHS IPM without crossover, 624 s; primal objective, so not a certified dual bound) did not beat the current word's
  cost in 900 s with HiGHS single-thread. Its incumbent local cost was 5318.99, against
  5316.72 for the current word.

## 5. Other levers considered
- Centre amortization: merge the 18 sequential centre transports per centre index into one
  rank-144 job. The fixed-mass ceiling is dM = 1152(8^-C - 144^-C) ~ 10.1, about +4.1e-5.
  It is illegal: each centre call reads and writes main data inside its local (#4698 shows
  z_out = z_in + h + R_X X), so the transports neither commute nor sit idle. #4700 proves the
  64-per-local floor under monotone chart retiming. The centre is the dominant waste: 1152 of
  surplus against 752 actual, and removing it gives 0.00806 (#4659). It is under active attack
  by 1337isnot1337 (#4694, #4698, #4700).
- Query/local fusion: fuse each rank-one query with an adjacent rank-one local climb on the
  same register, on disjoint axes. The ceiling is 1680(2 - 2^(1-C)) ~ 7.0, about +2.8e-5.
  Query copies live in an owned temporary Z that is erased, with no common frame with the
  local's climbs. Not realizable without a new native interface.
- Compiler-only: the raw crossing is 7.1e-11 above the claimed 0.0030217758, so a further
  reserve tightening could state about 0.00302177586. This is not a lever, and #4610 round6
  already marks it as numerical-only.

## Conclusion
No lever beats 0.0030217758. The quantified headroom is in climb fragmentation (rows 1-4), and
only a changed scalar circuit or order can reach it, because frame-equal ADD coupling forces
the fragmentation. The next concrete step is a coupled-relaxation solve restricted to one
connected block of the add graph, with exact G-map availability, to locate which registers'
fragmentation is forced by order rather than by available warps.
