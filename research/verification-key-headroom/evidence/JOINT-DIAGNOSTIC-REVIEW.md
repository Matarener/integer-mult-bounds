# Joint integer and contribution-key diagnostic: independent source review

Date: 2026-10-28. Final status: SOURCE-ONLY CLEARANCE FOR ONE GUARDED DIAGNOSTIC;
NO CONSTRUCTION OR PERFORMANCE ADMISSION. No source blocker was found in the
final files identified below. This reviewer performed only source reads,
text comparison/reversal and hashes. No scientific import, compiler, numerical
run, benchmark, browser/network/Git action or further hypothesis search was
performed. Only this newly created report is owned by this review.

The proposed action is one fixed, guarded information diagnostic of the unchanged
complete PR5864 workload. It is not a candidate optimization or a new B/C sample.
The previously closed standalone GC route stays closed. A negative optimistic
cost envelope may reject the nominated joint boundary; a positive envelope
cannot establish an achievable saving or admit construction.

## C fragments and assembly

The contribution wrapper preserves the original statements in order: exact
Fraction and index guards, four direct member-slot reads, seven-component key
construction, calls/hits/misses, full dictionary equality, original callback
arguments, result validation, FIFO eviction and insertion. The callback remains
the original PyObject_Vectorcall(s->compute, argv, 5, NULL).

The lookup timer closes once on every visible early error, cache hit or miss.
On a miss it closes before callback depth is incremented and before the Python
callback is invoked. Callback depth is decremented after either a successful or
exceptional callback return. A fresh post-callback timer covers result validation
and FIFO/insertion/cleanup; each error and its success close that timer. Existing
Python exceptions survive these C timing helpers: they use no Python operation
that sets an exception, and preserve errno around clock_gettime. The original
error, refcount and arithmetic order is retained.

Contribution calls made from inside a callback are counted separately and
excluded from eligible timing while callback depth is nonzero. Eligible key
intervals mark nesting and integer activity. Entering an integer interval while
a key interval is active also marks overlap. The completed driver rejects every
nonzero nesting/overlap/error indicator and any unbalanced depth or phase total.

The complete C diff leaves Event.apply, Cache.statistics, cache/event construction
and ownership/GC methods unchanged. Each original F(0), all three ordered score
additions, row update order, counters and the cache statistics API remain intact.
Four separate diagnostic methods are added to the module; no field is added to
Cache.statistics.

prepare_source.py declares three unique C edits and their exact inverse. It
strips only declared timer/marker statements from the replacement contribution
function and requires equality to the original function bytes. An independent
text-only reversal of the three receipt edits produced SHA-256
78ed2e240ee40ce4989a4718e77e8b3967b092d2bf8c900124a26942c98a14cb,
the exact original complete C source hash. An independent directory byte
comparison found only native_cache.c and NATIVE-SOURCE.json different between
the original and diagnostic baseline trees. These source checks do not establish
compilation or runtime correctness.

## Completed driver review

diagnostic.py:35-74 authenticates both original and copied baseline file sets,
each original file's bytes/mode, and every unchanged copy. It permits exactly
native_cache.c and NATIVE-SOURCE.json as declared copy changes, checks their
exact content pins, and reverses the three C edits to the fixed original hash.
The same checks run again after the complete qualifier. Generated __pycache__
files are explicitly outside the file census; original-file and copied-tree
symlink checks remain active. The existing cold loader still snapshots and
compiles its authenticated C source and retains its build receipt.

The integer facade authenticates the archived integer.py source and delegates to
its original Engine. The loaded module and Engine class are retained, and the
driver checks the class identity after qualification. Lines 114-154 place the C
activity marker before both start clocks and remove it only after both end
clocks. Nested finally blocks clear the marker and Python depth on a callee
exception or a clock failure. Incomplete timers cannot pass. The original
function's return is propagated; original callee exceptions are re-raised unless
a diagnostic failure aborts the command. Metadata/classification is outside the
eligible integer union. Expected family counts are exactly 4 ideal, 121
error_trace and 121 reverse_all calls; nested integer intervals are rejected.

Lines 197-217 reject nonzero key/integer/callback depths, clock/protocol errors,
key nesting and integer/key overlap. C integer enter/leave counts must match all
246 observed integer calls. Each key phase requires equal entries/closed/timed
counts, no excluded nested callback interval and nonnegative measured durations.
Lookup hit/miss/error totals partition entries; every miss must have exactly one
post-callback result/cleanup interval partitioned into insertion or error. Thus
the same-run sum is admitted only as a disjoint diagnostic observation.

Lines 220-245 require the exact full.py hash, exactly one namespace seam and
exactly one archived integer-load seam. They execute the transformed original
full qualifier once with native=True. Original actual digest/cache-counter
checks, finite/source/ownership controls, independent Fraction calculation and
complete witness validation are retained. No B arm, repeat loop, alternate
workload argument, GC-cost addition or prior-run addition is introduced.

## Accounting and execution boundary

The key buckets include retained guards, reference management and validation as
well as possible future key-table work. Their raw observed cost is not an
achievable saving. The original Fraction callback, per-item F(0) and score
arithmetic stay outside this nominated key boundary.

Clock reads, diagnostic counters/markers and classification/reporting incur real
cost. Calibration may describe perturbation but cannot be credited as savings.
It runs outside the eligible totals and is not subtracted; the driver verifies
it left diagnostic totals unchanged. The raw instrumented integer plus disjoint
key time is a generous information screen against the fixed wall AND CPU gates.
Instrumentation may perturb costs, so this is no universal runtime bound.

The final report always sets performance_sample, optimization_constructed and
construction_admitted to false. Even HEADROOM_FOR_COST_DESIGN_ONLY leaves
retained integer/key runtime and complete validation/build costs explicitly
UNPRICED_NONZERO. The 0.5-second reserve is provisional, not a measured bill.
Original residual work, new controls, cold compilation/link/load, compiler-child
CPU and independent correctness obligations remain unpaid by a positive screen.

The parent may freeze these exact sources and run the single diagnostic under
the existing serial/resource/shared-budget guard. Execution, runtime preservation
receipts and compilation remain unverified by this reviewer. Every failure must
be retained; this source clearance does not authorize a favorable reroll.

## Frozen review identities

All paths below are relative to joint-cost-screen/. Hashes were read directly
after the worker's readiness signal; no reviewed source file was edited here.

| File | SHA-256 |
| --- | --- |
| diagnostic.py | fb7dd1e71c461754987c7e1af941d8220ec4b17806e0cdec27be977fdc39dfee |
| baseline-public/native_cache.c | 039c2c5fce353cf8be526c14f5f824dbc2b072999accddc310cc575e65e903f3 |
| SOURCE-EDITS.json | 91a10a6e14fb718f2c3cd44a547cb2576fb1dda0a832884a2a5c064e137d81c8 |
| joint_diag.inc | 91e0e716c7ea9ca532991277ddf2535dfb34d00d4a25212ffe192927f6f6ae35 |
| contribution_diagnostic.c | 2e62c74ae8121d806caa7f3d79ab29b8b9390ba2c06896a539ce1213932e38cd |
| prepare_source.py | 92e8ae1370f47c2cf2659a738f3bd561299755c3347be5aa9256fd17a994dd13 |
