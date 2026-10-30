# Commutative products can require a third right-vector factor

**Scoped proof with a complete small-model certificate. No new kappa.**
This answers Open question 3 of Nick Petalas's
[PR4276](https://github.com/CrocSwap/integer-mult-bounds/pull/4276):
commutativity does not make `cost(M)=delta(M)` for every invertible target.

The exact source model has two roles, paid factors `I+u y^T` with `u in R^2`
and `y in K^2`, and arbitrary `GL2(K)` maps free anywhere. `K` embeds
diagonally into a product algebra. The free maps and right vectors must be
common to all components; the `R` left coefficients may vary by component.
No scratch or borrowed helper is used.

## Result

For an invertible target over `R=K^k`, two paid factors suffice exactly when
some common nonzero base-field row `phi` and column `t` make every
`phi M_i t` nonzero. Every invertible target over a finite product of field
`K`-algebras has an explicit three-factor word, with right vectors
`e1,e2,e1`. If `K` has `q` elements, the component threshold is sharp:

- `k<=q`: every invertible target has `cost=delta<=2`.
- `k>=q+1`: an invertible target can have `cost=3` and `delta=2`.

[PROOF.md](PROOF.md) gives the complete quantified argument, including the
quadratic-extension construction for **every finite field**, not just prime
fields. It rederives the predecessor criteria, which retain their credit.
Projective counting, field extensions and determinant algebra are classical;
this is their scoped application to the retained research question.

The small counterexample is `R=F2^3`, with component matrices

```text
I = [[1,0],[0,1]],  J = [[0,1],[1,1]],  J^2 = [[1,1],[1,0]].
```

For each nonzero `t`, these three matrices send `t` to all three nonzero
binary columns. Every nonzero row kills one of them, so all nine common
pivots fail. An explicit attaining word is in the proof. In particular the
predecessor's suggested invertible `F3^3` search cannot refute the claim:
three components are still below its four-component obstruction threshold.
This does not classify singular targets or every commutative algebra.

## Exact finite evidence

`engine.py` independently enumerates the literal paid alphabet and computes
the complete invertible `F2^3` metric by BFS. It imports no predecessor code
and uses no projective criterion. All 216 targets are reached using 22 distinct
invertible paid factors. Filtering singular factors is sound for an
invertible endpoint over a product of fields.

| Paid cost | delta | Targets |
|---:|---:|---:|
| 0 | 0 | 6 |
| 1 | 1 | 54 |
| 2 | 2 | 144 |
| 3 | 2 | 12 |

The distance certificate checks all 4,752 paid edges and all 1,296 free edges,
132 conjugations, all 216 attaining matrix words and 13,824 arbitrary-input
evaluations. Delta is computed from the literal six-by-two binary column
matrix at all six free endpoints. `EXPECTED-BFS.json` retains every target,
distance, delta endpoint and attaining word.

The separate `oracle.py` computes the complete same 216 cost/delta records
from projective pivots and common literal-vector images, with no BFS import.
All records agree. It checks sharp witnesses over prime fields
`2,3,5,7,11,13,17,19`, all 512 possible nonzero first-column triples for
`F3^3`, and 2,550 literal three-factor identities over `F2,F3,F5,F7`.
`EXPECTED-ORACLE.json` retains the complete regenerated data. Prime-field
replay corroborates the written all-finite-field theorem; it does not replace
that proof or claim an extension-field software census.

**Word conventions:** BFS records use execution order: apply the recorded
free map first, then left-apply each paid factor, giving `P_r...P_1 S`.
Oracle `word` arrays use algebraic product order `F1 F2 F3`; a column-vector
execution applies `F3` first. These are separately checked witnesses and must
not be interchanged. The independent review identified this presentation
distinction; it is explicit here without changing either computation.

Controls detect omitted factors, wrong component and free chart, reversed
products, a dropped obstruction component, treating componentwise free maps
as the common free model, composite moduli incorrectly labelled fields,
singular targets outside the upper theorem, and typed/coverage evidence
corruptions. Explicit checks remain active under optimized Python.

## Reproduce

Python 3.12 standard library only:

```sh
python3.12 -B scripts/research_package.py --package research/right-vector-commutative-products
```

Both registered normal and optimized warning-strict commands freshly execute
both implementations, compare **all typed regenerated data** with the
retained artifacts, and compare all 216 cross-engine cost/delta records.
The command prints a compact receipt; the full data remains in the two
EXPECTED files. Source contracts are exact unchanged exports of PR4276 head
`59c7bac0122ef2b80793c30a3d52329db6bdf17d`, retained through input ancestor
`326b25e5da8330cc3a44f84e8dcde0e4ff50c5e0` with Git/SHA256 pins.

## Open next questions

1. Specify a product of commutative local algebras and prove the unit/right-ideal
   reduction before searching. This could separate shared residue-field charts
   from nilpotent effects; the present theorem only classifies field products.
2. Bind one literal native producer/consumer to the stipulated `R`-left-vector
   and common-free-map interface, with its complete invoice before construction.
   Preparation, routing, control, precision, restoration and stock costs are
   **UNKNOWN**. This formal three-factor word supplies none of them.

`TASK.json` records the changed original card, bounded decision and structured
follow-ups. No native caller, supplier, outer multiplication theorem,
independent human acceptance or formal proof-kernel review is supplied. The
selected frontier is unchanged; maintainer edits are disabled.

## Credit

Nick Petalas's PR4276 supplies the exact criteria and open question, following
PR4265 and PR4243. Wentao Li's PR4099 supplies the right-vector alphabet and
column bound, building on PR2513. Their source documents and attribution are
retained unchanged. New work by ToikY with substantial OpenAI Codex assistance:
separate proof author, BFS implementation, projective oracle and static review
contexts. These are AI-assisted checks, not independent human review. New
material Apache-2.0; no merge or selected-frontier change.
