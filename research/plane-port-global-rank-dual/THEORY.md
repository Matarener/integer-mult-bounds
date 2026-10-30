# The 224 conjecture and the structure of a possible escape

Notation as in [PROOF.md](PROOF.md). "Escape" means a decoder, or a decoder restricted to a group
of planes, that costs less than 2 per port.

## Conjecture

**Every decoder of the strict 112-port mask costs at least 224, over every field.**

Equivalently, under #4365's contract, plane ports cannot lower the additive COPY mass below
separate coordinate messages, whatever the coefficients. What is proved:

| Class | Bound | Source |
|---|---:|---|
| 2-integral coefficients (odd denominators) | 224, sharp | Philippe Van Velzen, Discussion 1587; #2532 |
| fields of characteristic 2 | 224, sharp | same rank argument; Lean `V4.decoder_cost_ge` |
| decoders split into disjoint plane pairs, any field | 224 | CubeJerry, `two-plane-copy-floor` (#4365) |
| any decoder, any field | 49 | fitting rank, `paired-plane-minrank-bracket-audit` |
| **any decoder, any field** | **140** | **this package** |

The gap is therefore `[140, 224]`, and it concerns only fields of characteristic 0, so in
particular rational decoders with even denominators.

## E1. Why an escape must use essential halves

The tariff depends only on the plane supports `(A_k, R_k)`. If the same support pattern, or a
pattern with smaller supports, is realized by some decoder over `F_2`, then its cost is at least 224
by the characteristic-2 theorem, because tariffs are monotone under shrinking supports. So an
escape needs a support pattern whose mask equations are solvable over `Q` but have no solution
over `F_2` with those supports. By the 2-integral theorem, no rescaling `u_k -> 2^a u_k`,
`v_k -> 2^-a v_k` of the terms may make all coefficients 2-integral.

## E2. 2-adic layering

Rescale every term of a rational decoder so that `u_k` is primitive (minimum 2-adic valuation 0).
Let `-e < 0` be the smallest valuation among the `v_k`, and `L` the set of terms that reach it. On
every fixed mask entry `M_pq` is an integer, so the leading parts cancel:

    sum over k in L of (u_k mod 2)(2^e v_k mod 2)^T = 0   on all fixed entries, over F_2.

The most fractional layer is a binary decomposition of the zero mask, free entries arbitrary. Such
layers are not free: each term still pays its full tariff. An escape must buy, with zero-mask
layers, a saving on the integral layer that the binary argument does not see. This is the same
mechanism as the known escape in `research/bit-full-borel-2adic-floor`, and the positive
half-integral barrier of `c5-dyadic-decoder-gate` (Tekalign) shows that the first layer alone does
not suffice in that model. Bounding what zero-mask layers can buy would settle the conjecture.

## E3. A necessary spectral condition on cliques

Let `S` be a clique, so the mask on its `2|S|` ports is the identity. Split the terms that touch
`S` on both sides into *diagonal* terms, where some plane of `S` lies in both `A_k` and `R_k`
(tariff at least 2, since the pairing already has rank 2 on that plane), and *cross* terms, where
`A_k` and `R_k` meet `S` in disjoint plane sets (tariff `t_j >= 1`, since the planes are
non-orthogonal). Let `N` be the sum of the cross terms restricted to `S` and `m = dim ker(I - N)`.
The diagonal terms sum to `I - N`, so there are at least `2|S| - m` of them, and

    cost on S  >=  4|S| - 2m + sum_j t_j.

A saving on `S` needs `2m > sum_j t_j`: the cross part must have eigenvalue 1 with multiplicity above
half its tariff.

- If the cross terms are bipartite (the planes of `S` split into two sides and every cross term goes
  between them), then `N` is similar to `-N`, so in characteristic not 2 the eigenspaces for 1 and
  -1 have the same dimension `m` and both lie in the range of `N`. Hence `2m <= rank N <= sum_j t_j`
  and there is no saving. For two planes this reproves the 8 of `two-plane-copy-floor`.
- So a saving needs odd cycles among the cross terms. These are not rare: 879 plane pairs have a
  single-plane cross term of tariff 1, these pairs touch all 56 planes, they form 5,136 triangles,
  and the graph is not bipartite. The combinatorial condition alone excludes nothing.
- The extreme case `m = 2|S| - 2` forces `I - N` to have rank 2, which is realizable over `F_2` and
  therefore excluded by E1.

## E4. Where an escape is most plausible

On groups that contain orthogonal plane pairs, the mask has free entries and its rank drops below
`2|S|` over every field: 5 instead of 4 per induced 5-cycle, 49 instead of 48 globally. Over `F_2`
the binary Gram lift removes the free entries, which is why the 224 bound survives those rank
savings in characteristic 2. Over `Q` there is no such lift. Odd holes of the non-orthogonality
graph together with dyadic coefficients are therefore the main suspects. The proven local
results there are sharp at 20 on the C5s (`c5-gram-rank-cover`, `c5-asymmetric-cost-floor`,
`c5-residual-weighted-cover`), and our numerical search found nothing cheaper on C5s extended by
one or two planes ([EVIDENCE.md](EVIDENCE.md)).

E1-E4 are structural observations, written proofs only; they are not formalized and they do not
prove the conjecture.
