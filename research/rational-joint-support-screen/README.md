# Generic rational two-plane bases retain the copy invoice 8

**Negative result; no kappa improvement claimed.** I extended the exact
four-message, two-plane screen from binary coefficient values to every
structurally possible support pattern of a generic rational 4x4 basis. Across
all 1,540 pairs of the 56 certified planes, every tested support pattern has
copy invoice at least 8. Each pair attains 8, the separate-plane baseline; no
strict improvement occurs.

The earlier binary screen in [PR #3990](https://github.com/CrocSwap/integer-mult-bounds/pull/3990)
covered 391 inverse-support signatures. This package derives all
37,823 structurally nonsingular 4x4 support matrices, which induce 439 generic
source/reader signatures. The 391 binary signatures are all recovered, along
with 48 additional signatures that require coefficient values beyond the
binary assignment. The two screens use the same pinned labels and pairing-rank
tariff, but this verifier does not depend on PR #3990 or its branch.

A second, exhaustive coefficient-value check covers all
\(3^{16}=43{,}046{,}721\) matrices with entries in \(\{-1,0,1\}\). Of these,
27,947,520 are invertible. Their exact inverse-support signatures are exactly
the same 439 signatures as the generic rational family: the signed values add
no new pattern or lower invoice. The C11 enumerator and its 439 exact matrix
witnesses are in [ternary_screen.c](ternary_screen.c) and
[TERNARY-SCREEN.txt](TERNARY-SCREEN.txt).

This is a complete negative result for **generic rational coefficients at a
fixed 4-message, 2-plane interface**. It does not prove a lower bound for all
rational encoders: special rational values outside the signed-ternary alphabet
can make a cofactor vanish even when its support minor has a perfect matching.
Those remaining cancellation strata, overcomplete factorizations, mixing
three or more planes, coefficient scaling costs, changed multi-array
primitives and physical routing/restoration remain outside scope. No
replacement coverage law, supplier, construction round or change to selected
kappa follows.

## Exact support model

For a 4x4 support matrix \(S\in\{0,1\}^{4\times4}\), a perfect matching in its
bipartite row/column graph is equivalent to the determinant polynomial not
being identically zero. The inverse entry \((P^{-1})_{j,k}\) is nonzero for a
generic rational assignment exactly when the 3x3 minor obtained by deleting
row \(k\) and column \(j\) has a perfect matching. The source support of
message \(j\) comes from column \(j\) of \(S\); its reader support comes from
row \(j\) of the generic inverse. Each support is then mapped to one or both
of the two complete planes.

These generic zero/nonzero claims hold simultaneously over \(\mathbb Q\):
every structurally nonzero determinant or cofactor is a nonzero polynomial,
and the product of those polynomials and all permitted entry variables is
nonzero. A nonzero multivariate polynomial over an infinite field has a
rational point where it does not vanish. Thus every enumerated generic
signature is realizable by an exact rational matrix. This does not include
special assignments on the cofactor-zero varieties.

The exact tariff for one message is the rank over \(\mathbb F_2\) of the
selected binary pairing matrix restricted to its complete source and reader
plane spans. It is not coefficient-matrix rank. The baseline has four
messages, two per plane, each charged two, for total copy invoice 8. We test
all 439 generic signatures against all plane pairs: 676,060 cases. Each pair's
minimum is exactly 8. `RESULT.json` records the histogram, representative
minimizer, pinned source digests and digest of every pair minimum.

The verifier checks structural nonsingularity by both permutation search and
subset dynamic programming. It separately computes exact integer determinants
and adjugates for all 65,536 binary matrices; the resulting 22,560 invertible
matrices induce 391 signatures, all contained in the generic set. Pairing
ranks are computed by independent row and column elimination routines. It
validates all 439 signed-ternary witness matrices against exact Python
determinants/adjugates and compares their signature set to the generic family.
When a C11 compiler is available, the registered replay also compiles and runs
the complete \(3^{16}\) sweep and byte-compares its output with the pinned
receipt. Without a compiler, the Python algebraic screen and witness checks
still run; only the exhaustive signed-ternary replay is skipped.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3.12 -I -B research/rational-joint-support-screen/verify.py
python3.12 -I -O -B research/rational-joint-support-screen/verify.py
python3.12 scripts/research_package.py --package research/rational-joint-support-screen --check-only
python3.12 scripts/research_package.py --package research/rational-joint-support-screen
```

The replay is read-only and must reproduce [RESULT.json](RESULT.json) byte for
byte. `VERIFY.json` registers both pinned live inputs. Source commits and
digests are in [SOURCES.json](SOURCES.json). The scientific base is canonical
main `20ecf2891d80b5acf18d980b2164fb44ea7faa90`, priority revision 6. Frozen
selected evidence remains unchanged.

The supplementary C audit uses only C11 and integer arithmetic. Its checked
build is:

```sh
cc -std=c11 -O3 -Wall -Wextra -Werror ternary_screen.c -o /tmp/ternary-screen
/tmp/ternary-screen > /tmp/TERNARY-SCREEN.txt
cmp TERNARY-SCREEN.txt /tmp/TERNARY-SCREEN.txt
```

The registered Python replay performs this check automatically when a C11
compiler is available. The recorded run used GCC 11.4.0 on Linux; a separate
UndefinedBehaviorSanitizer run produced the same receipt. The main package has
no Python package dependencies; a C compiler is needed only to replay the
signed-ternary sweep.

## Open next questions

Can rational values outside \(\{-1,0,1\}\) produce a cheaper inverse
support through exact cofactor cancellations? The next step is to classify inverse zero-pattern
strata for 4x4 matrices, starting with supports whose cofactor polynomials have
multiple matching monomials and solving for exact rational witnesses. A
pattern counts only if the determinant and every required nonzero entry remain
nonzero; then test its tariff on all 1,540 plane pairs. The blocker is
completeness of the cancellation-stratum enumeration. Any invoice saving also
needs priced coefficient arithmetic and a realizable native endpoint.

## Credit

Credit the selected paired-plane matching and endpoint lineage, Discussion
[#1587](https://github.com/CrocSwap/integer-mult-bounds/discussions/1587),
[PR #2126](https://github.com/CrocSwap/integer-mult-bounds/pull/2126), and the
binary support screen in [PR #3990](https://github.com/CrocSwap/integer-mult-bounds/pull/3990).
Prepared for Gonzalo Mier with substantial OpenAI Codex assistance in the
symbolic model, enumeration, verifier, checking and writing. No independent
human review is claimed. New work is Apache-2.0.
