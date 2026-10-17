# Orthonormal k-group covers of P112: exact fitting ranks 57 (k = 3) and 68 (k = 4)

**Finite algebraic result. No native copy price, supplier or new κ.** The selected
record is unchanged.

A k-dimensional port contract (source `E_j → FULL`, target `0 → E_i⊥`, with
`E_i` the span of port `i`'s group of `k` orthonormal labels) leaves `u = k`
unpaid coordinates per family.
[kport-group-scalar-endpoint-audit](../kport-group-scalar-endpoint-audit/README.md)
fixed its scalar mask: `K_ii = 1`, and `K_ij = 0` unless `i` and `j` lie in
**distinct, mutually orthogonal** groups. The published k = 3 cover (PR2041)
leaves only 102 free ordered pairs, so its fitting rank is near 112. For k = 2,
PR2484 found exact rank 49 on PR1825's matching and PR3335 found 34 on a rematched
one. This package covers k = 3 and k = 4.

## Result ([CERTIFICATE.json](CERTIFICATE.json), [RESULT.json](RESULT.json))

| k (unpaid) | cover | exact fitting rank, every field | colouring floor | reference |
|---:|---|---:|---:|---|
| 2 | 56 rematched planes | 34 | 28 | PR3335 |
| 3 | 37 orthonormal triads + 1 singleton port | **57** | 57 | PR2041's cover: ~112 |
| 4 | 28 orthonormal tetrads | **68** | 56 | — |

For each cover the verifier checks the following:

- the groups partition the 112 ports and are orthonormal;
- a colouring puts only pairwise orthogonal groups in a class;
- one support per class and position gives a 0/1 matrix that fits all forced
  entries (12,154 for k = 3, 12,192 for k = 4), with dense rank equal to the support
  count mod 2, 3 and 1000003;
- a set of pairwise non-orthogonal groups of the same total size forces that
  identity block in every fit, so the rank is exact.

**Why the colouring floors hold.** An exhaustive enumeration finds that the largest
sets of pairwise orthogonal labels have size **eight** (4,032 such frames), and
that none has size nine. A colour class therefore holds at most two groups of size
≥ 3. Any colouring of a triad cover needs at least ⌈37/2⌉ = 19 classes, i.e. 57
supports. A tetrad cover needs at least 14 classes, i.e. 56 supports. The k = 3
cover attains its floor.

The singleton port in the k = 3 cover is forced because 112 = 3·37 + 1. Its
coverage-law effect is that of a mixed-port cover (see mixed-port-coverage-audit).

## What it means and what it does not

The fitting rank is the **query dimension** of a scalar decoder for the k-port
mask. It is not a copy price ([contract map](../../docs/research/paired-plane-contract-map.md)).
The copy budgets of [complex-multi-unpaid-copy-budgets](https://github.com/CrocSwap/integer-mult-bounds/pull/3344)
give scale: about 264 (u = 3) and 360 (u = 4) per call at the incumbent tie, and
more with large local children. Independent per-port copies (about `112·u`) exceed
those budgets.

These covers exist with fewer channels than ports: 57 rather than 112 at k = 3.
Whether a native implementation can share one copy per channel, and at what rank,
is open. No such implementation, restoration, precision or hosting bill is
claimed.

## Reproduce

```sh
python3.12 -B research/p112-k-group-cover-ranks/verify.py      # ~2 s
python3 scripts/research_package.py --package research/p112-k-group-cover-ranks --check-only
```

Standard library only; `--write` regenerates RESULT.json. Controls reject a
single-colour assignment and a non-orthonormal group. `discover/` keeps the
search scripts (simulated annealing over size-preserving swaps from an exact
cover, and frame packing) as provenance only. They use local absolute paths and
are not part of verification.

## Open next questions

1. Can a tetrad cover reach its colouring floor of 56? It would need 14 classes,
   i.e. a partition of the labels into 14 orthonormal 8-frames. Bounded packing
   found 12 disjoint frames and no partition.
2. What is the native price of one shared channel for a k-port decoder? This is
   the binding blocker for using any of these covers. A first step is to expand one
   colour class's supports into payload arrays and legal native operations (PR2203's
   independent-block contract is the baseline).

## Credit

1337isnot1337 (PR2041, PR2297 k-group covers; PR1825 planes); the kport-group
scalar endpoint audit and Discussion 1587 (ctoth, philippeVV) for the mask;
ywz65 (PR2471) and thakrarsagar (PR2484) for the clique and colouring method and
the verifier primitives reused here. Found and checked by Claude (Anthropic) via
Claude Code, in a session donated by Mark. Apache-2.0. No human or formal review is
claimed.
