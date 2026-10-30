# The complex motif ratio lies below the manuscript power

**Partial. No new exponent.**

The complex motif displays

```text
s_c = 1873807244636671267308000000
```

and the deficit formula `2N - 2 L_c`, with `L_c/N = 101/539`. Rebuilding that
deficit gives

```text
eta = 73/19906842167500,
```

which matches the displayed ratio, and `s_c/W_c = m(1-eta)` with
`m = 1000000`.

`2^{50} eta` exceeds six times the ninth harmonic number. That harmonic
number exceeds `ln(10)`, so it exceeds `ln(m)`. The same integral comparison
used for the bit motif therefore gives

```text
s_c/W_c < m^{1-2^{-50}}.
```

For a list of `s_c` width-1 children, Psi at this exponent is that ratio
divided by the power, so Psi is below 1. The motif text counts `s_c`
translation factors and states this comparison directly. No network is
replayed.

## What was executed

The checker reads the displayed rank sum, rebuilds `2(N-L_c)`, matches the
deficit ratio, and compares `2^{50} eta` with the harmonic bound. A one-unit
deficit fails that comparison.

## Scope and evidence

Original card: `uniform-transfer-audit`, priority revision 6, refined to the
complex ratio. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the motif section and the batched Psi
definition. No selected frontier file changes.

Upstream checkpoint: `20ecf2891d80b5acf18d980b2164fb44ea7faa90`, priority
revision 6, checked 2026-10-18 04:53 UTC. The new main commit is a queue
close. The catalogue, selected record, family status, and these sources have
the same blobs as the previous checkpoint. Fork main was still
`6f100d4bb5083f8c35d96fd95a539811c62f245c` at the check.

## Reproduce

From the repository root, standard-library Python 3.12:

```sh
python3.12 -B research/uniform-complex-exponent/verify.py
python3.12 -B research/uniform-complex-exponent/test_verify.py
python3.12 -B scripts/research_package.py --package research/uniform-complex-exponent
```

The replay finishes in under a second.

## Open next questions

Both displayed motif ratios clear the same logarithm bound at exponent
`1-2^{-50}`. Repeating the exponent sketch would not add a new comparison.

## Credit

The motif section states `s_c`, the deficit `2N-2L_c`, the ratio, and the
exponent. The batched note states Psi.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
