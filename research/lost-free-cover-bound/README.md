# One hundred twelve frames give the lost-free size 56

**Partial. No new exponent.**

The selected phase file has 112 ports in `F2^9`, each of norm one, and together
they span the whole space. The retained cover has 112 frames. Each frame is
eight ports with the 8 by 8 identity Gram matrix. Its weights are positive
rationals, every port receives total weight 1, and the weights sum to 14. Four
times that total is 56, so a lost-free set of ports has size at most 56.

The retained 32-plane witness meets the lost-free pair condition: each assigned
partner is orthonormal to its port, and orthogonal ports have orthogonal
partners.

With the fixed block cost 72, a set of size `s` costs `72 + 2 * (112 - s)`.
Size 32 costs 232. Sizes 33 through 36 cost 230, 228, 226, and 224. Size 37
costs 222. Size 56 costs 184. That cost drops below `1792/9` at size 49. It
meets the recorded rank-2 ceiling 164 at size 66 and the rank-8 ceiling 160 at
size 68. Meeting those ceilings already at size 56 would need block costs 52
and 48. The selected kappa is unchanged.

## What was executed

The checker reads the selected phase member and prices the retained frames. It
does not census frames.

`scripts/research_baseline.py` needs
`research/community-frontier1094-audit/ASSEMBLY.json`, which this checkout
does not have. The orientation used here is the compact cover in PR 3674,
head `efe1d72e4dcd14c2c48693b8f3a8c66f23d539b0`.

## Scope and evidence

Original card: `uniform-transfer-audit`, priority revision 6, refined to this
cover. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the selected record, the phase archive, and
the copy-budget receipt. No selected frontier file changes.

## Reproduce

From the repository root, CPython 3.12:

```sh
python3.12 -B research/lost-free-cover-bound/verify.py
python3.12 -B research/lost-free-cover-bound/test_verify.py
python3.12 -B scripts/research_package.py --package research/lost-free-cover-bound
```

## Open next questions

This cover is the size bound. Another block invoice would leave it.

## Credit

ToikY certified this cover.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
