# Exact error price of unbiased random query compression

This contribution was produced by Nick Petalas. Apache-2.0.

Scoped algebraic proof with finite corroboration; no new kappa. For an
input-independent unbiased random linear response on `k` lanes, with hard
rank cap `R`, the exact worst-input relative mean-square error at expected
rank-power bill `B=b R^t`, `0<t<1`, `0<b<=1`, is

```
omega_min = k/(b R) - 1.
```

Arbitrary complex encoders and decoders do not improve this frontier. Uniform
coordinate projection, with a random zero branch and the specified rescaling,
attains it. At `R=k`, the only optimal response law is a lottery between zero
and `I_k/b`. Every intermediate nonzero response rank is strictly too expensive
to attain the frontier under the concave tariff.

For unrestricted rank and normalized error tolerance `omega<=epsilon^2`,
the maximum expected fractional bill saving is exactly
`epsilon^2/(1+epsilon^2)`. At `epsilon=2^-6` it is `1/4097`. These are relative
MSE units, with no identification of six with a selected precision guard.

[PROOF.md](PROOF.md) gives the universal proof, attaining finite law and equality
classification. The trace/rank inequality and ordinary uniform sparsification
are classical. The contribution is their exact concave rank-power query
frontier, with random workload size, worst-input error and the full-rank
optimizer restriction. This is an original changed-interface investigation,
not a replay or audit of a previous construction. No literature priority is
claimed for those classical tools. See Safaryan, Shulgin and Richtarik's
[compression uncertainty paper](https://arxiv.org/abs/2002.08958) for the
ordinary random-sparsification variance and a different bit-communication
uncertainty model.

## Connection and limits

The optimistic one-layer interface asks whether `k` independent copies of
a common unitary job can be replaced by an unbiased low-rank random linear
sketch. Its scalar lane response is `A`; error for `A tensor Q` against
`I tensor Q` is exactly the same as error for `A` against `I`.

The declared price `rank(A)^t` is an assumption. Lane rank is not automatically
a selected recursive frame rank. A physical application must establish a
response-rank-to-complete-price bridge, or another price which dominates
this one, with the same normalization. Acquisition, encoding, decoding,
randomness, dirty restoration and all other charges are granted free here.
No native implementation, selected caller, signed supplier invoice, recovery
probability or new exponent is supplied. The exact frontier is an obstruction
inside this relaxation, not a universal finite-network limit.

Input-dependent matrices, bias, nonlinear decoding, promised input subspaces,
feedback and verification/retry are outside the theorem. The written proof
covers complex matrices and real `t`; the executable uses the finite real
rational domains below. Independent human and formal proof-kernel review are
unclaimed. No selected scientific replay, Lean or Docker run was performed.
The five selected framework assumptions remain.

## Evidence and reproduction

From the repository root, using the CPython 3.12 standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/randomized-query-power-frontier/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/randomized-query-power-frontier/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/randomized-query-power-frontier
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/randomized-query-power-frontier --check-source-history
```

Another CPython 3.12 installation can replace the displayed local path.
The direct marker is `PASS_RANDOMIZED_QUERY_POWER_FRONTIER`. A run prints
a generated JSON receipt, including the environment and hashes of all six
package files. It writes nothing; redirect stdout to an external scratch
file to retain the receipt. Registered normal and optimized runs have
120-second limits and retain every explicit check.

The finite checks enumerate:

- 204 attaining probability laws at `k=1..8`, every cap `R=1..k`, and
  `b` in `{1,1/2,2/3,1/4}`. Coordinate laws and Walsh-conjugated laws for
  power-of-two `k` have their complete means and every covariance entry
  checked. Their 3,308 outcome records include the explicit zero record,
  even when its probability is zero, and repeated matrices across laws.
- All 19,767 matrices of dimensions one, two and three with entries in
  `{-1,0,1}`. The trace/rank inequality holds; all 46 nonzero equality
  matrices also pass the literal scalar-projector identity and symmetry.
- 8,320 exact integer-power tariff comparisons at `R=1..64`, every positive
  `r<=R`, and exponents `{1/2,2/3,9/10,499/500}`. Exactly 8,064 are strict.
  The normalized tolerance formula is checked at every `g=0..16`.
- 18 control cases, including invalid dimensions, probability sign/sum,
  rank-cap violations, biased laws, corrupted scaling, omitted thinning
  noise, confusing mean rank with power price, and every independent
  average of one through eight Bernoulli whole-job samples.

The universal result follows from the written proof. These finite checks
corroborate its identities and hypotheses rather than enumerate its infinite
domain. No predecessor program or scientific census is imported.

## Scope and source record

Base canonical main is `721c03822c421b7f7fcbb2598993b947c4d88419`, priority
revision 8, selected PR6030. The baseline source-binding orientation passed
after materializing its omitted sparse inputs. It is not an operator replay.
The [advance CLAIM](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19241914)
declares this stochastic contract. [TASK.json](TASK.json) preserves the original
card and explicitly changes its scope to an optimistic algebraic side result.
[SOURCES.json](SOURCES.json) binds the catalogue and selected record as historical
provenance. There are no external runtime inputs or pending Git dependencies.

Live open/account PRs, active Discussions, recent handoffs, merged term searches
and main's omitted README files were checked before reservation. The overlap
cache reports complete pagination for 379 open PRs and 5,782 Discussion records,
but omits 8,278 local note paths from its sparse working-tree scan. Separate
Git searches covered the proposed object's terms on main. These searches are
bounded coordination evidence, not a proof of novelty. The deterministic
multi-bank shear question in #6114 has a different contract and is not
answered here.

Power of Ten inspection finds no recursion, dynamic code, subprocesses or
background work. Functions fit within 60 lines. Loops have fixed domains,
matrices have at most eight rows, and one law has at most 71 outcome records.
The exhaustive matrix domain is at most `3^9` per dimension. Source-hash reads
are capped at 256 KiB per file. Python allocates managed objects dynamically,
a deviation from fixed allocation; the fixed domains bound live mathematical
state. Revisit those capacities before increasing the domain. Explicit checks
survive optimized Python, and warnings are errors. No external static analyzer
or proof assistant is claimed.

## Open next questions

1. Can one actual common-query supplier establish the response-rank-to-price
   bridge and pay its full caller costs? Start with a named additive layer,
   its response map and every paid rank and restoration obligation. The
   physical producer/consumer and matching tariff are missing.
2. Can bias or input-dependent coding yield a favorable complete cost with
   certified recovery? Start with one approximation and verification/retry
   contract, charging every retry and worst-input error. No such recovery
   proof or selected precision allowance is supplied here.

Structured relevance and blockers are in TASK.json. No further search or
construction was undertaken after the sharp frontier was obtained.
