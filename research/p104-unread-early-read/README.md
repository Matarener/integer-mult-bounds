# Early source observation on the PR #5827 unread path

**Partial audit; no new kappa.** The selected frontier stays the conditional
result recorded at this base. This package does not admit PR #5827.

## Scope and evidence

Task card: `p104-side-correction`, scope **refined**. The live handoff on
[Discussion #1166](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166)
for [PR #5827](https://github.com/CrocSwap/integer-mult-bounds/pull/5827)
asks for an independent review of the early source observation, the direct
native phase and the full bill. This package settles the early observation
and the frame ranks it sits on. The native phase and the caller bill are
open.

On the pinned PR #5811 word, the seven events at index 13815 are the unique
copy of the published source block. The published replacement word differs
only there. Replaying frames up to that cut puts roles 695 and 733 in frame
3, role 709 in frame 597 and role 773 in frame 1031. Both schedules are
legal and realize

```text
a' = a + b + c,  b' = b + c,  c' = c,  d' = d + c
```

with the same exit frames. The first new event is `ADD 695 += 733` in frame
3, while role 733 still holds its interval-entry value. Omitting it drops
`b` from `a`. A coefficient 2 writes `2b`. Placing that event after the
other six is not a legal common-chart addition.

Frame bases at 3, 597 and 1031 have lengths 0, 1 and 5, and the spans are
strictly nested. The role-695 legs therefore have ranks 1 (frame 3 to 597)
and 4 (frame 597 to 1031). The replacement leg has rank 5. PR #5827's proof
states dimensions 0, 4 and 5 and assigns those two leg ranks in the opposite
order. The nesting claim is right. The MOVE multiset still changes by
`-H_1 - H_4 + H_5`, because the other two moves are common to both
schedules. For every real `t` in `(0, 1)`, `1^t + 4^t - 5^t > 0`. One extra
coefficient-+1 ADD costs 8 real scalar primitives under the retained local
rule. That is not a caller moment.

The argument, pins and controls are in [PROOF.md](PROOF.md). Source commits,
Git blobs and SHA256 pins for the catalogue and selected record are in
[SOURCES.json](SOURCES.json). The two word files are live inputs; their
gzip and canonical SHA256 pins are constants in `verify.py`, matched to
PR #5827 `WITNESS.json`.

## Reproduce

From the repository root, with Python 3.12:

```sh
python3 scripts/research_package.py --package research/p104-unread-early-read --check-only
python3.12 -B scripts/research_package.py --package research/p104-unread-early-read
```

Both registered modes print:

```text
PASS_P104_UNREAD_EARLY_READ
```

No network and no third-party package. The verifier walks the vendored
words directly. It does not import `research/p104-unread-path-resynthesis`.

## Open next questions

- Do the native phases of the actual rank-1 map (frame 3 to 597) and the
  actual rank-4 map (frame 597 to 1031) match the PR #5827 receipt? The
  published sentence points a reviewer at a rank-4 map from frame 3 to
  frame 597, which is not this transport. First lower those two frame
  pairs. This package does not vendor the Clifford code.
- Does the complete caller bill still lie in
  `(0.00312476681507, 0.00312476681508)`? The corrected labels do not
  change the paid multiset, so the number can survive, but it was not
  recomputed. The five framework assumptions remain, and this audit is
  not a reason to move the selected frontier.

## Credit

The words, the seven-event plan and the conditional-kappa claim belong to
Mason Hale's PR #5811 and Ali Romman's PR #5827, with the retained
native, helper, controller, compiler and analytic predecessors named there.
The independent frame walk, the rank correction and this verifier are new.
Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
