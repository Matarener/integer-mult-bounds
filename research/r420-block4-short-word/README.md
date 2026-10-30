# R420 block 4 in 29 XOR additions

This finite construction is produced by Nick Petalas. It realizes the fixed
12-wire binary map of Cinna Davis's [PR #1383](https://github.com/CrocSwap/integer-mult-bounds/pull/1383)
in **29 XOR additions**, with no workspace and an explicit output assignment.
The [51-gate construction in PR #1363](https://github.com/CrocSwap/integer-mult-bounds/pull/1363)
is the cited predecessor, so the new local word saves 22 additions.
No predecessor count or program is independently audited here.

Claim type: finite exact circuit certificate, with a written extension to
arbitrary binary vector payloads. This is a local construction, without an
optimality claim, a complete R420 replacement, or a new kappa.

## Exact endpoint

Let the twelve arbitrary input values be x0 through x11, in physical order

```text
(23,110,102,28,46,38,87,92,55,60,78,70).
```

The target is frame 546, phase-B block 4 of the historical R420 word. Its
specification is taken from PR1383's pinned `CERTIFICATE.json`, specifically
`source_target_rows` and `object.input_wires`. A row integer m denotes the
linear form sum_j bit_j(m) x_j over F2. The ordered target rows are

```text
(4092,4085,3951,3967,511,1535,2559,3326,3743,3855,4080,4059).
```

For each pair (d,s) below, perform r[d] ^= r[s]. Start with r[j]=x_j.

```text
(5,6)  (7,8)  (1,3)  (1,2)  (6,2)  (3,0)  (1,9)
(2,0)  (0,8)  (9,5)  (9,10) (7,4)  (0,10) (6,8)
(0,11) (9,11) (9,7)  (8,1)  (8,9)  (1,0)  (0,8)
(7,1)  (6,7)  (2,9)  (3,2)  (5,1)  (11,0) (10,0)
(4,5)
```

Read logical output i from r[p_i], where

```text
p = (3,2,5,4,0,10,11,8,7,1,9,6).
physical output wires = (28,102,38,46,23,78,70,55,92,110,60,87).
```

The output assignment is part of the endpoint contract. It is not an
implemented physical routing operation or a claim that routing is free.
There are exactly twelve registers throughout, all initially arbitrary.
To invert the endpoint, load y_i on wire p_i and run the 29 gates backward.

## Construction and proof

The first bidirectional greedy trajectory, with tie seed zero, reduces the
target matrix M to a permutation P. A row step left-multiplies by an
involutory elementary matrix. A column step right-multiplies by one. Thus
L M R = P and M = L^-1 P R^-1. Move P to the endpoint assignment. Execute
the column-derived input gates, followed by the reversed row gates conjugated
by P. `construct()` implements exactly this conversion and recovers the
literal word and assignment above. It has a 150-move bound. No second
trajectory was searched after this first strict improvement.

A separate packed-row replay begins with the twelve unit rows, applies the
29 listed gates, and reads them in order p. It gives exactly the twelve target
rows displayed above. This proves the binary matrix identity. The independent
list-valued Boolean interpreter then checks all 4,096 inputs and all 4,096
inverse reconstructions. For payloads in any F2-vector space, apply the same
matrix identity coordinate by coordinate. This extension uses linearity and
holds at every payload width. It does not assert the same identity for real
or integer addition.

The new scope changes `centre-path-sharing` to PR1383's explicit historical
shortening handoff. The current selected-baseline command passed its source
binding and metadata checks before the experiment. It was not a scientific
supplier replay. The historical local map does not establish a current
persistent-centre contract or a complete signed-moment gain.

## Reproduce

From the repository root, using CPython 3.12 and the standard library:

```sh
~/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/r420-block4-short-word/verify.py
~/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -O -B research/r420-block4-short-word/verify.py
~/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/r420-block4-short-word
~/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/r420-block4-short-word --check-source-history
```

Both direct modes print

```text
PASS_R420_BLOCK4_SHORT_WORD
gates=29 cited_predecessor=51 local_saving=22 inputs=4096 inverses=4096 workspace=0
deletions_rejected=29 directions_rejected=29 endpoint_controls=2 malformed_rejected=11
```

The final line gives a SHA256 digest of the full target, input wires, word and
output assignment. Every single gate deletion and every single gate direction
reversal fails the endpoint. Two more controls reject omission of the output
assignment and a changed target. Eleven malformed program/specification cases
are rejected. Explicit exceptions preserve all checks under optimized Python.
The direct verifier reads no external files and writes nothing. `SOURCES.json`
pins the predecessor specification and explanations as Git provenance, not
as executable dependencies. No predecessor verifier is imported or replayed.

All functions are under sixty lines. Loops have fixed bounds: 4,096 inputs,
29 gate mutations per kind, eleven malformed cases, and at most 150 reduction
moves, each considering 264 row/column moves. Python's managed allocation is
a deviation from fixed preallocation: the reduction retains at most 150
12-entry states and 264 candidate triples, while Boolean inputs are streamed
one at a time. Every matrix entry is a twelve-bit integer. Warning-strict
normal and optimized runs check the real endpoint and rejection paths.

## Limits

This word uses the binary map and explicit logical output assignment of the
source handoff. It does not preserve the predecessor's positive integer lift,
local norm envelope, downstream route assignment or full cleanup word. Those
properties are not implied by binary equality. No full-word scalar saving,
unchanged paid profile, hosted precision, native implementation, caller bill,
supplier admission, selected-frontier update or complete multiplication
theorem is claimed. There was no exact-depth exclusion, so 29 is an upper
bound and optimality remains open. Independent human and formal proof-kernel
review are unclaimed. No selected cold replay, Lean or Docker was run.

## Open next questions

1. Can one complete historical R420 caller use this exact output assignment
   while rebuilding downstream routing and literal reverse cleanup? Start
   with this one block and charge the complete changed word, its positive
   norm envelope and payload cap. None of those source-bound obligations is
   supplied here; the 22-addition local saving cannot be doubled automatically.
2. Can a short invariant prove a lower bound approaching 29 for this exact
   binary target with arbitrary output assignment and no workspace? Start
   with a declared elementary-gate model and an independently checkable
   bound. The present successful trajectory supplies no optimality evidence.

These questions are unreserved. The structured scope and blockers are in
`TASK.json`. Stop here at the first smaller finite word.

## Credit

The new word, reduction and checker were produced by Nick Petalas. Apache-2.0.
Cinna Davis / 1337isnot1337 supplies the exact target, input order and explicit
open question in PR1383, and the 51-gate predecessor with its separate
whole-word route in PR1363. Credit eumemic for the retained PR543 R420 source,
and the PR370/493 construction and checker lineage cited by those packages.
Ali Romman's PR688 supplied predecessor whole-word replay structure, which
is not used here. Elementary row/column XOR reduction and bidirectional linear
circuit synthesis are classical methods; no general algorithm novelty is
claimed. Frozen predecessor files and their credit are unchanged.
