# Neutral fixed-frame displacement-two retiming on staged544

This package closes the specific neutral fixed-frame first-move gap identified
by PR3957. It tests both immutable PR3734 providers: an existing ADD crosses
exactly two scalar neighbours while keeping its frame and zero paid delta,
then any existing ADD may move anywhere in its legal scalar corridor with any
common binary frame. All entrances, native maps/cuts, exits and other frames
stay fixed. Every covered combined raw moment is non-improving for all real `0<a<1`.
Per provider, 8,034 legal first records expose 9,109,630 block-ADD prices and
4,616,377 outside-ADD interior-cut prices: 13,726,007 per provider and
27,452,014 total. All 19 signed histogram types have exact certificates.
The detailed counts are in `CENSUS.json`; the complete local obligation ledger
is `LEDGER.json`.

The new proof reduces the second move to every ADD in the reordered
three-instruction block plus both newly exposed interior insertion cuts for
outside ADDs. Other second prices map to the regenerated pinned single-move
certificate. This is a scoped finite obstruction; it does not classify all
circuit rewrites or admit a supplier or new kappa. Oriented first records and
reduced cut/dimension prices are not counts of distinct whole circuits.

Read `PROOF.md` for the two-interior-cut argument, including SCALE crossings,
fixed checks and all possible second-frame orientations. `RESULT-base.json`
and `RESULT-extra.json` bind the deterministic state streams, exact aggregate
histograms, dirty-block checks and whole-word sample receipts. Regeneration
recomputes every first and second reduced case. No sampled census or shared
provider shortcut is used.

## Reproduce

Python 3.12+, standard library only, from any working directory:

```sh
python3 -B research/staged544-neutral-fixed-d2/verify.py --provider base
python3 -B research/staged544-neutral-fixed-d2/verify.py --provider extra
python3 -B research/staged544-neutral-fixed-d2/check_controls.py
python3 -O -B research/staged544-neutral-fixed-d2/check_controls.py
python3 -B scripts/research_package.py --package research/staged544-neutral-fixed-d2
```

Ordinary commands are read-only. `verify.py --provider base --emit /external/path.json`
explicitly writes a regenerated receipt outside the package; writes inside the
package are rejected. The registered hook repeats both complete providers and
assertion-disabled independent controls. `VALIDATION.json` records actual commands,
runtimes, failures and publication/history-check boundaries.

The primary search uses exact local reindexing of traces and frame geometry.
Controls compare it with fresh full reconstruction across every available
phase, direction and three-instruction operation pattern, and independently
enumerate every first admission/rejection by direct monotone event itineraries.
Both interior cuts are compared with unoptimized reach and frame pricing. A
production mutation omitting the second interior cut must alter the census.
An early native-barrier overcount discovered by these controls was corrected;
preliminary interrupted attempts are not presented as passing evidence.

All first edits receive exact rational arbitrary-dirty three-instruction matrix
checks. Complete 723-input free-operator replays cover both baselines and explicit
first/final word samples, both orientations, reverse pullback and cleanup. These
sampled whole-word checks are distinct from the universal local-composition
proof. No human review or formal-kernel acceptance is claimed.

## Sources and credit

Canonical base: `20ecf2891d80b5acf18d980b2164fb44ea7faa90`, priority revision 6.
Scientific input: dataisfire/PR3734
`fa041037a3374eaa08feeca0b26a5d6893194147`. All immutable local snapshots have
byte count, SHA256 and Git-blob bindings in `SOURCES.json`.

Credit PR3886's single-move theorem and implementation; PR3941's adjacent
middle-cut reduction and exact dirty block method; PR3942's exact interval-price
implementation; and PR3957's explicit gap, verification scaffolding and cost
ledger. Retain Jeremy Kothe/PR2957's already-known positive fixture and the
PR2979 staged-entry lineage, Dugongue/PR3863's proposed paid exchange target,
Sagar Thakrar's auditor, roger-sato's semantic adapter and Arham Tahir's
frame-contract attribution. These interpreters are credited reuse, not new
independent semantic engines. New three-instruction reduction, census and
adversarial controls by Chris R / Clear1nsight with substantial OpenAI Codex
assistance. Apache-2.0 and retained source notices apply.

## Cost and acceptance boundary

The local bill records every recursive rank count, rank mass, helper width,
borrowed dirty buffer, scalar/native instruction count, entrance/exit hash and
finite coefficient-height bound. Unknown fresh native Gaussian/Clifford phase,
physical hosting and owner chronology, uniform precision/stock/tape, all-size
compiler, outer/supplier, analytic and BIT obligations remain unknown rather
than zero. The frozen inherited outer profile is authenticated but is not newly
reconstructed or admitted here.

## Open next questions

- A simultaneous two-frame rewrite with no legal sequential intermediate can
  evade this scope. Begin with one exact before/after word and arbitrary-dirty
  restoration contract, then its complete paid/native/physical bill.
- Changed terminal/native contracts in concurrent proposals need source-bound
  consumer and complete-cost audits. This fixed-boundary result cannot reject
  them. Audit one concrete claimed reduction before optimizing another group.
- Farther first displacements remain outside this package. No further radius
  census is automatically proposed: require a separate expansion decision and
  a clear decision that the result can change.
