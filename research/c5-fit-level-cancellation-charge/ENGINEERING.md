# Engineering notes

## Choices

- Reuse the authenticated C5 geometry loaders and 23-cycle census pattern with
  `HERE.parents[1]` as the repository root and `need()` for all proof gates so
  `-O` admission holds.
- Primary scanner uses packed bit pivots; the independent scanner uses dense
  GF(2) elimination and an iterative chordless-path C5 census.
- Named-support domination is checked with integer weight lifts (`weight16`
  summing to 36) and precomputed 5-plane local rank tables so the 2.5M-rectangle
  census finishes in seconds on CPython 3.12.
- Diagonal and J-extension fixtures certify the J-free and one-J corollaries
  without reprinting the residual/local-opt `460 > 224` arithmetic as a charge.

## Rejected alternatives

- Rescaled residual-local-opt `sum Cost_opt(K|_C) <= (115/56) Cost_opt(K)`:
  thin rename of #3639's diagonal arithmetic; excluded by donor instruction.
- Diagonal-only incidence LP targeting floor 70: fails domination on many
  two-plane rectangles that named OD/P terms actually use.
- Uncredited termwise on all rectangles with these weights: blocked by
  `ρ = 303/16 > 9`, recovering no improvement over the classical method.

## Runtime

Primary verify and the independent census each finish well under their
VERIFY.json budgets on CPython 3.12 with the standard library only.
