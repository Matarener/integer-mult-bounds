# Exact phase defects under fixed-subspace chart constraints

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: scoped algebraic proof with exact finite corroboration. This answers
the literal-axis restriction question left open by merged
[#5225](https://github.com/CrocSwap/integer-mult-bounds/pull/5225), and permits
an arbitrary specified binary subspace W, including degenerate W.

For V=F2^n, fixed sign mask b, and q_b(x)=wt(x)+2(b dot x) modulo four, let
G_W be the orthogonal chart changes fixing W pointwise. The result is

```text
{d_b(S): S in G_W} = {e in W-perpendicular: q_b(e)=0}.
T_e = I + e e^T lies in G_W and attains each such e.
S = T_(d_b(S)) H, with H fixing W and preserving the phase exactly.
```

All defect fibers have equal size. For k fixed literal axes and m=n-k free
axes, their number is

```text
N = sum_{0<=j<=m, j == wt(b_free) mod 4} binomial(m,j).
```

The exact phase-preserver subgroup has order |O(m,2)|/N. Signs on fixed axes
do not affect this count. The all-fixed case has N=1.

The actual fixed subspace matters. At n=4 with all positive signs, fixing e1
permits only defect zero, while fixing e1+e2 permits zero and (1,1,1,1).
These are constraints of the same dimension. [PROOF.md](PROOF.md) gives the
all-width argument, attaining representatives, subgroup fibers and these
specializations. This is a local algebraic result, with no new kappa.

## Evidence and reproduction

The standalone verifier enumerates every orthogonal matrix, subspace and
sign mask through width five. It checks the restricted images, equal fibers,
attaining representatives and full factorization for each admissible matrix.
Its generated counts are:

- 464 subspaces and 13,192 subspace/sign contexts;
- 30,232 attaining representatives and 168,200 restricted factorizations;
- 1,364 literal-axis formula contexts;
- 777 orthogonal matrices and 749,988 literal phase comparisons.

Eight controls distinguish unrestricted charts, fixed sums versus separately
fixed axes, even weight versus phase zero, transported signs, pointwise versus
setwise stabilization, zero versus nonzero correction, and capacity rejection.
These finite checks corroborate the new restriction theorem. The universal
claim rests on the proof and cited unrestricted theorem, not extrapolation.
No predecessor executable is imported or replayed.

From the repository root, with CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/fixed-subspace-phase-defects/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -O -B research/fixed-subspace-phase-defects/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/fixed-subspace-phase-defects
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/fixed-subspace-phase-defects --check-source-history
```

Any CPython 3.12 installation can replace the local interpreter path. The
verifier prints `PASS_FIXED_SUBSPACE_PHASE_DEFECTS` and a generated JSON receipt
binding all six package files by SHA256. It writes nothing. The publication
preflight requires Git history; the direct verifier supports a Git-free export.

## Scope, sources and implementation limits

The base is canonical main de5ec2e7a6074068452f45b1a191b5c72832df4a, priority
revision 8. [TASK.json](TASK.json) changes the `bit-helper-contract` card to
this algebraic side result, because #5225 explicitly leaves this route constraint
open. The card's current selected-binding first step passed. It is metadata
orientation, not a selected supplier replay. [SOURCES.json](SOURCES.json) pins
the predecessor proof and README as provenance, alongside the selected record
and catalogue. They are not runtime inputs to the new verifier.

The advance [CLAIM](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19214412)
followed live open/account PR and Discussion checks, local reservation and
distinctive main/merged searches. The overlap cache completely paginated 416
open PRs and 5,307 Discussion records. Sparse local coverage searched 185 of
7,845 tracked notes; targeted all-main README and merged-PR searches supplemented
it. Unpublished work and arbitrary historical diffs remain outside that coverage.
No search establishes external mathematical priority.

The new verifier is bounded at widths 1..5, at most 720 complete matrices,
374 subspaces and 32 vectors in one width. It has no recursion, subprocesses,
network, dynamic code or shared mutable state. All functions stay below 60
physical lines. Explicit exceptions retain the checks under optimized Python;
both registered commands treat warnings as errors. No additional static analyzer
is configured or claimed. The only file reads are the six local receipt inputs.

Power of Ten rule 3 deviation: CPython allocates integers and containers during
finite enumeration. The enforced width bound limits each subspace to 32 vectors,
the subspace inventory to 374 entries, the group inventory to 720 entries and
the sign/defect table to 32 by 720 integers. No fixed-allocation claim is made.
Normal and optimized complete finite replays exercise this domain. Any executable
width expansion requires a fresh capacity review; the written theorem has no
such finite-width restriction.

The contract fixes W pointwise and retains orthogonal charts and a fixed sign
mask. Setwise stabilization and nonorthogonal charts are outside scope. No native
producer, chart circuit, physical route, acquisition, dirty restoration, stock,
precision, tape implementation, compiler or complete consumer bill is supplied.
Those costs remain unknown. No supplier admission, selected-frontier change or
complete multiplication theorem follows. Lean, Docker and selected scientific
cold replay were not run. Independent human and formal proof-kernel review are
unclaimed.

## Open next questions

Can a named native helper exploit one nonzero admissible defect while preserving
its required literal directions? Start with its actual fixed subspace W and
sign mask b, and price the T_e chart change with all acquisition, transport and
restoration costs. Algebraic attainability supplies none of those prices. This
question is unclaimed here; no further construction expansion is justified by
this package alone.

## Credit

Nick Petalas #5225 supplies the unrestricted mixed-sign theorem and explicit
fixed-axis question. Philipp / mightyOil #1300 supplies the equal-sign phase
model, Gareth Davidson #1255 the residual C-gate contract and row convention,
and yssite #1558 following icekylinx #24 the signed Gauss-normalization context.
Credit Rohan Arun, Jeremy Kothe, Hao Yan, Josie Elliston, Douglas Colkitt and the
retained Clifford/normalization lineage. Classical quadratic refinements,
transvections and subgroup-fiber arguments retain their classical status.
All predecessor notices remain unchanged.
