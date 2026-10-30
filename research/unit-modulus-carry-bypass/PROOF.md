# The prefix and its uniform physical bounds

This is a scoped construction in the nineteen-tape, seven-symbol machine
of the retained PR5849 quarter-carry leaf. One literal branch, write, unit
move, goto or halt costs one transition. Space is the sum of visited tape
interval lengths, including all nineteen initial head positions and erased
storage. These are the predecessor's currencies.

## Declared interface and dependencies

Let P,Q,S be positive canonical LSB-first binary descriptors. Q is odd.
Tape0 contains the complete original-owner Boolean stream of volume V=PQS.
Tape5 starts on the first Q bit. The valid supplied packet encodes k+16 in
five bits, with -16<=k<=12. All private and spectator contracts are exactly
those of the pinned source. The requested permutation is a rotation by
plus or minus k*4^-1 modulo Q in the Q coordinate, with all other state
restored. At Q=1 this is the identity, since there is only one coordinate.

For odd Q>=3, cite the following nonunit conclusions from the section
"Physically supplied quarter code" of PR5849's retained PROOF.md:

```text
T_old <= (1111/3)V,
W_old <= 24V.
```

These are used as predecessor results, not re-proved or independently
replayed. In particular the old offset producer, payload permutation,
restoration, and its analytic count remain that contribution. The two
source tables, interpreters and proof statements are bound in SOURCES.json.

## A fixed seven-row table

The following rows are prepended. All source destinations are increased by
seven, and the fallback goto targets seven plus the source entry.

```text
0: move tape5 right
1: branch tape5: RIGHT -> 2, ZERO -> 4, ONE -> 4, other -> 6
2: move tape5 left
3: halt
4: move tape5 left
5: goto relocated source entry
6: reject
```

This construction receives a source table and alphabet constants only.
It receives no runtime Q, packet, extent, payload or head position.
Selection occurs by a physical read on tape5.

A canonical positive odd Q has first bit ONE. The next symbol is RIGHT
exactly when Q=1. In this case the executed rows are 0,1,2,3, costing
exactly four transitions. No tape is written. Tape5 moves one step right
and one step left, and every head therefore returns. The only visited
position beyond the nineteen initial positions is tape5's next position,
so W_new=20. Arbitrary payloads, descriptors and spectators are unchanged.
This proves the required endpoint for every P,S and valid packet at Q=1.

For odd Q>=3, the next symbol is ZERO or ONE. The executed prefix rows are
0,1,4,5. These cost exactly four transitions and enter the retained program
in its original complete configuration, after relocation. Induction on
the old program's transitions proves that relocation preserves each tape
operation, branch choice, halt and rejection. Thus

```text
T_new = T_old + 4          for Q>=3.
```

The prefix visits just the first two Q positions. The retained nonunit
descriptor producer already visits those positions: it checks tape5's first
ONE, moves right and reads the next bit before entering its general branch.
Thus the prefix adds no visited positions to a complete valid nonunit run,
and W_new=W_old there.

## Improved complete bounds

For Q>=3, V=PQS>=3, so the cited nonunit inequality gives

```text
T_new <= (1111/3)V + 4 <= (1115/3)V,
W_new <= 24V.
```

For Q=1, V>=1, and the exact new counts give

```text
T_new = 4 <= (1115/3)V,
W_new = 20 <= 24V.
```

Both directions therefore satisfy the displayed complete bounds for every
valid input. The transition coefficient decreases by exactly 289/3 from
the old tight uniform bound 468, and the sufficient visited-cell coefficient
decreases from 49 to 24. The new bounds need not be tight. Nonunit executions
pay four extra transitions; this is an improvement to the worst-case uniform
envelope over the whole interface, not a claim that each invocation is cheaper.

The result preserves the successful-input contract. It does not promise
to diagnose invalid unused packets or private state in the unit branch.
Source-to-caller legality and the remaining G20 obligations in the README
are separate from this proof.

## Implementation limits and verification choices

The assembler transforms the pinned 31,873-row tables and rejects more than
100,000 input rows. Its loops are finite table traversals with at most seven
branch destinations per row. It neither interprets runtime descriptors nor
introduces a new runtime loop. Each changed function is under sixty lines.
Internal invariants use explicit checks that remain active under optimized
Python. The suffix checker independently reverses relocation before comparing
every row, rather than comparing the wrapper to a second call to itself.

Managed Python allocation is a rule-3 deviation in the finite assembler and
verifier. Live allocations are bounded by the authenticated fixed table,
at most four payload bits for unit cases, 513 descriptor bits for prefix-only
cases, and 125 payload bits for complete compositions. Each simulated run
has at most 200,000 transitions. These verification limits do not restrict
the mathematical input domain. The retained interpreter owns any dynamic
simulation storage; no source runtime behavior is changed to satisfy them.

Direct compilation of two authenticated interpreter sources and the local
wrapper is a rule-8 deviation. It prevents stale bytecode from replacing
the declared bytes, has three fixed module targets, checks fresh names,
and removes each temporary module entry on every exit. Negative-control
callbacks are a rule-9 deviation limited to six immediate checks with no
retained state. Follow-on changes to these bounds or targets require
revisiting the controls. The finite table, fixtures and execution caps
bound allocations and all loops. Warning-strict normal and optimized
registered replays check this scope. No static analyzer is configured for
this isolated package; diagnostics on the two new files are run if available.

No predecessor verification suite, formal proof-kernel check or independent
human review is claimed.
