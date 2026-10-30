# Fixed rank-one channels cannot cheaply repair the retained modes

This source-bound necessary-quotient result restricts the rank-one-only part of
[Ali Romman's PR5745](https://github.com/CrocSwap/integer-mult-bounds/pull/5745)
open question about nine or more jointly noisy channels. It builds on
[flyingviper's PR5720](https://github.com/CrocSwap/integer-mult-bounds/pull/5720).
No new multiplication bound or physical construction is claimed.

## Contract

Keep the frozen F9-SOURCE-DAG-ALL8 backward word and omit its unimplemented
physical_add tail. Each channel carries a fixed scalar combination of the eight
original captured modes, prepared in one fixed rank-one chart. It may scatter
at any number of chronological contacts in that chart. Arbitrarily many
channels and joint cancellation of their nuisance outputs are allowed. Each
channel must pay its preparation; gathering, storage and ordinary scatter costs
are optimistically ignored. Ground-helper cleanup is granted. Y must return
correctly through the stated controls: extra delivery to its final charts is
not granted for free.

Changing the native word, recomputing a payload from changed live data,
inter-chart transport or reframing, and extra paid cleanup are outside this
contract. Native address operators use the retained common-fixed-vector
specialization. A negative necessary test is not a general feedback theorem.

## Certificate and proof

The retained endpoint is X-CY, Y, H, with C=I-R^T R/4. For every control form
Z=deltaX+C deltaY. If all Y outputs are restored, the desired X correction must
be supplied by Z. This allows cancellations between different channels rather
than requiring each channel to be clean independently.

The exact census covers every response-changing interval in each actual
rank-one chart. For each chart, retain the union of possible nonzero Z output
coordinates. Assign nonnegative weights to required output coordinates such
that every chart's union has total weight at most one. Any successful set of
charts must cover every required coordinate, so its size is at least the total
weight. This argument permits arbitrary rational coefficients and cancellation;
it is not a bounded coefficient search.

The retained certificate establishes a weight of 50 for mode5. For the full
eight-mode correction, all 112 X rows are required. The only chart reaching
multiple Z coordinates reaches twelve; give those coordinates weight 1/12 and
the other hundred weight one. Every chart has load at most one, giving a bound
of 101 distinct fixed rank-one charts and hence at least 101 channels.
For the recursive power tariff H_r=r^q H_1, 0<q<=1, the removed allowance
8H_8 is at most 64H_1. Thus this rank-one-only family cannot repay the removed
centers. This does not decide mixed-rank or changed-feedback constructions.

`rank1-controller.json` retains the exact chart supports, weights, source pins,
coverage counts and rejection controls. `rank1_controller.py` regenerates them
with rational arithmetic. [Y-CLEANUP.md](Y-CLEANUP.md) explains why treating
final Y cleanup as a free ground-frame ADD is invalid: its affected fields
finish in 56 distinct rank-eight charts. The rational 1/13 correction also
needs an actual arithmetic/precision contract.

## Reproduce

Python 3.12 standard library only, from the repository root:

```sh
python3 -B scripts/research_package.py --package research/active-rank1-controller
python3 -B scripts/check_research_commit.py --package research/active-rank1-controller --check-source-history
```

The registered normal and optimized commands authenticate the unchanged source
archive, read two data members into a temporary directory, and compare complete
semantic receipts. No archived Python code is imported. Direct exported replay
uses `python3 -B research/active-rank1-controller/verify.py`; inputs remain
read-only and no Git or network access is needed.

## Open next questions

See TASK.json for concrete first steps: test a mixed-rank noisy-channel family,
or change one source dependency/address map and charge its complete restoration.
The higher-rank and general feedback questions in PR5745 remain open.

## Provenance and credit

Prepared on canonical main de5ec2e7a6074068452f45b1a191b5c72832df4a, priority
revision 8. SOURCE pins preserve the current task card and the two predecessor
proofs. The selected frontier is unchanged. Ali Romman's PR5745 provides the
canonical channel contract, clean-channel tariff and at-most-eight noisy-channel
argument; this package adds a resource bound for arbitrarily many rank-one-only
channels. The frozen source retains Cao Yifan, Cinna Davis, Dugongue and the
native/mode/controller authors and notices.

Prepared for flyingviper with substantial OpenAI Codex assistance and separate
agent checks. This is not independent human peer review or formal verification
of the multiplication theorem. New work is Apache-2.0.
