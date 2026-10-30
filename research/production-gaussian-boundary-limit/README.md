# Uniform Gaussian conditioning at the production scale

The exact full-cell broad Gaussian inverse has the two-edge half-line limit
uniformly when `theta^(1/10) <= b=pi/alpha² <= 1`. This includes the actual
PR4100 choice `alpha=ceil(sqrt((4/pi)log(16p)))`, uniformly for
`1/(4p²)<=theta<=1/p²`. Its inverse norm is eventually at most `p^(2+eta)`
for every fixed `eta>0`. The exact asymptotic coefficient retains the full
infinite product; see [PROOF.md](PROOF.md).

The predecessor proved the boundary limit only for fixed alpha. Normalizing
finite q-products before estimating them removes the absolute constants that
prevented its production substitution. This is a new quantified analytic
implication, not another finite parameter run or a claim of a faster solver.
The exact original phase, `N=floor(1/theta)`, both boundary layers and the
ceiling in alpha are retained. The first source case is still
alpha3/theta1/400/N400; its geometry is checked without pretending that a
small fixture proves the uniform theorem.

The small standard-library checker authenticates the retained sources,
checks nonvacuous normalized-product bounds by rational enclosures, compares
the whole q-LDU sum with independent exact elimination, and exercises the
rescaled exponent and floor/ceiling geometry. Controls discriminate dropped
positive summands, omitted distance from the edge, missing sqrt(b) grid
scaling, reflection offsets and mistyped receipts. RESULT.json is mandatory;
ordinary verification does not rewrite it.

```
python3.12 -B scripts/research_package.py --package research/production-gaussian-boundary-limit
python3 -B scripts/check_research_commit.py --package research/production-gaussian-boundary-limit --check-source-history
```

Both normal and optimized runs are registered. An official committed export
can execute verify.py with its declared inputs without Git or network.
This is a scoped written theorem and finite corroboration, not independent
human or formal-kernel acceptance. No selected frontier changes.

## Costs and limits

The full cell is an analytic source matrix, not an admitted capped
RawGaussian program. The result does not price coefficient formation,
truncation, common-reference rounding, prefix amplification, inverse
application, page storage/delivery, tape movement or integer recovery.
These remain obligations rather than zero charges. The existing p^10
allowance dominates this exact inverse eventually; applying it to a
perturbed reference still requires its actual perturbation invoice.

## Open next questions

Bind one explicitly rounded full-cell reference to the new polynomial inverse
bound, then identify an actual consumer whose complete preparation and
physical execution costs justify using it. Different section lengths or
phase endpoints need a separate theorem. TASK.json records first steps.

Canonical claim: [Discussion4202 comment19172868](https://github.com/CrocSwap/integer-mult-bounds/discussions/4202#discussioncomment-19172868).
Base 32890bc5de034ab8fc93ac88ead7279a6a416d04, priority7. Fresh overlap was
coordinated by the parent before assignment; no global novelty guarantee is
claimed. SOURCES.json binds the exact inherited theorem and source geometry.

JoyboyBrian, with substantial OpenAI Codex assistance. Apache-2.0.
Credit Jose Manuel/#4193, Vlado Vojdanovski/#1673, Cinna Davis/PR4100,
Ryanson Jonathan/#4435, Nick Petalas/#5150, the retained JoyboyBrian
full-cell and half-line work, and the classical q-LDU and product identities.
Frozen predecessors and their notices remain unchanged.
