# Fixed P104 source restrictions fail two exact moment gates

**Scoped finite obstruction; no new kappa.** For the exact PR5827 word,
no simultaneous coordinate restriction of its main ports and productive
helpers passes either tested moment gate:

- `kappa = 0.003124767`, just above the source claim `0.00312476680`;
- `kappa = 0.003156014468`, exactly one percent above that source claim.

This statement permits every subset of 666 groups: 104 main-port pairs and
562 individual helpers, with at least one main port retained. It gives an
optimistic query discount whenever the complete original input support or
output support of that query is removed. The test debits all removed targets
and rebuilds the complete p16/a7 main contribution. It omits new ordinary,
route and precision costs in favor of the candidate.

The two certificates have 233 and 221 branch nodes. Their integer flow
allocations prove strict negative upper bounds without a solver at replay.
The primary checker recomputes all 3455 query supports with rational arithmetic
from the 25984-event word and checks its forward and transpose endpoints.
It also reconstructs the entire published paid and target invoice.

| Tested kappa | Priced leaves | Largest local upper bound |
|---|---:|---:|
| 0.003124767 | 116 | -2481461 / 10^12 |
| 0.003156014468 | 110 | -46854465615 / 10^12 |

The full caller margin is 18 times the local margin in this table.
These are bounds from the certificates, not exact maximizing values.
The original word passes its own lower gate as a positive control.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/p104-joint-restriction-gate
```

Expected: `PASS_P104_JOINT_RESTRICTION_GATE` in normal and optimized modes.
Only the Python standard library is required. The scientific replay reads
package files only. It needs no Git, network, flow solver or predecessor import.
[PROOF.md](PROOF.md) states the exact model, tariff and dual inequality.
[RESULT.json](RESULT.json) contains the complete expected receipt.

`discover.py` is optional. It needs PyMaxflow and NetworkX and writes a new
certificate. It is not a proof dependency. The checker only validates positive
integer allocations against source and group capacities and checks coverage
of both children at each branch. Seven semantic corruptions must fail at each
tested saving. Source bytes have independent SHA256 and Git-blob pins.

## Scope and attribution

Source: [PR5827](https://github.com/CrocSwap/integer-mult-bounds/pull/5827),
head `05cd36e5af06d7a3790e30ce3f449fa89b853768`.
Canonical main: `de5ec2e7a6074068452f45b1a191b5c72832df4a`, priority 8.
The selected `.00310045` record is unchanged.

This result closes a fixed-source restriction screen. It does not exclude
changed scalar words, native paths, arbitrary linear quotient inputs, new
helpers or a new caller. The two pointwise moment tests do not prove monotonicity
on an interval or a universal kappa ceiling. Individual zero/dead conditions
need not compose into a legal physical word; the model grants every such
discount at once, so its failure is a favorable necessary-condition test.
No new physical supplier, full native replay, uniform compiler, rounded
multiplier or proof-assistant acceptance is claimed. The five inherited
framework assumptions remain.

The earlier single-input tests in Discussion #5125 and forty-helper experiment
in Discussion #5645 are prior work. This package adds complete subset coverage
for the declared support model and exact prices. Its source includes Mason
Hale's PR5811 composition, Ali Romman's helper and accumulation work, Joel
Pulikkan's R22, Dugongue's composition proof, flyingviper and all retained
native/controller/compiler/BIT authors. The full PR5827 notice is preserved
in `inputs/PR5827-NOTICE`. New work: Ali Romman with substantial OpenAI Codex
assistance; no subagents. Apache-2.0. All new checks are author-side.

The later [PR5835 audit](https://github.com/CrocSwap/integer-mult-bounds/pull/5835)
by unpaidmoon corrects the order of two frame ranks in the source proof.
It leaves the paid multiset unchanged. This checker uses the actual word and
frame basis lengths. The vendored source proof is preserved without edits.

[Canonical coordination](https://github.com/CrocSwap/integer-mult-bounds/discussions/5600#discussioncomment-19209322)
records the scope and earlier local searches. Current open PRs and adjacent
live claims were checked. The complete cached Discussion index was searched. Sparse notes,
arbitrary diffs and unpublished work remain coverage limits. Hosted CI and
independent scientific acceptance are separate from local checks.

## Open next questions

- Can a changed query argument permit a paid saving that is absent from the
  original zero/dead supports? This changes the model. Check the live #5645
  historical-value claim before choosing a disjoint source and edit.
- Can an independent reviewer check the complete main-port debit and the flow
  coverage proof? Start with Sections 2 and 3 of PROOF.md and the solver-free
  replay. No physical native replay is needed to check the stated finite model.

The donor's requested large kappa improvement remains unmet. This negative
result is a research handoff, not completion of that goal.
