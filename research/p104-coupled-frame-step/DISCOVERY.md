# Discovery and source credit

The construction uses DreamingOfClouds's event-lattice model from PR5568,
exact commit `47a347ff70044615e7be6581d275d12f5df38295`. That package
reports a small retiming gain on PR5561. Its model and reported gain are
prior work, not a discovery claimed here.

A first composition on PR5580 passed the complete registered checks at
kappa .00308191. Before publication, a fresh PR check found Pierre-Loic
Doulcet's larger PR5565 cascade. The first candidate was preserved locally;
it is not the contribution submitted here. The search was transferred to
PR5565 at `9af814164b9dfc21f19ec737959d67cb71488c95` without changing
its scalar order.

The new run used OR-Tools 9.14.6206 on CPython 3.12.13, four solver workers,
90 seconds, neighbor radius two and all intermediate subspaces in anchor
quotients of dimension at most three. Its command structure was:

```sh
HEAVY_THREADS=4 python3.12 -B evlat.py PR5565-WORD.json.gz witness.json.gz 90 2 3
```

The status was `FEASIBLE`. The fast legality check passed and the re-price
was about 0.003085951751. The solver was not an optimality proof, and its
parallel output is not promised to be deterministic.

The output changed 26 event/endpoint nodes in 20 independent components.
Only one component changed the moment: three ADD charts and helper 307's
final chart. The submitted construction retains exactly that component.
CHANGES.json fixes its four source sites and the new three-dimensional
frame. No solver is needed to reconstruct or verify it.

Earlier scratch, compensated-scalar, fixed-order and commuting-ADD screens
found no paid-profile gain. Those searches are not submitted as exhaustive
obstructions. In particular, the independent owned-holder obstruction
belongs to PR5579. The submitted claim is this explicit frame step on the
newer cascade, its written chart proof and its complete exact certificate.
