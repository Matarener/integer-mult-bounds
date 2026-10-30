# Rational three-query directions keep the P112 reader floor

Every arbitrary rational three-query basis in the span of two literal PR3370
queries and one independent binary seed costs at least the original pair under
the actual complete-plane source-to-reader tariff. The floor is sharp. Applying
disjoint pair replacements cannot lower the literal global bill of 224.

This closes the arbitrary-rational-direction continuation of
[PR3398](https://github.com/CrocSwap/integer-mult-bounds/pull/3398) for exactly
three independent queries and a binary seed. That predecessor treated seven
canonical directions. Here signs and denominators are unrestricted. The
proof splits by seed coefficients and reader supports, constructs a cheaper
integral replacement in the mixed-reader cases, and uses rank subadditivity
when all readers touch both groups. [PROOF.md](PROOF.md) states every assumption.

This is a scoped obstruction, with no new kappa or supplier admission. The
matrix and physical tariff stay fixed. Native coefficient execution and the
full construction invoice are outside this result.

## Reproduce

Canonical baseline `6f100d4bb5083f8c35d96fd95a539811c62f245c`, priority revision 6.
Python 3.12 or later, standard library only. From the repository root:

```sh
python3.12 -I -Werror -B scripts/research_package.py \
  --package research/p112-rational-reader-pricing
```

Direct replay is Git-free:

```sh
python3 -I -Werror -B research/p112-rational-reader-pricing/verify.py
python3 -I -Werror -B research/p112-rational-reader-pricing/independent.py
python3 -I -Werror -B research/p112-rational-reader-pricing/test_controls.py
```

[RESULT.json](RESULT.json) records all 496 literal query-pair geometry checks,
50,176 expanded identity entries, 1,009 finite support-pattern classes and
eighteen exact rational fixtures. Universal coverage comes from the written
proof, rather than extrapolation from those fixtures. The separate checker
reconstructs the support classes through set partitions and uses rational
elimination instead of the primary cofactor code. All checks are author
computation. [VALIDATION.md](VALIDATION.md) records diagnostics and limits.

[SOURCES.json](SOURCES.json) binds the canonical label input and retained exact
PR3370 certificate. The package requires no unmerged Git object, external
optimizer or network service. Normal replay does not rewrite evidence.
`verify.py --write` explicitly regenerates the mathematical receipt.

## Open next questions

Multiple external seed dimensions, nonbinary seeds and dependent lists of
four or more queries remain open. A useful next candidate must price each
query against its actual reader. Start with one exact rational factorization
of the same K whose total rectangular tariff is below 224, then examine its
native acquisition, restoration and complete paid invoice. A source self-Gram
decrease alone does not supply that candidate. [TASK.json](TASK.json) records
the first steps and blockers. This package starts no further research round.

## Credit

Tekalign's PR3370 supplies the unchanged literal partition and rank-32 matrix.
PR3398 identifies the actual-reader boundary and supplies the canonical
seven-direction predecessor. PR3383 owns the fixed-rowspace self-Gram result;
PR3345 and Philippe Van Velzen retain the integral expanded-identity floor.
Credit also stays with Matarener/Mark/PR3335, ctoth, ywz65, Sagar Thakrar,
Cinna Davis, Adam Gall, Jeremy Diviney and the retained E8/P112/native/compiler
lineage. Prepared by Nick Petalas. Apache-2.0. Assistance is disclosed in
TASK.json. No independent human or proof-kernel review is claimed.
