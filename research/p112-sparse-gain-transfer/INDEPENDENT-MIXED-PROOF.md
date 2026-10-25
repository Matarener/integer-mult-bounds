# Independent audit: mixed two-port factors transfer in the strict mask

20 October 2026. This independently audits the mixed-orientation extension of
the uniform two-port result in this package. No experiment, coefficient grid,
or assumption that the two orientation subsums separately vanish at forbidden
positions is used. In particular the proof permits cancellation of forbidden
entries between those subsums.

## Statement and precise output

Let M be any rational square matrix with diagonal one and a prescribed set of
off-diagonal zero entries. The other off-diagonal positions are free. Suppose

    M = sum_t u_t v_t^T,

and each term has either at most two nonzero scalar coordinates in u_t or at
most two in v_t. Orient each term once: put it in A when its source u_t is
two-port, or in B when its reader v_t is two-port. A term satisfying both may
be assigned arbitrarily. Zero terms can be deleted.

There is a characteristic-two factorization of another strict fit M' with the
same required diagonal and forbidden zeros, using the same term slots and
termwise subsets of the original source and reader supports. The free entries
may change. It is not a support-preserving rational normalization and does not
promise the old exact endpoint.

For the authenticated P112 physical cover, the usual whole-group expansion of
every such characteristic-two strict fit is I334. Hence its total whole-group
binary-rank invoice is at least334. Termwise support deletion cannot increase
that invoice, so the original rational mixed-orientation invoice is also at
least334, for every rank and factor count.

## 1. A linear problem on matrix positions

Freeze u_t for A and v_t for B. Treat each originally nonzero entry of v_t
(t in A), and each originally nonzero entry of u_t (t in B), as an independent
variable; originally zero entries stay zero. The equation for M is linear in
these variables. Its coefficient columns are supported on at most two matrix
positions:

* An A variable at reader coordinate q contributes u_t at positions (p,q).
* A B variable at source coordinate p contributes v_t at positions (p,q).

Thus this coefficient matrix is a gain-incidence matrix on vertices (p,q),
with links for two-position columns and grounded units for one-position
columns. Choose a column basis from these originally active variables that
spans the old M, and set all other variables to zero. This choice is made over
the original rational field; it is not a claim that the graph's full edge set
is independent.

In each connected component, an independent gain-incidence set is a tree, a
tree with one grounded unit, or a unicycle whose gain holonomy is not one.
Indeed a connected link graph has at least v-1 edges and independence permits
at most v columns. A grounded component must have exactly one unit and tree
links; an ungrounded v-edge component is a unicycle, and elimination around
that cycle gives independence precisely when its holonomy is not one.
Parallel links and two-edge cycles are included. A single unit vertex is a
grounded tree. A tree's one-dimensional left kernel has a nonzero coordinate
at every vertex, by propagation along nonzero-gain links.

## 2. Repeated gains introduce no hidden obstruction

For every original frozen two-port factor, order its two scalar coordinates
once and normalize its entries to `(1,-g_t)` over Q. Its first nonzero scalar
is absorbed in all of that term's variable coefficients. The same orientation
is used in every vectorized copy of that frozen factor.

Now work over the infinite field F2(z,{x_t}), with one algebraically independent
gain variable x_t per original frozen factor and a spare indeterminate z.
Replace `(1,-g_t)` by `(1,x_t)` in that factor. Units can be normalized to one.
Repeated vectorized copies reuse x_t; they are not given independent values.

Every oriented cycle holonomy is a Laurent monomial in the x_t. If this
monomial were identically one, substituting x_t=g_t into the same Laurent word
over Q would make the old holonomy one. It therefore cannot be identically one
for any unbalanced unicycle in the selected old basis. This argument includes
the signs: the original relation gain is g_t, because the normalized column
was `(1,-g_t)`. Traversing a link backwards uses the reciprocal gain, in either
field. An exponent-zero word has no leftover odd-cycle sign. Consequently all
selected unicycles remain unbalanced, and their coefficient components remain
full row rank over the new field. Grounded trees are full row rank over every
field. Selected tree components retain exactly one nonzero-everywhere left
annihilator.

## 3. Construct a strict output separately on each component

Let D be the diagonal matrix positions in a selected component.

If the component is full row rank, prescribe value one at every vertex in D
and zero at all other vertices. This is recoverable within that component.

If it is a tree, let z_v be its nonzero-everywhere left annihilator.

* With D empty, prescribe zero everywhere.
* With D consisting of one vertex d, the old component output cannot have
  been nonzero only at d: its old annihilator would contradict the old
  diagonal value one. Thus some other vertex b in the component has a nonzero
  old output. It is necessarily an allowed free position, because every
  forbidden entry of the complete old M is zero. Prescribe value one at d,
  value `-z_d/z_b` at b, and zero elsewhere. This lies in the new tree's image.
* With k>=2 diagonal vertices, choose nonzero values w_d so that
  `sum_d z_d w_d=0`, and prescribe zero outside D. Such values always exist over
  the infinite characteristic-two field. For even k, pair equal nonzero
  contributions; for odd k>=3, use contributions `1,z,1+z` and pairs for the
  rest. Divide each contribution by its nonzero z_d.

Components are disjoint, so all these assignments are simultaneous. Each
diagonal vertex is present in the selected basis's vertex union, since the old
M has nonzero output there. The resulting matrix has a nonzero value at every
diagonal position and zero at every forbidden position. Solving each component
uses only the selected original active variables. Hence each unfrozen factor
support shrinks; each frozen factor retains its support.

Finally multiply the resulting matrix on the left by the diagonal matrix of
inverse diagonal entries. Apply that same row scaling to every query/source
factor in both A and B. All source and reader supports remain unchanged by
this scaling. This gives diagonal one and preserves all
forbidden zeros, proving the claimed strict fit M'. Equivalently the P112
expanded matrix already had full rank334 before this normalization, since its
expanded diagonal entries were nonzero.

The essential distinction from the failed separate-subsum strategy is that
the graph's vertices are positions of the complete matrix M. Its old component
output already incorporates every cross-orientation cancellation, so the free
witness in the one-diagonal tree case is certified using M itself.

### Independently audited zero-pattern refinement

The same proof permits D to be all old nonzero entries in each selected
component. An ungrounded tree then has either zero or at least two such
positions; one is impossible by the old annihilator. Assign nonzero values
to all positions in D satisfying the new tree relation, or ones in a
full-rank component, and zero elsewhere. This preserves the entire matrix
zero/nonzero pattern, with termwise factor supports still contained in the
old ones. Final row scaling fixes the nonzero diagonal without changing
that pattern. Free coefficients may change; this is not exact endpoint
preservation. The chosen infinite characteristic-two field is sufficient.

## 4. P112 whole-group consequence

For each physical triad, expand a payload coordinate by its three binary label
coordinates; expand the residual line by one. The fixed strict mask has own
identity blocks and only free cross blocks whose binary group-pairing matrix
is identically zero. Therefore every characteristic-two strict fit expands to
I334, regardless of its free coefficients. A lifted rank-one term supported
on physical group sets S,T has rank at most the fixed binary pairing rank
rho(S,T). This rank is unchanged by extending the characteristic-two field.
Rank subadditivity gives334 <= sum_t rho(S_t,T_t).

These are the same authenticated mask and expansion premises as in
`PROOF.md` and `INDEPENDENT-PROOF.md`, regenerated by the existing standalone
checkers from the two scientific inputs pinned in `SOURCES.json`. No new
finite geometry assertion is needed.
The new proof is the symbolic mixed-factor transfer above, not a computational
formalization of that argument.

## 5. Per-term splitting and a necessary budget of38

For each arbitrary rational factor u_t v_t^T, choose any partition of the
nonzero scalar source coordinates into chunks of size at most two. Let

    delta_source(t) = sum_chunks rho(source_chunk,reader_t)
                      - rho(source_t,reader_t).

Choose independently a partition of its reader coordinates into chunks of
size at most two and define delta_reader(t) analogously. Both quantities are nonnegative
by rank subadditivity: the full group space is the span of the chunk group
spaces, even when the same physical group appears in several chunks.

For each term choose whichever of its two proposed partitions has smaller
delta. Expand only on that chosen side. The exact original endpoint is
unchanged, and every new term has a two-port side, with mixed orientations
allowed. Applying the theorem gives

    C + sum_t min(delta_source(t),delta_reader(t)) >= 334.

This holds for every choice of the two partitions per term; one may minimize
over partitions as well. A proposed C<=296 decoder consequently requires at
least38 units of this splitting surcharge. This is a necessary inequality,
not a claim that an optimal partition or such a decoder has been found.

## 6. Common within-group gauge

Apply one invertible block-diagonal matrix G on the physical groups and use
the similarity `M -> G M G^-1`. Own identity blocks and forbidden whole cross
blocks remain unchanged. Each factor becomes `(G u_t)(G^-T v_t)^T`; its two
whole-group supports and tariff are preserved. If every transformed term has
a two-port side, possibly a different side for each term, the334 floor applies.
Thus a successful decoder must have a term with at least three source ports
and at least three reader ports in every such common gauge. No independently
chosen per-term gauge or unrestricted dense-factor lower bound is asserted.

## 7. Canonical coefficient sources and actual readers

There is a distinct rectangular extension for the exact canonical endpoint.
Let C be an indicator matrix with nonempty pairwise disjoint column supports,
let U=C A, and suppose U R=C C^T. Injectivity of C gives A R=C^T. Assume each
term has either at most two nonzero coefficient entries in A_t or at most two
nonzero actual scalar reader entries in R_t. These two conditions can again be
mixed term by term. Coefficient two-sparsity is not literal physical two-port
sparsity: one canonical mark can itself have three physical copies.

Freeze the assigned sparse sides and vectorize the rectangular equation
A R=C^T. The same repeated-gain construction and independent-variable basis
argument applies. The desired nonzero positions are now those of C^T; all
others are prescribed zero. In a selected tree component there cannot be
exactly one desired nonzero, since the old output would contradict the
everywhere-nonzero tree annihilator. With no desired positions use zero; with
at least two, prescribe nonzero values satisfying the new single annihilator
equation. A full-rank component receives its desired ones and other zeros.

Every actual output column contains at most one desired nonzero, because the
marks are disjoint. Independently scale each column having such a position by
the inverse of its new nonzero value; leave other columns unchanged. This is
right diagonal scaling of R, which preserves reader supports, including the
assigned frozen sparse-reader factors. The resulting coefficient endpoint is
exactly C^T. Multiplying by unchanged C gives the exact physical C C^T.
Shrinking a coefficient support shrinks the physical query support because
the columns of C have disjoint supports. For the full pinned57-mark P112 C,
the I334 expansion yields the334 floor, including J and the three-copy
residual mark. No common-reader or independent-query premise is required.

This does not prove334 from canonical sources alone. A possible saving under
that sole span hypothesis must use a term with at least three nonzero canonical
source coefficients and at least three actual reader ports; general such dense
coefficient factors are outside this graph reduction.

Prepared by flyingviper with substantial OpenAI Codex assistance and a separate
AI-agent proof audit. This is a written symbolic argument, not a proof-assistant
formalization or an independent human review. Apache-2.0.
