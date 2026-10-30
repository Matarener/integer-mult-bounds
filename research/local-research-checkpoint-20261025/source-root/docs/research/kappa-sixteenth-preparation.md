# Preparation for κ = 1/16

Douglas Colkitt, with OpenAI Codex assistance. 2026-10-09. Apache-2.0.

**Research target, not a new bound.** The proposed target is
`T(N) = O(N (log N)^(15/16))`, conditional on the inherited multiplication
framework and any new interfaces proved along the way. The selected witness
remains `κ = 0.000661885549259598`. Reaching `1/16` would increase that saving
by approximately 94.4 times.

This preparation supplies an exact budget, rejection screens and a bounded
first research round. It does not construct stronger suppliers or extend an
analytic theorem. The [current record](current-status.md) and
[domain audit](assembly-domain-audit.md) govern those distinctions.
The completed [first bounded round](kappa-sixteenth-domain-round.md) narrows
the search beyond local boundary tuning using a stronger gross-ledger screen.

## The supplier budget includes the bit wrapper

In the retained balanced assembly, the limiting conversion is
`κ < a/(1+a)`. Therefore `κ=1/16` requires an admitted effective bit saving
`a > 1/15`, together with `(1−β)b > a` for the complex supplier.
These are necessary conditions within this assembly, not general multiplication
or butterfly lower bounds.

The paid bit wrapper matters. Write its coarse saving as `a₀`, its ordinary
leaf saving as `o=384599/10^10`, and its stopping fraction as `θ`. It supplies

`A = (1−θ)a₀ + θo`, with `A < θ < 1−A`.

For `a₀>o`, the strict condition `θ>A` implies
`A < a₀/(1+a₀−o)`. Consequently even the limiting coarse requirement is

`a₀ > (1−o)/14 = 9999615401/140000000000 ≈ 0.07142582429`.

An illustrative budget with room for finite backoffs is:

| Quantity | Rational target | Meaning |
| --- | --- | --- |
| Coarse bit saving `a₀` | `2/25 = 0.08` | New coarse supplier required |
| Stopping fraction `θ` | `3/40 = 0.075` | Pays for ordinary leaves |
| Effective bit saving `A` | `29601153797/400000000000` | About 0.07400288449 |
| Admitted bit saving `a` | `7/100 = 0.07` | Leaves wrapper slack |
| Complex saving `b` | `3/40 = 0.075` | New complex supplier required |
| Phase fraction `β` | `1/100` | Gives `(1−β)b=0.07425>a` |
| Assembly backoff | `1/10^6` | Strict finite slack |
| Target `κ` | `1/16` | Logarithmic exponent `15/16` |

The unchanged assembly function, with an explicitly assumed positive bridge,
has 46 positive slacks at these parameters. Its remaining slack is
`1/32−b = −7/160`. The strict arithmetic check rejects the example.
The retained Gaussian parameter is below `1/4`; that particular restriction
does not block this target. Passing the other displayed inequalities does not
establish supplier availability, the bridge, or the all-size hypotheses.

The first proof task is a domain audit for this specific supplier budget:
trace every use of the small-saving range through the analytic estimates,
cutoffs, uniform recurrences and bridge. An extended exponential enclosure is
only an arithmetic tool, not a proof that `b<1/32` can be removed.

## Exact screens before a large search

For a profile with dimension `m`, role count `W` and child multiplicities `nₜ`,
use the normalized raw moment

`M(s) = Σₜ [nₜ t/(Wm)] (m/t)^s`.

Contraction requires this moment below one. Additional nonnegative costs in
the bit wrapper make a raw-moment failure conclusive and a pass preliminary.
The [diagnostic](../../scripts/prepare_kappa_sixteenth.py) evaluates exact
rational intervals using the pinned enclosure implementation, with a separate
research-only halving-and-squaring extension. Every term is independently
checked by integer powers: for `s=p/q`, its enclosure `[E,F]` must satisfy
`E^q ≤ (m/t)^p ≤ F^q`. No frozen source or production verifier is changed.

At the illustrative targets, the retained profiles give approximately:

| Profile | Target saving | Raw moment | Minimum normalized moment reduction needed |
| --- | --- | --- | --- |
| Bit | 0.08 | 1.18096128 | 15.32% |
| Complex | 0.075 | 1.18700942 | 15.75% |

These are reductions in a normalized recurrence score. They are **not**
percentages of scalar gates to delete. Changing role counts also changes the
normalization; deleting cheap roles while retaining expensive children can
make this score worse. All endpoint, restoration, frame, reserve and fallback
costs must be included before a candidate can become a supplier certificate.

There is also a useful compression-only exclusion. Keep the present complex
ledger's deficit `Δ=1320`, dimension `m=66`, maximum child `20`, and two
disjoint data banks of `v=1320` roles each. Even deleting every auxiliary role
leaves `W≥2640`, hence

`M(s) ≥ (1−Δ/(Wm))(66/20)^s ≥ (131/132)(33/10)^s`.

At the necessary saving `s=1/15`, the exact rational test
`(131/132)^15 (33/10) > 1` rejects this entire fixed-ledger compression route.
A successful mechanism must change a premise: useful deficit, dimension,
child structure, bank obligations, or the transfer contract. This is not an
exclusion of all shared banks, fused operations, or different geometries.

## Bounded next round

1. **Audit the target domain.** Produce a dependency table for the proposed
   `a=0.07, b=0.075` budget. Separate range restrictions removable by a proved
   estimate from restrictions needing a different algorithm. Keep the strict
   production guard until the proof and verifier changes are reviewable.
2. **Compare at most two structural mechanisms.** The preferred first candidate
   jointly designs producer and readout across a charged invocation boundary,
   so useful information can survive a transition that currently loses rank.
   The alternative is a different finite topology or rank geometry, screened
   for full-role obligations before matrix synthesis. Require a concrete
   explanation of which premise of the compression exclusion changes.
3. **Build one exact small prototype per survivor.** Measure the full moment,
   not just additions or representation dimension. Include arbitrary input
   workspace restoration, all terminal obligations, rational edge ranks and
   the complex companion or an explicit obstacle to it. A local improvement
   earns another round only if it extends to a complete paid certificate and
   has a credible scaling mechanism toward the target budget.
4. **Stop and assess.** End this first round after the domain table and two
   candidate assessments. Record missing lemmas and exact rejection reasons.
   Do not turn a failed narrow model into a universal barrier or continue a
   search merely because some uncharged algebra looks promising.

Both suppliers need attention. A spectacular bit-only improvement leaves the
complex supplier binding; a complex-only improvement leaves the bit wrapper
binding. If a new supplier changes maximum child size or dimension, recheck
recursion depth, row stock, guard constants and admissible primes rather than
editing only its histogram.

The [retired aggregate branch](../../research/shared-aggregate-followup/STATUS.md)
already closes its clean producer/separate-readout model. The
[fusion report](../../research/computation-fusion-nine/REPORT.md) records paid
readout failures of two simple fused schedules. The
[current construction review](../../research/coordinated-frames-and-entrance-banks/RESEARCH-REVIEW.md)
also distinguishes scalar savings from frame-compatible implementations.
The proposed boundary-spanning work must change those assumptions explicitly;
repeating the same scalar identities is not a new mechanism.

## Reproduction and provenance

```sh
python3 -B scripts/prepare_kappa_sixteenth.py --check docs/research/kappa-sixteenth-preparation.json
python3 -B tests/test_kappa_sixteenth_preparation.py
python3 -B tests/test_assembly_domain.py
make selected-record-check
```

The [receipt](kappa-sixteenth-preparation.json) pins the selected certificate
and arithmetic sources, records rational bounds and replays the published
47-slack arithmetic with its real numeric bridge. It does not rerun the full
construction suite or certify a new supplier.

The retained finite profiles come from Dugongue's PR #186, on chafreaky's
PR #181 and eumemic's PR #168, with the cumulative lineage recorded in the
[round-eight review](community-round8-review.md). The balance and domain
discussion inherits the contributions credited in the
[assembly-domain audit](assembly-domain-audit.md). This preparation adds
target budgeting and scoped research diagnostics, not a new exponent result.
