# A stochastic precision certificate for the selected P104 prefix

This contribution was produced by Nick Petalas. Apache-2.0.

Scoped proof with an exact finite influence certificate. On the selected
#5599 word's first 9,589-event common-frame scalar block, fresh unbiased
fixed-grid stochastic rounding has exact squared influence maximum **733/8**.
For arbitrary incoming grid values, including dirty helpers, six fractional
bits give simultaneous absolute error below 1/2 in every real output at one
stream sample with failure probability below **2^-23**. For both components
of complex outputs the probability is below **2^-22**.

The deterministic nearest-rounding absolute-influence certificate on this
same block gives error at most 45h and needs seven fractional bits to certify
a strict error below 1/2. This is a one-bit improvement between sufficient
certificates with different guarantees. Neither precision is proved optimal,
and the exact intermediate endpoint need not be integral.

The stochastic arithmetic contract is new here. Each noninteger dyadic scalar
update is evaluated exactly and rounded once, with fresh conditional randomness.
Integer-grid operations are exact. No predecessor verifier is imported or
replayed, and no predecessor result is audited. [PROOF.md](PROOF.md) derives
the variance and tail inequalities, explains their classical basis and states
the complete boundary. No new kappa, physical supplier or multiplication
theorem is claimed.

## Evidence and reproduction

The standalone verifier authenticates the frozen selected word and extracts
its prefix before the first MOVE. A reverse integer-column engine and an
independent chronological formal-error engine agree on all 748 output pairs.
The generated stdout receipt includes every output's squared and absolute
influence, the source/package hashes and the exact tail certificate.

The block contains 7,421 potentially rounded updates. Its maximum absolute
influence is 90; 282 outputs have nonzero formal noise influence. The forward
engine retains 8,493 nonzero formal coefficients, at most 98 per output.
An exact positive Taylor polynomial proves the exponential comparison.
All 125 tiny-input fixtures are enumerated, with 423 terminal state occurrences.
No random sampling is used.
Controls distinguish chronological order, altered coefficients, fresh draws
from a reused coin and unbiased rounding from biased ties. All checks remain
active with Python optimization.

From the repository root, using CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -X dev -B research/p104-stochastic-prefix/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -X dev -O -B research/p104-stochastic-prefix/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/p104-stochastic-prefix
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/p104-stochastic-prefix --check-source-history
```

Another CPython 3.12 path may replace the displayed interpreter. Expected
markers are `PASS_P104_STOCHASTIC_PREFIX`, `PASS_REGISTERED_RESEARCH_PACKAGE`
and `PASS_RESEARCH_COMMIT_BYTES`. Each registered command has a 120-second
limit. The direct verifier writes no files. The publication preflight needs
committed files and full source history. A Git-free replay needs this package
and the single live word path declared in VERIFY.json.

## Scope, cost and limitations

The changed `uniform-transfer-audit` scope concerns the selected
`precision_tape` assumption. Source-binding orientation passes, but no selected
scientific replay is performed. Canonical base is
`19fdb086ea96af9a9f87936a2b888e10af4ed810`, priority revision 8.
The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19228531)
records the question. Live open PRs, account history, Discussions, local
reservations, main README contents and distinctive merged-PR terms were
searched. Sparse local cache coverage is incomplete, and these checks cannot
exclude unpublished overlap or establish literature priority.

The prefix uses one empty common frame and no MOVE. The proof is scalar and
pointwise. All incoming values must already lie on the chosen grid; overflow
and saturation are excluded. At M samples a union bound multiplies the stated
failure probability by M. The literal dyadic sampler needs at most 11,713
fresh fair bits per real sample, with integer arithmetic and random-bit
movement still unpriced. Native approximation, input conversion, later blocks,
stream-wide precision, physical random sampling, exact dirty restoration,
compiler/stock obligations and analytic recovery remain unproved. All five
selected framework assumptions remain. Independent human and formal
proof-kernel review are unclaimed. Lean, Docker and full multiplier replays
were not run.

Fresh rounding does not make a rounded inverse restore dirty inputs exactly.
A two-update identity word in the proof can leave a nonzero error. A reused
coin can also violate the variance bound even when its one-step marginals
look unbiased. These limitations prevent interpreting the certificate as an
admitted randomized supplier.

## Credit

Ali Romman's #5599 supplies the selected independent-helper word and split
construction. Pierre-Loic Doulcet / hexapode's #5565 supplies its commuting
contacts. Retain Ali Romman's #5580/#5544/#5545, Joel Pulikkan / GamingPuzzled's
#5569, DreamingOfClouds' #5561, thu-nmrc's #5551, Gareth Davidson / bitplane,
David Arias, Cinna Davis, Jacob Alan Sussman, zxv, Cao Yifan and all geometry,
BIT, native, precision, analytic and source predecessors in the unchanged
[selected notice](../p104-helper-subspace-splits/NOTICE).
SOURCES.json pins that notice and the source README as provenance.

Stochastic rounding and mean-independent error analysis are classical; see
[Connolly, Higham and Mary (2021)](https://doi.org/10.1137/20M1334796).
The proof gives the fixed-grid concentration argument directly. The new
contribution is the exact selected-prefix influence certificate, its explicit
failure bound and the comparison of sufficient precision certificates.

## Open next questions

Can one complete native caller use this rounding model while restoring its
dirty state exactly? Start with a round-and-restore ABI that retains and then
erases its random bits, charging every action. A physical reversible sampler
and its complete cost are the present blockers.

Can a finite sample count and the next actual MOVE preserve a useful total
failure budget? First propagate this block's errors through that native
operator with its own approximation contract. Whole-stream precision and
later blocks are outside this certificate. Structured questions are in
TASK.json.

## Code constraints

The verifier is nonrecursive and uses no subprocess, network, dynamic code
or write path. Fixed source bounds are 26,000 full-word events, 9,589 extracted
events, 748 roles, coefficients with denominator at most four and absolute
value at most 16. Reverse vectors have at most 128-bit numerators and exponent
64; forward rational coefficients have matching bit caps, enforced during
replay. Each formal row has at most 10,000 terms. Source
reads are capped at 1 MiB compressed and 4 MiB unpacked, and six receipt reads
at 1 MiB each. Tiny probability trees have at most eight steps, three roles
and 256 states, enforced during enumeration. The Taylor sum has 65 terms.
Functions fit below 60 physical lines. Warning-strict development-mode normal
and optimized runs are the available diagnostics; no external static analyzer
or whole-repository lint configuration is claimed.

Power of Ten rule 3 has a managed-runtime deviation. Python, Fraction, JSON
and gzip allocate dynamically. The verifier is a finite offline check with
the enforced collection and input caps above, rather than a fixed-allocation
arithmetic implementation. Its matrix and dictionary capacities are finite;
this does not inspect allocator internals or establish a real-time guarantee.
A deployed sampler would need its own storage and random-bit lifetime proof.
