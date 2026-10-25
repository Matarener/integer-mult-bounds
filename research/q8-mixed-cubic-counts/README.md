# Mixed cubic Q8 count bounds

For t inverse-generator targets in formal F2[Q8], every positive-i/j
word satisfies

```text
2 n_i+n_j>=3t,       n_i+2 n_j>=3t.
```

The [written proof](PROOF.md) allows arbitrary finite restored dirty
workspace and free binary scalar GL mixing. It derives the exact mixed
cubic correction `E_i L^2 E_j`, then bounds its rank. At n=2t both paid
label counts must equal t, and t and both target multiplicities must be
even. Therefore three zi targets and one zj target cost **ten or twelve**
calls. Neither remaining length is decided.

This strengthens the inherited quadratic rank and parity relaxation for
the 3/1 shape. It does not assert that the degree-two quotient attained
that shape at eight. The homogeneous and 2/2 eight-call boundaries remain
open under the necessary balanced paid count (4,4). Independent human and
formal proof-kernel review are unclaimed. Physical callers, a supplier,
new kappa and selected-frontier changes remain outside scope.

## Replay

Use CPython 3.12. No third-party dependency is needed. Set TMPDIR to a
private external writable directory. From the repository root:

```sh
python3.12 -Werror -B scripts/research_package.py --package research/q8-mixed-cubic-counts
python3.12 -B scripts/check_research_commit.py --package research/q8-mixed-cubic-counts --check-source-history
```

The actual scientific and control commands also work without Git,
network, a solver, compiler or foreign Git objects:

```sh
python3.12 -I -Werror -B research/q8-mixed-cubic-counts/verify.py
python3.12 -I -O -Werror -B research/q8-mixed-cubic-counts/test_package.py
```

[RESULT.json](RESULT.json) authenticates all scientific/runtime sources
and records the complete deterministic result. Replay checks the exact
basis, all 64 Hamilton products, eight cubic products and sixteen
four-increment reductions; 241 fixed mixed-word matrix/action fixtures
on 841 group-identity input columns; fourteen sharp rank-lemma fixtures;
680 direct attained endpoints on 25,472 faithful dirty-input columns;
3,756 omitted-factor controls; and PR3551's retained quadratic false
positive. Five optimized behavioral groups reject actual arithmetic,
action, table, rank-hypothesis, domain, source, receipt and overwrite
faults. These finite checks corroborate the proof. They are not an
endpoint search or a minimum-length census.

`--write PATH` writes a candidate receipt exclusively and refuses an
existing file. The normal command compares every receipt field. Bounds,
managed-runtime deviations and verification limits are in
[VALIDATION.md](VALIDATION.md).

## Sources and scope

Canonical baseline is `20ecf2891d80b5acf18d980b2164fb44ea7faa90`, priority
revision 6. SOURCES.json pins canonical provenance. The actual used
PR3536 and PR3558 proofs and PR3551 witness are unchanged under inputs/;
[RETENTION.json](inputs/RETENTION.json) records origin commits, paths,
blobs, SHA256 and credit. Scientific replay reads those retained bytes.

Nick Petalas/PR3536 retains the quadratic chronological bound, PR3558 the
cyclic subspace argument and PR3551 the explicit false-positive fixture.
PR3517, Tuafo/PR2900, ywz65/PR2587, PR3487, Aaron Wang/PR2318, Cinna
Davis, steph4n-gh and the retained Q8/register-model lineage keep their
credit. Arham Tahir/PR3137 and PR3461 have separate physical/scalar costs.
The new contribution is the mixed cubic count theorem and asymmetric
four-negative exclusion. New material is Apache-2.0. Nick Petalas.

[Canonical investigation and original scoped claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/2034#discussioncomment-19012680).
TASK.json preserves the original hypothesis, scope and current result.
No solver or expanded research census ran. The selected full cold replay,
independent human acceptance and formal proof-kernel acceptance are unrun.

## Open next questions

- Decide the ten-call 3/1 shape with a complete word or exclusion.
- Decide whether a balanced (4,4) eight-call word exists for the
  homogeneous or 2/2 shape. Its cubic correction must have rank four.
- Identify an actual caller and complete bill before treating any formal
  saving as a supplier improvement.

TASK.json states each question's relevance, first step and blockers.
