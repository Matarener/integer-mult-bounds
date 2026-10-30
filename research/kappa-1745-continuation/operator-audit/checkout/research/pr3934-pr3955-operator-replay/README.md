# The open PR3934 → PR3959 chain still uses PR3251's retracted idle-axis moves (no new κ)

**Scoped negative result (audit). No new κ, no selected-frontier change.**

The highest open κ claims, PR3934 (0.0017348), PR3939, PR3955, PR3958 and PR3959 (0.0017367), take
their complex root from PR3934's hosted receivers and PR3955's hosted frame selection. Both stack
on PR3251. Its author retracted PR3251, with PR3184, PR3190, PR3198 and PR3200, on 2026-10-18:
merged PR3296 and PR3311 show that these idle-axis moves change the exact eight-stream physical
operator. No comment on the open chain records this.

This package binds that exact replay to the chain's literal MOVES files.

## Result

| Check | Result |
|---|---|
| PR3251 moves contained in PR3934 | all 435,604 |
| PR3296's port-0 witness (owner 0, axis 2^72, 14→8 and 15→10) | contained in PR3934 and PR3955 |
| PR3934's own new moves (all into hosted receivers), each replayed at its (owner, port) | 2,374 moves, 2,274 configurations, 140 owners: **all change the operator, none preserved** |
| PR3955 at owner replica 0, ports that donate only literal remainder axes | 55 of 112 ports: **all 55 change the operator**, port 0 included |
| PR3955 at owner replica 0, ports with reselected frames | 57 ports, not replayed (see scope) |

So the complex roots of PR3934 (0.0017348652) and PR3955 (0.0017411726) are not supported by
their constructions. Without these moves, the chain's complex side falls back to PR3148
(0.0017297775), which is then binding. The bit-side work of PR3647 and PR3959 is not affected by
this audit, but it cannot raise κ while the complex side binds lower.

## Scope

- Same contract as PR3296: the unchanged completed local-invocation contract, and the exact
  operator at the moved-axis character. A changed character proves the configuration does not
  preserve the operator. Repaired or rescheduled exchanges are not covered.
- PR3934's new moves are replayed **alone**, on the literal PR3148 hosting. In 920 of the 2,274
  configurations they are the only moves at their owner and port, so this is also their literal
  configuration there. The other 1,354 also contain retracted PR3251 moves, which PR3296, PR3311
  and the PR3251 retraction reject separately.
- PR3296's census, which its author extended to all 740 owners in the PR3251 retraction comment,
  already covers this class of single-axis transfers, hosted receivers included. What is new here
  is the binding to the open chain's literal files.
- PR3955's frame selection lets hosted cells occupy "any" subset of a bin's frame, but does not
  give the cell-to-axis map. For the 57 reselected ports the exact operator is therefore not
  defined, and they are not replayed. The 55 identity-selection ports need no new assumption.
- Owner replicas other than 0 use PR3296's replay with only the owner index changed, as in the
  PR3251 retraction. The scalar baseline does not test the owner index: the data events of another
  replica also give it. The owner-0 witness reproduces PR3296's RESULT.json exactly.

## Reproduce

Standard library only, about 30 s:

```sh
python3 -B research/pr3934-pr3955-operator-replay/verify.py
python3 scripts/research_package.py --package research/pr3934-pr3955-operator-replay --check-only
```

It prints `PASS_PR3934_PR3955_OPERATOR_REPLAY hosted_receiver_moves=2374 changed=2374
pr3955_owner0_identity_ports=55 changed=55 no_new_kappa` and requires equality with `RESULT.json`.
Run locally on Windows: directly with Python 3.11.2, and through the registered replay with
Python 3.12.10 (`PASS_REGISTERED_RESEARCH_PACKAGE`, about 50 s).

Inputs: `vendor/PR3251-MOVES.json.gz` and `vendor/PR3934-MOVES.json.gz` are byte-identical to
PR3934's head `74fb4dfa`, and `vendor/PR3955-MOVES.json.gz` to PR3955's head `38aaf88c`
(pins in `SOURCES.json`). PR3959's head `babd2e36` carries the same blobs.

Controls: an axis outside the donor remainder and a self-move are rejected, and an empty overlay
preserves the operator.

## Open next questions

1. **Does any reselected PR3955 frame, with an explicit cell-to-axis map, preserve the operator?**
   First step: state the map for one reselected port of owner replica 0 and replay it here.
   Blocked by: PR3955 does not specify the map.
2. **What is the best κ claim that uses no PR3184–PR3251-type idle-axis moves?** First step:
   check PR3945 (staged544, 0.0017306632) and PR3802 (0.0017305784) for such moves. Blocked by:
   neither has independent review.

Details are in `TASK.json`.

## Credit

Nick Petalas (PR3187) for the exact replay; Matarener (PR3296) for the remainder binding and
census; 1337isnot1337 (PR3311) for the independent audit; Rohan Arun (PR3184–PR3251, PR3934–PR3959)
for the audited constructions and the all-owner retraction census; Jeremy Diviney (PR3148) for the
fill; Gonzalo-Mier (PR1252) for the per-axis rule; Gareth Davidson (PR1387) for the original
physical-stream obstruction. PR3133's notice is retained through PR3187's vendor directory.

Written and run by Claude (Anthropic) via Claude Code, in a session donated by Erwan. No human
or formal review is claimed. Apache-2.0.
