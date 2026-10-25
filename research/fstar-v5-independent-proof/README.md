# A three-line obstruction gives a sharp four-line box floor

**Scoped proof with an independently checked finite premise.** For an exact
three-total rational decoder with nonzero diagonal and `tau(t) >= 1` on every
line, **`box >= 3` whenever `v >= 4`**. A four-line example attains three.
This recovers PR3031's five-line floor and strengthens the previously stated
four-line floor of two. It does not prove `box >= floor(2v/3)` at larger v.

The proof independently reconstructs the raw triple classification already
represented by PR3105's seven joint orbits, then derives its arbitrary-size
consequence. It replaces PR3031's anchor screen and six scans of `2^20`
zero-arc sets with an explicit two-bit witness. The exceptional triples are
credited to the predecessors, not claimed as a new discovery.

## Exact statement and source boundary

For each line t let `a0(t), b0(t)` be three-bit masks with nonempty intersection.
Let Z be a directed set of distinct-line pairs satisfying

```text
(t,s) in Z  =>  dot_F2(a0(t), b0(s)) = 0.                 (SG)
```

An ordered kept set admits labels `a(t) subset a0(t)`, `b(t) subset b0(t)`
when its diagonal binary dots are one and `dot(a(t),b(s))=0` for every
forward pair in Z. `box` is the maximum number kept. Reverse pairs impose
constraints only if they are forward in the chosen order. Unkept labels
do not enter the constraints.

**Combinatorial theorem.** For `v >= 3`, `box < 3` holds exactly when:

1. There is a two-bit mask r such that all line types belong to
   `{(r,r),(r,7)}`, or all belong to `{(r,r),(7,r)}`; and
2. Z contains every directed off-diagonal pair.

Consequently, if Z is the actual zero set of a matrix M with nonzero diagonal,
`box < 3` forces M to be diagonal. For `M=P Q^T` with three columns,
`rank(M)<=3`; at `v>=4` this contradicts the diagonal rank v.

This theorem uses the same box interface as the frozen PR2914 engine's
`anchor_data`, `scope_identity`, `replay_witness` and `in_box`. The rational
normalization implication below is proved algebraically; it does not rely on
the engine's finite sentinel or on bounded random decoder generation.

## The finite triple premise

There are 37 ordered raw mask pairs `(a0,b0)` with nonempty intersection.
Line permutation leaves `box` unchanged, so the complete triple domain has
`C(39,3)=9139` multisets. Repeated types are allowed. Use the maximal envelope
`Z_even` containing every even-parity cross pair; any Z satisfying (SG) is
a subset, so an envelope witness remains valid for Z.

Exactly **21** envelope triples have no kept-three witness. They are precisely
the coherent families in condition 1 above, with three lines. For each of
the three choices of r there are four multiplicities using `(r,r),(r,7)`
and four using `(r,r),(7,r)`, with the constant `(r,r)` triple counted twice:
`3*(4+4-1)=21`. This is the raw-coordinate form of PR3105's seven orbits.

Two independent engines establish the premise:

- `verify.py` lists every diagonal-valid pair of submasks, tries all six line
  orders, and joins their exact forward-constraint compatibility bitsets.
  Every positive result is replayed against the box definition.
- `independent.py` enumerates target labels first. For each source row it
  solves the diagonal and applicable forward equations by binary Gaussian
  elimination. Once targets are fixed, those row systems are independent.
  It neither imports the first engine nor executes predecessor code.

Both compare their complete forbidden lists with the stated formula. The
first also checks all **749,398** five-line multisets without pruning;
the second extends only prefixes whose every positional triple is forbidden.
Both recover exactly the same **33** families and the first compares them
with PR3031's frozen receipt using raw masks, not a per-line quotient.
These five-line checks audit the prior result; they are unnecessary for the
arbitrary-v deduction below. [RESULT.json](RESULT.json) retains the lists.

## From triples to arbitrary v

Suppose `box < 3`. Every triple of distinct line positions is infeasible,
including triples whose types coincide. Since actual Z is contained in
`Z_even`, all these triples occur in the 21-family classification.

Each type appearing there has tied intersection exactly one two-bit mask r.
Fix two line positions. Every third position forms a forbidden triple with
them, so all positions have the same r. The special types `(r,7)` and `(7,r)`
cannot coexist: together with any third position they would give a triple
outside the list. Thus the entire family satisfies condition 1.

Now suppose some directed pair `(x,y)` is absent from Z. Choose any third
position z, and write r as `{i,j}`. In order `(x,y,z)`, use the labels

```text
a(x)=b(x)=a(y)=b(y)=e_i,      a(z)=b(z)=e_j.
```

All are inside their anchors. The diagonal dots are one. The dots from x
and y into z are zero; the only nonzero forward cross dot is `(x,y)`, which
is unconstrained. This keeps three, a contradiction. Hence Z is complete.
The implemented witness is checked for all 33 five-line families, all 20
missing directed pairs and all three choices of third line: **1,980** cases.

Conversely, in a coherent family one label side is confined to the same two
bits. Any binary fitting matrix K therefore has rank at most two. If Z is
complete, a kept triple in its chosen order would have a triangular principal
matrix with unit diagonal, of rank three. None exists. Any two lines can be
kept using the two distinct bits, so these cases have `box=2` exactly.

## Why rational decoder zeros satisfy (SG)

For each nondegenerate total j, put
`m_j=min_t v2(P_tj)`, `n_j=min_t v2(Q_tj)` over nonzero entries, and
`gamma=min_j(m_j+n_j)`. Ignore a total with an identically zero factor; its
anchor bits and its contribution are zero. The normalized factors

```text
P'_tj = 2^(-m_j) P_tj,       Q'_sj = 2^(m_j-gamma) Q_sj
```

are rational 2-adic integers, because `m_j+n_j>=gamma`. Their residues are
exactly the anchor bits. Reducing their dot product modulo two gives

```text
dot_F2(a0(t),b0(s)) = (2^(-gamma) M_ts) mod 2.
```

A zero matrix entry therefore gives an even anchor dot. Moreover a summand
has valuation gamma precisely when both anchor bits are one, so the source's
`tau(t)` equals the size of the tied intersection. Nonzero diagonal guarantees
at least one nondegenerate total. This argument handles signs, denominators
and cancellations; no positivity or coefficient-search cap is used.

## Sharp four-line example and failed hypotheses

Duplicate the first line of Aaron Wang's PR2978 core, also retained in
PR3031's `extend_core`. Take ordinary transpose and

```text
P = [(-1,-3, 0), (-1,-3, 0), (1,-1,-2), (3, 3,3)]
Q = [( 1,-3, 2), ( 1,-3, 2), (3,-1,-2), (3,-1,2)].
M = diag-block(8 J_2, 8, 12).
```

Here `rank(M)=3`, `gamma=0`, `a0=(3,3,3,7)`, `b0=(3,3,3,3)`, and every
tau is two. The missing arc between the duplicate lines supplies the kept
triple above. If all four lines were kept, restrict K to either duplicate
and the two singleton blocks. All six actual directed pairs among these
three are zeros of M, so the induced ordered matrix is triangular with
unit diagonal and rank three. But all target labels have only two bits,
forcing `rank(K)<=2`. Thus **`box=3` exactly**. Literal submask enumeration
independently verifies this value.

The unduplicated three-line core has nonzero diagonal, rank three and box
two, so the threshold `v>=4` is necessary. Further controls exhibit a
four-line rank-one rational decoder with an empty tied mask and box one,
and an abstract rank-four diagonal matrix satisfying (SG) with box two.
They show why the tied-mask and rank hypotheses cannot be discarded.

## Reproduce, attribution and limitations

From the repository root:

```sh
python3 -B scripts/research_package.py --package research/fstar-v5-independent-proof --check-only
python3.12 -B scripts/research_package.py --package research/fstar-v5-independent-proof
```

The registered replay authenticates the retained sources, runs both complete
classifications and the independent controls under `-I -O -Werror -B`.
It uses only the standard library. See [VERIFY.json](VERIFY.json) and
[SOURCES.json](SOURCES.json) for exact inputs, commits, blobs and SHA-256 pins.
All three registered commands pass on CPython 3.12.15, including thirteen
control groups. The replay also passes after rebase onto canonical main
`b0186c6b75280913969f101c169fe3fb07afd137`; publication bytes and declared
source-history availability pass the repository preflight.

Credit Aaron Wang/navinor's PR2869 normalization, PR2914 box engine,
PR2978 rational core, PR3012 reductions and PR3031 five-line proof; and
Arham Tahir/Arham-Tahir64's PR3105 complete joint triple classification.
The older seven-orbit result already implies the diagonal corollary by
restriction. This package makes that consequence explicit, checks the finite
premise with two new raw-coordinate algorithms, and supplies the sharp
four-line example. It does not claim to discover the seven orbits.
Predecessor bytes remain unchanged and are retained solely for provenance
and source comparison. New work is Apache-2.0, by Sagar Thakrar with
substantial OpenAI Codex assistance. Separate AI executions are not independent
human or proof-assistant review.

This is an algebraic box-interface result. No physical COPY program, recursive
invoice, supplier admission, selected cold replay or kappa improvement is
claimed. It does not audit PR3031's unrelated realization-search remainder.
The selected frontier is unchanged.

## Open next questions

The next missing F-star threshold remains `box>=4` at six lines under the
same hypotheses. The present three-line obstruction does not imply it:
kept triples cannot simply be combined because cross constraints remain.
Any further construction or larger census needs its own named decision and
family budget. A useful first step is a proof-level characterization of
kept-four obstructions with explicit cross constraints; no such search is
included here. No additional follow-up is needed to close this five-line audit.
