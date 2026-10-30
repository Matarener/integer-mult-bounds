# Polynomial helper gates cannot reduce the labelled linear call minimum

This contribution was produced by Nick Petalas.

**Scoped proof with finite exact corroboration; no new kappa.** Grant each
paid linear-operator call a free, fixed coordinatewise polynomial before or
after it. Require every polynomial to fix zero. For an exact linear endpoint
over an infinite field, this extension has exactly the same Pareto-minimal
labelled operator-call profiles as the linear model, with every required dirty
and clean return included. Any finite number of workspace registers is allowed.

The extraction is explicit:

    b += p(Ta)  or  b += T p(a)   becomes   b += p'(0) T a.

A zero derivative deletes that call. Every other call retains its operator,
ports, label and chronological position. Scalar multiplication by p'(0) must
be permitted in the comparison's linear class. [PROOF.md](PROOF.md) proves the
statement with the degree-one quotient, gives its uniform-family corollary,
and spells out the necessary assumptions. Classical polynomial linearization
is the method; the new step is the declared helper-interface profile theorem
and executable extraction, without any claim of literature priority.

This rejects one proposed escape route from a linear call lower bound even
when polynomial arithmetic is granted free. It does not exclude arbitrary
nonlinear computation. Nonzero constant gates, branching, finite-grid or
rounded execution, nonlinear address permutations, and changed output
contracts need separate analysis. Actual scalar, frame, native, movement,
precision, stock and compiler costs are not equated by this theorem. The
selected supplier and frontier are unchanged.

## Exact evidence and reproduction

The rational implementation in [compiler.py](compiler.py) has a bounded,
validated immutable input contract. It extracts the linear word; it does not
certify the premise that the original endpoint is linear. The checker uses
complete sparse multivariate polynomial expansion to certify that premise
on its fixtures, including every dirty coordinate. A separate dual-number
interpreter corroborates extraction. Literal rational execution checks the
same directions against the known target. The receipt is generated and bound
to SHA256 hashes of all seven source/metadata files.

The finite corpus has 145 exact linear-endpoint fixtures and 1,029 directions
for each of dual-number and numerical comparison, plus 14 controls. It includes
singular and nonsymmetric operators, rational coefficients, both polynomial
placements, clean and dirty borrowed registers, exact inverses, and successive
blocks with noncommuting operators. The five-gate dirty echo's illustrative
profile changes from `T:3, read:2` to `T:2, read:2`. These labels denote abstract
operator classes, not measured Fourier ranks or selected-word jobs.

From the worktree root:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/polynomial-helper-profile-domination/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/polynomial-helper-profile-domination
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/polynomial-helper-profile-domination --check-source-history
```

A portable checkout can use any CPython 3.12 interpreter in those commands.
The registered checks run normal and optimized modes with warnings as errors.
No predecessor mathematical replay, supplier admission, Lean build, Docker
run or complete multiplier is required or claimed. Independent human and
formal proof-kernel review are unclaimed.

## Relation to previous work

Jose Manuel / jmbarrancoml's [#1757](https://github.com/CrocSwap/integer-mult-bounds/pull/1757)
proves a cut obstruction for arbitrary deterministic finite-alphabet gates
under frame conditions. The present theorem uses a different infinite-field
polynomial model, has no common-flag premise, and preserves call labels.
Chris R / Clear1nsight's [#3992](https://github.com/CrocSwap/integer-mult-bounds/pull/3992)
uses a generic Jacobian or transcendence-degree bound for a typed Toom-only
boundary. It does not extract a chronological word or compare call profiles.
Both results are cited premises/context, not audit targets or new claims here.
The finite-menu adaptivity investigation claimed in #1166 concerns branch
selection among linear maps and is separate from this fixed nonlinear word.
No predecessor code is copied or executed. Exact context pins are in
[SOURCES.json](SOURCES.json), alongside the current card and selected record.

## Open next questions

- Can nonzero constant trajectories produce a genuinely cheaper complete
  complex helper word? First account for preparation, constants, the varying
  coordinate derivatives, retained outputs and restoration. The explicit
  translated-square counterexample only shows why this proof does not apply.
- Can a physical finite-grid polynomial or bit-operation mechanism save calls
  while meeting the selected source's precision and all-input requirements?
  First specify that grid and the exact nonlinear consumer; the F2 square
  control shows why a formal derivative is not a certificate on a finite grid.

These are reopening conditions, not an implementation campaign. TASK.json
records the changed card, stopping rule and remaining obligations.

## Verification bounds

The extractor accepts at most eight roles of width four, 32 gates and scalar
polynomials of degree four. Input numerators and denominators are at most
1,024 in magnitude. Rational evaluation rejects intermediates exceeding
4,096 bits. The finite symbolic checker caps each polynomial at 512 monomials
and total degree 16. It uses no recursion or generated code. Every function
is below 60 physical lines. Explicit runtime checks remain active under `-O`.

Python's Fraction arithmetic, dictionaries, tuples and standard dataclass
construction allocate dynamically. This is a managed-runtime deviation from
Power of Ten rule 3, restricted to this finite checker/extractor. The input,
term, degree and scalar bounds constrain live state and reject exhaustion.
The small fixture corpus is checked in both modes. A fixed-capacity backend
would be needed if this extractor became a production bounded-memory service;
no such service or physical memory tariff is claimed. Warning-strict replay
and an AST syntax/function-length check are the available diagnostics; no
separate static type checker is a package dependency.
