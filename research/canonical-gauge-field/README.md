# The canonical word payload omits the gauge annihilator

**Partial. No new exponent.**

The paired-cube producer stores each selected gauge's annihilator in
`_gauge_ann`, then writes the gzipped word from the keys that do not start
with `_`. Its regeneration check decompresses that container and compares the
bytes.

Two words with the same public gauges and annihilators `[3]` and `[4]`
therefore decompress to the same payload. Their container hashes still change
when the gzip modification time changes, and a change to the public gauge
dimension reaches the payload. The annihilator is the omitted proof field.

The export path reads `_gauge_ann` while the word is still in memory. This
check does not rerun that export and does not rebuild the p = 12 word.

## What was executed

The checker applies the producer's public-key filter and the same
`gzip.compress(..., mtime=...)` container used for the timestamp control. It
does not import the producer.

## Scope and evidence

Original card: `portable-replay`, priority revision 6, refined to this one
omitted field. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the producer and the gzip-container note.
No selected frontier file changes. Immutable source hashes stay in the pin.

Upstream checkpoint: `20ecf2891d80b5acf18d980b2164fb44ea7faa90`, priority
revision 6, checked 2026-10-18 05:18 UTC. Catalogue and selected record match
that commit. Handoff discussion #1166, through the PR3542 note at 2026-10-18
05:14 UTC, was released work. Draw seed `a5f2e8440fbfa35d468f338e46b20574`,
track `verifier-engineering`, first card `portable-replay`.

## Reproduce

From the repository root, standard-library Python 3.12:

```sh
python3.12 -B research/canonical-gauge-field/verify.py
python3.12 -B research/canonical-gauge-field/test_verify.py
python3.12 -B scripts/research_package.py --package research/canonical-gauge-field
```

The replay finishes in under a second.

## Open next questions

The word payload omits `_gauge_ann`. Putting that list back into the
canonical word would be a producer edit, which this audit does not make.

## Credit

The paired-cube producer states the private annihilator and the payload
comparison. The gzip-container note states that a payload comparison is the
canonical check.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
