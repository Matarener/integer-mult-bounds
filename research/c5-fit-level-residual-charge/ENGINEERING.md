# Engineering notes

## Choices

- Reuse the authenticated C5 geometry loaders and 23-cycle census pattern from
  the termwise charging obstruction, with `HERE.parents[1]` as the repository
  root and `need()` (not assert) for all proof gates so `-O` admission holds.
- Primary scanner uses packed bit pivots; the independent scanner uses dense
  GF(2) elimination and an iterative chordless-path C5 census.
- The diagonal identity is checked by assembling the 112-by-112 matrix and by
  summing per-term plane self-ranks equal to 2.
- J-bearing extensions are checked only to record that they do not discriminate
  the residual-local-opt candidate; they are not used as the counterexample.

## Rejected alternatives

- Re-proving commoncut35: already on main as `research/p112-mixed566-cut35`.
- Recomputing the termwise `180/7` ceiling: already published.
- Using only the J-identity extensions as tests of `(*)`: they pass numerically
  for cost reasons and would falsely suggest the candidate works.

## Runtime

All three registered commands finish well under their 120-second budgets on
CPython 3.12 with the standard library only.
