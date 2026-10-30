# Validation, coverage and limits

## What was run

`verify.py` performs, on every invocation:

1. All `64` Q8 group products compared between two independent
   implementations: a basis bit-arithmetic product and a signed-unit table
   (`group_product` and `hamilton`). Any disagreement rejects.
2. Direct algebra checks `i^3 = zi`, `j^3 = zj`, `z^2 = 1` in `F2[Q8]`.
3. Eight explicit witnesses replayed to their exact diagonal endpoints,
   recomputed from the paid-factor definition. Each witness's call count is
   compared with the parity-rounded `11t/5` bound computed independently.
4. Five complete breadth-first searches, replayed from the identity matrix:
   one role to length `2`, two roles to length `5`. Each enumerates **every**
   legal word in its domain and must report exhaustion without reaching the
   target, and without hitting the state cap.

Typical wall time is about 1.2 s single-threaded on CPython 3.12, macOS/arm64.
State counts reached: `6` for the single-role cases and `56,084` for each
two-role case.

## What this does and does not cover

Covered exactly:

- Minimum paid-call count `3` for `t = 1` (both `zi` and `zj`), and `6` for
  `t = 2` (all three target splits). The lower bound is role-free, so these
  minima are complete over all role counts.
- The uniform `11t/5` constant is attained at `t = 1` and `t = 2`.

**Not** covered, and not claimed:

- `t >= 3`. The minimum for `t = 3` is in `{7,9}` and for balanced `t = 4` in
  `{10,12}`; neither is decided here.
- Any role count above `2` in the exhaustive census. The exhaustive receipts
  are a cross-check of the model and the witnesses; the theoretical bound
  supplies completeness at `t <= 2`.
- Any physical cost. No scalar, routing, restoration, hosting, precision,
  recursive or supplier-admission cost is computed.
- Any improvement to the selected kappa `0.001672660197076918`.

## Recorded search failure

A separate randomised hill-climbing search (not part of `verify.py`, not
committed as evidence of absence) looked for a ten-call balanced four-target
word. Configuration: 18 independent runs across `4`, `5` and `6` roles,
random restarts, 400 mutation iterations per restart, objective = Hamming
distance from the target diagonal in the group basis. Best cost reached was
`6`; no cost `0` was found. An independent ten-call-style search was also run
at twelve calls as a positive control and reached cost `8`, so the search is
**known to be weak** and its failure is recorded here only to prevent a later
reader from mistaking it for evidence. It excludes nothing.

## Code constraints

Standard library only. No Git object, no network access and no third-party
package is required for scientific replay. `assert` statements are not used;
every check goes through `require`, so `-O` does not weaken the verifier.
Assumptions are `require(len(a) == len(b), ...)` and `strict=True` so that
Python 3.12 rejects malformed replay inputs.

## Unrun obligations

Lean, Docker, the selected full cold replay (`make frontier1094-verify`),
independent human review and formal proof-kernel acceptance are all unrun.