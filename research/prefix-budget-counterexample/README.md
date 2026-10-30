# The word `01021323` is universal and fails a balanced collision budget

**Partial. No new exponent.**

In dimension 4 the word `01021323` flips one coordinate at a time and returns
to zero. Its eight nonclosing prefixes are

```text
{0, 1, 2, 3, 4, 6, 8, 12}
```

and their pairwise XOR masks are all 16 vectors. Each of the four labels
occurs twice. The Hamming-weight classes have sizes `(4, 4)` and collision
excess 0. The least-coordinate classes have sizes `(6, 2)` and collision
excess 8.

A budget that inserts the balanced sizes `(4, 4)` allows only

```text
C(4,2) + C(4,2) - 7 = 5
```

collisions, so it rejects this universal word. The budget for the actual
class sizes allows

```text
C(6,2) + C(2,2) - 7 = 9
```

and 8 fits. The same word meets the actual-size budget of every one of the
15 nonzero linear functionals. The five stated length-20 rows are the same
binomial rule at dimension 7:

```text
(10,10) -> 27, 36
(10,9)  -> 18, 26
(10,8)  -> 10, 16
(9,9)   -> 9, 17
(10,7)  -> 3, 6
```

The selected kappa is unchanged. This check does not decide `f(7)`.

## What was executed

The checker rebuilds the prefix walk, the two class budgets, the pair
identity on the bit-0 classes, and the five binomial rows. It does not run a
seven-label census.

`scripts/research_baseline.py` needs
`research/community-frontier1094-audit/ASSEMBLY.json`, which this checkout
does not have. The orientation used here is the dimension-4 counterexample in
PR 2973, head `20ecf2891d80b5acf18d980b2164fb44ea7faa90`.

## Scope and evidence

Original card: `census-pruning-audit`, priority revision 6, refined to this
word. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the selected record. No selected frontier
file changes.

## Reproduce

From the repository root, CPython 3.12:

```sh
python3.12 -B research/prefix-budget-counterexample/verify.py
python3.12 -B research/prefix-budget-counterexample/test_verify.py
python3.12 -B scripts/research_package.py --package research/prefix-budget-counterexample
```

## Open next questions

The eight prefix states and both budgets are finite. A seven-label census
would leave this package.

## Credit

Nicholas Stone recorded this word in the collision-budget note of PR 2973.
This package reconstructs the prefixes and the two budgets.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
