# The #1042 status link opens the live selected record

**Partial. No new exponent.**

The historical section "Historical status through #1042" prints

```text
0.001672188119205421
```

and links "Selected record" to `certificates/selected-result.json`. That file's
kappa is `836330098538459/500000000000000000`. The same href is the live
section's selected-record link.

The printed decimal equals the checkpoint

```text
certificates/checkpoints/frontier1042.json
```

whose kappa is `1672188119205421/1000000000000000000`. The live record names
that file as `previous_record`. The historical wording is left as printed.

## What was executed

The checker reads the status page, the live record and the checkpoint. It
does not rewrite the page.

## Scope and evidence

Original card: `scope-navigation`, priority revision 6, refined to this link.
[TASK.json](TASK.json) records the scope change. [RESULT.json](RESULT.json)
is the executed receipt and is not rewritten. [SOURCES.json](SOURCES.json)
pins the three files. No selected frontier file changes.

Upstream checkpoint: `20ecf2891d80b5acf18d980b2164fb44ea7faa90`, priority
revision 6, checked 2026-10-18 05:57 UTC. Catalogue and selected record match
that commit. Handoff discussion #1166, through the PR3560 note at 2026-10-18
05:54 UTC, was released work. Draw seed `1c96b80206e3f5d545684875a27e1d7c`,
track `consolidation`, first card `scope-navigation`.

## Reproduce

From the repository root, standard-library Python 3.12:

```sh
python3.12 -B research/historical-1042-link/verify.py
python3.12 -B research/historical-1042-link/test_verify.py
python3.12 -B scripts/research_package.py --package research/historical-1042-link
```

The check finishes in under a second.

## Open next questions

The #1042 section's Selected record link opens the live record. The printed
decimal is the frontier1042 checkpoint.

## Credit

The status page and both records are the repository's. The live kappa is
Rohan Arun's #1094 selection. The checkpoint kappa is the #1042 record named
by that selection's `previous_record` field.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
