# Exact integer height for a logarithmic compiler guard

Scoped mathematical proof, produced by Nick Petalas. Apache-2.0.

For the fixed guard in Richard Hoekstra's
[PR #5787](https://github.com/CrocSwap/integer-mult-bounds/pull/5787),

```text
(H+1)^322 < 2^(H/700000000000), H a positive integer,
```

the minimum height is exactly **12040587444441491**. Every larger integer
height passes, and every smaller positive integer height fails. This is
**112555558509** below the cited sufficient grid height 12040700000000000.
The separate guard H>8192 also holds.

The new step removes the restriction H=ceil(j/d) for this inequality. It
does not audit the predecessor's complete caller, or claim that its full
application has already been instantiated at the smaller height. The
selected frontier and kappa do not change.

## Proof and evidence

[PROOF.md](PROOF.md) proves that ln(1+H)/H strictly decreases for H>0.
Consequently exact opposite signs at two adjacent integers settle the
entire positive integer domain. For D(H)=H/700000000000-322 log2(H+1),
the checker proves the rational brackets

```text
-36/10^15 < D(12040587444441490) < -35/10^15
1354/10^15 < D(12040587444441491) < 1355/10^15
```

verify.py uses an exact positive odd-power logarithm series and outward
dyadic rounding. independent.py uses a separately implemented alternating
Mercator series and imports no primary or predecessor executable.

Local CPython 3.12.15 warning-strict checks pass both adjacent comparisons,
1024 small exact integer-power comparisons, 65 exact power-of-two logarithms
and 17 rejection controls. These are finite checks supporting the written
all-height proof. They are not proof-kernel or independent human review.

## Reproduce

From the repository root:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/integer-carrier-height/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/integer-carrier-height/independent.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/integer-carrier-height
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/integer-carrier-height --check-source-history
```

Any CPython 3.12 interpreter can replace the local executable path. The
standalone scripts use only the standard library and work without Git.
An optional `verify.py --receipt /absolute/output/path` writes a generated
receipt binding every package file's SHA256. Ordinary checks write nothing.

Expected markers:

```text
PASS_INTEGER_CARRIER_HEIGHT minimum=12040587444441491 reduction=112555558509 small_exact=1024 controls=13
PASS_INDEPENDENT_INTEGER_HEIGHT minimum=12040587444441491 adjacent_signs=2 exact_powers=65 controls=4
```

## Sources and credit

Richard Hoekstra's PR #5787 at exact head
08f0e5899254aa82288a91e70789049dc1f29690 supplies the fixed parameters,
the complete paid-tail application and the explicit unclaimed integer-height
boundary. Its PROOF.md and frontier.py are retained verbatim in retained/.
[PREDECESSOR.json](PREDECESSOR.json) records their origin paths, Git blobs
and SHA256 hashes. They were retrieved from the repository contents API at
that exact head. The checker verifies both hashes and source parameter
literals, but never executes the predecessor code or reruns its result.
Retaining these two interface sources makes replay independent of an
unmerged commit's availability. The source-history preflight separately
checks the ancestor provenance in SOURCES.json.

The source retains zxv's logarithmic compiler, Jacob Alan Sussman's mixed
flow, Chris R/Clear1nsight's #5413 caller and exact arithmetic, Dillon
Amburgey's provider, Ali Romman's controller, Cao Yifan's native word,
Cinna Davis's helper/product lineage and their cumulative notices.
The new integer-height theorem and checkers are produced by Nick Petalas.
Independent human and formal proof-kernel review are unclaimed.

The upstream checkpoint is de5ec2e7a6074068452f45b1a191b5c72832df4a,
priority revision 8. TASK.json records the changed scope from an audit card
to original parameter optimization, the overlap limits and next question.
The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19217785)
states the same guard-only scope.

## Limitations

This proves the exact threshold of one fixed logarithmic inequality. It
does not minimize over p, d, compiler geometries, paid profiles or suppliers.
The full changed-height finite-template, precision, conjunction, layout and
physical implementation obligations remain open. No predecessor supplier
replay, selected cold replay, Lean build or complete multiplication theorem
is supplied. No scientific obligation is delegated to CI alone.

The new checkers use managed Python fractions. Their fixed series lengths,
64-bit height domain, fixed small control domains and at-most-32-file receipt
inventory bound the work. Runtime allocation remains a managed-language
deviation from Power of Ten's static-storage rule. No recursion, dynamic
code execution, numerical logarithm library or optimization-sensitive Python
assertion is used in the new checkers. Retained code is an immutable cited
source and is not executed.

## Open next questions

Can the full PR #5787 finite-template and precision application be instantiated
at this exact height? Start by deriving its height-dependent counts,
rounding, precision and conjunction guards at H=12040587444441491, with every
paid tail retained. A complete changed-N application and any required layout
integrality are missing. This package's logarithmic threshold alone does
not settle those obligations.

## Related open work

- [#5787](https://github.com/CrocSwap/integer-mult-bounds/pull/5787) supplies
  the complete #5413 carrier application and sufficient grid height. This
  package proves the minimum integer height for its fixed logarithmic guard.
- [#5899](https://github.com/CrocSwap/integer-mult-bounds/pull/5899) determines
  a different PR5756 tail-gate block-length threshold. It does not compute
  this #5413 integer-height guard, and is not a predecessor of this result.

Merged PRs #5462 and #5468 refine the #5413 saving and its gap-parametric
precision. They retain sufficient height grids and do not compute this
fixed guard's minimum integer height. This package changes neither result.

## CI notes

Hosted replay is pending. All registered scientific commands run locally;
no hosted scientific pass is claimed in advance.
