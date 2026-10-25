# A local first move does not unlock a second ADD saving on staged544

This follows the neutral-first handoff from **CrocSwap PR3886** and fork PR9.
It proves a broader, but still precisely bounded, negative result on both exact
PR3734 staged544 providers. A first ADD may change its frame in place or cross
one adjacent scalar gate, with any legal first frame. A second ADD may then move
arbitrarily far within its allowed scalar corridor with any common frame.
Neither a neutral nor a locally losing first move enables a strictly better raw
rank moment for any real `0<a<1` in this class.

This is not an arbitrary two-ADD impossibility result. The first displacement
is limited to one neighbour, the intermediate word must be legal, and other
frames and all caller boundaries stay fixed. Longer first moves, simultaneous
changes requiring an illegal intermediate, warp crossings, and changed
interfaces remain open. No new circuit saving, supplier, or kappa is claimed.

## What was checked

For each provider the exact first-state census contains 4,709 distinct
fixed-frame adjacent swaps, 49 neutral and 616 losing adjacent changes with a
changed first frame, and 29 neutral and 353 losing stationary frame changes.
There are **5,756 nontrivial first-move records**. The identity first move is already
covered by the regenerated predecessor single-move census.

The new interaction and single-new-gap reductions avoid an unstructured square
of the old census. Fixed-frame swaps require 14,693 new-gap cut/dimension checks.
The 1,047 changed-frame first states require 11,903,025 interacting second
cut/dimension checks. The total is **11,917,718 reduced candidate prices per
provider**, yielding **49 signed histogram types**, all exactly certified as
non-improving. These are price cases, not a count of distinct complete circuits.
All actual first subspaces are enumerated; second dimensions suffice because
their price depends only on dimension. No other first states are silently
represented by one arbitrary frame orientation.

`PROOF.md` states the contract and proves the reductions. The compact
`RESULT-base.json` and `RESULT-extra.json` retain every resulting signed type,
multiplicity, capped sum, and sign prefix, together with source and first-state
hashes. The standalone verifier regenerates them without a solver or network.
It also regenerates the entire PR3886 single-move premise and checks both source
words with the retained arbitrary-dirty interpreter in both orientations.

## Reproduce

Python 3.12 is the registered environment; the standalone scientific replay
also passes on CPython 3.13.5, Linux x86_64, standard library only.

```sh
python3 -B research/staged544-local-two-add/verify.py --provider base
python3 -B research/staged544-local-two-add/verify.py --provider extra
python3 -B research/staged544-local-two-add/test_checks.py
python3 -O -B research/staged544-local-two-add/test_checks.py
python3 -B scripts/research_package.py --package research/staged544-local-two-add
```

Ordinary execution is read-only, authenticates local source snapshots before
loading retained code, and compares the complete regenerated receipt.
`--emit /an/external/path.json` explicitly regenerates an external receipt; it
refuses to overwrite files inside this package. The registered full census is
bounded separately from the smaller controls. Hosted execution and metadata
checks are reported independently of the original scientific execution.

Controls independently enumerate all 3,118 first-frame intervals by quotient
bases and subset XOR, compare 26 fast bridge cases with full intermediate
traces, and check 3,804 unpruned non-bridge prices. The sample includes every
nonzero fast-bridge case. An actual disabled bridge predicate is detected.
There are 48 exact matrix checks of scale conjugation, source corruption and
resource-bound controls, literal undo checks, and scalar/frame/barrier mutants.
The credited Jeremy Kothe PR2957 counterfactual rollback/recovery still produces
`2+3 -> 1+4` and is rejected by a non-improvement certificate. Wrong-scalar
controls rederive inverse cleanup before testing semantics, so stale cleanup
is not the cause of rejection. This control is not a new current improvement.

## Boundary and cost decision

The declared milestone is a scoped obstruction, not an implementation admission.
Fixed helper widths, buffer identities, entrances/exits, and unchanged gates are
part of the class. Elementary-matrix identities establish scalar equality on
arbitrary dirty state; inverse cleanup is rederived for literal controls.
Frame invoices are fully reconstructed. Each changed-frame intermediate also
passes the separately retained frame auditor. The negative raw comparison needs
no new allocation, and cannot fund added nonnegative cost under unchanged
normalisers and common bills.

Native Clifford phase, full physical allocation, uniform coefficients/stock,
precision, all-size compiler, whole supplier admission, and outer/BIT/analytic
chains were not freshly replayed here. Unknown costs are not zero. In particular,
this is not a claim that every candidate has been admitted as a complete
physical supplier. The expansion decision is **narrow this search away from a
local first displacement**. Repeating the same first-move class with more seeds
cannot alter this exact result.

## Open next questions

Can a first ADD moving across at least two neighbours, with a concrete changed
intermediate frame, unlock a profitable second move? First freeze one such
literal witness and its complete local invoice. This is the nearest escape from
the proved radius-one premise; long-range exploratory samples in this session
were incomplete and are not a barrier certificate.

Can a simultaneous two-frame rewrite, or a changed entrance/exit contract,
realise PR3863's `2+2 -> 1+3` target without an individually legal intermediate?
First provide the exact before/after word and dirty restoration contract, then
price all changed children and consumer costs. This is distinct from choosing
compatible-looking ranks from an aggregate histogram. Native and physical
admission remain separate blockers even after a favourable local identity.

## Sources and credit

Scientific base is canonical main `20ecf2891d80b5acf18d980b2164fb44ea7faa90`,
priority revision 6. Neither the selected certificate nor frozen packages are
modified. `SOURCES.json` pins every local snapshot by byte count, SHA256, and Git
blob. PR3734/dataisfire supplies the words at
`fa041037a3374eaa08feeca0b26a5d6893194147`. PR3886/Chris R supplies the reused
trace, single-move proof, sign criterion, and applier at
`359fe0fe77d29544972fd22ee674085ed5a3b4d0`. Dugongue's PR3863 supplies the
paid-profile target; Jeremy Kothe's PR2957 supplies the existing swap control.
PR2979 and the staged-entry/retiming lineage retain their construction credit.

Sagar Thakrar's auditor and roger-sato's semantic adapter are retained unchanged,
including Arham Tahir's frame-contract attribution. They are not newly
independent interpreters. New reductions, paired census, and controls are by
Chris R / Clear1nsight with substantial OpenAI assistance. Apache-2.0 and all
notices in `vendor/SOURCE-CREDITS.md` apply. There is no independent human or
formal-kernel review claim.

The official overlap helper refreshed 630 open PRs and 2,544 Discussion records
with complete pagination at 2026-10-19 03:39 UTC; local-note coverage was limited
to the exported inputs. PR3890's width-price region is a different contract.
The upstream claim comment was denied with HTTP403; no posted upstream claim is
asserted. Temporary fork-only input-export infrastructure is excluded from this
research PR. Exact execution, exploration limits, and publication checkpoints
are recorded in `VALIDATION.json`.
