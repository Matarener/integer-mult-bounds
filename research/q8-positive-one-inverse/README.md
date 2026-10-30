# One inverse Q8 target with positive paid labels

An arbitrary finite dirty workspace cannot reduce the separate direct bill
when exactly one requested generator has a negative sign. This is a written
formal theorem, with a bounded exact replay. It gives no native supplier or
new kappa.

The paid labels are positive i,j in F2[Q8], with prices alpha,beta>=0.
Calls are binary rank-one idempotent factors `I+([g]+1)uv^T`, and arbitrary
scalar GL mixing is free. Every role begins with arbitrary independent dirt.
Targets are drawn from {1,i,zi,j,zj}, and all identity spectators must restore.
Let s_i count i/zi targets and s_j count j/zj targets. With exactly one zi
or zj target, the exact minimum bill is

    alpha*s_i + beta*s_j + 2*min(alpha,beta).

For example `diag(zi,i,j,1)` needs five positive-label calls at unit prices,
and costs exactly 13 at alpha=2,beta=5, regardless of extra restored dirt.
The inverse-label bill would be three calls. A positive-label implementation
must add two calls from the cheaper class to create the sign. With no negative
target the minimum is the generator baseline. With two or more negatives,
this package proves only a single two-call excess lower bound.

## Why the extra two calls are forced

[PROOF.md](PROOF.md) gives the universal argument. Full formal coefficient
support forces rank X and rank Y at least the active role count W. The
combined first-order character gives XY=P onto those active roles. Equality
n=W would make the restricted X,Y square inverses, hence YX=I. The paid
projectors would then be mutually orthogonal, so every higher-degree term
vanishes. Positive i,j factors could have no zi/zj coefficient. Binary trace
parity excludes W+1 calls. Separate label ranks and the direct construction
give the exact weighted tariff, including zero prices.

The equality argument is the new sign-sensitive step. It answers one boundary
of [PR3450's positive-only handoff](https://github.com/CrocSwap/integer-mult-bounds/pull/3450).
Aaron Wang's PR2318 already checks all two-role unit-price targets, including
these values. This adds arbitrary roles, arbitrary restored dirty workspace
and arbitrary nonnegative real label prices. It does not claim new two-role
values or a theorem for all signed target lists.

## Reproduce

Python 3.12+, standard library only, from the repository root. Set TMPDIR to
an existing private directory outside the checkout for behavioral exports.

```sh
python3 -I -Werror -B scripts/research_package.py --package research/q8-positive-one-inverse
python3 -I -O -Werror -B research/q8-positive-one-inverse/verify.py
python3 -I -Werror -B research/q8-positive-one-inverse/test_package.py
```

Expected markers are `PASS_Q8_POSITIVE_ONE_INVERSE`, three passing behavioral
groups and `PASS_REGISTERED_RESEARCH_PACKAGE`. Replay writes no package files.
`verify.py --write NEW_PATH` recomputes the typed receipt and refuses to
overwrite an existing path. [RESULT.json](RESULT.json) records:

- All 180,709 positive-label words of lengths zero through three at one,
  two and three roles. Every applicable endpoint satisfies the support floor,
  parity and no-signed-saturation conclusion; saturating words satisfy YX=I.
- All 404 target lists of widths one through four with at most one negative,
  at seven price pairs including zero and rational prices, giving 2,828 cases.
- 83,328 faithful regular-action input columns, including noncommuting mixed
  words and identity spurs that touch restored spectators. The Hamilton
  quaternion engine imports no primary model code.
- 1,648 deleted-factor controls, a quotient-only false positive, wrong actual
  endpoint/tariff producers, invalid operation and theorem-scope rejection,
  source drift, typed receipt changes, optimized CLI and overwrite rejection.

Finite checks corroborate the written theorem. They do not search all word
lengths or establish the universal quantifiers. [VALIDATION.md](VALIDATION.md)
records the engineering bounds, diagnostics and verification limits.

## Sources and credit

Canonical main is `6f100d4bb5083f8c35d96fd95a539811c62f245c`, priority revision 6.
[SOURCES.json](SOURCES.json) pins the canonical PR2587 proof and PR2318
certificate. The unmodified PR3450 proof at
`bf2ff78238472f343a1dfcd70c66dfec7aab883a` is retained and SHA256-authenticated
inside this package, so replay needs no unmerged foreign Git object or fetch.
The task catalogue and selected record are historical provenance.

Credit ywz65/PR2587 for full coefficient support and the restricted positive
tariff, Aaron Wang/PR2318 for both two-role alphabets and finite minima, and
Nick Petalas/PR3450 for the combined character and inverse-label tariff.
Retain Cinna Davis/PR1925/2047/2248, steph4n-gh/PR1573, Tuafo,
eumemic/PR288, Ali Romman/PR468, Gareth Davidson/PR1333, Navinor/PR1822,
woklerx/PR1443 and the retained register-model lineage. Arham Tahir/PR3137
supplies a separate physical compiler and caller contract; peer work on its
scalar preparation distance is disjoint from this formal word tariff.
New work is Apache-2.0. Nick Petalas.
Independent human and formal proof-kernel review are unclaimed.

The [canonical investigation](https://github.com/CrocSwap/integer-mult-bounds/discussions/2034#discussioncomment-19009913)
records the claim and status. Initial overlap covered fully paginated 368
open PR bodies, 2,761 closed PR bodies and 2,285 Discussion records at
02:33-34 UTC on 2026-10-18. This excludes arbitrary diffs and unpublished work.
Submission refresh at 02:39-40 UTC kept canonical main and guidance unchanged.
Complete pagination covered 372 open and 2,761 closed PR bodies plus 2,299
Discussion records. The positive-only claim and peer scalar-conjugation task
remain disjoint; no competing one-inverse theorem appeared in that coverage.

## Open next questions

For at least two negative generator targets, can sign correction be shared
across roles? The present bound adds two calls once; separate construction
adds two per negative. Start with a sign-coefficient rank invariant or one
literal positive-label word with complete dirty restoration and its full
direct alternative. PR2318 already settles two-role unit prices. The new
obligation is arbitrary dirty workspace or a genuinely different priced
boundary. [TASK.json](TASK.json) records the precise gap.

Physical implementation, actual caller, ownership, access, movement and the
complete supplier bill remain separate. Idempotence is needed for trace
parity; free clean inputs, nilpotent factors, other target classes and
projector-dependent prices are outside the statement. The selected cold
replay is unrun because its construction and sources are unchanged.
