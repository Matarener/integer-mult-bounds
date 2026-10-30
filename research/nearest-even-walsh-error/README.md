# Sharp nearest-even Walsh-stage error

This contribution was produced by Nick Petalas. Apache-2.0.

For J distinct normalized Walsh stages, with exact sums and differences
and nearest-even rounding to a common grid h after each stage, the sharp
uniform error over every grid input is

    h [J/3 + (1-(-1/2)^J)/9].

The usual stagewise bound is J h/2. The new bound is strictly smaller
for J>=2 and approaches two thirds of that coefficient. This is a scoped
mathematical proof with exact finite corroboration, not a new kappa.

[PROOF.md](PROOF.md) proves the even/odd output recurrence and constructs
attaining integer inputs for every J. At even stored outputs the maximum
is h a_J; at odd outputs it is h a_(J-1). The attaining even-output inputs
use only integers between -J and zero in grid units.

## New source application

CubeJerry's [PR #6119](https://github.com/CrocSwap/integer-mult-bounds/pull/6119)
reports normalized error at most 3/16 on a finite cube for its particular
two-phase nearest-even surrogate at h=1/4. Its separate arbitrary-defect
box has a sharp bound of 1. The present result proves **3/16 is the exact
global error for every grid input** of that surrogate. Exact raw recovery
gives the sharp value 3/4. Its rounded echo returns the temporary row to
zero on every such input. This does not establish a physical erasure cost.

The source is pinned as a literature reference at
`bdfe5a10d488b5f774e906d8d4588dc8da25e7ba`. Its explicit m=1/2,a=4 echo
becomes identity on grid inputs; the remaining computation is two rounded
Walsh axes. One new attaining original-coordinate input is
`(0,0,-1/4,0,-1/2,0,0,0)`. No predecessor verifier or census is imported,
executed or offered as this contribution.

## Reproduce

From the repository root, CPython 3.12 and the standard library suffice:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/nearest-even-walsh-error/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/nearest-even-walsh-error/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/nearest-even-walsh-error
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/nearest-even-walsh-error --check-source-history
```

Another CPython 3.12 interpreter may replace that absolute path. The last
command checks publication bytes after committing. Direct verification
prints a generated SHA256-bound JSON receipt with status
`PASS_NEAREST_EVEN_WALSH_ERROR` and writes no files.

The exact finite coverage is:

- 2,049 signed half-integers checked against a separate exact Fraction
  nearest-even implementation, including the tie-output parity.
- All 16 one-stage and 4,096 two-stage residue inputs, with every output
  compared to the literal Walsh coefficient formula. Error periodicity
  makes these complete integer-input domains at those two depths.
- Reachable error sets classified by output parity through depth seven,
  independently of the proposed closed formula.
- Even- and odd-output attaining witnesses through depth twelve, in both
  low-bit-first and reversed schedules, with every output checked and
  negative witnesses checked by actual execution.
- 256 signed periodicity fixtures through eight stages, 513 echo values
  and 65 full eight-coordinate source-application fixtures.
- Four scope controls and five rejected invalid inputs. Off-grid data
  give error 7/8 at J=2; different tie rules can give error 1. These
  explicitly reject unwarranted extensions of the 3/4 grid-unit theorem.

The finite checks corroborate the all-J written proof. They do not replace
its quantifiers or supply independent human or proof-kernel review.

## Scope, provenance and overlap

The original `uniform-transfer-audit` card is explicitly changed to this
numerical side theorem for the `precision_tape` boundary. It does not
discharge any selected framework assumption. The authenticated selected
metadata baseline passed at main
`721c03822c421b7f7fcbb2598993b947c4d88419`, priority revision 8. Its selected
conditional kappa is 0.003125804. No selected cold replay was needed or run.

This is a new quantizer-specific step beyond PR6119's finite cube, not an
audit of its arbitrary-defect theorem. Source questions and exact reference
heads are in [TASK.json](TASK.json). The
[advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19241916)
records the expected scope. Live PRs, recent account work, Discussion
claims, local reservations, main text and merged-PR searches were checked.
The overlap cache covered 379 open PRs and 5,777 Discussion records with
complete remote pagination, but only 70 of 8,348 local note paths. Direct
Git searches supplemented that sparse coverage. These are bounded overlap
checks, not proof of global novelty.

The theorem requires grid input, distinct Walsh axes, the specified tie
rule, exact pre-rounding arithmetic and sufficient range. Arbitrary faults,
non-grid inputs, other gates, repeated axes and complex Gaussian butterflies
need separate bounds. A real emitted recursive caller, bit costs, overflow
guards, tape routing, reversible history and supplier admission remain open.
The selected frontier and all five assumptions are unchanged. No Lean,
Docker, full native replay or complete multiplication theorem is claimed.

## Engineering bounds

The verifier has no recursion, subprocesses or external mathematical imports.
Its transform accepts at most 4,096 entries and signed inputs of magnitude
at most 2^64. The formula interface permits depths through 64; executed
full witnesses stop at twelve. Every function is below 60 physical lines.
The largest explicit exhaustive input domain has 4,096 tuples; the parity
enumeration stops at seven and stores at most 627 errors in one parity set.
All checks use explicit exceptions and remain active under optimization.

Python's required dynamic allocation is the bounded managed-runtime
deviation from Power of Ten static allocation. Lists, integer sizes and
set domains are bounded by the fixed limits above. Receipt reads are
limited to twelve package files of at most one MiB each. Warning-strict
normal and optimized checks provide runtime diagnostics; no shared build
configuration is changed. This offline verifier is not a machine-cost model.

## Open next questions

1. Bind the sharp bound to an actual emitted recursive H0 boundary with
   its grid, axis ordering, pre-rounding arithmetic and range guards.
   First export that complete event list; it is missing here. The smaller
   logical error coefficient alone supplies no accelerated physical bill.
2. Can an analogous parity-state analysis sharpen deterministic rounding
   for the actual complex Gaussian butterflies? Start with their joint
   real/imaginary parity states. Their mixing and error amplification
   differ from this real averaging tree, so this formula does not transfer.

## Credit

Credit CubeJerry for PR6119's explicit surrogate and separation between
defect boxes and quantizer correlations; Vlado Vojdanovski for PR1673's
normalized H0/deferred-row interface; and JoyboyBrian for related pair-first
nearest-even Gaussian butterfly arithmetic and parity constraints. Their
native, analytic, compiler and selected-construction predecessors retain
their attribution. The new result is the all-J parity recurrence, its
sharp attaining family and the all-grid two-phase consequence. Independent
human and formal proof-kernel review are unclaimed.
