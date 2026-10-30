# Stochastic scalar prefixes can restore dirty inputs with a parity log

A grid-valued stochastic ADD is an exactly invertible shear when its inverse
uses the complemented coin. A rounded signed halving instead needs one parity
bit; keeping that bit suffices, and recomputing it during reversal clears it.
Together these give a compute–accumulate–uncompute interface for the exact
9,589-event scalar prefix studied by
[Nick Petalas](https://github.com/petalas)'s
[PR #6026](https://github.com/CrocSwap/integer-mult-bounds/pull/6026).

The source has 84 signed halvings. The protocol uses **84 clean residue bits
and 11,713 read-only random bits per real stream sample**, restores all 748
arbitrary dirty working values, returns the residue log to zero, and leaves
the random tape unchanged. Its forward arithmetic law is exactly the source's
fresh stochastic rounding law. Thus its source-relative forward error bound
is retained under the source's assumptions; that concentration result is cited,
not independently replayed or strengthened here.

This is a logical scalar-grid ABI, not a native rounded supplier, physically
reversible bit-level implementation, complete caller invoice or new κ. Physical
random-bit preparation/access, guard widths, integer arithmetic, temporary
cleanup and the later native MOVE remain payable and unimplemented.

## Exact stochastic rounding and an inverse shear

Normalize the grid spacing to one. For an integer numerator $n$, dyadic
denominator $d=2^q$, and a fixed coin integer $0\leq U<d$, divide
$n=dk+r$ with $0\leq r<d$, using Euclidean division even for negative $n$.
Define $S(n,d,U)$ to be $k$ plus one when $U<r$ and $k$ otherwise. Uniform
$U$ gives exactly unbiased stochastic rounding of $n/d$.

Two identities hold for every integer input and every coin:

$$
S(dy+n,d,U)=y+S(n,d,U),
$$

$$
\boxed{S(-n,d,d-1-U)=-S(n,d,U).}
$$

For the second identity, if $r=0$ both sides are exact integers. Otherwise
$-n=d(-k-1)+(d-r)$, and the condition $d-1-U<d-r$ is equivalent to $U\geq r$.
This is precisely the complement of $U<r$. The proof includes all signs and
ties. Complementing a $q$-bit coin gives $d-1-U$ without another random draw.

For distinct source and destination coordinates, implement a dyadic ADD by

$$
y\leftarrow y+S(sx,d,U).
$$

It is a translation in $y$ for fixed $x,U$. The inverse is the same stochastic
ADD with coefficient $-s/d$ and complemented coin. The first identity shows
that this is exactly the source's rule of rounding the whole updated grid value.
No lost fractional residue needs to be saved for a shear, because its source
coordinate remains available.

Reversing a complete word recovers that source at each corresponding inverse
step by induction. Coins may be fresh across **forward** events and reused only
at their matched inverse. The independent-forward concentration hypothesis is
therefore preserved. Reusing one coin across different forward events is not
justified by this construction.

## Signed halving and its necessary local bit

For a SCALE coefficient $\sigma/2$, with $\sigma$ equal to plus or minus one,
save $r=(\sigma x)\bmod2$ in a clean bit and set $y=S(\sigma x,2,U)$. Recover

$$
x=\sigma\bigl(2y-2[U<r]+r\bigr),
$$

where the bracket is one when its condition holds and zero otherwise. This
follows immediately from $\sigma x=2k+r$ and $y=k+[U<r]$. Recompute the recovered
parity and XOR it into the saved bit, clearing the log without discarding an
unknown value. The random coin is read, not overwritten.

One bit is necessary for this **isolated** rounded halving when the coin is
returned unchanged and no other value retains the input distinction: for fixed
$U=1$, inputs zero and one both round to zero. A side state with only one value
cannot distinguish them. The parity bit supplies the required two states.
This is not a proof that the complete source word needs all 84 bits; later
structure might permit reuse or infer some residues.

SCALE by minus one is exact and self-inverse. SCALE by two is exact on the
forward grid, and its inverse divides the reached even value by two. These
are logical operations on reached grid states, not an all-state physical gate
synthesis. A finite implementation must provide its magnitude/guard format.

## Complete source-bound compute–accumulate–uncompute protocol

The pinned historical #5599 prefix has 9,358 ADDs and 231 SCALEs on 748 public
roles, all at its empty common frame before the first MOVE. Of the SCALEs,
115 are minus one, 32 are two, 18 are one half and 66 are minus one half.
There are 7,421 potentially rounded events, with total denominator logarithm
11,713. These source counts are independently reconstructed by replay.

Supply arbitrary grid-valued working inputs $x$, disjoint arbitrary dirty
output accumulators $y$, an independent uniform random tape, and 84 clean
residue bits. Give each potentially rounded forward event its own fixed coin
block, even when its particular value happens to be on the grid.

1. Execute the source prefix with its exact fresh stochastic rounding law,
   saving each signed-half parity in its assigned clean bit.
2. Add the resulting 748 grid components to the output accumulators.
3. Reverse every event. Use complemented matched coins for ADDs; use saved
   parities for signed-half recovery and clear each bit by recomputation.

Let $\widetilde F_U$ be the forward rounded map at the fixed tape $U$. The
complete endpoint is

$$
(x,y,U,0)\longmapsto(x,y+\widetilde F_U(x),U,0).
$$

The output accumulators are never read by the reverse pass, so they can begin
arbitrarily dirty. Every working input and the entire tape are restored for
every coin string, not merely in expectation or with high probability. The
forward output's probability law is unchanged under uniform independent coins;
its source-relative error guarantee applies at the copied output. There is no
claim that the rounded map equals the exact Gaussian or native operator.

The returned tape is unchanged bit for bit, but the retained rounded output can
be correlated with it. It is not automatically a fresh independent random
resource for a later adaptive call. Such a call needs new independent coin
blocks or a new conditional-error proof; restoration alone does not replenish
randomness. The verifier includes a two-shear reused-tape bias counterexample.

The logical ledger is 9,589 forward macro-updates, 748 integer output ADDs and
9,589 reverse macro-updates, totaling 19,926 macros. The tape contains 11,713
bits and is read twice; the 84 owned parity bits are returned clean. A reverse
halving macro includes parity-dependent integer correction and log clearing.
**These are macro/resource counts, not a bit-operation or tape-movement tariff.**
The physical sampler, temporary arithmetic storage and complete native caller
bill are unknown, not zero.

## Evidence and reproduction

```
python3.12 -B scripts/research_package.py --package research/reversible-stochastic-shears
python3.12 -B scripts/check_research_commit.py --package research/reversible-stochastic-shears
```

The verifier authenticates the unchanged prefix source and proof, reconstructs
all source opcodes/counts, checks exact unbiased marginals, grid translation and
the antithetic identity for signed numerators and denominators through 16,
enumerates signed-half inverses and a two-role protocol with changing sources,
and executes the entire source-bound protocol on four dirty-input families and
four deterministic coin tapes. Those tapes check pathwise restoration, not a
Monte Carlo tail estimate. Missing residue, uncomplemented inverse coins and
invalid coefficient/tape domains have rejecting controls. Normal and optimized
modes write no package files; arbitrary-size and all-coin uniformity follows
from the written inverse identities and chronological induction.

The replay uses exact Python integers. Its finite fixtures cap values at 256
bits; this is a verifier bound, not a proved physical format for arbitrary input.
No proof assistant, selected replay, native MOVE, overflow analysis or independent
human review is claimed. The current selected #6030 word is a different source;
this result deliberately retains the exact #6026/#5599 historical prefix.

Main was refreshed on 2026-10-28 UTC at
721c03822c421b7f7fcbb2598993b947c4d88419, priority 8. The navigation repair from
[PR #6050](https://github.com/CrocSwap/integer-mult-bounds/pull/6050) is included.
The optional full-history preflight is unavailable in this shallow checkout;
all declared pins use the reachable base. Frozen sources and selection stay unchanged.

## Significance for researchers

Unbiased forward rounding and exact dirty restoration are compatible at this
scalar boundary when inverse coins are coupled correctly and irreversible
halvings retain their residue information. The result supplies an explicit
logical lifecycle for the random tape and residue log, rather than relying on
fresh rounding in the inverse. It closes this scalar interface step while
leaving the physical reversible sampler, native execution and full cost open.

## Open next questions

Can the logical macros be lowered to a source-compatible reversible integer
arithmetic and tape program with bounded scratch and a competitive full bill?
Start with one signed-half macro and an explicit input/guard format. This
package supplies no such bit-level lowering or random-tape preparation.

Can some of the 84 parity bits be reused or inferred at the actual word's
chronological cuts? Start with one half/double segment and prove exact recovery
for all dirty grid inputs and coins. The one-bit local necessity result does
not establish global log optimality.

Can the next actual native MOVE preserve a useful complete output error bound?
First supply its all-column numerical contract and the output consumer. The
common-frame scalar protocol alone does not answer that question.

## Credit

Prepared by [zxv](https://github.com/zxv) with substantial OpenAI Codex assistance.
[Nick Petalas](https://github.com/petalas)'s #6026 supplies the stochastic law,
exact historical-prefix influence proof and round/restore question.
[Ali Romman](https://github.com/aliromman)'s #5599 supplies the unchanged word,
with the retained helper, controller, geometry, BIT and precision lineage in
its sources. Antithetic sampling, residue retention and compute/uncompute are
classical techniques. The scoped contribution is the exact coupled inverse ABI,
source-bound 84-bit parity ledger and dirty-output accumulation endpoint here.
Apache-2.0; predecessor files and attribution remain intact.
