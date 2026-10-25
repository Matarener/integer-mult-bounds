# Price of one K/adjoint round trip

**Partial ledger. No new κ.** Selected conditional κ stays
`0.001672660197076918`.

## Scope and evidence

Original card: `independent-moment`, scope **changed**. The card asks for an
independent check of one changed supplier claim and its physical ledger. The
session handoff is the unpaid physical boundary in discussion #1166 comment
19036235, left by PR #4002. The catalogue method used is that card's frame
reconstruction: one coordinated substitution and its single-change control.

The pinned boundary is the new-version witness warp on register `333`, index
`4`, together with the adjoint descriptor that swaps its entrance and
terminal. Both use

```text
G = (1, 2, 8, 32, 44, 128, 59, 66, 489).
```

`K_{G^{-1}} K_G = Z_{256}` and `J_{G^{-1}} J_G = J_I`. The single-change
control deletes only `Z_{256}`. The binary product stays the identity, and
256 of 512 states change sign. [PROOF.md](PROOF.md) records the tags
`t_G = 144` and `t_{G^{-1}} = 68`.

The published `linear_Z4` on the sign-+1 gate is not the mask `144`. Helper,
routing and tape charges are absent from the descriptor and stay unknown.
The exact sign adds no denominator. A favorable complete bill is not
established. No native expansion and no κ change.

`RECIPES.json` is the byte-identical `source/RECIPES.json` from PR #4002 at
`d593941ea0a4926021cba9d01fe60500579e464f`, SHA256
`64b85f6aef485026eebaec7acddb41999f57e074b0dfde8077b6543700cd684b`. That
commit is not required as a Git object in this clone. The checker rejects any
other bytes. It does not import PR #4002's verifier.

## Reproduce

From the repository root, CPython 3.12:

```sh
python3.12 -B scripts/research_package.py --package research/k-adjoint-boundary-price
```

Direct check:

```sh
python3.12 -B research/k-adjoint-boundary-price/verify.py
```

Expected marker: `PASS_K_ADJOINT_BOUNDARY_PRICE` with
`central_child=Z_256`, `states_wrong_under_J=256`,
`favorable_complete_bill=false`, and `new_kappa=false`.

## Open next questions

1. Can `Z_{256}` be absorbed by an adjacent paid gate on register `333`?
   First step: name the predecessor and successor of index `4` in the
   PR #3945 schedule and multiply those three operators. Blocked here
   because this descriptor has no neighboring gates.
2. What helper, routing and tape tariff does this warp pay in the emitter?
   First step: read the owner row for register `333` in the PR #3945
   native inventory. Blocked because those fields are not in `RECIPES.json`.

## Credit

Chris R / Clear1nsight, PR #3987, for the canonical lift and the inverse
witness. ToikY, PR #4002, for the explicit tag formula, the frozen four-map
inventory, and the open pricing question. Dugongue, PR #3945 / #3929, and the
native lineage named in that package, for the recipe convention. The tag
arithmetic on this one pair was recomputed here and does not import that
checker.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
No independent human or formal-kernel review is claimed.
