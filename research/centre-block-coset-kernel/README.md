# A route-realized centre common-kernel vector on 4080 owners

**Exact finite certificate and a short written argument. No new κ, supplier or
frontier change.** In the selected calls-0/4 block-repair observation model of
[`centre-block-repair-information`](../centre-block-repair-information/README.md)
and [`centre-block-moore-bound`](../centre-block-moore-bound/README.md), there is
a nonzero vector invisible to both the old observations and the whole later
query, supported on **4080 source owners**. Together with the 15-owner lower
bound, the smallest such support lies in **[15, 4080]**.

This answers, from above, the first open question of `centre-block-moore-bound`
("can the abstract 15-owner incidence meet the actual route labels and
coefficient equations?") and the second open question of PR3147 ("does the
two-stage block obstruction extend all the way?"). It does not settle the exact
minimum.

## Model

Unchanged from the predecessors. For a regular cover owner `g`, `x(g)` is in
`C^112`; the old observation is `Sx(g) = R x(g)` and the later query is
`Tx(d) = sum_p H[:,p] x_p(d rho_p)` with `H = R/4`. `R` and the 112 involutory
routes `rho_p` are taken from the retained, source-authenticated loader of
`centre-block-moore-bound`, which also checks `rank R = 8`, `H = R/4`,
nonparallel columns and unique ordered route products.

## Result

Ports `(0, 6, 85)` have primitive columns
`(1,1,1,1,0,0,0,0)`, `(0,1,1,0,1,0,0,1)`, `(1,0,0,1,-1,0,0,-1)`, and

```text
R_0 - R_6 - R_85 = 0.
```

Let `K = <rho_0, rho_6, rho_85>` and `K+ = <rho_0 rho_6, rho_6 rho_85>` its
even-word subgroup. On the full 73-dimensional routes, `|K| = 8160` and
`|K+| = 4080` (the order of `SL2(16)`), with `rho_0` not in `K+`. No other
port's route lies in `K`.

Put `x_0(g) = 1`, `x_6(g) = -1`, `x_85(g) = -1` for every `g` in `K+`, and
zero elsewhere. Then `R x(g) = 0` at every owner. For any output `d`, the three
possible source owners `d rho_0`, `d rho_6`, `d rho_85` lie in one left coset
of `K+`, because `(d rho_q)^(-1) (d rho_p) = rho_q rho_p` is in `K+`. They are
therefore all in the support or all outside it, and `Tx(d)` is either
`(1/4) R u = 0` or empty. The verifier checks both identities exactly at all
4080 owners and all 4080 touched outputs.

Consequence for the block-repair theorem: a block equal to this coset has a
common kernel of dimension at least one, so it needs at most `104 * 4080 - 1`
repair coordinates instead of `104 * 4080 = 424,320`. The 104-per-owner floor
is therefore not valid for every block size, but this witness saves one
coordinate in 424,320, which is negligible as an information-compression route.

## Why 4080 is the best single-triple witness

Suppose every active owner and every output uses exactly one dependent triple
`{a, b, c}`. The rank-two kernel is one-dimensional, so `x(g) = lambda(g) u`
and each output vector is `mu(d) u`. Matching the shared edge values gives
`lambda(d rho_a) = lambda(d rho_b) = lambda(d rho_c)` for every `d`, so
`lambda` is constant on left cosets of `K+` and a finite support is a union of
those cosets. The census over all 896 dependent triples finds even subgroups of
order exactly 4080 for 56 triples; the other 840 exceed 4080 elements. Mixed
port sets, higher-degree owners and supports that are not unions of cosets
are not covered.

## Reproduce

Python 3.12 and its standard library, from the repository root:

```sh
python3.12 -B research/centre-block-coset-kernel/verify.py
python3.12 scripts/research_package.py --package research/centre-block-coset-kernel
```

Expected output:
`PASS_CENTRE_BLOCK_COSET_KERNEL support 4080 dependent_triples 896 even_orders 4080:56 gt4080:840 range 15..4080 no_new_kappa`.
`--emit` prints the recomputed [RESULT.json](RESULT.json); the normal run
requires byte-level JSON equality with it. Runtime is about one minute.

Controls in `verify.py`: removing one owner leaves exactly three nonzero
outputs; changing one coefficient breaks `Sx = 0` at that owner; the other left
coset of `K+` in `K` is also a valid support (positive control).

## Scope and limits

- Same constant-payload, regular-owner, whole-later-query model as the
  predecessors; the native interpretation stays conditional on their
  common-frame and source-adapter identities.
- The certificate is a scalar linear-information statement. It prices no
  collection, restoration, hosting, precision or recursive child cost and is
  not a sharing construction.
- The exact minimum support remains open in [15, 4080].

## Open next questions

1. **Close the gap [15, 4080].** Why it matters: it fixes the exact block size
   at which owner-local centre repair stops being incompressible. First step:
   enumerate reduced length-8 route relations (the Tutte 8-cage that attains
   the abstract bound needs them) and test the resulting labelled incidences
   against the coefficient equations. Blocked by: no length-8 relation census
   yet.
2. **Is any compression large enough to matter?** The witness saves one
   coordinate per 424,320. First step: compute the full common-kernel
   dimension on this coset with all 112 ports. Blocked by: a large exact
   linear system; a representation-theoretic reduction over `K+` would help.

## Credit

The block-repair observation model and source extraction are Ross
Richardson's PR3071; the 15-owner floor, the PR3147 correction and the
authenticated loader reused here are Sagar Thakrar's
[`centre-block-moore-bound`](../centre-block-moore-bound/README.md) (PR3291);
the dependent-triple braid census is dcharb78's PR3147, the six-relation
classification Gonzalo Mier's PR3097, and the independent route check
Sudarsh3301's PR3168. Centre-sharing and observation lineage: Aaron
Wang/navinor and ywz65. Selected construction credit stays with its retained
authors.

New coset witness, census and verifier: Matarener (session donor Mark), with
substantial Claude (Anthropic) assistance; no independent human review.
New work is Apache-2.0.
