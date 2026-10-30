# Dynamic helper captures on the final G20 BIT word

On the exact PR5708 G20 local word (conditional ordinary BIT saving
0.003507719059749), no owned-helper capture of the PR5586 **B1** kind pays
its target for one helper or for any pair of helpers, with an arbitrary
injected payload at every epoch. Every retained helper has exactly **one
live interval**, so the multi-epoch premise of B1 has no instance on this
word. A joint parity-token bound limits larger owned sets. The complete
search over sets of three or more helpers is left open below, with a
concrete encoding. No new kappa or supplier admission is claimed.

Claim type: finite exact census with a scoped linear-algebra argument.
Base: canonical main `19fdb086ea96af9a9f87936a2b888e10af4ed810`.

## Results at the B1 target C = 0.0037 (t = 1 - C)

| Check | Result |
|---|---|
| Needed over the PR5708 invoice | +40.952 signed moment, +2.2751 per local word (18 calls) |
| Debit of one owned full helper | 8^t = 7.9387 |
| Single helper, arbitrary injection, all epochs (415 helpers) | none pays; best 0 (helper 684, H4 for H4); max removed rank mass 7 |
| Live intervals per helper | exactly 1 for all 415 |
| Pairs whose joint ownership lengthens a dead interval | 5, all lose (exact best -1.968) |
| Pairs with a shared query, individual schedule | 6030: 5638 closed by the parity-class bound, 392 enumerated exactly; best -1.957 |
| Joint token bound, any owned set | removed t-mass at most 26/4 = 6.5 per owned helper, plus its free own query |
| Consequence | a set gains only through the 180 helpers with a free rank-2 own query (at most +0.556 each); reaching 0.0037 needs at least 5 of them, all compatible |

Positive control: on the PR5667 word (the source of Ali Romman's PR5671,
from Dugongue's PR5665 theorem) at C = 0.0035 the same single-helper census
finds exactly the nine selected late-binding helpers of PR5671
(223, 319, 331, 344, 371, 375, 484, 501, 551), each as a free own H1 plus one
removed H7. No other helper is positive there.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/g20-dynamic-capture-census
python3.12 -I -W error -B research/g20-dynamic-capture-census/verify.py
```

Python 3.12 and the standard library suffice; one run takes under a
minute. Expected final token: `PASS_G20_DYNAMIC_CAPTURE_CENSUS`. The
verifier authenticates the pinned inputs in SOURCES.json, checks the PR5708
local paid profile, recomputes every number above and compares RESULT.json
in full. `--write` regenerates RESULT.json. [PROOF.md](PROOF.md) gives the
model, the exactness argument and the precise scope.

## Scope

The word, its frames and its native contract are used as published. Captures
own retained helpers, drop writes into a helper while it is dead-forward,
and inject arbitrary payloads by ordinary same-frame scalar operations; the
scalar fees of those injections are not charged, which only helps a capture.
Paid frame conversions, added contacts, changed scalar order and changed
words are outside this census. Native/ROW, compiler, ordinary backend,
precision and tape premises of the source framework are unchanged and not
replayed. This is an author check, not independent acceptance.

## Open next questions

- **Complete joint search for three or more helpers.** Only sets built
  mostly from the 180 helpers with a free rank-2 own query can still gain,
  at most +0.556 per helper by the token bound. Encode candidate injections
  with their exact matrix-level kill conditions and solve the weighted
  maximum consistent subset (ILP or MaxSAT) with the moment gain as
  objective; check any witness with `capture.py`. Expected outcome is
  negative, but it is not proved here. Volunteers are welcome.
- **Changed words.** B1 needs helpers with several live intervals or larger
  shared queries. Run `capture.py` on any new G20 successor word: a second
  live interval or a positive single-helper bound is the signal.

TASK.json records both questions.

## Credit

Dugongue proposed B1 in PR5586 and the deferred-input theorem in PR5665.
Ali Romman supplied the nine-owned-relation method (PR5421), the static
entry-capture capacity bound whose token argument is adapted here (PR5604),
the PR5671 late-binding admission used as the control and the PR5679/PR5708
words. Credit ai-nanachi's PR5512 G20 source and all native, controller,
helper, ordinary and stock predecessors named in those packages. Nick
Petalas's PR5983 covers a different (split) mechanism on the same word.
Prepared for Matarener with substantial Anthropic Claude assistance
(Claude Code). Apache-2.0.
