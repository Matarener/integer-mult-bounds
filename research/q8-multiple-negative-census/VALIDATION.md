# Validation and limits

The acceptance predicate is exact formal matrix equality, not a runtime speed
claim or a selected-supplier test. `RESULT.json` records deterministic state
counts and hashes. Independent full-convolution sets must equal every stored
native ball before acceptance; SHA256 alone is not the equality test.
`std::unordered_set` resolves hash collisions with full four-row equality.

The registered command uses Python 3.12 and a C++20 compiler. The native source
is compiled on each replay with `-O3 -Wall -Wextra -Wconversion -Wsign-conversion
-Wshadow -Wpedantic -Werror`. Scoped Ruff 0.14.2 checks `E,F,B,UP,SIM`; its format
check passes. Python runs with `-I -Werror -B`, and behavioral checks run with
`-O` too. All mathematical contracts use explicit errors that survive `-O`.
The original selected source-binding command passes after its declared frozen
inputs are materialized. This is distinct from the unrun selected cold replay.

The exact receipt and README describe the independent coverage boundary.
The two largest membership streams are implemented once in C++. The separate
oracle independently regenerates their complete stored inputs and compares
native multiplication against full convolution, but does not repeat every
candidate lookup in those two streams. The smaller meet queries are also
repeated independently. No proof-kernel or independent human review is claimed.

## Power of Ten inspection

1. All production control flow is structured. The touched call graph is
   acyclic; no recursion is used. Subprocesses finish or raise on a timeout,
   and owned temporary directories close on both success and failure.
2. All group loops have size eight or 256. Roles are bounded by four;
   stored depth is at most three at width three and two at width four.
   There are at most 240 factors and five fixed cases. The largest stored
   ball is 91,955 states. Before deduplication a width-three depth-three ball
   has at most `1+56+56²+56³=178,809` words; a width-four depth-two ball has at
   most `1+240+240²=57,841`. The candidate loop has an explicit bound equal
   to the checked prefix-ball size times `factors+1`, at most 10,131,881 here.
   The oracle permits exactly these stored-depth limits. Its target generator
   checks at most `5^4` lists, and probes use exactly 1,024 words of length five
   at each of four widths. Compiler and process waits have timeouts.
3. Each native case constructs its bounded factor, ball and query sets before
   its membership stream. The stream uses fixed four-row values and does not
   grow a collection. Python object allocation, standard stream buffers and
   container initialization require the bounded-runtime deviation below.
4. Every Python function is at most 49 physical lines. Native functions are
   below 60 physical lines, including the complete finite-search operation.
5. Executable contracts check role/depth bounds, output completion, factor
   inverses, group products, complete alphabet/state sets, stream counts,
   symmetry coverage, exact endpoints and omissions. Validation remains active
   under optimization. Additional tautological assertions would add no coverage.
6. The only mutable search state is local to one invocation. No checkout,
   external input, Git configuration or predecessor is mutated by replay.
7. CLI output creation refuses existing receipt paths. Source inputs are
   SHA256 checked before compilation. Subprocess and file failures propagate;
   native output streams are checked after writing and closing. Ordinary
   counter/set operations and standard library result ownership were inspected.
8. There is no code generation or dynamic evaluation in the production engine.
   The oracle import is restricted to its package directory. The test-only
   source substitutions below have exactly three fixed bounded targets.
9. Native access is a fixed four-row value, local vectors and full-value hash
   sets. No function pointers or pointer arithmetic appear. Python unittest
   dispatch and temporary-directory callbacks use the framework deviation below.
10. Strict native compiler diagnostics, Python warnings as errors, Ruff checks
    and formatting are required in this contribution's validation. The registered
    hook recompiles with the native diagnostics on every replay. Ruff is a
    recorded local check; it is not installed or enforced by this package hook.

Rule: 3, fixed memory capacity.
Location: `oracle.py`, `verify.py`, `test_package.py`, native initialization/output.
Reason: CPython and the standard containers/streams allocate during execution.
Scope: these finite checks only, with no service or unbounded input stream.
Compensating control: fixed role/depth/factor/probe limits; finite target sets;
only one native stream runs at a time; temporary files and compiler binaries
belong to a scoped external temporary directory. Native membership streams do
not retain candidates. No allocator-independent byte ceiling is claimed.
Verification: complete registered replay, explicit depth guards, exact largest
state counts and clean temporary-directory exit.
Follow-up: a larger role/depth domain requires a new explicit memory budget or
an externally sorted exact engine before its search is admitted.

Rule: 8, restricted metaprogramming, and 9, indirect calls.
Location: `test_package.py` and package-local imports in `verify.py`.
Reason: unittest discovers two fixed methods; behavioral mutation checks compile
three exact text substitutions to exercise actual faults. Python import and
context-manager protocols use runtime dispatch.
Scope: fixed local modules and these test groups only.
Compensating control: each mutation has exactly one matched source location;
compiled faults must be rejected by the independent oracle or native contract.
The fourth-role fault changes only its output row, retaining the first three.
No arbitrary plugin or external module is loaded.
Verification: optimized behavioral command and scoped lint. The wrapper uses
its own resolved package path, so Git-free relocation uses the same modules.
Follow-up: retain a bounded test corpus and direct imports if the package grows;
do not expose the substitution mechanism as a general mutation service.

## Unrun obligations

There is no arbitrary-role multiple-negative theorem, four-role three-negative
exclusion, nonuniform-price optimization, nilpotent alphabet, native caller,
physical invoice, supplier admission, Lean/Docker replay or complete
multiplication theorem. The selected frontier and frozen source files are
unchanged. New TASK metadata uses the donor's required review-status sentence.
