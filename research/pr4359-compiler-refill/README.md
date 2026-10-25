# Conditional κ = 0.00230509 and smaller explicit templates after PR4359

This package refines [zxv's PR #4359](https://github.com/CrocSwap/integer-mult-bounds/pull/4359)
at immutable head `da637c87c89482bc4c86be36bd0071b3d400dbed`.
It retains that construction's native, finite-compiler, delayed-cover,
precision, storage, analytic and fixed-tape hypotheses. It leaves the selected
frontier unchanged and is a conditional research contribution awaiting review.

The first result is an explicit rational parameter family proving that every
fixed rational saving below the same complex mixed root is admitted by the
retained outer inequalities. The endpoint itself is not claimed. A concrete
exactly checked point is **κ = 0.00230509**, improving the source's declared
0.0023 by **0.00000509**, about **0.2213% in the exponent saving**. This is
not a measured running-time improvement. The complex mixed root and native
inventory are unchanged.

The second result tightens the compiler induction by using its actual
complement coefficient, instead of replacing it by 1/4 and imposing an exit
coefficient of 1/8. At the original supplier savings:

| Supplier | Uniform saving | Original sufficient rank | Improved sufficient rank |
| --- | ---: | ---: | ---: |
| Complex | 0.002304 | `2^276540184361` | `2^1546084442` |
| BIT before cover | 0.002760 | `2^6552928412` | `2^42843607` |

For the new κ point, the combined stronger bound gives complex rank
`2^2099384703303215709`. These are effective finite specifications of
astronomically large templates. Their words, widths and constants are not
materialized. Decreasing the specified rank does not assert monotonicity of
all generated program sizes or give a practical algorithm.

- [ENDPOINT.md](ENDPOINT.md) gives the rational family, complete outer bill,
  source comparisons, and inherited obligations.
- [TEMPLATE.md](TEMPLATE.md) proves the sharper quantitative induction.
- [REVIEW.md](REVIEW.md) records the scoped source review and overlap.
- [RESULT.json](RESULT.json) contains the reproducible exact certificate.
- [SOURCE-REPLAY.json](SOURCE-REPLAY.json) records the separate full source
  replay: all 23 stages passed and all 59 artifacts matched under the source's
  explicitly declared timing, metadata and compression comparison rules.

## Reproduce

Python standard library only, with Python 3.12 or newer:

```sh
python3 -I -O -B research/pr4359-compiler-refill/verify.py
python3 -B scripts/research_package.py --package research/pr4359-compiler-refill
```

The verifier authenticates every exported source byte and Git blob, binds the
literal profiles to the frozen source, reproduces the old nine-row outer
bill and all 54 source predicates, checks the new strict predicates and
functional conditions, independently encloses the mixed root, and rejects
explicit invalid parameters and one-less integer rank controls. It compares
its complete deterministic output with `RESULT.json`; it does not rewrite
artifacts during normal verification.

The complete 23-stage source replay requires a separate checkout of PR4359
and its supported runner:

```sh
python3 -B research/kappa-0023-productive-jobs/verify.py --check-only
python3 -B research/kappa-0023-productive-jobs/verify.py --out /absolute/new/path
```

The source's native and universal arguments remain distinct from these
finite checks. The historical archive-recovery discrepancy is not repaired.
The repository-selected conditional κ remains 0.001672660197076918.

## Exact source export and attribution

`EXPORTED-SOURCES.json` records the original PR head, paths, Git blobs and
SHA-256 digests of the focused unchanged exports under `source/`. Their
bytes were independently compared with the immutable Git objects. This is
a self-contained source export because the unmerged source PR is not an
ancestor of this main-based contribution. The generic `SOURCES.json` pins
only the main-branch task and selected-record provenance; it does not falsely
claim that the external PR belongs to publication ancestry.

The productive-helper construction and preserved interval engine are zxv's
PR4359. The mixed flow derives from Jacob Alan Sussman's Theorem 1G / PR4268.
The retained native words and outer wrapper retain their earlier attribution
in the source documents and repository notices. New material was prepared for
1337isnot1337 with substantial OpenAI Codex assistance. Apache-2.0; all original
notices are retained.

## Open next questions

The structured questions, first steps and blockers are in [TASK.json](TASK.json).
A changed complete native tariff is needed to exceed this mixed root. A
geometry-aware H decoder or another change in the actual productive jobs must
pay all preparation, routes, owned storage, restoration and endpoints.
Separately, optimizing the intermediate induction exponent or using sharper
exit/source distributions may further reduce sufficient template ranks.
Neither direction is needed for the two results above.
