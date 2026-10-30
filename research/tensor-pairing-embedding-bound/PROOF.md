# A sharp common-root embedding boundary for the tensor pairing

This is a scoped application of elementary binary rank and real Gram-matrix
arguments to homelab-05's [PR3895](https://github.com/CrocSwap/integer-mult-bounds/pull/3895),
at `2e969106d82a7e53ee3a22580653521b4876cc6b`. No novelty is claimed for those
linear-algebra tools. The result concerns the literal pairing matrix, not all
possible decoders on the selected alphabet.

## 1. Object and three different requirements

The predecessor uses `G0 = [[2,1],[1,2]]` and `G4 = G0 tensor G0 tensor G0 tensor G0`.
Index rows by four-bit words `0,...,15`. If `d(i,j)` is Hamming distance, then
`G4[i,j] = 2^(4-d(i,j))`. Thus over F2,

```
B4 = (G4 + J16) mod 2 = P16 + J16,
P16[i,j] = 1 iff j = i xor 15.
```

The diagonal is one; the only zero in row i is its complement partner.
For a principal restriction S, distinguish:

1. **Rank screen:** `rank_F2(B_S) <= 9`, a necessary condition for a bilinear
   pairing of nine-bit source and reader labels. It is not a label embedding.
2. **Common injective E8 embedding:** distinct indices use distinct root lines
   and the *same* map on source and reader sides, preserving
   `B_ij = (<r_i,r_j> + 1) mod 2` for norm-two real E8 roots.
3. **Scalar decoder identity:** the factors must also give the required
   coefficients on every constrained pair. Binary pairing preservation alone
   does not establish this identity.

The selected 112-port alphabet is the E8 line system with one orthogonal
eight-line frame removed. Its actual nine-bit labels and their correspondence
to this geometric model are checked against the selected archive, using the
explicit map supplied by Gonzalo Mier's PR3566.

## 2. Full matrix: even different label maps cannot fit

Every row of P16 has one one, so `P16 J16 = J16 P16 = J16`, and `J16^2 = 0`
in characteristic two. Hence `(P16 + J16)^2 = I16`: B4 has rank sixteen.
For any source label matrix A and reader label matrix C with nine columns,
and any nine-dimensional bilinear form H, `rank(A H C^T) <= 9`.
Therefore the complete literal B4 cannot embed in the selected nine-bit
alphabet, even allowing different source/reader maps or repeated labels.
This excludes only preservation of this complete pairing.

## 3. Principal restrictions: the geometric bound is exactly eight

**Theorem.** Any common injective E8 root-line embedding of B_S has `|S| <= 8`.
The bound is attained inside selected P112.

Distinct norm-two E8 root lines have inner products in `{-1,0,1}` after
choosing either sign representative. Thus pairing one on distinct indices
forces inner product zero; pairing zero forces inner product +1 or -1.
The complement relation is a matching. After reordering S, its real Gram
matrix is block diagonal with singleton blocks `[2]` and pair blocks

```
[[2, epsilon], [epsilon, 2]],        epsilon in {-1,1}.
```

The singleton eigenvalue is 2; each pair block has eigenvalues 1 and 3.
The matrix is positive definite and has rank `|S|`. All roots lie in R^8,
so their Gram rank is at most eight. This proves the bound for every S
without enumerating E8 maps.

For attainment, take tensor indices `(0,15,1,14,2,13,3,12)` and map each
consecutive pair to these doubled-coordinate E8 roots (the true roots are
the displayed vectors divided by two):

| Tensor indices | Doubled roots | Selected provider port indices |
|---|---|---|
| 0,15 | `(0,0,0,0,0,2,-2,0)`; `(0,0,0,0,0,2,0,-2)` | 0,76 |
| 1,14 | `(0,0,0,2,-2,0,0,0)`; `(0,0,2,0,-2,0,0,0)` | 28,86 |
| 2,13 | `(1,-1,-1,-1,-1,1,1,1)`; `(1,-1,1,1,1,-1,-1,-1)` | 103,17 |
| 3,12 | `(1,1,-1,-1,-1,-1,-1,-1)`; `(1,1,1,1,1,1,1,1)` | 10,11 |

Their norms are two; within-pair products are `1,1,-1,-1`; all cross-pair
products are zero. They avoid the removed frame. The verifier checks all
64 witness pairings, Gram rank eight and binary rank eight, after binding
all 12,544 P112 pairings to actual selected ports. The witness proves the
maximum size is eight; it does not classify which smaller S embed.

Injectivity and the common map are essential hypotheses. Repeating a line
permits even inner product +2 or -2, so pairing one need not mean orthogonal.
Concretely, tensor indices `(0,15,1,2,3,4,5,6,7)` preserve the pairing under
the noninjective P112 root-index map `(0,1,8,8,8,8,8,8,8)`: the last seven
indices share a line orthogonal to the first A2 pair. The checker accepts its
pairings but rejects it as an injective embedding. Thus the distinctness
qualification cannot simply be omitted from the eight-vertex conclusion.
Different source/reader maps give a cross-Gram matrix rather than this positive
definite Gram matrix. The eight-vertex theorem does not cover that case.

## 4. What the binary rank screen alone misses

Let S contain p complete complement pairs and s singletons, with `p+s <= 8`.
Write `B_S = P_S + J`. If s=0, the same square argument gives rank `2p`.
If s>0, the kernel equation is `P_S x = t 1`, where `t` is the sum of x.
A singleton row forces t=0; pair rows force all paired coordinates zero;
the remaining s singleton coordinates have sum zero. The kernel dimension
is s-1, so the rank is `2p+1`. This includes rank zero for empty S.

The largest |S| passing rank at most nine is twelve, at p=4,s=4.
This is **only a rank-screen ceiling**: it does not claim an injective
twelve-label embedding. For example, at full ambient rank nine equal rows
would force equal labels, and the four singleton rows here are equal.

The geometric obstruction still adds information with injectivity: p=4,s=1
has an abstract nine-bit embedding with nine distinct labels. Let u be the
all-ones nine-bit vector. Its even-weight orthogonal complement has a
nondegenerate alternating form. For a symplectic basis `(a_i,b_i)`, i=1..4,
use labels `u+a_i,u+b_i`, plus u. These have diagonal pairing one, pairing
zero exactly within the four pairs, and one elsewhere. The verifier supplies
and checks explicit labels. E8 excludes that nine-vertex restriction by
Section 3. No maximal injective abstract-label census is claimed.

## 5. Pairing attainment is not a restricted tensor decoder

Every entry of G4 is positive. The eight-root witness has zero Gram entries
between different pairs, exactly where B_S is one and the selected scalar
identity therefore constrains the coefficient to zero. The predecessor's
identity `D4 T4^T = 2 G4` has nonzero coefficients there. Restricting its
rows to S and applying this pairing map cannot be a selected masked decoder.

There is also a diagonal normalization mismatch (16 versus 2). Even granting
the global normalization `G4/8`, its cross-pair entries remain nonzero.
The checker records a concrete masked-zero counterexample in both scales.
Changing or recombining factors to repair that identity is a different task.

This closes the literal full-pairing embedding route and the stated common-map
principal-subset question. It proves no universal COPY floor, physical tariff,
dirty-state consumer, new supplier, improved kappa or full multiplication theorem.
