# Encoded minimum root prefix at the complete caller

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.

This package implements the minimum-prefix construction of PR5688 on the
retained physical Count interface. The numeric minimum and its production
witnesses belong to that predecessor. The new result is an encoded search,
a complete RootPlan adapter, and completed reduced RootLayer executions.
There is no new complete kappa bound.

## Domain and exact search

Fix integers 1<=r<m<=73, F>1, and T>=m. The three borrowed input Counts
encode M>=1, K>=1 and T. They start in canonical form at their first digit.
The fixed constants m,r,F belong to the compiled construction. Define

```text
D(w)=0 if w<T; otherwise D(w)=1+D(r floor(w/m)),
S(q)=F^D(M-q), R(q)=2^(Kq), P(q)=ceil(R(q)/S(q)) S(q).
```

The retained PREFIX-PROOF.md proves that P(q)<2R(q) is equivalent to
floor(log2 S(q))<=Kq. It proves monotonicity and the feasible upper bound
U=min(M-1,ceil(cD(M)/K)), where c=ceil(log2 F). These statements hold also
when R(q)<S(q)<2R(q). This package uses them without a stronger rounding
condition.

`reached_profile` keeps a Count for the current width. After i iterations,
it contains the i-fold maximum child width; the other two Counts contain
i and F^i. The width strictly decreases at every iteration. The loop stops
exactly when the current width is below T. It returns D(w) and F^D(w).

`floor_log2` scans the stock digits, increments an encoded digit count,
and subtracts one. The stock is positive, so this subtraction is defined.
The only host bit-length operation in planner.py is `(F-1).bit_length()`.
F is fixed at construction. No input-dependent Count is decoded.

The search maintains a closed interval [lower,upper] that contains the
least feasible q. Initially lower=0 and upper=U. It computes the encoded
floor midpoint, evaluates the exact predicate, and replaces the appropriate
endpoint. If the midpoint fails, monotonicity excludes every value below
or equal to it. If it succeeds, the minimum is no larger. The interval
strictly decreases until its endpoints agree. The final profile is computed
at that q. Thus the output is the least prefix in the specified complete-row
format for every valid input. Exhaustive finite tests are separate evidence.

## Root interface

`MinimumRootPlan` inherits the source constructor, all 29 named roles,
`count`, `clear`, and the 256-tape scratch pool. Its production parameter law
is unchanged: d=floor(p^(997/1000)), K=floor(d^(1/500)),
G=4 ceil(log2 p)+6, H=dG and delta=d*2^guard_exponent. The default guard
exponent remains 210000. The selected width, residue, coefficient and row
domains remain the source domains.

It keeps qF=ceil(2H/K) and qB=ceil(H/K). For M=n-qF-qB>0 it computes
T=max(m,ceil(d^(1/1000))), then saves the encoded minimum q0, exact depth
and stock. For M<=0 it uses the direct branch. Every dependent field uses
the source formula, including Q0, the two row counts, row_bits, core_width,
core_front and core_back. Unused direct-branch depth is zero. Source address,
guard, row-divisibility and zero-row endpoint arguments are retained from
PR5688 and the physical controller; they are not new native proofs here.

The existing RootLayer constructor accepts a plan. This is the sole
integration point. This package changes no retained execution body and
adds no runtime patch. The root applies the actual phase sweeps, reserved
leaves, row padding, recursive Machine, normalization and truncation. The
non-power fixture has q0=2, depth=1, stock=6, four original rows and six
padded rows. It reaches the complete Walsh endpoint and removes the two
zero rows. A nonzero added row is rejected by the source removal routine.

The complete fast fixtures use an explicit reduced parameter law
(d,K,G,H,delta)=(8,1,1,1,32). They use the complete elementary C2 fixture.
One or three disjoint copies of its two-family group give divisors two
or six. Copying a complete group changes the row divisor but not its
rowwise endpoint. The fixed source Ordinary backend uses q=2. These tests
are not production O73/GL64 payloads. Four direct-root fixtures keep the
production parameter formulas but use guard exponent two.

## Ownership and positive cost

All trial values are physical Count tapes. Their arithmetic is the retained
serial tape code. Each trial closes its core, depth, stock, digit count and
product before the next trial. Every borrowed input is rewound. Only the
three returned Counts remain live on success. Invalid domain controls leave
no live scratch lease. The caller closes the three outputs.

The standalone search needs at most 14 simultaneous owned leases. Before a
trial it has one, dimension_count, last, lower, upper and midpoint: six.
Core, returned depth and stock raise this to nine. The logarithm scan has
two local Counts and one subtraction result, for a peak of twelve. Its
returned bit count leaves ten live. Count.product temporarily needs factor,
scan and result, plus the one copy used by Count.add, for a peak of fourteen.
The initial profile, upper-bound division and final profile stay below that
peak. Compare, normalization and small fixed arithmetic need no extra lease.
The verifier checks this against a fixed pool of 32 tapes.

The root has fewer than 96 retained expression results and fewer than 32
simultaneous primitive temporaries. These are fixed source expression counts,
not functions of input width. The new search is below that temporary bound.
The inherited pool of 256 therefore remains sufficient. The tested roots
record their actual peaks. Empty pools and blank owned role tapes are checked
at complete returns; borrowed records and descriptor bytes are preserved.

Put B=ceil(log2(p+2)) and fix the construction constants. The trial interval
has O_F(B) values and each candidate uses O_F(B)-bit Counts. Serial copy,
comparison, schoolbook products, division, counters, rewinds and clearing
have positive costs. The loose O_F(B^5) tape-action and O_F(B^2) scratch-bit
bounds from PR5688 cover this direct implementation and the fixed-degree
threshold computation. The final original_rows descriptor can have
O_F(B+K) bits. Its construction and the other root output descriptors are
charged separately by their source scans. Payload copies, leaves, native
calls, parking and normalization remain paid.

The finite action receipt counts physical reads, writes and moves from
entry to output cleanup for 1,251 searches. It excludes input construction,
verifier observations and the caller's final destruction of borrowed inputs.
It is not a complete root bill or a measured production speedup. The fixed
search pool and the unchanged root pool add no input-dependent tape count.

## Frozen source and validation limits

The physical cohort authenticates a historical selected record. The retained
archive contains its exact source closure, with a per-member Git blob,
SHA256 and byte count in SOURCE-INDEX.json. It includes that historical
record only inside the isolated archive. The live selected frontier is not
changed. `retained.py` verifies all members before it activates the source
cohort. The source's own activation adapters are unchanged and remain part
of its inherited contract. Temporary extraction does not modify the package.

The source hash control, optimized Git-free run, bounded integer oracle,
complete reduced endpoint tests and ownership checks establish the stated
executable evidence. They do not establish the complete production physical
refinement, a literal universal transition table, independent human or
formal acceptance, an improved QQ16 invoice, or a new multiplication theorem.
