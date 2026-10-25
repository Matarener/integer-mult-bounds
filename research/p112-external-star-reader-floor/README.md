# One shared external query cannot lower the reader bill

For any number k of disjoint literal indicators, adding one common external
query direction and one compensation term cannot reduce the actual reader
tariff. The theorem holds over every coefficient field, for arbitrary seed
values and support, zero or nonzero arm coefficients, and any finite even
orthonormal partition of binary labels. It is sharp in the stated class.

The exact module is

    sum_j a_j a_j^T
      = sum_j a_j (a_j + alpha_j c)^T - (sum_j alpha_j a_j) c^T.

The complete-plane rectangular binary-rank bill is at least the sum of the
selected indicators' group sizes. Such replacements cannot lower the whole
literal PR3370 P112 tariff of 224. The compensating reader is fully charged.
[PROOF.md](PROOF.md) gives the zero-preserving binary reduction and rank proof.
The primary checker also gives an exactly support-preserving GF4 reduction.
The separate implementation uses binary support domination instead.

This answers one architecture within
[PR3463's external-query handoff](https://github.com/CrocSwap/integer-mult-bounds/pull/3463).
The initial two-target idea was already covered by
[PR3414](https://github.com/CrocSwap/integer-mult-bounds/pull/3414), whose exact
proof was read before synthesis. It is not claimed again. The new domain is
k>=3 targets and k+1 queries with an external direction, plus the general
partition theorem. PR3414 treats a two-target, three-independent-query domain;
PR3463 treats arbitrary lists inside a two-target span. Exact source heads,
hashes and the scope comparison are in SOURCES.json and PROOF.md.

## Evidence and replay

The replay authenticates the selected 112 labels and Tekalign's unchanged
PR3370 partition. It checks all 50,176 expanded-identity entries, 12,492 local
finite-field states, 4,960 literal triple fixtures with external seeds, one
fixture for every k from 1 to 32, and 12,544 exact rational/GF4 operator entries.
The triple fixtures are corroborating examples, not an exhaustive optimization
over seeds. A four-independent-query external example attains its baseline
bill of 24, with zero arm coefficients allowed.

The separate binary checker imports none of the primary arithmetic. It checks
3,500 rational local states, 30 literal all-k fixtures, a non-P112 geometry
and invalid-partition controls. Five actual optimized CLI corruptions reject
altered live bytes, retained fixture bytes, transfer logic, field arithmetic
and the committed receipt. The restored primary and separate checks pass.

Use Python 3.12 or later and an existing external TMPDIR for disposable copies:

```sh
python3.12 -I -Werror -B scripts/research_package.py --package research/p112-external-star-reader-floor
python3 -I -O -Werror -B research/p112-external-star-reader-floor/verify.py
python3 -I -O -Werror -B research/p112-external-star-reader-floor/independent.py
python3 -I -O -Werror -B research/p112-external-star-reader-floor/test_controls.py
```

Ordinary replay does not rewrite RESULT.json. The explicit `verify.py --write`
option regenerates it. VERIFY.json registers all three standard-library commands.
[VALIDATION.md](VALIDATION.md) records the verification and code boundaries.

## Limits and next decision

This is a scoped negative theorem, with no native supplier, new kappa or
selected-frontier change. A general four-query pair realization with two
independent external directions is outside the statement. So are arbitrary
joint recodings of three targets. Acquisition, coefficient execution, frames,
dirty restoration, hosting, stock, precision, compiler/all-size admission and
outer multiplication transfer remain separate obligations. Independent human
and formal proof-kernel review are unclaimed.

The saving predicate fails for this common-perturbation architecture before
physical costs are added. Stop its synthesis here. Another construction needs
a changed query/reader contract and an explicit complete bill.

## Open next questions

Can a four-query pair realization with two independent external directions
beat the literal pair bill? First provide the exact queries and actual readers,
verify their operator and price every complete-plane rectangle. No such
lower-cost witness or paid consumer is supplied here. TASK.json records this
bounded first step and its blockers.

## Credit

Nick Petalas. Apache-2.0. Tekalign's PR3370 supplies the retained partition.
Philippe Van Velzen and PR3345 supply the expanded-identity tariff argument.
Nick Petalas's PR3414 and PR3463 supply the immediate scope boundaries.
Matarener/Mark, ctoth, ywz65, Sagar Thakrar, Cinna Davis, Adam Gall, Jeremy
Diviney and the retained P112/E8/native/compiler/supplier lineage keep their
predecessor credit. Frozen fixture bytes and attribution are unchanged.
