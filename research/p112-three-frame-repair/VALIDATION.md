# Verification and remaining obligations

## Actual environments and commands

Local source-bound checks use CPython 3.12.15 with Clang 23.1.3 on Darwin arm64.
The second interpreter is CPython 3.15.0 with Clang 21.0.0. Python's standard
library is the only mathematical replay dependency. The registered environment
is Python 3.12 with no third-party requirements.

During final checks the shared managed 3.12 executable became mode 0644 and
could no longer execute through the main checkout's virtual environment.
The shared target was left untouched. A complete session-owned runtime copy,
with only its own regular executable made executable, supplied the final 3.12
replay. Its binary SHA256 matched the shared source,
`3274dde21f9767655564d093e63c9a5faacefbf1d41bc1e6bf8b6f6e5a441903`.
The exact private path and source modes are retained in the external session
report. The independent optimized 3.15 checks use Homebrew's executable.

From the repository root, the registered replay is:

```sh
python3.12 -I -Werror -B scripts/research_package.py \
  --package research/p112-three-frame-repair
```

For each of `verify.py`, `independent.py` and `test_controls.py`, the optimized
direct check is:

```sh
python3.15 -I -O -Werror -B research/p112-three-frame-repair/verify.py
python3.15 -I -O -Werror -B research/p112-three-frame-repair/independent.py
python3.15 -I -O -Werror -B research/p112-three-frame-repair/test_controls.py
```

The primary visits 533,382 search states and the separate implementation
2,314,084, including duplicate pops. Both finish all 286 cases without
exhaustion. Their complete group inventories agree case by case. Exact receipts
are committed, rather than just the final negative answer.

Six behavioral test groups cover all 384 four-port family/slot cases, thirteen
complete small geometric subset inventories at five slot counts, the unchanged
attaining witness, budget exhaustion, invalid labels/masks, semantic partition
mutants and three optimized actual CLI corruptions. Exhaustion and corruptions
raise errors. Checks remain active under `-O` because acceptance does not depend
on Python assertions.

Ruff 0.17.1 formatting and the E/F/B/SIM/I/UP/PLW diagnostics pass on the package.
The optional linter is a development tool, not a mathematical dependency:

```sh
ruff check --no-cache --select E,F,B,SIM,I,UP,PLW research/p112-three-frame-repair
ruff format --check research/p112-three-frame-repair
```

The initial card's positive-control ceiling command passed after its omitted
selected sources were materialized. It did not price or admit this different
query-interface result. Initial missing sparse inputs and a draft metadata enum
were corrected before the final registered replay.

## Source and publication binding

The live selected payload is hash-bound through SOURCES.json and declared in
VERIFY.json. PREDECESSOR13.json and UPPER16.json were compared byte for byte with
their public source commits, as recorded in SOURCE-EXPORT.json. Normal replay
authenticates those retained bytes and needs no pending Git history.

Publication checks use:

```sh
python3 -B scripts/check_research_commit.py \
  --package research/p112-three-frame-repair --check-source-history
python3 -B scripts/export_research_package.py export \
  --package research/p112-three-frame-repair --ref HEAD --output "$run/package.tar"
python3 -B scripts/export_research_package.py check "$run/package.tar"
```

Here `run` names an external session-owned directory. After export integrity
passes, extract into that directory and run the three direct commands in a
read-only Git-free tree. Commit-dependent publication checks occur after the
commit; their exact commit and outcome belong in the contribution PR and final
session report. No hosted CI result is claimed by this document.

## Engineering inspection

Build the Lever shaped the retained deterministic checkers and complete case
receipts. Prove It Works shaped the source authentication, actual CLI rejection
fixtures and publication-byte checks. Laziness Protocol kept this change in one
isolated package and removed the exploratory native compiler dependency.
Separate Before Serializing Shared State kept session outputs outside the
checkout, exclusive worker ownership, and advisory locks around shared Git and
task-reservation mutations. The local append-only decision trail remains in the
assigned session directory. Additional agent review was not run because the
assignment forbids extra agents.

Power of Ten inspection found no recursion, generated code, unsafe pointer use,
input-selected dispatch or discarded subprocess result in the new verifier.
Functions fit the 60-line guideline. All geometric loops derive from at most
32 ports, 8,192 groups, nine coordinates or 286 fixed cases; worklists and search
iterations have explicit caps. Source files have byte bounds in the production
boundary, and the controls' subprocesses have 90-second timeouts. Python
exceptions propagate failures; temporary control trees have scoped cleanup.
The control loader names only the two fixed local checker files.

Rule 3, fixed memory capacity, needs a managed-runtime deviation. Python allocates
integers, tuples, lists and sets during exact search. Replacing that runtime
allocation would require a separate native implementation and exceed this
bounded source-verification task. The scope is these two finite case searches.
Compensating controls cap each enumeration and search at one million pops, the
group list at 8,192 and each pending stack at 100,000; only one case is live at
a time. Mask widths are at most 32 port bits and 8,192 group bits. Exhaustion
raises an error, and the tests exercise that path. Portable exact byte usage is
not claimed. A future native-portability task must preserve both complete
receipts and these failure semantics.

## Limits

This is author-checked finite exhaustion with a written reduction and a separate
implementation. It is not independent human review, a proof-kernel certificate
or a complete multiplication theorem. No selected cold replay, Lean, Docker,
native supplier construction, outer transfer or deeper repair search was run.
The claim retains at least ten specified original full frames. Global
fifteen-group attainment, arbitrary fitting matrices, changed reader contracts
and their physical costs remain open. No native saving or new kappa follows.
