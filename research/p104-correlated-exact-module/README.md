# A sharp exact correlated P104 entrance

For the actual first-collector dependency slice, all correlated inputs
Y27=y, Y26=-y have a sharp stagewise exactness condition. In the actual
rank-one transport's right-wrapper coordinates w, every value must be
divisible by 4 and each bit-zero difference must be divisible by 4(1+i).

Equivalently the Newton coefficient on S has exponent at least
`max(|S|,4+1_{0 in S})`. The admitted module has index `2^280` in B9 and
contains the independent 4B9 domain with relative index `2^1768`.
[PROOF.md](PROOF.md) proves necessity, sufficiency and the exact index.
[RESULT.json](RESULT.json) contains the literal source paths and evidence.

This answers a scoped part of PR3426's stagewise-integrality handoff.
It covers the authenticated 257-event dependency slice and arbitrary B9
dirty D/Q inputs, with the other Y sources in 4B9. Noncone banks in the full
prefix have additional obligations. No supplier, new kappa or selected-frontier
change is claimed. The unchanged-profile cost stop remains.

## Reproduce

Python 3.12 and the standard library suffice. From the repository root:

```sh
python3.12 -W error -B scripts/research_package.py --package research/p104-correlated-exact-module
python3.12 -O -W error -B research/p104-correlated-exact-module/verify.py
python3.12 -O -W error -B research/p104-correlated-exact-module/independent.py
python3.12 -O -W error -B research/p104-correlated-exact-module/test_controls.py
```

Use an owned external TMPDIR for temporary CLI fixtures. They remove themselves
without changing file modes. The primary checks all 512 basis vectors and
186 sharp one-pi failures, then executes eight actual complete slice fixtures.
The separate check uses forward histories and all 4096 pair residues.
Actual optimized CLI controls include one acceptance and three rejections.

The standalone commands are Git-free with this package plus the two declared
inputs from `research/p104-rounded-collector/inputs/`. SOURCES.json pins those
canonical-main bytes. Frozen predecessor proofs are retained in this PR's own
history, with their origin hashes in inputs/ORIGINS.json. No pending source
commit needs a separate fetch. Registered replay additionally validates Git
provenance. Independent human and formal proof-kernel review are unclaimed.

## Open next questions

Which further congruences admit the noncone outputs of this same full prefix?
Start with the other actual Y27/Y26 reads, intersecting their stage constraints
with the explicit module here. This matters before treating the slice as an
actual caller entrance. General rounded trajectories are still unclassified.

Can a paid caller prepare this correlation and preserve all consumers cheaply?
Bind the real preparation, ownership, restoration and output histories, then
apply the family expansion gate. The algebraic index supplies no free operation
or storage saving. No further construction round is reserved.

## Credit and scope

Nick Petalas/PR3426 supplies the preceding correlated handoff; Clear1nsight's
PR3382/3423 supply the Newton and producer boundaries; PR3416 supplies finite
native covariance. Credit ywz65/PR2586, Arham Tahir/PR2665, Tekalign/PR3025,
Ross Richardson/PR3068 and the retained source lineage. New work is Apache-2.0.
Predecessor attribution and notices are retained unchanged.

The original card is `p104-side-correction`, priority revision six. This is a
declared interface result. Inherited alphabet/covariance proofs, noncone
admission, physical pricing, all-size transfer, human/formal review, Lean,
Docker and the selected cold replay are not supplied by these finite checks.

The final overlap refresh found Clear1nsight's concurrent
[general 58-bank claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/2750#discussioncomment-19009685),
posted after this two-source investigation began. That claim targets the full
correlated cone entrance and an encoder. This independent two-source result
supplies a sharp calibration case and does not claim that broader classification
or duplicate a published general result. Its evidence status remains provisional.
