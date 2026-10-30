# Bulk rational arithmetic: static design and bounded prototype

Status: source-only review and prototype, 2026-10-27. No compiler invocation,
module import of this prototype, numerical execution, timing, browser action,
or remote action was performed by this reviewer. The parent owns the sole
serial execution slot and any qualification. Kappa, Work 1/2 mathematics,
feeds and automations remain paused. Synced sources were not modified.

The narrow row-batch mechanism is technically plausible, but **this nomination
has no credible complete-performance headroom under the required unchanged
literal Python Fraction oracle**. Restoring that oracle costs more in the
retained observation than the entire PR5864 trace this mechanism could remove,
even with zero cost for the new candidate. Finite qualification can establish a
reusable scoped prototype and negative screen; it does not authorize an actual
word audit or a complete rational benchmark in this round.

## Evidence and source boundaries

The read-only design inputs were the workspace AGENTS.md, current
VERIFICATION-PERFORMANCE-WORKING-PLAN.md, and
outputs/c-native-opportunities-20261027/OPPORTUNITIES.json. The implementation
was inspected in the frozen package
outputs/fraction-native-cache-20261027/SEALED/research/fraction-native-qualification,
including native_cache.c, fraction_table.py, native_backend.py, slot_binding.py,
entry_parent.py, compact_parent.py, full.py, finite.py, actual_audit.py and
PROOF.md. The literal reference was inspected at
outputs/c-native-opportunities-20261027/source/reference_precision.py.
The instrumented census was read as existing diagnostic evidence, never run.
The upstream predecessor index and old conversations were not read.

The authoritative public PR5864 pin is
3f15c943e4ad6479f03e674c80fff1269a16ccfe. The parent reports the authenticated
public archive SHA256 as
7b142567acacac5182045bf8daa8780e916661c2cf343dbf81b13c88ead85d64 and the extracted
163-file baseline as outputs/c-verification-all-opportunities-20261027/baseline-public.
That authentication is the parent's evidence; this reviewer did not repeat it.
The local owned C fork starts from the scientifically identical frozen C file.

The runtime binding initially supports the inspected Linux CPython 3.12 source
/usr/lib/python3.12/fractions.py, SHA256
cf33568f7b767f66896995a7a81cc662e8be226f2e58efb61d2028f64eb5d231. This is a deliberate
narrow source pin. Another supported Python patch build needs its own inspected
binding/qualification; it must not silently broaden this pin.

## Hotspot selected

PR5864 native_cache.c:event_apply already batches the sparse row loop, but
executes three PyNumber_InPlaceAdd calls on Fractions for every coefficient.
Its actual trace has 2,579,750 contribution calls. Consequently those three score
lanes account for 7,739,250 Fraction addition sites in that trace. The census
records 13,144,283 Fraction._add calls over the complete profiled qualification,
which also includes other paths and finite tests. These quantities identify a
mechanism; they are not an unprofiled time estimate.

The selected change keeps each score as an owned numerator/denominator pair of
arbitrary-width Python integers for one ADD/COPY event. It performs the same
ordered lane updates, then materializes the three exact built-in Fractions
before the unchanged outer Python code performs rounded injection, pair capture,
stream serialization, peak comparison and witness copying. The reference records
prefix observations at event boundaries, not after every coefficient. The finite
probe additionally compares every coefficient prefix to expose arithmetic errors.

The contribution cache, callback on every miss, exact seven-field keys, complete
FIFO order/counters, original source-site indexing, row iteration and row writes
are unchanged. In particular the per-coefficient F(0) construction is retained.
This nomination does not revive the failed direct-add dispatch or constructor
elision nomination.

## Concrete source-only interface

Owned files are under outputs/c-verification-all-opportunities-20261027/rational/:

- native_bulk.c: an owned fork of native_cache.c adding
  event.apply_rational(dst, src, scores, authenticated_math_gcd).
  The original Event.apply, Cache API, module name _fraction_native and all
  inherited controls remain present.
- bulk_fragment.c.txt: the added kernel retained separately for easy review.
- arithmetic_binding.py: source/runtime qualification of bypassed Fraction
  operations, fallback closures, owned descriptors, inherited in-place protocol,
  attribute setters, finalizer absence and builtin gcd; freshness is checked
  before each selected trace.
- bulk_backend.py: a separate derive/install wrapper. It authenticates the same
  source seam and preserves the predecessor route for unsupported or changed
  domains. It does not patch the literal reference or construct a complete
  replacement qualification.
- finite_probe.py: source for bounded finite checks and optional fixed BCCB micro
  diagnostic. It does not execute the actual word.

The parent may stage native_bulk.c as native_cache.c in its owned baseline copy,
update the staged NATIVE-SOURCE.json hash, and invoke finite_probe.py with the
staged package path. native_backend.load supplies the existing cold compilation,
source authentication and load receipt. The probe accepts an optional --micro;
its samples are illustrative kernel observations only. They exclude cold build
from the inner micro interval, so the outer receipt remains necessary.

No source was imported or compiled by this reviewer. These files are not claimed
to pass even their finite harness until the parent runs and records it. A first
write to the copied C file failed because its copied mode was readonly; only the
new owned copy's user-write bit was added, then the source edit completed. This
was a static file-write failure, not a numerical or compiler failure.

## Rational representation and proof obligations

The prototype deliberately implements **general normalized rational pairs**, not
only dyadics. entry_parent.certified_domain accepts arbitrary exact Fraction
weights, and permitted string scalars can contain odd denominators. For example,
1/3 and -5/7 are valid error_trace scalars. The ideal verifier's separate dyadic
constraint does not justify narrowing the public error-trace API or its controls.

For normalized a=n/d and b=m/e, the kernel computes g=gcd(d,e). If g=1, the
result is (n*e+d*m)/(d*e). Otherwise it computes s=d/g, t=n*(e/g)+m*s,
g2=gcd(t,g), and returns (t/g2)/(s*(e/g2)). An equal-denominator branch computes
(n+m)/d and reduces by gcd(n+m,d). Denominators stay positive and zero reduces
to 0/1. All products, sums, divisions and comparisons use Python integer C API
operations on exact PyLong values; C machine words hold only checked indices
and inherited counters. No int64 approximation, private PyLong digit access,
floating point, machine-word rational denominator or silently truncated exponent
is introduced. Arithmetic order remains coefficient order, with score lanes
0, 1, 2 updated in that order.

Only the score accumulators use pairs; all cache values and sparse coefficients
remain exact Fraction objects. At each event boundary the kernel allocates an
exact Fraction object and writes its normalized integer slots through the
already authenticated owned member descriptors. This is a new construction
obligation, not justified merely by equal numeric values. Output tree types,
positive canonical denominators, zero representation and signed serialization
must all be checked. Live changes to the original arithmetic or factory select
the predecessor rather than silently bypassing the changed operation.

A future dyadic specialization could retain (n,k) for n/2^k and align integer
numerators, reducing only at event boundaries. Because denominators are powers
of two, the event denominator can remain the largest encountered power, rather
than a product. This could avoid much gcd work. It requires an explicit proven
dyadic eligibility condition, arbitrary-width numerator handling, bounded
exponent conversion, a general fallback, and exact materialization at every
observed prefix. It is deferred here: it does not remove the oracle-restoration
bill, and no second mechanism or favorable micro sample justifies construction.

## Literal oracle independence and complete-cost stop

Retaining exact Fraction output types is not retaining an independent literal
Fraction oracle. The new kernel replaces the additions that PR5864 deliberately
left to Python Fraction. Its output cannot validate itself through another call
to the same new C arithmetic. The independent integer engine is useful additional
cross-checking, but does not meet an explicit requirement for an untouched
literal Python Fraction oracle by itself.

The admissible strict design for this nomination therefore has three separately
executed paths: untouched literal Fraction, unchanged integer, and new rational
candidate. Mutable inputs, caches, answers and PASS receipts cannot be shared
between those paths. Restoring the literal Fraction error trace is a new full
control cost and belongs in every claimed complete candidate command. An offline
comparison, prior digest, cached expected result or a benchmark B sample cannot
be relabeled as a free live oracle in C.

The frozen retained observation is:
outputs/fraction-native-cache-20261027/SEALED/research/fraction-native-qualification/
evidence/runtime/runs/actual-native-apply/stdout.txt.
Its original raw outer receipt is beside it as receipt.json and usage.json.
The producing source is actual_audit.py. It reports 25,984 events, 799 coordinates,
identical complete output digest
954c7448ff74d78753828e9623ad44c46da9e5ce459420b6e50a5d47294250b9,
and these historical, same-audit component observations:

| Component | Wall seconds | CPU seconds |
| --- | ---: | ---: |
| Untouched original Fraction error trace | 20.534678025986068 | 20.523067174 |
| PR5864 native apply, including cold build | 11.886980237992248 | 11.883082538000005 |

Grant the rational candidate zero runtime, zero cold build, zero new checks and
zero conversion cost. The most optimistic replacement saving from these retained
components is still:

- wall: 11.886980237992248 - 20.534678025986068 = **-8.647697787993820 s**;
- CPU: 11.883082538000005 - 20.523067174 = **-8.639984635999995 s**.

The negative signs mean an added cost. The cold build included in the removed
component makes this screen especially generous to the new candidate. Positive
candidate runtime and required new checks only worsen this historical scenario.
The new 15% complete target requires about 4.915695 seconds wall saving from the
recorded PR5864 median 32.771297 seconds, and 4.911 seconds CPU from 32.74 seconds.
The zero-cost candidate screen is already adverse before seeking that target.

These are source-pinned historical observations, not fresh measurements, not a
measured lower bound on all future machines, not a sum of profiler cumulative
times, and not a universal impossibility result. They are sufficient to reject
credible headroom for this exact additive restoration design in the current
bounded round. No new actual-word or complete rational run is recommended.
A different ownership/algorithm boundary would require its own explicit contract
and cost screen; calling an optimized path "literal" would not create headroom.

## Complete added validation bill

Any later proposal that changes the design enough to reopen the gate must pay
all of the following; none is a deferred free service:

1. Preserve all 118 adopted native/predecessor controls, four custody controls,
   27 observation controls, the original 120-program differential, six semantic
   rejections, three integer rejections, source guards and every original output.
2. Add native rational arithmetic checks covering odd denominators, equal and
   coprime denominator branches, negative values, complete cancellation, zero,
   large numerators/denominators, repeated hits, FIFO wrap and every counter.
3. Check exact built-in output types and canonical slots at each coefficient
   prefix in bounded fixtures and every event prefix; compare full signed
   witnesses, tie-breaking, Pareto order, scores, hashes and inputs unchanged.
4. Add arithmetic-source, code-object, closure, defaults, builtin/global,
   getter/descriptor and inherited-protocol drift controls, with a pure fallback
   decision. Noncanonical manually mutated Fraction slots must not enter the
   normalized-pair assumptions. General non-dyadic canonical Fractions must work.
5. Preserve low-level memory safety: strong references, partial initialization,
   allocation/error cleanup, original dict iterator mutation errors, score-list
   mutation detection, safe callback/reentry handling and no repair of mutated
   caller data. Retain all legacy generic callback controls on Event.apply.
6. Independently execute the literal Fraction oracle in the complete command,
   compare all 25,984 events/799 coordinates and full output materialization,
   retain the unchanged integer path, and charge this new oracle cost.
7. Charge source/runtime binding, input qualification, conversions, per-event
   materialization, native bookkeeping, cold compile/link/load, compiler-child
   CPU and peak process-group RSS. Only immutable loaded code may be reused
   inside a process; never reuse mutable answers or receipts across backends.
8. Complete normal/-O, readonly Git-free replay, source bytes/modes, committed
   inventory, metadata/source pins, final-head CI and publication/handoff checks
   if and only if a complete positive screen actually reopens construction.

The finite probe deliberately addresses a bounded subset: 165 coefficient
prefix comparisons (five scalar choices, 33 prefixes each), 13 complete event
prefix comparisons, source/fallback controls, generic non-dyadic arithmetic,
mutation checks and a fixed optional BCCB micro. It does not assert that this is
the complete added validation union or discharge item 6.

## Static safety limits and next decision

Event.apply_rational is a source-qualified packet interface. Arbitrary callbacks
can observe intermediate score-list values under the old Event.apply API;
batching intentionally delays those values until the event boundary. The new
method therefore does not claim arbitrary callback observational equivalence.
The wrapper admits only the authenticated pure callback, and the legacy method
retains its original public callback behavior and tests. New direct hostile
callback probes test safe rejection/cleanup, not a broader semantic theorem.

Scores and source entries are held strongly across callback activity. Score-list
size and identities are checked after the callback and before publishing. Source
iteration retains the original Python items iterator. A failure attempts to
publish completed exact score updates only when the caller list still has its
original identity contents; it never resizes or repairs a mutated list. Allocation
failure during this recovery is not claimed to preserve the exact allocator-level
partial state of the original sequence; the original exception is retained.
Successful stable-input execution is the arithmetic equivalence domain. Full OOM
fault-injection/lifetime review remains an added construction obligation if the
scope reopens.

The initial binder is deliberately source-pinned and conservative; a rejection
is a fallback, not an excuse to relax it. Live runtime/input mutation during a
trace remains excluded by the inherited stable-input/runtime premise, while
explicit low-level mutation checks continue to protect memory safety. This is
ordinary CPython 3.12 with the GIL, not abi3, free-threaded or subinterpreter support.

The parent's chosen next step is finite qualification plus the fixed micro only,
if useful as a scoped negative artifact. Every failure and correction must remain.
No actual-word audit or full rational qualification follows merely because the
micro improves. The result to publish, if finite qualification succeeds, is a
reusable exact batching prototype and an explicit oracle-cost engineering stop,
with no new complete speedup or global-optimality claim.

## Parent-run bounded v1 receipt

After this source-only implementation, the parent executed its frozen
stages/rational-v1/run_finite.py in the serial guard. I inspected the retained
stdout and receipt at outputs/c-verification-all-opportunities-20261027/runtime/
runs/rational-finite-micro-v1/. They record exit 0, no stderr, unchanged staged
source bytes/modes, 178 comparisons and 19 added named controls. Outer wall was
1.3062437750049867 seconds; recorded user+system CPU was 1.24 seconds; sampled
process-group RSS was 79,007,744 bytes. The extended C source SHA256 is
4a4949e36cff4ff2894dd1f9379b58a58346ec7c888903271d4b98bbe4cfc7ae.

The single fixed BCCB micro retained all four samples:

| Sample | Wall seconds | CPU seconds |
| --- | ---: | ---: |
| B1 | 0.06855765299405903 | 0.06854380399999993 |
| C1 | 0.06020033897948451 | 0.060203247000000015 |
| C2 | 0.04673448100220412 | 0.046702148000000054 |
| B2 | 0.07398301700595766 | 0.073957787 |

Each sample has 16,384 contribution calls, 16,352 hits and 32 misses, with no
FIFO eviction. This deliberately small repeated fixture is not an actual-word
cost model. It excludes cold compilation from its inner interval and does not
include a complete restored literal oracle. The smaller first-pair gross micro
improvement cannot overcome the separately identified oracle cost. No actual
word or complete rational replay was performed.

The reviewer subsequently made conservative binding-only source edits for an
exact expected Fraction MRO, finalizer absence/freshness, and predecessor factory
identity. Those final Python bytes must be matched to the parent's frozen stage
before extending the v1 pass to them. The current owned sources are:

- arithmetic_binding.py SHA256
  2115d639fac0262352a3091cc1fcce2c9aefd892992b92e5740ffd173330fdbd;
- bulk_backend.py SHA256
  9b440bd3d921bb06ff5035cb8ae85053f3e0b6880b6ec37d364b55da012449ca;
- finite_probe.py SHA256
  362bcd2bc967ed223ed303835048d1c51697f0293cfc83cffd4a9e02e2efcccd.

The C source is unchanged from the passed v1 receipt. A final finite-only replay
of changed Python binding bytes is appropriate; another micro sequence is not
needed to preserve the negative engineering decision.
