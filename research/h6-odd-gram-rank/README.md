# Sharp noncubic ranks for the H6 odd-Gram family

For every characteristic-zero odd Gram function with `f(2)=0` and `f(4)=1`,
the canonical 28,800-port root-product principal block has rank at least
**9,424** if its odd interpolation is genuinely quintic, and **20,400** if it
has a nonzero septic coefficient. Both bounds are attained. The cubic member
has root-block rank 800. These are exact ranks of this principal block, not
claims about the rank of the entire 30,960-port H6 matrix.

Under a **full-width 17 scalar rank-one return-episode** implementation, the
noncubic ranks alone force paid rank at least 160,208 or 346,800, respectively.
Both exceed all 30,960 ports before compensation. Reusing a physical centre
still pays for its separate episodes. This is not a lower bound for arbitrary
helpers, partial-frame networks, operator-valued factors, nonisotropic kernels
or changed geometry, and it is not a new kappa claim.

[PROOF.md](PROOF.md) gives the interpolation, five exact projectors, six
eigenforms, complete parameter cases and conditional cost implication.
`derive.py` and `independent.py` are separate standard-library implementations.
Each freshly checks all 57,600 association-square entries and 18 exact actions
with 28,800 columns apiece. Four producer mutations and one independent
normalization mutation must fail. The all-parameter conclusion uses the written
exhaustive case proof; it is not inferred from finitely sampled parameters.

Run from the repository root with Python 3.12:

```sh
python3.12 -I -O -B -Werror scripts/research_package.py --package research/h6-odd-gram-rank
python3.12 -I -O -B -Werror research/h6-odd-gram-rank/verify.py --out /tmp/fresh-odd-gram-result
```

The registered replay has a 120-second cap, requires no third-party modules,
writes only fresh external temporary outputs and authenticates all inputs
before and after. `e8_cubed.py` stays a live, exact-pinned source. The geometric
binding to its `e8_shells` and `construct_shell` is a written source inspection;
the NumPy shell generator and complete H6 supplier are not rerun. Exact source
hashes and original Git blobs are in `SOURCES.json`; portable script
adaptations are recorded in `ADAPTATIONS.json`.

## Open next questions

- Can a nonisotropic or operator-valued kernel improve the complete paid
  invoice? First specify actual frames, factor maps and a restored word. No
  source-bound realization or complete budget is provided here.
- Can partial-frame returns avoid the full-width premise? First give one exact
  dirty-input gather/scatter/restore mechanism with legal chronology. Matrix
  rank alone does not price that mechanism.

Credit Dominik Scholz's E8 geometry/factorization in PR606, DreamingOfClouds'
H6/Walsh proposal in Discussion1167, and PR1830's complete compensation/encoder
audit with its retained predecessor lineage. This adds the complete normalized
odd-function classification beyond the cubic kernel; it claims no priority for
E8 association algebra or generic rank subadditivity. Ross Richardson, with
substantial OpenAI Codex assistance in derivation, separate audit and packaging.
Separate AI implementations are not independent human review or formal-kernel
verification. Apache-2.0.
