# Skip settled columns in encoded Gaussian inverse setup

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: scoped semantics/resource proof with exact finite corroboration.
The exact positive-pivot inverse of Jose Manuel's
[PR3851](https://github.com/CrocSwap/integer-mult-bounds/pull/3851)
can omit reads of its completed identity columns. At pivot k, with m_k
nonzero off-diagonal elimination factors, the exact saving is

```text
sum k(1+m_k) matrix reads,
between n(n-1)/2 and n^2(n-1)/2, both sharp.
```

The candidate performs identical rational arithmetic and matrix writes,
returns identical encoded output and preserves the positive-pivot numerical
domain. It requires additional scratch. [PROOF.md](PROOF.md) gives the
all-dimension invariant, sharp examples and resource boundary. No new kappa
or selected-frontier change is claimed.

For the literal physical 4-by-4 matrix `4I+J`, where J is all ones:

| Measured complete finite workload | Retained inverse | Candidate |
| --- | ---: | ---: |
| Matrix reads during inversion | 236 | 212 |
| Matrix writes during inversion | 80 | 80 |
| Pooled tape reads | 947301 | 922401 |
| Pooled tape writes | 187399 | 182739 |
| Pooled unit head moves | 869032 | 846336 |
| Peak pool leases | 34 | 36 |

The pooled counters include input construction, output decoding and final
cleanup. They include the suffix iterator's extra scratch operations. They
are finite record-tape counters, not a complete machine instruction count
or recursive supplier invoice. A pool sized only for the original peak
need not suffice. The first checked improvement is shipped without further
optimization.

## Evidence and reproduction

The new checker executes ten paired physical fixtures, checks every output
against a separate rational trace and both inverse products, and confirms
the exact read reduction and unchanged writes. Eight executions reject
nonsquare, singular, zero-pivot and negative-pivot inputs with the same
messages and cleanup. Another 81 rational matrices corroborate the identity
invariant. All checks use explicit exceptions and survive optimized Python.
The inversion itself runs under sealed constructors and a host-decoding ban.

From the repository root, with CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/gaussian-inverse-settled-columns/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/gaussian-inverse-settled-columns/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/gaussian-inverse-settled-columns
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/gaussian-inverse-settled-columns --check-source-history --check-modes
```

Other hosts may substitute their CPython 3.12 path. The direct checker writes
no files and prints a generated receipt bound to every package file. It
authenticates all five live inputs before importing the retained physical
runtime. An official package export includes those inputs and supports a
Git-free replay; full history is needed only for the repository provenance
checks. No predecessor scientific verifier is imported or replayed.

## Cold runtime limit

Run the separate benchmark with

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/gaussian-inverse-settled-columns/benchmark.py --pairs 9
```

Nine alternating fresh-process pairs on macOS arm64, CPython 3.12.15,
give medians 0.928621375 seconds retained and 0.922816875 seconds candidate.
Their ranges are 0.917676334 to 1.030556625 seconds and 0.909664875 to
0.998733333 seconds. All eighteen complete output byte strings agree and
there are zero errors. This comparison is inconclusive: the median gap is
smaller than the observed variation. No wall-time speedup is claimed.

The timed region includes authentication, nested export extraction, imports,
fixture construction, inversion, literal output checking and cleanup. A
separate profile of the same 4-by-4 workload places the retained inversion
at 0.703 of 1.532 profiled seconds; `Matrix.get` accounts for 0.189 seconds. Authentication and
extraction dominate this tiny cold workload. The host has eighteen logical
CPUs, and other processes were active. Alternating sides limits drift but
does not remove contention. Neither side uses result caching or a changed
fixture. Timing is not a CI acceptance threshold.

## Open next questions

The structured questions and blockers are in [TASK.json](TASK.json).

1. Can one exact streamed row update reduce complete tape work without
   increasing peak scratch? First specify every borrowed record, scan and
   cleanup operation. No such primitive or cost proof is supplied here.
2. Does this inverse improve a complete reached Gaussian preparation?
   First compare an actual preparation page, its full output bytes,
   ownership and pooled meters. Production pages and a full caller
   benchmark were not run.

## Credit, scope and implementation limits

Jose Manuel / jmbarrancoml retains PR3851's physical Gaussian setup,
positive-pivot rational inverse, encoded tape operations and word-product
lineage. Chafik Boukhalfa, RaD/hipotures, Mason Hale, Dugongue and the
retained arithmetic, Gaussian and multiplication contributors retain their
source credit. Existing files and attribution are unchanged. Gauss-Jordan
elimination and its identity-column argument are classical; the new result
is their checked physical read-count refinement in this exact implementation.

The canonical base is `a5bff3bf133e482541c09eba4e773884bdb2b1b7`, priority
revision 8. The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19279747)
and [TASK.json](TASK.json) record the original question and bounded overlap
coverage. Direct live PR/Discussion and main-tree searches supplement the
helper's incomplete sparse local coverage. Unpublished work and arbitrary
historical code diffs are outside that search.

The source Gaussian theorem is cited rather than audited. Native all-column,
numerical Gaussian admission, production preparation, precision/tape/stock,
complete caller and all five selected framework assumptions remain open.
No selected scientific cold replay, Lean or Docker run was performed.
Independent human and formal proof-kernel review are unclaimed.

Power of Ten inspection covers the five new Python files. Functions are
under sixty lines; numerical loops are bounded by matrix dimension and
fixtures by width four. The 81-matrix host domain and at most fifteen
benchmark pairs are explicit. Subprocesses have sixty-second timeouts.
Source files are capped at 128 MiB and the manifest at 64 KiB and sixteen
rows. Recursion and runtime code generation are absent from new code.
Managed Python allocation is a rule-3 deviation; inherited tape buffers
also allocate dynamically, so no fixed-storage implementation is claimed.
The two engine choices, source loader, fixture constructor and temporary
instrumentation are bounded indirect calls, a rule-9 deviation. Strict
warnings and normal/optimized replays are the available local diagnostics.
