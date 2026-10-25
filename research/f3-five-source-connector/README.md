# Exact unsigned F3 five-source connector optimum

This package proves an exact **108 complete-call optimum** for five immutable
sources and all 31 nonzero binary-mask outputs over F3. Every one of the 36
operators is used exactly three times. Consequently, for any independently
positive fixed complete-call prices, the exact map-call bill is

```text
3 sum_(j=0..4) c_Bj + 3 sum_(m=1..31) c_Am.
```

This is a scoped proof with an explicit finite certificate. It answers the
five-source open question in [#4189](https://github.com/CrocSwap/integer-mult-bounds/pull/4189),
at head `5fb3936dfc8082f438f21c72dd6ca49ff4366ae7`. It is a new batch construction,
not an independent recheck of that contribution's six-call one-source result.
There is no new kappa or selected-frontier change.

## Exact boundary

All 37 length-L rows are arbitrary and distinct: five read-only sources x_j,
31 output rows y_m, and one borrowed dirty connector z. For arbitrary F3-linear
maps B_j and A_m of compatible dimension, implement

```text
y_m += sum_(j: bit_j(m)=1) A_m B_j x_j,    m = 1,...,31;
x_j and z unchanged.
```

The only operations are unsigned complete calls
`B_j: z += B_j x_j` and `A_m: y_m += A_m z`. Source and coefficient rows are
immutable. Each call preserves other rows, restores its private scratch and
heads, and has action independent of its old target. Data rows are excluded
from private scratch. Outputs are unobserved until completion.
No signed call, direct product, connector scaling, extra connector, mutable
source, frame change, free copy or overwrite is admitted. The maps may be
singular and need not commute. The theorem is uniform in L and these maps,
within this abstract complete-call contract.

The characteristic-two prefix-difference construction in Ross Richardson's
[#943](../universal-connector-boundary/README.md) has a different field and
cost. Its 74-call number is not an F3 lower bound. Sagar Thakrar's
[#1349](https://github.com/CrocSwap/integer-mult-bounds/pull/1349) allows signed
calls and studies a three-by-three signed target, a different interface.

## Lower bound over every finite legal word

Specialize to scalar identity maps and keep the five source scalars and the
initial connector scalar z0 independent. If B_j occurs b_j times, the final
coefficient of x_j in z is b_j modulo three. Restoration forces `3 | b_j`.
If A_m occurs a_m times, the coefficient of z0 added to y_m is a_m modulo
three, since B calls never change that coefficient of z. Removing connector
dirt forces `3 | a_m`.

Each A_m must occur at least once because its requested row is nonzero. Each
B_j must occur at least once because the singleton output for j depends on
x_j, and B_j is the only operation that can transmit x_j to an output.
Thus every one of the 36 counts is at least three. Every legal generic word
has at least 108 calls, and its positive fixed-price bill is at least the
displayed formula. This argument does not impose a word-length search cap.

## Attaining word and triple-prefix identity

Project a word onto its B events. Let q_t be the five source-call counts,
modulo three, after t such events. At that boundary,

```text
z = z0 + sum_j q_t[j] B_j x_j.
```

Three A_m calls at boundaries a,b,c therefore add
`A_m(3 z0 + sum_j (q_a[j]+q_b[j]+q_c[j]) B_j x_j)`.
This is the requested row exactly when that prefix sum equals the binary
coefficient vector of m in F3^5. Boundaries may repeat; multiple unsigned
readouts at one boundary are legal. Distinct output calls commute because
they preserve z and have distinct targets. No commutation of A_m with B_j
is used.

The source path is

```text
B0 B4 B4 B0 B0 B1 B3 B2 B2 B1 B3 B3 B4 B2 B1.
```

It uses every B_j three times, so q_15=0. The certificate lists a triple for
each of the 31 masks. For example, mask 1 uses boundaries `(0,0,1)`, and mask
31 uses `(0,3,8)`. Here
`q_3=(1,0,0,0,2)` and `q_8=(0,1,1,1,2)`, whose sum is `(1,1,1,1,1)` modulo
three. The verifier enumerates all 816 triples with repetition from the 16
boundaries and independently regenerates the lexicographically first triple
for each requested mask. It then regenerates and checks the literal 108-call
word in [CERTIFICATE.json](CERTIFICATE.json). This finite list completes the
upper-bound proof. It is not an exhaustive census of source paths.

Reversing the literal word, keeping every call unsigned, implements the
inverse in another 108 calls. At the reverse occurrence of a readout that
formerly saw q_t, the connector now sees -q_t, because the full source path
has total zero. Each output still has three readouts, so its connector dirt
cancels and its source increment is negated. The connector restores. No
two-call implementation of an individual inverse is charged or assumed.

## Complete tariff and remaining costs

The lower bound is attained coordinate by coordinate, so it holds for every
independently positive fixed price, without choosing a different schedule.
Unit prices give 108. Source prices `(1,4,10,16,28)` and readout prices 1 give
270. Those are abstract complete-call bills in F3, not physical runtime
comparisons to a characteristic-two implementation.

Let I pay input admission and layout, P_F pay reusable coefficient preparation,
and D_W pay instruction storage, reads, dispatch and schedule construction for
this literal word. A conditional completed caller upper bound is

```text
I + sum_F P_F + D_W + 3 sum_j c_Bj(L) + 3 sum_m c_Am(L).
```

Each c_F must already include its actual source/coefficient access, arithmetic,
target update, private scratch restoration, head returns and entry/exit
frames. Only z is shared borrowed scratch at the root. Primitive private
scratch remains additional and excludes all 37 data rows. The fixed table
has 108 instruction records; it is not an unpaid scheduling oracle.
The fixed-price theorem optimizes the map-call sum. Word-dependent I, P_F
or D_W can change a physical optimum and are not set to zero.

The exact call counts and algebra are **proved**. The displayed total is a
**constructive conditional upper bound** once complete primitives and their
layout are supplied. A selected-supplier consumer, physical primitive prices,
frame/owner admission, coefficient access and precision/outer-transfer
obligations are **unknown here**. This side result closes a local interface
question; it does not justify a supplier implementation campaign.

## Verification and source binding

From the repository root, using the supplied interpreter:

```sh
~/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/f3-five-source-connector/verify.py
~/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/f3-five-source-connector
~/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/f3-five-source-connector --check-source-history
```

Both registered commands run with warnings as errors, once normally and once
with `-O`. Checks use explicit exceptions and remain active in optimized
Python. Expected marker: `PASS_F3_FIVE_SOURCE_CONNECTOR calls=108 masks=31`.
The verifier prints a generated receipt bound to all six package files and
the live predecessor README. It does not write files or hand-author a receipt.
SOURCES.json also pins the original card and selected record as provenance.
No executable or unmerged Git dependency from #4189 is imported.

The generic coefficient checker treats `A_m z0` and `A_m B_j x_j` separately.
A separate dense implementation checks all 222 input basis vectors and nine
mixed dirty vectors across L=1,2,3, including singular and noncommuting maps.
That gives 462 forward/reverse comparisons and 462 two-direction roundtrips.
Eight semantic controls cover a missing source, a missing readout, changed
source ports, changed output ports, a readout moved across a nonzero prefix,
the wrong inverse direction, and reversed matrix-factor order at L=2,3.
These finite checks support the written proof; they are not a proof-kernel
certificate or a complete multiplication theorem.

The card's unchanged #943 positive control passed with 945 pairings,
maximum coverage 31, 74 queries and 182 leaves. Selected baseline bindings
also passed after the sparse checkout was widened to the declared input
directories. The selected cold replay, physical/native replay and proof-kernel
build were not run for this isolated interface result.

The verifier has no recursion, dynamic evaluation or subprocesses. All loops
are bounded by the fixed 15-event path, 816 triples, 108-event word, 36 maps
or L<=3 dense fixtures. No function exceeds 60 lines. Python necessarily
allocates objects during computation, a Power of Ten rule 3 deviation limited
to this bounded offline check. The fixture list has at most 114 states of
111 scalars each, plus a fixed number of comparison states. Every file read
has a 128 KiB cap. The 30-second registered
timeouts and normal/optimized warning checks are compensating controls.
Reassess storage if parameterized searches are ever added. Python has no
compile-time pointer/macro checks; direct calls and shallow list operations
are the inspected equivalents for rules 8 and 9.

## Open next questions

The structured questions are in [TASK.json](TASK.json).

1. Does this same 108-call lower bound admit a schedule at a concrete caller
   with immutable sources and unobserved outputs? First identify that caller
   and price all 36 complete primitives plus admission and dispatch. A cheaper
   recursive invoice is blocked by the missing physical consumer, not by
   another search for this already optimal abstract word.
2. For all 242 nonzero ternary coefficient rows on the same five sources,
   can one 15-event path supply three readouts per output? That would test the
   boundary of count-floor attainment beyond binary demand. First inspect the
   triple-prefix coverage of this path, then decide whether that demand has a
   useful consumer. No exhaustive search or answer for that different family
   is claimed here.

## Credit

This contribution was produced by Nick Petalas. It retains Ross Richardson's
#943/#934 prefix-connector lineage, ywz65's five-source contract map, Sagar
Thakrar's distinct signed-F3 comparison in #1349, and Riquelme Soares's #4189 unsigned-F3
one-source result and explicit batch handoff. No predecessor credit line or
frozen package is changed. Independent human and formal proof-kernel review
are unclaimed. Apache-2.0.
