# Exact history for nearest-even rounded shears

For a fixed rational matrix A, retain the integer source x and return
`z = R(y + A*x)`, where y is an arbitrary independent integer destination and
R rounds each whole sum to its nearest integer, breaking half ties toward the
even integer. The minimum fixed binary history needed to reconstruct every y
is exactly

```
tau(A) = max over integer x of #{i : (A*x)_i is a half integer}.
```

A half integer means an integer plus 1/2. For `A = B/2` with B integral, tau
is the maximum Hamming weight in the binary linear code `im(B mod 2)`.
Even rational and binary rank one can require arbitrarily many history bits.
This is a scoped mathematical proof with exact finite corroboration, with no
physical history circuit, completed native child or new kappa.

## Contract and quantified result

Let A have m rows and n columns, with m,n positive and finite. Its coefficients
are fixed rationals. The map is

`F_A : Z^n x Z^m -> Z^n x Z^m, (x,y) -> (x,R(y+A*x))`.

There is no overflow, saturation, variable grid or hidden transcript. The
decoder knows A and the retained source x. A history is an extra value from
one fixed finite alphabet, and may depend on both x and y. All additional
input-dependent metadata counts as history. The guarantee is worst case,
without an average-length or input-distribution assumption.

For fixed x, write t(x) for its number of half-integer coordinates. Every
nonempty fiber over `(x,z)` has exactly `2^t(x)` elements. The smallest sufficient
history alphabet therefore has exactly `2^tau(A)` values. The smallest fixed
bit budget is tau(A), attained by the explicit decoder below. This is an
injective encoding statement, not a reversible machine on a full dirty
auxiliary state space.

F_A itself is a bijection exactly when every reduced denominator of every
entry of A is odd. Thus an integral dyadic A needs no history, while every
nonintegral dyadic A loses some information on the full entrance grid. A common
absolute grid precision does not change this statement after rescaling to
integer units, with the same unrestricted source and destination contract.

## Proof

Fix a scalar offset a. Away from half integers there is a unique nearest
integer, so `R(y+a)=y+R(a)` for all integer y. This coordinate is a bijective
integer translation.

If `a=k+1/2`, only even output integers z are possible. Each such z has exactly
the two preimages `y=z-k-1` and `y=z-k`. Their unrounded sums are z-1/2 and
z+1/2, which both round to the even integer z. No other integer y is within
distance 1/2. Destination coordinates are independent once x is retained.
Multiplying coordinate fiber sizes proves the exact `2^t(x)` statement.

Let D be the least common multiple of all reduced entry denominators. Changing
x by D times an integer vector changes A*x by an integer vector, preserving
its half-integer positions. Thus tau(A) is attained on `(Z/DZ)^n`. A nonempty
fiber at a maximizing source has `2^tau(A)` elements, which fewer history
values cannot distinguish, by the pigeonhole principle.

For the matching upper bound, enumerate the half-integer coordinates in row
order. At offset `k_i+1/2`, store the bit `b_i=y_i-(z_i-k_i-1)`. The decoder
returns `z_i-k_i-1+b_i`. At every other coordinate it returns
`z_i-R((A*x)_i)`. The retained source identifies the tie coordinates, so no
tie-location transcript is needed. Pack the t(x) bits in the low positions
of a tau(A)-bit history and pad the unused bits with zero. This reconstructs
every signed integer destination.

For the bijectivity classification, a sum of rationals with odd denominators
still has odd reduced denominator and cannot be a half integer. Conversely,
choose a row whose least common denominator d is even, and write it as
`(b_1,...,b_n)/d`. Minimality of d gives `gcd(d,b_1,...,b_n)=1`. Bezout's
identity supplies an integer vector x with `sum b_j*x_j = d/2 mod d`.
That row then has a half-integer offset. Hence tau is zero exactly for
odd-denominator matrices. When tau is zero, every source fiber is a bijective
translation; otherwise F_A has a collision.

Finally, if `A=B/2`, a coordinate is a half integer exactly when the corresponding
coordinate of `B*x mod 2` is one. Every binary source residue occurs, proving
the maximum-codeword-weight formula.

## Sharp consequences

For m copies of the single coefficient 1/2, x=1 makes every coordinate a tie.
The rational and binary ranks are both one, yet the fiber at the all-zero
output contains every `y in {-1,0}^m`. Exactly m history bits are necessary
and sufficient for every m>=1.

Rank also fails to determine the answer with dimensions fixed. The matrices
`B0=[[1,0],[1,1],[0,1]]` and `B1=[[1,0],[0,1],[0,1]]` both have rational and
binary rank two. The image weights of B0 are zero or two; B1 attains weight
three. Thus `tau(B0/2)=2` and `tau(B1/2)=3`.

## Reproduction and evidence

From the repository root, use CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B -W error research/nearest-even-shear-history/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/nearest-even-shear-history
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/nearest-even-shear-history --check-source-history
```

Both VERIFY.json commands are timed by the package runner. One enables isolated
optimized execution. All semantic checks remain active without assertions.
The direct verifier prints a generated JSON receipt with the hashes of all five
package files and writes nothing into the checkout. The written proof establishes
the unbounded theorem; finite enumeration corroborates it.

The independent literal oracle minimizes exact rational distance and breaks
ties by parity. The encoder instead uses an integer-division rounder. Destination
residues modulo two give a complete finite fiber oracle because
`R(v+2)=R(v)+2`. All source residues modulo the exact denominator are enumerated.

CPython 3.12.15 checks 682 binary matrices, with 5,003 source cases and 37,294
literal destination cases; 668 rational fixtures, with 12,891 source cases and
50,128 literal destination cases; 38,759 signed exact history round trips; and
13 malformed-input/history/image rejections. The binary domain contains every
matrix of each shape from 1-by-1 through 3-by-3. Rational fixtures include a
signed scalar menu, a complete mixed-denominator 2-by-2 menu and all 2-by-2
quarter-integral matrices with numerators zero through three. Rational fixtures
may repeat equal reduced coefficients. Additional controls check signed half
ties, the eight-element rank-one fiber, and increment/whole-sum distinctions.

The replay API caps matrices at eight rows and six columns and each periodic
corroboration at 4,096 source residues. All loops have finite fixture/dimension
bounds. There is no recursion. Python/Fraction allocation is a managed-runtime
deviation from fixed-memory rules; the live fiber Counter has at most 256
entries. Every function is under 60 lines. Explicit invariant checks remain
enabled with optimization. Warnings-as-errors run in both registered commands;
no additional static analyzer is configured for this package.

## Sources, scope and credit

This contribution was produced by Nick Petalas. Independent human and formal
proof-kernel review are unclaimed. New work is Apache-2.0.

Ali Romman's [PR #5838](https://github.com/CrocSwap/integer-mult-bounds/pull/5838),
head `a7fe04425abb083842686f29c54ca0fed6252d31`, distinguishes independently
adverse completed defects from an actual rounder with stronger correlations.
Its open question motivates this deterministic side result. Its error numbers
and source word are not replayed or newly claimed. SOURCES.json records the
exact README blob and SHA256 used as question context.

ywz65's [PR #2555](https://github.com/CrocSwap/integer-mult-bounds/pull/2555)
already gives a scalar whole-sum tie collision and the distinct positive
increment-rounding translation contract. Its unchanged README is pinned as
historical provenance. Rounding's general information loss, the pigeonhole
principle, Bezout's identity and binary linear codes are standard facts.
The new result is the exact rational-shear fiber/history classification,
its attaining encoding and the maximum-codeword-weight specialization.

The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19216882)
records the question. The original `joint-query-controller` card is explicitly
changed to this local arithmetic/cleanup theorem. Neither predecessor verifier
is imported. Source context is provenance, not a live computational dependency.

No history lifetime, physical register count, instruction count or reversible
uncomputation cost is proved. Restricted reachable inputs, different tie rules,
round-the-increment updates, extra retained outputs or discarded sources change
the contract. No full P104 word, native recipe, rounded supplier, selected cold
replay, compiler, tapes, Lean, outer arithmetic or complete multiplication
theorem has been implemented or verified. The five selected assumptions remain.

## Open next questions

Can one actual completed P104 child retain and uncompute its required tie
history within its complete physical bill? The encoding alone does not supply
a zero-return native workspace. First freeze the actual rounding sites,
entrance lattice and returned fields of one child, derive its fibers, then
price a history lifecycle. The missing completed physical child and history
restoration machine block that step. Structured details are in TASK.json.
