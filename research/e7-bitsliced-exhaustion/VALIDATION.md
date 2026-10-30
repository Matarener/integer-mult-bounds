# Validation and limits

Base: canonical main df0137efd35e11b4445734bf612bdd4c7ebc330c, priority 7,
selected conditional kappa 0.00310045. The current source-binding baseline
passes. It does not constitute a selected cold replay.

The consumed classifier is PR5669 at
700efb538a3d919409c9506d117846b7895b02ea. All ten original files are retained
byte for byte. SOURCE-ORIGIN.json maps their original paths and hashes.
SOURCES.json binds these files and that map to retention commit
1b853397390a537a3d63ed22976f8cc699743619.

## Scientific checks

Python 3.12.14 passes the complete new verifier. It covers 34,525 comparisons
across every independent unordered generator set in F2^4, all weight bounds
and five batch sizes; 108 wide-code comparisons; 13 malformed inputs and
three changed-input/bound controls; the full original scientific receipt; and
a second full E7 basis. The original source also passes unchanged on
Python 3.14.7. No skipped source check or runtime function replacement occurs.

The syntax comparison confirms that the derived classifier changes only its
source-root expression and minimum-support function. Every downstream check
and every source-receipt field remains active. RESULT.json records the exact
normal result and support digest.

## Complete replay timing

BENCHMARK.json records six serial fresh Python 3.12.14 processes, in the
order old,new,new,old,old,new. All use -I -B. Each process runs the complete
classification and verifies its fixed receipt. All six stdout hashes match,
and all stderr streams are empty.

The old times are 15.090499, 13.816090, 13.724912 seconds. The new times are
0.788342, 0.887017, 0.723674 seconds. The median ratio is 17.525510662.
These are local macOS arm64 measurements. They compare the same complete
scientific replay, not the extra generic-code conformance suite. They do
not establish a universal hardware ratio or a multiplication speedup.

## Remaining limits

This checkout is shallow. Full-history publication preflight is unavailable;
exact source bytes and immediate retained-source ancestry are checked.
No selected cold replay, all-history suite, native/outer supplier admission,
Lean build, independent human review or proof-kernel acceptance is claimed.
No physical word or invoice changes, so no new kappa follows.

The shared current-main CI navigation defect has existing repair PRs 5659
and 5703. Hosted checks must be reported separately from local checks.

## Registered replay

The registered Python 3.12.14 command passes all declared checks and ends
with PASS_REGISTERED_RESEARCH_PACKAGE. The normal result equals RESULT.json.
The complete source classification is unchanged. No locally declared command
is omitted.

## Isolated export and final overlap

The official committed-byte and export checks pass for all 23 package files
at scientific commit 5c5aa5674885a81b11d301bd393481843ff3c266.
The exported package passes Python 3.12.14 with -I -O -B, no Git directory,
an empty executable PATH and read-only files. All 24 exported files retain
their bytes and permissions. An actual changed source input is rejected
before the full replay; its bytes are restored before that replay.

The final remote refresh covers 404 open PRs and 5,072 Discussion records
at 2026-10-26T14:30:44Z. All 7,676 main package notes are searched. A separate
recent-body scan finds no competing E7 bit-lane optimization. The live source
head is still the consumed commit. Canonical main remains unchanged. Closed
unretained and unpublished work are outside this coverage.

The final evidence commit changes documentation and coordination metadata
only. Scientific code and source inputs are unchanged from the isolated run.
