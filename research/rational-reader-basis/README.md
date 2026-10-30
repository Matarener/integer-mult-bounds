# Eight fewer coefficient ADDs for the actual Gaussian reader

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: finite explicit rational-kernel construction with a scoped
algebraic proof. No new kappa.

After Ali Romman's [PR #5646](https://github.com/CrocSwap/integer-mult-bounds/pull/5646)
basis, one further rational shear gives

    D5 += (3/40) D4,       J4 -= (3/40) J5.

It reduces the complete four-shear coefficient bill from 20,352 to 20,344.
There are 208 source coefficients and 9,964 reader coefficients, compared
with 208 and 9,968 before. The new word preserves every arbitrary dirty
centre and the supplied reader operator. It uses four shears and thirty
borrowed fields. [PROOF.md](PROOF.md) gives the all-input argument.

This answers a small part of #5646's first Open next question. Its
single-dyadic-ADD local optimum permits this rational escape. The common
denominator changes from 960 to 1,200, introducing a second factor of five.
The largest coefficient remains one; the factor row-sum bounds remain
9/4 and 1036/15. A reduction in coefficient support does not establish a
reduction in bit operations, routing, precision, recursive cost or kappa.
The selected frontier and all five framework assumptions are unchanged.

## Reproduction and evidence

From the worktree root, with the Python 3.12 standard library:

```sh
~/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/rational-reader-basis/verify.py
~/git/integer-mult-bounds/.venv/bin/python3.12 -W error -O -B research/rational-reader-basis/verify.py
~/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/rational-reader-basis
~/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/rational-reader-basis --check-source-history
```

Expected verifier status is `PASS_RATIONAL_READER_BASIS`. The JSON output
is generated from the replay and bound to package hashes; no stored receipt
is accepted as evidence. The source manifest binds the supplied factors,
port directions, inverse-character data and published basis. The replay
constructs these inputs to apply the new step; it does not run or audit
predecessor rank, inverse-certificate or local-optimum checks.

The new checks compare every coefficient of the changed pair's kernel
product, the literal inverse basis and all untouched factor entries. A
literal 512-address payload executes and counts both complete words,
compares every data output and restores every dirty centre coordinate.
Five controls detect three losing coefficients, an omitted inverse source
update and a corrupted reader coefficient. The finite payload supports
instruction-order checking; the algebraic proof covers arbitrary inputs.

## Open next questions

1. Does the eight-instruction saving survive the extra factor of five in
   one concrete rational-arithmetic caller? Start with a primitive that
   implements these coefficients, including rounding, routing and storage.
   Its complete physical price is missing.
2. Can one broader basis reduce coefficient support further without
   increasing the complete physical bill? Start from the explicit changed
   factors and a priced candidate. This package claims neither pairwise nor
   global optimality and reserves no follow-up.

The structured questions and changed card scope are in [TASK.json](TASK.json).

## Credit and dependencies

Ali Romman's #5646 supplies the actual factors, ten-operation basis and
broader-basis open question. David Ganz, @Dugongue, supplies
[PR #5634](https://github.com/CrocSwap/integer-mult-bounds/pull/5634), the
reader substitution and four-shear identity. Ali Romman's
[PR #5640](https://github.com/CrocSwap/integer-mult-bounds/pull/5640)
supplies the grouped tariff and dirty-bank boundary.
`kernels.py` reconstructs #5646's supplied factor formulas and basis with
that credit retained. Its original files and notices are unchanged.

The underlying `centre-code-services` sources retain
`reciprocal-native-responses`, `native-centre-capture`,
`centre-metric-encoders`, PR #3133, #3148, #2588 and #2226 and their
individual contributor notices. This package cites their source identity
and boundary rather than asserting independent acceptance. The new result
is the explicit 3/40 shear and its eight-instruction saving.
Independent human and formal proof-kernel review are unclaimed.

## Code bounds and verification limits

The verifier is standard-library Python. There is no recursion, subprocess,
network operation, solver or mutable global research state. The fixed
matrix dimensions are 112 ports, 30 centre coordinates and 512 addresses;
each sparse kernel has at most 57,344 positions. There are exactly ten
supplied basis operations and one new operation. All input bytes are
SHA256 authenticated before decoding. Functions stay below sixty lines.
Runtime `require` checks remain enabled under optimization.

Power-of-Ten rule 3 has a managed-runtime deviation. Python allocates
integers, fractions, dictionaries and lists while computing. The fixed
source dimensions and 16 MiB encoded/decoded source bounds constrain live
data, but no fixed allocation pool or byte-exact heap bound is claimed.
The literal replay uses a shared integer denominator at each of four
shears, avoiding per-address rational allocation. Interpreter/library
allocation remains outside direct inspection. Warning-strict normal and
optimized registered runs supply the available runtime diagnostics;
no unavailable static analyzer or formal kernel is claimed as run.
