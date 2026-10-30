# Idle rank cap sensitivity of the selected complex word's packing endpoint

**Scoped exact arithmetic and independent reproduction. No new κ, no supplier and no
selected-frontier change.**

The reviewed [packing ceiling](../complex-local-word-ceiling/README.md) caps every idle
repacking of the selected complex local word at a < 0.001690054109089, κ < 0.001687202646,
which is +0.869% over the selected κ = 0.001672660197076918. That cap uses the largest idle
rank the outer halving guard admits, R = 51 (`2·51² < 73² ≤ 2·52²`), while the selected word
itself only ever uses idle ranks up to 48. The legality of rank-49 to rank-51 idle children is
exactly the physical owner/hosting question the
[integer-optimum package](../idle-packing-stability/README.md) names as consequential.

This package prices that question. It certifies the endpoint of the optimal integer idle
packing for every legal idle rank cap, using an independently written rational enclosure chain
(`enclosures.py`: atanh logarithms, positive Taylor exponential, directed rounding to 2^-200),
so the headline numbers of both predecessor packages are reproduced without their arithmetic.

## What is established, and at what strength

For the selected word (per-call uniform local profile `{1:2412, 2:418, 3:432, 4:142, 5:82, 8:8}`,
144 calls, 14,336 live data families, PR1012 coverage `rank mass = 72W + 64N`, idle mass
237,024) the endpoint is the root of

    (1/W) sum_r n_r (r/m)^(1-a) = 1,   m = 73.

Certified lower bounds on the relative gain over the selected endpoint a_c are:

| Legal idle rank cap | Optimal aggregate integer packing | certified gain over a_c | κ gain |
|---|---|---:|---:|
| 51 (guard) | 4647×51 + 27 | **+0.870319%** | +0.868851% |
| 50 | 4740×50 + 24 | +0.714648% | +0.713444% |
| 49 | 4837×49 + 11 | +0.556373% | +0.555438% |
| 48 (attested) | 4938×48 | +0.395842% | +0.395178% |
| 47 | 5043×47 + 3 | +0.231630% | +0.231242% |
| 46 | 5152×46 + 32 | +0.064600% | +0.064492% |
| ≤ 45 | — | none | none |

The table is monotone in the cap and the bracketing gap is 2^-50 per entry. **Ranks 49 to 51
carry 54.5% of the quoted headroom.** At the largest rank the selected word itself attests,
the certified headroom is +0.396%, not +0.87%. Below cap 46 the optimal integer packing is
worse than the selected word's own idle histogram, which is admissible from cap 48 upward.

Two further distinctions, both certified at cap 51:

- **Pooling.** If every call must reach its own optimum (`1646 = 32×51 + 14` per call), the
  gain falls to +0.784307% with endpoint bracket `[0.00168860344652622, 0.00168860344653532]`.
  The certified gain is smaller, but the aggregate optimum depends on distributing 4647 rank-51
  children over 144 calls unevenly. The selected idle histogram is itself not per-call uniform
  (`4866/144` is not an integer), so the aggregate model is the one its own invoice uses.
- **Residue form.** Carrying the 27-unit residue in rank-1 children instead of one rank-27 child
  costs 0.003 percentage points: +0.867352%.

Everything here is a pricing statement under the stated model: it allows fractional counts and
every repacking, and checks no physical hostability, owner-family, restoration or consumer cost.
A gain is available only if a legal packing realizes the histogram.

## Independent reproductions and refinements

| Published claim | This package |
|---|---|
| Ceiling `a < 0.001690054109089` (grid 1e-15) | independently certified bracket `[0.0016900541090878463, 0.0016900541090887344]`, 11% narrower, overlapping; κ(lo) = 0.00168720264533 ≤ published κ cap |
| Per-call integer ceiling `0.001688603446527` | reproduced and contained: the independent bracket is `[0.0016886034465262156, 0.0016886034465271038]` |
| Unrestricted integer optimum `{51:4647, 27:1}` | reproduced, with certified endpoint gap 9.56e-9 in `a` below the fractional relaxation (2.78e-8 in normalized moment, as reported by the integer-optimum package) |
| Selected endpoint `a_c` with moment one | certified bracket `[0.0016754626768076, 0.0016754626768085]`; the exact moment at the published a_c is `1 − (1.30 ± 0.06)e-24`, so the published value is a truncation of the root |
| Selected κ = a/(1+a) at a_c | the published 18-digit value is the truncated decimal of `a_c/(1+a_c) = 0.00167266019707691866` |

## Related open work

Open PR #3729 (`research/complex-idle-integrality-ceiling`) prices the same selected word
under a stricter premise: idle counts are integers *within one call*, so each call packs
`1646 = 32·51 + 14`.

- **Agreement, per call.** Its published per-call ceiling `a < 0.001688603446527` lies inside
  this package's independently certified per-call bracket
  `[0.0016886034465262156, 0.0016886034465271038]`; its quoted κ gain `+0.782985%` equals this
  package's certified per-call κ gain `+0.782985%`; and both find the same per-call optimum
  `32×51 + 14` per call (`{51:4608, 14:144}` in aggregate).
- **What differs.** This package prices the per-call premise as one row of a cap table, not as
  the corrected ceiling: the aggregate rows pool the idle mass across calls
  (`4647×51 + 27` at cap 51), which the per-call premise forbids. The aggregate rows are the
  ones comparable with the selected word's own idle histogram, whose rank-48 count `4866` is
  not divisible by 144. Which premise the physical invoice realizes is a separate open
  question, raised for the record by the peer audit in PR #3747 and not adjudicated here.

## Controls

Nine controls must hold (`verify.py`, all certified, no sampling):

1. the halving guard admits 51 and rejects 52;
2. the selected histogram exceeds one at the published ceiling;
3. the published ceiling bracket and the independent bracket overlap, and the published κ cap
   is not below `κ(a_lo)`;
4. the published endpoint lies in the certified grid bracket and its exact moment is below one
   by less than 1e-23;
5. the aggregate integer optimum is monotone in the cap over all 21 caps;
6. the same mass at rank 1 prices strictly worse than at the cap;
7. the aggregate optimum strictly beats the per-call optimum at cap 51;
8. refused inputs: a rank-52 child, an idle mass off by one, and a negative count.

## Reproduce

```sh
python3.12 -B research/idle-rank-cap-sensitivity/verify.py          # ~11 s, PASS_IDLE_RANK_CAP_SENSITIVITY
python3.12 -B research/idle-rank-cap-sensitivity/verify.py --write  # regenerates RESULT.json
```

Standard library only. The registered hook runs the first command with a 300 s timeout.

## Scope and limits

- One fixed per-call local profile, 144 calls, 14,336 live families, the PR1012 coverage law and
  the outer halving guard. It is not a bound for other local words, port counts, templates,
  coverage laws or outer recipes.
- Endpoints are roots of the exact moment; the gains are certified lower bounds at grid 2^-50.
  Fractional and integer packings are pricing models, not constructed programs.
- No physical hosting, owner-family, restoration, consumer, supplier or κ claim. The selected
  result and the selected frontier are unchanged.

## Open next questions

- **Which idle ranks are legally hostable, above all ranks 49 to 51?** The certified gain is
  +0.870% at cap 51 but +0.396% at the attested cap 48. First step: extract one selected
  owner-family residual instance and test whether a rank-49 to rank-51 idle child satisfies the
  stated owner, port and halving contracts. Blocked by: no source-bound characterization of legal
  idle groups and hosting resources is available in this checkout.
- **Does the pooled aggregate optimum survive the per-call distribution of the selected invoice?**
  Requiring a per-call optimum loses about 0.086 percentage points at cap 51. First step: bind one
  call's actual idle remainder to its recorded owner slots and check whether the record already
  pools across calls. Blocked by: the selected owner ledger available here is an aggregate
  histogram, not a per-call assignment.

## Credit

The selected complex supplier, its endpoint, its coverage identity, the fractional packing
ceiling, the integer-optimum and stability results are the work of their credited predecessors:
certificates and sources are pinned in `SOURCES.json`, and the ceiling and integer-optimum
packages keep their own attribution. This package adds the cap-sensitivity table, the
independently written enclosure chain and the controls. Produced by Nick Petalas with AI
assistance. Apache-2.0.
