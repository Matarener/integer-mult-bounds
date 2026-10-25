# Flag obstruction for span six with one dirty auxiliary

**Partial lower bound.** Selected κ stays `0.001672660197076918`. The selected
record is unchanged.

In the abelian rank-one model of
[PR #468](https://github.com/CrocSwap/integer-mult-bounds/pull/468), three
invertible rational `3×3` targets and one dirty auxiliary register cannot be
reached by eight nonzero calls when either of the following holds.

- The calls are simultaneously permutation-triangular. This exclusion is uniform
  in the frame span, and it applies to every shorter word as well.
- The frame span is six and the occurring noncoordinate projectors share a
  complete flag of `F₂⁴`.

Nine coordinate calls still realize the three targets, so eight is sharp for
the permutation-triangular class. The only span-six words left open are those
whose occurring noncoordinate set is one of 72 flagless triples, one
`GL(4,2)` orbit, and those whose off-diagonal pattern is one of 12 cyclic
lines and whose cube relations span the full relation lattice.

Task card: `bit-new-register-model`, scope refined. The changed hypothesis is
the register count in
[`research/bit-dirty-auxiliary-registers`](../bit-dirty-auxiliary-registers/README.md)
§6: three data registers, eight calls, one dirty auxiliary. That note excludes
frame spans at most three and at least seven for any number of dirty
auxiliaries. Spans four, five and six remained, and its engine cannot enumerate
`120⁸` words. A parallel span-four classification, Discussion #1166 comment
19056267, reduces span four to one five-call `2×2` shape and explicitly leaves
spans five and six open. This package redoes the four-register pattern-span
census and closes the flagged part of span six.

## 1. Model

Let `G = (Q^{3×3}, +)`, written multiplicatively by `[A][B] = [A+B]`, and work
in `M₄(F₂[G])`. A paid call is

```text
D_N([A]) = I + ([A] - 1) N,    rank_Q A = 1,    N = xy^T,    y^T x = 1,
```

with `x, y ∈ F₂⁴`. There are four scalar registers. Registers `0, 1, 2` are
data registers and register `3` is a dirty auxiliary: its input is arbitrary
and its endpoint is unconstrained. A word of nonzero calls succeeds when the
product equals `diag([C₀], [C₁], [C₂], [C₃])` with `C₀, C₁, C₂` invertible.
Zero frames are identities and are deleted. Free scalar mixings are absorbed
into `N`, as in PR #468 §1. No triangularity is imposed on the targets.

The predecessor’s Lemma 2 says that fewer than `mW = 9` calls forces frame
span at least `m + 1 = 4`. Its Lemma 1, applied through the corollary in that
note, forces the relation rank to be at least 2, hence span at most 6. The
remaining span-six case is relation rank exactly 2.

## 2. Cube rank at most one

Let `L ⊂ Z⁸` be the saturated relation lattice of the eight frames, of rank 2.
A cube vector is an element of `L ∩ {-1,0,1}⁸`. In the expansion of
`∏(I + (tⱼ - 1) Nⱼ)`, two subset monomials become the same element of `F₂[H]`
precisely when their exponent difference lies in `L`. Every such difference
is a cube vector. Extra relations with an entry of absolute value at least 2
do not identify any pair of subset monomials.

If the only cube vector is `0`, the subset sums are distinct, every
off-diagonal entry vanishes as a multilinear polynomial, and differentiation
at `1` makes each `Nⱼ` diagonal. The four diagonal blocks are disjoint sums of
rank-one frames, so their ranks sum to at most 8.

If the cube vectors span a one-dimensional space, their saturated hull is
`Zu` with `u` itself a cube vector: a primitive generator with an entry of
absolute value at least 2 has no nonzero cube multiple. The only subset
collisions are translation by `u`. The proof of Lemma 1 in the
dirty-auxiliary note uses only this one cube relation and holds for every
register count. It supplies pairwise disjoint subset sums for the four
diagonal blocks, and the ranks again sum to at most 8.

Three invertible blocks would require rank sum at least 9. Both branches are
impossible. The flag census is not an input to this step.

## 3. Saturated cube basis

Now the cube vectors span `L` over `Q`. Take independent cube vectors `r, s`.
If their reductions modulo 2 are independent, some `2×2` minor is odd. A cube
minor has absolute value at most 2, so that minor is `±1` and `r, s` is a
saturated `Z`-basis of `L`. If the reductions agree and are nonzero, replace
the pair by `(r+s)/2` and `(r-s)/2`. Independence of `r, s` makes both halves
nonzero; they are cube vectors with disjoint supports and a unit minor, so
again they basis `L`. A cube vector cannot reduce to `0` modulo 2 unless it
is `0`. This is the same arithmetic as PR #468 §5.2 and does not use the
register count. The resulting basis still has entries in `{-1,0,1}` and is
independent modulo 2.

Write `yⱼ = tⱼ - 1` and `P = ∏(I + yⱼ Nⱼ)`. The degree-one term is
`∑ yⱼ Nⱼ`. Since `L` is saturated of rank 2, the kernel of `F₂⁸ → H/2H` is
spanned by the mod-2 reductions of the basis. The product is diagonal, so
every off-diagonal graded symbol vanishes on `H/2H`. The degree-one
off-diagonal symbol therefore vanishes on the common kernel of the two
coordinate forms, and

```text
off(Nⱼ) = (rⱼ mod 2) B + (sⱼ mod 2) C
```

for two fixed off-diagonal matrices `B, C`. The off-diagonal patterns of the
word span an `F₂`-space of dimension at most 2.

## 4. Permutation-triangular words

Suppose there is a coordinate order in which every projector is upper
triangular, and the word has length `s ≤ 8`. In that order the product is
upper triangular. Over a commutative ring the diagonal of a product of upper
triangular matrices is the product of the diagonals.

Each factor has exactly one diagonal `1`. Indeed `trace(N) = yᵀx = 1`. If
two diagonal entries in this order were `1`, both basis vectors would lie in
the supports of `x` and of `y`, and the backward edge between them would be
`1`, contradicting triangularity. Each call therefore contributes its frame
to exactly one output register. A coordinate permutation preserves
diagonality, so the four blocks `Cᵢ` are a permutation of disjoint subset
sums of the frames. Rank subadditivity gives

```text
rank C₀ + rank C₁ + rank C₂ + rank C₃ ≤ s ≤ 8.
```

The auxiliary rank is nonnegative and each data block of an invertible `3×3`
matrix has rank 3, so the left side is at least 9. This is independent of
the frame span and of any further linear relation among the frames.

The bound is sharp. The three matrix units `E₀₀, E₁₁, E₂₂` are rank one and
sum to `I₃`. Nine coordinate calls, three on each data register and none on
the auxiliary, give `diag([I₃], [I₃], [I₃], [0])`. Every assignment of eight
coordinate calls leaves some data register with at most two frames. The same
pigeonhole is the coordinate case of the open
[PR #3537](https://github.com/CrocSwap/integer-mult-bounds/pull/3537); the
argument here extends it from the four coordinate idempotents to every
simultaneously permutation-triangular family.

Splitting `D_N([A]) = D_N([A/2]) D_N([A/2])` preserves the projector multiset
and the span. A shorter permutation-triangular word is already covered by the
length bound, without splitting.

## 5. Complete flags at span six

It remains to treat span exactly six when the cube rank is two and `B, C`
are independent, so the pattern dimension is two. A zero pattern then forces
`rⱼ ≡ sⱼ ≡ 0 (mod 2)`. Entries lie in `{-1,0,1}`, so `rⱼ = sⱼ = 0` as
integers. Both relations are supported on the nonzero-pattern calls `S`. The
complement `T` is the set of coordinate-projector calls, and
`H = H_S ⊕ Z^T`.

Set every `T` variable equal to `1`. Those factors become `I`, and the
remaining product of the `S` factors equals `diag([C₀ˢ], …, [C₃ˢ])`, where
`Cᵢˢ` is the `H_S`-component of `Cᵢ`. The occurring noncoordinate projectors
are exactly the `S` factors. Assume they share a complete flag of `F₂⁴`.
Conjugation by a change of basis adapted to that flag is invertible over
`F₂` and replaces each `N` by an upper triangular rank-one idempotent. The
same one-diagonal count holds in the new basis: it was proved from
`trace = 1` and the absence of a backward edge. The conjugated product is
upper triangular, its diagonal monomials are disjoint subset products of the
`S` frames, and its characteristic polynomial equals that of the diagonal
matrix of the `Cᵢˢ`.

`F₂[H_S]` is an integral domain. A monic polynomial over an integral domain
has at most one factorization into monic linear factors, because a root in
the domain splits off by monic division and a product of nonzero elements is
nonzero. The multisets `{Cᵢˢ}` and the disjoint subset sums therefore agree.
Rank subadditivity gives `∑ᵢ rank Cᵢˢ ≤ |S|`.

Each single `T` frame is isolated by setting every other variable to `1`.
The surviving factor is one coordinate projector, so that frame lies on
exactly one diagonal block. Hence `∑ᵢ rank Cᵢᵀ ≤ |T|`. The splitting of `H`
writes `Cᵢ = Cᵢˢ + Cᵢᵀ` as matrices, and

```text
∑ᵢ rank Cᵢ ≤ |S| + |T| = 8 < 9.
```

Coordinate projectors need not preserve the flag. They are removed before
the triangularization. That is why the argument reaches pattern spans that
have a complete flag and no coordinate order.

A shorter span-six word in the same pattern class splits to length 8 without
changing the occurring projectors or the span. The length-8 case already
covers it.

## 6. Finite classification

The verifier enumerates the idempotents in two ways: outer products `xyᵀ`
with `yᵀx = 1`, and a scan of all `2¹⁶` binary `4×4` matrices for
`N² = N` and rank 1. Both lists are the same set of 120 matrices.

| Quantity | Count |
| --- | ---: |
| Rank-one idempotents | 120 |
| Off-diagonal patterns, including zero | 105 |
| Nonzero patterns | 104 |
| Acyclic patterns, including zero | 93 |
| Cyclic patterns | 12 |
| Nonzero patterns with one lift / two lifts | 92 / 12 |
| Realizable two-dimensional pattern spans | 4964 |
| Spans in which all three nonzero patterns occur | 196 |
| Of those, common topological order / cyclic union | 176 / 20 |
| Spans whose noncoordinate pool has a complete flag | 4892 |
| Flagless spans | 72 |
| Flagged spans that are permutation-triangular | 1748 |

These pattern counts agree with
[`research/two-relation-pattern-census-seed52`](../two-relation-pattern-census-seed52/README.md):
105 patterns including zero, 93 acyclic including zero, 12 cyclic, 196 full
planes, 176 with a common topological order and 20 with cyclic union. That
census answers a different question, four rank-four targets in fifteen calls.
The complete-flag column is new. All 196 full planes are flagged, including
the 20 cyclic-union planes, so those 20 fall under §5 at span six even though
they have no coordinate order.

Every flagless span is partial: exactly two of its three nonzero vectors are
realized, by three projectors, with fiber sizes 2 and 1. Every proper subset
has a complete flag. The same 72 pools are exactly the pools that fail the
weaker line-inside-plane test, so requiring a hyperplane does not remove any
further span. The 12 cyclic patterns each have one projector. That projector
is triangularizable, and the verifier checks one diagonal `1` in every adapted
basis of every preserved flag (10,080 pairs). None of those 12 shares a
complete flag with all four coordinate projectors. Every acyclic pattern is
permutation-triangular together with the coordinate projectors, so §4 applies
to it.

The 72 triples are one orbit under `GL(4,2)`. The 24 permutation matrices and
the 12 transvections generate a group of order 20,160, which is `|GL(4,2)|`.
Conjugation of a minimum-weight triple fills an orbit of 10,080 triples and
meets every flagless pool. The minimum-weight representative, with column 0
written on the left, is

```text
X = e₀(e₀+e₁)ᵀ       = 1100/0000/0000/0000
Y = (e₀+e₁)e₁ᵀ       = 0100/0100/0000/0000
Z = (e₁+e₂)(e₀+e₂)ᵀ  = 0000/1010/1010/0000
```

`X` and `Y` share the single off-diagonal edge `(0,1)` and differ on the
diagonal. A one-bit tamper of `X` leaves the rank-one idempotents.

Consequently, at span six, after §2 and §4, the only words not excluded by §5
are those whose occurring noncoordinate projectors are exactly one of these
72 triples, and those whose pattern space is one of the 12 cyclic lines.
Span five remains open outside the permutation-triangular class. Span four is
the parallel classification cited above; §4 still forbids its
permutation-triangular words. Clean ancillas, other paid primitives,
nonabelian frames and free address maps stay outside the model, as in the
predecessor.

## 7. Reproduction

From the repository root, with Python 3.12 and the standard library:

```sh
python3 -B research/auxiliary-span-six-flag/verify.py
python3 scripts/research_package.py --package research/auxiliary-span-six-flag --check-only
python3.12 scripts/research_package.py --package research/auxiliary-span-six-flag
```

The verifier prints `PASS_AUXILIARY_SPAN_SIX_FLAG`. It checks the two
projector enumerations, the counts in the table, the pivot property, the
generation of `GL(4,2)`, the normal-form orbit, the eight-call and nine-call
coordinate pigeonholes, the sum of three matrix units to `I₃`, the cyclic
versus coordinate flag separation, and the one-bit tamper.

Checks not run: the internal acyclic and common-projector cases of the cited
Lemma 1, any proof assistant, the predecessor’s C++ engine, and any search of
spans four or five or of the 72 triples. The 80-minute auxiliary census was
not repeated.

## Open next questions

1. **Can the normal-form triple `X, Y, Z`, interleaved with the four
   coordinate projectors, realize three invertible `3×3` blocks in eight
   calls at frame span six?** These 72 triples are one `GL(4,2)` orbit and
   are the only two-dimensional spans with no common complete flag, so one
   calculation would close every two-dimensional span-six word. First step:
   repeat the degree-two bookkeeping of PR #468 §5.1 on this seven-matrix
   alphabet after transporting the word to the normal form. Blocker: the
   transport of a diagonal target is not diagonal, and `7⁸` ordered words are
   outside this verifier. Lemma 1 does not apply at relation rank 2.

2. **Can one of the 12 cyclic projectors, interleaved with coordinate
   projectors, meet the same bound at span six when the cube rank is two?**
   Cube rank at most one is already impossible. Each cyclic projector is
   triangular in some flag basis and in no basis that all four coordinate
   projectors preserve. First step: collapse consecutive copies by
   `(I+(a-1)N)(I+(b-1)N) = I+(ab-1)N` and classify the resulting words in
   that five-matrix alphabet. Blocker: in pattern dimension one a zero
   off-diagonal pattern need not kill both cube-basis coordinates, so the
   relation support can meet the coordinate calls.

3. **Does span five admit an eight-call word outside the
   permutation-triangular class?** Span four is already reduced by the
   parallel note in Discussion #1166 comment 19056267 to one five-call `2×2`
   shape, and §4 removes permutation-triangular words at every span. First
   step: extend the span-five scalar catalogue of PR #468 §7 from 28
   projectors to these 120, starting at pattern dimension three. Blocker:
   relation rank three no longer caps the pattern space at dimension two, and
   `120⁸` enumeration does not fit this verifier.

## Credit

The model, the Laurent expansion and the three-register span-six argument are
Ali Romman’s
[PR #468](https://github.com/CrocSwap/integer-mult-bounds/pull/468),
`research/bit-three-register-lower-bound/` at blob
`25e41c370c101a33a6deb978de08b03ed7539b79`. That work credits eumemic’s PR #288
and huxint’s PR #203. David Govea’s open PR #720 is the three-register form of
the disjoint-subset lemma and is not a dependency. Lemma 1, Lemma 2 and the
span-six handoff are waynenilsen’s
`research/bit-dirty-auxiliary-registers/` (merged as PR #1882). The pattern
counts 105 / 93 / 12 / 196 / 176 / 20 were recomputed here and agree with
`research/two-relation-pattern-census-seed52/` (PR #1733). The coordinate
eight-call pigeonhole is the special case already stated by open PR #3537,
which explicitly leaves the 120-projector classification undone. The span-four
shape theorem posted in Discussion #1166 comment 19056267 (fork package
`research/bit-span4-auxiliary-structure`) is parallel work on the same handoff
and is cited above; it leaves span six open.

Prepared by unpaidmoon with substantial assistance from Grok 4.7 (xAI), which
drafted the classification, the argument, the verifier and this note. No
independent human review is claimed. New work is Apache-2.0.
