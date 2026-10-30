# Share the physical ROM bank across CRT rows

A new explicit bank interface lets consecutive paid CRT row queries reuse the
same 52 physical ROM tapes. In the complete ten-row forward/reverse fixture,
retained owned work falls from the derived distinct-bank baseline of 24,314
cells to 8,894 cells, saving 15,420 finite-symbol tape cells. Source and protected
input backing are additional in both counts.

Claim type: a source-bound construction and scoped composition proof, with
finite executable evidence. This is a new reentry interface for the open shared
workspace question of Ali Romman's [PR #5625](https://github.com/CrocSwap/integer-mult-bounds/pull/5625).
Its source-update theorem and the numerical/ROM producer theorems are premises,
not audit targets. No new kappa or selected-assumption discharge is claimed.

The 52-role inventory, componentwise extent formulas and within-row reuse
argument are credited to commdata2338's
[PR #5519](https://github.com/CrocSwap/integer-mult-bounds/pull/5519), including
its retained-backing predecessors. The new step is executable reuse across
separately constructed row queries, with exclusive leases and full historical
blank tails at each reentry. Numerical entry workspaces and the three other
joined ports remain distinct and fully charged.

See [PROOF.md](PROOF.md), [shared.py](shared.py), [verify.py](verify.py) and the
generated, hash-bound [RESULT.json](RESULT.json). The verifier executes the
changed caller and uses the retained logical caller only as its endpoint oracle.
It does not run a predecessor scientific replay. An additional two-row control
uses a long target followed by a short target within each row. Every bank keeps
its preallocated extent, including blank tails. Five rejection controls cover
lease ownership, historical tails, extent changes and source drift.

From the worktree root, reproduce with:

```sh
~/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/crt-shared-row-banks
~/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/crt-shared-row-banks/verify.py
```

Both normal and optimized registered commands must print
`PASS_CRT_SHARED_ROW_BANKS`. Metadata, committed-byte checks and hosted CI are
separate from the mathematical premises. Python 3.12 and the standard library
suffice. No full selected replay, proof assistant or binary compiler is supplied.

## Open next questions

Can JoyboyBrian's [PR #5505](https://github.com/CrocSwap/integer-mult-bounds/pull/5505)
reusable 63-role numerical owner compose with this updated source and shared
ROM bank? That predecessor already constructs numerical-bank reuse across
changing precision, separately from physical ROM/level integration. Start by
binding its live-result lease and marker reinstatement to this query close.
The current construction keeps its numerical workspaces distinct and does not
claim this additional composition.

Can a single bank cross a changing-precision node boundary? Start with the
actual protected-word conversion and source lifecycle at one adjacent pair of
nodes. Monotone bank capacities alone do not establish those caller contracts.

How can the required clean reserve be acquired from arbitrary dirty backing?
Start with the source-owned erasure contract and charge the complete restoration
or allocation mechanism. This construction assumes supplied clean banks.

This contribution was produced by Nick Petalas. Credit Ali Romman for paid CRT
source updates and row reentry; commdata2338 for the exact shared ROM footprint;
JoyboyBrian for the joined query and numerical/ROM lifecycle; ToikY for the
retained arena and caller; Hiroki KUMAZAKI and Cinna Davis for the CRT contracts.
All retained source notices and predecessor credit remain unchanged. Apache-2.0.
