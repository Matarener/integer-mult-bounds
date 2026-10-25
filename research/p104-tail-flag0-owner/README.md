# The flag-0 source read has no owner

**Partial. No new exponent.**

Event 5759 adds `-1/2` times `X0` into `Y34`. The add has five fields and no
owner. The tail package states that it assigns no global owner or host for
that read.

## What was executed

The tail witness has three sections: `initial_frames`, `final_frames` and
`program`. Event 5759 is

```text
add Y34 X0 -1/2 [1, 2, 4, 8, 16, 32, 64, 128, 256]
```

The result's remaining obligation is to prove a globally legal owner/host
schedule for the appended source reads. Its scope says the construction does
not supply global chronological helper hosting. The task blocks on the
sentence "No global owner/host assignment for the current 104-by-104 source
reads has been established." The readme says the construction does not assign
global owners or hosts.

## Scope and evidence

Original card: `p104-side-correction`, priority revision 6, refined to this
owner question. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the tail word, its readme, its result and
its task. No selected frontier file changes. This reading does not build a
schedule.

## Reproduce

From the repository root, standard-library Python 3.12:

```sh
python3.12 -B research/p104-tail-flag0-owner/verify.py
python3.12 -B research/p104-tail-flag0-owner/test_verify.py
python3.12 -B scripts/research_package.py --package research/p104-tail-flag0-owner
```

The replay finishes in under a second.

## Open next questions

The tail word leaves the owner unbound. The next reading is whether a later
package assigns an owner to this same read of `X0`.

## Credit

Cinna Davis supplied the tail word and the statement that no global owner or
host is assigned.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
