# Determinant of a residue-field presentation change

**Scoped written proof with exhaustive prime-field evidence; no new κ.**
This answers Open next question 2 of apoursh's merged
[PR #5663](https://github.com/CrocSwap/integer-mult-bounds/pull/5663)
(`research/nonsplit-frobenius-characters`). That package requires identical
residue presentations and says that comparing different ones needs "a
separately supplied and checked field isomorphism, with its determinant
included." apoursh's merged
[PR #5668](https://github.com/CrocSwap/integer-mult-bounds/pull/5668)
(`research/nonsplit-sl-transport`) already builds such field maps by a linear
solve and divides the determinant ratio by det(Q), computed numerically. This
package adds a closed form for the field factor of that determinant and its
dependence on which isomorphism is chosen. It does not change either
executable.

## Result

Let K=F_q, let f and g be monic irreducible of degree d over K, and put
L_f=K[u]/(f), L_g=K[v]/(g), each with its power basis 1,…,u^(d-1) and
1,…,v^(d-1). Every K-algebra isomorphism φ: L_f → L_g is u ↦ α for a root α
of f in L_g. Write V(x_0,…,x_(d-1)) = ∏_(i<j) (x_j − x_i). Then

```
det_K(φ) = V(α, α^q, …, α^(q^(d-1))) / V(v, v^q, …, v^(q^(d-1))),
```

computed in L_g, and the quotient lies in K. Consequences:

1. det_K(φ)^2 = disc(f)/disc(g).
2. The d isomorphisms are φ_k: u ↦ α^(q^k), and
   det_K(φ_k) = (−1)^(k(d−1)) det_K(φ_0). For odd q all d share one
   determinant when d is odd; when d is even, ±det_K(φ_0) each occur d/2
   times. In characteristic two there is one value.
3. On a component L[x_i]/(x_i^(p^h_i)) of K-dimension dN, in PR #5663's basis
   order (truncated monomial, then coefficient-field power), φ⊗id has
   determinant det_K(φ)^N.

So a supplied factor map that changes the presentation of component j must
multiply its determinant by det_K(φ_j)^(N_j). Item 2 matches PR #5663's
Frobenius sign (−1)^(d−1): the choice of isomorphism matters exactly when
that sign is nontrivial.

## Proof

Let σ(x)=x^q on L_g. Define the K-linear map E_g: L_g → L_g^d,
b ↦ (b, σb, …, σ^(d−1)b). In the power basis its matrix has rows
((σ^k v)^i)_i, a Vandermonde matrix with determinant V(v, σv, …, σ^(d−1)v).
This is nonzero because the conjugates of v are distinct (g is separable).
For a = Σ a_i u^i, σ^k(φ(a)) = Σ a_i (σ^k α)^i, since σ fixes K. So E_g∘φ
has rows ((σ^k α)^i)_i and determinant V(α, σα, …, σ^(d−1)α). Matrices
of K-linear maps are K-matrices, and det(E_g)·det(φ)=det(E_g∘φ) over L_g.
This gives the formula; the quotient is det_K(φ) ∈ K.

Item 1: V(ρ_0,…,ρ_(d−1))^2 = ∏_(i<j)(ρ_i−ρ_j)^2 = disc of the monic
polynomial with roots ρ_k. The conjugates of α are the roots of f and those
of v are the roots of g.

Item 2: K-automorphisms of L_g form ⟨σ⟩, so the isomorphisms are σ^k∘φ_0,
that is u ↦ σ^k α. Its Frobenius-ordered list is the list for α rotated k
places. A rotation of d entries is a product of k(d−1) transpositions, and
each transposition negates V. The even-degree count follows because exactly
half of k=0,…,d−1 are odd.

Item 3: in coefficient-minor order φ⊗id is block diagonal with N copies of
the d×d matrix of φ.

The Vandermonde and discriminant identities and the normal-basis Frobenius
sign are classical; no literature priority is claimed. The new step is the
explicit determinant for the PR #5663 presentation interface, its sign rule
and the component power.

## Evidence

From the repository root, with CPython 3.12:

```sh
python3.12 -B scripts/research_package.py --package research/residue-presentation-determinant
python3.12 -B scripts/check_research_commit.py --package research/residue-presentation-determinant --check-source-history
python3.12 -I -W error -B research/residue-presentation-determinant/verify.py
python3.12 -I -O -W error -B research/residue-presentation-determinant/verify.py
```

The marker is `PASS_RESIDUE_PRESENTATION_DETERMINANT`. The program uses only
the standard library, reads no files and writes none. A run takes about
17 seconds.

- **Domains.** Every ordered pair of monic irreducible (f,g) over F_p for
  (p,d) in (2,2…5), (3,2…4), (5,2), (5,3), (7,2), (7,3), (11,2):
  279 irreducibles (Rabin's test), 18,157 pairs and 51,300 isomorphisms.
  Roots of f in L_g are found by evaluating f at every element.
- **Independent checks per isomorphism.** The determinant by Gaussian
  elimination mod p equals the Vandermonde ratio; the squared determinant
  times a Sylvester-resultant disc(g) equals disc(f); the cyclic sign rule
  holds; and Kronecker blocks give det^N for N=2,3,4 (153,900 checks).
  The 3,899 odd-q even-degree pairs each show both signs d/2 times.
- **Mutation controls.** Each must be detected at least once: Vandermonde
  over sorted rather than Frobenius-ordered roots (24,659 detections),
  ignoring the Frobenius sign (4,223), using exponent kd instead of k(d−1)
  (4,223), and assuming determinant one (40,671).

Executable coverage is prime fields only; the written proof covers every
finite K. This is a scoped proof, not a recognizer, a modification of the
PR #5663 or PR #5668 executable, or a physical caller.

## Open next questions

1. Use the closed form as an independent cross-check of the det(Q) factors
   that PR #5668 computes by linear solves. The first step is to read each
   recovered field map's image α_j of the reference generator and compare
   det(φ_j)^(N_j) with its numerical value. No such cross-check is run here.
2. Extend the formula to non-power bases, such as normal bases, that a real
   producer might store. Compose with the basis change to the power basis.
   No named producer or consumer basis is supplied.

Structured versions are in [TASK.json](TASK.json).

## Credit

This contribution was produced by Nick Petalas. It builds on apoursh's
[PR #5663](https://github.com/CrocSwap/integer-mult-bounds/pull/5663) and
[PR #5668](https://github.com/CrocSwap/integer-mult-bounds/pull/5668) and their
predecessors credited there. Apache-2.0.
