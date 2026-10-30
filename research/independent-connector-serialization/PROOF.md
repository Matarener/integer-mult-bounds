# Independent dirty connectors can be serialized without extra calls

This is a written algebraic proof. The executable evidence corroborates it on
bounded domains. No formal-kernel or independent human verification is claimed.

## Contract and statement

Work over F2. There are finitely many immutable source arrays `x_j`, arbitrary
dirty connector arrays `z_p` of the same dimension, and distinct dirty output
arrays `y_i`. Every source has a fixed compatible linear map `B_j`, and every
output has a fixed compatible linear map `A_i`. The maps may be singular and
need not commute. At every connector port the same named map is available.

A finite data-independent word uses only the complete calls

```text
B_j(p): z_p += B_j x_j
A_i(p): y_i += A_i z_p.
```

Each call preserves other rows and restores disjoint private scratch and its
agreed head/frame state. Public source, output and connector arrays are excluded
from private scratch. There are no transfers between connectors, root-frame
changes, source writes, output reads or mixing, aliases, resets or hidden clean
arrays. Outputs are observed only at completion. At the endpoint every root is
restored and each output has a prescribed source-only increment

```text
y_i += A_i sum_j M_ij B_j x_j.
```

Correctness must hold for every compatible assignment of the maps and arbitrary
initial source, root and output contents. This is the inherited universal
connector contract with arbitrarily many independent connector rows.

**Serialization theorem.** Every such word can be replaced by a word on one
arbitrary dirty connector, with exactly the same number of calls to each named
`A_i` and `B_j`, and exactly the same required endpoint. Stable grouping by root,
followed by replacing every root name by one common root, constructs it.
Unused connector spectators remain untouched. The theorem covers all finite
source/output/root counts and word lengths; the executable API has smaller
resource limits.

Consequently the sets of attainable aggregate call-count vectors with one and
with any fixed positive number of independent roots are equal. The reverse
inclusion simply leaves the additional roots unused.

## 1. Calls on distinct roots commute

Two B calls on distinct roots update distinct arrays from immutable sources.
A B call and an A call on distinct roots also commute, because the source of
the A call is unchanged by the B call. Two A calls commute even if they share
a destination: both add an independently determined value, and neither reads
an output. This uses addition in the output space, without commuting any
`A_i` past any `B_j` inside a composed product.

Adjacent exchanges of such calls stably group the word by root. This first
step preserves the entire map on all original rows, including every dirty
root column, and preserves every named call count. It does not yet identify
any two roots. Grouping alone would not justify dropping a restoration or
intermediate observation requirement.

## 2. Every root block restores its own source state and cancels its own dirt

Write `b_j=B_j x_j` and let `d_p` be the independently arbitrary incoming root.
At any cut in root p's block its value is

```text
d_p + sum_j q_pj b_j,
```

where `q_pj` is the parity of preceding B_j calls in that block. Restoring root p
forces the final `q_pj` to vanish. Necessity follows by specializing to scalar
identity maps with independent source bits. Conversely, those parities suffice
for all linear maps, so the block returns its root exactly for every input.

For output i let `r_ip` be the number of its reads from root p, modulo two.
The contribution of the block has the form

```text
r_ip A_i d_p + A_i sum_j c_ipj b_j.
```

No other block can cancel the `A_i d_p` term because its incoming dirt variables
are independent and it never reads root p. Correctness of the full endpoint
therefore forces every `r_ip=0`. Again scalar identity maps with independent
root bits prove necessity. Thus each block's output increment is independent
of its root's incoming contents, even when the block does not implement the
complete target by itself. The source coefficients `c_ipj` may differ between
blocks and may cancel when added.

## 3. Reuse one dirty connector sequentially

Run the grouped blocks on the same incoming dirty row d. Each block restores d
and makes the same source-only output increment it made on its own root.
Earlier blocks may have changed the outputs, but later blocks never read them.
Their increments therefore add to

```text
A_i sum_j (sum_p c_ipj) B_j x_j,
```

which is the original endpoint. No call is inserted, deleted, inverted or
changed to a different named map. The resulting per-operator counts are
identical. A linear-time implementation uses one bucket per input root and
visits each event once before concatenating the buckets.

The order of these two steps matters. For two sources, two outputs with masks
1 and 2, and two roots, the interleaved word

```text
B0(0) B1(1) A0(0) A1(1) B0(0) B1(1) A0(0) A1(1)
```

is valid. Identifying the roots immediately makes both outputs receive
`A_i(B0 x0+B1 x1)`. Grouping by root before identification gives the required
separate singleton outputs. The CLI rejects the immediate-identification mutant.

## 4. The five-source tariff is unchanged

Adam Gall's PR2063 proves the one-root optimum and its sixteen minimal count
vectors. Let `b_j>0` price a complete B_j call and `a_m>0` price a complete A_m
call, with the same price at every root port. For all 31 nonzero five-bit masks,
put `H={m: popcount(m) is 3 or 5}`. Serialization gives the same optimum for
any finite number of independent dirty roots:

```text
OPT = 2 sum_j b_j + 2 sum_(m=1..31) a_m
      + 2 min({b_0,...,b_4} union {a_m: m in H}).
```

The aggregate componentwise frontier is exactly PR2063's sixteen vectors:
two calls to each map plus two calls to one of the five sources or eleven heavy
odd readers. Every vector is attained on one root; serialization excludes any
new vector on more roots. No new source-word census or all-tariff classification
is claimed. The new implication is that the inherited optimum survives
arbitrary independent workspace and arbitrary redundant call multiplicities.
At unit map prices the exact map bill remains 74.

## 5. What changes the conclusion

Root transfers break the first step. Adam Gall's credited PR2065 six-transfer
word has ten source calls, 62 reader calls and six charged root XORs. With
common complete map price 1 and transfer price 1/4, its map-plus-transfer bill
is `72+6/4=147/2<74`. This is a conditional price illustration of that existing
construction, not a new word or a realized supplier price. An extra setup bill
can remove the advantage. We replay its dirty endpoint and explicitly reject
its transfer alphabet at the serializer boundary.

Port-specific prices do not survive root substitution. Consider two sources,
two singleton outputs and two roots. Give B0 price 1 at root0 and 100 at root1,
and give B1 the opposite prices. Every A call costs 1. The displayed
interleaved word costs 8. At either single root, at least two uses of the
expensive source, two of the cheap source and four output reads are necessary,
so the exact one-root bill is 206. Separate four-call echoes attain it. This
is an abstract complete-price counterexample, not a measured machine cost.
Call counts are preserved while physical port prices change.

An intermediate observer also changes the contract. Run a four-call singleton
echo for output1 on root1, then one for output0 on root0. After four calls the
original word has updated output1. Stable ascending-root serialization updates
output0 first and leaves output1 unchanged at that cut. The final maps agree;
the specified delivery observation does not. Output feedback, shared child
scratch, different root dimensions and map-dependent frame conversions likewise
need their own contracts.

For a physical comparison add each word's actual admission, preparation,
instruction, storage, routing, hosting and dispatch charges not already inside
the complete call prices. The theorem equates the map-call bill under uniform
ports. It does not equate these additional charges or elapsed time and does
not establish an admitted supplier, contracting moment or new kappa.
