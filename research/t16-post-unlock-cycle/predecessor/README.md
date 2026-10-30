# Five interacting helpers improve the PR3359 T16 packing

A neutral swap followed by a three-helper cycle gives conditional finite
`kappa = 0.001673627634134309`, an exact gain of `7.61110280e-10` over
[PR3359](https://github.com/CrocSwap/integer-mult-bounds/pull/3359). This answers
its explicit neutral-rearrangement question. Two rank-one idle remainders
become one rank-two remainder; every other paid count and physical invoice
charge is retained. This is a further packing witness, not an optimum or a
selected-frontier update.

The neutral pair is `(34864,43904)` and the forward triple is
`(37210,30301,31680)`. The shared bin `(11,14,1)` loses two original width-eight
helpers and gains widths seven and nine. Five distinct helpers relocate and
18 rows change including offsets. The [proof](PROOF.md) gives the bin ledger
and exact inequality `2^(1-a) < 2` for every `0 < a < 1`.

## Evidence and replay

Requires standard-library CPython 3.12. From the repository root, use an
external directory for temporary files:

```sh
RUN="$HOME/.cache/integer-mult-bounds-runs/my-neutral-unlock-replay"
mkdir -p "$RUN"
TMPDIR="$RUN" python3.12 -Werror -B scripts/research_package.py \
  --package research/t16-neutral-unlock
```

The registered command checks all source pins, reconstructs the complete
PR3359 owner payload, audits the neutral intermediate map and final map,
prices both supplier paths, runs the unchanged eleven-stage strict admission,
compares the entire typed invoice, and checks the fixed-word packing cap.
It then runs eleven behavioral groups normally and with optimized Python.
Expected final markers include `PASS_T16_NEUTRAL_UNLOCK` and
`PASS_REGISTERED_RESEARCH_PACKAGE`. Assertions in the inherited admission
must remain enabled; only the behavioral controls run under `-O`.

To retain freshly generated owner/PLAN/SPEC files and admission evidence:

```sh
TMPDIR="$RUN" python3.12 -Werror -B research/t16-neutral-unlock/verify.py \
  --work "$RUN/fresh-evidence"
```

`fresh-evidence` must not already exist. The normal replay is read-only with
respect to the package; `--write` is only for regenerating its result receipt.
No solver or unmerged Git commit is needed. The exact predecessor array is
reconstructed from canonical main bytes plus `predecessor.patch.json` and
checked against PR3359's retained complete-payload digest.

[RESULT.json](RESULT.json) is the deterministic mathematical receipt.
[ADMISSION.json](ADMISSION.json) and [INVOICE.json](INVOICE.json) are observed
outputs of the first successful full local replay on CPython 3.12.15, macOS
arm64. Admission stage times are observations, not performance claims or replay
acceptance criteria. Fresh replay proves its own coverage; old PASS fields do
not replace execution. Compressed bytes may differ across Python/zlib versions;
owner equality uses the complete canonical JSON payload.

The full replay passes 69 admission controls, 12 bit controls, six independent
T16 controls and 15 controller mutations, plus eleven independent owner controls.
Both seven-step bootstrap paths and all 47 strict outer inequalities per path
pass. Complete rank mass remains 1,041,408 with deficit 5,120. Prefix 397 is
still charged at 512 and the physical row coefficient is 16,469. Actual charts
fall from 10,008 to 10,005, with no reduction in the retained paid invoice.

The native complex endpoint is
`1676433359331271080293 / 10^24`; the retained bit endpoint is
`1733427039589844234749 / 10^24`. The conservative path gives
`kappa = 0.001673627631281533`. Complex binds. The fixed-word kappa cap is
`1690054109089 / 1001690054109089`; this witness realizes about 99.1954% of it.
That cap concerns the fixed local profile and stated coverage/halving model,
not every possible multiplication construction.

Controls reject an omitted neutral move, partial exchange, reversed triple,
wrong physical family or width, overlapping roles, a legal but non-neutral
first swap, corrupted predecessor bytes and invoice value/type/key/order
changes. Identifier-only rebinding and JSON object key order are allowed.

## Scope and credit

Canonical base is `6f100d4bb5083f8c35d96fd95a539811c62f245c`, priority revision 6,
card `selected-packing`. Exact predecessor is PR3359 head
`3bdc260e996fd3a94dcb7560b68f2c61d2253d80`. Its seven prior cycles remain present.
[Sources](SOURCES.json), [retained predecessor](predecessor/README.md),
[export binding](SOURCE-EXPORT.json) and [task](TASK.json) specify the lineage.

Credit Pierre / hexapode for PR3359's six composed cycles and question;
Nick Petalas for PR3354/3338; Gonzalo Mier for PR3308; Philippe Van Velzen for
PR2169; Jeremy Kothe, Rohan Arun, Hao Yan, George Lydakis, Josie Elliston and
the retained native/compiler/bit/moment sources. Their notices are preserved.
New material by Nick Petalas is Apache-2.0. Substantial automated assistance was
used; no independent human review or formal-kernel proof is claimed.

The concurrent worker-2 direct-cycle investigation starts from the same map
but permits exactly one original helper out and in per bin. This witness has
two departures and two arrivals at the shared bin, so it is outside that
restriction. Its independent finite boundary check reproduces this map and
idle delta; it does not substitute for the full admission here.

All selected all-size/compiler, common-label/mutable-source realization,
whole-call hosting, precision/tape, exact-recovery, analytic-transfer and bit
H1-H5 assumptions remain. Local native ancestry is source-bound reuse, not a
fresh cold native rebuild. No full multiplication theorem, global-best claim,
hosted-CI success or selected supplier admission is claimed.

## Engineering boundaries

Build the Lever produced the literal reconstruction and paid replay.
Prove It Works required actual eleven-stage execution and entire typed invoice
equality. Laziness Protocol kept the search private and the published artifact
to one exact witness. Separate Before Serializing Shared State kept outputs and
owned source files separate from the other four workers, with process-held
ownership and serialized shared Git mutations.

All new loops have fixed input bounds: 69,120 roles, two swap roles, three cycle
roles, 512 patch rows, 100 source rows, 32 MiB JSON inputs and 112 ports per
window. The archive loader caps 500 files and 128 MiB expanded source. The strict
subprocess has a 300-second timeout. New functions are below 60 physical lines.
Checks use explicit exceptions and remain active under optimized Python.

[Exact Power of Ten deviations and controls](ENGINEERING.md) cover managed
Python allocation, the fixed
local import loader, and inherited admission/engine code. Python necessarily
allocates decoded objects and temporary arrays; finite byte/row bounds and
single-process execution constrain their lifetimes. Imported sources retain
existing control flow and assertions; source hashes, bounded execution and
mutation controls constrain their use. Replacing those inherited engines is
outside this packing change. Any larger input domain or changed import target
requires revisiting these limits and their controls. New Python is checked
with Ruff and warnings promoted to errors; shared CI settings are unchanged.

## Open next questions

Can another interacting neutral-unlock move compose on this exact successor?
Recompute capacities, windows and same-call family occupancy, preserve this
five-role gain, and check one explicit exchange with the complete invoice.
A new seed or isolated scalar saving is not sufficient. This witness does not
exhaust that domain; no further search is reserved here. Structured first step
and blocker are in [TASK.json](TASK.json).
