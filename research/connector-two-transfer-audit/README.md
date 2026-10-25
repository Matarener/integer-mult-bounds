# Independent check of the two-transfer 73-map connector exclusion

Both exceptional multiplicity cases in conorholds' [PR2208](https://github.com/CrocSwap/integer-mult-bounds/pull/2208)
pass a new standard-library census with a different exhaustive reduction.
The contribution closes its explicitly stated single-implementation gap for
this implication. The existing tariff theorem is credited predecessor work.
No new kappa, physical supplier or selected-frontier improvement is claimed.

The [coverage proof](PROOF.md) rotates a restoring word to its first transfer,
solves source restoration in the two contiguous phases, and checks every
possible paired or triple read. The implementation imports no predecessor code.
[RESULT.json](RESULT.json) records all eight domains, exact histograms and
ordered candidate digests.

| Five-source case | New restoring assignments | Maximum masks including zero | Successful completions |
| --- | ---: | ---: | ---: |
| Paired sources, one three-read output | 145,080 | 31/32 | 0 |
| One three-insertion source, paired outputs | 1,401,120 | 31/32 | 0 |

Multiplying each new histogram bin by 12 or 13 exactly recovers the predecessor's
full 1,740,960- and 18,214,560-assignment histograms. The marked-transfer
counting argument explains these factors, including rotational stabilizers.
The verifier recomputes every bin before comparing with the pinned receipt.
Both original two-transfer native censuses were also freshly replayed locally.
Their four-transfer census was not rerun.

A separately implemented set-valued oracle checks all 116,400 small port
assignments in both root orientations, including all 2,796 restoring cases and
their complete two- and three-read mask sets. Four literal positive words include
both odd-multiplicity cases and the credited 74-call and 78-call five-source
witnesses. They pass 552 dirty-basis/mixed-state forward/inverse pairs with
singular and noncommuting maps. All 356 individual omissions and port/direction
changes fail; three invalid domains fail. Behavioral controls also reject actual
faulty producers, changed source bytes and a counterfeit result receipt.
[CHECKS.json](CHECKS.json) and [VALIDATION.md](VALIDATION.md) give the coverage.

## Exact scope

Sources are immutable; roots and outputs start arbitrary; outputs are observed
only at completion. Complete operations are `z_p += B_j x_j`,
`y_m += A_m z_p`, `z0 += z1`, and `z1 += z0` over F2. Each named map is fixed
across occurrences and arbitrary compatible dimension. Every child restores
private scratch and agreed heads/frames. No extra root, source write, root
frame, clean row, output feedback, combined call or direct product is allowed.
The audited domain has 73 map calls and two transfers. The arbitrary-dimension
statement uses the formal coefficient proof, not finite dense extrapolation.

This supports only PR2208's existing implication in the equal-price result
`min(74c,72c+6sigma)`. The other lower bounds and attaining constructions remain
inherited. Unequal map/port prices, an actual recursive caller, admission,
preparation, storage, routing, hosting, precision/tape, both supplier moments
and outer multiplication transfer are separate obligations. No complete
selected cold replay, formal-kernel or independent human review is claimed.

## Reproduce

Python 3.12+, standard library only, from the repository root:

```sh
python3 -I -Werror -B scripts/research_package.py --package research/connector-two-transfer-audit
python3 -I -O -Werror -B research/connector-two-transfer-audit/verify.py
python3 -I -O -Werror -B research/connector-two-transfer-audit/independent.py
python3 -I -O -Werror -B research/connector-two-transfer-audit/controls.py
python3 -I -O -Werror -B research/connector-two-transfer-audit/test_package.py
```

The registered replay recomputes the census, small oracle, dirty controls and
behavioral tests. `verify.py --emit` emits a recomputed JSON receipt on stdout;
ordinary replay never rewrites evidence. Use an owned external TMPDIR for
behavioral exports. No compiler, Git object lookup or network is needed by the
direct scientific checks. Metadata/provenance checks require repository history.

## Sources and credit

Canonical scientific base is `6f100d4bb5083f8c35d96fd95a539811c62f245c`,
priority revision 6. [SOURCES.json](SOURCES.json) pins retained blobs and SHA256
values. Every declared runtime input is present at that base. No pending branch
object is needed. [TASK.json](TASK.json) records the changed card scope and
neutral review status. Predecessor packages, frozen evidence and selected
records remain unchanged.

Credit conorholds / PR2208, head `28480ef4fdb4caeab89765ea56595bf1f6f37688`,
for the 73-map exclusion, original census and equal-price tariff theorem;
Adam Gall / PR2065 for the credited bidirectional six-transfer endpoint;
Ross Richardson / PR943 and PR934 for the universal connector, prefix boundary
and 74-call repair. Retain the root-contract lineage of woklerx / PR1438,
Gareth Davidson / PR1498, Hanson Sun / PR1615, Cinna Davis / PR1887 and
Discussion1412, and the dirty-commutator lineage of shhxera/CubeJerry and Chafik
Boukhalfa. The related paid-frame single-root exclusion is Arham Garg / PR1945
following Adam Gall / PR1915; it does not replace this two-root check.
New work by Nick Petalas is Apache-2.0.

[Canonical investigation](https://github.com/CrocSwap/integer-mult-bounds/discussions/2049#discussioncomment-19009368).
The live overlap check identified the already-covered tariff before any new
research computation. This independent audit addresses the published remaining
verification gap. It does not reopen the exact same-price optimization.

## Open next questions

The useful construction question remains a real recursive caller with known
complete port and transfer prices. Bind one actual source/reader boundary,
verify dirty restoration and offline observations, then charge admission,
preparation, program/storage, routing and hosting before applying the existing
tariff. No qualifying caller or complete physical bill is identified here.
Further abstract construction searches are not assigned by this audit.
