# Three-term rigidity closes a new eight-call twist pattern

A new rank-distance/syzygy argument closes the first three-contribution
escape named in [Discussion4999](https://github.com/CrocSwap/integer-mult-bounds/discussions/4999).
Distinct PBQ transports on M_m(F2) differ in rank by at least m; three-term
quadratic cancellation would force rank at most one. For m>=2 this makes
all active relative transports equal. Source compatibility then excludes the
specific eight-call pattern with two J calls, three P_s and three D_s under
all orders and arbitrary odd-denominator rank-one frames and independent
per-register PBQ conjugations. Every diagonal target has mod2 rank<=1.

[PROOF.md](PROOF.md) is the quantified result. The package includes a genuinely
first-order-feasible m3 eight-call fixture with all frames nonzero, a complete
272,160-case normalized GL2 local check and 39 independent sparse finite
group-ring word checks. Twelve representative orders corroborate the
order-independent proof; they are not an exhaustive eight-call search.
General GL(V) admits the explicit rank-one-difference control, so this is
not a theorem for arbitrary linear twists, extra mixing, helpers or patterns.
No native tariff, kappa improvement, supplier or full multiplication theorem.

## Reproduce

```sh
python3.12 -I -W error -B research/bit-three-term-twist-rigidity/verify.py
python3.12 -I -O -W error -B research/bit-three-term-twist-rigidity/verify.py
python3.12 -B scripts/research_package.py --package research/bit-three-term-twist-rigidity
```

Expected `PASS_THREE_TERM_TWIST_RIGIDITY`; standard library only. The verifier
imports no predecessor executable. Exact proof dependencies are in SOURCES.json
and declared in VERIFY.json. Native/full-route/Lean checks are outside scope.
The result is author-checked with AI assistance, not independent human or
proof-kernel acceptance. See VALIDATION.md for performed checks.

## Open next questions

1. Find a different first-order-feasible pattern with at least four active
   contributions and derive its dirty-input syzygies before attempting synthesis.
   This result supplies no candidate or justification for an unchanged census.
2. Price a legal native realization of the explicit general-GL(V) transvections
   before treating their algebraic escape as a useful construction.

Structured gates are in TASK.json. Original assignment and selected result
are provenance only; selected frontier files are unchanged.

## Credit

JoyboyBrian, with substantial OpenAI Codex assistance; Apache-2.0. PR5003 by
Krzysztof Wójt supplies the second-order quotient, source compatibility and
seven-call obstruction; PR4953 supplies the two-sided model and first-order
witness. Credit Cinna Davis/PR2110 and the Ali Romman, eumemic and huxint
lineage. The new contribution is the uniform rank-distance/three-term lemma,
its different eight-call pattern, and independent algebraic corroboration.
