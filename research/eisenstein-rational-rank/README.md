# Faster complete Eisenstein replay with integer rational rank

The complete replay using ywz65's K-rank adapter takes a median
0.436824 seconds with the original Q-rank function and 0.282744 seconds
with this optional rational-rank adapter, a 35.27% reduction in wall time.
This is the first implementation tried; optimization stopped at that gain.
The measured ranges do not overlap. All 209 actual Q calls agree, and the
complete stdout is byte-identical, including the seven original rejection
controls. The 359 K calls keep ywz65's implementation and all 311 F4 calls
keep Jose Manuel's implementation.

Claim type: finite exact equivalence certificate and local performance
measurement. The new result is faster execution of the same complete fixture.
It does not add to or independently review the cited Eisenstein cost theorem.
The adapter, verifier and benchmark were produced by Nick Petalas. Apache-2.0.

## Method and exactness

Clear every row's rational denominators by their positive lcm. For a nonzero
pivot p and an entry a below it, replace the lower row r by p*r-a*pivot_row,
then divide out its nonzero integer content. Multiplication by p is invertible
over Q. The pivot row stays unchanged, so this replacement is an invertible
row operation. Removing integer content also preserves row space. Previously
eliminated columns are zero, and every counted pivot is nonzero. Thus the
returned pivot count is the rational rank. Empty and zero-width matrices have
rank zero. These are standard elimination facts; no new rank theorem is claimed.

The routine copies its input and caches no matrix or mathematical success.
It accepts rectangular lists or tuples containing exact integers or Fractions.
There are at most 96 rows and columns, input numerators and denominators have
at most 128 bits, and every initialized or updated integer row has at most
4096 bits per entry. Capacity exhaustion raises an error. The actual fixture
has dimensions at most 80 by 80 and input heights at most four bits.

[replay.py](replay.py) authenticates all three executable source files by SHA256
and Git blob ID before loading either predecessor module. Both comparison modes
use the same wrapper, imports, source authentication and K adapter. Only Q-rank
changes. No frozen source or production verifier is modified.

## Evidence

[BENCHMARK.json](BENCHMARK.json) is generated evidence with every observation,
execution order, environment, code hashes and ordered Q-call digest. Six pairs
alternate the order of baseline and integer execution, after an excluded warmup
pair. Complete fresh-process wall time includes imports and authentication.

The original-Q mode ranges from 0.428594 to 0.498021 seconds. The integer-Q mode
ranges from 0.278763 to 0.306366 seconds. There are zero failed timed runs.
Every timed run executes all 879 rank calls and compares complete stdout bytes.
Separate timed executions of the 209 actual Q matrices have medians 0.198648
and 0.049803 seconds. The original Q kernel is about 45% of the measured whole
replay, so its reduction explains the complete improvement. These separate
kernel timings do not include matrix capture or the correctness oracle.

Measurements used CPython 3.12.15 on macOS arm64. The host has 18 logical CPUs;
the pre-run load averages were 5.67, 5.15 and 4.01. Other work was running and
was not stopped. Alternation controls drift, but timings remain observations
on this host, not a universal speed guarantee or multiplication speedup.
An untimed cProfile run identified Fraction multiplication/addition in Q-rank
as the main remaining cost after the K adapter.

[verify.py](verify.py) compares every actual Q-call result and checks input
preservation. It compares the complete replay output, checks the original seven
controls are present, and rejects a zero-returning Q adapter through the original
checks. A separate Leibniz-determinant/minor oracle checks 1,798 rational matrices,
including complete small rectangular domains and 200 deterministic 3-by-3
fixtures. Seven invalid-input/capacity controls remain active under `-O`.

[integrity.py](integrity.py) runs both complete modes in a Git-free private copy,
compares their output and all input hashes, and corrupts each of the three live
sources in turn. Each corruption must fail at authentication before import.
The private copies are removed. Default replay writes no artifacts.

## Reproduce

From the repository root, use Python 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -I -O -B research/eisenstein-rational-rank/replay.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -I -B research/eisenstein-rational-rank/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/eisenstein-rational-rank
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/eisenstein-rational-rank --check-source-history
```

Any CPython 3.12 path can replace the displayed interpreter. The standalone
marker is `PASS_EISENSTEIN_RATIONAL_RANK`; integrity prints
`PASS_EISENSTEIN_RATIONAL_INTEGRITY`. The registered commands run normal and
optimized correctness checks and the integrity check, each with a 60-second
limit. Timing is optional and is never a passing threshold:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -I -O -B research/eisenstein-rational-rank/benchmark.py --output /absolute/new/path/benchmark.json
```

The timing destination must be absent and outside the checkout. The default
uses six measured pairs plus one discarded warmup pair.

## Sources and scope

This answers Open next question 2 of ywz65's
[PR2627](https://github.com/CrocSwap/integer-mult-bounds/pull/2627), which supplies
the retained integer-pair K-rank implementation and leaves Q-rank unchanged.
Jose Manuel / jmbarrancoml's
[PR2017](https://github.com/CrocSwap/integer-mult-bounds/pull/2017) supplies the
original complete verifier and mathematical cost-40 proof. Geometry retains
Jonathan Lam / PR798 and Joel Pulikkan / GamingPuzzled / PR620's credit.
Primitive integer-row elimination is classical. All predecessor credit and
source bytes remain unchanged.

[SOURCES.json](SOURCES.json) pins exact inputs and historical provenance at
canonical main `19fdb086ea96af9a9f87936a2b888e10af4ed810`, priority revision 8.
[TASK.json](TASK.json) refines the current replay-runtime card.
The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19220187)
preceded implementation. Live PRs, recent claims, account history and targeted
main/merged searches were checked. Cached overlap covered 324 open PRs and
5,496 Discussions with complete pagination. Sparse local coverage was partial;
targeted main searches supplement it. Unpublished work and arbitrary diffs are
not an exhaustive novelty guarantee.

The retained cost theorem is a cited result, not this contribution's deliverable.
No pairing bound, native word, complete multiplication theorem, new kappa or
selected-frontier change is claimed. Physical access, restoration, precision,
compiler, stock and supplier admission are outside this package. Independent
human and formal proof-kernel review are unclaimed. Lean, Docker and the selected
supplier's cold replay are unrun.

Python and the standard library allocate dynamically, a managed-runtime deviation
from fixed allocation. The stated dimensions and bit capacities bound the rank
routine's live arrays. Verifier fixtures, child counts and 30-second child
process timeouts are explicit; every function is below 60 physical lines.
Dynamic module loading and callback replacement have only the two authenticated
source targets and the local adapter. Warning-strict normal/optimized execution
and the package checks supply diagnostics. No broad shared-code change is made.

## Open next questions

Does the same Q-rank adapter improve another named complete replay with larger
ranks or coefficient heights? Capture that consumer's actual ordered matrix
census and run matched complete fresh-process measurements before proposing
adoption. Its coefficient bounds and full workload remain prerequisites.
No further field optimization or construction expansion is part of this result.
