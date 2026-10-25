# Verification contract and implementation inspection

The scientific command checks explicit quotient models and the inherited
finite old-field premises. The all-field contraction and graph theorems
are author-written in PROOF.md and use the retained PR3583 obstruction.
No finite test is described as human or proof-kernel acceptance.

## Bounded implementation

The committed entry points are verify.py and test_controls.py. Both use
only CPython's standard library. All scientific failure checks use
explicit exceptions and remain active with optimization. The controls
execute the actual optimized verifier, check its exit and intended error,
then restore exact bytes before the next fault. A corrupted projection is
a code mutation, not just a malformed certificate. A false receipt is
also rejected. The original attempted disconnected-branch fault removed
an edge with a valid chord bypass, so the verifier correctly accepted it.
The corrected fault inserts an actually disconnected unused vertex into
a branch set. The failed original diagnostics are retained in the session
receipts rather than counted as passing controls.

The following ten-rule inspection shaped the two new Python files:

1. Control flow is structured, with no recursive application calls.
   TemporaryDirectory owns the complete copied package on success or
   failure. The standard library's directory cleanup is not reimplemented.
2. Each JSON file is bounded by 1 MB. There are at most 16 cases, 20
   vertices of length at most 32, 40 edges and five branch sets. Successful
   branch validation bounds their combined size by 20. Each forest grows
   at most that many vertices. Rank matrices have at most 64 rows and 24
   columns. Subset enumeration has exactly 512 iterations, two marks and
   three fields. Control subprocesses have 120-second timeouts. Package
   copying is limited to 64 filesystem entries. Invalid JSON shapes fail
   closed, sometimes through standard Python type/index exceptions.
3. CPython and Fraction allocate dynamically. Direct compliance with a
   no-allocation steady state is unavailable in this managed runtime.
   Scope: these finite offline verification commands only. The input,
   graph and rank bounds above cap live collections; each predicate stream
   has 3,072 rows and is discarded after its digest. Integer elimination
   normalizes every resulting row by its gcd. Matrix entries originate
   from 0,+1,-1 graph coordinates. Integer bit lengths are not instrumented.
   A conservative recurrence for the largest absolute entry is
   B_next <= 2*B_current^2 before gcd normalization, for at most 24 pivots.
   JSON parsing and standard-library internal allocations are not
   instrumented. Follow-up: use fixed buffers in a native checker if this
   finite contract ever becomes an online or unbounded service.
4. Functions fit within 60 physical lines after repository formatting.
   Certificate validation, geometry, projection and predicate comparison
   have separate responsibilities. No forwarding abstraction was added.
5. Explicit contracts check graph ownership, root placement, disjointness,
   branch connectivity, links, kernel inclusion/dimension, independent
   quotient marks, exact projected queries and every predicate pair.
   Retained source hashes and exact field-independent premise identities
   are checked before graph verification. These contracts remain enabled
   under -O; they replace assertions for this verifier.
6. The only module state is the immutable package root and six target
   endpoint pairs. Mutable geometry, forest and row state are local.
   Controls write only their owned temporary package.
7. Every scientific comparison is consumed by an explicit contract.
   Subprocess return codes and expected diagnostics are checked. Byte-copy
   writes are checked for completeness. File errors propagate and fail
   verification. There is no discarded scientific status or background
   child. Print/write_text results for small local reports use Python's
   normal all-or-exception contract.
8. There is no eval, dynamic source generation or runtime registration in
   science. Controls deliberately mutate one fixed source literal to
   verify that a wrong projection is detected, then restore its bytes.
9. Data access has explicit local dictionaries, lists and tuples. The
   controls use six bounded local mutation callbacks, a managed-language
   deviation from forbidding indirect calls. Targets are the six listed
   JSON edits only, with no external callback or retained capability.
   Verification is their actual CLI rejection at the intended boundary.
   Follow-up: replace callbacks by explicit tagged mutations if the
   control alphabet becomes externally supplied.
10. Repository Ruff checks and formatting checks cover both new files.
    The only initial lint finding was an implicit subprocess check policy;
    the call now explicitly uses check=False because negative controls
    inspect nonzero exit statuses. CPython warning-as-error, optimized
    scientific/control commands and the registered package runner are the
    runtime diagnostics. No warning is suppressed. No static type checker
    is configured for this package, and no repository-wide configuration
    changes are introduced.

## Source and export coverage

ORIGINS.json describes the three used pending predecessor files as actual
proof and certificate inputs. Their retained bytes are SHA256-bound and
available inside this package. SOURCES.json records the canonical task
and selected-record provenance. No replay requires the pending source
commit to be in a foreign Git object cache. The existing frozen packages
are unchanged.

Publication verification runs the metadata/pin checker and committed-byte
checker with source history at the actual final HEAD, then the registered
CPython 3.12 commands. A committed package export is integrity-checked,
copied into a Git-free owned directory using exclusive regular byte
writes with distinct inodes, and both scientific/control commands are
executed there. The export manifest and before/after source/export hashes
are retained in the session report. Runtime bytes, inode and modes are
measured before and after; none is changed by this work. No copy2,
metadata copying or chmod is used for export or cleanup.

Hosted CI, independent human/formal acceptance, tariff optimality, graph
classification, physical execution, supplier admission and the full
multiplication theorem remain outside these checks. No broad historical
or selected-frontier reproduction is required by this isolated package.
