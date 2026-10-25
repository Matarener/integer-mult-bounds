# Engineering decisions

The task is the specific encoded-control implication left by PR3582. Build the
Lever changed the deliverable into a rerunnable current-cell counter/controller
simulator and an independent opcode replay. Prove It Works changed validation
into actual zero/one schedules, source-authenticated arithmetic, exact access
invoices, committed-byte checks and Git-free scientific/control commands.

Power of Ten applies to the new executable paths. The retained predecessor
files are frozen inputs and are not edited or imported. All new functions are
below 60 physical lines. There is no recursion or dynamic evaluation. Core
dispatch has a fixed set of tape roles, 21 counters, eight Boolean registers and
80 data instruction symbols. The only runtime import of external code is the
authenticated canonical circuit oracle in checks.py; it is outside production.

All loops have enforced bounds from descriptor length, physical extent, the
fixed small replay domain or the declared package inventory. Successful core
loops terminate by a delimiter or an actual counter comparison. Overflow,
underflow, unknown symbols, bad boundaries and exhausted diagnostic fuel raise
ordinary exceptions, including under -O. Counter arithmetic contracts and
private/source/head postconditions are checked by the verifier. Host admission
checks grammar, limits, exact types and address extent before execution.

## Bounded runtime deviations

Rule 3, fixed allocation. Python allocates integers, containers and diagnostic
objects during simulation and replay. The physical theorem counts the explicit
preallocated simulated tapes, not Python heap usage. Input limits bound the
simulator's arrays and loops; trace collection is optional and disabled in
production. The finite small verification domain and subprocess timeouts bound
the diagnostic work. Verification does not claim measured Python space. A
lower-level runtime implementation would require its own allocation evidence.

Rule 9, indirect calls. Python method dispatch and standard-library context
managers are required by the interpreter and temporary-copy controls. Targets
are the named local classes and fixed opcode dispatch; no plugin registration
or untrusted executable target is accepted. The canonical import is source
authenticated and used only as an oracle. The source mutation controls exercise
this boundary. A native implementation would need equivalent ownership and
target checks.

Rule 10, diagnostics. Verification uses CPython3.12 with -I, -Werror and -B,
including deliberate optimized executions. Explicit contracts stay enabled
under optimization. Static lint uses the installed Ruff E/F/B diagnostics with line length 100.
AST inspection confirms that every new function is below 60 lines. Exact
commands and the repository metadata/pin checks are recorded in session evidence. No project-wide diagnostic configuration
or historical replay was changed. Existing broad-tool limitations are reported
without suppressing new diagnostics.

The source formula/layout, counter correctness, accumulator invariant, constant
control graph and polynomial work/capacity bounds are stated in PROOF.md.
No finite result is promoted to independent or proof-kernel acceptance. Scratch,
logs and decision evidence belong in the session-owned external directory.
