# A hash-keyed stage list skips the coverage producer's parse

**Partial. No new exponent.**

`scripts/verify_replay_coverage.py` reads the coverage contract with

```text
tree = ast.parse(producer.read_bytes())
```

The producer is `research/complex-sw4-frame8/verify.py`. Its top-level `run`
calls name 22 stages, from `ancestral558-fresh` through
`independent-two-engine-outer47`.

Parsing that file on every read is the measured loop. Keeping the stage list
when the source hash matches makes one hundred reads more than twice as fast.
The cached list equals a fresh parse. Appending a comment changes the hash,
so the stale list is dropped and the producer is parsed again. The stage
check is the same list either way.

## What was executed

The checker times the two loops on this producer. It does not run
`verify_replay_coverage.py --frontier`.

`scripts/research_baseline.py` needs
`research/community-frontier1094-audit/ASSEMBLY.json`, which this checkout
does not have. The orientation used here is the coverage script's parse of
the pinned producer.

## Scope and evidence

Original card: `replay-runtime`, priority revision 6, refined to this parse.
[TASK.json](TASK.json) records the scope change. [RESULT.json](RESULT.json)
is the executed receipt and is not rewritten. [SOURCES.json](SOURCES.json)
pins the coverage script and the producer. No selected frontier file changes.

## Reproduce

From the repository root, CPython 3.12:

```sh
python3.12 -B research/replay-ast-cache/verify.py
python3.12 -B research/replay-ast-cache/test_verify.py
python3.12 -B scripts/research_package.py --package research/replay-ast-cache
```

## Open next questions

This producer parse is the measured stage. The frontier coverage command
would leave this timing.

## Credit

Lucas (@ljste), PR 838, is credited in the coverage script for the
ancestor-coverage audit. The producer file is the sw4 package that script
parses.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
