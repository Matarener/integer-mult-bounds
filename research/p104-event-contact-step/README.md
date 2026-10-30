# Conditional kappa 0.00308189 from one P104 contact change

This construction increases complete conditional kappa from 0.00308181 in
[PR #5569](https://github.com/CrocSwap/integer-mult-bounds/pull/5569) to
**0.00308189**. The raw crossing increases by between 7.645343e-8 and
7.645345e-8. The selected record remains 0.003027288235.

One ADD contact moves from a three-dimensional chart to a four-dimensional
chart. Each of the 18 local calls replaces two rank-three paid jobs with
one rank-two and one rank-four job. Strict concavity proves a positive
signed-moment change for every 0 < kappa < 1. Every public endpoint,
productive target, scalar instruction and owned lifetime stays fixed.

Read [the proof](PROOF.md), [the four-site construction](construct.py),
[the complete receipt](RESULT.json), [the source pins](SOURCES.json) and
[the verification record](VALIDATION.md). The complete bill retains
66,852 paid jobs and 12,814 productive fields. The exact raw crossing is
in (0.00308189496866, 0.00308189496867). The claim is tested at
0.0030818905, below that crossing.

This is a small paid-profile step after the priced helper-706 handoff.
It composes with that handoff and retains the source's free helper endpoints.
It is not a new controller or a new selected frontier. No independent human
review or complete proof-kernel verification is claimed.

## Reproduction

Python 3.12 and the standard library suffice. No optimization solver is
needed to reconstruct or verify the published word.

```sh
python3.12 -B scripts/research_package.py --package research/p104-event-contact-step
```

Both registered modes must print:

```text
PASS_P104_EVENT_CONTACT_KAPPA_00308189
```

The launcher must print `PASS_REGISTERED_RESEARCH_PACKAGE`. It runs exact
source reconstruction, both arbitrary-input endpoints, dense transpose
columns, all signed native maps, the physical caller, two moment engines,
the compiler and all 58 outer predicates. It compares the complete result
with the committed receipt and runs the negative controls.

The PR5545 official source export is retained unchanged as an executable
dependency. The verifier checks its archive hash, inventory and 33 payload
files before import. It also checks the PR5569 word and price source against
their Git blob IDs and SHA256 values. These files are retained sources,
not new contributions. Compressed word regeneration is compared by its
complete decompressed payload.

The price implementation retains the source's mathematical tests. Its
[diff](LITERAL-CHANGES.diff) changes the claim/comparison declarations and
derives the actual local rank sum in the reported native growth bound.
The latter corrects the old literal 5,894 to 6,013; it is not the source of
the kappa gain.

## Limits and ceiling

The five framework assumptions remain: native all-column implementation,
owned erasure, uniform compiler closure, precision and fixed-tape costs,
and analytic recovery. Independent acceptance of the source helper-endpoint
contract also remains inherited. The new change preserves those endpoints.
The uniform word and complete rounded multiplier are not materialized.

On [0,0.0034], the fixed invoice has a strictly decreasing signed moment.
Its raw funding ceiling is the crossing interval above. The headroom above
the claimed endpoint is between 4.96866e-9 and 4.96867e-9. This is not a
ceiling for other words or suppliers.

The p19 proposals have larger numerical headlines. In particular,
[PR #5440](https://github.com/CrocSwap/integer-mult-bounds/pull/5440) records
an unresolved chain-to-native compiler and physical attachment. This package
improves the complete P104 paid-caller line; it does not claim to exceed that
proposal's extra-premise numerical model.

## Coordination and credit

Base: current canonical main `5e0052ca0aa3036a3afa8b0438927377c8d97d53`.
The [canonical claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/5574)
records the changed scope, initial overlap coverage and test.
[TASK.json](TASK.json) retains the revision-7 card. The released
[event-placement handoff](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19181969)
supplied the research lead. The event-level model in
[PR #5568](https://github.com/CrocSwap/integer-mult-bounds/pull/5568) by
@DreamingOfClouds informed discovery. The submitted edit was then isolated
by a direct single-contact scan and is reconstructed without that solver.

- Joel Pulikkan, @GamingPuzzled, supplied the exact PR5569 word and priced
  helper-706 handoff, building on his successor-handoff work in
  [PR #5472](https://github.com/CrocSwap/integer-mult-bounds/pull/5472).
- @DreamingOfClouds supplied the free-endpoint word in
  [PR #5561](https://github.com/CrocSwap/integer-mult-bounds/pull/5561)
  and the event-level toolkit and released handoff.
- @thu-nmrc supplied the coupled contacts in
  [PR #5551](https://github.com/CrocSwap/integer-mult-bounds/pull/5551).
- Ali Romman supplied the complete caller and source closure in
  [PR #5544](https://github.com/CrocSwap/integer-mult-bounds/pull/5544) and
  [PR #5545](https://github.com/CrocSwap/integer-mult-bounds/pull/5545).
- The retained source notices credit Gareth Davidson, David Arias and
  Cinna Davis for the P104 word, coalescing and private reuse; Cinna Davis
  for the controller; Jacob Alan Sussman for productive recursion; zxv and
  Cao Yifan for the interval, compiler and native framework. The official
  source closure preserves the earlier geometry, BIT and analytic notices.

New construction, proof and verification by Ali Romman with substantial
OpenAI Codex assistance. Apache-2.0. The search, proof and checks were
performed by the same assistant; they are not independent review.

## Open next questions

Independently review this contact and the inherited helper-endpoint contract,
then recompute the complete invoice from the word. A later construction
must change a paid itinerary or a target contract. Another root digit does
not change this invoice. No wider optimality or native-admission claim
follows from the bounded contact search. Structured questions are in
[TASK.json](TASK.json).
