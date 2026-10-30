# A plane-port repair delivers two coordinates, and charge 224 does not save

**Partial. No new exponent.**

The inherited geometry puts the final Y endpoint at `C_all C_q^{-1}`. A
source that began at `C_q` therefore exchanges as `C_all C_q^{-2}`, which
equals `C_all X_q`. The literal factor `X_q` removes that extra factor.
The paid advances do not include the port direction `q`. That is the single
unpaid coordinate. The repair still advances it, so the delivered endpoint
is `C_all`.

Replace the line by the plane `E = {q, r}`. The same square `C_E^2` is the
repair, and both plane coordinates are unpaid. On a state of three
coordinates, with the spectator starting at exponent 2, the line repair and
the plane repair both finish at `C_all` on the data coordinates and leave
the spectator at exponent 2. Dropping the plane repair misses `C_all`.

The ideal unpaid=2 screen, with the selected local word and centre charge
64, has ceiling 6377984109/1000000000000. Its ratio to the selected ceiling
rounds to the published 3.77. The naive plane-port charge is 224 rank-2
queries, local profile `{7: 224, 2: 112}`. Its deficit is `-224/9`, and
`ceiling.ceiling` rejects a positive saving.

## What was executed

The checker multiplies the coordinate exponents and calls `ceiling.ceiling`
on the ideal and naive profiles. It does not replay the frontier certificate.

## Scope and evidence

Original card: `coverage-law-change`, priority revision 6, refined to this
endpoint. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the ceiling, the geometry note and the
plane-port budget note. No selected frontier file changes.

Upstream checkpoint: `20ecf2891d80b5acf18d980b2164fb44ea7faa90`, priority
revision 6, checked 2026-10-18 05:36 UTC. Catalogue and selected record match
that commit. Handoff discussion #1166, through the PR3551 note at 2026-10-18
05:34 UTC, was released work. Draw seed `5b21e54f2184a7574e607206a582d4dd`,
track `recursive-interfaces`, third card `coverage-law-change`.

## Reproduce

From the repository root, standard-library Python 3.12:

```sh
python3.12 -B research/plane-port-endpoint/verify.py
python3.12 -B research/plane-port-endpoint/test_verify.py
python3.12 -B scripts/research_package.py --package research/plane-port-endpoint
```

The ceiling screen takes a few seconds.

## Open next questions

The naive charge 224 has no positive saving. A cheaper plane-port decoder
would be another round, and this screen does not start one.

## Credit

The line-port endpoint identity is in the inherited complex geometry note.
The plane-port charge of 224 is the naive realization recorded by the
plane-port budget note, from ctoth's contract. The packing ceiling is
Douglas Colkitt's, with Claude (Anthropic).

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
