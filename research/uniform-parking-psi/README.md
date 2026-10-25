# The bit-motif parking node has Psi above one at one half

**Partial. No new exponent.**

The fixed-tape schedule in the power-width interchange parks the inactive
role streams and makes one recursive call per unit of edge rank. For the bit
motif those calls have width `e/m`, so every child width in the normalized
list is 1. The modulus is `m = 1000000`. The role count is
`177176569091445000000`. The child count is the displayed rank sum
`177176569088785861287000000`.

At `tau = 1/2`,

```text
Psi = 22587334999661/22587335000
```

which is greater than 1. The node does not meet the strict transfer
hypothesis at this exponent. No network is replayed.

## What was executed

The checker reads the batched Psi definition, the swap parking paragraph,
and the motif parameters. It rebuilds the rank deficit from `N` and
`L_b/N = 100/539`, checks that deficit against the displayed ratio
`339/22587335000000`, and evaluates Psi for `s_b` width-1 children.

## Scope and evidence

Original card: `uniform-transfer-audit`, priority revision 6, refined to
this parking node. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the batched note, the swap section, and
the motif section. No selected frontier file changes.

Upstream checkpoint: `6f100d4bb5083f8c35d96fd95a539811c62f245c`, priority
revision 6, checked 2026-10-18 04:46 UTC. Canonical main and the fork main
were at that commit.

## Reproduce

From the repository root, standard-library Python 3.12:

```sh
python3.12 -B research/uniform-parking-psi/verify.py
python3.12 -B research/uniform-parking-psi/test_verify.py
python3.12 -B scripts/research_package.py --package research/uniform-parking-psi
```

The replay finishes in under a second.

## Open next questions

The manuscript states its transfer exponent as `1-2^{-50}`, not `1/2`. The
next reading is whether this same child list has Psi below 1 at that
exponent.

## Credit

The batched note states Psi and the stack-top parking rule. The swap section
states the fixed-tape schedule and the `s` recursive calls of width `e/m`.
The motif section states `m`, the rank sum, and the deficit ratio.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
