# Exact cyclic inverse-generator tariff

For every positive integer t, exactly 3t positive-g calls are necessary
and sufficient to produce t inverse-g targets with any finite restored
dirty workspace, when g is fixed to i or fixed to j in formal F2[Q8].
Only binary scalar GL mixing is free, and every paid call is a conjugated
binary rank-one idempotent. This closes the cyclic handoff in PR3551,
whose eight-call four-target probes returned unknown.

The [written proof](PROOF.md) uses the full cubic coefficient. In the
n-dimensional call space it constructs two disjoint t-dimensional
subspaces inside a kernel of dimension n-t. Thus n>=3t. Three calls on
each target attain the bound. A separate lemma proves every quadratically
correct n=2t cyclic word has a compressed cubic defect of rank t.
The determinant also forces n=3t modulo four.

The result covers all t; the executable supplies finite corroboration.
It does not decide minima for mixed i/j words. Physical caller, routing,
scalar preparation, hosting, precision, recursive composition, a complete
supplier and a new kappa remain unclaimed. Independent human and formal
proof-kernel review are unclaimed.

## Replay

Use CPython 3.12 and a private external writable TMPDIR. The package has
no third-party dependency. Standalone replay needs no Git, network,
solver, compiler or foreign Git object.

```sh
python3.12 -Werror -B scripts/research_package.py --package research/q8-cyclic-cubic-obstruction
python3.12 -B scripts/check_research_commit.py --package research/q8-cyclic-cubic-obstruction --check-source-history
```

The Git-free scientific and control commands are:

```sh
python3.12 -I -Werror -B research/q8-cyclic-cubic-obstruction/verify.py
python3.12 -I -O -Werror -B research/q8-cyclic-cubic-obstruction/test_package.py
```

[RESULT.json](RESULT.json) records all deterministic fields. The verifier
compares the complete receipt, authenticates its runtime/proof inputs,
and refuses to overwrite an existing `--write` path. Its checks cover
all 4,104 small off-diagonal block matrices, including 578 invertible
ones, 3,120 short labeled words on 49,840 faithful input columns, the
retained eight-call false positive, 24 direct endpoints on 736 columns
and 180 omitted-factor controls. Five optimized behavioral groups check
actual arithmetic/action/rank faults, necessary hypotheses, domains,
source/receipt corruption and exclusive output.

The old residue-only `lower_bound` helper is a coarse numerical control,
not the proof or the exact all-t tariff. Its t=5 value eleven is weaker
than the new written lower bound fifteen. No extra search or enlarged
scientific replay was added for the all-t strengthening.

## Sources and scope history

Canonical base is `20ecf2891d80b5acf18d980b2164fb44ea7faa90`, priority
revision 6. TASK.json preserves the initial four-target hypothesis and
its same-task strengthening. The initial public overlap snapshot covered
274 open PR bodies and 2,389 Discussion records with complete pagination.
Bodies and prose do not cover every diff or unpublished result.

The [canonical investigation](https://github.com/CrocSwap/integer-mult-bounds/discussions/2034#discussioncomment-19012351)
records the original claim and its current status. Exact PR3536 and
PR3517 proof bytes and PR3551 witness bytes are retained unchanged under
inputs/, with origin commits, paths, blobs, SHA256 and credit in
inputs/RETENTION.json. SOURCES.json pins only canonical-ancestor
provenance. Scientific replay reads the retained bytes directly.

Nick Petalas/PR3536 retains the half-call bound, PR3517 the ordered
Gram/core lineage and PR3551 the saturated quadratic witness. The proof
retains the earlier Q8/register-model credit. New material is Apache-2.0.
Nick Petalas.

## Open next questions

- Decide the mixed positive-i/j four-target boundary. Start with its
  noncommutative cubic equations; the single-generator argument does
  not apply.
- Bind a real Q8 caller to a complete alternative invoice. Start with
  PR3137's contiguous layout contract; formal call counts do not price
  routing, scalar, hosting, precision or recursive composition.

TASK.json gives the relevance, first step and blockers for both questions.
