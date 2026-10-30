# Verification limits and implementation checks

The mathematical claim and finite-alphabet cost model are in PROOF.md.
This note records the verifier's boundaries.

## Local checks

CPython 3.12.15 on macOS, standard library only, passes direct isolated normal
and optimized execution with warnings treated as errors. Their single measured
wall times were 0.19 and 0.22 seconds. These establish replay timeout headroom,
not a performance comparison. The registered package runs those same two
commands with 60-second limits and passes metadata/source validation.

The selected baseline initially failed because its source closure was omitted
by sparse checkout. After materializing its 41 research roots, the unchanged
baseline reports PASS_RESEARCH_BASELINE_BINDINGS_ONLY. This is orientation,
not a selected scientific replay. The new package changes no selected input.

The verifier executes all 10,000 local rules through finite injectivity and
write-permission checks. Literal paths then check the new implementation's
actual output, returned head, preserved tape, marker erasure and exact bill.
It does not replay the predecessor's 144-pair probability/optimality census.
The expected-cost consequence uses the cited predecessor mean.

No Lean, Docker, full selected/native replay, binary-alphabet lowering, actual
caller integration or conditional-randomness reuse was run or proved.
No independent human or proof-kernel review is claimed.

## Code constraints

`machine.py` has no recursion. Every machine-building loop is bounded by the
fixed 312-state source graph, 624 edges, 624 reverse targets or four output
symbols. The observer accepts at most 1,024 binary fixture symbols, start offsets
1 through 64, and at most 10,000 steps. It fails on a missing transition,
exhausted fixture, exhausted step budget or unreturned tape/head.

`verify.py` visits the 1,024 ten-bit fixtures, four output values, and 470
compact prefix levels with at most three unfinished prefixes each. It never
expands the full depth-470 binary tree. All new functions are at most 26 lines.
Contracts use explicit exceptions, so optimized Python retains them. Source
byte hashes are checked before executing the retained sampler definitions.
The modules compile cleanly under `-W error`; ruff, mypy and pyright are not
installed. No repository-wide analyzer configuration was changed.

The following bounded deviations from low-level allocation/call restrictions
are explicit:

- Python allocates dictionary entries, tuples and observer traces dynamically.
  The target is a finite machine description; its 10,000 rules are constructed
  before execution. The observer's bounded fixtures and 10,000-step cap bound
  live data. Python allocation is not claimed to implement constant physical
  auxiliary storage. A future physical lowering must use the finite rule model.
- Loading executes source bytes for two fixed Python modules. The retained
  predecessor is hash-authenticated before compilation, `main` is not called,
  and only `make(1,1)` is used. New machine bytes compile directly without
  bytecode-cache lookup. There is no input-generated code or plugin registry.
  The required module registration supports the frozen Trace dataclass.
- Negative controls use fixed local lambdas. Their targets are explicit and
  bounded. No machine rule dispatches through a Python function pointer;
  rules contain only finite data.

These deviations apply to the checking program. They do not add a stopping
counter, Python heap, callback or absolute-address test to the machine's finite
control. Binary gate implementation remains an open question.

The internal read-only review found no blocking issue in the construction,
proof or initial checker. It identified missing source bindings and draft
packaging as follow-up items. RESULT.json now binds the proof, machine,
verifier and retained sources by SHA256; the completed package passes its
registered checks. The review does not constitute independent human acceptance.
