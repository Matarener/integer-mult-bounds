# A smaller exact locality polynomial for the Gaussian inverse

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: scoped written mathematical proof with exact finite corroboration.
Under the historical Gaussian caller's unchanged assumptions
`||H||_2, ||H^-1||_2 <= p^10` and physical bandwidth `W<p`, an explicit
Chebyshev inverse polynomial replaces the Neumann locality witness:

```text
                            historical witness      new witness
residual degree             p^42                    p^22
conservative halo           p^48                    p^24
inverse error bound         p^10 exp(-p^2)           2p^10 exp(-2p^2)
```

The new error is strictly smaller than the old majorant for every integer
`p>=2`. A section polynomial row agrees exactly with its global row when
its distance to omitted indices exceeds `(2p^22-1)W`. Each section used
for an inverse estimate must retain the same conditioning assumptions.

[PROOF.md](PROOF.md) gives the polynomial, the ordered error identity for
nonnormal matrices, exact row locality and a rational coefficient recurrence
with polynomial bit lengths. Chebyshev approximation is classical, with
[DLMF equation 18.5.1](https://dlmf.nist.gov/18.5.E1) cited explicitly.
The new step is the source-compatible parameter replacement. No claim of
global literature priority is made. The general approximation-based
inverse-decay method is credited to
[Demko, Moss and Smith](https://doi.org/10.1090/S0025-5718-1984-0758197-9).

## Reproduction and evidence

From the repository root, use CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -X dev -I -B research/chebyshev-inverse-locality/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -X dev -I -O -B research/chebyshev-inverse-locality/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/chebyshev-inverse-locality
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/chebyshev-inverse-locality --check-source-history
```

Another CPython 3.12 installation can replace the shown interpreter. Direct
replay prints `PASS_CHEBYSHEV_INVERSE_LOCALITY` in generated JSON, binding
all six package files by SHA256. It writes no files. The finite checks cover:

- 3,696 exact scalar samples for `K=2..8`, degrees `1..16`, and 33 rational
  points across the complete spectral interval. Integer coefficient
  construction agrees with an independent scalar Chebyshev recurrence;
  normalizations agree with the closed-form identity.
- 45 nonnormal operator fixtures, checking the exact ordered inverse-error
  identity and its operator-norm bound by rational LDL positivity. Moving
  the residual to the wrong side or reversing its sign fails on each fixture.
- 33 full section rows on a 21-point circle, for degrees 1,2,3, with exact
  global/section agreement beyond the proved radius. Six rows at the radius
  reject the smaller-halo extension. All bandwidth entries are checked.
- 127 integer parameter substitutions `p=2..128`, and six rejected invalid
  coefficient-constructor inputs. Checks remain active under optimized Python.

These reduced fixtures do not construct a degree-`p^22` production matrix.
The universal statement follows from the written proof, not a finite census.
No predecessor verifier, fixture or mathematical result is rechecked.

## Scope and obligations

The `uniform-transfer-audit` card is changed to an original component
construction for the `precision_tape` locality interface. This supplies a
smaller exact polynomial under explicit assumptions. It does not discharge
that entire selected assumption or provide a new supplier.

No optimized core geometry, complete physical coefficient-page cost,
finite-precision recurrence stability, native execution, rounded multiplier,
new kappa or complete multiplication theorem is supplied. No selected-source
cold replay, Lean or Docker build is run. Independent human and formal
proof-kernel review are unclaimed. The selected frontier and its five
assumptions remain unchanged.

The verifier has no recursion, subprocesses or external runtime inputs.
All loops run over fixed finite collections, with matrices at most 21 by 21
and coefficient degree at most 16. Its largest function is below 60 lines.
Python's required dynamic allocation is a Power of Ten deviation, bounded
here by those fixed domains and one active matrix fixture. Exact fractions
have bounded sizes because both dimensions and rational inputs are fixed.
The checks use explicit exceptions under normal and optimized Python, with
warnings treated as errors. No shared build settings are changed.
Ruff is unavailable in the supplied interpreter; no separate static analyzer
is claimed. Static AST inspection finds a maximum function length of 28 lines.

## Credit and overlap

Cinna Davis's PR #4100 supplies the historical Gaussian caller, its
conditioning/section contract and Neumann locality witness. Credit the
retained capped-Gaussian and multiplication-framework predecessors in its
NOTICE.md. Nick Petalas's #4217 separates polynomial locality from inverse
row equality, and Mihir Srivastava's #4501 retains the ordered nonnormal
identity and a stronger cross-cell conditioning contract. These are cited
predecessor results, not new outputs. SOURCES.json pins their retained
texts at main `19fdb086ea96af9a9f87936a2b888e10af4ed810`.

The new construction changes the approximation polynomial while retaining
the input matrix class and conditioning contract.
The exact finite verifier is new and imports no predecessor implementation.
Live open PRs, handoff claims, main README searches and
merged-PR searches were checked. Cached overlap has complete remote
pagination but incomplete sparse local-note coverage. These bounded checks
are not a novelty certificate.

Advance claim:
https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19226112

## Open next questions

Can a complete coefficient-page producer realize this smaller polynomial
with a favorable rounding and physical setup bill? The first step is a
bounded, exact coefficient page at one named caller section, with every
coefficient width, recurrence intermediate and output error charged. This
matters because exact locality alone does not lower the physical invoice.
The missing rounding, coefficient-page and consumer contracts are blockers.
No further construction or search is included here.
