# Conditional kappa 0.00310184 by composing a relay, cascade and helper splits

This package combines the compensated public relay in
[PR #5605](https://github.com/CrocSwap/integer-mult-bounds/pull/5605), the full
commuting-contact cascade in
[PR #5565](https://github.com/CrocSwap/integer-mult-bounds/pull/5565), and 13 of
the 15 independent helper splits in
[PR #5599](https://github.com/CrocSwap/integer-mult-bounds/pull/5599).
The complete conditional endpoint is **kappa 0.00310184**, a gain of
**0.00000345** over the consumed PR5599 version's 0.00309839.
During verification, PR5599 advanced to **0.00310045** at
`09dd0965711ca7eeb169057a420abab1c9052137`, independently composing its splits
with PR5565. Our endpoint is **0.00000139 higher** than that newer claim.
Our immutable inputs and historical comparison receipt retain the consumed
versions explicitly; no source head is silently replaced. The selected
frontier is unchanged.

The exact raw crossing lies in **(0.00310184254783, 0.00310184254784)**;
the claim is tested at 0.0031018405. The full bill contains **66,690 paid
calls** and **13,048 independent productive targets**, with rank surplus 760.
The local word has **748 arbitrary public inputs, 540 helpers, eight owned
lifetimes, owned peak one and 25,502 events**, below the retained 26,000 bound.
All extra independent inputs and ordinary basis operations are charged.

Read [PROOF.md](PROOF.md), [construct.py](construct.py), the exact
[SPLITS.json](SPLITS.json), [RESULT.json](RESULT.json), and [source pins](SOURCES.json).

## Why the composition is not just adding headline gains

The cascade removes the intermediate line visits needed by original split
numbers 12 and 15. They are omitted, including their target credits. The
other 13 retain their exact rational witness vectors; only their event cuts
move. At every new cut, the verifier recomputes the complete prefix functional
and suffix direction on the evolving word. It then replays every independent
input and output before proceeding to the next split.

Relative to PR5599, the local paid change is
`-9H1-H2-2H3-2H4+4H5+H6`, and the target change is
`-2H1-H4+H5-2H8+2H9`. Both enter the full invoice 18 times.
The root crossing and compiler reserve are recomputed from that actual bill.
No universal optimality or concave-order improvement for every possible
tariff is claimed. Other combinations were used during discovery; the
submitted claim concerns this explicit word only.

## Reproduce

Python 3.12 and its standard library suffice:

```sh
python3.12 -B scripts/research_package.py --package research/p104-relay-split-composition
```

Both registered modes must print `PASS_P104_RELAY_SPLIT_COMPOSITION_KAPPA_00310184`;
the launcher must print `PASS_REGISTERED_RESEARCH_PACKAGE`.

The verifier authenticates immutable sources and every payload in the unchanged
33-file PR5545 closure; independently merges the two retained predecessor
generators' disjoint source edits; checks all 13 rational split witnesses and
every intermediate arbitrary-input endpoint; regenerates the entire saved word;
checks the dense transpose and every signed native map; replays the complete
physical caller; and checks two exact interval engines, charged tail completion,
compiler conditions and all 58 outer predicates. Five controls reject a false
split prefix, missing initial/final basis changes, unearned targets and unpaid
transport. Compressed outputs are compared by complete decompressed payload.

The retained PR5599 pricing code changes only five declarations: the claimed
and tested endpoints, comparison endpoint, complete target/call counts, reported
decimal and predecessor key. [LITERAL-CHANGES.diff](LITERAL-CHANGES.diff) records
them. In particular, its completion decay 39/40 and compiler logarithm power
1024 are preserved; the older power 1000 is not reused.

## Limits and ceiling

The five framework assumptions remain: native all-column implementation,
owned erasure, uniform compiler closure, precision and fixed-tape costs, and
analytic recovery. The source helper-endpoint contract remains inherited.
Neither a complete rounded multiplier nor the enormous uniform word is
materialized. Exact finite replay is not proof-kernel verification or selected
frontier admission.

The signed moment for this fixed invoice is strictly decreasing on [0,0.0034].
Its raw funding ceiling is the crossing above, leaving between 2.54783e-9 and
2.54784e-9 above the claimed endpoint. This is not a ceiling for other words,
helper bases, inventories or compiler choices.

## Sources, scope and credit

Canonical main base: `5e0052ca0aa3036a3afa8b0438927377c8d97d53`, priority revision 7.
The assigned scalar-to-moment task is refined to a fully charged composition
of changed public dependencies, contacts and independent target splits.

Pinned sources are Ali Romman's PR5580 at
`6efa248cf456d6101d757e9d09ba29711d18a13a` and PR5599 at
`0644592d421b375c221045954fdf13932575ffa8`; Pierre-Loic Doulcet (@hexapode)'s
PR5565 at `9af814164b9dfc21f19ec737959d67cb71488c95`; and flyingviper's PR5605 at
`4a57d245ac3918ccc9947a867ece24573605e243`. Retained source files are unchanged.
Source retention commits make their bytes reachable without unmerged-object
caches. Exact source paths, Git blobs and SHA256 values are in SOURCES.json.

Further credit follows those sources: Joel Pulikkan/GamingPuzzled for the
helper-706 and successor handoffs; DreamingOfClouds for free endpoints and
event-level tools; thu-nmrc for coupled contacts; Ali Romman for the complete
caller and source closure; Gareth Davidson, David Arias and Cinna Davis for
P104 word, coalescing and private reuse; Cinna Davis for the controller;
Jacob Alan Sussman for productive recursion; zxv and Cao Yifan for interval,
compiler and native machinery; and all retained geometry, BIT and analytic
notices. The elementary basis identity is credited, not claimed as new.

New composition and verification prepared for flyingviper with substantial
OpenAI Codex assistance and independent agents. Separate agents derived the
composition, audited its algebraic hazards and reviewed the source/price checks.
No independent human review is claimed. Apache-2.0.

## Open next questions

Can a different legal cut recover productive credit after the cascade removes
the old line contacts? Begin with exact prefix/suffix subspaces at a changed
common chart, not a root search. A new split must introduce an independent input,
retain a valid endpoint and fund its added completion/ordinary costs.

Can another dirty relay alter the remaining owned consumers? First establish
the live-input endpoint identity, then an invertible correction and charged
cleanup. The simple free zero-frame correction lemma for the original 735-input
word must not be assumed for newly split successors that start at positive
frames. See structured questions in [TASK.json](TASK.json).
