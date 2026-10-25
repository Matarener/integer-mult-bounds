# Source-bound dyadic block compiler: 68 fewer scalar-allowance units

This package compiles four actual disjoint scalar windows from the retained native source using one reusable owned temporary. Their complete scalar allowance falls from **766 to 698 per orientation**, including initialization and erasure. The compiler also handles higher-rank dyadic blocks without introducing illegal odd denominators. **No new κ is claimed.**

[PROOF.md](PROOF.md) proves dyadic rank factorization by integer column operations, the one-temporary block construction and its inverse-transpose version. [CASES.json](CASES.json) binds the four source windows, including one rank-two block. [RESULT.json](RESULT.json) contains the actual emitted programs. This extends the rank-one shared bridge in [#4489](https://github.com/CrocSwap/integer-mult-bounds/pull/4489); the integer reduction is classical, with no novelty claim.

## Reproduce

From the repository root, using Python 3.12 and only its standard library:

```sh
python3.12 -B scripts/research_package.py --package research/dyadic-block-compiler --check-only
python3.12 -B scripts/research_package.py --package research/dyadic-block-compiler
```

A Git-free exported tree can run `python3.12 -I -O -B research/dyadic-block-compiler/verify.py`. No Windows path, PowerShell, C++ compiler, GPU, SciPy or NumPy is required. Windows execution was checked; Linux execution remains untested.

The replay authenticates two source inputs, locates the actual forward/backward windows, derives both matrices, checks an independent rational rank, compares every emitted local input column and owned return, and invokes the pinned source's actual scalar-pricing function. It checks 200 deterministic additional dyadic matrices and rejects omitted clears, a false factor, an illegal third and a shifted source selector. Unchanged repeated-edge coalescing costs are checked before reporting a gain.

For a new matrix, `python3.12 research/dyadic-block-compiler/compiler.py matrix.json` prints a plan. A nonzero `--query-rank` is an explicitly declared interface premise, not a native Fourier-rank certificate. The four source cases use the actual identity query and therefore require no such premise. Rank minimization alone need not minimize scalar cost; inspect the complete output allowance before substituting a plan. These emitted macros are not claimed to be the best scalar rewrites; alternative gauge rescaling may improve them further.

## Open next questions

The result is a constructive local macro with one additional owned field, no temporary productive credit and unchanged recursive jobs. It does not install a changed global supplier, prove the complete caller stock bound, or improve κ. Local allowances are upper bounds under the retained pricing convention, not measured runtime.

A useful next step is to find a different-chart source block whose independently verified physical bridge and full entry/exit costs improve the complete invoice. Begin with its exact source window and arbitrary-input contract, then replay both orientations and charge every owned field, monomial route and outer obligation. CASES.json already supplies source-bound examples for testing the compiler; do not treat their finite nonrecursive saving as an exponent gain.

See [ATTRIBUTION.md](ATTRIBUTION.md) and [TASK.json](TASK.json). Prepared for Dugongue with substantial OpenAI assistance; Apache-2.0.
