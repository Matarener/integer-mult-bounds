# Sharp tensor gap with variable productive boundaries

This scoped proof determines a signed subspace-distance invoice over every
field. Three variable spaces each pay their distance from zero and receive
credit for their three pairwise distances. The exact linear optimum in
ambient dimension m is `-floor(3m/2)`. Every minimizer is classified.

At two copies the normalized power-tariff optimum is
`min(-1, 3/2^t - 3)`, for `0<t<=1`; the one-copy optimum is `-1`.
Coupling therefore helps exactly when `2^t > 3/2`. At the linear tariff,
the normalized optimum drops from `-1` to `-3/2`.

This is an exact gap in an abstract signed graph, with finite corroboration.
It supplies neither a physical scalar word nor a new kappa. In particular,
the three graph credits are not claimed to be independently delivered
recursive targets on arbitrary dirty inputs.

## Proof and context

[PROOF.md](PROOF.md) gives the dimension bound, attainment, all equality
cases and the exhaustive two-dimensional affine table. This extends the
variable-boundary question left open by Ali Romman's
[PR6171](https://github.com/CrocSwap/integer-mult-bounds/pull/6171), at
`343232cdf5273d1f77569de390f0977b46916644`. That result fixes every productive
boundary to a repeated space. This package makes those boundaries variable
and proves an exact optimum, beyond its arithmetic warning about negative
credits. It does not audit or contradict the fixed-boundary theorem.

Base main is `3f0152a32eeebac0df11946dbd50cabe5a7f7839`, priority revision 8.
The selected `0.003125804` frontier is unchanged. The card's first selected
source-binding control passed; no predecessor scientific replay was run.
The source PR is cited as conceptual context. No pending executable or Git
object is needed for the proof or replay.

## Reproduce

From the repository root, with CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -I -B research/signed-triangle-tensor-gap/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -I -O -B research/signed-triangle-tensor-gap/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/signed-triangle-tensor-gap
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/signed-triangle-tensor-gap --check-source-history
```

A clean `python3.12` executable can replace the local interpreter path.
The direct marker is `PASS_SIGNED_TRIANGLE_TENSOR_GAP`.
[RESULT.json](RESULT.json) records every finite domain, minimizer count and
ordered trace digest, and binds all six source files by SHA256. Replays are
read-only. To regenerate a receipt, supply `--output /absolute/scratch/result.json`
with a new output filename, then compare it with the committed receipt.

The verifier enumerates all ordered triples over F2 in dimensions 0 through
4 and over F3 and F5 in dimension 2. A separate closure inventory checks the
binary RREF enumeration. It checks the attaining construction at widths
1 through 64 and the nine affine costs at all three relevant envelope
endpoints. Missing/spurious table rows, intersecting-plane equality and the
strict threshold have explicit controls. The written proof supplies the
unbounded all-field claim; the finite checks do not replace it.

## Limitations

The domain consists of canonical subspace charts. General Lagrangian charts,
a prescribed scalar contact graph and actual native phases are outside it.
A legal dirty-input circuit, independence of physical targets, restoration,
owned storage, movement, adapters, precision, compiler closure, BIT and outer
admission remain open and unpriced. No selected cold replay, Lean or Docker
run is needed for this scoped theorem. Independent human and formal
proof-kernel review are unclaimed.

## Open next questions

- Can a legal arbitrary-dirty-input scalar circuit realize this signed graph,
  or is there a contact/path invariant that excludes it? First assign the
  three productive pairs to distinct logical lifetimes and account for every
  paid transition. Independent target delivery and restoration are blockers.
- What is the all-width optimum for `0<t<1`? Start with the signed distance
  objective itself, allowing unequal dimensions and nonzero intersections.
  The linear dimension bound and the two-copy table do not settle that domain.
  Such a relaxation result would still need a complete physical invoice.

## Credit

This contribution was produced by Nick Petalas. Apache-2.0.
Ali Romman retains PR6171's graph model, normalization and fixed-boundary
reduction. Cinna Davis retains the projection inequality, icekylinx retains
the canonical subspace-frame construction, and the P104/native/helper/caller/
compiler contributors retain their predecessor credit. Standard dimension,
graph-subspace and affine-envelope facts are background. No predecessor
code is copied and no literature-priority claim is made.
