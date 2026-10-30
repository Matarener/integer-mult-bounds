# Exact neutral-first two-edit searches on staged544

This package continues PR3886's explicit open question: can a neutral first
retiming enable a strictly cheaper second gate/frame edit on the literal
PR3734 staged544 words? It preserves all caller, helper, phase and native-warp
interfaces and searches two declared first-edit domains. The result is scoped
to those domains; it is not a global barrier, supplier admission or new kappa.

**Result:** neither declared domain lowers the raw recursive moment for any
real `0<a<1`, on either frozen provider. Each provider has **5,236,828 explicitly
priced second cut/dimension cells**, all with exact non-improvement certificates:

| First/second domain | Legal first words | Second prices per provider |
| --- | ---: | ---: |
| Frame-changing first, displacement <=2; interacting second moves | 122 | 1,035,911 |
| Adjacent neutral swap; second moves of either swapped ADD | 3,752 | 3,155,468 |
| Same adjacent starts; third ADD into the new middle cut | same 3,752 | 1,045,449 |

The adjacent census considers 3,928 commuting pairs and rejects 176 for illegal
frame order. The 3,752 first words in the last two rows are the same starts,
not two disjoint collections. There are 19 second-delta types in their union
(including zero), and seven types in the frame-changing-first domain. Other
third-gate cuts inherit baseline prices by the written reduction. These counts
are an over-approximation of legal second circuits, which makes the scoped
negative result stronger; they are not a count of distinct circuits.

## Search domains

1. Every neutral first ADD retiming at final displacement at most two, including
   frame-only edits, that changes the moved gate's binary frame. Every neutral
   dimension is an endpoint of its admissible subspace interval, so these first
   frames are unique rather than sampled. There are 122 legal first words per
   provider. Search all interacting second ADD retimings, with no second distance
   bound and every second-frame price; disjoint second moves inherit the checked
   baseline obstruction.
2. Every legal neutral adjacent commuting ADD swap retaining both original
   frames. Search every retiming of either swapped gate, and every third gate
   into the new middle cut. A written reduction covers other third-gate cuts
   by their identical-price baseline counterparts. This changes the first-edit
   alphabet beyond the frame-changing starts in domain 1.

The exact counts and signed-profile certificates are retained in CENSUS.json.
PROOF.md gives the frame-completeness argument, new-middle-cut reduction,
arbitrary-dirty algebra, sign certificate and scope limits. Counts are insertion
cut/dimension prices in a relaxation, not numbers of distinct circuits or all
subspace assignments. First words must pass real frame/boundary checks.

## Verification and ledger

The standalone verifier uses Python 3.12 and the standard library. It
authenticates source bytes before executing vendored modules, binds the
enumerator to the full baseline census, checks every first edit by exact
rational local matrices, rederives cleanup, recomputes local bills and checks
all-exponent sign certificates. Full retained free-operator replay includes
632 independent live inputs and 91 arbitrary dirty buffers in both orientations,
the reverse pull-back and cleanup boundary. The complete finite ledger and
remaining physical/supplier obligations are in LEDGER.json.

The positive fixture splits the already-retained Jeremy Kothe PR2957 recovery
into a neutral adjacent swap and a profitable frame-only second edit. It
recovers the literal pinned source with `2+3 -> 1+4`. This is a sensitivity
control, not a new current improvement. The verifier also includes wrong-scalar,
bad-frame, cleanup, noncommutation, source-drift and invoice controls.

Full per-first-word dirty replay, from the repository root:

```sh
python3 -B research/staged544-neutral-two-edit/verify.py --provider base
python3 -B research/staged544-neutral-two-edit/verify.py --provider extra
```

The registered replay uses `--compositional-dirty`: it checks every first block
on independent dirty symbols and fully replays the baseline and positive
controls, rather than repeating 122 whole-word interpreter runs. The full mode
above remains available. Both modes regenerate all search cells, compare exact
certificates and check the complete ledger. Both full normal replays passed:
635.689 seconds for base and 540.046 seconds for extra on CPython 3.12.3.
Assertion-disabled checks repeat the positive fixtures, rejection controls and
retained sign arithmetic; they do not repeat the full enumeration under `-O`.
Finalized execution coverage is recorded in VALIDATION.json.

```sh
python3 -B scripts/research_package.py --package research/staged544-neutral-two-edit
```

The opt-in hook is VERIFY.json. Metadata/history/hosted CI validation are
distinct from mathematical verification. The official registered replay and
metadata/pin checks passed in an isolated fixture with the exact authenticated
canonical Git objects; delivered scientific-code and manifest bytes match that
checked snapshot. The fixture explicitly marks missing older history shallow,
so no full source-history preflight or hosted CI result is claimed. No fresh native
Gaussian/Clifford, physical hosting/allocation, precision/tape, all-size/compiler,
full outer/supplier, analytic or BIT admission is asserted.

## Open next questions

* Can a nonadjacent neutral first move outside the two domains unlock a gain?
  Pin one literal outside-domain word and derive its interacting second-move
  ledger. The missing evidence is a legal source-bound witness, not another
  aggregate histogram allowance.
* Can two coordinated frame changes improve the bill through an intermediate
  word that is not neutral? Supply a literal before/after word and restored
  dirty-state contract before a wider search. Simultaneous legality and full
  physical consumer costs remain blockers.

Structured questions, the explicit user assignment, expansion decision,
checkpoint and overlap limitations are retained in TASK.json. Neither a zero
result here nor PR3886's frozen-baseline certificate can be iterated into a
universal obstruction.

## Credit and provenance

* dataisfire / PR3734, `fa041037a3374eaa08feeca0b26a5d6893194147`:
  literal staged544 providers and retained auditor sources.
* Chris R / Clear1nsight / PR3886 scientific head
  `359fe0fe77d29544972fd22ee674085ed5a3b4d0`: single-ADD relaxation,
  exact sign certificate and source-bound recovery control. The later PR head
  `6e5c125bdc1064a31a8705d42f091e23c94fd659` changes only an unrelated workflow;
  its research package is unchanged.
* Jeremy Kothe / PR2957 and PR2979, with the subsequent staged-entry and
  retiming chain: already-retained circuit mechanism and construction lineage.
* Dugongue / PR3863, `635fe84596c19016f3d0316a5cf7abbe48285490`, and the
  ranked-pair/MathProof predecessors: paid rank-profile targets and accounting.
* Sagar Thakrar's audit_core and roger-sato's semantic adapter are reused
  unchanged. Their Arham Tahir frame-contract attribution is preserved in
  vendor/SOURCE-CREDITS.md. They are not newly independent interpreters.

New neutral-first enumeration, middle-cut reduction, exact block checks and
ledger by Chris R / Clear1nsight with substantial OpenAI Codex assistance.
Apache-2.0 and all retained notices apply. No independent human review or
formal-kernel acceptance is claimed.
