# The owned-zero screen is forward mass 8658/5

**Partial. No new exponent.**

The nine-stage recipe has four pairs, five forward calls and four reverse
calls. Its width is `m = 64` and its live width is `W = 28416`, so the
capacity is `64 * 28416 = 1818624`. The pinned idle rules, with 111 ports and
32 replicas, contribute

`{7: 21312, 14: 14208, 28: 14208, 42: 14208}`,

of mass `1342656`.

Each reverse call is charged only two rank-7 endpoint moves per port. That
allowance is `4 * 32 * 14 * 111 = 198912`. The room left for the five forward
copies is `277056`. Spread over `5 * 32 = 160` copies, the forward mass that
makes the zero-saving bill exactly one is

`277056 / 160 = 8658/5`.

Any larger forward mass exceeds one before saving is added. The selected kappa
is unchanged.

## What was executed

The checker reads the pinned recipe and solves this screen. It does not replay
the owned-scratch word.

`scripts/research_baseline.py` needs
`research/community-frontier1094-audit/ASSEMBLY.json`, which this checkout
does not have. The orientation used here is the owned-zero screen in
PR 3772, head `5b1d4c2ade90dfa0d8b837148cc5b9cc4be1cdab`.

## Scope and evidence

Original card: `bit-helper-contract`, priority revision 6, refined to this
screen. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the selected record, the odd-stage recipe,
the replica count and the live port count. No selected frontier file changes.

## Reproduce

From the repository root, CPython 3.12:

```sh
python3.12 -B research/owned-zero-mass-screen/verify.py
python3.12 -B research/owned-zero-mass-screen/test_verify.py
python3.12 -B scripts/research_package.py --package research/owned-zero-mass-screen
```

## Open next questions

This fraction is the screen. A different reverse allowance would leave it.

## Credit

DreamingOfClouds wrote the odd-stage recipe. Gonzalo Mier recorded this
forward-mass screen. The recipe file also names Zhihao Chen, eumemic and
chafreaky.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
