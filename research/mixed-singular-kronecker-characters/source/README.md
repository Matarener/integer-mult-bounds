# Determinant images for repeated singular Kronecker blocks

**Scoped written proof with exact finite corroboration; no new kappa.**
This answers the single-minimal-index/multiplicity next question in Nick
Petalas's [PR #5250](https://github.com/CrocSwap/integer-mult-bounds/pull/5250).
It complements that package's regular square pencils with an invertible slice.
It does not classify mixed pencils or recover a decomposition from arbitrary
input tensors.

For any field K and positive integers e,r, let L_e(s,t) be the e by e+1 pencil
with s on the diagonal and t on the superdiagonal, repeated as L_e tensor I_r.
Use the action `(P,Q,R)` on slices `(A,B)` given by

```
(P(aA+bB)Q^T, P(cA+dB)Q^T),  R=[[a,b],[c,d]].
```

The exact stabilizer determinant image is

```
Delta = {(x,y,z) in (K*)^3 : x^(e+1) y^e z^[r e(e+1)/2] = 1}.
```

For the transposed pencil exchange x and y. [PROOF.md](PROOF.md) proves
necessity and sufficiency, explicitly lifts every GL2 slice action in every
characteristic, and constructs a witness for every allowed triple without root
extraction. The half-product is an integer exponent, including characteristic
two. Over F_q the image has size (q-1)^2 and the GL orbit splits into exactly
q-1 orbits under the product of the three special linear groups.

## Why this scope and what it adds

PR #5250, exact head `43142bedc7cb5c0f1f73ff3fea6d9bfd237949ee`, explicitly
leaves singular blocks and their multiplicity spaces open. Its README at this
package's base has the identical Git blob. The new step is the complete
one-type determinant image, its explicit slice-action lifts and constructive
converse. Classical Kronecker blocks and symmetric powers are not claimed as
new mathematics; global literature priority is unclaimed.

This takes that concrete handoff before a random assignment. The original
`formal-interface-lemma` card is retained verbatim in [TASK.json](TASK.json)
with **changed scope**: a written mathematical side result, not a Lean
formalization or a selected-supplier implication. Canonical main was pulled at
`df0137efd35e11b4445734bf612bdd4c7ebc330c`, priority revision 7; selected kappa
remains 0.00310045. The schema-aware source-binding baseline passed; its
metadata check is not a cold scientific replay. Coordination and the five-point
family comparison are in TASK.json and [Discussion #5670](https://github.com/CrocSwap/integer-mult-bounds/discussions/5670).

## Reproducible evidence

Use CPython 3.12 and its standard library from the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/kronecker-determinant-image
python3.12 -B scripts/check_research_commit.py --package research/kronecker-determinant-image --check-source-history
```

The registered commands run both ordinary and optimized Python with warnings
as errors. Direct replay also works without Git or repository files:

```sh
python3.12 -I -W error -B research/kronecker-determinant-image/verify.py
python3.12 -I -O -W error -B research/kronecker-determinant-image/verify.py
```

The success marker is `PASS_KRONECKER_DETERMINANT_IMAGE`. The preceding `RESULT`
JSON gives all tested domains, determinant images and counts; `PACKAGE_SHA256`
binds the local package files. The program writes no files. Each registered
command has a 120-second limit. [SOURCES.json](SOURCES.json) pins historical
provenance only: no predecessor executable or external scientific input is
imported, and no live input is omitted from VERIFY.json.

- **Completeness discriminator:** [oracle.py](oracle.py) independently enumerates
  every P and R and solves both literal equations for the unique Q transpose.
  Eight fixed (e,r,q) domains are (1,1,2/3/5), (2,1,2/3), (1,2,2/3) and
  (3,1,2): 7,710 candidate pairs and 4,470 stabilizers. Its determinant images
  agree exactly with the character kernel. It uses no symmetric powers or
  predicted-image formula.
- **Constructive checks:** [pencil.py](pencil.py) uses polynomial convolution,
  without factorial division, over F2, F3, F4 and F5. Thirteen explicit domains
  in `verify.py:LIFT_DOMAINS` cover indices through five and multiplicities
  through three. Every GL2 action and every nonzero multiplicity determinant
  is tested in those domains, including nonscalar repeated-block mixing:
  4,932 right-block lifts and 4,932 transposed lifts.
- **Converse:** all 454 nonzero determinant triples across both orientations
  in those domains are checked: 154 produce literal stabilizers with exactly
  the requested determinants and 300 are excluded by the character.
- **Failure controls:** six mathematical mutants detect a missing slice
  exponent, missing multiplicity, wrong orientation, two incorrect right-factor
  conventions and binomial reduction modulo q instead of the characteristic.
  Fourteen malformed/domain controls reject; 224 finite-field triples check
  associativity and distributivity. These explicit checks survive `-O`.

These are bounded checks, not exhaustive verification of every field or index.
F4 lift checks exercise characteristic two with nontrivial determinants; the
independent exhaustive stabilizer oracle is over prime fields only. Necessity
in general dimensions rests on the written block recurrence. Code limits are
e<=5, r<=3 and q in {2,3,4,5}; admitted bounds do not mean every combination was
tested. The oracle caps raw matrix enumeration at 625, retained group size at
480 and P,R pairs at 2,304 per fixture. No dependencies were added. Functions
are short, loops are bounded, and Python's managed allocation is used for these
small matrices; this is not an unbounded public tensor API.

## Boundaries and credit

Excluded: degree-zero unused rows/columns, unequal minimal indices, mixtures
of left and right blocks, regular/singular coupling, and regular pencils with
no invertible base-field rational slice. No arbitrary-tensor recognition or
uniform bit-complexity result is supplied. Native realization, dirty-state
ownership, routing, storage, precision, compiler cost and the full recursive
invoice remain **unknown**, not free. No physical supplier, selected-frontier
change, complete multiplication theorem, Lean build or selected cold replay is
claimed. Human and formal proof-kernel review remain unclaimed; parallel agent
checks are AI-assisted review.

Nick Petalas retains credit for the restricted regular-pencil extraction and
this explicit handoff. David Ganz retains atlas A030/A026/A029 and its cited
tensor/stabilizer lineage. The classical Kronecker, symmetric-power and
centralizer/canonical-form results remain predecessor work; this package does
not reproduce or claim the regular-pencil algorithms of Arne Storjohann or
the determinant work of Ferrer, Mingueza and Montoro. Source pins and the atlas
attribution file are recorded in SOURCES.json. Prepared by **apoursh** with
substantial **OpenAI Codex** assistance, including parallel proof, overlap and
independent corroborator work. Apache-2.0.

## Open next questions

- **Mixed positive minimal indices and block types.** Classify the fixed-slice
  homomorphisms of L_1 direct sum L_2, then determine how they affect determinant
  characters before adding any regular block. This is needed to combine the
  one-type result with PR5250; a mixed-block filtration and complete slice-action
  analysis are missing here.
- **Regular pencils without an invertible rational slice.** Start with
  diag(s,t,s+t) over F2 and its homogeneous elementary divisors. Its determinant
  polynomial is nonzero but all base-field projective slices are singular.
  A coordinate-independent replacement for B_R inverse and compatible descent
  remain the separate blocker in PR5250.

Structured relevance, first steps and blockers are also in TASK.json. Neither
question is reserved by this submission.
