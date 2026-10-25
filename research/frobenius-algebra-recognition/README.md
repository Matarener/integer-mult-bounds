# Recognize Frobenius-truncated prime-field algebra tables

Given a nonzero multiplication table over a prime field `F_p`, this package
decides whether it is isomorphic to

```
F_p[x_1,...,x_r] / (x_i^(p^h_i)),  h_i >= 1,
```

recovers the height multiset, and constructs a verified monomial change of
basis and its inverse. The input uses one common basis for both inputs and
the output; the unit need not be a coordinate vector and is recovered.
The empty height list represents `F_p`.

This answers the supplied prime-field algebra-table part of
[Ali Romman's recognition handoff in PR5459](https://github.com/CrocSwap/integer-mult-bounds/pull/5459).
The [canonical investigation thread](https://github.com/CrocSwap/integer-mult-bounds/discussions/5493)
records the advance claim and public status. There is no new kappa, physical
supplier, arbitrary tensor isotopy recognizer, or formal proof-kernel result.

## Criterion and implementation

After checking the commutative, associative and unital laws, let `F(a)=a^p`,
let `E` be the least integer with `p^E >= n`, and compute

```
J = ker(F^E),
V_e = (ker(F^e) + J^2)/J^2,
d_e = dim(V_e) - dim(V_(e-1)).
```

The table belongs to the displayed family if and only if `codim J = 1`
and `p^(sum e*d_e) = n`. Height `e` occurs `d_e` times. Actual kernel lifts
give tangent generators and hence a surjection from the proposed model;
dimension equality makes it an isomorphism. [PROOF.md](PROOF.md) proves both
directions, the nilradical bound, coordinate invariance, constructive witness
and polynomial complexity for fixed `p`.

The order of operations matters: Frobenius induced on `J/J^2` is always zero.
Taking its kernel there would incorrectly assign height one to
`F_2[t]/(t^4)`. We instead take the kernels in the full algebra and then
project them to the tangent quotient.

[`recognize.py`](recognize.py) exports `recognize(p, table)` and
`validate_witness(p, table, witness)`. Structure constants use
`table[i][j][k]`; integer coefficients are normalized modulo `p`. Malformed
input raises `ValueError`. A well-formed table outside the family returns
`status="rejected"` with its reason and available diagnostics.

An accepted result contains `heights`, `generators`, `unit`,
`monomial_exponents`, `transporter` (a list of columns), and `inverse`
(matrix rows). Exponent tuples are lexicographic, last coordinate fastest.
The witness checker verifies generator relations, all monomial columns,
both inverse identities and every model basis product. It does not trust
the computed radical or height flag. Primality uses trial division, so the
implementation does not claim polynomial primality testing in `log p`.

## Evidence and reproduction

The package uses only the Python standard library. In CPython 3.12.14,
the registered normal and optimized commands check:

- 46 positive presentations over primes 2, 3, 5 and 7, through dimension 16,
  including mixed heights, changes mixing the unit and radical, a
  noncoordinate one-dimensional unit, and a hidden short generator;
  3,217 independent basis-product identities.
- Nine nonmember controls, six malformed inputs, two coefficient-normalization
  controls and seven rejected witness mutations. The nonmembers include
  nonlocal algebras, a nonsplit residue field, extra relations, failed algebra
  laws, and `F_2[x,y,z]/(x^2+yz,y^2,z^2)`: dimension eight, recovered heights
  `(1,1,2)`, predicted dimension sixteen.
- An independent bitset/finite-span oracle covers all 525 commutative fixed-unit
  tables: four two-dimensional `F_2` tables, 512 three-dimensional `F_2`
  tables and nine two-dimensional `F_3` tables. Exactly 64 of the 512
  three-dimensional tables are associative; their nilradical dimensions
  0, 1 and 2 occur 24, 24 and 16 times respectively.
- Complete unit-fixing basis orbits of both four-dimensional target algebras over `F_2`:
  1,344 basis changes per target yield 336 cyclic and 56 elementary distinct
  tables. Every accepted transporter is checked independently. This is not
  an enumeration of all `2^24` four-dimensional commutative fixed-unit tables.

From the repository root, run the four bounded commands in `VERIFY.json`:

```sh
python3.12 -B scripts/research_package.py --package research/frobenius-algebra-recognition
```

The launcher checks source metadata and uses a fresh bytecode-cache namespace
for each command. Expected markers include `PASS_FROBENIUS_ALGEBRA_RECOGNITION`
and `PASS_REGISTERED_RESEARCH_PACKAGE`. Both verifiers accept `--json` for
deterministic reports. Their direct Git-free forms, also suitable for a
checked committed-package export, are:

```sh
python3.12 -I -B -X pycache_prefix=/tmp/frobenius-fresh-cache research/frobenius-algebra-recognition/verify.py --json
python3.12 -I -B -X pycache_prefix=/tmp/frobenius-fresh-cache research/frobenius-algebra-recognition/check_exhaustive.py --json
```

Use a fresh cache path for each replay; repeat with `-O` for the optimization
control. Explicit exceptions implement all verification conditions, so
optimized Python cannot remove them. Finite tests corroborate the written
all-dimension theorem; they do not replace a mathematical review.

## Scope and provenance

Base `32890bc5de034ab8fc93ac88ead7279a6a416d04`, priority revision 7.
The `formal-interface-lemma` card is retained verbatim in `TASK.json`, with
the changed scope explicitly recorded: a written algebra-recognition theorem
and implementation, not a proof-assistant build or the card's acceptance gate.
The selected record and retained predecessor notes are provenance-only pins
in `SOURCES.json`; replay has no external scientific inputs, network calls,
or dependency on an unmerged predecessor commit.

Ali Romman's PR5459 at `bef3575ddb19c44434a7e2460a353eac7c4d9387` supplies
the unequal-height family, height flag and recognition handoff. His PR5316
at `c777c9a4b5f50a0e1561b2e24304486f40e8d001` supplies the univariate
predecessor. Nick Petalas's PR5252 at
`07e6f55d18d2d3fd6dcea19bd642d71657c5fe14` supplies the etale comparison,
normalization and nilpotent follow-up. David Ganz and the retained atlas
lineage retain their credit. No pending executable or source archive is
imported. The proof uses classical commutative algebra, including the finite
nilpotent form of [Nakayama's lemma](https://stacks.math.columbia.edu/tag/00DV);
no general literature-priority claim is made.

The advance overlap check covered the live handoff, relevant all-state PR
keyword searches and a Frobenius Discussion search. Sparse local search
covered only 5 of 7,402 tracked notes. Neither this coverage nor an absent
keyword match proves novelty. The separately claimed finite-etale recognition
and native/caller/CRT work are outside this package.

## Open next questions

1. **Recover a compatible algebra table from an arbitrary three-factor tensor.**
   This would remove the remaining coordinate/isotopy promise. Start with a
   faithful regular nucleus action and verify both input transports and the
   output map before using this recognizer. No such reconstruction is supplied.
2. **Extend to supplied non-prime finite fields.** This would match the broader
   predecessor family. Start with explicit field coordinates and the
   semilinear characteristic-power Frobenius kernels; this implementation
   assumes prime-field linearity and supplies no extension-field layer.

Neither task alone supplies physical coefficient preparation, native gates,
precision/movement accounting or supplier admission. No selected construction
cold replay or proof-assistant build was needed or run.

Prepared by **apoursh**, with substantial OpenAI Codex assistance across the
coordinator, proof, implementation and separate finite-domain audit workers.
The separate oracle is an implementation cross-check, not independent human
or proof-kernel acceptance. New contribution: Apache-2.0.
