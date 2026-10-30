# Determinant characters for split Frobenius products

This package extends the local-algebra character interface to a nonempty finite
product of Frobenius-truncated local algebras. It supplies a written proof,
explicit prime-field determinant witnesses, and a checker for a supplied
three-factor tensor certificate. It does not discover that certificate from an
arbitrary tensor. The selected multiplication bound is unchanged.

The direct next question is the product/component-matching handoff in Ali
Romman's [PR #5637](https://github.com/CrocSwap/integer-mult-bounds/pull/5637),
at `86389e525d3efafe236e929f6ae401c68be1d115`. The
[canonical investigation](https://github.com/CrocSwap/integer-mult-bounds/discussions/5655)
records the claim and public status. Base is
`df0137efd35e11b4445734bf612bdd4c7ebc330c`, priority revision 7.
The selected conditional kappa at that base is `62009/20000000`.

## Result

Let K=F_q have characteristic p and let

```
A = product_j B_j,
B_j = K[x_1,...,x_sj]/(x_i^(p^h_ji)),   h_ji >= 1,
N_j = p^(sum_i h_ji),
E_ji = N_j (p^h_ji-1)/2.
```

The empty height list means B_j=K. Each factor type is its sorted height list.
Let g be the gcd of q-1 and all E_ji, additionally including (q-1)/2 when q
is odd and some factor type occurs at least twice. Then

```
det Aut_K(A) = {c^g : c in K*},
Delta(mu_A) = {(u,v,w) in (K*)^3 : (uvw)^((q-1)/g) = 1}.
```

Here Delta uses the covariant action on `A* tensor A* tensor A`. The GL orbit
of this tensor splits into exactly g orbits under SL x SL x SL.
[PROOF.md](PROOF.md) gives the component decomposition, local characters,
permutation signs, unit determinants, and autotopism normalization.

Two distinctions are essential. Exponents use each **local** dimension N_j,
not the total dimension. Component permutations are allowed only between
isomorphic factors, not arbitrary equal-dimensional factors. For example,
over F3 the local algebra F3[x]/x^9 has trivial automorphism determinant image,
but the product of two copies acquires determinant -1 by exchanging them.
The dimension-nine factors with heights (2) and (1,1) are not isomorphic.

Even when the total dimension is not coprime to q-1, unit determinants still
fill K*: vary a scalar on one component, whose dimension is a power of p.
Using a single common scalar on the whole product would miss valid witnesses.

## Supplied-certificate contract

The executable accepts prime fields only; the written theorem covers all finite
fields. It uses canonical residues 0,...,p-1, exact integer arithmetic, and
standard-library Python. Matrices act on column vectors. A tensor is indexed
by `tensor[i][j][k]`, with k the output coordinate.

For a supplied product model and invertible matrices U,V,W, the checker tests
every basis product in

```
tensor(Ua,Vb) = W mu_A(a,b).
```

Acceptance verifies the certificate; it is not an algorithm to find U,V,W or
the component decomposition. Malformed data and incorrect certificates are
rejected. Heights are sorted inside each component, but supplied component
order is retained. To compare orbit labels, the checker first identifies this
order with the canonical lexicographic order of factor types. The determinant
of that permutation must be included: exchanging different types can change
an unnormalized coordinate label even though it is not an algebra automorphism
of the fixed ordered model.

`model.py` exposes `make_model`, `determinant_character`, `automorphism`,
`autotopism`, `covariant_stabilizer`, `validate_certificate`, and
`sl_transporter`. Height parameters always define the internally sorted local
model; supplied matrices must use that model's ordered monomials. The executable
materializes the algebra and uses field-element enumeration; it makes no
polynomial bit-complexity claim in binary-encoded heights or log p.

The code constructs automorphism and covariant stabilizer witnesses for every
admissible determinant request. The inverse-input convention is explicit:
an autotopism F(a)G(b)=H(ab) acts as `(F^-T,G^-T,H)` on the tensor. It also
constructs determinant-one maps between certified tensors with equal types
and canonical orbit labels, checking their determinants and every transported
basis product.

## Verification

From the repository root, with Python 3.12:

```sh
python3.12 -B scripts/research_package.py --package research/frobenius-product-characters
```

For an exported package and its three declared proof-source inputs:

```sh
python3.12 -I -B research/frobenius-product-characters/verify.py
python3.12 -I -O -B research/frobenius-product-characters/verify.py
```

Checks use explicit exceptions and remain active with optimizations enabled.
`SOURCES.json` pins the exact retained predecessor proof bytes, and the direct
verifier authenticates their hashes without Git. No predecessor executable is
imported. Finite enumeration corroborates the proof only in its stated domains;
it is not proof-kernel verification or independent human review.

The separate checker enumerates all 40,487 matrices across six domains of
dimension at most three over F2 or F3: 22,854 are invertible and 23 are algebra
automorphisms. It checks 2,372 normalized autotopisms directly on basis products.
Separate polynomial substitution oracles exhaust all 4,374 automorphisms of
F3[x]/x^9 and all 500 automorphisms of F5[x]/x^5. The moderate product tests
accept 44 determinant triples and reject 36 outside the predicted image.

Literal covariant coefficient-index checks over F5 and F7 accept 104 triples
and reject 176. Nonlinear substitution controls reject omitting the input
transpose. Twelve malformed or changed certificate controls are rejected.
Independent factor bases in dimension nine and component-order normalization
in dimension ten exercise the supplied-certificate interface; equal-label
special-linear transport succeeds and unequal-label transport is rejected.
These are bounded finite domains, not enumeration of all larger product
algebras. Each direct run takes about one second on the development machine.

The selected-record source-binding orientation passed after materializing its
sparse inputs. That check did not replay the selected physical construction.
The written proof and executable were reviewed by separate Codex agents;
this is AI-assisted internal review, not independent human acceptance.

## Sources, overlap and limitations

Ali Romman's [PR #5459](https://github.com/CrocSwap/integer-mult-bounds/pull/5459)
supplies the local height-flag character formula; apoursh's
[PR #5502](https://github.com/CrocSwap/integer-mult-bounds/pull/5502) supplies the
intrinsic height flag. Nick Petalas's
[PR #5252](https://github.com/CrocSwap/integer-mult-bounds/pull/5252) supplies
the finite-etale determinant-image precedent and autotopism normalization.
Their retained files are pinned at the base in `SOURCES.json`. David Ganz and
the atlas lineage retain credit for the character/orbit framework. PR #5637
is the pending handoff source, not an executable dependency of this package.

Overlap checks covered current main guidance, the newest live handoffs and
bounded all-state PR searches for product/Frobenius/component terms. Sparse
local notes, arbitrary historical diffs and unpublished work were not completely
searched. No literature-priority claim follows from those checks.
`TASK.json` explicitly changes the formal-interface-lemma card to this written
algebraic interface proof; no Lean formalization is claimed.

## Open next questions

- Recover the product decomposition and three factor maps from an arbitrary
  tensor. This would remove the supplied-certificate premise. Start with the
  nucleus regular-module test and primitive idempotents, then apply the local
  height recognizer. A complete decomposition algorithm and complexity bound
  remain missing here.
- Allow nontrivial residue fields. This would cover nonsplit components. First
  specify field embeddings and isomorphisms and account for their determinants;
  the current proof assumes every residue field is K.
- Realize a certified tensor in a named native producer/consumer pair. A bound
  improvement requires paying representation, coefficients, movement, precision
  and restoration. No such physical construction or invoice is supplied here.

## Credit

New product proof and implementation: apoursh, with substantial OpenAI Codex
assistance, including a separate finite checker and proof audit. Predecessor
methods and notices retain the attribution above. Apache-2.0. No selected cold
replay, proof-assistant build, or independent human acceptance is claimed.
