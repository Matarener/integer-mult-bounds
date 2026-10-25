# Four-plane COPY floor: exact certificates for 98.5% of plane quadruples

**Claim type:** exact lower-bound certificates, checked by a standard-library verifier, plus a
documented open remainder. **No new κ.** This extends CubeJerry's
[#4365](https://github.com/CrocSwap/integer-mult-bounds/pull/4365), which closed two-plane
mixing, and my [#4421](https://github.com/CrocSwap/integer-mult-bounds/pull/4421), which closed
three-plane mixing on all 27,720 triples, to four planes. The contract is #4365's unchanged:

- whole-plane closures;
- `F₂`-rank tariffs `t(S, T)`;
- additive charges;
- payload in any field.

## Result

For **361,706 of the 367,290 plane quadruples (98.48%)**, every decomposition of `I₈` costs at
least **16 = Σ p_i²**, over every field. This is exactly the cost of separate coordinate messages,
so on those quadruples four-plane mixing cannot lower the COPY mass. **5,584 quadruples, in 3,650
tariff classes, remain open.**

## Certificates

The functionals are those of #4421, extended to four planes:

    L(M) = Σ_{(Z, X)} w · rank(Φ_Z(M)_XX).

- `X` ranges over the 15 plane unions.
- `Φ_Z` zeroes a set `Z` of the 12 off-diagonal plane blocks. `Z = ∅` gives #4365's block-rank
  functional.
- **Subadditivity.** `rank` of a linear image is subadditive.
- **Atom bound.** `Φ_Z(u vᵀ)_XX` is a sum over touched row planes of `u_P(Σ_allowed v_Q)ᵀ`. So its
  rank is at most the number of distinct allowed column (or row) plane sets, a combinatorial bound
  valid over every field.
- **The test.** If `Σ w·bound(S, T, X, Z) ≤ t(S, T)` for all 225 closure pairs, every decomposition
  costs at least `L(I₈) = Σ w·2|X|`. This holds because `Φ_Z` never touches the diagonal blocks.

Coverage:

| Certificate | Classes | Quadruples |
| --- | --- | --- |
| block-rank (`Z = ∅`) | 195,523 | the bulk |
| zeroed-block and mixed (several `Z`) | 24,732 | |
| **total certified** | **220,255 of 223,905** | **361,706 of 367,290** |

All certificates have value exactly 16, and there are 9,330 distinct ones. `verify.py`
recomputes all 367,290 quadruples' tariffs from the pinned selected archive and matching
certificate, the same pins as #4365 and #4421. It reads one certificate index per quadruple from
`CERT-INDEX.bin.gz` and checks every certificate exactly, with integer-scaled weights against an
exact bound table that it builds itself.

## The open remainder

On the 3,650 open classes, the best LP value over all `4096 × 15` zero-set and union pairs ranges
from 12.571 to just under 16. Most values are 15.33, 15.5, 15.0 or 15.6. These classes typically
combine two kinds of cheap atom:

- one free plane pair: binary cross rank 0, so messages between the two planes cost 0;
- a cheap full closure: joint Gram rank 5–7 instead of 8, so a message touching all four planes
  costs less than 8.

The LP's fractional covering leans on the free cross atoms. As in the three-plane case, a real
decomposition must cancel them, and these functionals cannot see the cancellation. For the
triples, one more family (mixed `Z`) closed the gap. For quadruples, the families here, including
off-principal blocks `rank(Φ_Z(M)_{X,Y})` tested on three open classes, do not. These quadruples
are **undecided**, not counterexamples. Two direct tests on one of them were also inconclusive:

- an exact `F₂` ILP over 65,025 binary atoms for mass ≤ 15 hit its 900 s limit;
- a short real-coefficient search found nothing.

## Not covered

- The ℚ/ℂ minimum on the 5,584 open quadruples.
- Decoders over five or more planes.
- Native realization, coverage and hosting, which are #4365's caveats.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/four-plane-rank-dual --check-only
python3.12 -B scripts/research_package.py --package research/four-plane-rank-dual
```

The verifier prints `PASS_FOUR_PLANE_RANK_DUAL` in about 4.5 minutes, using only the standard
library. `generation/` holds the scipy scripts that produced the certificates; verification does
not need them.

## Open next questions

1. **Is the four-plane mass below 16 over ℂ on the open classes?**
   - *Why it matters:* a mass below 16 would be the first mixing gain under #4365's contract.
   - *First step:* a cancellation-aware functional for a free plane pair combined with a cheap full
     closure. Alternatively, an exact `F₃` or `F₂` search on the lowest class (LP 12.571).
   - *Blocked by:* nothing.

## Credit

- The contract and the two-plane theorem are CubeJerry's (#4365).
- The labels and matching come from PR1825/2126 (Cinna Davis) and the retained matching
  certificate.
- Gonzalo Mier's PR3990/3997 are predecessors.

Prepared by Ryanson Jonathan with substantial Claude Code (Claude Opus 5.5) assistance.
Apache-2.0.
