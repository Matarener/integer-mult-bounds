# Selected P111 orthogonal port-pair screen

**Bounded positive local result. No supplier or κ improvement is claimed.**

## Change and mathematical scope

For the selected tuned P111 bit word, the verifier forms the exact binary port
Gram matrix `B0 = (J + G/2) mod 2`, where `G` is the root-line Gram matrix. It
constructs a deterministic orthogonal matching of 55 pairs and one residual
port. For every matching in the bounded neighborhood of two-edge switches and
one-edge residual swaps, it solves the exact F2 plane-coefficient system. The
best of 751 candidates has an inherited scalar copy-rank charge of **112**,
attained twice; the next charge is 128. Its 55 plane matrices have ranks
`{0: 45, 1: 7, 2: 3}`, giving 13 plane terms and one residual-line term, all
priced at rank 8.

The coefficient identity is checked after a basis change of the actual word's
target and source factors. The replacement reproduces all **73,371 entries**
of the selected 111-by-661 dirty decoder map, including its 550 helper-input
columns. Its SHA256 agrees with the independent P111 Parseval audit receipt.
This verifies an algebraic decomposition of the existing dirty map; it does
not schedule those terms as legal physical operations.

The charge 112 is a sum of exact rational pairing ranks under the inherited
scalar-copy tariff. The original nine-line decoder costs 63 in that model, so
this decomposition is not a copy-cost improvement by itself. It does not
establish the physical source/target plane endpoints, a native route, hosting,
precision, restoration or a complete family bill.

## Task and overlap

This refines the `coverage-law-change` task to test one concrete port grouping
on the selected P111 word before attempting a physical implementation. A
favorable relaxation with `unpaid = 221/111` gives an upper bracket
`a_hi = 572091203/125000000000` (about 0.004577); at `a = 3/997`, it tolerates
at most 29 more centre-charge units. The value `221/111` is an assumption for
this screen, not a proved coverage identity, and the 29 units must cover every
unpriced route and interface cost. The selected κ remains
`0.001672660197076918`; this result does not certify κ above `0.003`.

The refreshed overlap check found [PR #1900](https://github.com/CrocSwap/integer-mult-bounds/pull/1900),
which audits five fixed rank-two coefficient blocks and obtains scalar charge
73. Those coefficient-space planes do not establish a matching of physical
P111 ports. [Discussion #1587](https://github.com/CrocSwap/integer-mult-bounds/discussions/1587)
records the separate source and target endpoint obligation. This package adds
an exact bounded port-matching decomposition and full dirty-map replay; it does
not close that endpoint obligation.

## Validation

From the repository root, run the registered replay:

```sh
python3 scripts/research_package.py --package research/p111-selected-plane-matching --check-only
python3.12 scripts/research_package.py --package research/p111-selected-plane-matching
```

The verifier uses standard-library Python, exact F2 elimination, `Fraction`
rank calculations and the pinned `ceiling.py`. It source-hash checks every
live input, compares the full dirty map with its predecessor receipt, and
rejects controls with a missing residual line or plane term. `RESULT.json`
retains the matching, neighborhood census, exact bill, basis change and
conditional ceiling bracket.

## Credit

The selected bit word and its lineage are documented in the
[tuning package](../e8-bit-p111-tuned/tune/README.md). The scalar pairing-rank
convention is documented in the [P111 copy-rank certificate](../p111-copy-rank-certificate/PROOF.md);
the related fixed-block audit is [PR #1900](https://github.com/CrocSwap/integer-mult-bounds/pull/1900).
This package preserves that predecessor work and does not claim its result.
Prepared by Gonzalo Mier with OpenAI Codex assistance; Apache-2.0.

## Open next questions

- **Can each matched plane be realized with the required physical source and target endpoints on one legal schedule?** This determines whether the assumed unpaid amount corresponds to actual work removed. First map one winning pair through the selected word's frames, ownership and reads, then replay its arbitrary dirty-input action. The present factorization has no source-acquisition, target-advance or restoration schedule.
- **Do all interface and recursive costs fit within the conditional 29-unit margin?** A passing relaxation has no force if routing, basis conversion, storage, hosting, precision or cleanup consumes the margin. First price one complete plane, including scratch restoration, against the same `ceiling.py` model. No complete native plane implementation or joint complex/bit budget is currently available.
