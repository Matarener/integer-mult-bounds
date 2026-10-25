# Minimum paid-call counts for small mixed-negative Q8 endpoints

## Result

In the mixed-negative Q8 bit-register model of PR3570/PR3578/PR3589, the
minimum number of paid rank-one calls realizing a diagonal endpoint is
**exactly** the parity-rounded uniform bound of PR3589 once `t <= 2`.

```text
PR3589 lower bound:   5n >= 11t,        inherited parity:  n = t mod 2
                      n >= ceil(11t/5) rounded up to a parity t value

t = 1   (zi)          minimum 3   attained
t = 1   (zj)          minimum 3   attained
t = 2   (zi, zi)      minimum 6   attained
t = 2   (zi, zj)      minimum 6   attained
t = 2   (zj, zj)      minimum 6   attained
```

Each minimum is attained by an explicit word. Three calls on one role
multiply that role by the cube of its label, and `i^3 = zi`, `j^3 = zj`, so
the witnesses are the `3t`-call disjoint construction, which happens to sit
exactly on the bound for `t = 1, 2`.

Two consequences.

- **The uniform constant is sharp in the sense PR3589 left open.** No strictly
  stronger function of `t` can hold at `t = 1` or `t = 2`, because the bound
  is met there. This settles open question 2 of that package for `t <= 2`.
- **The bound is not attained for `t >= 3` by these witnesses.**
  `t = 3` admits the bound value `7` but the best witness here has `9` calls;
  `t = 4` balanced admits `10` and the best witness has `12`. Those minima
  remain `{7,9}` and `{10,12}` respectively, exactly as PR3589 left them.

This is a mathematical side result for the nonabelian bit-register model. It
does **not** claim a new kappa, a physical supplier, an improved selected
result, or a complete multiplication theorem. The selected frontier is
unchanged.

## Reproduce

Use CPython 3.12 from a repository root:

```sh
python3.12 -Werror -B scripts/research_package.py --package research/q8-min-length-census
```

Direct scientific and control replay also work without Git or network:

```sh
python3.12 -I -Werror -B research/q8-min-length-census/verify.py
python3.12 -I -O -Werror -B research/q8-min-length-census/verify.py
python3.12 -I -O -Werror -B research/q8-min-length-census/test_package.py
```

The package is self-contained: standard library only, no Git objects, no
network, no third-party dependency. `RESULT.json` is the exact finite
receipt; [VALIDATION.md](VALIDATION.md) states coverage and limits.

## Evidence

- All 64 Q8 products agree between an independent signed-unit table and the
  basis product, and `i^3 = zi`, `j^3 = zj`, `z^2 = 1` are checked directly.
- Eight explicit witnesses are replayed to their exact diagonal endpoints.
- Five **complete** breadth-first searches exhaust every word on 1 and 2 roles
  up to the lengths `2` and `5`, over `7` and `56,084` distinct states
  respectively, and find none. These are a cross-check: for `t <= 2` the
  PR3589 bound plus parity already excludes every shorter length at *every*
  role count, so the census is not the source of the lower bound.

## Sources and limits

The model, the notation and the `5n >= 11t` bound are inherited unchanged from
Nick Petalas/PR3570, PR3578 and PR3589. No predecessor mathematics is
re-derived here; this package supplies attainment witnesses and a complete
small-case census.

Full group-algebra finite fields, longer-word classification, the sharp
constant for `t >= 3`, physical execution, scalar/routing/restoration/
hosting/precision costs, a complete supplier, an improved kappa, independent
human review and formal proof-kernel acceptance are all **out of scope and
unrun**. A randomised search for a ten-call balanced four-target word is
recorded in [VALIDATION.md](VALIDATION.md) as a **search failure only**; it is
not an exclusion and not evidence of novelty.

## Open next questions

- Is the balanced four-target minimum ten or twelve? PR3589's bound admits
  ten and no witness below twelve is known. A complete bounded census, not a
  randomised search, would decide it.
- Is the `t = 3` minimum seven or nine? This is the smallest case where the
  parity-rounded bound is not already attained by the `3t` construction.
- What is the sharp uniform constant for `t >= 3`? Attainment at `t <= 2`
  does not settle this.

## Credit

Nick Petalas/PR3589 for the mixed-negative boundary-rank bound, with
PR3570/PR3578 for the cubic identities and the two-orientation method,
PR3536 for the sign-sensitive chronology and PR3558 for the cyclic subspace
argument. Their retained lineage includes Tuafo/PR2900, ywz65/PR2587,
Aaron Wang/PR2318, Cinna Davis and steph4n-gh.