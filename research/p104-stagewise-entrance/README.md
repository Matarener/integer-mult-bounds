# Exact correlated entrance for the first P104 collector

Clear1nsight, with substantial OpenAI assistance from four concurrent agents.

This package answers the stagewise admission question left by
[PR #3426](https://github.com/CrocSwap/integer-mult-bounds/pull/3426).
It gives the **maximal correlated entrance within the 58 initial Newton
banks** for exact literal execution of the first collector's **257-event
producer dependency cone**, followed by six admitted collector inputs. It
also supplies an explicit reversible parameterisation and its direct
arithmetic and width bill.

The result is a local module theorem. Its index is $2^{20424}$, compared with
$2^{10240}$ for the predecessor's ideal final-cut conditions. The additional
factor $2^{10184}$ measures stagewise divisibility constraints. These are
algebraic indices, not saved storage bits or a supplier improvement.

The frozen main is `6f100d4bb5083f8c35d96fd95a539811c62f245c`. The scientific
WORD and NATIVE bytes are the existing PR #2586 inputs retained through
PR #2665. The selected frontier and the conditional unchanged-profile
**599/584** cost stop are preserved.

## Exact scope

Let $R=\mathbb Z[i]$, $\pi=1+i$, and

$$
E_r=\begin{pmatrix}1&0\\1&\pi\end{pmatrix}^{\otimes r},
\qquad B_r=E_rR^{2^r}.
$$

The actual rank is nine, with 512 Gaussian coordinates per bank. Initially,
the 52 Y banks and the six dirty banks D31, D30, D29, D28, D27 and Q7 all
belong to $B_9$. Those six dirty values are arbitrary admitted values.

The classified contract requires every fractional ADD in the selected cone
to have an integral increment, every native pair's literal signed-floor
output to equal its ideal output, and all six target arrays immediately
before zero-based event 2025 to belong to $B_9$. The proof establishes both
necessity and sufficiency within this initial domain.

The original prefix has 2,025 events, of which 1,768 are outside this cone.
This theorem does not admit their omitted arithmetic histories, the later
external recipients, or genuinely rounded trajectories whose errors later
cancel. The cone contains 200 native occurrences, 52 positive quarter-ADDs,
and five early dirty D-to-Q subtractions. The native rank sum is 354.

## The admission theorem

In each actual chronological Y group, replace its sources by independent
partial-sum coordinates

$$
p_t=y_1+\cdots+y_t,\qquad y_t=p_t-p_{t-1},\qquad p_0=0.
$$

This bank change is unimodular. The five groups have sizes 3, 7, 7, 11 and
24. Their 47 nonterminal intervals have only two types. The five final
partial sums supply the terminal conditions.

| Partial-sum interval | Count | Diagonal exponent in weighted Newton coordinates | Local index |
|---|---:|---|---:|
| No D transport | 32 | $\max(4-|S|,0)$ | $2^{187}$ |
| One actual rank-one D transport | 15 | $\max(4-|S\setminus\{0\}|,0)$ | $2^{280}$ |
| Terminal sum | 5 | $4$ on every coefficient | $2^{2048}$ |

For a read-frame map $A_H$ and a rank-one native's actual right wrapper
$M_R$, the nonterminal modules are respectively $A_H^{-1}L_0$ and
$(M_RA_H)^{-1}L_1$, with the displayed diagonal profiles defining $L_0$
and $L_1$. Every terminal sum belongs to $4B_9$.

The rank-one condition comes from testing both sides of its actual $C_0$
stage. Writing a bit-zero pair as $(f,f+\pi g)$ gives
$C(f,f+\pi g)=(f+g,f+ig)$. Both arrays are divisible by four exactly when
both $f$ and $g$ are divisible by four. Testing only the quarter output
would miss this extra condition.

Consequently the quotient of $B_9^{52}$ by the exact Y entrance
$\mathcal M$ is

$$
(R/(\pi))^{4368}\oplus(R/(\pi^2))^{1992}
\oplus(R/(\pi^3))^{528}\oplus(R/(\pi^4))^{2622}.
$$

There are also 17,114 unrestricted Gaussian coefficient coordinates. The
index exponent is $32(187)+15(280)+5(2048)=20424$. For the predecessor's
ideal entrance $\mathcal I$ and the strong independent product entrance,

$$
(4B_9)^{52}\subsetneq\mathcal M\subsetneq\mathcal I,
\qquad [\mathcal I:\mathcal M]=2^{10184},
\qquad [\mathcal M:(4B_9)^{52}]=2^{86072}.
$$

[PROOF.md](PROOF.md) includes the dirty-input argument, sufficiency of the
quarter increments, terminal admission, and the literal pair parity
criterion. Odd internal floor-halves are allowed when the complete pair
still equals its integral ideal output.

## Constructive encoder and inverse

The encoder takes **52 owned arbitrary Gaussian coefficient banks**. It
applies each local diagonal profile and Newton encoder, follows the actual
inverse frame history, applies the extra inverse right wrapper where
required, and finally takes groupwise backward differences. Terminal scaling
uses positive $4$, since $\pi^4=-4$ has a different parameter convention.

The inverse takes forward partial sums, follows the actual forward histories,
and performs exact Newton and diagonal divisions. It rejects unavailable
divisions. These maps are a bijection onto the entire classified entrance.
The six already admitted dirty D/Q banks are supplied separately.

This parameterisation changes the numerical meaning of arbitrary raw source
arrays. A useful caller still needs an input/output intertwiner and a proved
returned-source, frame, and ownership contract. Functional Python arrays are
reference implementations of the algebraic schedule, without a measured
physical in-place layout.

## Direct preparation costs

The actual 47 nonterminal inverse paths contain 158 native occurrences of
total rank 281. Including the 15 extra right wrappers gives 331 wrapper
occurrences, 10,452 permutation cycles, and 159,020 direct Gaussian payload
SWAPs. The independent counter reconstructs these histories from the frozen
inputs without importing the primary implementation.

| Arithmetic category | Encoder | Decoder |
|---|---:|---:|
| Real ADD/subtract subtotal before SWAP and phase lowering | 1,133,456 | 1,123,216 |
| Native real signed floor-halves | 287,744 | 287,744 |
| Additional exact real halves | 0 | 270,224 |
| Native pair applications | 71,936 | 71,936 |
| Gaussian payload SWAPs | 159,020 | 159,020 |

Wrapper phases, native quarter turns, and movement are separately itemised
in [COSTS.md](COSTS.md). Its optional component-arithmetic lowering permits
source-minus-target overwrites; it is not the repository's stricter ADD
tariff. The resulting schedules are constructive upper bounds, with no
minimality claim.

For raw coefficient component bound $H$, all encoder work is bounded by
$612480H<2^{20}H$. For an admitted Y component bound $J$, decoder work is
bounded by $98304J<2^{17}J$. Signed storage also needs a sign bit. These
bounds concern this codec; physical routing, control, copies, the six dirty
inputs, caller execution, and recursive tariffs still need their own bill.

## Reproduction and evidence

No third-party Python dependency is required. The registered Python 3.12
commands run with ordinary and optimised interpretation:

```sh
python3 -B scripts/research_package.py --package research/p104-stagewise-entrance --check-only
python3 -B scripts/research_package.py --package research/p104-stagewise-entrance
```

Both registered modes passed on CPython 3.12.14, producing the same complete
typed receipt. Its file SHA-256 is
`91b4f644189bacdd19952e360d55d3738a915e50cf98001baf7f47fda54bd561`;
its canonical scientific digest is
`f2ec5be0707ab21f9f7fae68ebb91e862c8ee8eff094fc2e62b37af39b9a0f49`.
Metadata and source pins also passed. Separate CLI processes in a disposable
Git-free copy rejected a missing WORD, a corrupted WORD, and a receipt with
Boolean `true` replacing integer `1`, each for the intended reason.

Inside a Git-free package export, run:

```sh
python3 -I -B research/p104-stagewise-entrance/verify.py
python3 -I -O -B research/p104-stagewise-entrance/verify.py
```

The verifier rebuilds [RECEIPT.json](RECEIPT.json) and compares its full typed
contents. It authenticates scientific and retained predecessor bytes before
mathematics and again before success. Its six implementation modules execute
from captured source bytes, and their hashes and the verifier hash are
recorded and rechecked. An explicit generation command uses exclusive
creation, so it cannot overwrite an existing receipt silently.

The evidence includes:

- Separate primary D-path and independent Y-path constructions agreeing on
  the dense initial and cut hashes, with 52 codec roundtrips. Both evaluate
  the actual cone and each checks all six full-array cut formulae.
- A deterministic dense fixture checking all 90,624 literal/ideal native
  pairs and all 52 exact quarter reads. It passes through a non-$B_9$
  intermediate D28 value at event 1087 and returns admitted cut arrays.
- Two ideal-admitted controls rejected by the module decoder and literal
  trace. Their first failures are an inexact quarter at event 1087 and an
  inexact native pair at event 1089.
- The credited PR #3426 paired-$64$ family passing the cone and giving a
  zero cut. Its cone counts are distinct from that predecessor's full-prefix
  experiment.
- Independent threshold checks for every one of the 512 basis directions
  in each nonterminal profile, plus an independently reconstructed cost
  invoice. The written proof supplies universal necessity and sufficiency;
  finite basis checks alone are not a proof for nonlinear rounded paths.
- Rejection of duplicate-key, floating, nonfinite, and Boolean-as-integer
  receipt data, unavailable exact profile divisions, and a corrupt frozen
  scientific source.

The reused PR #3382 model is a dependency of the primary implementation.
`independent.py` and `independent_cost.py` import neither it nor the primary
layers. Complete native covariance is inherited from PR #3416; binding the
recipes here does not recertify its full 1,245-record theorem. No independent
human review or formal proof-kernel acceptance is claimed.

## Coordination and credit

The canonical claim is
[Discussion #2750, comment 19009685](https://github.com/CrocSwap/integer-mult-bounds/discussions/2750#discussioncomment-19009685).
The submission checkpoint found unchanged main and completed all four
open-PR pages, 368 records, alongside targeted Discussion refreshes. This is
a scoped overlap review, not a complete novelty certificate.

The mathematical and source predecessors include ywz65's PR #2586 word,
Arham Tahir's PR #2665 retention, Clear1nsight's PR #3382 Newton domain and
PR #3423 producer interfaces, Nick Petalas's PR #3416 native covariance and
PR #3426 ideal correlated entrance, Tekalign's PR #3025 literal-floor and
PR #3218 phase-sensitive checks, Ross Richardson's PR #3068 domain question,
and Jose Manuel and Vasek W's inherited unchanged-profile cost stop.
[SOURCES.json](SOURCES.json) records exact source identities and retained
proofs, with the older collector lineage retained in the exported sources.

Nick Petalas's concurrent
[PR #3449](https://github.com/CrocSwap/integer-mult-bounds/pull/3449), at
`5cb2ff187a27de1cbd1a37933f7228b35b15702b`, independently gives the sharp
index-$280$ condition for the particular Y27/Y26 rank-one window. Its proof
was read at submission and agrees with the local profile above. This package
adds the general 58-bank module, all 52 independent partial-sum coordinates,
and the actual-path codec and bill. No priority over that concurrent local
formula is claimed.

Hiroki Kumazaki's PR #3446 recipient closure and Nick Petalas's PR #3448
all-depth product entrance are complementary results. Their complete
executables were not replayed here, and their scopes are not absorbed into
this producer claim.

## Open next questions

1. **Which actual caller consumes these coefficient coordinates and returns
   the prepared banks for undo?** Name its output, prove the input/output
   intertwiner and return equations, and price copies, control, routes,
   widths, cleanup, and displaced work. No such paid caller is supplied by
   this producer theorem.
2. **What further stagewise conditions does that caller need outside the
   cone?** Intersect this explicit module with its additional authenticated
   reads and recipient histories. Coordinate with PR #3446's closure and
   PR #3449's noncone-read handoff. The required whole execution and ownership
   boundary must be specified first.
3. **Can a named changed supplier profile afford the complete bill?** Declare
   the changed coverage or cost hypothesis and apply a fully charged
   optimistic moment screen before another supplier construction round.
   The unchanged 599/584 screen remains a stop; the larger admission module
   supplies no new selected frontier or all-size transfer.
