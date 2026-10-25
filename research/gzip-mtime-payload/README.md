# An mtime-one gzip container still carries the same payload

**Partial. No new exponent.**

The published container note requires a check to compare payloads, and it
records that `verify_balanced_split.py` asserts
`digest(word) == meta['gzip_sha256']`. On one fixed payload, level-9 gzip
with mtime 0 and mtime 1 differs in header bytes 4 through 7. The digest of
the mtime-zero container rejects the mtime-one container. Both decompress to
the payload, whose sha256 is

```text
0ca09c6bea5b4320135b555d02c56d208cbb2d0cd699708d1dc3c57a0a376b60
```

The payload digest accepts the alternate container. The compressed bytes are
an environment header, and the word is the decompressed payload.

## What was executed

The checker builds both containers from the fixed payload and applies the
two comparisons. It does not rebuild the shipped archive and it does not
edit the balanced-split verifier.

`scripts/research_baseline.py` needs
`research/community-frontier1094-audit/ASSEMBLY.json`, which this checkout
does not have. The orientation used here is the gzip-container convention.

## Scope and evidence

Original card: `portable-replay`, priority revision 6, refined to this header
mismatch. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the container note. No selected frontier
file changes.

## Reproduce

From the repository root, CPython 3.12:

```sh
python3.12 -B research/gzip-mtime-payload/verify.py
python3.12 -B research/gzip-mtime-payload/test_verify.py
python3.12 -B scripts/research_package.py --package research/gzip-mtime-payload
```

## Open next questions

This header mismatch is the reproduced failure. Rebuilding the shipped
archive would leave this fixture.

## Credit

The container convention is the gzip-container note, prepared with Anthropic
Claude. That note credits PR #214 for the first observation and the audit of
PR #212 for the second.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
