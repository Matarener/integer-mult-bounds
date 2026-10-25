# Fixed three-seed BIT star cannot reach primitive exponent .002

This is an all-parameter necessary-cost obstruction, conditional on the
declared seed profile and ideal deficit. It is not a universal BIT bound.
Scientific pin: `20ecf2891d80b5acf18d980b2164fb44ea7faa90`.

Let the complete child histogram be `c_r`, parent arity `m`, width `W`, and
deficit `D=mW-sum(r*c_r)`. Its normalized moment at primitive exponent `a`
is below one exactly when

    sum_r r*c_r*((m/r)^a-1) < D.

The changed seeded star has `L>=3`, `m=1+7L>=22`, and three unchanged R438
seed calls. The pinned source profile of each seed has rank mass5121 and
maximum child rank7. Grant the remaining new calls, idle queries, owner
completion and padding their most favorable declared deficit `D<=33`.
This upper budget is `2*111-3*63`; the zero-private FULL-target fanout adds
no surplus. Any extra charges reduce the available deficit. A construction
changing this coverage or any seed profile requires a new analysis.

For every `a>=1/500`, the three seeds alone exert pressure at least

    15363/500 * ln(22/7)
      > 15363/500 * 2*(15/29 + (15/29)^3/3)
      = 21108762/609725
      = 33 + 987837/609725 > D.

Here `exp(t)-1>=t` for `t>=0`, and the strict logarithm bound is the first
two positive terms of `ln(x)=2*atanh((x-1)/(x+1))`. Every omitted term is
nonnegative because all child ranks are at most the parent arity. This
proves rejection for every L, without an asymptotic approximation, finite
parameter sweep or any missing owner cost being treated as free progress.

The argument tests primitive exponent .002 directly. Earlier handoff
screens evaluated the conservative retained map `a=kappa/(1-kappa)`;
that map is not asserted to be necessary for every newer outer theorem.
The present rejection also applies when the outer exponent approaches a.

Reproduce with `python3 seeded_star_pressure.py` from this directory.
The producer reads the literal seed profile through Python's AST, pins
the source word hash, and uses exact fractions. Its three sensitivity
controls deliberately invalidate the coarse rejection witness by dropping
one seed, raising the maximum rank, or raising D. These controls do not
establish that any changed construction exists or has a positive bound.
