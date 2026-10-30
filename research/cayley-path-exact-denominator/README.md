# Exact Cayley path denominators and a smaller sufficient grid

This scoped algebraic proof determines the exact least common denominator of
every signed path Cayley block. It improves one arithmetic step in Ali
Romman's [PR #5339](https://github.com/CrocSwap/integer-mult-bounds/pull/5339).
For coprime positive a,b and an n-vertex connected path,

```text
D_0 = 1, D_1 = b, D_n = b D_(n-1) + a^2 D_(n-2)
den((bI-aK)^(-1)(bI+aK)) = D_n/gcd(D_n,2b).
```

The inverse has the same denominator. Disconnected label runs combine by
least common multiple. The far-corner matrix entry proves minimality.
[PROOF.md](PROOF.md) proves the formula for every finite signed path and
substitutes it into the predecessor's complete rational-register separation
and error implication. No predecessor scientific replay or audit is performed.

In a specified nine-dimensional alternating-label example with eight calls,
the same sufficient precision inequality drops from **318 to 108 fractional
bits**, a reduction of 210. This is a guard improvement, not least precision,
a runtime measurement, native admission or a new multiplication exponent.

## Reproduce

From the repository root, using CPython 3.12 and only its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/cayley-path-exact-denominator
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/cayley-path-exact-denominator/verify.py
```

A different CPython 3.12 path can replace this machine's interpreter path.
The registered commands run the warning-strict verifier in normal and
optimized modes. Expected scientific marker:
`PASS_CAYLEY_PATH_EXACT_DENOMINATOR`.

The verifier compares the formula with dense rational inversion, enumerates
signed supports, checks complete dirty-input bank maps, executes both dyadic
grids in the strict example, and exercises rejection controls. It emits a
generated stdout receipt bound to all seven package file hashes. It writes
no files. [VALIDATION.md](VALIDATION.md) records domains and execution limits.

## Limitations

The exact per-matrix denominator need not be the least common denominator
of a composed program. The new sufficient grid need not be optimal. The
funded detector's error theorem is credited to #5339. Its general arithmetic
kernel, native compatibility, physical costs and upstream coefficient
producer are not audited here. The written theorem is unbounded in path
size; the finite checker limits matrices to dimension 32 and tests the
explicit smaller domains in VALIDATION.md.

No selected caller, production precision policy, physical supplier, new
kappa, selected-frontier change or complete multiplication theorem is
claimed. Independent human and formal proof-kernel review are unclaimed.

## Open next questions

- Can program-level cancellation reduce the lattice H below the product of
  the exact per-call denominators? Start with one literal inverse-pair word
  and retain all scalar and dirty-return effects. Matrix-level minimality
  does not settle this question.
- Can this arithmetic refinement lower a bound for a native-compatible
  witness with a complete paid error contract? First pin its actual operator
  relations and caller. That binding and its physical cost remain open.

## Related open work

The live publication search found no open PR studying these skew-path Cayley
denominators or this orthogonal-witness precision bound. Historical #5315,
#5339 and #5352 are credited predecessors, not open work. Search coverage
and its sparse-local limitation are recorded in TASK.json.

## Credit

This contribution was produced by Nick Petalas. Credit Ali Romman #5339 for
the separation/error consumer and its open optimization question, and #5315
for the rational orthogonal realization; Krzysztof Wojt #5262 for the inverse
compiler and shortest-word theorem; zxv #5235 and the retained
dirty-echo/tensor/phase and rational-series lineage. Cayley transforms,
continuants, adjugates and integer lattice separation are classical. No
global literature-priority claim is made. Apache-2.0.
