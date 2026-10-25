# Shortest unsigned depth-three chain connector

This scoped proof gives the exact shortest word for an unsigned dirty
connector chained through two dirty intermediates, over every finite
characteristic. The contribution was produced by Nick Petalas.

The complete calls are `z1 += B1 x`, `z2 += B2 z1` and `y += B3 z2`. The source
x is immutable, z1, z2 and y start with arbitrary dirty data, and the maps are
arbitrary. Coefficients lie in a nonzero unital ring of exact characteristic m.
For a nonzero residue c the word must restore z1 and z2 and add
`c B3 B2 B1 x` to y.

```text
shortest length = 3m   for every m >= 2 and c != 0 (mod m),
                         except (m, c) = (2, 1), (3, 2), (4, 3): 4m.
```

Each call is used a positive multiple of m times, so 3m is the per-call floor.
For m >= 5 an explicit word attains it, with one exception handled by a checked
witness at (m, c) = (6, 5):

```text
1^a 2 3^t 1^(m-2a) 2 1^a 2^(m-t-2) 3 2^t 3^(m-t-1),   ta ≡ c (mod m)
```

Here a = 1, t = c when c <= m - 2. For c = m - 1, a is a unit of Z/m in
[2, m/2] and t = -1/a. In characteristic 2, 3 and 4 the target c ≡ -1 cannot
be reached with m calls of each kind, and costs 4m. The binary case agrees with
the eight-call one-target count in [#1662](../ut4-central-tariff-relaxation/README.md).
That package uses a broader workspace model. Over characteristic zero, no
unsigned word reaches any nonzero c.

The per-call floor does **not** extend to depth four. Exact search over the
four-call chain gives 12, 18, 20 and 25 calls at m = 2, 3, 4 and 5. The floor
4m would give 8, 12, 16 and 20.

[PROOF.md](PROOF.md) has the complete argument. Lemma 1 reduces correctness to
interval subword counts mod m. Lemma 2 proves the floor, Lemma 3 is the
all-m construction, and Lemma 4 settles characteristics 2 to 4 by finite
enumeration. The depth-four table is a finite certificate only.

## Evidence and reproduction

From the repository root, with CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/depth3-chain-connector/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/depth3-chain-connector/verify.py --depth4-m5
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/depth3-chain-connector
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/depth3-chain-connector --check-source-history
```

Any CPython 3.12 can replace the local interpreter path. The default run
prints a generated JSON receipt with every package and input SHA-256, then
`PASS_DEPTH3_CHAIN_CONNECTOR depth4_moduli=3 constructed=32634`. It writes no
files and takes about 12 seconds locally. The `--depth4-m5` flag adds the
9,765,625-state depth-four search at m = 5. It is opt-in and not registered,
because it takes much longer and needs more memory.

The default checks:

- Exact breadth-first minima over all of UT4(Z/m), m = 2 to 8, for every c.
- An independent census of all 90, 1,680 and 34,650 balanced words at
  m = 2, 3, 4, and the three 4m exception witnesses.
- The explicit word for all 32,634 pairs (m, c) with 5 <= m <= 256, checked
  for letter counts and every interval condition.
- Literal replay with noncommuting 2x2 maps and dirty registers for every
  constructed word through m = 32, and for the exception witnesses.
- Exact depth-four minima at m = 2, 3, 4.
- Six controls: an omitted readout, an adjacent transposition, a wrong
  coefficient, a moved middle call, a reversed factor order and the
  construction's domain guard.

## Attribution and scope

Ross Richardson's [#943/#934 lineage](../universal-connector-boundary/README.md)
supplies the complete-call dirty-connector interface. The depth-two
(one-source) chain and its 2m floor come from
[#4231](https://github.com/CrocSwap/integer-mult-bounds/pull/4231) and
[#4236](https://github.com/CrocSwap/integer-mult-bounds/pull/4236). The UT4
central-target line, [#1662](../ut4-central-tariff-relaxation/README.md) and
its credited lineage, already prices the binary case in a broader model. The
new results here are the all-characteristic depth-three law, its construction,
the c ≡ -1 exceptions and the depth-four table. Subword counts and unitriangular
matrices are classical tools; no novelty is claimed for them. No pending
executable or archived source is imported. Exact pins are in
[SOURCES.json](SOURCES.json).

The `connector-alphabet-change` card is explicitly changed to this side
question. The chain gets one more complete call; the operations stay
unsigned, and no new connector operation is added. All calls carry their
complete implementation prices. Admission, dispatch, routing of the two
intermediates and word-dependent physical costs are additional. No supplier
caller, precision analysis, outer multiplication theorem, formal-kernel proof
or new kappa is supplied. Independent human and formal proof-kernel review are
unclaimed. Apache-2.0.

## Open next questions

The structured questions in [TASK.json](TASK.json) give first steps and blockers.

1. What is the exact depth-four minimum in every characteristic? The floor 4m
   fails for m <= 5. Whether it returns for large m is open, and plain search
   has m^10 states.
2. Does any concrete recursive caller route through two dirty intermediates
   with a favorable complete invoice for these 3m calls?
