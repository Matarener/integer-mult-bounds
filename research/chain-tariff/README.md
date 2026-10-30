# Exact count vectors and prices for the unsigned depth-three chain

This scoped proof classifies every feasible call-count vector for the dirty
chain `z1 += B1 x`, `z2 += B2 z1`, `y += B3 z2` over every finite ring
characteristic m. The contribution was produced by Nick Petalas.

The maps and initial dirty data are arbitrary. A word must restore z1,z2 and
add `c B3 B2 B1 x` to y, with 1<=c<m. Let P be its set of minimal count vectors:

```text
(m,c) = (2,1):   P = {(2,4,2)}
(m,c) = (3,2):   P = {(6,3,3), (3,6,3), (3,3,6)}
(m,c) = (4,3):   P = {(8,4,4), (4,8,4), (4,4,8)}
every other case: P = {(m,m,m)}
```

A count vector is feasible exactly when its coordinates are multiples of m
and it dominates one member of P. This holds for words of any length. With
positive complete-call prices p1,p2,p3 and S=p1+p2+p3, the exact tariff is

```text
2S + 2p2                    at (2,1)
mS + m min(p1,p2,p3)         at (3,2) and (4,3)
mS                          otherwise.
```

[PR4249](https://github.com/CrocSwap/integer-mult-bounds/pull/4249) supplies the
credited balanced construction and unit-price exception law. Merged
ToikY's [PR1662](../ut4-central-tariff-relaxation/README.md) already proves the binary
weighted formula in a broader workspace model. The new result completes the
attainable count set, gives all three characteristic-three/four repairs and
their price dependence, and counts their literal optimum words exactly.
For the first, middle and last doubled profiles the numbers are respectively
`108,180,108` at (3,2) and `3520,4288,3520` at (4,3). Ties between cheapest
prices add the corresponding counts. The binary minimum has four words.

For example, at m=3,c=2 and prices (1,10,10), the first-doubled word costs
66, while the middle-doubled word costs 93. At m=2,c=1, doubling cheap outer
calls cannot replace the four mandatory middle calls, however long the word.
The binary restriction is credited predecessor work, not a new obstruction.

## Evidence and reproduction

[PROOF.md](PROOF.md) gives the complete argument and seven exceptional words.
The exact census step proves the small-characteristic balanced exclusions
and exceptional multiplicities. The all-characteristic count classification
also uses a written unbounded argument and identity padding.

From the repository root, using CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/chain-tariff/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -O -B research/chain-tariff/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/chain-tariff
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/chain-tariff --check-source-history
```

Any CPython 3.12 path can replace the local path. Expected marker:
`PASS_CHAIN_TARIFF`. The script writes no files and prints a generated receipt
bound to every package file and the live input SHA-256. Both registered
checks run the complete finite domain, with assertions enabled and disabled.
They compare a modular count DP against an independent integer position
census and a separate weighted full-group shortest-path oracle, test rational
prices, and execute every dirty input basis column
with noncommuting 2x2 maps, check identity padding and reject altered words
and invalid domains. The full check enumerates 2,795,820 literal words, tests 33,232 rational-price
cases, 384 independent weighted shortest-path cases, 4,500 dirty basis/mixed
cases and 270 identity paddings, and rejects 102 altered words or invalid
domains. These counts are enumerated, not estimated.

Local execution used CPython 3.12.15 on macOS 27.0.1 arm64. Each full direct
mode takes about four seconds locally, below its registered 180-second limit.
These are check durations, not performance comparisons. Package metadata and
source pins pass. The source-history publication check runs on the committed
package.

## Related open work

- PR4249 is the exact depth-three predecessor. Unit prices recover its
  exceptional 8,12,16 calls and its 3m balanced law, checked for m<=32. The
  count cone and unequal-price alternatives are the extension here.
- PR4236 and PR4189 study the depth-two one-source chain. Their minimum 2m
  counts agree with the shared per-letter floor; neither contains this
  three-operation tariff or its exceptional multiplicities.
- PR1930 uses a three-stage persistent prefix chain and retains updates to
  intermediate rows. Its lack of restoration is a different contract, and
  its one-call-per-map bill is not compared as the same quantity.
- PR4241 and PR4233 price a signed multi-source/output connector. Its six
  signed operators and target differ, so no identical tariff is compared.

## Attribution and scope

The complete-call interface comes from Ross Richardson's PR943/PR934 lineage
and [universal connector](../universal-connector-boundary/README.md).
Nick Petalas's PR4249, exact head
`03b8a19d7442edebb3565064631f6ca2408d731e`, is the immediate predecessor.
Its balanced construction is restated with credit and implemented locally;
no pending executable or foreign Git object is needed. PR1662's UT4
central-target theorem, its author and retained lineage own the earlier
binary tariff. [SOURCES.json](SOURCES.json) binds the main-tree provenance
and live interface input. Scattered-subword counting is classical.

The `connector-alphabet-change` card is explicitly changed to a pricing
side question in [TASK.json](TASK.json). The alphabet is unchanged and no
operation is declared free. Prices must cover the complete three calls.
Actual admission, instruction dispatch, coefficient preparation, routing,
precision, stock and supplier/outer transfer remain separate obligations.
There is no concrete supplier caller, selected-frontier change, new kappa,
formal-kernel proof or complete multiplication theorem. The selected cold
replay and formal builds were not run. Independent human and formal
proof-kernel review are unclaimed. Apache-2.0.

## Open next questions

The structured questions in TASK.json give relevance, first steps and blockers.

1. Find a closed form for balanced minimum-word multiplicities at arbitrary m.
   PR4236's depth-two residue formula does not include both pair constraints
   and the triple coefficient of this chain.
2. Pin an actual recursive caller with two dirty intermediates and compare
   these words using its full physical invoice. A call-price optimum alone
   does not establish favorable routing or supplier admission.
