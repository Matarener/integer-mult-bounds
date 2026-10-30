# Equivalence of the incidence substitution

This scoped implementation argument is produced by Nick Petalas. The P104
facts, root model, original assertions and bounded verification domain are
Matarener's PR6188. This argument concerns the new implementation, not an
independent proof of those mathematical facts.

Let the ordered port labels be P=(p_0,...,p_(n-1)). For each nonzero binary
section label z, define an integer

    Z_z = sum_i 2^i [popcount(p_i & z) is even].

The summands have distinct bit positions. Consequently bit i of Z_z is one
if and only if the old ldot(p_i,z) equals zero. The old single-section count
is therefore popcount(Z_z), and its two-section count is
popcount(Z_z & Z_y). Integer AND has no cross-coordinate carries. Python's
unbounded nonnegative integers compute these identities exactly.

The implementation constructs Z_z for every z=1,...,511 and retains the
original maximum over all z and every z<y. There are still 130,305 pairs.
It does not identify planes modulo basis changes or discard equivalent pairs.
The only reuse is the incidence of a fixed port with a fixed section.
All maxima, including empty port sets in the test interface, are over the
same nonempty sets of section labels.

The source-bound adapter replaces only the S0 count computation. It retains
the original definitions used later, the original S0 log and assertions, and
every S1/S2' line. Adding a raw prefix to the initial docstring preserves its
literal unrecognised backslash-H escape and removes its compilation warning.
No executable statement changes for that spelling adjustment. Both engines
make that same docstring adjustment. For the enclosing verifier, the only
substitution selects the new span command at its original subprocess site.
All other subprocesses, log authentication, assertions, result comparisons,
controls and Lean-source checks execute unchanged. The inherited FULL mode is
removed from the comparison environment so the command has the bounded
contract. Neither engine runs the historical full census or a Lean build.

Every live input is checked against its pinned SHA256 before compilation.
The adapter accepts only this pinned source version; no claim of compatibility
with future edits is made. A changed source needs a new pin and a new adapter
review. Child commands always run without optimization. This preserves every
predecessor assertion even when the new conformance driver runs under -O.
The replay adapter rejects direct optimized invocation rather than silently
dropping assertions.

The conformance checker independently computes each parity as a sum of bit
products, checks every represented coordinate and every actual two-section
intersection, and compares the complete scalar and bitset outputs for both
commands. Only the leading elapsed-time field is normalized. Counts, witness
summaries, PASS markers and all remaining text must match exactly. Checks use
explicit exceptions and remain active under optimization.

# Resource and diagnostic scope

The new incidence API admits widths 2..9 and at most 512 distinct labels.
It stores at most 511 nonnegative 512-bit masks. Each capacity computation
visits at most 130,305 pairs. The fixed conformance domains are 281 port sets,
including all subsets at widths two and three, eight width-four fixtures,
and the actual 104-port input. Each child has a 180-second timeout. The
source inventory is bounded to 256 rows, each file to 16 MiB; files are read
one at a time. Functions are below 60 lines. No new recursion or retry loop
is introduced.

Python allocates managed objects during execution. This is a Power of Ten
rule 3 deviation, bounded by the fixed domains above; runtime/library
allocation is not independently instrumented. Executing the source-bound
adapter is a rule 8 deviation: both substitution sites are fixed, all input
bytes are authenticated, and the comparator exercises the retained complete
commands. The predecessor's own control flow and libraries remain inherited
and unmodified. The purpose is a bounded replay improvement, not a rewrite
of the older implementation under new coding rules.

Warning-strict normal and optimized conformance are registered. The retained
span docstring is the sole source spelling adjustment; no diagnostic is
suppressed. The benchmark uses five alternating fresh-process pairs per
scope, counts failed commands as errors, consumes and compares the complete
output within each run, and includes source authentication and startup in
its timed region. Its output contains the interpreter, numpy version,
platform, processor count, load, raw samples and implementation hashes.
Performance percentages are local measurements, not portable guarantees.

# Descriptive timing comparison

STATISTICS.json is generated from the saved BENCHMARK.json and binds its SHA256.
For each scope put U=sum(a>b for a in scalar for b in bitset). Enumerate every
five-element subset of the ten measurements as a possible scalar allocation.
For each allocation recompute U, and count abs(2U-25) at least as large as the
observed value. The complete domain has binomial(10,5)=252 allocations. The
span command has U=25 with two tail allocations; the complete verifier has
U=23 with eight. All five paired differences in each scope are positive.
These exact calculations describe the supplied small sample. Independence
from host load or a speed guarantee on another host is not proved. Registered
conformance validates the main timing record; the descriptive calculation is
separately recorded for inspection and is not a new runtime benchmark.
