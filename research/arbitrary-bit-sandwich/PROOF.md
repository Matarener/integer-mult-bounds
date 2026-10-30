# Conditional arbitrary-bit boundary construction

This is the correctness and payment argument for the new wrapper in
`boundary.py`. It uses the completed Sandwich interface of JoyboyBrian's
PR5095 and implements the released handoff in Discussion3664. The handoff's
representation calculation is predecessor work. No production recovery or
multiplication theorem is established here.

## Preconditions and promised return

Let n,b be positive integers represented by canonical independent Count
tapes. First, second and catalogue are three further distinct borrowed Tape
ports, disjoint from every boundary and child resident tape. Both operands
contain exactly n binary cells followed by BLANK, after a LEFT marker.
Their values x,y lie in [0,2^n); leading zeroes are allowed. Input heads are
at their canonical first-cell positions. Arbitrary incoming head positions
are outside this contract. The catalogue remains a child-admission input.

The child is idle with no pending return. For positive q,b and two complete
qb-bit packed operands, its successful production call returns exactly 2qb
MSB-first bits for their exact integer product. Its returned Tape is borrowed
until `consume`, which clears the body and owned marker. It preserves its
borrowed ports, returns their heads canonically, and closes its own work.
A failed child call must also close its work and preserve the borrowed ports.
The child retains every analytic/catalogue/native precondition for recovery.
These are interface premises, not claims proved by wrapper tests.

The wrapper's successful return is exactly 2n MSB-first bits representing xy.
It preserves the five borrowed ports and their canonical heads. Its two packed
banks and metadata leases are erased. Its own return stays protected until
the caller invokes `consume`, after which its body and marker are erased.

## Encoded parameter and representation argument

The retained exact `divide(n,b)` returns quotient a and remainder r with
n=ab+r and 0<=r<b. The wrapper sets q=a+[r>0]. Its exact product and
subtraction operations compute d=qb-n, so 0<=d<b and q>=1. No input Count
is converted into a host integer.

Validation reads exactly n symbols and then requires BLANK. Reversing those
n MSB-first bits puts bit i of x at packed position i for 0<=i<n.
Appending d zeroes extends it to qb positions. Thus packed word j, read
little-endian within the least-significant-first b-bit word sequence, equals

```text
floor(x / 2^(jb)) mod 2^b,  0<=j<q.
```

The same holds for y. The child's exact-product premise therefore gives xy
in 2qb MSB-first bits. Since xy<2^(2n), the first 2d bits must all be zero.
`normalize` explicitly checks those bits, copies exactly 2n further binary
symbols and requires BLANK immediately afterwards. It rejects a nonzero
prefix, a short output, an invalid symbol or an extra symbol. The copied
stream is therefore the claimed product representation.

## Ownership and failure argument

Construction allocates 32 metadata tapes, two packed tapes and one output
tape. Their identities and the child's declared private inventory are fixed
before numerical entry. Preflight rejects repeated external ports, metadata
aliases, all private aliases, a busy child and an unconsumed wrapper return
before moving any tape. Positivity is checked before owned marker setup.

The installed metadata pool redirects retained Count and Counter constructor
sites to leases. Physical Tape/Arena constructors are sealed during the
invocation. The wrapper never reads cells, a head index, an inspected Count
value or a meter in its charged runtime. Count tests inspect only symbolic
digits through the retained physical methods.

Both operands are validated and packed before child entry. If either fails,
the common finally path rewinds the borrowed ports and clears partial packed
banks and every live metadata lease. The child is not called. During the
child call the wrapper's allocation scope is suspended, preserving its live
metadata leases while the child uses its own owner inventory.

Every successful child return enters an inner finally block that invokes
`child.consume`, including when output validation fails partway through the
prefix or copied return. A completed child failure follows the child's
cleanup premise and then the wrapper's common cleanup path. On any failure
the partial wrapper output and its marker are erased. On success only that
output remains live. The later wrapper `consume` pays its clear and marker
erasure. No return is silently treated as deallocated storage.

The guarded lease inventory is sufficient for these retained operations.
The main scope retains at most six metadata tapes: q, r, qb, d, 2n and 2d.
The final payload loops add one Counter at a time. Earlier setup operations
retain fewer main values: divide owns at most its divisor, quotient and
remainder plus one replacement remainder; product owns two copied factors
and a result; literal construction adds one temporary tape; subtract owns
one result. Count copying, normalization, comparisons, small multiplication
and increment create no additional physical tapes. These bounds are all
below the fixed capacity of 32 and do not depend on n or b. Child work is
outside this pool while the scope is suspended.

## Payment and space

Write D(n,b) for the paid retained Count division, product, subtraction and
constant-factor operations used to form q,d,2n,2d. This term is retained;
it is not assigned zero or claimed constant time.

Validation, forward traversal, reverse copying, zero padding, normalization,
rewinds and erasure each scan at most a fixed number of streams of lengths
n, d, 2d, 2n or qb. The countdowns copy a finite binary Count and use the
retained ripple-decrement routine. Across k decrements the carry lengths
sum to O(k+log(k+1)), so their complete setup/decrement/close cost is linear
in the scanned extent plus its encoded width. The wrapper adds

```text
O(qb + D(n,b))
```

physical operations to `child.run`. This includes consuming the child's
2qb-bit return and consuming the wrapper's 2n-bit return. It does not infer
an affordable complete production bill from that asymptotic expression.

The added payload capacity is at most 2qb+2n cells, plus markers, for the two
packed banks and output. Each metadata role has the historical maximum extent
of its retained Count/Counter operations. These operate on values bounded by
a constant multiple of n+b, with bounded digit/marker slack, giving
O(log(n+b+1)) cells per metadata tape under the retained Count storage
contract. The fixed pool has 32 tapes. Historical backing is kept after
clear; the space statement uses the maximum visited extent of each tape.
The child's complete inventory and storage bill are additional.

The 29-by-23 fixture measures every participating physical meter before and
after execution and final consumption. It subtracts only the fixture
`child.run` meter delta. Child consumption remains charged. Host oracle
calculation and output inspection are outside those deltas. The resulting
exact boundary tally is 1,738 reads, 468 writes and 1,746 moves. This single
fixture is evidence about the declared metered implementation, not a
production or end-to-end performance claim.

## Scope of verification

The 1,845 positive fixtures use independent host integer products as completed
child returns and literal packed-stream expectations. They execute the actual
Tape/Count/Counter runtime with sealed constructors and Count decoding
disabled. The failure and ownership controls test the new wrapper's state
transitions. A separate actual Sandwich invocation preserves its mandatory
rejection of the reduced catalogue and exercises cleanup through the real
owner boundary. The predecessor's numerical experiment is not replayed.

The written argument supplies the conditional finite-n contract. It leaves
production parameter choice, catalogue preparation, numerical precision,
native admission and complete multiplication costs open. Independent human
and formal proof-kernel review are unclaimed. This proof and the new wrapper
were produced by Nick Petalas; predecessor formulas and interfaces retain
their credit. Apache-2.0.
