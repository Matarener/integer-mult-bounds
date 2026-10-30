# Independent F9 automorphism-character audit

The finite audit corroborates PR5459's determinant character on **12,315
substitutions over F9**, adding an odd-characteristic extension field absent
from its checker. It also supplies an explicit control showing that a
restriction-of-scalars determinant alone can accept a wrong F9 determinant.
No discrepancy was found in the tested character formula. No new kappa,
supplier, full theorem proof or independent human acceptance is claimed.

The exact statement under test is, for
`A = F9[x_i]/(x_i^(3^e_i))`, `N = dim_F9 A`, and a valid substitution with
invertible height-preserving tangent blocks `L_e`,

```
det_F9(sigma) = product_e det(L_e)^(N (3^e - 1)/2).
```

Source: Ali Romman's [PR5459](https://github.com/CrocSwap/integer-mult-bounds/pull/5459),
head `bef3575ddb19c44434a7e2460a353eac7c4d9387`. Its theorem is pending, and its
checker covers F2, F3, F4, F5 and F7. The byte-exact source proof and checker
are retained in `source/`, with API Git blob IDs and SHA256 in
[REFERENCE.json](REFERENCE.json). They are authenticated but **never executed
or imported**. The F4 domains are not repeated. The new field, quotient algebra,
substitution evaluator and three determinant checks are separately written.
Classical methods and the mathematical formula remain credited source work.

## Exact finite domain and result

Let `K = F3[i]/(i^2+1)`. Elements are encoded as `a+3b` for `a+b*i`.

| Algebra/domain | Completed maps | Observed determinant image |
| --- | ---: | --- |
| K[x]/x^3, every automorphism `x -> ax+bx^2`, a nonzero | 72 | all eight nonzero elements, nine each |
| K[x]/x^9, every nonzero linear coefficient and at most two nonzero nonlinear monomials | 11,208 | +1 and -1, 5,604 each |
| K[x,y]/(x^3,y^9), every height-preserving invertible linear map | 576 | all eight nonzero elements, 72 each |
| Same mixed algebra, identity tangent and exactly one admissible nonlinear monomial in one generator | 376 | 1 |
| Same mixed algebra, 83 seed-83 dense nonlinear samples | 83 | all eight nonzero elements |

For the second row the exact count is
`8 * (1 + 7*8 + binom(7,2)*8^2) = 11208`; it is **not** the full nonlinear
automorphism group. The mixed linear maps are `x -> ax`, `y -> bx+cy`,
with a,c nonzero and b arbitrary. There are 23 admissible nonlinear monomials
for x and 24 for y, giving `(23+24)*8 = 376` one-tail maps. The 83 dense
samples are a deterministic bounded sample, not exhaustive coverage. Classes
can overlap across rows; counts describe checked presentations, not the
number of distinct maps across their union. The stopping rule is completion
of precisely these five domains and controls, with no adaptive search.

All 12,315 maps pass defining-power relations, unit preservation, every
generator-times-basis product (156,978 checks), invertibility via nonzero
determinant and the stated character. The 11,280 one-variable matrices also
pass a division-free Leibniz subset determinant, independently of Gaussian
elimination. Simultaneous seeded row/column permutations avoid relying on
already triangular input matrices. All 72 cutoff-three maps, the eight
linear cutoff-nine maps and 83 dense mixed maps pass an independent F3
restriction-of-scalars determinant, for **163 norm checks**.

Every scientific output field, including the domain counts, spectra,
control list and streamed case digest, is compared with [RESULT.json](RESULT.json).
The digest binds the ordered presentations and their determinants; it is
not a proof of the general theorem or a replacement for rerunning the checks.

## Why the norm check is not enough

For `z=a+b*i`, multiplication on the F3 basis `(1,i)` is
`[[a,-b],[b,a]]`, so `Norm(z)=a^2+b^2`. Block replacement gives
`det_F3 Res(M) = Norm(det_F9 M)`. This standard identity supplies a second
arithmetic path through ordinary modular F3 elimination, independent of
the extension-field operation tables. It loses information: `Norm(i)=1`
although `i != 1`. In particular the cutoff-nine character image is
`{+1,-1}`, but the incorrect extra value `i` has the same norm as 1.
The executable control demonstrates this ambiguity. Exact F9 determinants
are retained; no norm-only acceptance claim is made.

Nine semantic controls cover forbidden upward height mixing, a nonlinear
tail that violates x^3=0 despite an invertible tangent, singular tangent,
a corrupted substitution column, confusing p-Frobenius with a K-linear map,
using q instead of p in the exponent, norm-only false positives, Z/9 in
place of F9, and an off-by-one character exponent. Some are explicit
counterexamples to a shortcut, others are rejected mutated inputs; none
is presented as a counterexample to PR5459. The p-Frobenius control uses
`(1+i)^3 != (1+i)*1^3`, while q-Frobenius fixes K.

The generator-times-basis checks, unit and defining relations bind all
monomial products by induction: repeatedly multiply by each generator,
using the checked transition at each step, and use the defining zero
products on crossing a cutoff. Linearity then extends to arbitrary inputs
for each checked finite substitution. This does not enumerate every possible
substitution or prove the all-field character theorem by testing.

## Reproduce

Python 3.12, standard library only, no network or Git needed by the checker:

```sh
python3 -W error -B research/f9-character-audit/verify.py
```

Expected: `PASS_F9_CHARACTER_AUDIT` with 12,315 maps, 156,978 products,
11,280 division-free determinants, 163 norm checks and nine controls.
The registered command runs normal and optimized modes:

```sh
python3 -B scripts/research_package.py --package research/f9-character-audit
```

`--emit` on the standalone checker prints the freshly computed JSON for
review; normal replay compares it with the committed receipt. Source hashes
are checked before any scientific work in either mode. See
[VALIDATION.md](VALIDATION.md) for executed checks and environments.

## Scope, sources and next questions

Base: `32890bc5de034ab8fc93ac88ead7279a6a416d04`; assignment and overlap
coverage are in [CLAIM.md](CLAIM.md). The selected conditional saving at
that base is 0.003027288235 (#5413), with its five inherited assumptions.
This algebraic side result does not reduce those assumptions. It does not
verify unit/autotopism characters, full three-factor stabilizer images,
orbit recognition, general equal-height blocks, arbitrary extension fields,
physical costs, compiler admission or a full multiplication theorem.
The pending source bytes are shipped locally so a clean checkout does not
depend on an unmerged Git object. The two main-branch predecessor proofs
are provenance, not imported runtime dependencies.

## Open next questions

These are also structured in TASK.json.

- Audit nontrivial equal-height tangent blocks over an odd extension field.
  They test determinant block coupling missing here. Start with F9[x,y]/(x^3,y^3)
  and a bounded set of genuinely mixed GL2 blocks; full nonlinear enumeration
  grows rapidly and needs a separate budget.
- Audit the full covariant autotopism determinant image over an extension
  field, retaining inverse-input conventions. Start with explicit unit maps
  and F9[x]/x^3. The normalization theorem and completeness of the image
  require their own proof review; this automorphism audit does not supply it.

## Attribution

Ali Romman: PR5459's height-flag formula and PR5316's univariate result.
Nick Petalas: PR5252's normalization and determinant-image interface.
David Ganz: the atlas character-equation framework. Local-algebra
filtrations, finite-field norms and determinant algorithms are classical.
Their notices remain in the retained source files. New independent audit,
norm-ambiguity control and packaging prepared for Charan / theon199 with
substantial OpenAI Codex assistance. No subagents or human review claimed.
New work is Apache-2.0, as is the repository and retained source.
