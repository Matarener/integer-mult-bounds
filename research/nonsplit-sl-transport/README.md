# Nonsplit field-presentation bridge and special-linear transport

This package connects two existing interfaces. Ali Romman's
[PR5664](https://github.com/CrocSwap/integer-mult-bounds/pull/5664) recognizes
Frobenius-product tensors and discovers their coefficient fields in arbitrary
bases. apoursh's [PR5663](https://github.com/CrocSwap/integer-mult-bounds/pull/5663)
computes determinant characters and witnesses in fixed residue-field
presentations. The bridge constructs the missing field identifications,
includes their determinants in all three factor maps, and produces
determinant-one transporters between equivalent raw tensors.

The common reference residue presentations are explicit parameters. The labels
are canonical relative to those parameters; this package does not choose a
globally canonical irreducible polynomial. No new kappa or paid physical
supplier is claimed.

## Mathematical interface

Fix the explicit base field K=F_q. The recognized class is

```
A = product_j L_j[x_i]/(x_i^(p^h_ji)),  L_j/K finite fields.
```

For two degree-d coefficient fields C and D given by multiplication tables,
the algebra C tensor_K D has d primitive factors, each a degree-d field. On
any primitive factor, the maps from C and D are isomorphisms. A linear solve
between these maps gives C -> D, followed by checks of the unit, invertibility
and every basis product. This uses the retained fixed-space/idempotent
algorithm, without enumerating all q^d field elements.

Extend these field maps across every variable monomial and match components
by their full `(residue degree, sorted height list)` type. If Q maps the common
reference model into a recovered model and the original certificate is
`t(Ua,Vb)=W mu_recovered(a,b)`, its normalized maps are `UQ,VQ,WQ`.
Consequently the determinant ratio changes by **division by det(Q)**:

```
delta_reference = det(W)/(det(U) det(V) det(Q)).
```

Ignoring this correction can assign different labels to the same tensor.
Different primitive factors, coefficient-field isomorphisms and pairings of
identical components change Q by a reference-model automorphism. The retained
character theorem therefore makes the normalized label independent of those
choices.

For equal-type tensors with equal normalized labels, the retained constructive
autotopism adjusts the three determinant ratios. The result satisfies
`t2(Px,Qy)=R t1(x,y)` with `det(P)=det(Q)=det(R)=1`. The corresponding
covariant tensor action uses `P^(-T), Q^(-T), R`; its input factors are not P,Q.
Different types or labels reject. [PROOF.md](PROOF.md) gives necessity,
attainment, conventions and algorithmic limits.

## Execution boundary

The raw tensor may have independently changed input and output bases; no
decomposition certificate is required by the recognition entry point. The
separate normalization entry point validates an explicitly supplied
recognition certificate before using it.

The public functions in `bridge.py` are:

- `field_isomorphism(C, D, base, component_choice=0)` returns a checked
  matrix C -> D. Both field tables have first basis vector one.
- `normalize_certificate(t, certificate, base, residues, field_choices=None)`
  validates and converts a PR5664 certificate, returning the reference model,
  three maps, explicit bridge, character index and normalized label.
- `recognize(t, base, residues)` discovers and normalizes the certificate.
- `sl_transport(t1, t2, base, residues)` returns the ordinary `P,Q,R` and
  covariant `A,B,C` maps. The last two functions return `(result, None)` on
  success or `(None, reason)` for class/orbit rejection.

Here `residues` maps each needed degree to a retained `Extension` over the
same `Field`; degree one may be omitted. Invalid field presentations,
coordinates, certificate maps or reference parameters raise `ValueError`.
Primitive choices in normalization are indexed by the sorted reference
components. They may alter the returned maps but not the label.

The base-field presentation is fixed. Field maps are K-linear, not maps that
apply an automorphism of K to coefficients. Recovered and reference fields
must have matching degrees; component matching also preserves the entire
height list. The executable checks multiplication identities after composing
maps rather than trusting matching dimensions or determinant values.

The field-table bridge uses polynomially many base-field operations for fixed
q. This is **not** a polynomial-complexity claim for the whole executable:
the retained reference-field constructor builds complete arithmetic tables,
and the retained determinant-witness construction searches norm preimages.
Those costs grow with the residue-field cardinality. No bit-complexity or
physical map-pricing claim follows from the linear-algebra bridge.

## Reproduction and evidence

Python 3.12 and the standard library suffice:

```sh
python3 -B scripts/research_package.py --package research/nonsplit-sl-transport
python3 -B scripts/check_research_commit.py --package research/nonsplit-sl-transport --check-source-history
```

The registered commands run the same explicit mathematical checks normally
and with optimization. [RESULT.json](RESULT.json) records their deterministic
report; [VALIDATION.md](VALIDATION.md) states the measured domains, failure
controls and checks not performed. The separate verifier uses its own field
arithmetic, elimination and tensor-action checks. It does not repeat the
predecessor's full raw-tensor recognition census.

Ten consumed predecessor files are retained unchanged. [SOURCES.json](SOURCES.json)
pins them to the initial retention commit of this branch;
[vendor/ORIGINS.json](vendor/ORIGINS.json) preserves their original paths,
commits, blobs and SHA256 values. They are authenticated before import. The
execution path compiles checked source bytes instead of trusting bytecode
caches. Proof and attribution inputs are included in the portable export.

## Selection, scope and credit

The base is canonical main `df0137efd35e11b4445734bf612bdd4c7ebc330c`, priority
revision 7, selected conditional kappa .00310045. Main was pulled before the
round. The selected source-binding baseline passed; it is not a scientific
replay. [TASK.json](TASK.json) records the changed formal-interface card,
handoff-first selection, family comparison, cost boundary and bounded stop
rule. The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/5655#discussioncomment-19188216)
follows PR5664's explicit released integration question. Live handoffs and
PR searches were checked; unpublished work and arbitrary historical diffs are
outside coverage.

Exact immediate predecessors:

- Ali Romman, PR5664, `8f7773e700d468396cbf893dfb18bf3ae6c20f66`:
  nonsplit recognition, coefficient fields, certificate validator and retained
  PR5661/5637 arithmetic and split-product helpers.
- apoursh, PR5663, `d72b2e42a4cf53ae85f5276da65c5cc84e17b253`:
  nonsplit determinant theorem, explicit models and constructive witnesses.

Credit Ali Romman PR5661/5637/5459, apoursh PR5656/5502, Nick Petalas PR5252,
David Ganz and the retained tensor-atlas lineage. Finite-field tensor-product
decomposition and scalar restriction are classical. The contribution here is
the checked composition of the two published interfaces, with the actual
field-basis determinant correction and explicit SL transport. No global
literature-priority claim is made.

Prepared by apoursh with substantial OpenAI Codex assistance, including
separate implementation, proof and finite-check agents. Apache-2.0. Agent
cross-checks are not independent human review or proof-kernel acceptance.

## Open next questions

- A named native producer/consumer must price these accepted maps before
  they can support a multiplication-bound improvement. First choose an actual
  caller and charge coefficients, movement, ownership, restoration, storage
  and precision. All those physical obligations remain unknown here.
- If large residue degrees are required by such a consumer, replace the
  retained full-table and norm-preimage searches with an explicitly specified
  efficient arithmetic contract. The bridge alone does not remove those
  costs; the first step is to measure them on the consumer's actual parameters.
