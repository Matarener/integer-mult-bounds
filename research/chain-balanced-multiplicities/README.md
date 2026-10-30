# Balanced depth-three chain multiplicities break every unit symmetry

**Claim type: finite certificate (exact counts for m = 2..24) with a short
scoped proof of its prime-characteristic consequence. No closed form, new
call count, tariff or kappa is claimed.** This contribution is produced by
Nick Petalas.

## Object

The unsigned depth-three dirty chain of
[research/chain-tariff](../chain-tariff/README.md) (PR #4257) has the calls
`1: z1 += B1 x`, `2: z2 += B2 z1` and `3: y += B3 z2` over a ring of exact
characteristic m. Its PROOF.md shows that a word is correct for the target
`y += c B3 B2 B1 x` exactly when every one-letter count and the subword counts
N12 and N23 vanish modulo m and N13 = c modulo m. Here Nij counts scattered
subwords i(i+1)...j. Let W(m,c) be the number of balanced words, with m copies
of each letter, that satisfy these conditions. The chain-tariff package asks
for a closed form for these multiplicities at arbitrary m.

For the one-source depth-two connector, PR #4236 proves a count that depends
only on gcd(c,m) through Ramanujan sums. In particular, at prime m every
nonzero c has the same count.

## Result

**Finite certificate.** For every 3 <= m <= 24, the m-1 numbers
W(m,1), ..., W(m,m-1) are pairwise distinct. Consequently no nontrivial unit u
modulo m satisfies W(m,uc) = W(m,c) for all c. In this range, no formula for
W(m,c) can depend only on gcd(c,m), on c up to sign, or on any other
unit-invariant feature of c. The depth-two law therefore does not extend to
depth three, even at prime m. The first rows are:

```text
m  c=0 .. m-1
2  42 0
3  270 24 0
4  2370 216 432 0
5  15456 5340 6390 3000 2970
6  216774 40320 96954 60228 84888 22320
7  1636956 1102374 1231314 1119006 1214262 869862 1052352
8  29455074 14150304 21697992 13892784 24824112 13586496 20537808 12071664
```

[RESULT.json](RESULT.json) holds every exact count for m <= 24, with the
argmin and argmax nonzero residue per row. The zero entries are exactly the
exceptional targets (2,1), (3,2), (4,3) of the predecessor theorem. This
agrees with it and is not an independent audit of it.

**Prime consequence (scoped proof).** Let p be prime, let V be the balanced
words with N12 = N23 = 0 modulo p, and let F(g) = sum over w in V of
zeta^(g N13(w)), with zeta a primitive p-th root of unity. Finite Fourier
inversion gives W(p,c) = (1/p) sum_g zeta^(-gc) F(g). The Galois automorphism
s_u (zeta to zeta^u) maps F(g) to F(ug). If s_u fixed F(1) for some unit
u != 1, then F(ug) = s_g(F(u)) = s_g(F(1)) = F(g) for every g != 0, and
F(0) is unchanged. Substituting g = u^(-1)h in the inversion formula then
gives W(p,uc) = W(p,c) for all c. The certificate excludes this for every
prime 3 <= p <= 23. Hence F(1) generates the full cyclotomic field Q(zeta_p)
there. At depth two the corresponding sum is rational at every prime, which is
why PR #4236's counts are equal.

## Evidence and reproduction

From the repository root, with CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/chain-balanced-multiplicities/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -O -B research/chain-balanced-multiplicities/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/chain-balanced-multiplicities
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/chain-balanced-multiplicities --check-source-history
```

Any CPython 3.12 path can replace the local interpreter. Expected marker:
`PASS_CHAIN_BALANCED_MULTIPLICITIES max_m=24`. Each direct mode takes about
80 to 90 seconds locally (CPython 3.12, macOS arm64). These are check
durations, not performance claims. The verifier writes nothing unless given
`--write`, which regenerates RESULT.json.

The verifier:

- counts balanced words by a chronological dynamic program over the letter
  counts and the residues of (N12, N23, N13), for m = 2..24;
- compares the complete residue distribution with an independent model for
  m <= 7. That model fixes the A_k ones and B_k threes before the k-th 2, so
  that N12 = sum A_k, N23 = sum (m - B_k) and N13 = sum A_k (m - B_k), and
  weights each gap by a binomial interleaving count;
- compares it again with literal enumeration of every balanced word for m <= 5;
- checks the total mass (3m)!/(m!)^3 for every m;
- checks that the counts for nonzero residues are pairwise distinct and the
  unit stabilizer is trivial for m = 3..24;
- as a positive control, reproduces PR #4236's equal depth-two counts
  (binom(2p,p)-2)/p and full stabilizer at p = 2, 3, 5, 7, so the
  distinctness test does detect equality when it holds;
- rejects a forged table with equal nonzero counts and compares the full
  recomputation with RESULT.json.

## Limits

The certificate is finite: m <= 24. It does not prove distinctness, or even
nontrivial asymmetry, for larger m, and it gives no closed form. The
correctness criterion is the cited chain-tariff identity; no dirty-register
execution is repeated here. Only balanced words are counted. These are the
minimum words except at the three exceptional targets, whose minimum words
chain-tariff already counts. Multiplicity concerns schedule choice only. No
supplier caller, physical routing, admission, precision or outer
multiplication transfer is addressed. Independent human and formal
proof-kernel review are unclaimed.

## Open next questions

Structured versions with first steps and blockers are in [TASK.json](TASK.json).

1. Does pairwise distinctness, or at least the trivial unit stabilizer, hold
   for every m >= 3? At prime p this is the statement that F(1) is not fixed
   by any nontrivial Galois automorphism.
2. Are the nonzero counts asymptotically equidistributed at prime m? The
   relative spread falls to about 1.2e-7 at p = 23. Composite m stay far more
   uneven, for example about 0.4% at m = 24 (spread is (max-min)/min).
3. Find a closed form or a holonomic recurrence for W(m,c). The certificate
   only rules out unit-invariant shapes.

## Credit and sources

Nick Petalas's PR #4257 (research/chain-tariff, head
`91b4e49d0b80b0d8589f6e2cb23a0af75422e91b`) supplies the chain contract, the
interval-count correctness identity and the open question. Nick Petalas's
PR #4236 (research/unsigned-connector-residue-count, head
`bd9b426837cddd37338dd284e49cc2303de57ca0`) supplies the depth-two law used
for contrast and control. Rotation closure of correct chain words is observed
in research/depth5-chain-connector and is not used here. The complete-call
interface belongs to Ross Richardson's PR943/PR934 lineage and the
[universal connector](../universal-connector-boundary/README.md). Predecessor
results are cited, not rechecked. Pins are in [SOURCES.json](SOURCES.json).
New files are Apache-2.0.
