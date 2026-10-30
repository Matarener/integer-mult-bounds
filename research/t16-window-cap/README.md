# Call windows do not strengthen the pooled T16 integer bound

Both sharp pooled integer inventories from
[PR3378](https://github.com/CrocSwap/integer-mult-bounds/pull/3378) fit the
literal selected T16 call windows. Each has an exact assignment of all 69,120
whole helpers to 32,256 disjoint-capacity bins. The assignment preserves every
call's helper widths and every selected window's allowed times.

Consequently the temporal integer relaxation has exactly the same minimum
idle cost as the pooled integer relaxation. For every real `0 <= a <= 1/2`,
with `p=1-a`, it is

```text
min(2431 + 17^p, 2429 + 5^p + 14^p) + 4887*48^p.
```

This closes the timing-only part of the physical-attainment handoff in
PR3352 and the timing/family question in PR1914. The profiles and their
pooled optimality are predecessor results. The new contribution is their
exact temporal realization. A stronger bound must use constraints beyond
the call-window, whole-width and disjoint-capacity conditions retained here.
Family identity, active-pair conflicts and physical realization are omitted.
There is no new supplier, kappa or selected-frontier claim.

## Exact model

The source is selected PR1094's literal `PLAN.json` and `SPEC.json`, at canonical
main `6f100d4bb5083f8c35d96fd95a539811c62f245c`, priority revision 6.
`SOURCES.json` pins their hashes and Git blobs, and the selected source manifest.
The verifier checks the manifest binding and SPEC's PLAN binding.

There are 144 calls. Each has 480 whole helpers, with width/count pairs
`4:56, 5:32, 7:30, 8:122, 9:240`. The 288 source windows each provide 112
separate bins. Every window specifies a capacity in `{8,16,32,48}` and the
call times it allows. A helper must be assigned to a bin whose window allows
its literal call time. Its width occupies one contiguous interval, disjoint
from every other reservation in that bin, including helpers at different times.

The source windows form 144 groups of two windows with identical capacity
and allowed-time sets. Each group has 224 interchangeable bins for this
relaxation. Grouping does not merge capacities or transfer rank between bins.
The checker reconstructs these groups from the pinned source.

This is the fixed selected chronology. It does not use the reordered chronology
of PR3381/3388 or alter any source input. It does not enforce the selected
owner/family or active-pair relation, frames, coefficients, dirty restoration,
common labels, native/controller legality, charts, hosting, precision, the
whole invoice or all-size/outer assumptions. The emitted rows are a temporal
relaxation witness and must not be submitted as an admitted owner map.

## Certificate and constructive proof

`CERTIFICATE.json` stores two profiles, `old` and `new`. Each contains:

- `patterns`, rows `[capacity, [n4,n5,n7,n8,n9], global_count]`.
- `allocation`, rows `[group_index, pattern_index, bin_count]`.
- `flow`, rows `[group_index, call_time, width_index, helper_count]`.

Groups are ordered lexicographically by capacity and allowed-time tuple.
Width indices refer to `(4,5,7,8,9)`. All values are integers. The old profile
has 250 nonzero allocation rows and 2,751 flow rows; the new has 232 and 992.
The discovery optimizer is absent from acceptance.

The checker verifies every group has 224 allocated bins, every global pattern
count is exact, and every pattern fits its own bin. For every group and width,
the allocated helper count equals the flow into that group. For every call and
width, the outgoing flow equals the literal source inventory. Every positive
flow uses an allowed call time. These are exact integer equalities and set
memberships, without tolerances.

These conditions construct a literal assignment. For each call and width,
list its actual helper indices in order and distribute them according to the
flow. For each group and width, match those helper tokens to the pattern slots
in order. Every bin of the group has the same allowed times, so matching
equal-width tokens preserves temporal eligibility. Place each bin's helpers
consecutively from offset zero. The pattern capacity inequality proves
disjointness and fit. Empty bins remain present.

The implementation then checks the resulting 69,120 rows separately from the
flow equations. It requires every literal `(call_time, helper_index)` exactly
once, the actual source width, actual window membership, valid port, contiguous
disjoint prefixes and bin capacity. It independently recounts the idle profiles:

```text
old: {1:2431, 17:1, 48:4887}
new: {1:2429, 5:1, 14:1, 48:4887}
```

Each has idle rank mass 237,024. `RESULT.json` binds the complete deterministic
assignments by SHA256 and records both independently recounted histograms.

Let `P` be the pooled feasible set and `T` this temporal feasible set. Every
temporal packing is a pooled packing, so `T` is a subset of `P`. PR3378 proves
the displayed minimum over `P`. Both inventories attaining that minimum belong
to `T` by the new certificates. Therefore the minimum over `T` equals the
minimum over `P` throughout the predecessor's parameter interval. No new
continuum inequalities or numerical-root calculations are needed.

## Replay and evidence

Python 3.12, standard library only, from the repository root:

```sh
python3.12 -I -Werror -B scripts/research_package.py --package research/t16-window-cap
python3.12 -I -O -Werror -B research/t16-window-cap/verify.py
python3.12 -I -O -Werror -B research/t16-window-cap/test_verify.py
```

Expected output includes `PASS_T16_TEMPORAL_ATTAINMENT` and seven passing test
groups. Set `TMPDIR` to an external session directory to contain replay caches
and the test's temporary source-corruption export. The normal verifier is
read-only. `verify.py --write` regenerates only this package's `RESULT.json`.
Acceptance checks the whole receipt, including both assignment digests.

Controls reject an out-of-window flow, missing or duplicate flow, boolean
count, missing bin allocation, overfull pattern, false idle claim, corrupted
literal offset/width/port/helper, changed source inventory, duplicate source
window time and duplicate source call. An actual optimized CLI replay first
accepts the exported inputs, then rejects a one-byte source change.

The registered command checks the new temporal witnesses. Its lower-bound
dependency is PR3378 at exact commit
`08da381d84bfc5eda02dad5008ddb00edb9bf9f2`, whose proof, certificate, checker
and result have exact hashes, Git blobs and public URLs recorded as external
provenance in `SOURCES.json`. These external records are not checked by the
generic metadata runner and require no pending Git object for normal replay.
During this session the
repository exporter produced and checked that exact committed package; its
standalone verifier passed all 56,987 continuum obligations. That replay is
separate from this package's registered command. To repeat it:

```sh
python3 -B scripts/export_research_package.py export \
  --package research/t16-integer-phase \
  --ref 08da381d84bfc5eda02dad5008ddb00edb9bf9f2 \
  --output "$RUN_ROOT/predecessor.tar"
python3 -B scripts/export_research_package.py check "$RUN_ROOT/predecessor.tar"
mkdir "$RUN_ROOT/predecessor"
tar -xf "$RUN_ROOT/predecessor.tar" -C "$RUN_ROOT/predecessor"
python3.12 -I -Werror -B "$RUN_ROOT/predecessor/research/t16-integer-phase/verify.py"
```

`RUN_ROOT` is an existing external session directory. The exact predecessor
commit must be available in Git for export. Neither this dependency replay nor
the new temporal checks is a full selected `make frontier1094-verify` replay.
No independent human review, proof-assistant theorem or hosted-CI result is
claimed by these local receipts.

Discovery used CPython 3.12.15, SciPy 1.18.1 and HiGHS 1.12.0. Its mixed-integer
model used one variable for each group/pattern count and each allowed
group/time/width flow, with the equations described above and objective zero.
Only the exact checked integer witnesses are evidence. Discovery timing and
the optimizer's status do not enter the claim.

## Implementation bounds

The checker uses structured, nonrecursive control flow. Boundary checks bound
JSON inputs at 8 MB, source pins at ten, calls at 144, helpers per call at 480,
windows at 288, patterns at twelve, allocation rows at 1,728 and flow rows at
30,000. Exact balances bound expansion at 69,120 rows per profile and 32,256
bins. Functions are below the 60-line review ceiling. All acceptance checks
use explicit exceptions and remain enabled under `-O`.

Power-of-Ten rule 3 has a managed-Python deviation. Lists, dictionaries, integer
objects and JSON parsing allocate dynamically. The fixed input-size and domain
bounds above bound the live collections; only one profile expansion is checked
at a time, and source-corruption tests clean their temporary directory on both
success and failure. Fixed allocation would require a different runtime and
is outside this finite verifier. Revisit it if the checker becomes a resident
service or accepts larger domains. The standard-library NamedTuple and unittest dispatch use bounded runtime
registration and calls. Their only targets are the two local checked modules
and seven test groups. This is the rule 8/9 Python framework deviation; all
mathematical call targets remain direct and no external plug-in is loaded.

## Open next questions

Can the near-selected attaining inventory also satisfy actual family and
active-pair compatibility? This is the remaining physical-attainment question.
First bind one literal eligibility relation from the selected strict admission
to the published patterns. Stop at the first unsupported interface or cost.
The present arbitrary same-width matching does not supply those labels, and
another timing-only bound cannot separate this relaxation from the pooled one.
The question and blockers are also recorded in `TASK.json`.

## Credit and scope

Ali Romman/PR1129 supplied the fractional optimum and dual; Hanson Sun/PR1914
independently bound it to selected T16 and posed the timing/family and integer
questions. PR3352 supplied the quantitative integer optimum, PR3364 extended
its interval, and PR3378 supplied the two-profile envelope used here. Rohan
Arun/PR1094 supplied the selected map, following Jeremy Kothe's packing and
local-word work, Rohan's slot discovery, Hao Yan/PR858 and the retained geometry,
ownership, compiler and bit-supplier lineage. Chafik Boukhalfa's related
uniform-dual work retains its predecessor credit. PR3384/3388 and the concurrent
worker's physical constructions concern stricter owner models and are not
repeated or superseded by this temporal result.

Nick Petalas. Development used substantial automated mathematical, code,
verification and writing assistance. Apache-2.0.
