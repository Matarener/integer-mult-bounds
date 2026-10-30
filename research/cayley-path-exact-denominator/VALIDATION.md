# Verification contract

The written result is a scoped algebraic proof. The checks corroborate the
new denominator formula and precision substitution, not predecessor results.
The two source Markdown files are authenticated by their manifest hashes.
No predecessor code is imported or executed.

## Finite domains

- Connected blocks use every reduced A/B with 4<=B<=28 and
  1<=A<=floor(B/4), at every dimension 1 through 9. Dense Fraction inversion
  checks the whole matrix's least denominator and the far-corner witness.
  An independent binomial sum checks the continuant recurrence.
- Signed supports use all edge tuples in {-1,0,1}^(n-1), for n=1 through 6,
  at parameters 1/4, 2/9 and 3/13. Every full inverse is compared with the
  transpose, and its exact common denominator is checked too.
- All one- and two-instruction words over six explicitly listed instruction
  fixtures are checked on all ten independent input columns. They include
  rational linear combinations, repeated terms, a zero coefficient, named
  forward/inverse applications, an ordinary query and a self-source query.
  Every role is retained. The denominator bound is checked on the whole bank
  and its difference from the identity program.
- The nine-dimensional guard fixture runs the exact eight-call program and
  its integer/dyadic replays at both prescribed grids. Every returned
  coordinate is checked against the same source error budget.
- Controls reject four invalid parameters and three invalid edge inputs.
  Separate arithmetic controls distinguish an omitted gcd, omitted primitive
  scaling, product versus lcm, maximum versus lcm, and omitted scalar factors.

Counts and package hashes come from the generated stdout receipt. No receipt
is written by hand or committed. All replay outputs and elapsed-time logs
belong outside the checkout.

## Commands

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/cayley-path-exact-denominator/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/cayley-path-exact-denominator/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/cayley-path-exact-denominator
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/cayley-path-exact-denominator --check-source-history
```

Hosted execution is separate from these local checks and from independent
scientific review. The PR body records current local timings and CI status.
No proof assistant, selected scientific cold replay, physical native caller,
upstream coefficient producer or general optimized detector is run.

## Code inspection and bounded deviations

The verifier uses structured control flow without recursion. Its largest
matrix is capped at dimension 32. All enumeration ranges are fixed above;
the register programs are private tuples with at most two instructions in
the census, and eight in the guard example. All functions fit within 60
physical lines. Meaningful requirements are explicit exceptions and remain
enabled with Python optimization. Source inputs and outputs are read-only.
No callbacks, code generation, reflection or subprocesses occur.

Rule 3, allocation after initialization, requires a managed-runtime deviation
for Python Fraction, integer and list allocation. The scope is this finite
standalone checker. Matrix buffers contain at most 32 rows and 64 augmented
columns. Rational parameters have at most 256 denominator bits, connected
determinants at most 32 times the parameter-size order, and the only replay
grids are bounded by 4096 bits. The fixed fixture coefficients and iteration
counts bound live arithmetic sizes. Python/library allocation internals are
not instrumented. Direct normal/optimized runs exercise the capacity controls.
If a production caller is added, its resource contract needs separate design.

Rule 10 uses the repository's Python package replay plus isolated
warning-strict normal and optimized execution. No repository-wide static
analysis configuration is changed for this isolated research package.
