# A clique saving needs an odd cycle shared by cross and diagonal terms

Contract and notation are those of `research/plane-port-global-rank-dual`
(PR #5560, Mark / Matarener), which uses CubeJerry's #4365 contract. A term
`u_k v_kᵀ` touches plane sets `A_k` (rows) and `R_k` (columns). Its tariff is
the binary pairing rank of the generated spans. Coefficients lie in a field of
characteristic other than 2. Characteristic 2 already has the floor 224.

## Setting (THEORY.md, E3)

Let `S` be a clique of pairwise non-orthogonal planes, so the mask restricted to
the `2|S|` ports of `S` is the identity. Restrict every term that touches `S` on
both sides to `S × S`. Other terms contribute nothing to this block. A term is
*diagonal* when `A_k ∩ R_k ∩ S` is nonempty, which forces tariff at least 2. It
is *cross* when `A_k ∩ S` and `R_k ∩ S` are disjoint, with tariff `t_j ≥ 1`. Let
`N` be the sum of the cross terms on `S` and `m = dim ker(I - N)`. E3 proves

    cost on S  >=  4|S| - 2m + Σ_j t_j,

and, when `N` is supported on a bipartite plane graph, `2m <= rank N`, hence no
saving.

## Lemma

Define two directed graphs on the planes of `S`:

- `G`: `(P, Q)` with `P ≠ Q` is an edge when some cross term has `P ∈ A_k` and
  `Q ∈ R_k`;
- `H`: `(P, Q)` with `P ≠ Q` is an edge when some diagonal term has `P ∈ A_k`
  and `Q ∈ R_k`.

Let `supp N` be the set of `(P, Q)` with `P ≠ Q` and nonzero block `N_PQ`. Then

    supp N  ⊆  G ∩ H.

If the undirected graph underlying `G ∩ H` is bipartite, the cost on `S` is at
least `4|S|`. Equivalently, a saving on `S` requires an odd cycle of planes
each of whose consecutive pairs is reached, in some orientation, by a cross
term **and** by a diagonal term.

## Proof

The block `N_PQ` is a sum of the `P × Q` blocks of cross terms. A cross term
contributes to it only when `P ∈ A_k` and `Q ∈ R_k`, so `supp N ⊆ G`.

On `S × S` the diagonal and cross terms sum to the identity, so
`N = I - D`, where `D` is the diagonal-term sum. For `P ≠ Q` the identity block
`I_PQ` is zero, so `N_PQ = -D_PQ`. A diagonal term contributes to `D_PQ` only
when `P ∈ A_k` and `Q ∈ R_k`. Hence `N_PQ ≠ 0` gives an edge of `H`, and
`supp N ⊆ H`.

Also `N_PP = 0`, because a cross term never has the same plane on both sides.
If the underlying graph of `G ∩ H` is bipartite, choose sides and let `Σ` be the
diagonal matrix with `+1` on the ports of one side and `-1` on the other. Every
nonzero block of `N` joins the two sides, so `Σ N Σ = -N`. Then `Σ` maps
`ker(I - N)` onto `ker(I + N)`. Both kernels lie in the range of `N`
(`x = ±N x`), and they meet only in 0 since `1 ≠ -1`. Thus
`2m <= rank N <= #cross terms <= Σ_j t_j`, and E3's inequality gives cost at
least `4|S|`. ∎

The bipartite step is E3's argument. The new content is the inclusion
`supp N ⊆ H`. Bipartiteness of the diagonal-term graph alone now excludes a
saving, whatever the cross terms do.

## Consequences

1. **Triangles.** For `|S| = 3` the only odd cycle is the triangle. A saving on
   a 3-clique needs diagonal terms reaching all three plane pairs, and cross
   terms reaching all three. A diagonal term reaching the pair `{P, Q}` touches
   `P` and `Q` across its two sides and shares a plane between them. Its
   tariff is therefore the pairing rank of a span containing a full plane on
   both sides together with a second plane on one side.
2. **Search pruning.** An exact or numerical escape search may discard every
   support pattern whose diagonal-term graph is bipartite, independently of the
   cross terms and of the coefficients.
3. **Not vacuous.** The spectral inequality alone does allow a triangle. Three
   cross terms with sources in distinct planes realize `N` equal to `I - J` on
   the first coordinate of each plane. Then `rank N = 3` and `m = 2`, so
   `2m > Σ t_j` is possible when each `t_j = 1`. The lemma then forces the
   diagonal part `I - N` to reach all six directed plane pairs.
   `verify.py` checks this example exactly.

## Not proved

The lemma gives a necessary condition only. It does not decide the 224
conjecture, any open triple or quadruple class, or the global floor 140. It
does not price the diagonal terms that the triangle condition forces, and it
says nothing about native realization or κ.
