# Conditional kappa 0.00308595 from three coupled P104 contacts

This construction raises complete conditional kappa from **0.00308520** in
[PR #5565](https://github.com/CrocSwap/integer-mult-bounds/pull/5565) to
**0.00308595**. The new raw crossing is in
**(0.00308595175070, 0.00308595175071)**. Its raw gain over the exact
PR5565 crossing is between **7.4119868e-7 and 7.4119870e-7**.
The selected record remains 0.003027288235.

The later [PR #5599](https://github.com/CrocSwap/integer-mult-bounds/pull/5599)
claims a larger endpoint from independent helper splits. This package is a
verified improvement to its pinned PR5565 source, not a claim to the largest
open bound. The combined word is untested; [HANDOFF.md](HANDOFF.md) gives
the concrete composition check.

Three ADD contacts use lower-dimensional charts. This lets helper 307
finish at rank four instead of rank five and removes one paid job per
local call. The complete caller has **66,708 paid jobs**, down from 66,726,
with the same 12,814 independent productive fields and rank-mass surplus
760. All scalar instructions, coefficients, scalar order, 208 main
endpoints and eight owned lifetimes stay fixed.

Read [the proof](PROOF.md), [the four declarations](CHANGES.json),
[the constructor](construct.py), [the complete receipt](RESULT.json),
[the source pins](SOURCES.json) and [the validation record](VALIDATION.md).
The local paid delta is `-2H2 + 2H3 - 2H4 + H5`, and the target delta is
`H4 - H5`. A majorization argument proves a strict signed-moment gain for
every `0 < kappa < 1`. The new chart is the three-dimensional intersection
of two source frames.

The construction uses the event-lattice search by @DreamingOfClouds in
[PR #5568](https://github.com/CrocSwap/integer-mult-bounds/pull/5568) on the
newer commuting cascade by Pierre-Loic Doulcet, @hexapode. It retains
both stages of that cascade. Only the positive four-node component of
the search output is retained; unrelated zero-gain edits are omitted.
[DISCOVERY.md](DISCOVERY.md) records the source method and attribution.

## Reproduction

Python 3.12 and the standard library suffice. No solver is needed to
construct or verify the submitted word. From the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/p104-coupled-frame-step
```

Both registered modes must print:

```text
PASS_P104_COUPLED_FRAME_KAPPA_00308595
```

The launcher must print `PASS_REGISTERED_RESEARCH_PACKAGE`. The two modes
check the input pins and complete 33-file source capsule, exact word
reconstruction, all original-input endpoints, dense transpose columns,
every signed native map, the physical caller, two rational moment engines,
the compiler and all 58 outer predicates. They compare the full receipt
and reject the declared negative controls.

The PR5545 executable capsule remains unchanged. Its archive, inventory
and all payload hashes are checked before import. The word and price
inputs are byte-pinned to PR5565. The price diff changes only the claim,
predecessor comparison and exact paid-count declarations. All mathematical
tests remain. See [LITERAL-CHANGES.diff](LITERAL-CHANGES.diff).

## Limits and ceiling

The five inherited assumptions remain: native all-column implementation,
owned erasure, uniform compiler closure, precision and fixed-tape costs,
and analytic recovery. The helper-endpoint contract retains its source
review status. Helper 307's changed native target is explicit and fully
priced; no input is initialized to zero or discarded.

The fixed invoice has a strictly decreasing signed moment on `[0,0.0034]`.
Its raw crossing is its funding ceiling on that retained BIT band. The
claim is tested at 0.0030859505 and has raw headroom between 1.75070e-9
and 1.75071e-9. No optimum over other words or contracts is claimed.
The uniform word and complete rounded multiplier are not materialized.
Author-side replay is not independent scientific review or proof-kernel
acceptance. Hosted CI status is separate.

The p19 proposals have larger numerical headlines. In particular,
[PR #5440](https://github.com/CrocSwap/integer-mult-bounds/pull/5440) retains
an unresolved chain-to-native compiler and physical attachment. This
package improves the complete P104 paid-caller line. It does not exceed
that extra-premise numerical proposal.

## Coordination and credit

Base: canonical main `5e0052ca0aa3036a3afa8b0438927377c8d97d53`, priority
revision 7. [Discussion #5575](https://github.com/CrocSwap/integer-mult-bounds/discussions/5575)
is the canonical claim. [TASK.json](TASK.json) records the scope and overlap
coverage. The scope preserves PR5565's scalar order and changes only frames.

- Pierre-Loic Doulcet, @hexapode, supplied the consumed two-stage cascade in
  [PR #5565](https://github.com/CrocSwap/integer-mult-bounds/pull/5565).
- @DreamingOfClouds supplied the event-lattice search in
  [PR #5568](https://github.com/CrocSwap/integer-mult-bounds/pull/5568) and
  the free-endpoint word in
  [PR #5561](https://github.com/CrocSwap/integer-mult-bounds/pull/5561).
- Ali Romman supplied the complete contact certificate in
  [PR #5580](https://github.com/CrocSwap/integer-mult-bounds/pull/5580),
  the caller in [PR #5544](https://github.com/CrocSwap/integer-mult-bounds/pull/5544)
  and the source closure in
  [PR #5545](https://github.com/CrocSwap/integer-mult-bounds/pull/5545).
- Joel Pulikkan, @GamingPuzzled, supplied the priced helper-706 handoff in
  [PR #5569](https://github.com/CrocSwap/integer-mult-bounds/pull/5569).
- @thu-nmrc supplied the earlier coupled contacts in
  [PR #5551](https://github.com/CrocSwap/integer-mult-bounds/pull/5551).
- The retained notices credit Gareth Davidson, David Arias and Cinna Davis
  for the source word, coalescing and private reuse; Cinna Davis for the
  Laurent controller; Jacob Alan Sussman for productive recursion; and zxv
  and Cao Yifan for interval, compiler and native work. The official source
  closure retains the earlier geometry, BIT, precision and analytic notices.

The fixed-word obstruction in
[PR #5579](https://github.com/CrocSwap/integer-mult-bounds/pull/5579) helped
close an earlier search direction. The fixed-contact floor in
[PR #5590](https://github.com/CrocSwap/integer-mult-bounds/pull/5590) is
related work; this construction changes contacts outside its fixed class.
Neither result is counted as a contribution or dependency of this package.

New construction, proof and verification by Ali Romman with substantial
OpenAI Codex assistance. Apache-2.0. The same assistant did this work and
its checks; no independent reviewer or subagent was used. The source
toolkit credits DreamingOfClouds with Claude Opus 5.5 assistance.

## Open next questions

Independently review the frame intersection, helper 307 and the complete
invoice, then replay the registered checks. A further kappa step must
change a paid itinerary or target contract. Another root digit does not
improve this fixed invoice. No general obstruction follows from the
unsuccessful local screens that preceded this construction. Structured
questions are in [TASK.json](TASK.json).
