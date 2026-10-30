# Three-plane COPY mass: the rank dual of #4365, for every plane triple

**Claim type:** exact lower-bound certificates for every plane triple, plus an exact `F₂` search
where those certificates are weak. **No new κ.** This answers part of the open question of
CubeJerry's [#4365](https://github.com/CrocSwap/integer-mult-bounds/pull/4365), which asks about a
"genuinely joint three-plane decoder". It uses #4365's contract unchanged:

- a scalar message `u vᵀ` is charged `t(S, U) = rank_{F₂}` of the binary label pairing on the
  whole-plane closures of `u` and `v`;
- charges add;
- payload coefficients lie in any field.

## Certificate

For a triple of planes and weights `w ≥ 0` on the seven plane unions `X`, define the functional
`L(M) = Σ_X w_X rank(M_XX)`. It is subadditive. On an atom `u vᵀ` it equals
`Σ_X w_X·[S meets X]·[U meets X]`. Suppose `L(u vᵀ) ≤ t(S, U)` for all 49 closure pairs. Then
every finite decomposition of `I₆`, over **any** field, costs at least `L(I₆) = Σ_X 2|X| w_X`.
This is #4365's two-plane functional `(p−c)rk M_AA + (q−c)rk M_BB + c·rk M`, extended from three
unions to seven. The coordinate decomposition always costs exactly 12.

## Results

The 56 matched planes of the selected archive give 27,720 triples in 486 tariff classes.

**27,395 triples (98.8%) have floor 12, proven over every field.** On these triples three-plane
mixing cannot lower the COPY mass below separate coordinate messages, whatever the coefficients or
the number of terms. Two certificate families cover them:

- **26,977 triples: block-rank certificates.** Each has an integer weight vector, for example
  `w_A = w_AB = w_C = w_BC = 1`, so `L(I) = 2 + 4 + 2 + 4 = 12`.
- **418 triples: zeroed-block certificates.**
  - *Why block-rank fails here.* In these triples, two planes `A` and `B` have binary cross rank
    0, so a message from `A` to `B` costs **0**. Every block-rank functional counts such free
    atoms, which caps that family at 8 or 10 or 11.
  - *The fix.* Let `Φ_Z` zero a set `Z` of off-diagonal plane blocks, here the free ones. Then
    `rank(Φ_Z(M)_XX)` is still subadditive, since it is the rank of a linear image. Free atoms map
    to 0, and `Φ_Z(I) = I` because only off-diagonal blocks are zeroed.
  - *The atom bound.* Restricted to rows and columns `X`, `Φ_Z(u vᵀ)` is a sum over touched row
    planes of `u_P (Σ_allowed v_Q)ᵀ`. Its rank is therefore at most the number of distinct
    allowed column sets, or of row sets. This bound is exact combinatorics and holds over every
    field.
  - *The certificate.* With it, `Σ_X w_X rank(Φ_Z(M)_XX)` certifies 12. For example,
    `2·rank(Φ_Z(M))` does so on the value-8 class.

**325 triples remain open over ℂ.** These are 6 tariff classes with no free atom. In each class,
two of the three plane pairs have a joint closure costing only 2, against 4 for an orthogonal
pair. In three of the classes the full closure also costs 4 instead of 6. Both families stop at 10
there:

- the block-rank value is 10, proven best within that family by an exact dual covering;
- the zeroed-block search over all 64 choices of `Z` also stops at 10 (generator run, not
  certified as optimal);
- an **exact minimum over `F₂`** across all 3,969 binary rank-one atoms (a parity ILP) still gives
  **12** for every class.

## Not covered

- **The minimum over ℚ or ℂ on the 325 open triples.** Neither certificate family decides it, and
  the `F₂` search covers binary coefficients only. A cheaper decomposition over ℂ would have to
  exploit those cheap joint closures. That makes these triples the place to look for a three-plane
  mixing gain.
- **Native realization, coverage and hosting.** These are #4365's caveats, unchanged.
- **Decoders that mix four or more planes.**

## Evidence and reproduction

`generate.py` uses scipy to write `CERTIFICATES.json`: LP weights, zeroed-block weights, covering
certificates and the `F₂` ILP minima. `verify.py` uses only the standard library. It recomputes every triple's tariffs
from the pinned archive and matching, then checks every certificate exactly. The ILP minima are
recorded local evidence, not re-solved.

```sh
python3.12 -B scripts/research_package.py --package research/three-plane-rank-dual --check-only
python3.12 -B scripts/research_package.py --package research/three-plane-rank-dual
```

The second command prints `PASS_THREE_PLANE_RANK_DUAL`. To regenerate the certificates, which
needs scipy 1.13 and numpy:

```sh
python3.12 -B research/three-plane-rank-dual/generate.py
```

## Open next questions

1. **Is the three-plane COPY mass below 12 over ℂ on the 325 open triples?**
   - *Why it matters:* it would be the first mixing gain under #4365's contract.
   - *First step:* an exact search over `F₃` and `F₅` atoms in the cheapest open class, or a
     functional that charges full-closure messages by their rank on the joint label space.
   - *Blocked by:* nothing.
2. **Does a triple-local decoder improve the complete budget?** Fifty-six planes do not split
   into triples, so a mixed pair and triple cover needs its own coverage model.

## Credit

The contract, the two-plane theorem and the open question are CubeJerry's (#4365). The labels and
matching come from PR1825/2126 (Cinna Davis) and the retained matching certificate. Predecessor
screens are Gonzalo Mier's PR3990/3997.

Prepared by Ryanson Jonathan with substantial Claude Code (Claude Opus 5.5) assistance.
Apache-2.0.
