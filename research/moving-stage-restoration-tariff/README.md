# Sharp positive moving-stage restoration count

Scoped mathematical proof with exact finite corroboration. For the moving
Gaussian stages `E_s=P_(0,s) D_0`, including `E_0=D_0`, request Gaussian
parity on k nonanchor blocks and anchor parity b. If the entire block
permutation must restore inside the charged word, the exact minimum is

```text
L(k,b) = 2k + ((k+b) mod 2).
```

Unused spectator blocks cannot shorten it. In particular, requesting all
m blocks costs `2m-2+(m mod 2)` stages. The internally restored three-block
boundary needs five stages. This gives an explicit cost for one restoration
method; it does not establish an improved recursive invoice or kappa.

[PROOF.md](PROOF.md) gives the lower bound and an attaining word. Each
requested nonanchor stage is used twice. At most one anchor stage corrects
parity. The exact residual is an explicitly stated block-local monomial
`(D_0^2)^((k+delta-b)/2)`, with `delta=(k+b) mod 2`. That monomial remains
part of the output contract and is not a free cleanup operation.

## Relation to predecessors

Cinna Davis / 1337isnot1337's [PR #5113](https://github.com/CrocSwap/integer-mult-bounds/pull/5113)
supplies the common-code moving-coordinate interface and its native/caller
limitations. Chris R / Clear1nsight's [PR #5133](https://github.com/CrocSwap/integer-mult-bounds/pull/5133)
uses a terminal anchor stage and rejects a fixed optimistic three-stage
invoice. Its three-stage word accepts an external whole-block permutation.
This result imposes internal permutation restoration instead and proves
the exact count for every target support and every number of blocks.
It does not replay, audit or claim either predecessor's result.

Credit Dillon #4933, Dugongue #4929, Cao Yifan, Cayden Burkart, JoyboyBrian,
zxv, Jacob Alan Sussman and the retained native/compiler/precision lineage
through #5113. Elementary permutation and tensor-product identities are
standard. The new scoped tariff, proof and verifier are produced by Nick Petalas.
Independent human and formal proof-kernel review are unclaimed. Apache-2.0.

## Reproduce

From the repository root, use CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -I -B research/moving-stage-restoration-tariff/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -I -O -B research/moving-stage-restoration-tariff/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/moving-stage-restoration-tariff
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/moving-stage-restoration-tariff --check-source-history
```

Both direct modes print `PASS_MOVING_STAGE_RESTORATION_TARIFF` with
50,362 quotient states, 126 permutation-restored endpoints, 916 literal
operator columns and 12 controls. The independent BFS uses an output-frame
state rather than the constructor's input-frame exponent representation.
Every stage is allowed at every quotient state. Literal finite-field
operators check every basis column on the declared fixtures, including
two-axis blocks and the residual local monomial. No predecessor executable
is imported. These are checks of the new theorem, not source replays.

Default verification writes nothing and needs no Git or network. Optional
`--receipt NEW_PATH` creates a receipt bound to the six package file hashes
and refuses an occupied path. The registered commands time out at 120
seconds each. All controls remain active under optimized Python.

## Scope and limits

The theorem covers every positive block width and finite spectator count.
The executable constructor and quotient oracle are bounded to six blocks;
the literal operator fixtures use one-axis blocks through four blocks and
two-axis blocks through three blocks. Finite enumeration corroborates the
written proof and does not replace it.

Only positive stages of this stated alphabet are charged. The endpoint
permits explicit block-local monomials and requires internal restoration
of the permutation of whole blocks. A caller accepting an external
permutation has a different contract. Full local-monomial cleanup, physical
movement, owner independence, helper targets, native/caller/compiler and
precision costs remain unpriced. No selected cold replay, Lean proof,
complete supplier, new kappa or complete multiplication theorem is claimed.
The selected frontier is unchanged.

Base is canonical main `19fdb086ea96af9a9f87936a2b888e10af4ed810`, priority
revision 8. The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19226084)
and [TASK.json](TASK.json) state the changed boundary and overlap coverage.
[SOURCES.json](SOURCES.json) pins both predecessor texts and the historical
card/selected record. Live open PRs, recent account PRs, handoffs, main
README terms and merged searches were checked; unpublished work and notes
outside those searches are not excluded.

## Open next questions

- Price internal restoration against an external block permutation in one
  actual complete caller. Start with that caller's exact endpoints and
  paid/target inventories, including the residual local monomial. The
  physical permutation tariff and consumer are missing here.
- Determine the minimum under a stricter contract that eliminates every
  residual local monomial. Start with exponents modulo four and fix whether
  inverse stages are legal. That different alphabet/endpoint contract is
  not answered by the present parity theorem.

## Implementation bounds

All loops have finite bounds from the declared block domains. The BFS has
at most `6! * 2^6` states and six outgoing stages per state. Literal vectors
have at most 64 entries. No function recurses and every function fits within
60 lines. Explicit exceptions enforce contracts in both Python modes.
Python integers and collections allocate dynamically; this is a bounded
managed-runtime verifier, not a fixed-allocation physical implementation.
Warning-strict normal and optimized replay provide interpreter diagnostics.
