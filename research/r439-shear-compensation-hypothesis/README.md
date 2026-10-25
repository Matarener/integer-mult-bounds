# Compensated restored shears keep the R439 helper footprint

**Partial certificate. No new kappa.** Selected κ stays
0.001672660197076918. This does not adopt a weakened `K_equals_D` contract
and does not change a paid profile.

## Question

The K-defect tally on the three retained helper-star words shows that the
helper mask `E` actually written by `D`, starting from identity columns,
equals the forward footprint `K` left by `(A, scatter, B)`. A three-gate
restored edge `h0 ^= h1`, `y ^= h0`, `h0 ^= h1` restores its helpers and
still has `E` different from the column it names. The released question is
which extra hypothesis the three words satisfy and that edge violates, tested
on one other pinned helper-mixing word. The hypothesis is not allowed to be
only "this `D` was built to match `K`".

Card `bit-helper-contract`, scope refined to that hypothesis.

## Hypothesis

Let the parent word be `research/r439-target-compensation/candidate.json.gz`.
Its `D` is three blocks: 306 target-to-target gates, 111 helper reads (one
per target), and 306 target-to-target gates. Neither transport block writes
a helper, and neither reads anything but targets.

A **compensated restored shear** of that parent is a word whose `D` is

```text
S + P + M + Q + reverse(S)
```

where `P` and `Q` are the parent's transport blocks, `S` is a list of gates
`h_a ^= h_b`, and `M` is the parent's middle support after the updates
`columns[b] ^= columns[a]` in that edge order. Bit `i` of `columns[j]` means
target `i` names helper `j`.

The three tally words and the pinned degree-1 pair control
`research/r439-bsection-stars-seed01/pair_control.json.gz` all have this
shape. Their edge counts are 221, 221, 236 and 188. The synthetic edge is
the shear `h0 ^= h1` with a middle that still names only `h0`.

## One-edge identity

Suppose each helper `j` currently holds a value `V_j` in an abelian 2-group,
and target `i` is about to receive the sum of `V_j` over `j` in its support
`S_i`. After the gate `h_a ^= h_b`, the new value of `h_a` is `V_a + V_b` and
`h_b` is unchanged. Replace the support by toggling membership of `b` on
exactly the targets that already name `a`.

- If target `i` does not name `a`, its support and its sum are unchanged.
- If it names `a` and already names `b`, the new sum replaces `V_a + V_b`
  by `V_a + V_b` from the dirty `h_a` alone. The named `b` is dropped.
- If it names `a` and does not name `b`, the new sum is
  `(V_a + V_b) + V_b = V_a`. The extra `V_b` is cancelled by naming `b`.

So one compensated edge preserves every target sum. The leading transport
block only mixes targets, and targets start with no helper columns, so it
does not change the helper footprint. The trailing block is the same map for
the parent and the sheared word, so the final executed mask `E` is the
parent's `E`. Reversing `S` restores every helper because `P`, `M` and `Q`
do not write helpers and each shear is an involution.

The parent's own execution has `E = K`. A descendant with the same forward
helper footprint therefore also has `E = K`. The star word keeps `A`,
`scatter` and `B` byte for byte. The composition, the later candidate and
the pair control change `B` and `C`; their forward helper masks were checked
equal to the parent's, not deduced from the text of those edits.

The identity does not use the gain order or the degree bound of the star
search. The verifier also runs five compensated edges that are not in those
searches, and the same five edges without the support update. Compensation
keeps `E`. Dropping it changes `E`.

## What was checked

| object | edges | shape | `E = K =` parent `K` |
|---|---:|---|---|
| parent target-compensation | 0 | bare bracket | yes |
| helper-stars-seed19 candidate | 221 | compensated | yes |
| bsection composition | 221 | compensated | yes |
| bsection candidate | 236 | compensated | yes |
| bsection pair control | 188 | compensated | yes |
| five-edge probe, support updated | 5 | compensated | `E` unchanged |
| same probe, support not updated | 5 | not the hypothesis | `E` changes |
| synthetic `h0 ^= h1` then read `h0` | 1 | not the hypothesis | delivers `h0+h1`, not `h0` |

The pair control is the other pinned helper-mixing word. It is not one of
the three tally words. It satisfies the hypothesis, so the agreement is the
shear identity rather than a property of those three greedy outputs alone.

## What is not established

`E = K` is not claimed for an arbitrary restored helper program. The
synthetic edge is the counterexample to that reading. Changed `B` and `C`
sections are checked only for the three words that carry them. The 612
target-to-target reads inside `D` remain an open H2 read-kind clause. No
supplier, native schedule, all-size transfer, or selected-frontier change is
claimed.

## Reproduce

From the repository root, CPython 3.12:

```sh
python3 -B research/r439-shear-compensation-hypothesis/verify.py
python3 -I -O -Werror -B research/r439-shear-compensation-hypothesis/verify.py
python3 scripts/research_package.py --package research/r439-shear-compensation-hypothesis
```

Expected first line:

```text
PASS_R439_SHEAR_COMPENSATION words=4 edges=221/221/236/188 parent_E_equals_K=1 descendants_E_equals_K=4 shape=4 one_edge_steps=871 compensated_probe=1 uncompensated_probe=1 synthetic_rejects=1 no_new_kappa
```

The verifier exits nonzero if a pin drifts, a descendant is not the
compensated shape, `E` or `K` moves, the one-edge identity fails, the
compensated probe moves `E`, or the uncompensated probe or synthetic edge
fails to separate. Runtime is a few seconds.

## Open next questions

1. Does every later phase-B rewrite with this same `D` bracket preserve `K`,
   or only the three checked variants? The shear lemma fixes `E`. Those
   variants were executed; their `B` and `C` edits were not identified.
   First step: compare one other pinned B-section word's forward helper mask
   with the parent. Blocked by the absence of a structural account of those
   edits.
2. Which H2 clause still fails once `E` is read as delivered columns? The
   read-kind clause on the 612 target-to-target gates is the obvious
   candidate and is not settled here. First step: name the first failing
   read of `H2_D_frame0_targets_from_helpers` on the star word. Blocked
   because this package does not rerun that checker and does not propose a
   replacement predicate.

## Credit

The parent bracket is the target-compensation word. The shear assembly and
the star and pair-control words are the helper-star builder (PR #967) and
the phase-B package `research/r439-bsection-stars-seed01`. PR #3533 isolates
one restored helper edge whose literal mask misses the delivered column.
PR #4092 (Nick Petalas) counts the defect by sector. The tally that left
this question open is PR #4115.

Prepared by unpaidmoon with substantial AI assistance (Cursor Grok).
Apache-2.0. Predecessor packages keep their own notices.
