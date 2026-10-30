# Unsigned connectors attain the call floor on at least 3c−1 sources

For every ring characteristic $c\geq8$, an explicit six-source depth-two block gives

$$
N(c)\geq2c+2\lfloor c/2\rfloor.
$$

This is $3c$ sources when $c$ is even, and $3c-1$ when $c$ is odd. It improves
[Nick Petalas](https://github.com/petalas)'s
[PR #6035](https://github.com/CrocSwap/integer-mult-bounds/pull/6035) bound
$N(c)\geq\lfloor5c/2\rfloor$ in this range and answers its first open question:
a depth-two block can serve six sources. Its smaller-characteristic results
are unchanged. This is a finite exact certificate plus a uniform lifting proof,
not a new supplier, physical consumer, multiplication theorem or $\kappa$.

## Interface and full call floor

Retain the unsigned complete-call interface of
[PR #4231](https://github.com/CrocSwap/integer-mult-bounds/pull/4231) and
[PR #4248](https://github.com/CrocSwap/integer-mult-bounds/pull/4248).
There are $k$ immutable source rows, one arbitrary dirty borrowed connector
$z$, and a distinct arbitrary dirty output $y_m$ for every nonzero binary mask.
The maps $A_m$ and $B_j$ are arbitrary and need not commute or be invertible.
The only operations are

$$
B_j:\ z\leftarrow z+B_jx_j,
\qquad
A_m:\ y_m\leftarrow y_m+A_mz.
$$

Every source and output operator is called exactly $c$ times in a floor word.
The complete count is

$$
c\bigl(k+2^k-1\bigr).
$$

Indeed each source-call count must be a positive multiple of $c$ for universal
connector restoration; each output-call count must be a positive multiple of
$c$ to cancel arbitrary connector dirt. No operator can be absent, because its
required source column or output is nonzero for some allowed map. These are
complete calls, with no free scaling, copies, signs, extra connectors, source
mutation or output feedback.

Let $q_t$ be the vector of source-event counts modulo $c$ after $t$ source
steps. Reading output $m$ at $c$ boundaries implements its required sum exactly
when the corresponding prefix vectors sum to $m$ modulo $c$. The coefficient
of its initial connector dirt is $c$, hence zero. Each initial output is retained.
Integer coefficients act centrally through the characteristic; this argument
does not commute $A_m$ past $B_j$.

## Six-source certificate

The 54-event base word uses each label exactly nine times:

```text
4 2 5 1 3 0 1 5 3 0 2 4 3 2 5 4 1 0
2 3 5 0 4 1 1 2 3 5 1 4 0 4 2 0 5 1
3 0 3 4 2 5 0 4 2 5 3 1 0 4 5 3 1 2
```

Its cut vector is $(4,4,4,4,5,4)$. Write $n_t(j)$ for the number of label-$j$
events before boundary $t$. Define the integer lifted prefix by
$L_t(j)=n_t(j)$ before that coordinate passes its cut, and
$L_t(j)=n_t(j)-9$ afterward.

**Finite proof core.** Every one of the 63 nonzero binary six-vectors is an
integer sum of two lifted prefixes. [CERTIFICATE.json](CERTIFICATE.json) gives
one exact boundary pair per mask; replay independently regenerates the complete
pair table and compares it. There is no numerical approximation or search
completeness assumption in this finite identity.

## Uniform lift to every characteristic c ≥ 8

Replace the first event past the cut of coordinate $j$ by a run of $c-8$ copies
of label $j$. At $c=8$ the event is deleted. Every source now occurs

$$
9-1+(c-8)=c
$$

times. Let $\tau(t)$ be the boundary after the expanded image of the first $t$
base events. Before coordinate $j$ passes its cut, its new count is still
$n_t(j)$. Afterward its new count is

$$
n_t(j)-1+(c-8)=n_t(j)+c-9.
$$

Therefore $q_{\tau(t)}$ is $L_t$ reduced modulo $c$, coordinate by coordinate.
Every certified integer pair still sums to its mask modulo $c$. Pad its two
readouts with $c-2$ copies of the zero boundary. All outputs use exactly $c$
reads, and the connector returns to its arbitrary initial value because all
six sources are added $c$ times. This proves the six-source block for every
$c\geq8$, independently of the bounded characteristic checks. ∎

The construction needs the nonnegative run length $c-8$. It proves no
exclusion for characteristics five, six or seven.

## Concatenation and the density-three bound

Concatenate $\lfloor c/2\rfloor$ such blocks on disjoint six-source sets. Each
block returns to zero modulo $c$, so a prefix inside one block has zero source
coefficients in every other block. Split an arbitrary global mask by blocks
and use its two local certified prefixes in each nonzero block.

For odd $c$, append the two-source depth-one block from #4248,

```text
a b a^(c-1) b^(c-1).
```

It has the required three nonzero binary prefixes. The total readout depth is
at most $c$. Pad unused readouts at the global zero boundary and sort their
boundary indices; repeated reads at a boundary are allowed. This constructs
all masks on

$$
6\lfloor c/2\rfloor+2\bigl(c-2\lfloor c/2\rfloor\bigr)
=2c+2\lfloor c/2\rfloor
$$

sources at the full call floor. Deleting source events and restricting to masks
that omit those sources gives every smaller source count, exactly as in #4248.
This rederives the needed concatenation and deletion implications rather than
assuming a favorable count itself is a word. ∎

| Characteristic $c$ | #6035 lower bound | This construction |
|---:|---:|---:|
| 8 | 20 | **24** |
| 9 | 22 | **26** |
| 10 | 25 | **30** |
| 11 | 27 | **32** |
| 12 | 30 | **36** |

These are attaining lower bounds, not exact values of $N(c)$ or an improvement
to the existing upper bounds.

## Evidence and reproduction

```
python3.12 -B scripts/research_package.py --package research/connector-six-source-lift
python3.12 -B scripts/check_research_commit.py --package research/connector-six-source-lift
```

The standard-library replay authenticates the predecessor sources, regenerates
all 63 integer identities, and recovers the credited five-source positive control.
It checks every expanded boundary and mask for $8\leq c\leq40$, executes complete
arbitrary-dirty symbolic connector words on six sources at $c=8,9,10,11$ and
on twelve sources at $c=8$, and separately replays noncommuting two-by-two
matrix maps over those prime and composite characteristic rings. Every source,
readout, restoration coefficient and complete call count is checked.

The maximal concatenated construction has exponentially many outputs, so replay
does not materialize it. It verifies its exact block decomposition and selected
complete masks for $8\leq c\leq20$; the written concatenation proof covers every
mask. Missing calls, changed labels, corrupted readouts and exceeded depth/run
budgets are rejected. Normal and optimized replays write no package files.

Discovery used a small C++ annealer; the verifier neither imports it nor trusts
its objective. Base-nine and base-ten words were found. Bounded base-six and
base-eight searches failed; they are search failures, not impossibility results.
Only the stronger base-nine witness is retained. The finite certificate and
uniform proof are reproducible without discovery logs or a compiler.

Main was refreshed at 721c03822c421b7f7fcbb2598993b947c4d88419, priority revision
8, on 2026-10-28 UTC. The navigation repair from
[PR #6050](https://github.com/CrocSwap/integer-mult-bounds/pull/6050) is included.
No selected replay was run. The optional full-history preflight is unavailable
in this shallow checkout; all source pins are at its reachable base. No
full-history or independent human/formal-kernel pass is claimed.

## Significance for researchers

Six sources per two reads improve the uniform characteristic-dependent
connector construction beyond the five-source block. This answers a concrete
architectural open question while preserving the dirty interface and every
complete abstract call. It does not price native calls, input admission,
coefficient preparation, dispatch, hosting, movement or the physical consumer.
Those costs remain necessary before inferring any supplier or exponent gain.

## Open next questions

Can a six-source depth-two block work in characteristic five, six or seven?
Start with one bounded exact search or a proved obstruction; this lift does not
cover those cases, and the failed discovery runs exclude nothing.

Can seven sources fit depth two, or can an odd-depth block remove the one-source
loss for odd characteristics? First find an exact integer-lift template, then
check a complete dirty word. No such template is supplied here.

Does one actual physical consumer benefit from this characteristic-dependent
batch after every complete operation is paid? Pin a source/consumer contract
and derive its full invoice before implementing larger batches.

## Credit

Prepared by [zxv](https://github.com/zxv) with substantial OpenAI Codex assistance.
[Nick Petalas](https://github.com/petalas)'s #6035 supplies the five-source
integer-lift method and six-source open question; #4248 supplies the depth-block,
concatenation and deletion framework. The #4231 interface and floor and the
[PR #943](https://github.com/CrocSwap/integer-mult-bounds/pull/943) connector
lineage retain their predecessor credit. No predecessor method is claimed as
new: the contribution is the six-source exact template and its stronger uniform
attaining bound. Apache-2.0.
