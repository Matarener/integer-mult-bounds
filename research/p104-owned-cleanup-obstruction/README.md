# P104 owned-cleanup obstructions

**Scoped negative result; no new kappa, construction, productive credit or
selected-frontier change.** This proves seven fixed-boundary owned-block cost floors, a joint crossing-count
floor, and a public multi-partner obstruction for the exceptional eighth block.
The results exclude concrete ways to save transport cost on PR5569's frozen
word, not owned temporaries in general.

Submission refresh found concurrent [PR5579](https://github.com/CrocSwap/integer-mult-bounds/pull/5579),
which already publishes the same 5,252-case public-window obstruction. Our
independent reconstruction is retained as corroborating source validation, not
claimed as novel. The cost floors, joint cut and 29,688-case exceptional-block
test below are the additional results. [Discussion5575](https://github.com/CrocSwap/integer-mult-bounds/discussions/5575)
now investigates compensated source substitution; that changed-dependency
scope is distinct and remains open. [PR5580](https://github.com/CrocSwap/integer-mult-bounds/pull/5580)
reports a gain by changing another scalar contact. We do not claim our frozen
PR5569 checks automatically apply to that changed word.

## Results

| Question | Checked result | Essential restriction |
| --- | --- | --- |
| Independent check of PR5579: can omitted owned-holder states support one common-chart cleanup? | All **5,252 helper/boundary pairs**, representing **2,832 full-holder geometries** and **2,340 public geometries**, have a two-public-role obstruction. | Unchanged scalar contacts; the nominated helper and all its public input-symbol holders meet at one chart. |
| Can a different internal word improve an owned delivery star? | **Seven of eight blocks attain a proved raw paid-moment floor** for every `0<t<=1`. | Same local public map and frames; no outside side information, work across the boundary or new credits. |
| Can an unchanged producer simply be prepared earlier at a lower frame? | Each producer has rank-eight original entry support and an individual total-owned-cost floor **H7** at its final delivery line. | One unchanged demanded value/frame; these floors cannot be summed across values. |

Two further source-bound results:

- [Joint cut](PROOF-joint-cut.md): the eight required values have independent
  projections onto inputs outside the span of their delivery lines. At least
  **eight owned crossings** into that span are necessary, even with sharing
  and sequential observations. The source attains the count. This is **not**
  an 8H7 cost bound; crossing ranks may still change.
- [Exceptional block738](PROOF-738.md): retiming its five existing deliveries
  still requires levels `8->7->6->{3 or 4}->1`, with the same minimal route
  histogram. For **29,688 recipient/cut pairs**, no public linear combination
  can replace one nominated delivery at one common frame. The public rows
  form a basis, so the copied value has unique necessary support. This is not
  a limit on partner count or a coefficient-grid search.

Here `H_d(t)=d^t`, with `t=1-kappa`. Fewer ADDs alone do not improve the recursive
invoice. The tight star tariffs are `3H1+H7`, `3H1+H7`, `2H1+H7`, and four copies
of `5H1+H7`. Their combined `28H1+7H7` is a floor only for **separate** replacements
respecting all seven boundaries. Owned738's observed tariff is `5H1+H2+H3`;
the star theorem does not prove it optimal under arbitrary replacement.

The [window proof](PROOF-windows.md) excludes every binary contact subspace,
not just listed source frames. The [block proof](PROOF-blocks.md) allows arbitrary
rational internal words and private zero auxiliaries inside its fixed boundary.
The [loss-space proof](PROOF-loss-space.md) allows changed preparation and erased
fields, but accounts globally for their descents. This global accounting is why
the per-value floors are not additive.

## Source and independent checks

Source: [PR5569](https://github.com/CrocSwap/integer-mult-bounds/pull/5569),
head `af9f091ac6f30c6eaacb9c27777bfbe2d0e5ffdf`. The two unchanged compressed
inputs and credits are retained [here](inputs/README.md). [SOURCES.json](SOURCES.json)
pins use a retention commit in this PR's own history; a clean replay needs no
cached, unmerged predecessor objects. Base main was
`5e0052ca0aa3036a3afa8b0438927377c8d97d53`.

The new replay checks all **743 final scalar rows**, preserving all 735 arbitrary
public inputs and clearing eight owned fields. It checks common scalar charts,
transport nesting and lifetimes. Each block's actual prefix and public suffix
have full ranks `4,4,3,6,6,6,6,6`; an unobservable local-map change cannot evade
the fixed-boundary result. Omitting a delivery changes final public outputs.

An independent agent implemented the complete window census before reading the
candidate code, reproducing all three counts and public-only obstructions.
Other agents derived boundary and support checks, reviewed proofs and searched
primary literature. These are author checks, not independent human acceptance.

The original PR5569 full verifier was run unchanged before this analysis and
returned `PASS P104_PRICED_HANDOFF`, including native/transposed replay, physical
caller, both moment engines, 54 strict plus four functional outer checks and
root interval `(0.00308181851522, 0.00308181851523)`. This is conditional,
unselected **predecessor baseline evidence**, not a new result. The small
registered replay here does not repeat that complete native/funding suite.

## Reproduce

Python 3.12, standard library only. Direct scientific replay needs no solver,
network, shell tools or Git. From the repository root:

```sh
python3.12 -I -B research/p104-owned-cleanup-obstruction/verify.py
python3.12 -I -O -B research/p104-owned-cleanup-obstruction/verify.py
python3.12 -B scripts/research_package.py --package research/p104-owned-cleanup-obstruction
```

The verifier compares its fresh exact result with [RESULT.json](RESULT.json).
Normal runs do not write files. `--witnesses PATH` optionally exports all window
witnesses; `--write` explicitly authors a receipt. Known successful cleanup706/173
is a positive control. Semantic controls reject changed source bytes, invalid
witnesses, reversed transports, changed payloads, incorrect delivery signs/frames
and a zeroed producer. Widening a delivery frame correctly weakens the producer
floor. Scientific checks do not depend on Python assertions.

The registered runner also checks metadata and Git provenance and needs full
history. Exported source runs the direct verifier without Git. This publication
also checks committed bytes, source ancestry and a Git-free exported replay.

## Literature and interpretation

The [literature note](LITERATURE.md) separates useful linear-circuit ideas from
what is proved for this tariff. The two-sided boundary identity `S(R-T)P=0` and
full-rank implication `R=T` are elementary linear algebra, proved explicitly.
No paper is treated as evidence of a legal or cheaper P104 construction.

The result corroborates PR5579's common-chart obstruction and establishes
additional fixed-boundary optima and delivery obstructions. Further coefficient search in those domains cannot help;
the dependency or boundary model must change. The whole productive-helper
programme is not ruled out.

## Open next questions

- Can a changed public dependency or cleanup using several contact charts lower
  the complete paid-minus-productive profile? First specify one replacement map
  and its entry/exit frames, then derive its histogram.
- Can a joint construction share preparation across owned lifetimes? Identify
  a specific transport serving two demanded values and check its exact map;
  adding the individual H7 bounds is invalid. Include all restorations, helpers,
  ordinary passes and ownership obligations before claiming a gain.

See [TASK.json](TASK.json) for the task refinement, expansion gate and stop rule.

## Credit

Prepared for flyingviper with substantial OpenAI Codex assistance and independent
agents; Apache-2.0. Ali Romman independently published the overlapping
window obstruction in PR5579 before our submission. Retain Joel Pulikkan (GamingPuzzled)'s PR5569 mechanism and
open question; DreamingOfClouds's PR5561/5553 endpoints and word; thu-nmrc's PR5551
contacts; Ali Romman's PR5544/5545 verifier and caller; and the full predecessor
lineage in [inputs/README.md](inputs/README.md). No source construction is newly
attributed to this package. No proof-kernel acceptance is claimed.
