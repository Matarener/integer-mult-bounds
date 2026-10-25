# Full ternary demand on the unsigned F3 six-source connector

For six immutable sources over F3, all **728 nonzero ternary coefficient
rows** and one arbitrarily dirty restored connector, the exact complete-call
optimum is **2208**. The operator-count floor is 2202. Every legal word pays at
least two extra call triples, and one explicit 2208-call word exists.

This is a **scoped proof with an explicit finite witness**. It answers the
six-source open question of
[#4238](https://github.com/CrocSwap/integer-mult-bounds/pull/4238)
(head `191a905d7adba6695b079f744140a73e832787a8`), which proved the 744-call
five-source optimum and left n = 6 undecided. The lower bound is
census-free apart from #4238's five-source value, which is cited and not
re-run here. It also gives lower bounds for every larger n. There is no new
kappa, supplier consumer or selected-frontier change.

## Exact boundary

The interface is #4225's and #4238's, unchanged. Read-only sources
x_0..x_{n-1}, one borrowed dirty connector z and output rows y_v, one for each
nonzero v in F3^n. For arbitrary F3-linear maps of compatible dimension,
implement

```text
y_v += sum_j v_j A_v B_j x_j    for all nonzero v;   x_j and z unchanged.
```

The only operations are unsigned complete calls `B_j: z += B_j x_j` and
`A_v: y_v += A_v z`. Signed calls, extra connectors, source mutation, frame
changes and free copies are excluded. Maps may be singular and need not
commute.

## Readout criterion and extra triples

Let source j occur b_j times and readout A_v occur a_v times. Let q_t in F3^n
count the source calls before boundary t, modulo three. Linearity gives
`y_v = y_v0 + a_v A_v z0 + sum_j (sum over readouts of q_t)_j A_v B_j x_j`.
So a word is correct iff every b_j and a_v is a multiple of three and, for each
row, the readout boundaries sum to v. This is #4225's count argument and
triple-prefix identity, generalized to any number of readouts. Each count is
at least three, so the floor is `F(n) = 3n + 3(3^n - 1)` and every word costs
`F(n) + 3E` for an integer E >= 0, its number of **extra triples**. Write e(n)
for the least E over legal words.

## Deletion lemma (averaging form)

Take a legal n-source word W and a source j. Delete every B_j call and every
A_v with v_j != 0. Each remaining boundary vector loses coordinate j, so every
surviving row's readouts still sum to that row, and all counts stay multiples
of three. The result W_j is a legal (n-1)-source word for the full nonzero
demand on the other coordinates.

Its extra triples are the source extras of the other sources plus the readout
extras of rows with v_j = 0. Summing over j, each source extra survives n - 1
deletions. A readout extra of row v survives once per zero coordinate of v,
which is at most n - 1 because v is nonzero. Hence
`sum_j E(W_j) <= (n - 1) E(W)`. Each E(W_j) is at least e(n - 1), so

```text
e(n) >= ceil(n e(n - 1) / (n - 1)).
```

#4232 proves the attainment-only form of this deletion for binary masks. The
averaging over j is what turns one forced triple into two here.

## Six sources

**Lower bound.** #4238's canonical census shows e(5) = 1. The recurrence gives
e(6) >= ceil(6/5) = 2, so every legal word has at least 2202 + 6 = 2208 calls.
Concretely: a word with one extra triple would either have all b_j = 3 and one
row read six times, or one source called six times and every row covered by
three readouts. Deleting a source in the support of the doubly read row, or
the doubled source, would give a five-source word at the 741-call floor.

**Construction.** The restored 24-event path

```text
B5 B4 B0 B1 B0 B3 B2 B4 B3 B1 B0 B1 B4 B5 B0 B1 B0 B2 B5 B3 B2 B1 B0 B1
```

uses B_0 and B_1 six times and every other source three times. Its 24
boundary vectors have every nonzero row of F3^6 as a sum of three of them,
with repetition. Three readouts per row give `24 + 3*728 = 2208` calls. The
verifier builds the literal word from the lexicographically first readout
triple of each row. It checks the word with a generic coefficient ledger,
valid for arbitrary noncommuting maps. It also runs dense random F3 execution
at dimensions 2 and 3 with dirty connector and output rows.

The six source deletions of this word are legal five-source words with
extras (1, 1, 2, 2, 2, 2). That agrees with the averaging identity: their sum,
10, is at most 5 times 2.

The witness came from a simulated-annealing search over 24-event paths. In
the same bounded search, 18-event paths reached at most 597 of 728 rows and
21-event paths at most 682. Those maxima are search observations, not proofs.
The lower bound does not use them.

## Larger source counts

Let `c(n)` be the counting bound. A path of length L = 3n + 3s has at most
`C(L + 2, 3) - L` distinct nonzero triple sums, and each uncovered row costs
an extra triple, so E >= s + max(0, 3^n - 1 - C(L + 2, 3) + L). Minimizing over
s gives c(n). Feeding the larger of the two bounds into the recurrence, the
verifier prints:

| n | recurrence | counting | lower bound on e(n) | lower bound on calls |
|---:|---:|---:|---:|---:|
| 5 | 1 (cited) | 0 | 1 | 744 |
| 6 | 2 | 0 | 2 | 2208 (attained) |
| 7 | 3 | 1 | 3 | 6588 |
| 8 | 4 | 4 | 4 | 19716 |
| 9 | 5 | 8 | 8 | 59097 |
| 10 | 9 | 14 | 14 | 177216 |
| 11 | 16 | 23 | 23 | 531540 |
| 12 | 26 | 37 | 37 | 1594467 |

The recurrence improves #4238's floor-plus-three bound at n = 6, 7 and 8.
Counting dominates from n = 9. Only n = 6 is exact here.

## Verification

From the repository root:

```sh
~/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/f3-ternary-six-source/verify.py
~/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/f3-ternary-six-source
~/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/f3-ternary-six-source --check-source-history
```

Expected marker: `PASS_F3_TERNARY_SIX_SOURCE calls=2208 floor=2202 rows=728`.
Each registered command takes about 5 s. The verifier uses only the standard
library and writes no files. Five rejection controls drop a readout, use a
source twice, misroute a readout, swap two path events, and reproduce #4238's
241-row gap path.

## Limitations

- This is the abstract unsigned complete-call interface over F3 only.
- The six-source lower bound depends on #4238's five-source census
  (e(5) = 1). That census is cited, not re-run. Its independent verification
  is a separate open claim.
- Exact values for n >= 7 are not determined. Only lower bounds are claimed.
- Prices are unit prices. No row- or source-dependent tariff is claimed.
- Admission, coefficient preparation, dispatch of the 2208-record word and
  physical charges are additional and unknown. No consumer for ternary demand
  is identified.
- No proof-kernel certificate exists. This is not a complete multiplication
  theorem.

## Open next questions

The structured versions are in [TASK.json](TASK.json).

1. **Seven sources.** Is the 6588-call lower bound attained? That needs a
   30-event path with three doubled sources covering all 2186 rows, or an
   equivalent mix. A bounded annealing run reached 1952.
2. **Eight sources.** The recurrence and counting bounds agree at four extra
   triples. One 36-event covering path would settle n = 8 exactly.
3. **Consumer.** Identify a caller that needs coefficient-2 rows before
   pricing any recursive use.

## Credit

This contribution was produced by Nick Petalas. It builds on #4238's
interface, five-source census and open question; on #4225's mod-three count
floor and triple-prefix identity; on #4232's binary-mask deletion lemma; on
Riquelme Soares's #4189 unsigned-F3 one-source result; on Ross Richardson's
#943/#934 prefix-connector lineage; and on ywz65's five-source contract map.
No predecessor credit line or frozen package is changed. Independent human and
formal proof-kernel review are unclaimed. Apache-2.0.
