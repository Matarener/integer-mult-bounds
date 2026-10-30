# Validation and limits

## Evidence contract

The universal claim is the all-field proof in PROOF.md. The finite scripts check
its equality-pattern reduction and concrete source bindings. They do not prove
that every factorization is optimal or that a physical supplier can execute the
coefficient maps. The selected frontier and frozen predecessor inputs are unchanged.

The primary receipt counts 501,760 original pair-operator entries and 301,056
integral replacement entries, all exact rational equalities. The 40 fixtures
include one, two and three nonzero seed coefficients, opposite halves of one
group, distinct groups, unequal group sizes, noncanonical fractions, negative
row scalings, nonbinary cancellation levels and seed support outside both groups.
The 24 replacement operators preserve each term's source and reader zeros.

The separate implementation uses bit-vector equality assignments and signed
permutation determinants. Its expanded source binding uses explicit nine-bit
coordinates and ordinary binary Gaussian elimination. It checks 24, 432 and
12,000 complete ordered affine triangles over F2, F3 and F5 respectively. Their
old query-zero constraints total 144, 2,592 and 72,000. The all-three-distinct
coordinate equality class first occurs in this check over F5. All 13 patterns
are reached there. The actual P112 expanded identity has 50,176 checked entries.

Controls exercise invalid dimensions, singular bases, collinear points, bad
binary rank rows/capacities, overlapping or nonbinary indicators, three distinct
nonbinary cancellation values on each half, outside-support noise deletion,
reader zero preservation, zero-cost unused readers, and seed-coefficient case
admission. Five actual optimized CLI corruptions change the expected receipt,
source blob pin, declared source path, retained certificate bytes and live label
bytes. Each fails with its expected diagnostic. Restoring every original byte
restores a successful CLI run. Both success and failure controls run without
assert-dependent checks.

## Reproduction environment and checks

Registered replay uses CPython 3.12.15. Direct optimized replay also uses
CPython 3.15.0. The package has no third-party runtime dependency.

```sh
python3.12 -I -Werror -B scripts/research_package.py --package research/p112-unrestricted-three-query
python3 -I -O -Werror -B research/p112-unrestricted-three-query/verify.py
python3 -I -O -Werror -B research/p112-unrestricted-three-query/independent.py
python3 -I -O -Werror -B research/p112-unrestricted-three-query/test_controls.py
ruff check --no-cache --select E,F,B,UP,SIM,C4,PIE,RSE,RUF research/p112-unrestricted-three-query
ruff format --check research/p112-unrestricted-three-query
python3 -B scripts/check_research_commit.py --package research/p112-unrestricted-three-query --check-source-history
```

Ruff version 0.17.1 is a validation tool, not a replay dependency. The source
history check covers the declared canonical provenance pins. Pending predecessor
proofs are bibliographic references, not executable imports or required Git
ancestors. The retained PR3370 certificate bytes are authenticated locally;
the separate original-head byte comparison is recorded in the publication receipt.
The actual committed Git-free export is replayed with normal and optimized
Python, with source/input hashes compared before and after. The official export
transport checker is distinct from mathematical replay. Hosted CI, independent
human review, a formal proof kernel and the selected full cold replay are not
claimed. The isolated package does not change the selected construction.

## Code bounds and principle decisions

Build the Lever produced the rerunnable support replacement and separate finite
check. Prove It Works requires actual operators, real CLI corruptions and a
committed-byte export. Separate Before Serializing Shared State gives this
worker exclusive ownership and short advisory locks for shared Git and task
reservations. No extra agent, thread, clone or worktree was created.

Power of Ten inspection covers these three new scripts. Control flow is iterative,
with no recursive call graph. The primary check has 16 formal coordinate-partition
pairs, at most 24 grid assignments per pair, and 40 fixed 112-port fixtures.
Every rank calculation has at most 224 rows and columns. The separate field
inventory is exactly {2,3,5}, hence at most 12,000 ordered triangles for one
field and 25 points. Source reads enforce 1 MiB or 32 KiB limits. Local algebra
sizes are fixed at three. The control suite creates four bounded source/input
copies and runs six CLI processes sequentially, each with a 30-second timeout.
The registered commands have explicit timeouts. All new functions fit within
60 physical lines after formatting.

Meaningful runtime invariants use explicit ValueError checks and remain active
under optimization. Parsing and authentication happen before source geometry is
used. No shared code, configuration, frozen input or predecessor file changes.
Resource ownership is scoped with file and temporary-directory context managers.
CLI return codes and diagnostics are checked. The module-loading dispatch in
the tests has one fixed package-local target, loaded without a cache write.
No dynamic code generation or evaluation is used.

Rule 3 deviation, managed runtime allocation. Python integers, fractions, lists
and JSON allocate dynamically; a steady-state allocation ban cannot be enforced
by this runtime. Scope is only these bounded offline checks. Read limits, fixed
port/field inventories, fixed test copies, sequential subprocesses and context
managed cleanup bound live resources. Larger inputs require a new capacity
review. No interpreter, shared runtime, source symlink or inode alias has its
mode changed.

Rule 9 deviation, standard-library test and import dispatch. unittest invokes a
fixed six-method test class; importlib loads the single fixed verify.py target.
The test runner and import API require this dispatch. No input selects a module
or callback. All six methods and the actual CLI success/failure paths execute.
A future removal of unittest/importlib must preserve those behavioral checks.

Rule 10 scope. The registered replay enables isolation, warnings as errors and
optimized controls. Ruff checks the listed diagnostics on every validation run.
It is recorded here rather than imposed on unrelated historical research code.
No separate Python static type checker is configured for this standard-library
package. A future shared library would need its own typed API and recurring
analysis configuration.
