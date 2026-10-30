# Encoded coefficient-address conversion

Tekalign (tekuuu), with substantial OpenAI Codex assistance. Apache-2.0.
Base: `20ecf2891d80b5acf18d980b2164fb44ea7faa90`.

## Statement and exact interface

Let D≥1, pairwise coprime odd integers s_i≥3, and powers of two t_i>s_i
be given on canonical little-endian Count tapes. Put S=∏s_i, T=∏t_i,
n=log₂T, P_i=∏_{j<i}s_j and μ_i=P_i⁻¹ mod s_i. A payload contains C≥1
rows, each of S consecutive opaque R≥1-bit records. Borrowed ports stand at
their left origin. Forward conversion moves record k to the natural tensor
address with digits b_i=μ_i k mod s_i; the final axis is contiguous. Inverse
conversion moves that record back to ordinary coefficient k. All R bits of
every record and every row are carried together. Output is a distinct owned
port, which the consumer must clear and erase before reuse. The implementation
restores borrowed bytes/heads and empties its scratch and routing descendants
on successful return. Checked malformed metadata/payload exits also clean their
owned scratch. This is not an interrupted-child recovery protocol.

`Converter.run_plan` accepts the actual, unchanged PR3935 `TensorPlan`, compiled
at `240597ed313fc2854c0462b23c89dc3bae72aaf5`. It extracts its packed axis rows
and checks its source product, padded product and address width against the
computed shape. The default record width is exactly `plan.record_bits`.
This is a typed layout bridge, not a call of the numerical tensor engine.
A TensorPlan need not have coprime source lengths; the new adapter rejects such
a plan. The executable typed witness has s=(3,5), t=(4,8), p=16 and is explicitly
nonproduction. Its 15 source records and 32 padded records match the real plan.

## Algebra and padded extension

This algebra is inherited from source08 (lines 216–283), following
Agarwal–Cooley; the new result is the encoded implementation and its complete
routing bill. The map x↦∏x_i^μ_i is a cyclic-group isomorphism because each μ_i
is a unit and the s_i are coprime. Therefore it preserves cyclic convolution.
Writing k=Σa_iP_i, its i-th coordinate is

    b_i = a_i + μ_i Σ_{j<i} a_j P_j (mod s_i).

Terms with j>i vanish modulo s_i; μ_iP_i=1. Forward updates run in descending
i, so lower coordinates are still original. Inverse updates run in ascending
i and subtract the same expression from already recovered lower coordinates.

On the full padded box, use offset zero whenever a lower control is invalid.
For a valid lower prefix, rotate only [0,s_i), fixing [s_i,t_i). Each step is
a bijection preserving the valid box and its complement, including arbitrary
nonzero payloads on invalid prefixes and target tails. Consequently initially
zero padding stays zero. Cropping checks every discarded bit is zero; it does
not silently throw away nonzero information.

The offset producer enumerates physical lower prefixes in natural axis order
(the last lower axis varies fastest), using a single packed address tape.
Its integer arithmetic forms Σa_jP_j and multiplies by μ_i before taking its
residue. No metadata cardinality is decoded into a host integer. Modular inverse
uses the binary extended-gcd invariants u≡ax, v≡ay mod m, 0≤x,y<m for odd m.
Even operands halve, adding m before halving an odd coefficient; odd differences
subtract modulo m. Each subtraction followed by halving reduces the positive
operands. A unit reaches 1. A nonunit reaches equal operands greater than 1
and rejects. Computing inverses for every prefix checks precisely the needed
coprimality, rather than assuming primality of the supplied s_i.

## Physical composition

Ordinary k order is colexicographic a order. Padding first enumerates the full
colex box. A single full-support router then reverses the order of the axis
fields, retaining little-endian bit order inside each field. It moves old bit
position P+j to n-P-width+j. The descriptor is sorted by old position and uses
the unchanged fixed-width `router_metadata.write_pair` codec. The inverse
map is separately compiled and sorted: unequal field widths do not in general
give an involution on bit positions.

In natural padded order, each controlled shift splits its target into the
first s_i-offset positions, the remaining offset positions, and the invalid
tail. A first sequential pass writes three bucket tapes. A second emits the
second, first and invalid buckets in that order, carrying each complete
spectator suffix as a block. Inverse splits at offset instead. It prepares
actual encoded offsets; there is no free shift or address oracle.

The actual tensor interface is compact, so a complete conversion is:

* forward: colex compact → colex padded → global field permutation →
  descending triangular shifts → natural compact;
* inverse: natural compact → natural padded → ascending inverse shifts →
  inverse global permutation → colex compact.

Thus each conversion pays one global router call, D shifts and **two** padding
passes. Integer multiplication would use three conversions (two forward inputs
and one inverse output), hence **three**, not two, global router calls. The final
S² normalization, rounding/carry recovery and integer wrapper are not supplied.

## Time invoice, including setup and restoration

Write V=CTR and r_min=min t_i. With n=Θ(p), R=Θ(p), the complete conditional
invoice per conversion is

    O(V p^β log^(1+τ)p + D V + CT(n+R)
      + C D T poly(n)/r_min + poly(p)) + fixed native compilation F_q + source setup F_src,

where τ=332353/332929 and β=41544341/41616125. The polynomial degrees are fixed,
independent of D,C and the input values. F_q is charged once to a fixed compiled
native instance; it is not silently reconstructed at each conversion. F_src
pays authentication, copying and extraction of the fixed pinned local source
artifacts once per cold cohort, with their fixed storage retained separately.
Network transport is a replay prerequisite, not a numerical tape operation.

The first term is the full-support PR3935 router theorem at the exact source
pin above (PROOF.md, “four canonical gathers”). It includes factorization into
two involutions, sorted batches, all unchanged spectators, interval/reservoir
selection, metadata, child recompilation and restoration. Its polynomial setup
is retained, then absorbed only under its stated n=Θ(p) caller hypothesis.
We inherit its B1/sparse endpoint, all-size/compiler, universal cost and bounded
fallback premises. We neither certify those premises here nor execute its
production-sized selected native program in the q=2 literal fixtures.

Each shear pays O(V) movement, including bucket copying/erasure, full suffixes,
row-offset copying and counter restoration. The copied offset has O(log t_i)
length, at most a constant times the t_i target records it controls. There are
B_i=∏_{j<i}t_j≤T/t_i prefixes. Packed metadata lookup and binary arithmetic cost
a fixed polynomial in n per prefix, so total offset preparation is bounded by
D T poly(n)/r_min; the displayed C factor safely includes row replication and
row-extent setup. Shape compilation, modular inverses and descriptor compilation
cost poly(n). Canonical binary countdowns have amortized ripple cost; fixed-role
Count products and their explicit rewinds are charged. Logarithmic C/R setup
is dominated by the full packet bill, since C,R≥1 and T=2^n.

Padding uses a packed (s_i,width_i) page, never a fresh scan of the full six-field
plan for each digit. Extracting all address fields, comparing bounds and returning
the heads costs O(n) per address. Handling the opaque record costs O(R).
Both scans therefore cost O(CT(n+R)); when n,R=Θ(p), this is O(V). Final compact
output copies and all successful erasures add O(V+poly(n)).

For the *conditional* newer caller laws D=Θ(p^(997/1000)), ell=Θ(p^(3/1000)),
t_i∈{2^ell,2^(ell-1)}, n=Θ(p), R=Θ(p), r_min exceeds every fixed polynomial.
Thus offset preparation is o(V), and .997 < β < Φ=.99827619697. The router's
extra factor log^τ p is absorbed by the strictly positive gap Φ-β. The complete
conversion is consequently O(V p^Φ log p). Three conversions obey the same
order, but their constant and F_q/setup costs remain paid. These inequalities
are conditional cost comparisons, not a new κ or a complete multiplication
algorithm. The pairwise coprime lengths are explicit inputs: no claim is made
that an old prime-generation cutoff proves their existence under newer laws.
Source08's adjacent-swap *upper bound* O(V D²(1+ell^τ)) does not certify this
allowance under these laws; it is not a lower bound or an impossibility theorem.

## Fixed roles and backing

The wrapper has 192 scratch roles and one protected output, allocated before
entry; all numerical execution runs under sealed constructors. There are no
D-sized host lists of runtime tapes. Axis metadata occupies O(Dn)≤O(n²) cells
on two packed tapes. Buckets, current data, offset copies and output occupy
O(V+n²) live cells. The finite maximum wrapper lease count is reported as an
observation, not an all-parameter role proof. A lexically fixed inventory bounds
simultaneous roles: shape/page ≤6, one six-field axis plus enclosing counters
≤16, prefix preparation plus its nested axis/arithmetic ≤64, or shear/copy
≤32, descriptor/padding ≤32, and conversion staging ≤16; even their conservative
sum is <192. Nested arithmetic uses fixed tuples of Counts, independent of D.
The child has its own fixed inventories, retained from its authenticated source.

`Tape.clear()` erases cells but does not shrink its Python bytearray. For a
sequence of calls, each fixed wrapper role therefore retains its largest past
extent. Wrapper *backing* is O(max_history(V+n²)), not merely current live space.
Add the inherited child high-water backing (including polynomial planning) and
fixed native storage and fixed source/extraction storage separately. This is not a quantified production memory
coefficient or a claim that all retained native backing is O(current V).

## Verification scope and unresolved work

The replay checks every coefficient column simultaneously as independent opaque
basis bits, forward and inverse, on four complete shapes (including unequal
widths and three axes), and compares directly to kμ_i mod s_i. It checks every
padded prefix, separate descriptor directions against the unchanged codec,
nonzero invalid shear geometry, the actual typed TensorPlan, 2,176 unit/nonunit
inverse cases, source and receipt integrity, protected outputs, malformed inputs,
zero-padding checks, aliases, dirty prior work and wrong-algebra/order controls.
It checks exact exponent arithmetic independently. These are finite implementation
checks alongside the scoped argument above, not formal verification of the
all-size multiplication theorem. Native compilation/execution at production q,
the inherited router theorem assumptions, prime supply, actual numerical tensor
composition and final integer recovery remain distinct obligations.
