# Actual Gaussian production positivity and matrix perturbation

The actual ProductionPlan guards, together with the cited scalar enclosure
[PR6085](https://github.com/CrocSwap/integer-mult-bounds/pull/6085) at
9fc80f1db55d4939c7b53c0799e6840cce35fbf8, imply every rounded similarity weight
is >2^(-8p-1). [PROOF.md](PROOF.md) proves the unchanged Axis.matrix_entry
consumer differs from its ideal truncated original-coordinate matrix by
less than p*2^(16p+4)*2^-P in infinity norm, stronger than the requested
p*2^(16p+7)*2^-P. It handles exact diagonals, holes, same-cell ratios,
cross-cell coefficients and physical-period cuts explicitly.

The scalar result is a cited mathematical dependency, not replayed or imported
pending bytes. All live scientific inputs are from main721c03822. This does
not discharge analytic_recovery or the selected frontier's five assumptions.

## Reproduction and evidence

Python3.12, standard library only, from repository root:

```
python3 scripts/research_package.py --package research/gaussian-production-matrix-guard
```

Direct export replay: `python3 -I -B research/gaussian-production-matrix-guard/verify.py`.
The checker authenticates live source hashes before imports, executes the actual
encoded ProductionPlan metadata example, and calls unchanged Axis.matrix_entry
with supplied rational coefficient fields. These fields exercise the consumer;
they are not a full Axis construction or production coefficient page. Exact
rational identities on 150 retained pairs, 3,645 denominator-sensitive scalar
perturbations and five failure controls corroborate the proof. The actual
consumer fixture executes 64 entries; the metadata fixture has seven rejection
controls. Normal and
optimized registered commands use explicit checks surviving Python -O.

## Open next questions

Bind the ideal truncated matrix to the intended infinite/periodized ideal
matrix with the claimed 2^-46p tail, then establish its uniform rowgap before
asserting production Axis admission. Start with physical-period seams and the
exact nearest convention in this proof. The retained ideal estimates and their
actual source hypotheses remain blockers. LU/Schur, online accuracy, complete
production pages and physical total cost remain separate obligations.

## Credit and scope

JoyboyBrian, with substantial OpenAI Codex assistance; Apache-2.0. Credit
Jose Manuel/jmbarrancoml PR3851 for the physical producer and original
precision/phase-cell argument; JoyboyBrian PR6085 for the scalar audit;
James Reed's gaussian-gauge-column for the distinct conditional column
argument; mihir-s-05 PR4449 for abstract across-cell rounding; RaD/hipotures,
Chafik Boukhalfa and the preserved Gaussian/physical-word lineage. No frozen
source is modified. Written proof and finite checks are by the same AI-assisted
contributor, not independent human or formal-kernel acceptance. No new kappa.
