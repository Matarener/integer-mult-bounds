# The pooled per-replica idle model: #1685's ceiling, and a lever the per-call model forbids

**Scoped obstruction and a model-discrimination result. No new κ, no supplier, no selected-frontier
change.** Prepared by Nick Petalas with AI assistance. Apache-2.0.

## The ambiguity this addresses

Two packages price the *same* selected complex local word and get *different* answers, and
neither says which one is contractually binding:

| Source | What one "unit" of accounting covers | Live families | Calls |
|---|---|---:|---:|
| [complex-local-word-ceiling](../complex-local-word-ceiling/README.md) | **one call** | `w = 896/9` | 1 |
| [idle-packing-stability](../idle-packing-stability/README.md) (#1685) | **one replica** | `W = 14336` | 144 |

Both apply PR1012's coverage identity, `mass = 72·W + 64·N`, and both cap idle ranks at
`R = 51` from the outer halving guard. They differ only in what they pool. The question this
package answers is what that difference *does*, which neither source states.

## Result 1: #1685's proved optimum implies a ceiling

#1685 proves the exact unrestricted integer idle optimum `{51:4647, 27:1}` for pooled idle
mass 237024, then explicitly declines to convert it: *"The predecessor's fixed-word cap
remains `a < 0.001690054109089` ... No packing gain or improved endpoint is claimed here."*
Converting it:

| Quantity | Fractional relaxation | Pooled integer optimum |
|---|---:|---:|
| Idle children | `237024/51 = 4647.53…` fractional | **`{51:4647, 27:1}`** |
| `a` ceiling | `0.001690054109089` | **`0.001690044548223`** |
| κ cap `κ < a/(1+a)` | `0.001687202645` | **`0.001687193117`** |
| Headroom over selected κ | +0.8694 % | **+0.8689 %** |

The pooled optimum reproduces #1685's published partition exactly, which independently
confirms the shared closed form. The *conversion* is the new content.

The tightening is small (0.0006 %) because pooling lets 144 calls share one remainder child,
which recovers almost all of the fractional ideal. That is the honest finding: **the pooled
model is nearly as loose as the fractional relaxation**, so integrality is not where the
real obstruction lives.

## Result 2: the two-unpaid premise is forbidden only by per-call accounting

`levers.py` advertises a "two unpaid coordinates per live family" lever at 3.77×, κ cap ≈
0.00634. PR #3729, working per call, reports it as unusable: with `unpaid = 2` the per-call
residual is `71·(896/9) + 64 − 5586 = 13918/9`, **not an integer**, so "a single call's child
multiset cannot have non-integral rank mass, so under this per-call model that premise admits
no integer packing at all."

That obstruction is an artefact of pricing one call. The denominator is 9, and the replica has
exactly nine stage invocations:

| Pooling level | Calls | `unpaid = 2` idle mass | Integer packing? |
|---|---:|---|---|
| one call (incumbent / #3729) | 1 | `13918/9` | **no** |
| one replica (9 stage invocations) | 9 | `13918` | **yes** |
| sixteen replicas (#1685's model) | 144 | `222688` | **yes** |

Both pooled levels price cleanly:

| Pooling level | Idle mass | Exact integer optimum | `a` ceiling | κ cap | Headroom over selected κ |
|---|---:|---|---:|---:|---:|
| one replica | 13918 | `{51:272, 46:1}` | `0.006377826759129` | `0.00633741` | **+278.88 %** |
| sixteen replicas | 222688 | `{51:4366, 22:1}` | `0.006377945692541` | `0.00633753` | **+278.89 %** |

The sixteen-replica κ cap `0.006337525300350` sits just under the incumbent's advertised
`a/(1+a)` figure for this lever, and the per-call model alone would have said the lever is
impossible. **A premise already published in the lever table is admissible or inadmissible
depending only on the accounting unit.**

Two cautions, both load-bearing:

- This is **not** a supplier and **not** a κ improvement. `unpaid = 2` is a what-if that the
  incumbent README itself labels as such: it changes the coverage law, which is a hypothesis
  of the whole ceiling model. It is priced here only to show the premise is not integrality-
  forbidden, which is a question about the *accounting unit* rather than about the premise's
  truth.
- The per-call and pooled ceilings for the **baseline** word differ by 0.085 % in `a`
  (`0.001688603446527` per call, from PR #3729; `0.001690044548223` pooled, here). A candidate
  supplier is billed against a different number depending on an unstated contract choice.

## Relation to concurrent integrality work

Live overlap at the submission checkpoint (450 open PR bodies, complete pagination, read
2026-10-18 ~19:30 UTC; bounded non-atomic coverage, not a novelty proof):

| Work | What it establishes | Relation here |
|---|---|---|
| PR #3729 | per-call integer idle ceiling `0.001688603446527`, DP-based | **Cited, not duplicated.** This package's `unpaid = 1` per-call figure is theirs. |
| PR #3737 / #3749 (jwr404) | the aggregate `{51:4647, 27:1}` at idle mass 237024 has moment below one where 144 per-call copies do not, with bracket `1690044548222/10^15`–`1690044548223/10^15` | **Overlap on Result 1.** Their aggregate bracket and this package's pooled ceiling are the same quantity, reached independently. Their credit stands; the conversion here was written before their PR was visible. |
| PR #3747 (Arham-Tahir64) | identifies the missing equal-mass-per-call restriction and gives the same aggregate-vs-per-call counterexample in the unrestricted aggregate cost model | Same overlap; theirs additionally names the modelling restriction. |

**What is not covered by any of them:** all three treat the baseline `unpaid = 1` word. PR #3729
states that at `unpaid = 2` "under this per-call model that premise admits no integer packing
at all". That is true per call and false pooled, as this package shows. The `13918` and `222688`
idle masses appear nowhere in the PR or discussion search.

## What each model is good for

Pooling only relaxes: it allows children to be shared across calls, so its ceiling is always
at least the per-call ceiling. Therefore:

- **Per-call** is the conservative screen. Use it to *reject* a packing claim.
- **Pooled** is the permissive screen. Use it to decide whether a premise is worth building at all.

A premise that is integrality-forbidden per call but admissible pooled (this one) has been
mis-screened. That is the actionable finding, and it is independent of whether the two-unpaid
premise is ever built.

## Controls

| Control | Count | What it rules out |
|---|---:|---|
| Exhaustive integer idle optima, mass ≤ 40 and cap ≤ 9, by DP over all partitions | 328 | a wrong closed form; no partition is skipped |
| Pooled moment never below the per-call fractional relaxation, random admissible templates, widths 9…73 | 240 | the pooling monotonicity claim, and an inverted interval |
| Semantic rejections | 5 | guard violation, over-mass local word, `unpaid = m`, zero cap, zero call count |
| Published realised packings excluded at the pooled ceiling | 2 | #1685's `{1:2276,3:377,7:7,48:4866}` and the incumbent's `{1:2249,2:1,3:400,7:3,16:47,48:4850}`, each priced complete with the local word, certified moments 1.0000043 and 1.0000044 |

Both sides of every ceiling bracket are certified and non-vacuous: the minimum pooled integer
moment is `> 1` at `a_hi` and `< 1` at `a_lo`.

**Deliberate-failure check.** Replacing the closed-form optimum with a suboptimal remainder
split makes the run fail loudly rather than return a bracket.

## Scope and limits

- **The accounting unit is a contract question, not an arithmetic one.** This package does not
  decide it. It shows the two answers and that the difference is material.
- Holds for one **fixed** paid local profile, `m = 73`, 112 ports, the nine-stage four-pair
  template, the coverage law and the halving guard `2R² < m²`. Not a bound for other local
  words, port counts, templates, coverage laws, centre charges or outer recipes.
- Idle ranks are integers `≤ R`. **Owner, hosting and width legality are not imposed**, exactly
  as in #1685; adding them can only lower the ceiling, so the bound stays valid.
- No packing is realised. `{51:4647, 27:1}` needs 4648 idle children per replica against the
  published 492 hosted helpers. Whether that is hostable is open.
- `κ < a/(1+a)` is the retained balanced reduction's **planning** ceiling. Nothing here changes
  the selected result or its obligations.
- Arithmetic is exact rational interval arithmetic imported from the credited module; no
  floating point enters a bracket. Decimals are display only.

## Reproduce

```sh
python3 -I -B research/pooled-idle-model-rescue/verify.py   # ~3 min, PASS_POOLED_IDLE_MODEL_RESCUE
python3 -B scripts/research_package.py --package research/pooled-idle-model-rescue
```

`verify.py --write` regenerates `RESULT.json`. `pooled.py` holds the model and imports
`research/complex-local-word-ceiling/ceiling.py` rather than reimplementing its arithmetic.

## Open next questions

- **Which accounting unit is contractual?** This is the decisive question and it is a
  documentation/contract decision, not a mathematical one. It changes the baseline ceiling by
  0.085 % and decides whether the two-unpaid premise is admissible at all. *First step:* read
  the PR1012 coverage identity's statement on whether the centre charge and the unpaid
  coordinate attach per call or per replica. *Blocker:* the sources do not settle it.
- **What ceiling survives owner and hosting legality?** #1685's own open question and the only
  route to a materially tighter bound. The unrestricted pooled optimum needs 4648 idle children
  against 492 hosted helpers, which is why a legal-partition optimum could be far tighter.
  *First step:* take one owner-family residual instance and enumerate only legal partitions
  while holding the local invoice fixed. *Blocker:* no source-bound characterisation of legal
  idle groups exists.
- **Does the same unit ambiguity hit the bit side?** Not attempted; its profile and coverage law
  differ and this model does not transfer automatically.

## Credit

The coverage identity is PR1012's. The ceiling engine and the exact rational interval
arithmetic are Douglas Colkitt's [complex-local-word-ceiling](../complex-local-word-ceiling/README.md),
imported here rather than re-derived. The exact integer idle optimum and its concavity proof
are [PR #1685](../idle-packing-stability/README.md) by Penguin for Maximus Putnam; this package
reuses their closed form, re-checks it independently by dynamic programming, and supplies the
ceiling conversion they declined to state. The per-call integrality ceiling is
[PR #3729](https://github.com/CrocSwap/integer-mult-bounds/pull/3729); this package does not
duplicate it and cites it as the per-call counterpart. Predecessor credit for every underlying
construction stays with its original authors.

Produced by Nick Petalas with AI assistance. Apache-2.0.