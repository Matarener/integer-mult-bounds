# Independent binomial-series audit of the PR4091 pooled dual

**No discrepancy found in the scoped pooled proof. No new κ.** A separate
standard-library implementation verifies all three duals of
[Ross Richardson's PR4091](https://github.com/CrocSwap/integer-mult-bounds/pull/4091)
on every whole-helper bin pattern, uniformly for
`0.00173 <= a <= 0.00174`. It reconstructs the affine primal witnesses for
every real mixture `0 <= x <= 3240` and the unique global optimum `x=1080`.

This closes a specific independent-verification obligation on the revision-7
`independent-moment` card. It does not recompute more digits of a root or
search for another packing. The mathematical optimum and its witnesses remain
PR4091's contribution.

| Checked object | Result |
|---|---|
| Complete pattern census, independently counted by a generating-function recurrence | 5 / 21 / 158 / 657 at capacities 8 / 16 / 32 / 48; 841 total |
| Left / middle / right dual faces | 11 / 8 / 9 identically tight patterns; all others strictly positive throughout the interval |
| Nonzero slack divided by `a`, conservative lower bounds | > 4.38806 / 0.69698 / 2.37161 |
| Central balance matrix | determinant −10; unique `x=1080` and all eight multiplicities recovered |
| Complete objective slope divided by `a` | left in [−0.348858,−0.348494]; right in [4.365719,4.365912] |
| `x=1090` consequence | right-face optimum has five `48:(6,6,9,9,9,9)` bins and idle `{3:22783,5:1625,48:138492}` |

The last row answers the pooled-feasibility question in
[PR5280](https://github.com/CrocSwap/integer-mult-bounds/pull/5280).
The central eight-pattern support alone forces 1080 calls. The central idle
multiset also has ten too few residual rank units for 1090. Thus
[PR4170](https://github.com/CrocSwap/integer-mult-bounds/pull/4170)'s open
question about reaching that same multiset **at 1090** requires changing the
mixture or invoice. These are independently checked consequences of PR4091's
existing formulas, not newly discovered constructions.

## Independence and evidence

The checker imports no predecessor Python. It recovers dual prices from exact
linear equations instead of executing the published formulas. It enumerates
patterns by a Cartesian product and checks every residual count against a
separate coin-generating-function recurrence. Its power enclosures use the
positive binomial series for `(r^(1-a)-r)/a`, integer outward rounding and an
explicit geometric tail. They use no logarithm/exponential engine, floating
acceptance, optimizer or external numerical library.

[PROOF.md](PROOF.md) proves the interval enclosure, weak-duality implication,
unique central optimum and global root-ceiling implication. [RESULT.json](RESULT.json)
records exact rational evidence, the census hash, affine solutions and input
hashes. Only the coarse endpoints `.00173` and `.00174` are evaluated to put
the root inside the dual-certified interval. The published 24-place root
bracket is not freshly verified or refined.

Twenty-one arithmetic/control tests include exact rational-root fixtures, a
Fraction partial-sum oracle, omitted-tail discrimination, missing/duplicate
patterns, a zero-mass perturbation that violates dual feasibility, inadequate
precision, wrong mixture/width/replica factor, an unpaid local charge and
corrupt source bytes. Explicit checks remain active under Python `-O`.

This is an independently implemented audit, author-checked in this package.
There was no separate human, external-agent or formal-kernel review.

## Source and accounting boundaries

Base: `32890bc5de034ab8fc93ac88ead7279a6a416d04`. Audited PR4091:
`a29bdd8f56cd18b805917775cdec09ff935eddc4`; its package is unchanged at the base.
Frozen PR4088: `76088d49e3ed4142a958659aa996b0ca4da5e88e`.

The eight exact input files are pinned in [SOURCES.json](SOURCES.json) and
declared in [VERIFY.json](VERIFY.json). The audit reconstructs helper widths
by explicit binary spans in all four word exports and derives bin counts
from the template and current order. It **inherits the local paid-profile
reports and comparison stock coefficient**. It does not rescan every paid
frame transition or establish native/operator correctness.

The complete bill includes `3240 L3 + x(L4-L3)` and every residual child,
including empty bins, against `(896*360)H73`. Words, whole-helper widths,
capacities, stock and this accounting boundary are fixed. Changing them
requires a new model. The selected PR5413 mechanism is outside this historical
ceiling's scope.

Not checked: chronological/family/offset feasibility, native and dirty-state
identities, source local-profile correctness, actual stock provision, compiler,
all-size, precision/tape, BIT or outer admission. No supplier promotion or
complete multiplication theorem follows from this audit. PR4181's reported
chronological attainment is credited but not replayed here.

## Reproduce

From the repository root, Python 3.12 and its standard library:

```sh
python3 -B scripts/research_package.py --package research/staged-fourth-dual-binomial-audit --check-only
python3 -B scripts/research_package.py --package research/staged-fourth-dual-binomial-audit
```

The registered commands run the checker and all 21 tests in normal and
optimized modes. A direct checker run takes about one second on the measured
Linux/Python 3.12 environment; timing is host-dependent. Expected checker line:

```text
PASS_STAGED_FOURTH_DUAL_BINOMIAL_AUDIT patterns=841 duals=3 tight=11/8/9 unique_x=1080
```

The direct scripts also work from an official export containing the declared
inputs, without Git or network access:

```sh
python3 -I -W error -B research/staged-fourth-dual-binomial-audit/verify.py
python3 -I -W error -B research/staged-fourth-dual-binomial-audit/test_verify.py
```

Add `-O` to check optimized execution. Normal replay compares the complete
canonical JSON result and never rewrites it. Regeneration is explicit:
`verify.py --output PATH`.

## Open next questions

No further fixed-inventory packing search is justified by this audit:
[PR4181](https://github.com/CrocSwap/integer-mult-bounds/pull/4181) already reports
attaining PR4091's cap. A consequential follow-up must name a changed word,
inventory or consumer boundary and derive its complete signed invoice before
reusing a ceiling. The first step is to identify which of the model's item,
capacity, residual or stock equations changes; absent such a source-bound
change, this audit supplies no reason to expand the search. Physical admission
and independent source-transition coverage remain separate obligations, not
closed by these LP checks.

## Credit

Prepared for commdata2338 (@commdata2338), with substantial OpenAI Codex assistance.

Ross Richardson and the credited PR4091 specialists supplied the pooled
theorem, all three duals and the affine witnesses. Cinna Davis/PR4088 supplied
the fixed words and fill. Nick Petalas/PR4170 and unpaidmoon/PR5280 supplied
the source-transfer checks and follow-up questions; their checks explicitly
exclude the pooled dual proof. Rohan Arun/PR4181 supplied the chronological
attainment. Retain Rohan Arun/PR4076; David Ganz (Dugongue)/PR3945 and
zxv/PR4085 with their lineage; dataisfire/PR3734; Erwan Secousses
(ChaloupeMusic)/PR3949/3815; and the original geometry, native, owner, compiler and transfer
contributors credited in PR4091's notices. This account's PR3237 concerned a
different PR2979 final-fill model and is not repeated here.

The new work is the binomial enclosure implementation, independently solved
dual/primal certificate, finite audit and controls. Substantial OpenAI Codex
(GPT-6 Astra) assistance was used for derivation, implementation, checking and
writing. No independent human review is claimed. Apache-2.0.
