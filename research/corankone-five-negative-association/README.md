# Five binary full-guard indicators are negatively associated

This contribution was produced by Nick Petalas. Apache-2.0.

**Claim type: scoped proof with an exact finite component. No new kappa.**
For five pairwise orthogonal rank-one idempotents U_i on F_2^m, draw a
complete uniform header G in GL_m(F_2), with m>=5. Let Z_i indicate that
all leading principal minors of G(I-U_i)G^-1 through order m-1 are nonzero.
Then any two nonconstant increasing real functions of disjoint nonempty
subsets of the five indicators have strictly negative covariance.

This settles Open next question 1 of Krzysztof Wojt's
[PR #5093](https://github.com/CrocSwap/integer-mult-bounds/pull/5093).
That predecessor proves the four-indicator theorem. The new comparisons
cover the 4+1 and 3+2 support splits; the existing fivefold-intersection
inequality alone does not settle them. The statement covers every integer
m>=5, rather than extrapolating a finite dimensional sample.

## Proof and evidence

[PROOF.md](PROOF.md) gives the argument. Subset Mobius inversion and
exchangeability reduce all 277 labelled increasing-event pairs to 37
covariance-gap power sums. Eleven correspond to the earlier support types;
26 additional types complete the five-indicator case. Every gap has a
positive exact finite prefix and a strict leading-term tail bound.
Superlevel-set decomposition then gives the assertion for real functions.

The self-contained standard-library verifier checks:

- All 1,4,18,166 nonconstant monotone Boolean truth tables on one through
  four inputs, including reconstruction of every truth value.
- All 37 expanded gap polynomials, 4,498 exact finite-prefix comparisons,
  37 uniform tail certificates and 111 additional tail identity probes.
  The largest tail begins at n=m-1=179, hence m=180.
- All 277 labelled pairs by direct 32-atom truth-table evaluation at
  m=5,6,8,16, giving 1,108 independent-path covariance comparisons.
- Ten domain, sign, cutoff, tail-mass, finite-denominator and distribution
  controls. Checks use explicit exceptions and remain active with -O.

Every run prints PASS_CORANKONE_FIVE_NEGATIVE_ASSOCIATION and a generated
receipt bound to all six package-file hashes. It writes no files and needs
neither Git nor network. The moment laws and spectra are cited inputs;
no predecessor executable is imported or independently audited here.

## Reproduce

From the repository root:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/corankone-five-negative-association/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/corankone-five-negative-association/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/corankone-five-negative-association
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/corankone-five-negative-association --check-source-history
```

Use another CPython 3.12 path on other machines. The publication preflight
requires a committed package and full history. Both registered scientific
commands use warning-strict isolated Python and have a 60-second cap.
Local command times and hosted CI status are recorded in the PR body.

## Scope and provenance

Scientific base is canonical main de5ec2e7a6074068452f45b1a191b5c72832df4a,
priority revision 8. TASK.json records the changed formal-interface-lemma
scope: an original dependence side result, without a proof-assistant claim.
SOURCES.json pins predecessor proof texts and code as historical provenance;
none is a runtime import. The selected-baseline source-binding orientation
passes after materializing its sparse inputs. It is not a scientific replay
or a premise of this theorem.

The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19213528)
records the question. Live open/account PR lists, latest handoffs, active
Discussions, distinctive main-tree README searches and merged-PR searches
were checked before claiming. The cached overlap report had incomplete sparse
local-note coverage. Unpublished work and arbitrary historical diffs are not
covered, and global literature priority is unclaimed. Submission freshness
and related open work are recorded in the PR.

The theorem fixes binary orthogonal kernels and the whole uniform header
measure. It gives no six-indicator, odd-field, conditioned-header or
nonorthogonal-kernel result. Physical header generation, selection, emission,
dispatch, dirty restoration, stock, precision and a paid consumer remain
unpriced. No supplier admission, multiplication theorem or selected-frontier
change is claimed. Independent human and formal proof-kernel review are
unclaimed. No Lean, Docker, native build or selected scientific cold replay
was run.

The verifier has no recursion or shared mutable state. Functions are under
60 physical lines. Truth-table candidates are bounded by 65,534; moment
fixtures are bounded by m<=359 in the actual run and an enforced m<=513
entry contract. The largest collected polynomial has 512 terms; every
multiplication enforces a 4,096-base capacity bound. Exact Python integers,
Fractions and bounded containers use managed dynamic allocation. This is a
documented deviation from fixed allocation, with fixed finite data domains;
there is no constant-bit-space claim. The controls use eight explicitly
listed local callbacks, the only indirect test-call targets. Warning-strict
normal and optimized execution supplies the available Python diagnostics.

## Open next questions

1. Does negative association persist for six orthogonal binary full-guard
   indicators? This would cover larger shared-header groups. First obtain
   a justified six-event moment input, then classify the new 5+1, 4+2 and
   3+3 increasing-event comparisons. The six-event spectrum and new mixed
   inequalities are absent here; no larger census is reserved.
2. Can a concrete paid caller realize and use the complete uniform-header
   premise? Start with its actual request family and sampling rule, then
   price selection, emission, dispatch and restoration. The missing physical
   consumer and complete bill prevent treating dependence as a kappa gain.

## Credit

Krzysztof Wojt #5093 supplies the four-event theorem, explicit five-event
question, and the power-sum/Mobius verification method adapted here.
lee-phys #5073 supplies the three-event theorem and earlier question.
Ryanson Jonathan #4607 supplies the cited five-event signed spectrum.
Nick Petalas #4227/#4261/#4275/#4599 supplies the marginal, joint character
laws and four-event spectrum. Cinna Davis's BIT request context, source527,
commdata2338, Jose Manuel's normalizer/closure lineage and Chris R /
Clear1nsight's counting context retain the attribution in those sources.
The new contribution is the 26 additional gap types and their complete
finite-prefix/tail proof, giving five-indicator negative association.
