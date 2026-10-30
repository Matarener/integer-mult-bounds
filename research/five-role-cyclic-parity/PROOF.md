# Twenty clockwise XORs are necessary and sufficient

This contribution was produced by Nick Petalas. Apache-2.0.

## Endpoint and alphabet

Five labeled registers contain independent arbitrary vectors over F2. The
only allowed instructions are `r_(i+1 mod 5) += r_i`, for i=0,...,4. Every
instruction costs one. The requested complete output is

```
y_i = x_i + x_(i+1 mod 5) + x_(i+2 mod 5),   0 <= i < 5.
```

No additional registers, free wire permutations, basis changes, initialization,
erasure or nonlinear/data-dependent instructions are allowed. The endpoint
matrix has row masks `(7,14,28,25,19)`, with bit j denoting input x_j.
The alphabet has exactly five generators, all involutions. Reverse-direction
neighboring additions and nonneighboring additions are excluded.

## Attainment

The following ordered word has twenty instructions. Each pair is source,
destination, and every pair is one of the five allowed clockwise edges.

```
(0,1) (2,3) (4,0) (0,1) (1,2)
(0,1) (3,4) (2,3) (4,0) (3,4)
(2,3) (1,2) (0,1) (3,4) (2,3)
(4,0) (0,1) (1,2) (0,1) (3,4)
```

Literal symbolic row substitution gives the specified complete matrix. A
separate bit interpreter executes the word on all 32 scalar inputs and checks
the same endpoint. A linear identity on the five input basis vectors extends
coordinatewise to arbitrary binary vector payloads. Reversing the involutions
recovers all five independent inputs. Thus twenty is an upper bound.

## Exhaustive lower bound

Encode each binary 5-by-5 matrix in a 25-bit integer, with five consecutive
five-bit rows. Adding row s to row d is exactly the `step` operation in
verify.py. Define B_r(M) to be all states reachable from center M in at most
r allowed instructions.

Starting with {M}, form all five neighbors of every state in the latest
layer, discard previously seen states and repeat r times. Induction proves
this enumerates exactly B_r(M): every positive-length word is a shorter
word followed by one allowed gate. Keeping only the shortest occurrence of a
state preserves every possible continuation. The search uses no symmetry
quotient, pivot heuristic or pruning beyond equality of complete matrices.
Its domain is contained in the 2^25 binary matrices.

The complete enumerated exact-distance layers are

```
radius     0  1   2   3    4    5    6     7     8     9     10
layer      1  5  15  40  100  240  555  1230  2665  5715  12010
```

The identity ball B_9(I) has 10,566 matrices. The target ball B_10(T) has
22,576 matrices. Their intersection is empty. Both balls and every layer
count are computed afresh by the standalone verifier, without accepting any
saved distance table or discovery output.

If a word of length l<=19 connected I to T, cut it after min(l,9) gates.
The intermediate matrix would lie in B_9(I). Reversing the remaining at most
ten involutions would place it in B_10(T), contradicting disjointness.
Therefore at least twenty instructions are necessary, matching the witness.

This is a finite computer-assisted certificate with a written reduction to
arbitrary vector payloads. It trusts the explicit enumerator and Python
execution; independent human and proof-kernel review are unclaimed.

## Controls and prior work

The literal bit interpreter uses a list of five bits, independently of packed
matrix arithmetic. It checks all 32 inputs, inverse recovery and a failure
after deletion of each of the twenty gates. The first nineteen witness gates
supply a positive control for the same 9+10 exclusion method: their known
nine-gate midpoint belongs to both corresponding balls. Nine malformed
input/program cases reject. All checks use explicit exceptions under -O.

Gareth Davidson's merged PR #1188 already certifies every unrestricted
five-role distance using all twenty directed row additions. This contribution
does not claim a new unrestricted metric or replay that predecessor. Restricting
the generator alphabet changes which paths exist; a shortest unrestricted
path does not determine the present optimum. Ali Romman's PR #5793 supplies
the related custom-alphabet synthesis interface, limited to four roles.
Classical shortest paths and meet-in-the-middle exclusion retain their credit.
Global literature priority for this endpoint is unclaimed.

The result prices scalar binary register additions in the stated cyclic
layout. It supplies no native tensor identity with phases, physical routing
invoice, recursive paid-child minimum, new kappa or complete multiplication
theorem. Other layouts, extra registers and altered alphabets are outside scope.
