# The fifteen thin query stages need fifteen rank-one requests per port

**Scoped negative result; no new κ.** The retained p16 controllers keep 15 chronological `QUERY_SHEAR` stages,
each paid as one rank-one request per port line (1,560 on the p104 word of
[PR #5907](https://github.com/CrocSwap/integer-mult-bounds/pull/5907), 1,680 on the
[PR #5398](https://github.com/CrocSwap/integer-mult-bounds/pull/5398) direct controller). Target **P8** of the
κ ≥ 0.0035 atlas ([PR #5586](https://github.com/CrocSwap/integer-mult-bounds/pull/5586), `provider-targets.md`)
asks for a causal linear realization of all 15 stages with at most 528 requests in total, each latent channel
evaluated on a currently available linear combination of fields, the 18 full calls kept. This package shows that
**on every port the 15 shear results are linearly independent modulo everything that is free**, so any such
realization needs at least 15 requests per port, i.e. at least the present count. P8 cannot be met by per-port
channels on any of the three retained controllers; the only route left is a channel that serves several ports at
once, which is a new physical primitive and not a controller rewrite.

Base: canonical main `19fdb086ea96af9a9f87936a2b888e10af4ed810`. Inputs are pinned in [SOURCES.json](SOURCES.json).

## The count

One central port. The 32 banks hold elements of `R = K[Q, Q⁻¹]`; bank `i` starts with the formal symbol `b_i`.
The controller alphabet is replayed literally (`research/p104-productive-controller/caller.py`): `ADD` with a
scalar, `SWAP`/`SIGNED_SWAP`, `Q_POWER ±2` and the stage markers are free; a `LOCAL` is a paid full call that
yields `Q⁻¹x` (or `Qx` backward) for its source content `x`; a `QUERY_SHEAR` must deliver `Q⁻¹u_j` (or `−Qu_j`) for
the actual source content `u_j`, which includes the results of earlier stages.

A rank-one latent channel evaluated on one available content `v` yields an element of `R·v`, and `Q^{2k}v` is
already free, so each channel adds at most one generator to the free span. With the 18 full calls kept, after `m`
channels every content lies in `F + span(q_1, …, q_m)`, where `F` is the span of the initial banks and the 18
full-call outputs. All 15 shear results must lie there, hence

    m ≥ dim(F + span{n_1, …, n_15}) − dim F.

The markers are specialised to 1 and `Q²` to a nonzero scalar θ; both are ring homomorphisms, so a realization in
the marked Laurent model maps to one in the specialised model and the specialised count is a valid lower bound.
Over `Q` with exact rationals, for θ = 7/3 and θ = 11/5, on each of the three controllers:

| Controller | Events | dim F | dim (F + shear results) | Floor per port | Greedy causal realization |
|---|---:|---:|---:|---:|---:|
| PR5398 direct (`kappa-backward-controller-20261023`) | 162 | 49 | 64 | **15** | 15 |
| Joint-helper lattice source (`joint-helper-lattice`) | 154 | 49 | 64 | **15** | 15 |
| p104 productive, all-forward (`p104-productive-controller`) | 218 | 49 | 64 | **15** | 15 |

`F` plus the 15 results is the whole 64-dimensional port space. Each shear result is also independent of `F` plus
the other 14, so the floor does not depend on the order of events, and the greedy causal realization (query exactly
when the current result is outside `F` plus earlier results) attains it. The first "attainable" question of P8,
two consecutive stages in fewer requests, is answered negatively by the same count.

Consequences: the thin pool is incompressible per port, 15 × 112 = 1,680 on the direct controller and
15 × 104 = 1,560 on the p104 word; the atlas's 528 is impossible with per-port channels. Together with
[`research/thin-query-shear-floor`](../thin-query-shear-floor/README.md) (fusion with a full call needs two
queries; parity floor 15 with lazy central frames) the per-port answer for the thin stages is complete.

## Verification

```sh
python3.12 -B research/p104-thin-query-port-floor/verify.py
```

Under a second, standard library only ([portfloor.py](portfloor.py)). It authenticates the pinned controllers;
computes the floor on all three for both values of θ; checks every result against the other 14; checks the greedy
count; runs three controls: a redundant sixteenth shear (the output of the last full call on its own pair) is
recognised as free with the floor unchanged; the flawed model that puts every present content into `F` (including
the queried results themselves) collapses to floor 0; declaring odd central powers free collapses to floor 0, so
the whole floor is the odd-power obstruction; and compares [RESULT.json](RESULT.json) in full.
Marker: `PASS_P104_THIN_QUERY_PORT_FLOOR`.

## Scope and limits

Per-port, linear, scalar model: a channel acts on one port line through the central algebra, as every retained
request does. A channel acting on several ports at once is outside the model and outside the present price list
(the P104 physical contract fixes a central port and a 17-axis route per port); it is not excluded here. The
markers are specialised, which can only lower the floor. Native maps, the caller, the compiler and the outer checks
are not involved; the selected record is unchanged. Agent check, not human acceptance.

## Open next questions

- Can one latent channel serve several port lines inside the P104 physical contract? First step: state it as a
  physical job in `caller.py` terms and price it in the complete invoice; a channel of rank `r` serving `k` ports
  must cost less than `k` H1. Blocked by a new physical primitive, not by this package.
- Does the symbolic-marker floor equal 15 or exceed it? Only of interest for a sharper statement; the conclusion
  cannot change because specialisation is a homomorphism. First step: repeat the count over `K(θ, D_0..D_33)`.

## Credit

Cinna Davis (controllers), Ali Romman (PR5398 direct controller, PR5398 replay), Dugongue (atlas PR5586) and the
P104 lineage retain credit; nothing of theirs is modified. Prepared by Matarener with Claude (Anthropic) via
Claude Code. Apache-2.0.
