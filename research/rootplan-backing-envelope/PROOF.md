# Complete encoded RootPlan backing envelope

This result was produced by Nick Petalas. Apache-2.0.

## Statement and boundary

Use the unchanged `MinimumRootPlan` in Ali Romman's merged PR #5707,
`research/encoded-minimum-root-prefix/planner.py`, pinned by SOURCES.json.
Its constructor fixes `2 <= m <= 73`, `1 <= r < m`, `F > 1` and integer
guard exponent `g >= 0`. Each successful `compute` borrows canonical,
distinct Counts

```
(p, s, left, right, C, B, rho),
p >= 2, C >= 1, B >= 1, 0 <= s <= d, 0 <= rho < K,
d = floor(p^(997/1000)), K = floor(d^(1/500)).
```

The seven borrowed tapes are separate from all owned tapes. Calls obey the
source's empty-scratch entry contract. We count `len(Tape.cells)`, including
erased BLANK tails, for its 256 scratch tapes and 29 field tapes. This does
not count Python heap memory, borrowed input backing, payload execution,
tape actions, or storage elsewhere in `RootLayer`.

For a call define

```
b = bitlength(p), u = bitlength(C), v = bitlength(B),
c = ceil(log2 F), h = m - 1, z = left + s*K + right,
E = 8 + max(1994*b, c*h*b, z + u + v + b + g).
```

For any finite history of successful calls, let `a_i` be physical tape i's
initial extent. At every instant through call j and its field cleanup,

```
len(cells_i) <= max(a_i, E_1, ..., E_j).
```

The sum of those 285 maxima bounds the complete owned backing. A cold
planner therefore needs at most `285*max_j E_j` cells throughout its history.
These are sufficient bounds, with no optimality claim for their constants.
The successful-call premise does not assert absence of pool exhaustion on
every input or provide a complete multiplier implementation.

## Primitive extent rule

The retained Count implementation represents an L-digit natural by LEFT at
index zero, digits at 1 through L, and RIGHT at L+1. Zero has one digit.
Copies, literal construction, increment and multiplication by a compiled
constant write only through the longest old or resulting digit interval.
Addition copies its right operand, then writes at most the longer input or
the sum's interval. `Count.product` copies both factors and scans multiplier
prefixes. Its result and temporary sums never exceed the final product when
both factors are positive. A zero factor still requires its input copy.

`encoded.divide` copies the divisor and keeps quotient and remainder. Each
pre-subtraction remainder is less than twice the divisor; quotient prefixes
are bounded by the final quotient. `subtract` copies its left operand.
Normalization and division may leave erased high digits, but never extend
past an already bounded old interval. Counter copies and decrements do not
increase the copied digit interval. `copy_symbols` writes the complete
Count including RIGHT. Clear writes through an existing dense body only.
Add two cells to a digit bound for the markers.

These rules follow directly from the retained `cardinal_counts`, `counts`,
`cardinality`, `encoded`, `compact_counts`, `stream`, `machine` and `records`
implementations. Their exact transitive bytes are retained in PR5707's
source archive. The new step is applying these rules to the complete caller,
including expressions outside the standalone callee of JoyboyBrian's PR #6098.

## Parameter calculations

The largest uncapped power target is `p^997`, used by `floor_power` and
`atom_width`. Exponentiation by squaring constructs powers with exponents
no larger than the requested fixed exponent. Saturated powers return their
cap when a nonzero operand is already at least the cap. Otherwise they
first form the full product of two operands smaller than the cap. Thus
saturation does not justify charging only the cap's length.

Every target and cap is at most `p^997+1 < 2^(997*b)+1`. Every such full
product has fewer than `1994*b+2` binary digits. Input copies, bisection
sums, `cap=target+1` and the smaller root computations fit this same bound.
The marker allowance in E exceeds the resulting `1994*b+4` extent bound.

The other parameter fields obey

```
1 <= d <= p, 1 <= K <= p,
G = 4 ceil(log2 p)+6 <= 4*b+6 < 2^(b+3),
H = d*G < 2^(2*b+3), delta = d*2^g < 2^(b+g).
```

Hence `qF=ceil(2H/K) <= 2H`, `qB <= H`, and their sum, products by K,
and addition of `q0 <= p` use fewer than `2*b+6` digits. The products
`qF*K < 2H+K` and `qB*K < H+K` are bounded before their subtractions.
`input_bits=p+2` and `work_bits=p+2*delta+3` use at most `b+g+3`
digits. Intermediate additions are nonnegative prefixes of those sums.
The fixed literals through m have at most seven digits. All these lengths
fit E after markers.

## Complete minimum-prefix call

This part uses the standalone envelope proved in JoyboyBrian's PR #6098 as
a cited input. Its proof gives, for `M=remaining <= p` and spacing `K<=p`,
at most

```
2 + max(7, bitlength(M)+bitlength(K)+1,
        c*h*bitlength(M)+2)
```

cells for every newly reached scratch extent. This is at most E. Other
caller leases remain live during that call, but cannot be acquired again
until closed. Their values are covered by the other rows of this proof.
The callee's free slots are still physical members of the same 256-tape
pool. No standalone aggregate or 14-live-lease bound is substituted for
historical backing of the caller.

The returned `q0` is at most M-1, every profile depth is at most h*b, and
`stock=F^depth <= 2^(c*h*b)`. These are the cited callee contract. The direct
branch returns constants zero and one instead.

## Address and row expressions

Put `a=s*K` and `t=q0*K`. Both are nonnegative, and on the fast branch
`t <= a`, since `q0 < M <= s`. The remaining complete expression ledger is

| Expression | Digit bound or nonnegative magnitude bound |
| --- | --- |
| `active_bits=s*K`, its input copies | a; numeric digit length <= z+1 |
| `left+active_bits+right` | z; its digit length <= z+1 |
| `addresses=2^z` and its Counter | z+1 digits; the counter is no longer |
| `gaussians=addresses*C*B` | at most z+u+v+1 digits, including both partial products |
| `core_width=s-Q0` | at most p |
| `core_front=qF*K-2H` | less than K |
| `core_back=qB*K-H+right` | less than K+right |
| `row_axes=t`, `original_rows=2^t` | t<=a; at most a+1 digits for the power |
| `prefixes=B*2^left` | at most left+v+1 digits |
| `ceil(original_rows/stock)` | quotient <= original_rows; temporary remainder < 2*stock |
| `padded_rows=ceil(original_rows/stock)*stock` | less than original_rows+stock, hence at most max(a,c*h*b)+2 digits |
| `rectangle=active_bits-row_axes+right` | between zero and a+right, hence at most z |
| `row_gaussians=2^rectangle*C` | at most z+u+1 digits |
| `row_bits=2*row_gaussians*work_bits` | at most z+u+b+g+4 digits, including the partial product |

The padded-row estimate uses only division arithmetic. It does not need
strict factor-two feasibility or a replay of the predecessor's padding
theorem. Product prefixes are bounded by the final value. Input copies,
sums, subtractions, counters and saved field copies all occur in this
ledger or the preceding parameter/callee ledgers. Borrowed left and right
have digit lengths at most z+1, since each is at most z. C and B have u and
v digits. Every row plus its two markers fits E. The direct branch replaces
the fast-only fields by zero or one, while still constructing addresses
and gaussians; it therefore fits as well.

## History and consequences

`Tape.write` extends a tape exactly to `head+1` when necessary. Nothing
reached here truncates `cells`. Thus each tape's extent is exactly the
maximum of its initial extent and every write index plus one so far. The
ledgers show that computation cannot extend it beyond E. Cleanup can write
through an older larger body, already in the prior maximum, and cannot
extend it. Induction over writes and calls proves the history theorem,
even with arbitrary finite initially erased tails.

For the production law, `a=s*K <= d*K`. Since `K^500 <= d` and
`d^1000 <= p^997`,

```
a^500000 <= p^499497.
```

For fixed construction constants the cold bound is therefore
`O(left+right+p^(499497/500000)+bitlength(p)+u+v)` cells. In particular it is
`O(p+left+right+u+v)`.

A bound linear only in encoded input digit lengths is impossible with
unrestricted side widths. Fix p=2, s=right=0 and C=B=1. For every integer
N>=0 set left=N. This direct-branch family has saved `gaussians=2^N`, with
exactly N+3 cells through RIGHT in its cold field. Borrowed left has only
max(1,bitlength(N)) digits. Conditional on successful execution, this lower
bound follows directly from the saved output. The usual Count primitives
terminate and this direct branch uses a fixed number of leases, so this
family also supplies actual successful calls. This explains why the complete
planner cannot inherit the callee's logarithmic bound without a caller
restriction on numeric side widths.

The proof concerns numerical backing of successful planner calls. The
enclosing root, its payload, precision accuracy, movement costs, arbitrary
exceptional exits and the five framework assumptions remain outside scope.
