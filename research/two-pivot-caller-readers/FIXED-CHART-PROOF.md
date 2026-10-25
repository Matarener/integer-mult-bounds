# Exact rank mass of the fixed native-product chart compiler

This proves the physical-word-to-signed-graph implication used by the n=6
certificate. It concerns the literal compiler in
`source/root-chronology/native_chart_search.py`, with its fixed input ADD,
ADDRESS and bank-SWAP skeleton. It makes no claim about other compilers.

For each bank retain a pending product of the commuting native plane
operators. A bit `s_j` records whether plane j occurs. The exact signed
plane algebra has `N_j^2=-I`; its Gaussian unit is retained separately.
It contributes zero native rank, although its physical scan remains paid.
The compiler invariant is that the old logical bank equals its pending
native product times the current retimed physical bank.

Initially every s_j is zero. A native/ADDRESS unary with native mask t
and plane permutation pi replaces the pending mask by `t xor pi(s)`.
The literal ADDRESS is emitted, and the exact scalar sign is retained.
A bank-SWAP exchanges the pending masks. Neither case introduces a new
binary choice in this compiler.

Immediately before a literal scalar ADD, source and destination must use
one common chart r. The compiler permits every native-product r, with
one independent bit r_j per plane. It emits alignment products with
masks `s_source xor r` and `s_destination xor r`, then performs the
unchanged scalar ADD. Each differing bit pays native rank 2f. The final
restoration aligns each bank with chart zero and has the same cost rule.
Splitting an alignment into contracting pieces preserves this rank mass.

Represent every current bit as `x_v xor c`, where x_0 is the fixed zero
variable, and c is a constant. At an ADD introduce a new variable x_w for
each common-chart bit. The two alignments contribute edges `(v,w,c)`.
Their violation bits are `x_v xor x_w xor c`. Unary events only move
the labels and toggle c; bank-SWAPs exchange them. Final restoration
contributes `(v,0,c)`. This is exactly the chronological construction in
`source/root-chronology/signed_chart_optimization.py::graph`.

Therefore, for every binary assignment of all chart choices, not merely
an optimizer-produced assignment, the compiled native rank mass is
`2f * sum_edges (x_u xor x_v xor c_edge)`. The same identity holds for
every scalar ADD coefficient in the fixed skeleton. Additional physical
scan costs cannot lower this expression.

On an Eulerian edge subgraph, every variable occurs an even number of
times, so XOR of all its edge violation bits equals XOR of its edge
signs. An odd signed Eulerian subgraph must contain a violated edge.
The retained certificate contains 36 such subgraphs with disjoint edge
sets. Every assignment therefore has at least 36 violations, and native
mass at least 72f. The retained six-bank word has exactly 72f, proving
equality for this compiler. Its stock is also 72f.

The verifier reconstructs the graph from the complete retained word,
checks every edge index, even vertex degree, odd sign sum and global
edge disjointness, and replays the matching compiled word on every
original input column in both literal inverse orders. A repeated cycle
is a rejected control. Numerical optimizer bounds are not used.

For b>0 and any strictly smaller recursive rank r<m, one has
`r^(1-b)>m^(-b) r`. Thus a complete word in this fixed compiler with
rank mass at least n*m cannot meet a favorable positive-b moment
against n full-size banks. This is a scoped moment consequence, not a
global caller, native-alphabet or multiplication-exponent lower bound.

Ross Richardson with substantial OpenAI Codex assistance. Apache-2.0.
