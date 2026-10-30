# Retained-value test for the small odd-E8 E caller

This archived investigation did not produce a supplier or a kappa increase.
It tests the four-input, four-axis fixture from THU New Media Research
Center's [PR #5464](https://github.com/CrocSwap/integer-mult-bounds/pull/5464).
The actual 1,404,928-port caller is outside this test.

The input is the unchanged
[N3 program](https://github.com/thu-nmrc/integer-mult-bounds/blob/56ba6d7d609124d71c067d6a380caed573963f8f/research/odd-e8-lowrank-e-native/N3-PROGRAM.json).
Its Git blob is `757fe38c7de18c137be95e0d8e4f7c53e0b5d443`.
Its SHA256 is
`00470b4fc8804e944e6a6117e70bedff651ae61eb7db46539f156f38f47940c9`.
Retain the source's Apache-2.0 license and attribution. The new local
scripts were prepared by Ali Romman with substantial OpenAI Codex assistance.

## Question and result

Can retained paid values complete the missing negative output bank?
The experiment retains all four original inputs and all fifteen paid
results. It allows arbitrary rational linear combinations of their
ordinary translations and axis permutations.

Use the exact group algebra of `(Z/4Z)^4 semidirect S4`. A group element
has the form `C^e P`, where each coordinate Gaussian has order four.
The ordinary subgroup is `(2Z/4Z)^4 semidirect S4`. Each stored row has
four independent original-input columns. Projection onto a translation
character gives a necessary span test. We check five fixed characters:
the first zero, one, two, three or four coordinate bits are set. Failure
at any one character suffices to reject membership in the full module.
We do not need to assert that these five tests cover every character.
No one-column numerical relation between Gaussian operators is used.

Exact rational elimination gives the same ranks in all five cases:

| Allowed values | Rank | Rank after adding both missing target orbits |
| --- | ---: | ---: |
| All retained inputs and paid returns | 456 | 504 |
| These values and every one-axis query on them | 1368 | 1416 |

Both already decoded positive targets belong to each retained span.
Neither negative target belongs to either span. The second test grants
all 76 source/coordinate query choices at once. It is more permissive
than selecting one or two such queries.

A separate modular screen at prime 65521 checks all 76 individual query
choices and all 2,850 distinct pairs. None gives the missing targets.
The exact rational span test is the stronger evidence for this alphabet.

The control sets the small fixture's spectral parameter to two. Then
`C=2P_minus` and `E=I`, and all four Gaussian targets are recovered.
The literal source blob is checked before this control. In the actual
large construction, the nonzero C modes do not fill the K-minus
eigenspace. The control therefore does not give a large-caller repair.

## Reproduce

Run from this directory with Python 3.12 or later:

```sh
python3 -B history_module.py --exact
python3 -O -B history_module.py --exact
python3 -B paid_return_screen.py
python3 -B verify_control.py
```

The first two commands write `history_module_exact.json`. The third writes
`paid_return_screen.json`. The control checks `control-lambda2.json` without
changing it. Normal and optimized exact runs have the same scientific
fields; elapsed time can differ.

## Limits and next decision

This is an exact result in the stated finite group algebra for the small
published fixture. It is not a general physical lower bound, an audit of
the complete source package, or a proof about all native query alphabets.
It does not exclude nonlinear use of history, changed native words,
other paid services, or a different caller. A full tensor-width separation
proof was not added. The selected supplier, compiler and outer admission
were not rerun.

Stop this fixed-fixture, one-layer, coordinate-query search. A further
construction must change that premise and state its complete cost. The
current selected kappa remains `0.003027288235`. This local test alone does not justify a new supplier claim. The present
handoff preserves its source and limits.
