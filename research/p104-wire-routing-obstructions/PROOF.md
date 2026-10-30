# Proofs

Notation. The 104 ports `q` are odd-weight vectors of `F_2^9`. Each port carries an E8 root line `r(q)` in A8 coordinates:
weight 7 gives `e_a - e_b` on its two zero coordinates, weight 3 gives `2/3` on its three coordinates and `-1/3` elsewhere
(as in `research/p104-carrier-code-uniqueness/e8/`). `G` is the Gram matrix: `G_ii = 2`, `G_ij = 0` when ports conflict
(`<q_i, q_j> = 1`), and `G_ij = ±1` otherwise (V1). The partner residual is `E = D (G/2) D^{-1}` for a diagonal gauge `D`
(rank-8 uniqueness, #1212 / `p104-carrier-code-uniqueness`). `Q_j = q_j^perp`, and `P(F)` is the set of ports in a frame `F`.

## Lemma 1 (sign lemma). Lean: `third_root_or_sign`

Let `k, i` be non-conflicting and let `j` be non-conflicting with both. Then either `r_j = ±(r_k - G_ki r_i)`, the third root
of the A2 spanned by `r_k, r_i`, or `G_jk G_ji = G_ki`.

*Proof.* `t = r_k - G_ki r_i` has norm 2, and `<r_j, t> = G_jk - G_ki G_ji ∈ {-2, 0, 2}`. Since `|r_j ∓ t|^2 = 4 ∓ 2<r_j, t>`,
the value `±2` forces `r_j = ±t`. Otherwise `G_jk = G_ki G_ji`. ∎

Consequence. The ratio `E_ji / E_jk = (d_k/d_i) G_ji G_jk` is the same for every common reader `j` except the third root.
So a register carrying `x_k + Σ s_i x_i` with `s_i = (d_k/d_i) G_ki` serves all its readers except at most one per carried port.
V2 checks every case: 4992 ordered pairs, the third root is a port in 4224 of them and one of the 16 missing lines in 768.

## Lemma 2 (triangle lemma). Lean: `triangle_iff`

For pairwise non-conflicting `k, m, i` with `a = G_km`, `b = G_mi`, `c = G_ki`: `abc = -1` iff `r_i = c r_k + b r_m`.

*Proof.* `|r_i - c r_k - b r_m|^2 = 2 + 2abc`. ∎

So the cocycle `G_km G_mi G_ik` is `-1` exactly on A2 triangles of ports. There are 704 of them among 19712 triples (V3).

## Lemma 3 (cover lemma). Computer-checked (V4)

For all ports `j ≠ a`, `|P(Q_j ∩ Q_a)| ≤ 24`. For `a ≠ b`, `P(Q_j ∩ Q_a) ∪ P(Q_j ∩ Q_b) = P(Q_j)` (48 ports) holds iff
`{j, a, b}` is an A2 triangle. In that case the two halves are disjoint, 24 + 24.

## Lemma 4 (capacity). Computer-checked (V5)

If `x, y` are non-conflicting and `P(Q_x ∩ Q_y)` has 24 ports, then every 6-dimensional subframe holds at most 16 of them.

## Lemma 5 (two sources). Hand proof from Lemmas 1, 3, 4 and V6

*Setting* (the minimal "lives as wires" architecture): a partner's public chain is `{0} → G_y → Q_y` with `dim G_y = 7`.
Every live has as its 8-dimensional frame some `Q`, with one live per `Q` (a "wire") or a carrier root. No public helpers.
Lives do not read owned registers.

*Claim.* There is no such legal word.

*Proof.* Content-in-frame (`p104-carrier-code-uniqueness`, Lemma 1): a public register's lives-part stays on the ports of
its frame. At `Q_y` partner `y` can only add the value of its wire, supported on that wire's 7-frame `F_y`. So
`P(G_y) ∪ P(F_y) = P(Q_y)`. By Lemma 3, `G_y = Q_y ∩ Q_x` and `F_y = Q_y ∩ Q_z` for an A2 triangle `{x, y, z}`.

The registers present at `G_y` are `Y_y` and lives whose 7-frame is `G_y`. Their 8-frames contain `G_y`, so they are `Q_x`,
`Q_y` or the non-port hyperplane `(q_x + q_y)^perp`. The wire of `y` is excluded, since its frame must cover the other half.
Hence the only other register is the wire of `x` (up to at most 8 frames equal to a carrier root). Let `A_w` and `A_y` be the
lives-parts with which the two arrive. Every write at `G_y` reads a register present at `G_y` (frame-rank law, cf. #6170 Theorem JR (i)), so by induction over the
events every lives-part held at `G_y` lies in `span(A_w, A_y)`.

Partner `x` reads the ports of `G_y = F_x` only through its wire. Partner `y` keeps its `G_y`-ports from `G_y` onward, because
its wire lives on the disjoint half. So `v_x|G_y` and `v_y|G_y` both lie in `span(A_w, A_y)`.

By Lemma 1 and V6, `v_y = λ v_x` on 23 ports of `G_y` and `v_y = -λ v_x` on the third vertex `z`. Hence these two rows are
independent and span the whole of `span(A_w, A_y)`. Every nonzero vector of that span has support of size at least 23, or is
a multiple of `e_z`. But `A_w` lies in the wire's 6-frame and `A_y` lies in `Y_y`'s previous frame, which is a subframe of
`G_y` of dimension ≤ 6. By Lemma 4 each has support ≤ 16. So both are multiples of `e_z`, a contradiction. ∎

## Remarks

- The triangle structure forces partners into disjoint A2 triangles, and 104 is not divisible by 3.
- A single extra port on the partner side (an extra stop at `<p_z>`, where the live is still pure) repairs the sign defect alone,
  and was checked exactly. Lemma 5 shows that the capacity defect needs a third source at `G_y`, that is, a helper.
