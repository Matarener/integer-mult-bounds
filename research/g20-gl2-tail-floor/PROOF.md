# A finite lower-bound certificate for three G20 boundary components

Use the exact PR5840 controller at
`6a043d0fc0199ee5b24c61f883f1943eaf6424be`, not a moving branch. Both boundary
programs contain isolated direct summands on banks
`(16,17,28,29)`, `(18,19,26,27)` and `(20,21,24,25)`. In each ordered summand
the complete endpoint is

```
R = [ 0 I2 ]
    [ I2 0 ].
```

Every source instruction touching a summand stays inside it. Each source
word consists of two bank exchanges there, charged as six XORs. All four
entry values are independent and arbitrary; no zero scratch, copy, erasure,
frame operation, native call or free permutation is available in this model.
The 12 directed operations `x_d <- x_d XOR x_s`, d != s, each cost one.
They may be interleaved arbitrarily. SWAP is exactly three such operations.

The source's diagonal target entries agree within each adjacent pair. For
any `A,B in GL2(F2)`, let `S=diag(A,B)`. If the inherited physical-core
identity is `L P R = D`, then

```
(S^-1 L) P (R S) = S^-1 D S = D.
```

Thus general binary pair bases give exactly the local right endpoints
`R S = [[0,B],[A,0]]`. There are six binary invertible two-by-two matrices:
choose two distinct nonzero row vectors from `(1,0),(0,1),(1,1)`.
All 36 independent choices are covered. The left endpoint is its inverse.
Reversing an XOR word gives its inverse at the same cost, so the exact minimum
is the same on both sides. The test does not silently charge the basis as
free work: it synthesizes and prices the complete new endpoint `R S`.

## Why the certificate proves the stated finite minimum

The certificate lists one integer potential `d(M)` for each of the 20,160
invertible binary four-by-four matrices. The independent cardinality is
`15*14*12*8`. A row-encoding checker enumerates all 65,536 binary matrices and
selects exactly the full-rank ones. It verifies:

1. The identity has potential zero and every potential is nonnegative.
2. For every matrix and all 12 paid generators, both endpoints are present
   and the potential changes by at most one (241,920 directed edges).
3. Every nonidentity matrix has a neighbor with potential one less.
4. Every candidate has a literal attaining word with exactly its potential
   number of paid XORs and the exact labeled endpoint.

Along any word starting at identity, condition 2 bounds potential by paid
length. Conditions 3 and 4 give attaining paths. This certifies exact distances,
including arbitrary-length competing words in this finite alphabet; it is
stronger than a failed search to some depth. The complete candidate histogram is

| Minimum XORs | Number of pair-basis choices |
| --- | ---: |
| 6 | 2 |
| 7 | 8 |
| 8 | 24 |
| 9 | 2 |

The two six-XOR choices use `A=B=I2` or `A=B=SWAP2`. Therefore a GL2 basis
change cannot reduce any of these three isolated exchanges below six.
When gates remain component-local, costs add across direct summands:
the tail needs exactly 18 XORs per side, or `18*2*111=3996` XORs across
both boundaries and all 111 ports. This is an existing cost floor, not a saving.

`check.py` imports no producer or predecessor executable. It constructs complete
16-input truth tables, enumerates all invertible maps separately by independent
column images, performs its own BFS, and matches every certificate potential.
It also interprets all 36 attaining words and their inverses on all inputs,
and both actual source boundary words on all 16 inputs in each component.
These are two implementations by the same AI-assisted contributor, not an
independent human review or a proof-kernel formalization.

## Scope of the implication

This result does not prove the entire G20 boundary needs 38 XORs. Twenty
XORs of each current side lie outside these three summands. Cross-component
gates, the remaining 18-register component, extra clean or dirty workspace,
different operation tariffs, nonbinary bases, changed physical cores and native
frame mechanisms are not covered. It also does not price a changed full caller.

The source's physical-core diagonalization and arbitrary-input native contract
are inherited, not freshly replayed. The local scalar lower bound does not
depend on those contracts; applying its conclusion to the proposed supplier
uses the exact source decomposition and that inherited interpretation.
All five selected framework assumptions remain. No new ordinary saving,
admitted BIT saving, multiplication kappa or full multiplier is claimed.

Ali Romman's PR5840 supplies the equal-target-pair mechanism and exact controller.
PR5834, PR5807/5828, PR5708/5671, ai-nanachi PR5512, Dugongue and the retained
native/controller/compiler line supply its predecessors. PR5793 is adjacent
general-purpose bounded XOR synthesis, including a six-XOR four-role reversal;
that result and its algorithm are not claimed as new here. This contribution
binds the actual G20 summands and covers all 36 pair bases with fresh evidence.
Historical formal coordinate-SWAP bounds (including PR2415) use a different
paid alphabet and do not establish the new basis-variant table.

Prepared for Charan / theon199 with substantial OpenAI Codex assistance.
Apache-2.0; retained source notice is in `inputs/PR5840-NOTICE`.
