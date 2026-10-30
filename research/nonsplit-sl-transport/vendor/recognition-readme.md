# Recognize Frobenius products with arbitrary finite residue fields

This package recognizes arbitrary square K-tensors that are isotopic to
products of L[x_i]/(x_i^(p^h_i)), where K=F_q and each L is any finite extension
of K. It returns every residue degree, height list, coefficient-field table,
and all three factor maps. No decomposition or coefficient-field section is
supplied. The output is an explicit algebra model and a literal tensor-isotopy certificate.

This removes the split-residue restriction of
[PR #5661](https://github.com/CrocSwap/integer-mult-bounds/pull/5661).
The new coefficient field is the kernel of Frob_(q^d)-I inside a local component
of residue degree d. Height tests use spans over that recovered field. Both
steps use base-field linear algebra and avoid enumeration of q^d elements.
The regular-module top has base-field dimension d.

The algorithm is necessary and sufficient for the stated class, and polynomial
in tensor dimension for each fixed K. Read [PROOF.md](PROOF.md),
[recognize.py](recognize.py), [RESULT.json](RESULT.json) and
[SOURCES.json](SOURCES.json). The result supplies an input test for the tensor
atlas. It supplies no paid physical construction or complete kappa increase.

## Contract

`recognize(t, field)` returns `(certificate, None)` or `(None, reason)`.
Invalid tensor shapes or noncanonical field elements raise `ValueError`.
The base field uses the exact explicit representation retained from PR5637.
The certificate has `components`, `U`, `V` and `W`.
Each component has `degree`, sorted `heights`, and a `field` multiplication
table whose first basis vector is one. Model basis order is variable monomial
first, then coefficient-field basis. All maps satisfy `t(Ua,Vb)=W mu(a,b)`.

The coefficient-field tables use discovered bases. Character images,
canonical orbit labels and determinant-one transporters between different
field tables are outside this package. The separate
[concurrent character claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/5655#discussioncomment-19187845)
uses supplied decompositions and explicitly leaves this discovery task open.
The package was narrowed after the submission overlap refresh to preserve
that separation. No field-presentation conversion is silently assumed.

## Verification

Use Python 3.12 and the standard library:

```sh
python3 -B scripts/research_package.py --package research/residue-product-tensor-recognition
```

Both normal and optimized commands must print
`PASS_RESIDUE_PRODUCT_TENSOR_RECOGNITION`. A separate coefficient-index GL orbit
generator agrees on every one of the 72,353 two-dimensional tensors over
F2/F3/F4, accepting 174/4,320/62,460. The new accepted cases include nonsplit
quadratic fields. This oracle does not use the nucleus or discovery kernels.

Further presentations over F2/F3/F4/F9 check nonsplit nilpotent factors,
repeated factors, mixed residue types, and residue degrees two and three.
Controls reject false maps and fields, wrong residue degrees, extra local
relations and nonregular modules. The coefficient-field validator also rejects
a reduced product of two fields. [RESULT.json](RESULT.json) gives the exact
counts, and [VALIDATION.md](VALIDATION.md) records the execution boundary.

## Credit and scope

Base is canonical main `df0137efd35e11b4445734bf612bdd4c7ebc330c`, priority 7.
The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/5655#discussioncomment-19187846)
records the fresh overlap check and changed residue premise. No selected file
or predecessor package is changed.

- [PR #5661](https://github.com/CrocSwap/integer-mult-bounds/pull/5661), exact
  `5d722279f4292c63361f1e958ff4ed5a6ec638aa`, supplies the split-product framework,
  basic linear-algebra helpers and the independent finite orbit-check routines.
- [PR #5637](https://github.com/CrocSwap/integer-mult-bounds/pull/5637) supplies
  the retained finite-field arithmetic and semilinear-kernel code. Its local
  height proof uses apoursh's [PR #5502](https://github.com/CrocSwap/integer-mult-bounds/pull/5502).
- apoursh's [PR #5656](https://github.com/CrocSwap/integer-mult-bounds/pull/5656)
  supplies split-product characters. Nick Petalas's
  [PR #5252](https://github.com/CrocSwap/integer-mult-bounds/pull/5252) supplies
  the finite-etale nucleus, spectral projectors, norms and Galois-sign precedent.
  David Ganz and the retained atlas authors keep their credit.

Exact executable and proof inputs are retained byte-for-byte and authenticated
before imports. The new code extends the nucleus/module composition and orbit
checks; it does not claim those predecessor methods as new. Coefficient-field
lifting is classical finite algebra. The new result is the complete recognition
interface for the stated nonsplit nonreduced family, with exact
certificates and checks. No literature-priority claim is made.

Physical native realization, coefficient costs, ownership, restoration, storage,
precision and a complete caller remain unpriced. Unknown costs are not zero.
Independent human or proof-kernel acceptance, hosted CI and the selected cold
replay are separate from these author-side checks.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.

## Open next questions

- Connect these recovered field tables to the concurrent supplied-decomposition
  character interface. Coordinate there before implementing field isomorphisms,
  labels or transporters.
- Choose an actual accepted tensor and price its maps in a complete native
  caller before treating the algebraic result as a kappa improvement.

First steps and blockers are also recorded in [TASK.json](TASK.json).
