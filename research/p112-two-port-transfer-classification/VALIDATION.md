# Verification scope

The finite scientific checks use CPython 3.12.15 and the standard library.
Rational ranks use exact fractions in verify.py and integer minors in
independent.py. GF4 ranks use Gaussian elimination in the former and the
complete dual-functional space in the latter. Neither implementation imports
the other. The ordered predicate stream is committed in RESULT.json.

The checked conclusions are twenty-nine coherent constructions, thirty star
constructions, all 3,312 compared subsets, 2,060 source and 2,736 reader
premises, the thirteen exact predicates used by the impossibility proof,
and the exceptional star's minimal-reader/maximal-source lists. Both programs
also reconstruct the thirteen successes of the predecessor fixed maps. These
are exact finite results. The proof that coherent transfer covers arbitrary
finite graphs and the impossibility over every characteristic-two field are
written arguments in PROOF.md, rather than exhaustive graph/field searches.

Both optimized checker CLIs reject six faults each: a zeroed coherent query,
a deleted exceptional hub coefficient, missing case coverage, the wrong field
polynomial, a changed expected premise count, and changed live source bytes.
Fourteen initial/restored CLI positives pass. Each control uses exclusive
owned regular copies with source/destination inode disjointness, and checks
that originals retain their hashes. Failure checks use ValueError and remain
enabled under `-O`. No assertions enforce acceptance.

## Publication checks and replay

The bounded registered suite is:

```sh
python3.12 -W error -B scripts/research_package.py --package research/p112-two-port-transfer-classification --check-only
TMPDIR=/your/private/tmp python3.12 -W error -B scripts/research_package.py --package research/p112-two-port-transfer-classification
python3.12 -W error -B scripts/check_research_commit.py --package research/p112-two-port-transfer-classification --check-source-history
```

The publication procedure runs these on the actual committed HEAD, then
exports that exact commit with scripts/export_research_package.py and checks
the export. It runs all three scientific/control scripts on the Git-free
committed bytes, including `-W error -O -B`. Publication receipts bind each
actual argv, HEAD, environment, stdout, stderr and exit independently. They
also preserve source/export hashes before and after replay, the official
export manifest, runtime identity, owned regular-file checks and distinct
copy inodes. Earlier exploratory or pre-commit passes do not substitute for
those final checks. The source-history check covers the canonical source
pins; comparison-only pending PRs are not required Git objects.

Focused Ruff E4,E7,E9,F,B,UP,SIM,I and formatter checks apply to the three new
Python scripts. New source files remain in this package; frozen predecessors
and the selected frontier are unchanged. The first card orientation failed
because a source was omitted by sparse checkout. Materializing those immutable
sources made the exact card command pass. That diagnostic and the first
unused-variable lint failure are retained with their corrections in the
external decision trail.

## Power of Ten inspection

The programs have no recursion, dynamic evaluation or background work. The
primary loops over thirty cases and at most 64 query subsets with four
source/reader checks each. Matrices have at most eight columns and dimension
four. The independent implementation checks minors of order at most four,
at most 24 determinant permutations, and at most 256 GF4 functionals. Its
memoization caches have explicit capacities 16,384 and 2,048. The six control
faults run two checkers with a sixty-second timeout each, then their positives.
Source fixtures have a 65,536-byte limit. JSON structure, field entries,
exact ordered case coverage and fixed marks are validated at the boundary.
Every checker failure propagates through the actual CLI. Resources in the
controls have scoped owners and automatic temporary-directory cleanup.

Python, arbitrary-precision integers, JSON and the standard library allocate
during checks. This is a managed-runtime deviation from fixed allocation;
live state is bounded by the fixed thirty-case fixture, dimension, subset,
file-size and cache limits. Standard-library internal allocation is not
instrumented. Python decorators are limited to those two bounded pure-function
caches. No C pointers or function-pointer APIs are introduced. After normal
formatting, calculate spans 65 lines in the primary and 62 in the second
implementation. Each owns one ordered result-table pass, counts and digest.
This is a small documented deviation from the approximate sixty-line ceiling;
no forwarding layer is added to divide that invariant. Exact measurements are
retained in the external inspection receipt.

Build the Lever shaped the deterministic table and two rerunnable checkers.
Prove It Works requires actual committed-byte and Git-free replay. No extra
agents, threads, checkouts or clones are used.

## Limits

Independent human and formal proof-kernel review are unclaimed. Hosted CI is
separate from the recorded local replay. The exceptional result excludes
coherent boundary maps; arbitrary graph-dependent transfers there remain
unresolved. No other marked-pair/scaling classification, full odd-characteristic
extension, larger/repeated interface theorem, masked-identity result, cheaper
literal operator, physical acquisition/coefficient/frame/restoration/hosting,
precision or stock proof, compiler/all-size admission, complete supplier,
kappa improvement or multiplication theorem is established. No unrelated
historical replay or selected-frontier cold suite is run.
