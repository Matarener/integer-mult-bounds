# Owner-cover supply of the two missing literal binary gates

Chris R / Clear1nsight, with substantial OpenAI Codex assistance. Apache-2.0.
The counting argument was developed jointly with the orchestrator. The source
Gauss–Jordan compiler, orthogonal-cover indexing and physical monomial engine
are inherited work; their implementation is not new here.

## Claim and exact interface

Let `g` run once through the authenticated `OrthogonalCover(73)`, of cardinality
`Gamma`. Let `W(g)` be the literal `binary_word` on `matrix_rows=g, offset=0`.
The coefficient, numerical width and packet data do not enter this fixed
finite-control compiler. Then each of the following strict bounds holds:

```
sum_g multiplicity(("add", 6, 8), W(g)) > Gamma / 32,
sum_g multiplicity(("add", 8, 6), W(g)) > Gamma / 32.
```

Consequently, 736 appearances of this owner word per owner supply more than
`23 Gamma` gates of **each** named type. Even the 672 service appearances alone
supply more than `21 Gamma` of each. This covers the separate histogram deficits
`4 Gamma add(6,8)` and `Gamma add(8,6)` with room to spare. Inverse execution only
reverses the literal word and preserves these multiplicities.

The assertion is an aggregate statement across the complete cover. The identity
owner has an empty word and is an explicit control against the false assertion
that every owner supplies either gate. This lemma does not itself assert that
arbitrary gate positions have equal physical cost. Its use in the signed action
bound requires the surrounding source-derived matching theorem: same ordered
`(kind,target,source)` and complete local packet geometry, including all
spectators, widths, markers and operation boundary states. It supplies no
axis-invariance shortcut and no finite-control or historical-space cancellation.

## Source points and inherited finite-group fact

The authenticated #4172 nested closure retains:

* `research/physical-complex-controller/cover.py`, `group_orders`,
  `OrthogonalCover._setup`, and its original `PROOF.md` section “Cover and
  complete global dispatch”;
* `research/physical-gaussian-leaf/inputs/pr3087.tar:phase_recipe.py`, whose
  `Recipe` uses `reference.binary_word`;
* that archive's retained physical-Compact/reference lineage,
  `inputs/pr3055.tar -> inputs/pr2250.tar -> monomial.py:binary_word`;
* `monomial_engine.py:run`, which visits `reversed(recipe.word)` for inverse
  execution and the original word otherwise.

The source reduction uses the first row `p >= j` with bit `j` set, emits a
three-add row swap if needed, then adds pivot row `j` into **every** other row
whose bit `j` is set. The returned word reverses the complete reduction. No gate
multiplicity changes under that reversal.

We retain the source cover invariant: any orthonormal prefix whose span does
not contain the ambient characteristic vector has a nonalternating orthogonal
complement and extends to an orthonormal basis. With `t` coordinates remaining,
the number of completions is `|O(t,2)|`, with

```
|O(t,2)| = product_{k=1..t} (2^(k-1) - [k>1 and k odd]).
```

This is the original source's indexing/extension theorem, not an assumption that
an arbitrary orthogonal prefix extends. Excluding the characteristic vector is
essential. The new counting argument below enforces that exclusion explicitly.

## Every nine-by-nine head has substantial mass

Fix any binary `9 x 9` matrix `A` as the first nine coordinates of the first nine
rows of a candidate 73-dimensional orthogonal matrix. Write those nine rows as
`(a_i, t_i)`, with `t_i` of length 64, and write `omega` for the all-one vector of
length 64. We count only choices for which

```
omega, t_0, ..., t_8
```

are linearly independent. At step `j`, the already chosen `j` tails and `omega`
are independent. The constraints on `t_j` are

```
t_j · t_i = delta_ij + a_j · a_i        (0 <= i < j),
t_j · omega = 1 + a_j · a_j.
```

There are `j+1` independent binary linear equations, so exactly
`2^(63-j)` solutions. At most `2^(j+1)` of them lie in the span of the previous
tails and `omega`. Discard those, leaving at least

```
L_j = 2^(63-j) - 2^(j+1),       j = 0,...,8.
```

Every resulting full nine-row frame is orthonormal. Its span does not contain
the 73-dimensional all-one vector, because its 64-coordinate tail would then
express `omega` in the span of the tails. It therefore has exactly `|O(64,2)|`
completions by the inherited source cover theorem. Different tail choices and
completions produce different matrices.

Thus the exact probability for this fixed head under the uniform cover is at
least

```
p_head >= (product L_j) |O(64,2)| / |O(73,2)|.
```

Also `|O(73,2)| / |O(64,2)| <= 2^612`, whereas

```
product L_j = 2^531 product_{j=0..8}(1 - 2^(2j-62)).
```

The product of the last nine factors exceeds one half (for example their
omitted fractions sum to less than `9 * 2^-46 < 1/2`). Hence

```
p_head > 2^-82 = (1/2) * 2^-81.
```

This is a pointwise counting bound for **every** head, not a simulation,
independence assertion about orthogonal entries, or probabilistic heuristic.
For any set of nine-by-nine heads its uniform-cover mass is therefore at least
half its ordinary independent-bit mass. `gate_cover.py` also evaluates the
stronger exact rational bound, without enumerating Gamma.

## Heads that force the named gates

First consider `add(6,8)`. Require that the leading `8 x 8` block `A_8` is
invertible. The first eight source pivot steps then find their pivots within
rows 0 through 7: internal row swaps are allowed, but no row outside that block
is chosen. After those steps, its column-eight entries in the top eight rows
are `A_8^-1 b`. Its row-eight, column-eight entry is the Schur complement
`s = d + c A_8^-1 b`. Require both coordinate six of `A_8^-1 b` and `s` to be
one. Then source step eight has pivot row eight and emits `add(6,8)`.

For a uniform independent-bit nine-by-nine head, invertibility of `A_8` has
probability `product_{i=1..8}(1-2^-i) > 1/4`. Conditional on `A_8`, the first
condition has probability one half because `b` is uniform. Conditional on
`A_8,b,c`, the second has probability one half because `d` is an independent
bit. This forcing event therefore has independent-bit mass greater than
`1/16` and orthogonal-cover mass greater than `1/32`.

For `add(8,6)`, instead require invertibility of the leading `6 x 6` block.
After the first six pivots, require the transformed entries `(6,6)` and `(8,6)`
both to be one. Each is a distinct original free diagonal/column entry plus a
term fixed by the leading block and corresponding first-six row entries;
they are independent uniform bits conditional on those data. Source step six
has pivot six and emits `add(8,6)`. The same calculation, using
`product_{i=1..6}(1-2^-i) > 1/4`, gives cover mass greater than `1/32`.

Each forcing event guarantees at least one named gate; additional occurrences
only increase the available supply. Applying the pointwise head bound and
summing over the complete cover proves the two aggregate claims.

## Executable evidence and boundaries

`gate_cover.certificate()` uses exact integers and `Fraction`; it checks the
source group orders, tail counts, head-density bound, event bound, and both
736-occurrence and service-only inequalities. Its exact lower probabilities
are approximately 0.07247977946 and 0.07333695889, but all acceptance decisions
use rational comparisons. The coarse `1/32` bound is deliberately retained in
the theorem for readability.

`gate_cover.source_checks(cohort)` requires an already authenticated cold source
cohort. It composes explicit even-weight orthogonal transvections to obtain
actual 73-dimensional orthogonal witnesses, checks their head conditions,
executes the retained `binary_word`, and confirms both literal gates and
inverse-word multiplicity. The identity owner rejects a universal per-owner
interpretation. These finite examples check the source interface; the tail
count and leading-block arguments carry the quantified cover claim.

This is an offline cost proof certificate. Its matrix arithmetic, rational
counts and witness generation are not proposed machine operations, a runtime
sampler, or free physical preparation. The surrounding package must charge the
actual owner monomial executions and preserve the complete comparison's
admission, finite-control and resource boundaries.
