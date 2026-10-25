# The bit-motif list has Psi below one at the manuscript exponent

**Partial. No new exponent.**

At `tau = 1/2` the bit-motif parking node has Psi greater than 1. At the
manuscript exponent `tau = 1-2^{-50}` the same width-1 list satisfies
`Psi(tau) < 1`.

The child count is the displayed rank sum `s_b`, each child has width `e/m`,
and `s_b/W_b = m(1-eta)` with

```text
eta = 339/22587335000000,    m = 1000000.
```

`Psi(tau) < 1` is the inequality `s_b/W_b < m^tau`. Let `u` be the deficit
divided by `s_b`. Then `ln(1+u) > u/(1+u) = eta`, because
`1/(1+t)` is larger than `1/(1+u)` on `[0,u)`. Also

```text
ln(10) = integral_0^9 dt/(1+t) < sum_{k=1}^{9} 1/k,
```

since on each interval `[k-1,k]` the integrand is strictly below `1/k`. Thus
`ln(m) = 6 ln(10)` is strictly below six times that harmonic sum. The checker
shows that `2^{50} eta` is larger still. Therefore

```text
(1+u)^{2^{50}} > m,
```

which rearranges to `m(1-eta) < m^{1-2^{-50}}`. No network is replayed.

## What was executed

The checker rebuilds the deficit from `N` and `L_b/N = 100/539`, matches it
to the displayed ratio, and compares `2^{50} eta` with six times the ninth
harmonic number. A one-unit deficit fails that comparison.

## Scope and evidence

Original card: `uniform-transfer-audit`, priority revision 6, refined to this
exponent comparison. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the motif section, the swap section, and
the batched Psi definition. No selected frontier file changes.

Upstream checkpoint: `714606601d4aae7fbe8cf0c9727b59ba754bc02e`, priority
revision 6, checked 2026-10-18 04:49 UTC. The new main commit records intake
and attribution only. The catalogue, selected record, family status, and these
three sources have the same blobs as `6f100d4b`. Fork main was still
`6f100d4bb5083f8c35d96fd95a539811c62f245c` at the check.

## Reproduce

From the repository root, standard-library Python 3.12:

```sh
python3.12 -B research/uniform-exponent-bound/verify.py
python3.12 -B research/uniform-exponent-bound/test_verify.py
python3.12 -B scripts/research_package.py --package research/uniform-exponent-bound
```

The replay finishes in under a second.

## Open next questions

The complex motif states the same exponent for `s_c/W_c`, with deficit ratio
`73/19906842167500`. That comparison is not done here.

## Credit

The motif section states `m`, `s_b`, the deficit ratio, and the exponent.
The swap section states the `s` calls of width `e/m`. The batched note states
Psi.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
