# Paid intermediate meetings

## Scope and source

The source is flyingviper's PR5718, commit
`a1534ac45401c9a9c80c07aa65c89e00e33594f8`. Its conditional exponent is
0.00311024570. The source word has canonical SHA256
`a1c8277189a811546bdc7b147d72e6a594504ff9585c9bf59a5681aa873abb01`.
The retained export includes its full source closure and attribution.

The new word creates intermediate meetings inside paid native queries.
It then applies the independent-helper basis identity from PR5599/5609 at
those meetings. The elementary linear algebra is not a new theorem.
The new contribution is the changed native schedule, its 23 compatible
helper splits, and the complete charged exponent calculation.

## Creating a meeting

Let a public field have a pending native query from frame U to frame V,
with U strictly contained in V. Select an intermediate frame F with
U strictly contained in F strictly contained in V. Replace the query
by U to F followed by F to V. The exact frame maps compose to the old
map, including its phase. The native verifier checks both new maps.

The first part can move earlier across events that do not read or write
this field. The constructor checks that condition against every event
before the old query. Other operations act on different physical fields.
Thus the new partial query commutes with them. This creates a real field
at F; it does not provide a free cross-frame scalar operation.

Several fields can advance to the same F. At that meeting, multiple
independent helper modes can share the added queries. All subdivisions
remain in the program and in the paid histogram.

## Exact helper split

Let A be the scalar prefix at the new meeting and B its suffix. Write
T = BA for the complete scalar map. Owned initialization and erasure
make some internal maps singular; the argument does not invert A or B.
Use a row a and column b supported on fields that are actually at F.
Define c = aA and d = Bb. The constructor checks, over rational numbers,

```text
ab = 1,    cd = 1,    Ad = b.
```

Both c and d use only independent helpers with empty input frame and
full output frame. The complete source acts as identity on their rows
and columns. In particular, cT = c and Td = d. Also, c is zero on main
inputs and d is zero on main outputs. Choose a helper pivot h for which
a_h and d_h are dyadic units.

At the input boundary, use the basis Q given by these ordinary operations:

```text
h -= sum(c_i * i, i != h)
h *= d_h
i += (d_i/d_h) * h, for each i != h in d
```

The identities cd = 1 and d_h != 0 imply Q e_h = d and cQ = e_h^T.
At F, use the basis S given by:

```text
h *= a_h
h += sum(a_i * i, i != h)
i -= b_i * h, for each i != h in b
```

The identities ab = 1 and a_h != 0 imply S b = e_h and
e_h^T S = a. Thus S A Q e_h = e_h and e_h^T S A Q = e_h^T.
The cut coordinate h is exactly the old independent input, and no other
cut coordinate depends on that input. Retire it at F. A new independent
input z takes its place. Apply S inverse with the new label, continue
the original suffix with that label, then apply Q inverse at the full
output frame.

Replacing h at the cut changes the suffix by d times the difference
between z and the old input. Since Q acts only on identity helper
coordinates, it commutes with T. The final Q inverse therefore returns
every old continuing helper to its input and returns the new helper to z.
The retired helper already holds its old input. All main shear endpoints
are unchanged. The exact whole-word checks also verify this conclusion
for every public input and every dirty owned input column.

All coefficients are dyadic. The constructor uses only ADD and dyadic-unit
SCALE for the two bases and their inverses. Every scalar operand must share
its actual frame. Each split shifts every owned label by one; it does not
change the owned allocation, initialization or erasure schedule.

## Concrete construction

PLAN.json gives exact event indices, original MOVE values, cut vectors and
boundary vectors. No solver or finite-field computation is used during replay.
WITNESS.json records the regenerated construction and its canonical digest.

The first 18 meetings each subdivide one query. Their pivots are
731, 706, 713, 724, 725, 730, 728, 722, 714, 720, 719, 718, 727, 729,
723, 712, 715 and 717, in that order. Each adds one independent target.

The next meeting advances fields 115, 179, 192, 455, 557 to frame 105 at cut 14100
of that intermediate word. Five subdivisions support three splits, with
pivots 557, 455, 115. Each split is checked again on the word produced by
its predecessor. The final two meetings each use two subdivisions. They
split pivot 452 at frame 245 and pivot 448 at frame 246.

There are 23 added public inputs and 27 added paid queries. The final word
has 767 public inputs, nine dirty owned labels, eleven owned lifetimes,
peak two owned fields, and 25,843 events. Its canonical SHA256 is
`c3b338bd5b48d916f332a64470a86d2ee5534d8839c9d80b23a7e89bed9742f5`.
Only source catalogue frames occur in this final construction.

## Complete invoice

Let H_r = r^(1-kappa). Relative to PR5718, one complete local call changes
the histograms as follows:

```text
Delta targets = 23 H1 + 23 H8 - 23 H9
Delta paid    = 35 H1 - 5 H2 - 3 H3 + 16 H5 - 16 H6
Delta margin  = 23 H8 - 23 H9 - 12 H1 + 5 H2 + 3 H3 - 16 H5 + 16 H6
```

The paid histogram is
`{1:2219,2:454,3:492,4:92,5:175,6:6,7:15}`.
The helper target histogram is
`{1:25,2:5,4:91,5:6,7:6,8:38,9:388}`.
The local rank mass is unchanged. The full p16/a7 caller has 18 forward
local calls, 15 query shears, every whole idle, and every main target from
the source caller. The full target count is 13,390; the full paid count is
66,834. Its rank-mass surplus remains 760.

The collective changes do not improve every concave tariff. The general
signed-invoice preflight is inconclusive. The full calculation therefore
uses two rational interval engines at the declared exponent. It also
proves a unique raw crossing below the retained BIT cap. RESULT.json gives
that interval, its headroom, both moments and all compiler parameters.

## Ordinary work and compiler

The literal scalar allowance is 224,138. The source local engine is retained
with one declared change: the old public-count range is replaced by the
exact count 767. The bound of fewer than 26,000 operations is unchanged.
Thus the scalar growth allowance 2^(16*26000) still applies. The input
count is finite and is charged in the route and normalizer census.

Every native query, helper normalizer, main adapter, scalar operation,
owned operation and route enters the retained complete cost calculation.
The finite local allowance is below 10^7 and the complete ordinary bound
is below 10^9. The caller construction is compared with its exact retained
CONTROLLER.json, then its physical maps are replayed on the new local word.

The extra targets require new compiler parameters. The cutoff is 16, the
floor is 17, the tail offset is 1/7, and the decay bound is 125/128. The old
cutoff 17 with decay 39/40 fails its completion-tail test. The power 1024,
reserve 10^-12 and 128-step blocks are retained. Since (125/128)^128 < 1/16,
eight blocks still give the required 2^-32 remainder. The complete calculation checks all tail ratios,
the uniform threshold and its predecessor rejection, the actual BIT stock,
54 strict outer inequalities and four functional checks. The published
exponent is below the tested saving and the raw crossing.

## Verification limits

The literal rational checker and dense integer transpose checker use
different implementations. Both are author-side checks. Native equality
includes signed Pauli images and global phase. Actual-word mutations remove
retirement, projection, injection, boundary repair or a paid query, or corrupt
an input boundary, target or owned label. Full-invoice controls remove a
query or invent a target. These must fail in both Python modes.

The five inherited assumptions remain: all-column native behavior, owned
erasure, compiler closure, precision/tape implementation and analytic recovery.
The huge uniform word and complete rounded multiplier are not materialized.
This is a conditional exponent improvement, not a practical multiplication
benchmark, independent human acceptance or a selected-frontier update.

Prepared by Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
