# A bounded fair-bit cap cannot exactly round the denominator-13 inverse

A stochastic extension of the retained denominator-13 inverse cannot use a
hard cap of fair bits, always return a rounded integer, and remain exactly
unbiased. A bounded sampler can instead accept a quantified bias or return
an explicit failure. Both tradeoffs have sharp closed forms.

There is an exact standalone sampler with expected draw count two, and that
expectation is optimal. Its worst-case draw count is unbounded. A tempting
bounded retry construction fails: cap that sampler at four bits, restart its
unfinished branch, and the desired probability **1/13 becomes 1/15**.
The correct exact conditional sampler needs abort probability at least **3/16**.

This is a scoped arithmetic/randomness theorem and failed-construction analysis,
not a new inverse implementation, native supplier or κ. The denominator-13
service in the pinned source is deterministic; it does not claim the stochastic
substitution tested here.

## Source-relative changed contract

[PR #5069](https://github.com/CrocSwap/integer-mult-bounds/pull/5069)'s physical
inverse-coded pair uses the exact mode identity

$$
A=I-MM^T/4,\qquad M^TM=56I,\qquad A^{-1}=I-MM^T/52.
$$

In particular $A^{-1}M=-M/13$. Its retained
[PR #5037](https://github.com/CrocSwap/integer-mult-bounds/pull/5037) grid kernel
uses deterministic approximation and does not give reversible cleanup.
The proposed change is to use unbiased stochastic grid rounding of a
non-dyadic scalar value, motivated by
[Nick Petalas](https://github.com/petalas)'s
[PR #6026](https://github.com/CrocSwap/integer-mult-bounds/pull/6026) dyadic
stochastic prefix and the coupled inverse ABI in
[PR #6066](https://github.com/CrocSwap/integer-mult-bounds/pull/6066).

For a scalar value whose fractional part is $a/b$, adjacent-grid stochastic
rounding must choose the upper grid point with exactly that probability.
The calibration $a/b=1/13$ tests a denominator intrinsic to the inverse, not a
claim that every reached service operand has that fraction. Actual reachable
residue classes and caller propagation still need a separate source-bound
analysis. No defect in the deterministic predecessor is alleged.

## Sharp finite-bit bias bound

Fix coprime integers $0<a<b$, with odd $b>1$. A standalone algorithm has a
fixed input, no free initial random state, and at most $R$ fresh independent
fair bits. It may branch adaptively and stop early, but always returns zero
or one. Pad every early termination with unused bits. It is now a function of
exactly $N=2^R$ equally likely strings. Its success probability is $k/N$ for an
integer $0\leq k\leq N$.

Let $r$ be the remainder of $aN$ upon division by $b$. The best possible total
variation error from the desired Bernoulli law is

$$
\boxed{\epsilon_R=\frac{\min(r,b-r)}{bN}>0.}
$$

Indeed the closest integer to $aN/b$ is one of its floor and ceiling, at distances
$r/b$ and $(b-r)/b$. Choosing the corresponding number of successful bit strings
attains the bound. Since $b$ is odd and $a,b$ are coprime, $r$ cannot be zero.
The same lattice argument rules out an exactly unbiased integer-valued result
even if nonadjacent output integers are allowed: its mean is still an integer
divided by $N$.

This is a theorem about a **hard** fair-bit cap. A non-fair primitive, an
uncharged random reservoir, an explicit failure or an unbounded stopping time
changes the hypotheses. It is not a lower bound on amortized randomness across
an arbitrarily large batch.

## Sharp abort bound with exact conditional output

Now allow a third outcome, abort, but demand that the accepted zero/one result
has exactly the desired law. Let $\alpha$ strings return one and $\beta$ return
zero. Exact conditional probability requires

$$
\frac{\alpha}{\alpha+\beta}=\frac{a}{b}.
$$

Coprimality forces $\alpha=at$ and $\beta=(b-a)t$ for an integer $t$. Therefore
at most $b\lfloor N/b\rfloor$ strings can be accepted, and

$$
\boxed{\delta_R=\frac{N-b\lfloor N/b\rfloor}{N}}
$$

is the smallest possible abort probability. It is attained by accepting that
many full $b$-sized groups, partitioning each in the ratio $a:(b-a)$ and aborting
the rest. If $N<b$, no positive acceptance probability is possible; the formula
then gives abort probability one. Repeating a correct accepted-law block until
success is exact, but its total worst-case draw count is unbounded.

For probability $1/13$:

| Fair-bit cap $R$ | Best unavoidable bias | Minimum abort for exact accepted law |
|---:|---:|---:|
| 4 | 3/208 | 3/16 |
| 8 | 1/832 | 9/256 |
| 12 | 1/53248 | 1/4096 |
| 16 | 3/851968 | 3/65536 |

Over all twelve nonzero residue probabilities $a/13$, the sharp worst-case
best bias at cap $R$ is $6/(13\cdot2^R)$. Multiplication by $2^R$ permutes the
nonzero residues modulo 13, so the largest distance to an integer is $6/13$.
These are sampling-law bounds, not propagated native-output errors.

## Exact two-draw expectation, and why naive retries change the law

Compare an infinite uniform binary fraction with the binary expansion of
$a/b$, stopping at the first unequal bit. Output one if the random bit is
smaller and zero if it is larger. The threshold digits are generated exactly
by integer residue doubling modulo $b$.

Because the threshold is non-dyadic, exactly one binary prefix is unresolved
at every depth $k$. Thus the probability of needing more than $k$ bits is
$2^{-k}$, and

$$
E[T]=\sum_{k\geq0}2^{-k}=2.
$$

The sampler terminates with probability one, but not on the single infinite
tape equal to the threshold expansion. Hence there is no finite worst-case
bound or all-tape completion guarantee. Any exact almost-surely terminating
standalone fair-bit sampler must leave at least one prefix unresolved at every
depth: otherwise the success probability would be dyadic. Its expected draw
count is consequently at least the same sum. The comparison sampler attains it.

After a cap of $R$ bits, the comparison sampler has exactly one unresolved
string. The accepted success count is $\lfloor aN/b\rfloor$, among $N-1$
completed strings. Restarting on the unresolved string therefore samples

$$
\frac{\lfloor aN/b\rfloor}{N-1},
$$

which equals $a/b$ **if and only if** $b$ divides $N-1$. Necessity follows
because $a(N-1)/b$ must be an integer; sufficiency follows by taking the floor
of that integer plus $a/b$.

For $a/b=1/13$ and $R=4$, there is one success, fourteen failures and one
unfinished string. Repeated cap-and-retry returns one with probability $1/15$.
An exact bounded conditional sampler must also reject two of those fourteen
completed failures, reaching the optimal three aborts out of sixteen.
This is the explicit failed construction, with its corrected resource choice.

## Evidence and reproduction

```
python3.12 -B scripts/research_package.py --package research/odd-denominator-rounding-budget
python3.12 -B scripts/check_research_commit.py --package research/odd-denominator-rounding-budget
```

The standalone verifier authenticates the source context, compares the sharp
bias formula with every attainable integer success count on bounded odd
probabilities, exhausts accepted/failure/abort count triples, independently
enumerates literal fair-bit tapes against exact comparison trees, checks the
capped-retry congruence and the denominator-13 table, and verifies the exact
truncated expectation identity. No random sampling or floating point is used.
Normal and optimized modes keep all checks active and write no package files.

The written counting and stopping-time proofs are uniform; finite checks are
corroboration, not a classification of every sampler implementation. No new
physical inverse, stochastic service integration, precision/guard budget,
reversible sampler, complete caller, selected replay or formal proof is supplied.
The optional full-history check is unavailable in this shallow repository;
all declared pins use its reachable base. The navigation repair from
[PR #6050](https://github.com/CrocSwap/integer-mult-bounds/pull/6050) is included.
Main was refreshed at 721c03822c421b7f7fcbb2598993b947c4d88419, priority 8,
on 2026-10-28 UTC. Frozen inputs and the selected result remain unchanged.

## Significance for researchers

The finite fair-bit ABI of a dyadic stochastic prefix cannot simply be reused
for an odd-denominator inverse. The complete design must choose and pay for
bias, an explicit failure contract, or unbounded stopping. Expected two draws
cannot be entered as a deterministic worst-case tariff, and truncation followed
by retry does not generally preserve the desired stochastic law.

## Open next questions

Can the sharp bounded bias fit a concrete inverse caller's full error budget?
First identify its reached residue classes and propagate their exact bias through
the actual suffix. This package supplies neither that reachability proof nor
an admissible precision saving.

Can a variable-time sampler be hosted with a retained random tape, reversible
cleanup and a complete runtime/stock contract? Start with the comparison loop
modulo thirteen and its stopping record. Mean two draws alone does not supply
bounded latency, tape movement or all-tape termination.

## Credit

Prepared by [zxv](https://github.com/zxv) with substantial OpenAI Codex assistance.
[JoyboyBrian](https://github.com/JoyboyBrian)'s #5069/#5037 lineage supplies the
retained denominator-13 inverse and deterministic grid context.
[Nick Petalas](https://github.com/petalas)'s #6026 supplies the dyadic stochastic
rounding comparison. Finite probability counting and binary comparison sampling
are classical. The scoped contribution is the exact source-relative
bias/abort/runtime decision and the failed capped-retry substitution here.
Predecessor sources and attribution remain unchanged. Apache-2.0; no independent
human or proof-assistant review is claimed.
