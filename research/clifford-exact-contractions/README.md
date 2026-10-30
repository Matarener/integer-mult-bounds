# Exact phase-sensitive Clifford contractions

This package computes exact inner products, traces, tensor residual norms and
best approximation in a supplied finite span of Gaussian-dyadic Clifford
operators. It uses compact affine supports and quadratic Gauss sums, including
the absolute phase. No dense matrix is required. This lets native-interface
searches test cancellation and publish attained finite-span error certificates.
There is no new kappa or selected-frontier change.

The algorithm and its precise contracts are in [PROOF.md](PROOF.md) and
[contractions.py](contractions.py). `best_approximation` permits dependent source
operators and returns coefficients with an exact orthogonality certificate.
`decide` applies the credited PR5526 four-width theorem to a fixed expanded
residual. It does not provide an efficient expansion of an arbitrary program.

## Evidence

[RESULT.json](RESULT.json) records 4,680 complete affine systems, 67,924 literal
Gauss sums, 2,124 literal state overlaps, 144 small matrix trace comparisons,
and every one of 9,216 kernel entries for all 96 exact one-axis lifts.
The source application covers every one of the 4,268 PR5698/5704 native recipes.
An independent signed-Pauli calculation checks every trace magnitude; seven
full 512-column matrix checks also check absolute phase, one per occurring rank.

Full-support examples at 16, 32 and 64 axes retain at most 128 support columns;
the largest Choi vector has 2^128 entries. Exact phase-residue controls reject
three-width false positives. The two-source C/I/X approximation has the sharp
squared distance 1-2^(1-f), including duplicate sources and widths through 257.
Twelve malformed inputs and three further semantic controls are rejected or
resolved exactly. These are author checks, not independent mathematical review.

## Reproduce

Use CPython 3.12 and its standard library:

```sh
python3.12 -B scripts/research_package.py --package research/clifford-exact-contractions
python3.12 -B scripts/check_research_commit.py --package research/clifford-exact-contractions
```

The registered normal and optimized commands compare the entire receipt. In an
export, run `python3.12 -I -O -W error -B research/clifford-exact-contractions/verify.py`.
All scientific inputs are retained and authenticated before import. [INPUTS.json](INPUTS.json)
and [SOURCES.json](SOURCES.json) bind their bytes. The shallow checkout does not
establish full source ancestry. Hosted replay and independent acceptance remain
separate from local verification.

## Scope and coordination

Base: canonical main df0137efd35e11b4445734bf612bdd4c7ebc330c, priority revision 7.
Selected conditional kappa .00310045 stays unchanged. [The claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/5236#discussioncomment-19197192)
refines the interface task into an exact executable proof contract; it is not a
proof-assistant formalization. The current baseline metadata orientation passed.

The fresh full overlap snapshot and latest PR/Discussion reads covered current
published work. PR5714 optimizes the absolute-row counting method; PR5675 gives
a two-axis full-group spectrum. This package supplies finite phase-sensitive
contractions and source binding, without another spectrum or cutoff claim.
Unpublished work and arbitrary historical diffs remain outside overlap coverage.
The p2 cyclic-generator gap was already closed by PR5618 and was not repeated.

## Open next questions

* Apply the exact optimum certificate to a named paid-history residual with all
  of its independent input and return columns. Start with its literal expanded
  source terms; expansion size and the complete physical bill remain obligations.
* Use phase-sensitive kernels to seek an all-dimension spectral bound beyond
  PR5714's absolute-row limit. A finite Gram sample does not prove that theorem.
* Review the affine intersection, Bell phase and normal-equation contracts
  independently. The complete replay and written proof are available here.

## Credit

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0. The methods are
classical stabilizer simulation and quadratic Gauss sums, including Aaronson and
Gottesman's [inner-product algorithms](https://arxiv.org/abs/quant-ph/0406196),
Dehaene and De Moor's binary quadratic formalism, and
[Bravyi et al.](https://arxiv.org/abs/1808.00128). No literature priority or
optimal simulation-complexity claim is made.

PR5704 supplies the unchanged compact engine; PR5526 supplies the unchanged
four-width theorem. PR5698 supplies the actual native recipe set. Retain
Dugongue/PR5687, Cao Yifan, Cinna Davis, DaysSky, Nick Petalas, Ryanson Jonathan,
zxv, Jacob Alan Sussman and all native/helper/controller/compiler/precision/stock
credit in the frozen notices. The new work is the exact contraction and finite
projection implementation, its proof binding and the independent checks above.
