# Uniqueness of the length-8 P104 decoding code via E8 (search-free proof)

Prepared by Matarener with Claude (Anthropic), via Claude Code. 2026-10-29.

This gives a second proof of Theorem 3 of [`../PROOF.md`](../PROOF.md), without the depth-first search certificate:
a structural argument. The argument has no branching, and every step is elementary. The finite inputs (the port
coordinates, the symmetries and the tables for Lemma V2) are listed in `ports-d8.md` and `handcert.md`, and a reader
can check them line by line. `verify_e8hand.py` re-checks everything with exact arithmetic in about a minute.

## 0. Setting

- Ports: 104 odd-weight vectors q in F_2^9. They are 104 of the 120 root lines of E8 (A8 coordinates). A weight-7 q
  maps to e_i − e_j, where i, j are its zeros. A weight-3 q maps to 2/3 on its support and −1/3 elsewhere.
- Ports i, j *conflict* (<q_i, q_j> = 1) exactly when their roots are orthogonal. Below, "x ⊥ y" means conflict.
- Problem: W ≤ F_3^104 has dim 8, and for every port l a vector w_l ∈ W has w_l[l] = 1 and w_l[m] = 0 for all
  m ⊥ l. Let M be the 104×104 matrix with rows w_l. We show that M = D·G'·D, where G' = Gram/2 mod 3 of the
  roots and D is a diagonal ±1 matrix. So W is unique up to signs, and the decoding vectors are unique.

**Coordinates mod 3.** E8 = D8 ∪ (D8 + ½·1) in orthonormal coordinates u_1..u_8. Every index involved is a power
of 2, so E8 ⊗ Z_(3) = Z_(3)^8. Roots therefore reduce to vectors of F_3^8 with the standard dot product
(½ ≡ 2). A D8 root ±u_i ± u_j reduces to itself. A half-spin root ½·s, s ∈ {±1}^8, reduces to −s.
Orthogonality is preserved, every root has square 2, and G'[x][y] = (r_x·r_y)/2 ≡ −r_x·r_y.

**Structure of the ports (V1).** The ports contain exactly one D8 subsystem, and contain all 56 of its lines. The
other 48 ports are half-spin lines; 16 of the 64 half-spin lines are missing (listed by `verify_e8hand.py`). There
are 759 frames, that is, sets of 8 pairwise orthogonal ports.

E8 facts used: (a) a root not in a frame F is non-orthogonal to exactly 4 members of F. (b) In frame coordinates,
every other root is ½(±r_a ± r_b ± r_c ± r_d) over a block {a,b,c,d} of the Steiner system S(3,4,8) on F.
(c) For every frame, Σ_{f∈F} (a·r_f)(r_f·b) = 2·(a·b) for all a, b, since r_f/√2 is an orthonormal basis.

## 1. Frame factorisation (hand)

For every frame F, M[F,F] = I, because of the diagonal and the conflict zeros. Since rank M ≤ 8,

    M = M[:,F] · M[F,:]        for every frame F.                                     (1)

## 2. The symmetric matrix N (hand)

Let N[t][x] = M[t][x]·M[x][t]. Then N is symmetric, N[t][t] = 1, and N[t][x] = 0 for x ⊥ t. The diagonal entry of
(1) gives

    Σ_{x∈F} N[t][x] = 1        for every port t and every frame F.                    (2)

If t ∉ F, only the 4 members of F that are non-orthogonal to t contribute, by fact (a).

## 3. Linear lemma (elementary, with tables)

Fix t and let N(t) be the 48 ports that are non-orthogonal to t. Put h_t(x) = N[t][x] − 1 for x ∈ N(t). By (2),
the four values on F ∩ N(t) sum to 1 − 4 ≡ 0 for every frame F ∌ t. Call such a set of four a *quadruple*.

For v ∈ r_t^⊥ (mod 3), the functions g_v(x) = (r_x·r_t)(r_x·v) satisfy every quadruple relation, by fact (c). They
form a 7-dimensional family. **Lemma V2**: every h with all quadruple relations is some g_v. Hence

    N[t][x] = 1 + (r_t·r_x)(r_x·v_t)    for a unique v_t ∈ r_t^⊥ (mod 3).             (3)

*Proof.* By symmetry it suffices to treat one port per orbit. The three signed permutations of the D8 axes in
`ports-d8.md` map the missing lines to themselves, so they map ports to ports and frames to frames. They have three
orbits on ports, represented by p0, p22 and p28. For each representative the proof uses only the tables in
`handcert.md`.

For x ∈ N(t), let x̄ be the third line of the A2 through t and x, so r_x̄ = ±(r_t − r_x). The reflection s_t in
r_t is an isometry of E8. It fixes every root orthogonal to t and swaps the lines x and x̄. So for a frame F ∌ t,
s_t(F) is again a frame, and its quadruple is the set of antipodes of the quadruple of F.

1. *Even part.* For each antipodal pair p = {x, x̄} of ports, put σ(p) = h(x) + h(x̄). Suppose F and s_t(F) are
   both port frames; the tables list them. Adding their two quadruple relations gives σ(p1) + … + σ(p4) = 0 over
   the four pairs. Call this a *tetrad*.
   Now take tetrads A = {p, q, a, b}, B = {p, q, c, d} and C = {a, b, c, d}. Then A + B − C gives
   2(σ(p) + σ(q)) = 0, so σ(p) = −σ(q).
   The tables give such edges forming a spanning tree of all 20–21 pairs, plus one triangle. Around the triangle,
   σ(p) = −σ(q) = σ(s) = −σ(p), so 2σ(p) = 0 and σ(p) = 0. Along the tree, σ = 0 on every pair. So h(x̄) = −h(x)
   whenever both are ports.
2. *Odd closure.* Take 7 seeds whose roots, together with r_t, are independent mod 3. Each table step fixes one more
   value of h, either by the antipode rule or by a quadruple with three known values. After 41 steps every value on
   N(t) is a fixed linear combination of the 7 seed values. So the solution space has dimension at most 7. It
   contains the 7-dimensional family g_v, so the two are equal. ∎

`verify_e8hand.py` (V2) re-checks the rank, 41 for every port, as an independent cross-check.

## 4. Symmetry and A2 triangles kill v_t (hand + V3)

Fix a root representative r_a for every port a. Because N is symmetric and r_a·r_b = ±1 for non-orthogonal a, b,
(3) gives

    r_b·v_a = r_a·v_b      for all non-orthogonal ports a, b.                        (4)

Let {t, x, y} be an A2 triangle of ports. Choose signs so that r_t·r_x = 1 and r_y = r_t − r_x. Then
r_y·r_t = 1 and r_y·r_x = −1. Using (4) together with v_a ⊥ r_a:

    r_y·v_t = (r_t − r_x)·v_t = −r_x·v_t,
    r_y·v_t = r_t·v_y = (r_x + r_y)·v_y = r_x·v_y = r_y·v_x = (r_t − r_x)·v_x = r_t·v_x = r_x·v_t.

So 2·(r_x·v_t) = 0, which gives r_x·v_t = 0 in characteristic 3.

**V3**: for every port t, r_t and the r_x with x ∈ N(t) whose A2 third line is a port span F_3^8. (There are 40
or 42 such x.) Hence v_t = 0 and N[t][x] = 1 for every non-orthogonal pair. Equivalently,

    M[t][x] = M[x][t] ∈ {±1}  for x non-orthogonal to t.                              (5)

So M is symmetric with exactly the E8 zero pattern. (V4 cross-checks steps 3–4 as one linear system.)

## 5. Signs (hand + V5)

Take the D8 matching frame T. By (b), every non-T port j is ½Σ_{t∈B_j} ε_j(t) r_t over a block B_j. Put
α_j(t) = M[j][t] for t ∈ B_j. These are ±1 by (5), and M[t][j] = α_j(t).

For a pair {a, b} ⊂ T, three blocks contain it. A line j in one of them has σ_ab(j) = ε_j(a)ε_j(b). Take two lines
j, k in different blocks through {a, b} with σ_ab(j) ≠ σ_ab(k). They are orthogonal, and the only common frame
coordinates are a and b. So (1) gives α_j(a)α_k(a) + α_j(b)α_k(b) = 0, that is,
α_j(a)α_j(b) = −α_k(a)α_k(b).

By V5, every block through {a, b} has ports of both signs. Hence ρ_s(ab) := α_j(a)α_j(b) depends only on
s = σ_ab(j), and ρ_−(ab) = −ρ_+(ab). So α_j(a)α_j(b) = σ_ab(j)·ρ_+(ab).

Around a triangle a, b, c, take a port of the block through a, b, c. The product of its three pair products is 1,
and so is the product of its σ's. Hence ρ_+(ab)ρ_+(bc)ρ_+(ca) = 1. A function on the pairs of 8 points whose
product around every triangle is 1 is a coboundary: ρ_+(ab) = d_a d_b with d_t = ±1. Therefore
α_j(t) = c_j d_t ε_j(t) for some sign c_j.

Now (1) gives M[j][k] = Σ_t α_j(t)α_k(t) = c_j c_k Σ_{t∈B_j∩B_k} ε_j(t)ε_k(t). This equals c_j c_k G'[j][k],
because G' = r·r/2 = ¼Σεε ≡ Σεε mod 3. Also M[j][t] = c_j d_t ε_j(t) = −c_j d_t G'[j][t]. With D_j = c_j off T and
D_t = −d_t on T, we get M = D G' D. ∎

## What is checked by a script

None of the hand steps depends on a computer. The finite inputs are tables a reader can check line by line:

- the port coordinates and symmetry generators in `ports-d8.md`;
- the tetrads, edges and closure steps in `handcert.md`;
- the A2 span (V3) and the availability fact (V5).

`verify_e8hand.py` re-checks all of these (V1–V5) with exact arithmetic and no search, in about a minute
(`python3 -B verify_e8hand.py`, final line `RESULT PASS`).

## Lean formalization

The whole argument is formalized in [`../lean/CarrierCode/E8*.lean`](../lean/CarrierCode). The final theorem
`CarrierCode.E8.decoding_unique` in `E8Main.lean` states: if a 104 × 104 matrix `M` over `ZMod 3` factors as
`A * B` with inner dimension 8, has unit diagonal, and vanishes on conflicting pairs (orthogonal roots), then
`M = D (2 Gm) D` for a diagonal `±1` matrix `D`, where `Gm` is the Gram form of the roots mod 3.

- `E8.lean`: the general steps (frame factorisation, frame sums, coboundary).
- `E8Step3.lean`, `E8Step4.lean`, `E8Step5.lean`: steps 3–5, including the general A2 trick.
- `E8Data*.lean`, `E8Cert.lean`: the finite inputs as lists of naturals (roots mod 3, the 759 frames, the step-3
  certificates, the A2 triangles with inverse matrices, the sign trees). Every property used is re-checked by the
  kernel (`decide +kernel` in `E8Check*.lean`), so the provenance of these lists does not matter.
- No `native_decide`. `#print axioms CarrierCode.E8.decoding_unique` gives `propext`, `Classical.choice` and
  `Quot.sound` only.

The E8 files are not imported by the default target, because the step-3 checks are heavy: each `E8Check3_k` needs
about 8 GB of memory and 3 minutes. Build them one at a time:

```sh
cd research/p104-carrier-code-uniqueness/lean && lake exe cache get
for t in E8CheckFrames E8Check3_0 E8Check3_1 E8Check3_2 E8Check3_3 E8Check3_4 E8Check3_5 E8Check3_6 E8Check3_7 \
         E8Check4 E8Check5 E8Main; do lake build CarrierCode.$t || break; done
```

A full sequential build took about 35 minutes on a 4-core, 31 GB machine.

Scope: the theorem is stated for the port order of `E8Data.lean`, which is the order of [`ports.json`](ports.json)
(odd-weight vectors of F_2^9 as integers), and for a
matrix `M` of decoding vectors. The link to the word-level `CodeFact` hypothesis of `../lean` (where the code is
the row space of `M`) is not formalized, and the weight part of `CodeFact` is still checked by `verify.py`.
