# Validation and limits

The scientific base is canonical main
`6f100d4bb5083f8c35d96fd95a539811c62f245c`, priority revision 6.
All declared inputs are available at that base. SOURCES.json binds exact
Git blobs and SHA256 bytes. No pending predecessor commit is required.

## Checks on the real artifact

The registered Python 3.12 replay runs these three commands, with the
package path expanded by scripts/research_package.py:

```sh
python3 -I -O -Werror -B research/q8-inverse-uniform-tariff/verify.py
python3 -I -O -Werror -B research/q8-inverse-uniform-tariff/independent.py
python3 -I -O -Werror -B research/q8-inverse-uniform-tariff/test_package.py
```

The primary replay recomputes RESULT.json, including every source-bound
predecessor pair minimum and each new deterministic receipt field. It
checks all 512 Q8 associativity triples and all 64 products under each
binary character. Across 580 target lists, every price pair in
{0,1,2,3,4}^2 attains the theorem's bill. There are 14,500 cases total.
The lists contain all 64 pairs, all 512 triples and four eight-role cases.
Twenty single omissions reject, five hypothesis controls distinguish
changed contracts, and six invalid domain requests fail under optimization.
The complete 36-factor rank-one alphabet at two roles includes nilpotents.
All 46,656 three-call words and all 4,980 factors at one through five roles
satisfy every checked quotient, coefficient-support and Sylvester identity.
This is not a minimum-word search or an all-role enumeration.

The code-disjoint Hamilton quaternion engine imports no primary or
predecessor code. Its full regular action is faithful on F2[Q8]. It checks
26,904 dirty-input columns across all pair/triple upper bounds, both central
recipes and seven longer words touching active and spectator dirt. All 112
single omissions from those longer words reject. Its separate receipt is
INDEPENDENT.json. The behavioral tests compare the two engines on every
dirty basis column of 168 further generic words at two through eight roles.
They also inject actual wrong endpoint, tariff and regular-action producers.

Three behavioral groups pass. The actual CLI succeeds in a Git-free export
with unchanged file inventory and hashes, rejects changed and missing live
sources, rejects an altered minimum receipt and preserves occupied outputs.
Temporary exports use an owned external TMPDIR. No source file is chmodded,
and no interpreter, symlink or shared runtime mode is changed.

The written proof was reviewed locally for the exact dual-number ring
homomorphisms, order of noncommuting group products, full coefficient
support, dimensions and pairing of X,Y, scalar normalization, nilpotent
invertibility, zero prices and coordinate attainment. This is author review.
No extra reviewer, agent, human approval or proof-kernel acceptance is claimed.

## Engineering decisions

Build the Lever produced model.py, verify.py and the separately implemented
regular-action replay. Prove It Works required full dirty endpoints, actual
faulty producers and committed-byte/source-history checks. Boundary Discipline
keeps domain validation in endpoint's input boundary and byte/size checks at
source and receipt reads. Separate Before Serializing Shared State kept the
package and output directory worker-owned; shared Git mutations and the task
reservation use the campaign's process-held advisory locks.

The Power of Ten inspection covers all four new Python paths and their
registered entry points. There is no direct or indirect recursion. Word input
is bounded by eight roles and 48 calls; group coefficients use eight bits.
Each function is at most 46 physical lines after formatting. Explicit
ValueError contracts remain active under -O. Internal rank inputs come only
from bounded validated words and eight-role coefficient matrices. File
handles use context managers; subprocess statuses are checked, each test
child has a 120-second timeout, and temporary directories release on success
or failure. SOURCE rows are capped at eight, manifests at 64,000 bytes, live
sources at 4,000,000 bytes, and result receipts at 100,000 bytes. All remaining
loops range over these bounds or fixed domains stated above.

Rule 3 deviation, managed allocation. Python allocates integers, tuples and
JSON values during execution. The verifier streams one word or fixture at a
time, retains no complete candidate history, limits live matrices to eight
roles and source input to the bounds above. The 36-factor tuple and 580-target
fixture collection are fixed. Failure paths and full-domain replays exercise
these bounds. A fixed-capacity native rewrite is only warranted if a future
caller needs allocation-free execution; no such runtime claim is made here.

Rules 8 and 9 deviation, module loading and test injection. Isolated scripts
load a fixed set of one or three package modules through import_module after
adding their own resolved directory. Targets are explicit names and no code
is generated or evaluated. unittest fault controls temporarily replace three
known functions and restore them via scoped contexts. Normal replay has no
runtime registration or callback dispatch. Optimized relocated execution and
actual injected failures check these boundaries. Static normal imports would
require a different standalone isolated-export entry contract.

Diagnostics use Ruff 0.17.1, Python target 3.12, with E,F,I,B,UP,SIM,RUF,C4,
PIE,PERF,PTH,RET and formatting checks, without suppressions. All scientific
commands run with warnings as errors; no compiler is involved. The registered
hook preserves that warning policy for future replays. Interpreter version,
exact local commands, outputs and publication checks are retained in the
session evidence and final report.

## Unrun obligations

The universal conclusion follows from PROOF.md, not extrapolation from finite
fixtures. No full selected cold replay, native supplier admission, physical
caller/routing/control invoice, recursive moment, all-size multiplication
transfer, Lean, independent human review or hosted-CI acceptance is claimed.
Positive-only signed tariffs and four independently priced labels remain
open. Source retention and a passing package hook are not scientific admission.
