# Elementary abelian diagonals still cost one call per non-identity entry

For every rank \(k\ge 2\), every finite register count, and every diagonal
target in \(\mathbb F_2[(C_2)^k]\), the legal alphabet of non-identity
rank-one updates has exact paid-call minimum \(t\), the number of
non-identity diagonal entries. Restored dirty roles are allowed and do not
lower the count. The direct coordinate word attains \(t\). The selected
multiplication exponent is unchanged
(\(\kappa=0.001672660197076918\)).

The address ring is commutative of exponent two. It is not a chain ring:
\(\mathfrak m/\mathfrak m^2\) has dimension \(k\ge 2\). The proof is the
graded image argument in [PROOF.md](PROOF.md). Finite checks compare two
multiplication engines and exhaust small words; they are not a substitute
for that argument.

## Pin search

Pinned CrocSwap `main` is `bb4bccbf42844d2801487450727c2f63e10d1d0f`
(`research_baseline_sparse: name sparse-checkout omissions without touching pinned inputs`,
[#3725](https://github.com/CrocSwap/integer-mult-bounds/pull/3725)).
Upstream had not moved at the time of the search.

`git grep` of `F2[x,y]/(x^2,y^2)` across `research/*/PROOF.md` and
`research/*/README.md` at that commit hits only
[`research/bit-cyclic-root-barrier`](https://github.com/CrocSwap/integer-mult-bounds/blob/bb4bccbf42844d2801487450727c2f63e10d1d0f/research/bit-cyclic-root-barrier/PROOF.md).
That proof assumes \(R=\mathbb F_2[z]/(z^q)\). Its non-chain paragraph says
the one-column socle witness "does not construct a saving in that group
algebra." The open question there asks for a module invariant or a shorter
word in a noncyclic alphabet. No package on the pin states a diagonal
minimum for \(\mathbb F_2[(C_2)^k]\), \(k\ge 2\).

The \(q=2\) case of the chain-ring theorem does not imply the rank-\(k\ge 2\)
statement. Labels outside a single \(C_2\) subgroup are legal, including on
a monochrome target, and \((z_1)\) is incomparable with \((z_2)\). The \(C_4\)
and \(C_{2^k}\) involution minima stay in the chain-ring socle argument and
are not recomputed.

## Evidence

The standard-library verifier is read-only unless `--write-receipt` is
passed, and that switch refuses to overwrite an existing receipt. Receipt,
source, and task JSON are parsed with duplicate keys rejected. Admission
checks are `need` calls, so they stay in force under `-O`.

```sh
python3.12 -I -O -B -W error research/elementary-abelian-diagonal-minimum/verify.py
python3.12 -I -O -B -W error research/elementary-abelian-diagonal-minimum/test_verify.py
python3.12 -B scripts/research_package.py --package research/elementary-abelian-diagonal-minimum
```

The default verifier prints `PASS_ELEMENTARY_ABELIAN_DIAGONAL_MINIMUM`.
The registered replay prints `PASS_REGISTERED_RESEARCH_PACKAGE`.

## Limits

There is no native rational-frame conversion, hosting bill, or recursive
moment. The result is an exact finite-alphabet minimum. It does not price a
selected bit supplier and does not claim a shorter circuit.

## Open next questions

Does a nonabelian group algebra of order at most 16 admit a legal diagonal
word shorter than its non-identity count in this same rank-one model? The
graded bound uses commutativity and a nonzero image in \(\mathfrak m/\mathfrak m^2\).
The \(C_4\) involution lies in \(1+\mathfrak m^2\), so this count does not
apply there. A first step is to list, for one nonabelian alphabet, which
non-identity elements lie in \(1+\mathfrak m^2\) before searching. Native
frame, hosting, and precision bills remain unpriced; the cyclic 2-power
socle census should not be rerun.

## Credit

The chain-ring diagonal theorem and the explicit non-chain socle witness are
from `research/bit-cyclic-root-barrier` (CrocSwap [#2513](https://github.com/CrocSwap/integer-mult-bounds/pull/2513)),
which credits Cinna Davis for the C4 root-lift. Prepared by Wentao Li with
substantial AI assistance. Apache-2.0.
