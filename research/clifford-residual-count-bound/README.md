# Stronger uniform Clifford tensor separation

kumagi, with substantial OpenAI Codex assistance. Apache-2.0.

For the same projective n-axis Clifford alphabet and the same sufficient
width `f >= 4n+4`, this package improves the guaranteed tensor Gram interval
from **[1/9,17/9] to [1/3,5/3]**. The proof actually gives the stronger
lower constant `α = 1491359/4161536 > 0.358367` and upper constant `2-α`.
The coefficients may be arbitrary complex numbers chosen at the tested width.
This makes the existing algebraic separation guarantee more robust; it does
not improve the multiplication exponent or supply a physical caller.

The new step is a short double count: pair an ordered basis of the residual
space with its nonsingular residual form, and count in the opposite order
from the predecessor's loose estimate. For `1 <= k <= 2n`,

```
#{S in Sp(2n,2): rank(S-I)=k} <= 2^(2nk-k(k-1)/2).
```

With the existing `2^k` nonzero-trace Pauli lifts per such `S`, the absolute
Gram row sum at `f >= 4n+4+2s` is at most
`sum_{k>=1} 2^(-k(k+1)/2-sk)`. An exact geometric tail gives the constant
above. See [PROOF.md](PROOF.md) for the all-dimension argument, including
normalization, reconstruction transpose, phases and quantifiers.

A missing projective target therefore has worst-case operator norm
approximation error at least `sqrt(α)`, and in particular `1/sqrt(3)`,
instead of the predecessor's `1/3`. For a fixed Gaussian-dyadic residual
with squared coefficient norm `M`, one of the four widths `4n+4,...,4n+7`
has normalized squared residual norm at least `α M`, improving `M/9`.
These are direct algebraic corollaries, not a newly audited caller application.

## Selection, sources and overlap

Started from canonical main `df0137efd35e11b4445734bf612bdd4c7ebc330c`,
priority revision 7, after reading the root guidance and #1166 handoffs.
The current picker returned track `recursive-interfaces`, seed
`1f66e16685e4ef83d568f7fabb3db680`. This is an explicit scope change from
`joint-query-controller`: an enabling separation lemma, not the card's
complete matched QQ16 bill. The card's resolved first example,
`scripts/research_selected_baseline.py`, passed binding checks only.
The selected κ and all inherited assumptions remain unchanged.

The direct predecessor is Ali Romman's [PR #5526](https://github.com/CrocSwap/integer-mult-bounds/pull/5526),
head `45f7de73b168721cdf7ec8c1769b1b594493716a`; its retained
[proof](../clifford-pointwise-faithfulness/PROOF.md) is byte-pinned in
[SOURCES.json](SOURCES.json). Its Section 3 supplies the signed trace-lift
argument and residual forms; Sections 4–5 supply the Gram and four-width
framework. We strengthen the count, preserving their attribution and that
of their classical and repository predecessors. No predecessor executable
is imported or rewritten.

[Claim and canonical discussion](https://github.com/CrocSwap/integer-mult-bounds/discussions/5236#discussioncomment-19189185).
The initial 05:37–05:40 UTC search on 2026-10-26 paginated all 374 open PRs
and 5,002 Discussion records, supplemented by Git HEAD searches of package
README/TASK notes and relevant proofs. The helper's sparse local coverage
was incomplete; the supplemental searches are not a full proof audit or
novelty certificate. A pre-submission refresh at 05:53–05:54 UTC covered 376 open PRs and
5,007 Discussion records; targeted full-cache checks found the predecessor
and this claim, but no competing nonsingular-form count claim. Canonical
main was unchanged. The sharp one-axis work in #5549/#5594 and sharp
two-axis work in #5675 concern different claims. This package changes the
uniform all-n sufficient constant at the existing width, not those exact
finite spectra or thresholds. #5547 and the paid-return/application audits
remain their authors' independent work.

## Verification

The package uses only Python's standard library. Run from the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/clifford-residual-count-bound
python3.12 -B scripts/check_research_commit.py --package research/clifford-residual-count-bound --check-source-history
```

[VERIFY.json](VERIFY.json) registers both ordinary and optimized (`-O`)
execution. Both passed on macOS with CPython 3.12.14. Checks use explicit
exceptions, not removable Python assertions.
The standalone verifier also runs in an exported tree without Git, with
its declared predecessor proof present at the repository-relative path:

```sh
python3.12 -B research/clifford-residual-count-bound/verify.py
```

Two constructions agree on the entire small symplectic sets:

| n | Projective signed Clifford actions | Symplectic rank histogram, k=0,...,2n | Exact Gram row sum at f=4n+4 |
|---|---:|---|---|
| 1 | 24 | 1, 3, 2 | 13/32 |
| 2 | 11,520 | 1, 15, 100, 300, 304 | 37739/65536 |

The first construction closes signed Pauli permutations under H, S and
controlled-X. Each generator's full signed table is independently checked
against literal Gaussian-integer matrix conjugation (unnormalized H with
its factor two retained); these small integers are exactly representable
in Python complex arithmetic. The second enumerates every binary subspace
and compatible nonsingular residual form, then reconstructs the symplectic
map. No group-enumeration or linear-algebra library is used.

The verifier also checks every fiber's `2^k` nonzero-trace lifts, exact row
sums and the infinite-tail rational certificate. Five negative controls
reject a singular form, the wrong reconstruction transpose, a lost Pauli
sign, an omitted lift multiplicity and a width below this sufficient bound.
A failed sufficient bound is not evidence of dependence at smaller widths.

The finite checks corroborate the written proof; neither they nor the
metadata/replay checks constitute independent mathematical acceptance.
No full selected-frontier replay is needed or claimed for this separate
algebraic package. Source hashes, commit availability and source-export
checks authenticate the declared evidence, not the theorem's correctness.

## Limits

The Gram columns must represent distinct **projective** Clifford operators.
Scalar copies are combined with their phase raised to the tested width.
Four-width testing requires the predecessor's fixed residual and four-element
Gaussian-dyadic scalar group. The theorem does not cover arbitrary nonlinear,
rounded, cross-column or non-Clifford operations, or arbitrary nonunitary
scalings. It does not sharpen the predecessor's rectangular stabilizer-map
bound, establish a least tensor width, or give an optimal spectral constant.

A complete caller still needs its exact alphabet, retained dirty state,
ownership and physical costs audited. No paid-call count, matched caller
budget, new algorithm, unconditional multiplication theorem or frontier
admission follows from this constant improvement alone.

## Open next questions

- Can phase cancellation yield a stronger all-n spectral bound than the
  absolute-row estimate? Start from the existing #5594/#5675 finite spectra
  and seek a uniform representation argument, without repeating those censuses.
- Does one exact complete caller satisfy the alphabet premise for the
  stronger error guarantee? Pin its operations and retained state and consult
  the existing application audits before substituting this constant.

The corresponding dependencies and first steps are in [TASK.json](TASK.json).
The count is presented as an improvement to the repository's retained proof,
not a claim of priority in the mathematical literature. All derivation, code
and writing received substantial OpenAI Codex assistance for kumagi; no
independent human review or formal-kernel proof is claimed.
