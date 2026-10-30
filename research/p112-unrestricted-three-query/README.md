# Unrestricted three-query P112 replacements keep the sharp reader floor

For the literal PR3370 fitting matrix, replacing two indicator terms by any
three independent scalar queries costs at least the original pair under the
actual complete-plane source-to-reader tariff. This holds over every coefficient
field, with unrestricted query values and support. The pair floor is sharp,
and disjoint replacements cannot lower the literal total of 224.

[PROOF.md](PROOF.md) removes PR3407's binary-seed and seed-location assumptions.
The new construction maps three query directions to a unimodular grid triangle
and chooses a fresh binary seed separately at each port. Every original query
and reader zero survives, so the integral replacement cannot cost more. The
retained expanded-identity argument supplies its lower bound. With one or two
nonzero seed coefficients, a two-query rank argument suffices.

This is a scoped obstruction. It supplies no cheaper factorization, physical
COPY implementation, supplier admission, new kappa or selected-frontier update.

## Reproduce

Canonical base `6f100d4bb5083f8c35d96fd95a539811c62f245c`, priority revision 6.
Python 3.12 or later, standard library only. From the repository root:

```sh
python3.12 -I -Werror -B scripts/research_package.py \
  --package research/p112-unrestricted-three-query
```

Direct replay needs no Git history or network service:

```sh
python3 -I -O -Werror -B research/p112-unrestricted-three-query/verify.py
python3 -I -O -Werror -B research/p112-unrestricted-three-query/independent.py
python3 -I -O -Werror -B research/p112-unrestricted-three-query/test_controls.py
```

Set `TMPDIR` to an existing directory outside the checkout if test copies
must stay in a particular location. The controls remove their own temporary
copies on exit. Ordinary replay never rewrites the committed evidence;
`verify.py --write` explicitly regenerates [RESULT.json](RESULT.json).

The primary checker covers all 13 coordinate-equality classes, 40 exact rational
operators and 24 support-dominated integral replacements on literal P112 pairs.
The separate implementation imports none of its algebra. It checks all 12,456
noncollinear ordered triangles over F2, F3 and F5, reconstructs I224 on all
50,176 entries, and independently prices the literal basis at 224. Six control
groups include five real optimized-CLI corruptions and a restored positive run.
Universal all-field coverage comes from the written proof, not extrapolation
from these finite checks. [VALIDATION.md](VALIDATION.md) records exact checks,
environment, code bounds and verification limits.

[SOURCES.json](SOURCES.json) pins the live selected labels, the unchanged retained
PR3370 certificate, and predecessor proof sources. No unmerged predecessor code
is imported. Review can start with the per-port seed rule in PROOF.md and the
three distinct nonbinary cancellation levels in the behavioral control.

## Open next questions

Four or more queries, dependent lists, multiple external dimensions and a changed
fitting matrix remain open. Before expanding a native construction, give an
exact lower-tariff factorization priced against its actual readers, then price
acquisition, coefficients, restoration, frames and the whole consumer. The
fixed-K three-query obstruction does not exclude a new physical contract.
[TASK.json](TASK.json) gives concrete first steps and blockers.

## Credit

Tekalign's PR3370 supplies the retained partition and rank-32 fit. PR3407 supplies
the binary-seed rational predecessor. PR3398 identifies the actual-reader cost
boundary. PR3383 owns the fixed-rowspace self-Gram floor, while PR3345 and
Philippe Van Velzen retain the integral expanded-identity argument. Credit stays
with Matarener/Mark/PR3335, ctoth, ywz65, Sagar Thakrar, Cinna Davis, Adam Gall,
Jeremy Diviney and the retained E8/P112/native/compiler/supplier lineage.
Prepared by Nick Petalas. Apache-2.0. The two implementations are author
computation, not independent human or formal-kernel acceptance.
