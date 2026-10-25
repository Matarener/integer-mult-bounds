# Trace-zero calls do not lower the twelve-call floor

**Partial. No new exponent.**

A rank-one matrix `u v^T` is idempotent exactly when `v · u = 1`. Dropping
that condition leaves 21 nonzero matrices on three bits: seven images, and
three nonzero duals of trace zero for each. The square of each is zero.

The cross scalar of two calls is `v_j · u_i`, not the diagonal of either
call. The pair

```text
u = (1, 0, 0),  v = (0, 1, 0)
u = (0, 1, 0),  v = (1, 0, 0)
```

has both diagonals equal to zero and both cross scalars equal to one. A
trace-zero factor can therefore feed the corner.

The linear block still stacks each coefficient as `(u, 0)`, `(0, u)` or
`(u, u)`. For any three shadows, that stacked image has dimension at least
the dimension of their sum. The comparison does not read `v · u`. The target
corner still has a three-dimensional column space, and the reversed corner
still forces the dual span to have dimension at least 3. Each side therefore
needs at least six calls. The same twelve-call word, one commutator on each
register, attains the bound. The selected kappa is unchanged.

## What was executed

The checker counts the 21 matrices, evaluates the cross scalar, ranks every
triple of three-bit subspaces, and multiplies the twelve-call word. It does
not search words.

`scripts/research_baseline.py` needs
`research/community-frontier1094-audit/ASSEMBLY.json`, which this checkout
does not have. The orientation used here is the trace-zero question in PR
3788, head `595b9426cc2fac34d31a71b24b98ed080f54c99a`.

## Scope and evidence

Original card: `formal-interface-lemma`, priority revision 6, refined to this
floor. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the selected record. No selected frontier
file changes.

## Reproduce

From the repository root, CPython 3.12:

```sh
python3.12 -B research/nilpotent-call-floor/verify.py
python3.12 -B research/nilpotent-call-floor/test_verify.py
python3.12 -B scripts/research_package.py --package research/nilpotent-call-floor
```

## Open next questions

This floor includes the trace-zero calls. A physical embedding would be a
different contract.

## Credit

Wentao Li asked whether a trace-zero factor can feed the corner. The
twelve-call schedules and the rank-one model are credited there to that
note, Cinna Davis, eumemic and woklerx.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
