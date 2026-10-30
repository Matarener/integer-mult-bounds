# Integer/format measured candidate: static review and stop assessment

**Decision: the scoped negative result is supported, subject to the boundaries
below. No new qualified speedup or further 15% result is admitted. No additional
implementation or timing round is recommended from the current evidence.**

This review inspected saved source and receipts only. It did not compile,
import scientific modules, execute arithmetic/tests, time anything, change
measured source, dispatch work, operate a browser or mutate Git. The reviewer
is separate from the parent's numerical execution, but authored the original
C/binder prototype. Therefore this is not an independent-author code audit or
an independent execution replay. It is a static second pass over integration,
coverage, independence and the recorded stopping decision.

## Reviewed artifacts and identity

All paths below are relative to `outputs/c-verification-all-opportunities-20261027/`.

- `stages/integer-complete-v1/candidate_full.py`, SHA256
  `e0978a90c63e5294a1ed04863c3966016b64a62a561e914d50821b08846ace72`.
- `stages/integer-complete-v1/baseline_full.py`, SHA256
  `470096a40078958bd4e32f99e312a44672613c2d93a76c9cbfd8d8fb6474471f`.
- Measured `integer_format.c` and `integer_binding.py` match the handed-off
  source hashes exactly: respectively
  `804cc25bd9ad0912de81fe97bc65b95ebcb0dec06453739e1d4863e7946c4f3d` and
  `dd3e4387dfb8882a524d938d866ed7ae04cd5ac938bbbcbec4eefd15f4bdcc9d`.
- `INTEGER-COMPLETE-GATE.json`, observed SHA256
  `85b9bca95c83e312f55f5d60748292033e3802697c21f757dec912fc95fe6b6e`.
- All six `runtime/runs/integer-complete-{B1,C1,C2,B2,B3,C3}/` final scientific
  receipt lines and guarded process receipts; fuller B2/C2 native/Observation
  records; archived original single-pass `candidate.py` and `custody.py`.
- The frozen PR5864 `baseline-public/{full.py,finite.py,frozen.py,README.md,
  benchmark.py,VALIDATION.json,VERIFY.json,verify.py,replay_driver.py,custody.py}`
  boundaries, and original `Observation` implementation.

The raw six scientific receipts have the same source result digest
`cc7739703ed23532d187949c8507d09c13ac4c152e07a930f0087cde0d7a3d98`,
25,984 events, 799 coordinates, 120 finite programs / 4,240 fixture events,
three integer rejections, six source controls, and complete actual witness
comparison. Every guarded process receipt inspected records exit 0, empty
stderr, unchanged source bytes/modes, no termination, and sampled RSS below
the parent cap. These are saved execution records, not executions by this
reviewer.

## Recorded performance decision

The fixed BCCBBC comparison records median wall/CPU of
34.661785392 / 34.47 seconds for B and 32.418777812 / 32.33 seconds for C.
The descriptive reductions are 6.471125% wall and 6.208297% CPU. The absolute
median differences, 2.243007580 wall and 2.14 CPU seconds, are smaller than the
recorded maximum repeat spreads, 2.713637238 wall and 2.35 CPU seconds.

Thus both the 15% target and the declared conservative noise gates failed.
The median numbers may be reported as descriptive raw observations, accompanied
by the failed gates. They are not a qualified smaller positive increment.
No sample may be discarded, and source edits or repeated timings cannot
retroactively repair this six-process result. The synthetic micro result does
not overturn this decision; its candidate commands paid cold compilation and
checks outside the inner batch timer.

## Coverage review

The new wrapper retains the frozen `full.main(True)` native finite work and
original source-bound Fraction trace adaptation. Its only additional complete
qualification seam is the authenticated integer module load at
`candidate_full.py:56-58`. The replacement checks an exact occurrence and
constructs a fresh candidate integer module using the pinned original source.
The new finite probe and integer cold build execute before `main(True)` and
are therefore inside the parent's outer process timing. The prior Fraction
native build, checks and actual bookkeeping counters remain present.

The archived original `qualify()` still performs the following work after the
integer replacement:

1. It runs `contract.calculate(p, candidate)` and compares the complete result
   against the frozen expected result, including source controls.
2. It runs a fresh original calculation through the unchanged PR5864 Fraction
   arithmetic/native-bookkeeping path and compares complete results.
3. Separate one-use Observations retain the actual ideal metadata/local weights
   and full error trace/signed witnesses, then compare both full values.
4. It runs the unchanged 120-program differential against the literal reference,
   including reverse equality, and checks the exact frozen qualification receipt.

The 27 Observation labels remain in the inherited entry-point finite run. The
118 inherited/native controls remain in the PR5864 finite run. The added
integer probe's 27 labels comprise six positive case groups and 21 rejection
paths; they are not 27 independent rejection cases. The eight row cases and
six ordered prefixes are separately recorded. Nothing in the candidate binder
replaces a full witness comparison with a digest-only check or samples hash
entries. Peaks, role tie-breaking, Pareto selection, returned Fraction types
and the public Engine call signatures remain in the unchanged Python outer
code. No additional scientific coverage omission was found in this review.

### Custody is separate from this timed scope

Neither measured wrapper invokes `custody.main()`. The portable
`replay_driver.py` does invoke it. This initially looked like missing timed
coverage, but the frozen PR5864 README line 19 and VALIDATION scope explicitly
place all four unchanged custody controls outside both timed candidate stages.
Its original `benchmark.py` uses `full_B.py`/`full_C.py` under that same boundary.
The current six samples therefore match the **complete frozen qualifier**
benchmark scope; they do not measure the full portable replay-driver command.

Publication must preserve and freshly run the separate registered custody
checks. The parent has stated it will do so; this review does not pre-claim
that later result. A separate successful custody replay must remain separately
identified and must not be added retroactively to the six measured commands.
No timing reroll is needed to preserve the scoped negative conclusion.

## Independence review

The integer numerical implementation has changed. The wrapper correctly emits
`integer_backend_changed=True` and `baseline_fraction_arithmetic_unchanged=True`.
It does not carry forward `integer_oracle_unchanged=True` as a current claim.
The fresh binder modifies only its newly created integer module. The inherited
PR5864 adaptation of a separate Fraction module remains exactly the same
numerical operation/bookkeeping route as before this round.

This means no **new integer C arithmetic** is shared with the Fraction
reference path. The two paths still share CPython's arbitrary-size integer
substrate and some original semantic helpers, as the predecessor already did.
They are distinct representations and computation paths, not independent
big-integer implementations, a proof of arbitrary C memory safety, or a
machine-checked correctness theorem. The retained source pins and output
agreement must not be described more strongly.

The literal `reference` used by the original finite differential is loaded
separately from the original calculation's observed Fraction module. The
new wrapper patches neither that literal reference nor its finite algorithms.
The actual PR5864 Fraction cache counters, output digest and one-use
Observation remain independently checked in the complete qualifier.

The binder receipt fields `source_only_handoff=True` and
`whole_replay_qualified=False` are historical construction metadata emitted by
`derive()`. They describe what that binder itself establishes; the surrounding
run later produces the actual qualifier receipt. Preserve the measured record,
but explain this distinction so readers do not interpret those fields either
as a later execution failure or as evidence that the binder alone qualified a
whole replay. Likewise, retained source docstrings saying all arithmetic is
unchanged are predecessor text, not the new candidate's scope statement.

## C and API limitations

The implementation keeps coefficients, scales, products and scores as exact
arbitrary-size PyLong objects. `PyLong_AsSsize_t` is confined to Python sequence
indices; it does not narrow numeric coefficients. Exact division tests the
remainder before accepting the quotient. The signed dyadic formatter uses
positive common power-of-two reduction, preserves zero and signs, and keeps
coefficient `/1` formatting distinct from Fraction-style score strings.
The parent finite/full receipts supply observed checks for this implementation;
this static inspection found no arithmetic or canonical-byte mismatch in the
supported path.

Fresh output dictionaries and score tuples avoid ordinary input alias mutation
and preserve inputs after failed row operations. The internal `add_row` helper
now returns a fresh dictionary instead of mutating its destination and returning
None; the binder changes both internal call sites accordingly. The supported
compatibility statement is the selected Engine/qualification workload, not a
drop-in replacement for arbitrary downstream code importing that old helper.
The new C API deliberately rejects bool/subclasses/foreign containers; it is a
new guarded interface, not semantic equivalence for every Python object the
old unguarded helper might accidentally accept.

The code assumes stable inputs/runtime during each native operation, matching
the scoped predecessor assumption. It retains borrowed dictionary items across
allocations and `PyDict_Next` loops. It does not establish safety against
arbitrary signal handlers, finalizers, reentrant callbacks or concurrent code
mutating supplied dictionaries during such a call. Ordinary alias fixtures do
not prove hostile asynchronous-mutation safety. In the complete Engine path,
those rows/scores are internal and no foreign callbacks are intentionally
invoked. Do not advertise this feasibility module as a generally reentrant or
free-threaded library. No claim of abi3, subinterpreter or other Python-version
support follows from Linux CPython 3.12 checks.

These limits do not reverse the scoped negative engineering result. They are
reasons to retain the prototype label and precise supported domain rather than
promote it as a generally qualified native library.

## Bounded broader batching assessment

A fundamentally broader design is conceivable while leaving PR5864 Fraction
numerical arithmetic untouched: a per-invocation native owner for validated
integer state. It would snapshot/validate the input operation and weight plan
once, own all mutable rows and score triples, and traverse a whole forward or
reverse integer program without returning a fresh row and revalidating it after
each event. Inside that ownership boundary it could mutate its own dicts,
retain constant scale metadata, and append canonical bytes directly, exposing
only the same completed outputs and required witness snapshots.

That is materially different from replacing another small Python arithmetic
call. It targets concrete bills in this candidate: repeated `int_row` scans,
`PyDict_Copy` per sparse update, temporary score tuples followed by Python list
conversion, per-event crossing/packet handling, and repeated scale validation.
It would retain arbitrary-size integer operations, exact dyadic rejection,
full event ordering, complete bytes and all observations. The unchanged
Fraction run would still execute afresh; no candidate result could stand in
for it. Any input plan reuse would need an explicit per-invocation ownership
contract and could not become cross-trace answers or cached PASS receipts.

However, the present data does **not** show that those removable bills contain
the several additional seconds necessary to move from the descriptive current
result to a further 15% complete reduction with its larger validation/build bill.
The source profile is instrumented and nested. The measured candidate is already
native inside the large sparse loops. Row validation/copying might be the
remaining bottleneck, or might account for far less than the shortfall; this
review cannot distinguish those possibilities. Moving the outer loop also
expands the proof/qualification surface for peak cuts, ordering, clearing,
source isolation, exception behavior and witness snapshots.

Therefore the architecture is a deferred hypothesis, not a presently funded
construction or an impossibility result. Current evidence supports stopping
this round and publishing its bounded negative result. If a future separately
authorized round is considered, its first gate should be a fixed diagnostic
attribution of the unchanged candidate's integer-state and crossing/copy costs,
with all outputs still computed and compared. Only evidence that a sufficiently
large removable bill exists after the complete new control/build/ownership
cost should authorize a private-state prototype. Freeze that gate and one
bounded discriminating fixture before implementation; do not reuse this
round's failed six timings as a new performance admission.

No such diagnostic, implementation, test or new route was performed here.
