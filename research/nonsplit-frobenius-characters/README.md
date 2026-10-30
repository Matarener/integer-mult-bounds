# Nonsplit Frobenius-product determinant characters

This package extends the supplied-decomposition tensor interface to products
whose residue fields are nontrivial finite extensions of the ground field.
It proves the exact automorphism and covariant stabilizer determinant images,
constructs witnesses, and checks supplied three-factor maps and their
special-linear orbit labels. It does not recover a decomposition from an
arbitrary tensor or supply a paid multiplication algorithm. No new kappa is
claimed.

## Result

Fix K=F_q of characteristic p. For each component choose an explicit extension
L_j=F_(q^d_j) and let

```
A = product_j L_j[x_i]/(x_i^(p^h_ji)),
N_j = p^(sum_i h_ji),
E_ji = N_j (p^h_ji - 1)/2.
```

An empty height list means the residue field itself. The intrinsic type of a
component is `(d_j, sorted heights)`. Set g to the gcd of q-1 and all E_ji,
also including (q-1)/2 if q is odd and either an even residue degree occurs
or an identical odd-degree type repeats. Then

```
det Aut_K(A) = (K*)^g,
Delta(mu_A) = {(u,v,w): (uvw)^((q-1)/g) = 1}.
```

The GL orbit splits into exactly g orbits under SL x SL x SL. For checked maps
`t(Ua,Vb)=W mu_A(a,b)` relative to the same ordered model, the complete label is

```
(det(W)/(det(U)det(V)))^((q-1)/g).
```

[PROOF.md](PROOF.md) proves the coefficient-field section, norm characters,
Frobenius signs, matching of factors, unit determinant surjectivity and the
covariant convention. The decisive dimension in E_ji is N_j over L_j, not
d_j N_j over K. Coefficient Frobenius contributes a separate sign, and only
identical full types may be exchanged.

For a discriminating example, take K=F9=F3[t]/(t^2+1), beta=1+t, and
L=K[u]/(u^2-beta). On L[x]/x^3 the substitution x -> u x has determinant
Norm(u)^3=beta^7 of order eight. Multiplying E by the residue degree would
incorrectly restrict this determinant to squares. Separately, on F9[x]/x^9
viewed over F3, coefficient Frobenius supplies determinant -1 even though
all residue-linear automorphisms have determinant one.

## Supplied presentation and executable contract

`model.py` uses exact finite-field arithmetic and standard-library Python.
The unchanged, authenticated `vendor/local.py` from PR5637 supplies the ground
field and matrix operations. `Field(p, modulus)` presents K with canonical
base-p digits. `Extension(base, modulus)` presents a residue field with
constant-first monic coefficients in K and canonical base-q digit encoding;
it rejects reducible moduli by checking every nonzero element is invertible.
This supports extension ground fields as well as prime fields.

`make_model(base, components, residues)` requires a nonempty, lexicographically
sorted list of `(degree, sorted positive heights)` and one explicit residue
presentation per used degree. The degree-one field can be omitted and is K.
The basis is ordered first by component, then lexicographic truncated monomial,
then polynomial coefficient-field power. This order is part of the certificate.
Unsorted types are rejected. If an external decomposition has a different
order, its supplied factor maps must include that actual permutation; its
sign must not be discarded.

`model_isomorphism` matches identical supplied presentations. It rejects a
different residue polynomial even when the abstract fields are isomorphic.
Comparing those presentations requires a separately supplied and checked field
isomorphism, with its determinant included. The code does not discover field
embeddings or infer them from equal dimensions.

The public witness operations are `variable_scaling`, `coefficient_frobenius`,
`component_swap` and `unit_multiplication`. `automorphism(model, determinant)`
constructs an admissible determinant or rejects it; `autotopism` and
`covariant_stabilizer` construct requested determinant triples. Every constructed
autotopism checks all basis products. The covariant action is `(U^-T,V^-T,W)`.
`validate_certificate(model, table, U, V, W)` checks shape, canonical entries,
invertibility and every basis product before returning the label.

Theorems cover all finite fields and all finite supplied types. The executable
materializes field tables and dense algebra tensors and enumerates field
scalars, primitive elements and discrete logarithms. No polynomial complexity
in log(q), binary-encoded heights, or growing residue degrees is claimed.
No general tensor recognizer or special-linear transporter between arbitrary
input tensors is supplied here.

## Verification

From the repository root with CPython 3.12:

```sh
python3 -B scripts/research_package.py --package research/nonsplit-frobenius-characters
python3 -B scripts/check_research_commit.py --package research/nonsplit-frobenius-characters --check-source-history
```

The registered commands use warning-strict isolated normal and optimized modes.
The checker authenticates all five live source inputs before importing the
model. Its direct matrix and orbit checks are separate from the constructive
witness routines. Exact counts and execution boundaries are recorded in
[VALIDATION.md](VALIDATION.md); the finite checks corroborate the written theorem
without replacing it.

## Sources, scope and coordination

Canonical base is `df0137efd35e11b4445734bf612bdd4c7ebc330c`, priority revision 7,
selected conditional kappa `62009/20000000`. The prescribed source-binding
baseline passed after materializing tracked files omitted by the sparse
checkout. It is a metadata check, not a scientific replay.

The [canonical claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/5655#discussioncomment-19187845)
and [TASK.json](TASK.json) record the handoff-first choice and family-expansion
decision. The split-product recognizer was already claimed and is now
[PR5661](https://github.com/CrocSwap/integer-mult-bounds/pull/5661), at
`5d722279f4292c63361f1e958ff4ed5a6ec638aa`; it explicitly excludes nonsplit
residue fields. This contribution answers the separate nonsplit-character
question in it and PR5656. The formal-interface-lemma card is retained verbatim
but scope is explicitly changed to a written algebraic theorem rather than a
proof-assistant development.

Compared alternative: PR5658 already supplies field-level routing prefix and
suffix bounds. Its remaining physical-cost question requires an actual caller;
this algebraic handoff has a bounded exact acceptance test. Fresh all-state PR
searches, live handoffs and the product investigation were checked. Sparse
historical notes, arbitrary old diffs and unpublished work remain coverage limits.

[SOURCES.json](SOURCES.json) pins the live proofs and reused executable.
[vendor/ORIGINS.json](vendor/ORIGINS.json) binds retained copies to their original
public commits and paths. Vendor bytes and frozen predecessor packages are
unchanged. The local determinant theorem and classical finite-field facts are
credited dependencies, not newly claimed results.

## Open next questions

- Recognize nonsplit products from arbitrary tensors. Recover compatible
  coefficient-field sections and local maps; the split recognizer cannot simply
  drop its residue-field test. This would remove the supplied-model premise.
- Compare different residue-field presentations. Supply a checked field
  isomorphism and account for its ground-field determinant in each factor map.
  The present executable intentionally requires common presentations.
- Use this interface in a named native producer and consumer. Charge field
  representation, coefficients, movement, precision and restoration before
  deriving any multiplication-bound consequence. No such caller is supplied.

Structured questions and their blockers are in [TASK.json](TASK.json).

## Credit

New nonsplit proof, construction and finite checker: apoursh, with substantial
OpenAI Codex assistance from a coordinator and separate implementation, proof
and verification agents. No independent human or proof-kernel review is claimed.
Nick Petalas's PR5252 (`07e6f55d18d2d3fd6dcea19bd642d71657c5fe14`) supplies the
etale norm/Frobenius/permutation interface. Ali Romman's PR5459
(`bef3575ddb19c44434a7e2460a353eac7c4d9387`) supplies local nilpotent characters;
PR5637 (`86389e525d3efafe236e929f6ae401c68be1d115`) supplies reused field/matrix
code. apoursh's PR5656 (`b5e6e7c45f606d639d102570f9fab257e1d0d393`) supplies the
split-product argument and handoff; PR5502 supplies the height-type lineage.
David Ganz and the retained tensor-atlas authors retain their notices. Norms,
normal bases, finite-field structure and regular-module arguments are classical.
New work is Apache-2.0, with all retained notices preserved; no global literature
priority claim is made. No selected cold replay, Lean or Docker run is required
or claimed for this isolated algebraic contribution.
