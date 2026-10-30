# Sharp error floor for contractive P104 Gram deflation

Discarding one real carrier mode through a positive contractive approximation
of the P104 Gram channel has an exact maximum coefficient-error floor of
**1/4**. Projecting away any omitted half-spin root direction attains it.
This is a scoped obstruction with a written proof and exact finite witnesses.
No new kappa or physical supplier is claimed.

Write R for the retained roots of squared norm 2 and K=RR^T/2. The theorem
covers K_D=RDR^T/2 with D real symmetric, 0<=D<=I, and rank D<=7. Its lower
bound uses only the retained D8 subsystem and applies to every admissible
real D. Its upper bound is the explicit dyadic projector D=I-qq^T/2 for an
omitted half-spin root q. [PROOF.md](PROOF.md) gives both arguments.

For some input B e_i every such approximation has output bias at least
|B|/4. Increasing arithmetic precision cannot remove that fixed linear
bias. This blocks treating a contractive one-mode deletion as vanishing
roundoff while keeping the rest of the Gram decomposition fixed. A changed
side correction or consumer must account for the residual.

## Reproduce

From the repository root, using CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/p104-contractive-gram-deflation/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -O -B research/p104-contractive-gram-deflation/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/p104-contractive-gram-deflation
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/p104-contractive-gram-deflation --check-source-history
```

The direct marker is `PASS_P104_CONTRACTIVE_GRAM_DEFLATION`. The registered
replay prints `PASS_REGISTERED_RESEARCH_PACKAGE`. A clean CPython 3.12 can
replace the absolute interpreter path. Replay reads without writing files.
The optional `--output PATH` generates a new receipt outside the checkout;
RESULT.json is generated and bound to every other package file's hashes.

The verifier enumerates 173,056 entries of sixteen new error matrices,
checks the sixteen exact rank-seven projectors and 6,560 integer-direction
fixtures, and retains three rejection controls. These finite checks
corroborate the written all-real-D proof. They do not recheck predecessors.

## Scope, sources and overlap

The original coverage-law-change question is changed to contractive approximate
decoding. The connection to the current complex bottleneck is a possible
carrier-mode saving which exact decoding excludes. This result computes its
unavoidable residual before any native or caller expansion. It supplies no
complete signed invoice or card-level supplier admission.

Base main is `3f0152a32eeebac0df11946dbd50cabe5a7f7839`, priority revision 8.
The selected frontier is unchanged. Historical provenance pins are in
SOURCES.json. The mathematical statement itself covers all D8 root lines
plus any proper subset of one half-spin shell.

For the P104 application, Matarener's [PR6166](https://github.com/CrocSwap/integer-mult-bounds/pull/6166)
at `096938513138868f0ed27639061f1a5054900f96` supplies its orthonormal D8
coordinate identification and sixteen omitted lines. [MISSING.json](MISSING.json)
retains those factual coordinates. This identification is a cited premise,
not independently verified here. Its ternary uniqueness, minimum weight and
code-support questions are separate. The new result concerns real contractive
approximation and introduces no question from that source's open-question list.

Rohan Arun's PR1972 and Chafik Boukhalfa's PR1991 supply the retained Gram
channel convention. Their native/operator results are cited, not replayed.
Ali Romman's PR5526 concerns Clifford-history error versus paid returns;
it is a different approximation contract. The present result neither uses
nor checks its call-cap or native tensor arguments.

## Limits and engineering notes

Unrestricted rank-seven matrices, nonsymmetric or noncontractive filters,
masked-entry accuracy, changed source encodings and nonlinear consumers
remain outside the theorem. The bias might be corrected elsewhere in a new
word. No restoration, ordinary-cost, native, physical caller, precision/tape,
compiler, BIT, outer, Lean or full multiplication-theorem replay is supplied.
Independent human and formal proof-kernel review are unclaimed.

The verifier has bounded loops, no recursion, functions below sixty lines
and explicit failure checks. Standard-library collection allocation is a
managed-runtime deviation from static allocation;
root tables have at most 120 rows of eight integers, and one error histogram
has at most 10,816 entries counted into integer bins. No shared code or
repository-wide diagnostics configuration is changed.

## Open next questions

- Can a noncontractive or nonsymmetric rank-seven factor beat 1/4 in maximum
  entry error? It would escape the positive-error argument. Start with an
  explicit rational factor and certify every coefficient; its physical
  realization and stability would still need a separate bill.
- Can a changed side correction absorb the explicit rank-one residual with
  a favorable full invoice? Start from one omitted-root projector and track
  its residual through an actual scalar word. No such caller is supplied.

## Credit

This proof and verifier were produced by Nick Petalas. Matarener retains the
P104 D8 coordinates and omitted-root list. Rohan Arun, Chafik Boukhalfa and
their retained native/root/frame predecessors retain the Gram-channel
construction. Ali Romman, DreamingOfClouds, Cinna Davis, Pierre-Loic Doulcet,
icekylinx, zxv, Jacob Alan Sussman and the retained P104/helper/compiler/BIT
contributors retain their source results. Root geometry, orthogonal
projection and positive-semidefinite order are classical. No general
literature-priority claim is made. Apache-2.0.
