# Plane-port clique savings need an odd cycle shared by both term types

**Scoped proof. No new κ.** The selected conditional exponent is unchanged.

For the strict plane-port decoder of Mark (Matarener)'s
[PR #5560](https://github.com/CrocSwap/integer-mult-bounds/pull/5560)
(`research/plane-port-global-rank-dual`), spectral condition E3 shows that a
clique `S` cannot save below 2 per port when its cross terms are bipartite.
This package sharpens that condition. On `S` the cross sum `N` equals `I`
minus the diagonal-term sum. Every nonzero off-diagonal block of `N` is
therefore reached by a cross term **and** by a diagonal term with the same
orientation:

    supp N  ⊆  G_cross ∩ H_diag.

A saving on a clique therefore needs an odd cycle of planes in both term
graphs. In particular, a bipartite diagonal-term graph excludes a saving,
whatever the cross terms and coefficients, in every characteristic other
than 2. On a 3-clique, diagonal terms must reach all three plane pairs.

The statement and proof are in [PROOF.md](PROOF.md). The bipartite step is
E3's argument. The inclusion into the diagonal graph is new.

## Evidence

[verify.py](verify.py) authenticates the E3 text it sharpens by SHA256. Over
exact rationals it then:

- builds 400 seeded decompositions of `I_6` on three planes. Each has random
  multi-plane terms, completed by an exact rank factorization of the
  remainder. For every decomposition it checks `supp N ⊆ G ∩ H`, at least
  `6 - m` diagonal terms, and, when `supp N` is bipartite, `dim ker(I+N) = m`
  and `2m <= rank N`;
- checks a triangle control. Three single-source cross terms with
  `N = I - J` on one coordinate per plane give `rank N = 3` and `m = 2`. The
  spectral inequality alone therefore admits a triangle, and the lemma forces
  diagonal terms on all six directed pairs.

The random decompositions corroborate the proof. They are not a census.

## Reproduce

From the repository root, Python 3.12, standard library only:

```sh
python3.12 -B scripts/research_package.py --package research/plane-port-clique-odd-cycle
python3.12 -B research/plane-port-clique-odd-cycle/verify.py
python3.12 -O -B research/plane-port-clique-odd-cycle/verify.py
```

Each prints `PASS_PLANE_PORT_CLIQUE_ODD_CYCLE` in well under a second.

## Limitations

This is a necessary condition only. It does not decide the 224 conjecture, the
global floor 140, or any open three- or four-plane class. It does not price
the multi-plane diagonal terms that a triangle forces, and it does not cover
native realization, hosting or κ. The proof is written and has not been
checked in a proof kernel.

## Open next questions

1. **Price the forced diagonal terms.** On the open three-plane classes of
   `three-plane-rank-dual`, a saving now needs diagonal terms reaching the
   expensive plane pair. Bound their tariff excess against `2m - Σ t_j`.
   First tabulate, for each open class, the cheapest diagonal support reaching
   each pair.
2. **Directed refinement.** The inclusion is directed. Does a saving need a
   directed odd cycle, or can the eigenvalue argument use orientation
   further?
3. **Global use.** Feed the bipartite-diagonal exclusion into a clique
   programme as a structural cut, rather than another LP column.

## Credit

The contract is CubeJerry's (#4365). The global floor, spectral condition E3
and the 224 conjecture are Mark (Matarener)'s PR #5560. The three-plane
classes are Ryanson Jonathan's `three-plane-rank-dual`. This package, produced
by Nick Petalas, adds only the diagonal-graph inclusion and its consequences.
Apache-2.0.
