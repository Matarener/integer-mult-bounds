# A prefix-walk return has even length

**Partial. No new exponent.**

Each step XORs one basis vector, so it changes the Hamming weight by one and
flips its parity. After an odd number of steps the weight parity differs from
the parity at the start of the block, and the state cannot have returned. Every
contiguous zero-XOR block therefore has even length. The checker confirms the
flip for every state and every label at width 7.

A repeated label is the length-2 case. The two steps cancel, so the endpoint
is unchanged. The prefix set gains at most the midpoint, and the set of
pairwise XORs grows. Coverage, once present, remains. The revisit count is
`length - |P|`. Two added steps and a new midpoint raise it by 1. Two added
steps and a midpoint that is already present raise it by 2. The words
`(0, 0, 1, 1)` and `(0, 0, 0, 0)` realize those two deltas. The word
`(0, 1, 0, 1)` returns with revisit count 0.

## What was executed

The checker uses this parity. It does not census words and it does not claim
`f(7)`.

`scripts/research_baseline.py` needs
`research/community-frontier1094-audit/ASSEMBLY.json`, which this checkout
does not have. The orientation used here is the padding lemma in PR 3708, head
`44334c60341e4354378666838c7921e6cabd6c03`.

## Scope and evidence

Original card: `census-pruning-audit`, priority revision 6, refined to this
return. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the selected record. No selected frontier
file changes.

## Reproduce

From the repository root, CPython 3.12:

```sh
python3.12 -B research/zero-xor-return/verify.py
python3.12 -B research/zero-xor-return/test_verify.py
python3.12 -B scripts/research_package.py --package research/zero-xor-return
```

## Open next questions

This return is the constraint. A word census would leave it.

## Credit

petalas recorded the canceling-pair padding in the length-22 domain.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
