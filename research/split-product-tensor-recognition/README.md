# Split-product tensor recognition

From an arbitrary square tensor over an explicit finite field, this package
recovers a product of split Frobenius-truncated local algebras, or rejects the
tensor. Acceptance returns the full local height types and three invertible
factor maps. It also gives a complete special-linear orbit label and constructs
determinant-one transporters. The test is necessary and sufficient for this
class and runs in deterministic polynomial time in dimension for fixed q.

This resolves the decomposition-discovery handoff in
[PR #5656](https://github.com/CrocSwap/integer-mult-bounds/pull/5656).
The earlier result requires supplied component types and factor maps. Here,
Frobenius-fixed spectral projectors recover the primitive factors, the module
top tests recover cyclic generators, and the retained local classifier supplies
the height types. Actual basis columns fix the component-order sign. Nilpotents,
extension fields and independent input/output bases are included.

Read [PROOF.md](PROOF.md), [recognize.py](recognize.py), and [RESULT.json](RESULT.json).
The maps satisfy `t(Ua,Vb)=W mu(a,b)` and are checked on every basis pair.
`recognize(t, field)` returns `(certificate, None)` or `(None, reason)`.
`sl_transporter(first, second, field)` returns maps F,G,H with determinant one
and `second(Fu,Gv)=H first(u,v)`. The explicit field representation and arithmetic
are retained unchanged from PR5637. Invalid tensor shapes or entries raise
`ValueError`; well-formed tensors outside the class have a rejection reason.

## Evidence and reproduction

The standard library suffices. Run with Python 3.12:

```sh
python3 -B scripts/research_package.py --package research/split-product-tensor-recognition
```

Both registered commands must print `PASS_SPLIT_PRODUCT_TENSOR_RECOGNITION`.
The complete two-dimensional domains contain 256, 6,561 and 65,536 tensors.
The independent coefficient-index orbit generator accepts 162, 3,456 and
49,500 tensors, respectively. Every acceptance agrees with the recognizer and
has a literal factor-map check. The oracle does not use a nucleus, radical,
module top or local recognition test.

There are 62 additional changed-basis presentations, 798 basis products,
62 special-linear transporters and 325 rejection/control checks. These include
products with more components than field elements, repeated nilpotent factors,
wrong residue fields, nonregular modules, incorrect maps and labels, and the
nontrivial component-order sign for F3 times F3[x]/x^9. Finite checks support the
written proof; they do not replace review in other dimensions.

Source hashes are checked before imports. [SOURCES.json](SOURCES.json) records
the exact upstream commits and the retained, byte-identical source copies.
[VALIDATION.md](VALIDATION.md) records the actual publication checks and limits.

## Use and limits

The tensor atlas can now obtain this class and its equivalence maps directly
from tensor coefficients. This is an interface result, with no new complete
kappa or change to the selected frontier. Native realization, coefficient
operations, ownership, restoration, storage, precision and the complete caller
remain unpriced. No multiplier or profitable supplier is claimed.

Residue fields must equal the supplied field. Arbitrary commutative algebras,
nonsplit residue extensions, and field-presentation changes are outside the
contract. Complexity is polynomial in dimension for fixed q; explicit field
tables and discrete-log enumeration do not give a polynomial bound in log q.
Independent human and formal proof-kernel acceptance remain open.

Base: `df0137efd35e11b4445734bf612bdd4c7ebc330c`, priority revision 7.
The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/5655#discussioncomment-19187666)
records the released handoff, scope and overlap coverage. Main's selected
conditional kappa was 0.00310045 at this checkpoint. This package changes no
selected record or predecessor package.

## Credit

- apoursh's [PR #5656](https://github.com/CrocSwap/integer-mult-bounds/pull/5656),
  head `b5e6e7c45f606d639d102570f9fab257e1d0d393`, supplies the product character
  theorem and the decomposition-discovery handoff. Its exact proof is retained
  in [vendor/PR5656.md](vendor/PR5656.md).
- Ali Romman's [PR #5637](https://github.com/CrocSwap/integer-mult-bounds/pull/5637),
  head `86389e525d3efafe236e929f6ae401c68be1d115`, supplies the finite-field
  arithmetic, local tensor recognizer, semilinear height proof and local factor
  normalization inputs. The exact executable and proof are retained in vendor.
- The retained sources credit apoursh's
  [PR #5502](https://github.com/CrocSwap/integer-mult-bounds/pull/5502) for the
  height criterion; Nick Petalas's
  [PR #5252](https://github.com/CrocSwap/integer-mult-bounds/pull/5252) for the
  nucleus approach and the reduced-case Frobenius-fixed spectral projectors;
  Ali Romman's
  [PR #5540](https://github.com/CrocSwap/integer-mult-bounds/pull/5540) and
  [PR #5459](https://github.com/CrocSwap/integer-mult-bounds/pull/5459) for local
  recovery and characters; and David Ganz for the tensor atlas lineage.

Primitive decomposition and spectral projectors are classical algebra. The
new contribution is their verified composition with regular-module recovery,
the local recognition algorithm and the product character interface, with no
supplied-decomposition premise. No literature-priority claim is made.

Prepared by Ali Romman with substantial OpenAI Codex assistance. The same
assistant supplied the proof and verifier. Apache-2.0.

## Open next questions

- Recover coefficient-field sections for nonsplit residue factors before
  extending the local height test. This needs explicit embeddings and a
  nonsplit character theorem.
- Bind one accepted tensor and its maps to a complete paid native caller.
  Charge coefficient execution and restoration before claiming a kappa gain.

The structured first steps and blockers are in [TASK.json](TASK.json).
