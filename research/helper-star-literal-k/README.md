# One restored helper edge misses the literal K mask

**Partial. No new exponent.**

The helper-star builder brackets its target writes by an edge and that edge
reversed:

```text
h0 ^= h1
y  ^= h0
h0 ^= h1
```

Both helpers finish on their starting columns. The checker's literal mask
records only sources named by target writes, so it names `h0`. The column
replay delivers `h0 XOR h1` to `y`. After the first gate, `h0` holds both
columns.

The same two direct writes without the edge, `y ^= h0` and `y ^= h1`, deliver
exactly the helpers they name.

The phase-B helper-star note already records false
`H2_D_frame0_targets_from_helpers` and `K_equals_D` beside the unchanged paid
profile `{1:1323, 2:1342, 3:79, 4:44, 5:102, 6:11, 7:19}`. The semantic D
contract uses this three-gate word as its boundary example. This package
checks the literal mask on that word. It does not replay the 661-column
circuit.

## What was executed

The checker replays the four registers as the owner checker does: register `r`
starts as column `e_r`, and each gate adds the XOR of its sources. It rebuilds
the literal mask by the checker's target-write rule.

## Scope and evidence

Original card: `bit-helper-contract`, priority revision 6, refined to this one
edge. [TASK.json](TASK.json) records the scope change. [RESULT.json](RESULT.json)
is the executed receipt and is not rewritten. [SOURCES.json](SOURCES.json) pins
the checker, the star builder and the two notes. No selected frontier file
changes.

Upstream checkpoint: `20ecf2891d80b5acf18d980b2164fb44ea7faa90`, priority
revision 6, checked 2026-10-18 05:00 UTC. Catalogue and selected record match
that commit. Handoff discussion #1166, through the PR3527 note at 2026-10-18
04:49 UTC, was released work. Draw seed `8dcfcac65abe8406658ec91a7fe397f4`,
track `bit-mechanisms`, first card `bit-helper-contract`.

## Reproduce

From the repository root, standard-library Python 3.12:

```sh
python3.12 -B research/helper-star-literal-k/verify.py
python3.12 -B research/helper-star-literal-k/test_verify.py
python3.12 -B scripts/research_package.py --package research/helper-star-literal-k
```

The replay finishes in under a second.

## Open next questions

The literal named-source implication fails on this one restored edge. The
semantic boundary contract is a different statement and is not reopened here.

## Credit

eumemic's owner checker states the literal K test. The helper-star builder
states the restored edge. Sagar Thakrar's phase-B note states the two false
flags and the paid profile. The semantic D contract states this three-gate
example.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
