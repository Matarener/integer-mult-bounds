# Static inverse tables remove 1,661,435 repeated tuple searches

This contribution was produced by Nick Petalas. Apache-2.0.

The complete radical-fanout command performs **260 `tuple.index` calls instead
of 1,661,695**, with byte-identical complete output. The change precomputes
additive inverses and unit inverses once per immutable finite ring. It retains
every demand, word, literal input, arithmetic check, control and shortest-path
query in lee-phys's [PR6210](https://github.com/CrocSwap/integer-mult-bounds/pull/6210).

Claim type: an exact implementation-work reduction with a scoped equivalence
argument and finite conformance evidence. This is a verifier-engineering
contribution, not a new mathematical tariff, an audit of the predecessor theorem,
a supplier admission or a new kappa. Wall time is reported separately below.

## Implementation and equivalence

[retained_source.py](retained_source.py) is the exact published verifier at
`4e08457f4d0b69c00a6ca62eca81c8d0a55f3e60`. [UPSTREAM.json](UPSTREAM.json)
records its original path, Git blob, SHA256 and author, together with the exact
source README. The pending commit is not required in the local Git object store.
All executable bytes required for replay are retained here. [SOURCES.json](SOURCES.json)
pins only canonical-ancestor task and selected-record provenance.

[fast.py](fast.py) authenticates the retained executable before importing it.
Its only replacement is the `Ring` class used by the retained ring factory.
The new frozen subclass adds two tuples and overrides `neg` and `inv`.
The source's full `main`, constructors, scalar interpreter, checks, Dijkstra
search and output statements execute unchanged.

For a valid ring table, the cached entry at x is exactly the original
`add[x].index(0)` or `mul[x].index(one)`. The tuples cannot become stale because
the original operation tables and the new tables are immutable. A fresh ring
builds fresh tables. There is no persisted answer or workload cache.
For a nonunit, the sentinel sends execution through the original failing
lookup, preserving its `ValueError` and message. Python negative indices and
out-of-range indices also preserve their original behavior.

It follows by induction over scalar instructions that every intermediate state,
gate coefficient and endpoint is unchanged. The search's neighbor states, costs,
heap ties and returned paths are unchanged too. No case is replaced by a cached
verdict. Constructor table scans are included in the full command and in the
260-call count. Construction also adds one membership test per ring element;
the count above is specifically `tuple.index` invocations, not every table read.

The executable accepts ring orders 1 through 81. The theorem's supplied fixtures
have orders 16, 81 and 64, and its nonlocal rejection fixture has order four.
The adapter adds at most 162 tuple entries per ring. Successful inverse queries
and all negations then use constant-time tuple indexing instead of a row search.
The explicit nonunit failure path retains its row search.

## Evidence

The new checker compares every element at both its nonnegative and negative
Python index in all three rings, 322 element/index cases. It also checks the
out-of-range exception type and message, rejects invalid orders and nonsquare
tables, and rejects changed executable source before import. Sixteen controls
run under normal and optimized Python.

Two fresh complete commands have equal stdout. Separate untimed profiles run
both complete workloads again and count exactly 1,661,695 and 260 tuple searches.
All four outputs agree, with SHA256
`6fcd968e3899b567f520b5b05bde6c481dd7581a754026af2aa300bf6396da1d`.
The generated receipt is printed to stdout and binds the actual local package
hashes. No receipt is handwritten or stored as an expected scientific answer.

The preserved source output enumerates 22,152 demands, 221,520 words,
1,772,160 formal forward/inverse evaluations, 1,310,720 literal evaluations,
four oracle queries and 8,465 settled entries. These are the predecessor's
workload and counters, not new mathematical findings claimed here.

## Wall-time measurement

The benchmark times fresh complete scientific commands, including imports,
table initialization, every check and the four shortest-path searches. It
compares every complete stdout and fails on a nonzero exit or stderr. Profiling
is separate from the reported timing sweep. The generic package runner and
export tools are outside the measured boundary.

The wall-time comparison is **inconclusive on this shared host**. Ten alternating
pairs have zero errors and equal complete output. The optimized median is lower,
but the ranges overlap and the difference is smaller than run-to-run variation.
No portable elapsed-time improvement is claimed.

| Complete command | Median seconds | Range seconds |
| --- | ---: | ---: |
| Retained source | 3.555522 | 3.155300 to 3.913315 |
| Inverse-table adapter | 3.256747 | 3.027612 to 3.633472 |

Raw alternating pairs, in seconds, are:

| Pair | Retained | Adapter |
| ---: | ---: | ---: |
| 1 | 3.762916 | 3.384731 |
| 2 | 3.551804 | 3.531334 |
| 3 | 3.913315 | 3.633472 |
| 4 | 3.899865 | 3.448595 |
| 5 | 3.621823 | 3.143365 |
| 6 | 3.559239 | 3.291734 |
| 7 | 3.329549 | 3.221761 |
| 8 | 3.421450 | 3.030692 |
| 9 | 3.202639 | 3.033553 |
| 10 | 3.155300 | 3.027612 |

Environment: CPython 3.12.15, macOS 27.0.1 arm64, 18 logical CPUs. The final
load averages were 4.43, 4.00 and 3.12. Other research processes shared the host;
the measured commands themselves ran serially. Both engines used identical
warning-strict flags and fresh private bytecode namespaces. The adapter digest
was `a556f916c57b6fb25d1cbcb54abbaf92d1cc32dc96e4c5fc886b461328e31f32`.

The separate baseline profile records 0.238 seconds of tuple-index self-time
within 6.546 profiled seconds. Endpoint interpretation, count bookkeeping and
shortest-path expansion remain substantial work. Tracing changes the timing
distribution, so this profile explains the limited scope of the optimization
rather than establishing an untraced speed bound. The exact lookup-count
reduction is the result being shipped; timing does not certify a faster multiplier.

## Reproduce

From the repository root, with CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/radical-fanout-inverse-tables/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -O -B research/radical-fanout-inverse-tables/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/radical-fanout-inverse-tables
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/radical-fanout-inverse-tables --check-source-history
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/radical-fanout-inverse-tables/benchmark.py --rounds 10
```

Another CPython 3.12 path may replace the displayed interpreter. Set
`IMB_RUN_ROOT` to an existing private scratch directory to collect all temporary
files there; otherwise the system temporary directory is used. Direct replay
needs no Git, network, foreign commit or
third-party package. Child interpreters use fresh private bytecode namespaces
and `-B`; all temporary directories are removed. The optional benchmark prints
all raw samples, complete-output digests, environment and summary statistics.
CI registers conformance, not a host-specific runtime threshold.

## Limits and engineering choices

This changes only an isolated optional replay. It does not patch the predecessor
package, shared runner or selected result. The predecessor mathematics remains
a cited result with its own review obligations. No selected scientific cold
replay, physical/native/compiler/stock/precision/outer proof, Lean or Docker run
is claimed. All five selected framework assumptions remain. Independent human
and formal proof-kernel review are unclaimed.

New functions fit within sixty lines. The new table loops are bounded by 81;
conformance uses three fixed rings; timing accepts five through ten rounds;
each child has a 120-second timeout. The retained source already has explicit
search resource guards and is unchanged. Its long functions and search loops
are retained dependencies, not newly refactored code. Managed Python allocation
is a documented deviation from fixed-allocation guidance. New table capacity
is bounded as above. The four inverse-method targets in the conformance helper
and the single explicit ring-factory replacement are bounded uses of dispatch.
Warning-strict normal and optimized execution are registered. No external linter
or proof assistant is required. Local compilation is checked without writing
bytecode files.

Build the Lever led to the rerunnable checker and benchmark. Prove It Works led
to complete-command equality, actual profile counts and the corrupt-source
control. Explain the Number keeps the wall-time uncertainty separate from the
exact lookup reduction. The engineering-mode playbook is Autonomous local run.

## Open next questions

Does this table adapter produce a stable complete wall-time gain on an idle
Linux CPython 3.12 host? Run five or more alternating complete commands with
`benchmark.py`, retain all output digests, and report medians and ranges. The
workload is supplied; an additional host measurement is missing. A source-level
factory hook could later integrate the adapter without altering the mathematical
workload, but no integration or additional optimization is reserved here.

## Credit and overlap

The new inverse-table adapter, equivalence explanation, checker and measurement
script were produced by Nick Petalas. The radical-triple theorem, complete
enumerated workload, interpreter and search are lee-phys's. Retain the source's
credit to #5259/#5514, Ali Romman #5266/#5310, lee-phys #5139/#5163, Nick Petalas
#5208/#4916, Krzysztof Wojt #5045, Ross Richardson #3063/#3121, Cinna Davis,
Anthony, Oscar Fennell, Tekalign and the retained lineage. The two retained
source files preserve their original credit verbatim.

The scientific base is canonical main
`a5bff3bf133e482541c09eba4e773884bdb2b1b7`, priority revision 8. The selected
binding-only orientation passed and resolves to PR6030 at kappa .003125804;
the older value in current-priority prose is not used as the selected value.
The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19279673)
reserves this optimization. Live open and account PRs, active Discussions,
recent handoffs, local locks, merged term searches and main README searches
found no matching optimization in their stated coverage. The overlap helper
covered 338 open PRs and 5,957 Discussion records with complete remote pagination,
but only 91 of 8,623 local note records. Separate Git README searches cover the
omitted main files for the distinctive terms; neither search proves novelty.
