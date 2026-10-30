# Sharp T16 profiles with distinct physical families

Both sharp pooled T16 integer profiles now have complete assignments on the
literal selected1094 windows with one helper per physical family per call.
Every helper keeps its actual call and width, avoids the active data pair,
and occupies a disjoint contiguous reservation. The source-bound exact
checker reconstructs and checks all 69,120 helpers in each assignment.

Combining this new attainment result with the separately replayed PR3378
pooled lower bound gives the exact finite-hosting idle-cost envelope for
all real `0<=a<=1/2`, with `p=1-a`:

```text
min(2431+17^p,2429+5^p+14^p) + 4887*48^p.
```

This closes PR3395's omitted distinct-family/active-pair question for the
stated supplied-window problem. It does not close chart/native/controller
admission, independently derive the windows from the source program, or
supply a new kappa. The selected frontier is unchanged.

## What changed

PR3395 realized the two integer inventories in a temporal relaxation.
Its old/new flows can assign 331/296 helpers of one call to a group of only
224 physical bins. A fresh integer flow now limits each call's use of a
pattern to that pattern's number of bins. Bipartite multigraph colouring
then produces literal assignments with distinct calls in every bin.

[PROOF.md](PROOF.md) proves sufficiency and states the finite model exactly.
CERTIFICATE.json has 1,342 and 1,266 nonzero new flow rows. The original
pattern tables and window-group allocation retain PR3395's credit. The two
idle profiles are `{1:2431,17:1,48:4887}` and
`{1:2429,5:1,14:1,48:4887}`, each with residual rank mass 237,024.

## Replay

Python 3.12 or later; standard library only. From the repository root:

```sh
python3 -B scripts/research_package.py --package research/t16-distinct-call-attainment
python3 -I -O -Werror -B research/t16-distinct-call-attainment/verify.py
python3 -I -O -Werror -B research/t16-distinct-call-attainment/independent.py
python3 -I -O -Werror -B research/t16-distinct-call-attainment/test_verify.py
```

The registered replay authenticates PLAN, SPEC and the selected source
manifest, checks all integer equations, constructs perfect matchings and
validates every expanded owner row. `independent.py` imports no project code
and separately checks the sufficient degree conditions and source-family
geometry. Tests cover 120 tiny feasible pattern systems, 86 regular
multigraphs with exhaustive matching oracles, malformed flows, literal
owner faults, family/window changes and actual optimized CLI source mutants.

To export both original-schema nominations, use a new external directory:

```sh
python3 -I -Werror -B research/t16-distinct-call-attainment/verify.py \
  --owners-dir "$RUN_ROOT/owners"
```

This writes `OWNERS-old.json.gz` and `OWNERS-new.json.gz`. Compare decompressed
payloads across Python/zlib versions. The map-row hashes in RESULT.json are
independent of compression. Reusing an existing output directory fails.
The source PLAN's old profile, SPEC hashes and admission receipts are not
updated by this export. A physical admission must construct its own derived
bindings and recompute its full invoice.

The continuum lower bound is an explicit external proof dependency, rather
than part of this package's ordinary feasibility replay. Pin and replay it
separately without creating another checkout:

```sh
git fetch --no-tags https://github.com/CrocSwap/integer-mult-bounds.git refs/pull/3378/head
# Require FETCH_HEAD == 08da381d84bfc5eda02dad5008ddb00edb9bf9f2.
python3 -B scripts/export_research_package.py export \
  --package research/t16-integer-phase \
  --ref 08da381d84bfc5eda02dad5008ddb00edb9bf9f2 --output "$RUN_ROOT/phase.tar"
python3 -B scripts/export_research_package.py check "$RUN_ROOT/phase.tar"
mkdir "$RUN_ROOT/phase"
tar -xf "$RUN_ROOT/phase.tar" -C "$RUN_ROOT/phase"
python3 -I -Werror -B "$RUN_ROOT/phase/research/t16-integer-phase/verify.py"
```

Expected output is `PASS_T16_INTEGER_PHASE 56987`, with 6,850 concavity,
330 Bernstein and one symbolic comparison types. This replay passed locally
from the exact committed export. DEPENDENCIES.json records public source
URLs, hashes and Git blobs. No pending predecessor Git object is required
by the new registered replay.

## Verification and limits

Discovery used SciPy 1.18.1/HiGHS 1.12.0 to find the certificate. Solvers and
private discovery scripts are absent from acceptance. CPython 3.12.15 normal
and optimized replays, the independent degree audit, behavioral controls and
Ruff diagnostics pass. The inherited `hosting/reuse_owners.py:audit_roles`
from the pinned selected archive separately accepts both exported maps.
That check tests finite owner validity, not the complete physical controller.

The supplied windows, selected local word and actual per-call widths are
unchanged. Full native/frame/chart/stock/controller/hosting/precision/tape,
all-size/compiler, common-label/mutable-source, outer analytic and bit-side
H1-H5 obligations remain separate. No selected cold replay, Lean proof,
independent human review or hosted-CI success is claimed.

The implementation uses bounded Python allocations, a managed-runtime
exception to Power of Ten rule 3. Inputs are at most 8 MB; the graph is at
most 144 by 144, each colouring uses at most 224 matchings, and each map has
69,120 rows. No recursion or solver enters acceptance. The tiny oracle uses
bounded exhaustive loops and unittest dispatch, a rule 9 framework exception.
Every rejection is an explicit check that remains active under `-O`.
New Python functions stay below 60 physical lines. Follow-up: retain these
bounds if the template grows, and split the replay before admitting a larger
runtime/memory domain. Shared or frozen code is unchanged.

## Open next questions

- Can either nomination pass the unchanged complete native/controller/chart
  and stock admission? First export one map, derive its PLAN/SPEC bindings,
  and run the existing strict controller against the actual charts. The
  missing invoice prevents a supplier or kappa claim. Stop at the first
  failed budget rather than treating the finite optimum as admission.
- If chart costs reject this allocation, what extra exact constraint makes
  the pattern-flow certificate reflect the failing physical budget? Start
  with that concrete rejecting chart/invoice entry. Any new optimization
  needs a complete cost ledger and an explicit expansion decision.

## Sources and credit

Base canonical main `6f100d4bb5083f8c35d96fd95a539811c62f245c`, priority
revision 6. SOURCES.json pins PLAN/SPEC through selected1094's source
manifest. DEPENDENCIES.json pins the separate PR3378 lower-bound proof and
records PR3395's temporal construction and the inherited owner-audit source.

Credit Ali Romman/PR1129, Hanson Sun/PR1914, PR3352/3364/3378/3395, Rohan
Arun/PR1094, Jeremy Kothe/PR1087 and the predecessor packing work, Hao Yan
FanPUYen/PR858, Philippe Van Velzen's strict-admission work, and the retained
geometry/owner/compiler/bit-supplier lineage. PR3390's repeated physical
augmentations and PR3396's fixed-buffer transport cut are complementary;
this result does not repeat or supersede their full admission evidence.
New contribution by Nick Petalas. Apache-2.0.
