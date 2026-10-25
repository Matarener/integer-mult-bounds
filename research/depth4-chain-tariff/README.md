# Count vectors and prices for the depth-four dirty chain, m = 2..5

This package classifies every feasible call-count vector of the unsigned
depth-four dirty chain connector in characteristics m = 2, 3, 4, 5, for every
nonzero target residue and for words of any length. It is a scoped proof whose
completeness step is a finite reduction checked by computer. The contribution
was produced by Nick Petalas.

The calls are `z_l += B_l z_{l-1}` for l = 1..4. The source x = z_0 is
immutable; z_1, z_2, z_3 and y = z_4 start dirty, and the maps are arbitrary.
A correct word restores z_1..z_3 and adds `c B4 B3 B2 B1 x` to y, 1 <= c < m.
Write n_l for the number of calls l. Let P(m) be the set of minimal correct
count vectors:

```text
m = 2:  P = {(2,4,4,2)}
m = 3:  P = {(3,3,9,3), (3,6,6,3), (3,9,3,3)}
m = 4:  P = {(4,4,8,4), (4,8,4,4)}
m = 5:  P = {(10,5,5,5), (5,10,5,5), (5,5,10,5), (5,5,5,10)}
```

**Theorem.** For m in {2,3,4,5} and every c != 0 mod m, a count vector is
attained by a correct word if and only if every n_l is a multiple of m and n
dominates some member of P(m) coordinate by coordinate. P(m) does not depend
on c.

With positive complete-call prices p_1..p_4 and S = p_1 + p_2 + p_3 + p_4,
the exact cheapest bill is therefore

```text
m = 2:  2S + 2(p2 + p3)
m = 3:  3S + 6 min(p2, p3)
m = 4:  4S + 4 min(p2, p3)
m = 5:  5S + 5 min(p1, p2, p3, p4)
```

At unit prices this recovers the minimum lengths 12, 18, 20, 25 of PR4249.
The new information is where the premium sits. In characteristics two, three
and four it is paid only on the two middle operations: no minimal word doubles
the first or last call, however cheap those calls are. At m = 3 the profile
(3,6,6,3) is minimal but is optimal only when p2 = p3. In characteristic five
any one operation can be doubled.

For 6 <= m <= 32, PR4263's balanced witnesses give P(m) = {(m,m,m,m)} and the
bill mS by the divisibility argument below. That is a corollary of cited
pending work, not rechecked here. For m >= 33 the classification is open.

## Proof

**Interval counts.** Let N_ij (1 <= i <= j <= 4) count scattered subwords
`i (i+1) ... j` of the word. As in PR4249 and PR4257, appending letter j adds
N_{i,j-1} to N_ij for i < j and increments N_jj, so

```text
z_j(final) = z_j(initial) + sum_{i<=j} N_ij B_j ... B_i z_{i-1}(initial).
```

A word is correct exactly when all ten counts vanish mod m except N_14 = c.
Sufficiency is this identity. For necessity take every module to be the ring,
every map the identity, and switch on one initial register at a time. Then
each n_l = N_ll is a multiple of m, and positive, since n_l = 0 forces
N_14 = 0. Appending m copies of any letter acts as the identity, so any
correct count vector stays correct after adding a multiple of m to one
coordinate. The witnesses in [witnesses.json](witnesses.json) attain every
member of P(m) for every c, and padding gives sufficiency.

**Reduction to the middle letters.** Fix the order of the 2s and 3s. Let
A[i][j] = 1 when the i-th 2 precedes the j-th 3, let u_i count the 1s before
the i-th 2 and let r_j count the 4s after the j-th 3. A 1 only matters through
which 2s follow it, and a 4 only through which 3s precede it. So

```text
N12 = sum u,   N13 = u . A1,   N23 = 1'A1,   N34 = sum r,
N24 = r . A'1,   N14 = u' A r,   N11 = n1,  N22 = n2,  N33 = n3,  N44 = n4.
```

For exact counts, u is nondecreasing in [0, n1] and r is nonincreasing in
[0, n4]. If n1 and n4 are left free, u and r range over all residue vectors:
every residue vector lifts to a nondecreasing integer sequence, and 1s after
the last 2 (or 4s before the first 3) change only N11 (or N44), which is then
padded to a multiple of m. The verifier implements both versions as engine A.

**Completeness.** It remains to show that no correct vector misses P(m).

- m = 5. A vector of positive multiples of 5 that dominates no single doubling
  is (5,5,5,5). Engine A with exact counts finds N14 = 0 for every correct
  remainder of such a word, for every c.
- m = 4. A vector that dominates neither (4,4,8,4) nor (4,8,4,4) has
  n2 = n3 = 4, with n1 and n4 arbitrary. Over all 70 orders of four 2s and
  four 3s and all residue vectors u, r, the relaxed engine never reaches a
  nonzero N14 once the other nine conditions hold.
- m = 3. A vector that dominates no member of P(3) has (n2, n3) in
  {(3,3), (3,6), (6,3)}, with n1 and n4 arbitrary. The relaxed engine again
  reaches only N14 = 0.
- m = 2. A vector that dominates no member has n2 = 2 or n3 = 2. Suppose
  n2 = 2. Then N12 = u1 + u2 = 0 mod 2, so u1 = u2. Every subword 1234 is a 1,
  then a 2, then a subword 34 after that 2. If t_i counts the subwords 34 after
  the i-th 2, then N14 = u1 t1 + u2 t2 = u1 (t1 + t2) = u1 N24 = 0, which is
  not c = 1. Reversing a word and relabelling l -> 5 - l preserves correctness
  and swaps n2 with n3, which covers n3 = 2.

The relaxations leave n1 and n4 unbounded, so this covers words of any
length, not a bounded search. Positive controls show the relaxed engine does
reach every residue on the adjacent feasible middle pairs: (3,9), (6,6), (9,3)
at m = 3, and (4,8), (8,4) at m = 4. At m = 5 it reaches every residue at
n2 = n3 = 5, which is why m = 5 needs the exact outer counts. QED.

Prices: every optimum has its count vector in P(m), because a strictly larger
feasible vector costs strictly more at positive prices. Minimizing over P(m)
gives the table above, using p2 + p3 >= 2 min(p2, p3) at m = 3.

## Verification

From the repository root:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/depth4-chain-tariff/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -O -B research/depth4-chain-tariff/verify.py
```

Both print `PASS_DEPTH4_CHAIN_TARIFF witnesses=29 replays=87
box_comparisons=125 cross_checks=116` and a receipt hash over every package
file and source input. The verifier uses only the standard library and takes
about 70 seconds. It checks:

1. all 29 witness words, one per (m, c, Pareto vector): exact counts, the ten
   interval conditions, an independent UT5(Z/m) matrix product, and three
   literal replays each with dirty registers and random noncommuting 2x2 maps;
2. the relaxed engine on each missed middle pair for m = 3, 4, and its
   positive controls;
3. the exact engine at (5,5,5,5) and the m = 2 lemma on n2 = 2 with the other
   counts in {2,4,6}, plus the mirror symmetry on the binary witness;
4. engine B, a direct DP over the six non-diagonal interval residues, on the
   boxes [2,6]^4 at m = 2, [3,6]^4 at m = 3 and [4,8]x{4}x{4}x[4,8] at m = 4.
   For all 125 (vector, residue) cases it agrees with the claimed cone, and in
   the 116 cases with every count at most 6 it also agrees with engine A;
5. controls: an adjacent swap, a wrong residue, a wrong-residue replay, the
   4m floor at m = 4, and an exact-engine positive case.

`witnesses.json` was produced by a seeded local annealing search that is not
part of the package; the verifier checks the words themselves.

## Related work

- PR4249 (Nick Petalas) supplies the chain model and the depth-four minimum
  lengths 12, 18, 20, 25. The unit-price case of the tariff table agrees with
  all four values.
- PR4257 (Nick Petalas) is the depth-three count classification. Its
  divisibility and padding arguments are reused; its exceptional profiles
  are one level shorter and share no number with this table.
- PR4263 (Nick Petalas) attains 4m for 6 <= m <= 32. It is used only for the
  cited corollary above.

## Attribution and scope

The complete-call connector interface comes from Ross Richardson's
PR943/PR934 lineage and the
[universal connector](../universal-connector-boundary/README.md).
[SOURCES.json](SOURCES.json) pins the main-tree provenance and the exact
heads of PR4249, PR4257 and PR4263. Scattered-subword counting is classical.

The `connector-alphabet-change` card is explicitly changed to a pricing side
question in [TASK.json](TASK.json). The alphabet is unchanged and no operation
is declared free. Prices must cover complete calls. Admission, instruction
dispatch, coefficient preparation, routing of three dirty intermediates,
precision, stock and supplier/outer transfer remain separate obligations.
There is no supplier caller, selected-frontier change, new κ, formal-kernel
proof or complete multiplication theorem. Independent human and formal
proof-kernel review are unclaimed. Apache-2.0.

## Open next questions

The structured versions in TASK.json give first steps and blockers.

1. What is P(m) for m >= 33? It is {(m,m,m,m)} exactly when the balanced
   vector is feasible, which PR4263 shows only up to m = 32.
2. How many words attain each Pareto vector? PR4257 recorded the depth-three
   counts; a counting DP at length 25 needs a sparser encoding for CI.
3. Which operations carry the premium at depth five? Here the outer calls are
   never doubled at m = 2, 3, 4, but any call can be at m = 5. The same
   middle-letter reduction applies with three inner letters.
4. Can a concrete recursive caller with three dirty intermediates use one of
   these profiles at a favorable complete physical cost?
