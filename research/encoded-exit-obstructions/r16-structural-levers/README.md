# R16 notes: structural levers against the fixed-profile ceiling U = 0.00302728825 (no κ claim)

Goal: a conditional κ above U = 0.00302728825 from a real change to the paid/target structure of the
supplier, not from compiler headroom. Base: selected #5413 profile (see `PROFILE.json` of #5428). Its raw
root is 0.00302728824993955878 and dM/dC = −246,768.15 (`tools/price16.py`, Decimal, 50 digits; this
matches #5428's bracket). U sits only 6×10⁻¹⁴ above that raw root. **So any genuine paid-profile
improvement beats U**, even a single 1+1→2 merge in one orientation of one local (about +1.7×10⁻⁸).
The bar is not size. It is whether the change is legal.

**Outcome: no lever survives.** Nothing was built. Two exact screens are new here: the helper-split
screen and the ZQY-observation screen. The rest are pricings with Decimal arithmetic of known blockers.

## Lever table (selected profile; float/Decimal screens unless marked exact)

| # | Lever | Optimistic ceiling (raw root) | Verdict / blocker |
|---|---|---:|---|
| 1 | Split a rank-9 productive helper into independent products (9→4+5) | +1.358e-6 per split (×18 locals); all rank-9 helpers split: 0.0035309 | **Dead on the #4610 word (exact screen, new).** A free split needs a moment, at an intermediate frame with climbs still ahead, when the helper's row is pure (only its own input) and no other register (C0 included) holds its input. `tools/split.py` finds **0** such points in both orientations. The positive control passes: the final rows equal the expected rows for all 632 registers in both orientations. 38 helpers are clean inside their op span, but only at end frames. A non-free split leaves the outputs coupled, e.g. (−x_b, G₉x_a + G_{9/F}x_b). Decoding those is the relation/coupled-output lever, which is exhausted (#5462: exact optimum is 8 per backward local). |
| 2 | New helper factorization so frames grow in large shared steps (defragmentation) | helpers one climb each: 0.0049895 (#5426 re-optimised controller: 0.0051074); mains one climb each: 0.0037079 (#5426: 0.0037103); Λ=0: 0.0081386 (#5426) | **Blocked: needs a new operation set.** At a fixed operation set it is closed: #5426 (exact, single-level drops, any order), #5422 (no H1+H1→H2 fusion by free rewiring), #5465 (reorder+reframe LP ≤ 0.003107; restricted MIPs gap 0; one-step correction rewrites 0 gains). There are also no end slack climbs: every helper and main register starts and ends at the frame of its first and last op (`tools/ends.py`). Helper threads are compute/uncompute chains: each reads a port line at a low frame and undoes the read at the full frame (e.g. h300: x19 at dim 1, x18 at dim 3, uncompute at dim 9). Fragmentation is set by the order in which those port lines climb. A redesign is a new native word with a new replay, new phases and a new caller pipeline; it does not fit in 3 hours. No ceiling smaller than 0.0049895 is proved for new operation sets. |
| 3 | Paid merges by local rewrites (1+1→2) | +3.06e-7 per merge (×18) | Closed by #5422/#5426/#5465 (see row 2). |
| 4 | Encoded-output exit of #5402's coupled modes by buying b = ZQY (#5428 target 1, #5415) | b free: 0.0071410 (+4.1e-3). Break-even: X ≤ **63** H1 per backward FULL (16 FULLs) on top of the 8 restoring H1 (`tools/zqy_budget.py`) | **Dead in the sum-then-query grammar (exact screen, new).** b_k = Σ_j M_kj/2 · Km_k⁻¹ Kp_j Q Y_j. Using the repository's `clifford_exact` evaluator with absolute phase: no Kp_j or Km_k commutes with Q or with D. The 112 port conjugates Kp_j⁻¹ Q Kp_j lie in 112 distinct monomial cosets, left and right (all pairwise quotients have rank 2). Per mode, the 56 supported ports give 56 distinct classes. So no two Y_j can share one rank-one query, even with free monomial maps on both sides. b needs ≥ 112 + 8 = 120 H1 per FULL, which is exactly #5415's constructive bound and far above 63. #5427 already shows that b is absent from every retained observation. Open: producing b by a non-termwise mixture of higher-rank jobs is not covered by this screen. |
| 5 | Larger coupled type (more modes sharing the port support), bought exit | needs ≥ **15** modes per FULL to pay at 112+m H1 (`tools/modes_budget.py`: m=14 gives 0.0029741, m=15 gives 0.0034798) | **Dead in the #5402 family:** the modes come from the 8 centre calls per local (one per centre-deletion cache), so m ≤ 8. |
| 6 | Free observation: delete query shears | delete all 1680: 0.0099; one H1 per local (×18): +7.3e-5 | Mass is not conserved, so this is not a real lever. Every thin query stays paid (#5415). No paid response can be reused (#5427: 0 of 3,298 climbs per orientation, 0 of 63 caller outputs). Control (`tools/zeroclimb.py`): no climb acts on an identically zero row in either orientation. |
| 7 | Query/local fusion (rank-1 query + adjacent rank-1 local climb) | 1680×(1+1→2): +2.88e-5 | Illegal without a new native interface: the query temporary shares no frame with the local climbs (R12 §5). |
| 8 | Centre: merge the 8 rank-8 transports of a centre index; remove the centre | merge: +4.10e-5 (illegal, #4698/#4700); removal: 0.0076685 | Contested (#4694/#4698/#4700/#4888). Out of scope by instruction. The uncontested variant is a productive centre payload. It fails because each of the 8 centre transports is a single 0↔rank-8 move (backward 0→8, forward 8→0; checked on the word), and owned C0 is CLEARed and COPY-filled before every use. No independent input survives a transport to earn credit, so the credit is 0. |
| 9 | Controller length / thinning / idles with the fixed local profile | — | Closed: #4658/#4659 (all p, all masks), #4664/#4666/#4674, #5405, #5429. |
| 10 | Multi-type recursive supplier (#5428 target 5), vector index code (#5428 target 3), decoder factorization (#5428 target 4) | not priceable without a concrete histogram | No candidate type pair or mask could be built and priced within this session. #5428 records the known failures: the 3\|7 macro is only a scheduling saving, and the phase-accumulator closure is critical before wrappers. |
| ref | p19 coded-reverse chain (#5270/#5440) | 0.0034 claimed | Failure modes (reviews by Matarener, zxv, gvconly, jwr404, Clear1nsight): the native call supplies D, not R = DQ. The missing Q costs 4,256 rank-1 jobs per unit, and the Q-conjugated terminal gauge is forced. The replay was compared against an operator different from the priced controller, and it reused the same nine axes while crediting fresh blocks. The compiler constants were inherited from the p7 unit shape. Lever 4's coset obstruction has the same form: Q does not pass through the port normalizers. |

## What would have to be true for a gain
- A new native operation set, not a reordering of the existing one, in which helper threads read port lines at
  frames they already visit. Every 1+1→2 merge it buys is worth +3.06e-7. It must come with a complete replay
  of all 632 columns and a new caller pipeline (#5383→#5402→#5413), because the owned relations are pinned
  to helper rows.
- Or an observation producer for b = ZQY that is **not** a termwise sum of conjugated queries, costing
  ≤ 63 H1-equivalent rank mass per FULL. The coset screen rules out the termwise route.

## Tools (`../tools/`, run with /opt/homebrew/bin/python3.12; inputs read from ~/imb-r13 (#4610 word) and ~/imb-r16 (upstream main 32890bc5d))
- `price16.py`: Decimal pricer for the selected profile. `levers.py`: the ceiling table (output in `levers.txt`).
- `split.py` and `split_ctl.py`: exact row replay for the free-split screen and its controls (`split.txt`, `split_ctl.txt`).
- `ends.py`, `thread.py`: end-slack census and per-register thread dump.
- `zqy_budget.py`, `modes_budget.py`: exit purchase budgets. `zqy_commute.py`: Clifford coset screen (`zqy_commute.txt`).
- `zeroclimb.py`: control showing no climb on a zero row.

Credits: Cao Yifan (#4610 word), zxv (#4359 paradigm, #5415, #5428), Dillon Amburgey (#5402 provider),
Ali Romman (#5383/#5398 relations and caller), Chris R / Clear1nsight (#5413 caller, audits), Matarener
(#5422/#5426/#5427/#5433), Cinna Davis (controller line), reviewers of #5270/#5440. Prepared with Claude Opus 5.5
(Anthropic) via Claude Code, directed by Joel Pulikkan (GamingPuzzled).
