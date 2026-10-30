# Full ternary demand on the unsigned F3 five-source connector

For five immutable sources over F3, all **242 nonzero ternary coefficient
rows** and one arbitrarily dirty restored connector, the exact complete-call
optimum is **744**. The operator-count floor is 741. No legal word attains it,
and two different 744-call words exist.

This is a **scoped proof with an exhaustive finite census**. It answers the
second open question of [#4225](https://github.com/CrocSwap/integer-mult-bounds/pull/4225)
(head `397025101d23195a5193c7912e6cd384eccdbf1c`), which proved the 108-call
optimum for the 31 binary-mask rows. The same count floor is attained for
one to four sources. Five is the first source count where it fails. It also
fails for every count of seven or more. Six sources remain undecided. There is
no new kappa, supplier consumer or selected-frontier change.

## Exact boundary

The interface is unchanged from #4225. Read-only sources x_0..x_4, one
borrowed dirty connector z and output rows y_v, one for each nonzero
v in F3^5. Implement, for arbitrary F3-linear maps of compatible dimension,

```text
y_v += sum_j v_j A_v B_j x_j    for all 242 nonzero v;   x_j and z unchanged.
```

The only operations are unsigned complete calls `B_j: z += B_j x_j` and
`A_v: y_v += A_v z`. Signed calls, extra connectors, source mutation, frame
changes and free copies are excluded. The maps may be singular and need not
commute. Outputs are unobserved until completion.

## Lower bound

The count argument is #4225's. Specialize to scalar identity maps. If B_j
occurs b_j times, restoration of z forces `3 | b_j`. If A_v occurs a_v times,
removing the connector dirt from y_v forces `3 | a_v`. Each a_v is nonzero
because the row is nonzero. Each b_j is nonzero because the singleton row
e_j depends on x_j. So every count is at least three and the total is at
least `15 + 3*242 = 741`.

Every count is a multiple of three, so a word below 744 calls has exactly 741.
Then every b_j and every a_v is exactly 3. The source path has 15 events
with each source three times. Let q_t in F3^5 be its source-count vector
modulo three after t events. #4225's triple-prefix identity says that three
readouts of A_v at boundaries a, b, c are correct iff
`q_a + q_b + q_c = v`. Boundaries may repeat. Since q_15 = q_0 = 0, a
741-call word exists iff some such path has
`{q_a + q_b + q_c} ⊇ F3^5 \ {0}` over the boundary set {q_0..q_14}.

The verifier enumerates every such path up to source relabeling: letters
first appear in the order 0, 1, 2, 3, 4. Every source occurs, so each
relabeling class has exactly one such member, and there are
`15!/(3!^5 5!) = 1,401,400` of them. Relabeling permutes coordinates of
F3^5 and fixes the full nonzero demand, so the restriction loses nothing.
The census finds a maximum coverage of **241** of the 242 rows, reached by
30 canonical paths. Each of those paths misses one row. Up to relabeling, a
missed row has either one 1 and one 2, or two 1s and two 2s. No path reaches
242. Hence every legal word has at least 744 calls.

As a check on the canonical reduction, the verifier compares it against full
labeled enumeration at two and three sources: same maximum, same feasibility,
and the class counts multiply out exactly.

## Two 744-call constructions

**Doubled source.** The restored 18-event path

```text
B1 B3 B2 B0 B0 B4 B3 B1 B1 B0 B4 B0 B0 B2 B3 B4 B2 B0
```

uses B_0 six times and every other source three times. Its boundary vectors
cover all 242 rows with three readouts each:
`18 + 3*242 = 744`. Relabeling gives such a path for each doubled source; the
verifier checks all five.

**Six-readout gap.** The 15-event path

```text
B0 B1 B0 B2 B1 B0 B3 B2 B1 B4 B3 B2 B4 B3 B4
```

covers 241 rows with three readouts. The missing row (1,2,0,1,2) uses six
readouts, at boundaries 0, 0, 1, 6, 9 and 14:
`15 + 3*241 + 6 = 744`.

In general, if a 15-event path misses only v, take any nonzero u it covers.
Then v - u is also covered, since v - u ≠ v. Six readouts realize u + (v - u).
For each word the verifier takes the lexicographically first readout
multiset per row and checks the literal 744-call word in two ways. A generic
free-coefficient ledger tracks z0 and each B_j x_j separately. A dense
execution uses random F3 matrices at L = 2 and 3, including dirty z and
output rows.

## Fixed prices with a common readout price

Let the source prices c_j be arbitrary and positive, and let every readout
cost α > 0. The exact optimum is

```text
3 sum_j c_j + 726 α + 3 min(min_j c_j, α).
```

The lower bound: a word that is not at the floor has some b_j ≥ 6 or some
a_v ≥ 6. Either costs at least the displayed extra. The two constructions
attain each branch. With row-dependent readout prices the exact envelope needs
every inclusion-minimal missing set of a 15-event path. Only the lone gaps
are recorded here, so that general envelope is **not** claimed. Fixtures:
unit prices give 744. Sources (1,4,10,16,28) with α=1 give 906. Sources
(2..6) with α=5 give 3696, by the doubled-source branch. Sources (7..11) with
α=1 give 864, by the gap branch.

## Other source counts

For n sources the floor is `3n + 3(3^n - 1)`, and attaining it needs a 3n-event
path whose at most 3n boundary points have every nonzero triple sum.

- **n = 1..4: attained.** The canonical census finds full-coverage paths:
  1 of 1, 10 of 10, 279 of 280 and 6,245 of 15,400 canonical paths.
- **n = 5: fails by one call triple** (this package).
- **n ≥ 7: fails by counting.** At most `C(3n,3) + 3n(3n-1) + 1` distinct
  triple sums exist (distinct triples, a doubled point, and 3q = 0), which is
  below 3^n for n ≥ 7. The verifier checks n = 7..63. Beyond that the cap is at
  most 27n³ < 3^n. So the optimum there is at least the floor plus three. Its
  exact value is not determined here.
- **n = 6: open.** The count allows 1,123 ≥ 729 values. The census has
  190,590,400 canonical paths, beyond this package's registered replay
  budget.

## Verification

From the repository root:

```sh
~/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/f3-ternary-demand-connector/verify.py
~/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/f3-ternary-demand-connector
~/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/f3-ternary-demand-connector --check-source-history
```

Expected marker: `PASS_F3_TERNARY_DEMAND_CONNECTOR calls=744 rows=242`. Each
registered command (normal and `-O`, warnings as errors) takes about 37 s
locally, almost all in the 1.4M-path census. The verifier uses only the
standard library, writes no files and prints a SHA256 receipt over the package
files. Checks raise explicit exceptions, so `-O` disables none.

Five rejection controls must fail: a dropped source call, a dropped readout,
a readout moved across a source call (also rejected by one dense seed), and
a changed source port. A positive control confirms that #4225's binary
15-event path covers only 203 ternary rows.

The census recursion has depth at most 15, the canonical class bound. Loops
are bounded by 243 field elements, at most 18 path events and the fixed
counts above. Python allocation is a Power of Ten rule 3 deviation, limited
to this bounded offline check. Reads are capped at 128 KiB.

## Limitations

This is an abstract complete-call interface over F3. Fixed prices must include
each primitive's complete implementation. Input admission, coefficient
preparation, dispatch of the 744-record word and physical charges are
additional and unknown. No consumer for full ternary demand is identified.
The census is a finite computation backed by the written reduction above, not
a proof-kernel certificate. This is not a complete multiplication theorem.

## Open next questions

The structured versions are in [TASK.json](TASK.json).

1. **Unequal readout prices.** Record every canonical path's missing set,
   close the sets under relabeling and keep the inclusion-minimal family. That
   gives the exact envelope for arbitrary positive prices.
2. **Six sources.** Decide whether the 2202-call floor is attained. A compiled
   census of 190,590,400 canonical paths, or one reduced by rotation and
   reversal (both preserve coverage), is the first step.
3. **Consumer.** Identify a caller that needs coefficient-2 rows before
   pricing any recursive use.

## Credit

This contribution was produced by Nick Petalas. It builds on the interface,
mod-three count floor and triple-prefix identity of #4225. It also builds on
Riquelme Soares's #4189 unsigned-F3 one-source result, Ross Richardson's
#943/#934 prefix-connector lineage and ywz65's five-source contract map. No
predecessor credit line or frozen package is changed. Independent human and
formal proof-kernel review are unclaimed. Apache-2.0.
