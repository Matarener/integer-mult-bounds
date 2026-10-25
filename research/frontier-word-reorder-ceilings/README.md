# Lever ceilings on the #4610 round-three productive-helper word (no κ claim)

Two screening rounds on Cao Yifan's #4610 word (`research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz`,
κ 0.0030217758). The word is unchanged in the current #5413 caller, so these bounds still describe it.
They say where the remaining headroom is *not*, so that effort goes elsewhere. Unless a line says
"exact", every bound is a floating-point screen and not a certificate.

## Summary

| Lever | Result | Where |
|---|---|---|
| Productive re-ranking (finish rank-4/7/8 helpers as rank 9) | loses for every k by strict subadditivity of x^(1−C): dM = f(9) − f(k) − f(9−k) < 0 (4→9: dC ≈ −1.35e-6) | `r12-levers/` §1 |
| Longer controllers, query thinning | already closed by #4658/#4659 and #4664/#4666/#4674 | `r12-levers/` §2–3 |
| Centre merging; query/local climb fusion | worth ≈ +4.1e-5 and +2.8e-5 if legal, but not legal (#4698/#4700; the query temporary shares no frame) | `r12-levers/` |
| One climb per register (fragmentation fully removed, same masses) | ceiling 0.0071457 | `r12-levers/` |
| Reorder freely + re-frame, keeping the ADD graph | ceiling 0.0071108 | `r13-reorder/` §2 |
| **Reorder within the exact commutation poset + re-frame** (dimension-only MIP, HiGHS optimal) | 0.0033076 (free warps) / 0.0032280 (pinned warps); **does not lift to real subspaces** (332 clashes) | `r13-reorder/` §2 |
| **Same, exact subspace LP over full frame domains (3.03M variables)** | local cost ≥ 5251.946 vs current 5253.117, i.e. ≤ 1.17 units per local, **κ ≤ ≈ 0.003107** | `r13-reorder/` §4 |
| Exact subspace MIP on restricted and medium frame domains (forward and backward) | **optimum equals the current word (gap 0)** | `r13-reorder/` §2 |
| One-step non-commuting swaps with exact correction ADDs | 0 gains (1005 + 1466 greedy sites; 36 MIP-reframed feasible rewrites all at exactly the current cost; 153 infeasible) | `r13-reorder/` §4 |

**Takeaway.** Each of the 632 registers climbs in 3–9 steps, because a scalar ADD needs both operands
at the identical frame. That fragmentation is the whole concave loss. Reordering within the true
dependencies and re-choosing frames can remove at most about 1.17 cost units per local. The helper
frames forced in *every* valid reordering already cost 3458.82 of the helpers' 3464.74. What remains
needs a redesigned helper factorization, not reordering or local rewrites. Our #5462 shows the
owned-relation lever is also at its optimum.

## Contents
- `r12-levers/`
  - `README.md`: notes.
  - `DIGEST.md`: a working digest of the productive-helper accounting, with commands.
  - `tools/`: `moment.py` reproduces #4610's raw crossing; `marg.py`, `consolidate.py`, `stab.py`,
    `regdp.py`, `dimmilp.py`, `dimlp.py`.
- `r13-reorder/`
  - `README.md`: model, ceilings, why the fragmentation is forced, and probes.
  - `tools/`: `poset.py`, `ceil.py`, `sdom.py`, `backbone.py`, `construct.py`, `realize.py`, `rewrite.py`,
    `mipeval.py`, `lift.py`, `price.py`, and others.
  - `logs/`: solver logs, renamed `.txt`.
  - `data/`: gzipped MIP/LP solutions.

`realize.py` rebuilds the current word exactly from the poset model and passes both native
interpreters on all 632 arbitrary-input columns. That is the positive control for the model.

**Running the tools.** They expect a checkout of #4610 (head 9fd59d9b) as the working directory, and a
few contain absolute paths from the machine that produced them; adjust those paths before running.
Python 3.12+ with numpy, scipy and highspy.

**Credits.** Cao Yifan (#4610 word and native semantics), zxv (#4359 productive-helper paradigm, native
and compiler machinery), Cinna Davis and 1337isnot1337 (#4440/#4441/#4447 controllers; #4658/#4659),
#4664/#4666/#4674/#4698/#4700, Dugongue (#4713), aliromman and Clear1nsight (#5383/#5413). Prepared by
Joel Pulikkan (GamingPuzzled) with Claude Opus 5.5 (Anthropic) via Claude Code. Apache-2.0.
