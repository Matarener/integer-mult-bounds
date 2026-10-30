# Exact determinant image of a full matrix multiplication tensor

This contribution was produced by Nick Petalas. Apache-2.0.

**Claim type: scoped algebraic proof with exact finite corroboration.**
Let mu be multiplication in M_n(F_q), viewed as an ordinary tensor in
A* tensor A* tensor A. Put H_n={(a^n):a in F_q*}. Its ordered covariant
stabilizer determinant image is exactly

```text
Delta(mu) = {(u,v,(uv)^-1): u,v in H_n}.
```

Its GL_(n^2)(F_q)^3 orbit contains exactly
`(q-1) gcd(n,q-1)^2` orbits under SL_(n^2)(F_q)^3.
Both statements hold for every finite field and every n>=1, including
characteristic dividing n. Independent input/output basis changes do not
change the image.

[PROOF.md](PROOF.md) derives the character table, proves that every
allowed determinant triple is attained, and gives an explicit stabilizer
that corrects a supplied GL transporter to an SL transporter whenever
possible. Under an explicit promise of membership in this multiplication
orbit, the dimensions and q suffice to extract the three character
equations without enumerating a stabilizer. This adds a noncommutative
case to David Ganz's atlas A030 question in
[#2849](https://github.com/CrocSwap/integer-mult-bounds/pull/2849).
It does not recognize arbitrary tensors or recover unknown multiplication
bases. A constructive transporter correction requires the literal source
tensor or a supplied multiplication chart.

## Reproduction

From the repository root, with CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/matrix-tensor-determinant-image/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -O -B research/matrix-tensor-determinant-image/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/matrix-tensor-determinant-image
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/matrix-tensor-determinant-image --check-source-history
```

Another CPython 3.12 installation can replace the absolute interpreter
path. The direct verifier prints `PASS_MATRIX_TENSOR_DETERMINANT_IMAGE
no_new_kappa` and a generated JSON receipt binding all six package files
by SHA256. It writes no files and needs no Git checkout. The publication
preflight requires a committed package and its pinned source history.

## Evidence and implementation limits

The written proof supplies the universal claim. The independent finite
corroboration uses q=2,3,4,5,7,8,9 and n=1,2,3. The extension fields
are literal polynomial quotients, and every nonzero element has an
enumerated multiplicative inverse.

- In 21 field/size contexts, 537 constructed stabilizers satisfy every
  basis-product identity and all 142,126 coefficients of the transformed
  covariant multiplication tensors. Their determinant triples attain
  every predicted image and agree with the three-equation description.
- A separate complete enumeration visits all 65,536 binary 4-by-4
  linear maps, finds 20,160 invertible maps, and tests which preserve
  the unit and all matrix-basis products. Its six automorphisms equal
  the six inner maps of M_2(F_2).
- At n=2, all 1,171 determinant triples over those seven fields are
  considered. Explicit stabilizers correct all 89 admissible triples
  to determinant one in each factor; the other 1,082 fail the criterion.
  This is a determinant-domain census, not an enumeration of whole
  transporter sets or whole tensor orbits.
- Twelve semantic and boundary controls distinguish raw input-map
  determinants from covariant determinants, both character constraints,
  even n, an extension field, n=1, q=2, an altered tensor factor and
  unsupported checker domains. Explicit exceptions preserve all checks
  under optimized Python.

The verifier has no recursion, subprocess, dynamic code loading or
external dependency. Its fixed domains bound every loop: fields have at
most nine elements, matrices have dimension at most nine, the exhaustive
map domain has 65,536 elements, and explicit powers stop at 128. Every
function stays below 60 physical lines. CPython's managed allocation is
a deviation from fixed steady-state allocation; fixed fixture domains
bound the live matrices and sets. Table-driven arithmetic and ordinary
iterator dispatch are bounded managed-runtime indirections. Warning-strict
normal and optimized runs provide diagnostics; no separate static
analyzer or proof kernel is claimed.

## Scope and credit

The tensor factors remain ordered and the action is K-linear. Semilinear
actions and factor permutations are outside scope. The promised orbit
class, literal-source/chart requirement for correction, and existing GL
transporter are explicit hypotheses. There is no physical supplier,
native operator, uniform compiler, precision/stock bill, new kappa or
complete multiplication theorem. Independent human and formal proof-kernel
review are unclaimed. Lean, Docker and selected scientific replay are unrun.

Credit David Ganz's [atlas #2849](https://github.com/CrocSwap/integer-mult-bounds/pull/2849)
for A019's associative isotopy normalization, A029's bounded character
framework and A030's extraction question. Nick Petalas's merged
[#5252](https://github.com/CrocSwap/integer-mult-bounds/pull/5252) provides
the finite-etale extraction precedent. The atlas retains the Chen,
Grochow, Qiao, Tang and Zhang tensor-action context. Innerness of full
matrix-algebra automorphisms, matrix-unit arguments and cyclic-group
arithmetic are classical. The new contribution is the exact matrix-algebra
character extraction and correction package in this repository. Global
literature priority is unclaimed. No predecessor executable is imported
or replayed, and no predecessor credit is changed.

[SOURCES.json](SOURCES.json) binds the atlas, etale predecessor, original
task catalogue and selected record as historical provenance. They are
not live executable inputs. [TASK.json](TASK.json) explicitly changes
the formal-interface card to this algebraic side question.

## Open next questions

1. What is the exact image for products of full matrix algebras over
   finite extensions? Derive one extension-field block character, then
   account for determinants of permutations of identical blocks. Those
   extension and permutation characters remain unproved here.
2. Can a raw tensor in this class be recognized with a multiplication
   chart and transporter? Start with its three nuclei and simple-module
   actions. A complete recognition and chart-recovery proof is missing.

The structured first steps and blockers are in [TASK.json](TASK.json).
