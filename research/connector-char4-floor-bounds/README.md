# Unsigned connector in characteristic four: 9 ≤ N(4) ≤ 20

Take the unsigned dirty connector of
[#4231](https://github.com/CrocSwap/integer-mult-bounds/pull/4231) over a ring
of characteristic c, with k immutable sources and all 2^k − 1 nonzero
binary-mask outputs. Every legal word needs at least c(k + 2^k − 1) complete
calls. Let N(c) be the largest k at which that floor is attained.
[#4248](https://github.com/CrocSwap/integer-mult-bounds/pull/4248) proved
9 ≤ N(4) ≤ 21 and asked for the exact value. This package shows:

- **Theorem P** (proof, instance-checked): for every even c, a floor walk on k
  sources needs 2^k − 1 ≤ P(c, k), where P counts parity sums of at most c
  boundaries after collapsing adjacent pairs. P(4, 21) = 1,743,531 <
  2,097,151, so **N(4) ≤ 20**. The bound also gives N(8) ≤ 54 (was 55) and
  N(2) ≤ 5; for c = 6, 10 and 12 it gives no gain.
- **No extension** (exhaustive finite check): none of the C(40, 4) = 91,390
  ways to insert four events of a tenth source into #4248's nine-source walk
  reaches all 1,023 masks. So a ten-source floor walk, if one exists, deletes
  to no relabelling of that walk.

The claims are a scoped proof plus an exhaustive finite check. There is no new
κ, no selected-frontier change and no multiplication theorem. N(4) is still
open in 9 ≤ N(4) ≤ 20.

## 1. Interface and prefix criterion

The interface and criterion are #4248's. A floor word has a source walk w of
length ck that uses each source exactly c times. Let q_t ∈ (Z/c)^k count
source events modulo c after t steps, for boundaries t = 0, …, ck. The word is
correct exactly when every nonzero mask m has readout boundaries
t_1 ≤ … ≤ t_c with

```text
q_(t_1) + ... + q_(t_c) = m   in (Z/c)^k.
```

The deletion lemma (#4232, extended by #4248 to every c) makes the set of
attaining k an initial segment. #4248's counting bound uses the
C(ck + c − 1, c) multisets of c boundaries and excludes k ≥ 22 at c = 4.

## 2. Theorem P: a parity count for even characteristic

Let c be even. Reduction Z/c → Z/2 is a ring map, so the parity vectors
u_t = q_t mod 2 ∈ F_2^k satisfy u_(t_1) + … + u_(t_c) = m, because m is binary.
Along the walk, u_t = u_(t−1) + e_(w_t): each step flips one bit. Also
u_0 = u_(ck) = 0.

Let T be the set of boundaries that occur an odd number of times among
t_1, …, t_c, with 0 and ck removed. Then |T| ≤ c, T is nonempty, T lies in
the n = ck − 1 inner boundaries, and m is the sum of u_t over T.

- If T contains no two consecutive boundaries, it is one of at most
  Σ_(i=1..c) C(n − i + 1, i) such subsets.
- If T contains t − 1 and t, then u_(t−1) + u_t = e_(w_t), so
  m = e_(w_t) + Σ_(r∈R) u_r with R = T \ {t − 1, t} and |R| ≤ c − 2. There are
  at most k · Σ_(i=0..c−2) C(n, i) such values.

Every nonzero mask needs a readout, so

```text
2^k − 1 ≤ P(c, k) = Σ_(i=1..c) C(ck − i, i) + k · Σ_(i=0..c−2) C(ck − 1, i).
```

At c = 4, P(4, 20) = 1,422,427 ≥ 1,048,575 but P(4, 21) = 1,743,531 <
2,097,151. With the deletion lemma, every k ≥ 21 fails. So N(4) ≤ 20.

| c | #4248 multiset bound: first excluded k | Theorem P: first excluded k |
|---:|---:|---:|
| 2 | 7 | 6 |
| 4 | 22 | **21** |
| 6 | 38 | 38 |
| 8 | 56 | 55 |
| 10 | 74 | 74 |
| 12 | 93 | 93 |

At c = 2 the bound is consistent with N(2) = 4, which
[#943](../universal-connector-boundary/README.md) established. For odd c the
reduction mod 2 is unavailable and #4248's bound stands.

**Instance check.** On #4248's nine-source walk, the verifier enumerates all
59,535 inner subsets of size at most four. Each one that contains an adjacent
pair has a sum in the e_j-plus-two family. It then reduces all 91,390 boundary
4-multisets mod 2 and checks that each lands in the two counted families.

## 3. The nine-source walk does not extend

[CERTIFICATE.json](CERTIFICATE.json) copies #4248's walk:

```text
4 2 6 4 0 8 1 7 3 2 5 2 1 7 4 3 0 2 5 8 6 5 6 4 8 3 1 0 5 7 8 7 0 3 6 1
```

The verifier re-checks all 511 masks. It then places four events of a tenth
source at every 4-subset of the 40 positions, keeping the other events in
order. For each of the 91,390 walks it finds a nonzero mask that no boundary
4-multiset reaches. The sweep uses 32 distinct witness masks.

Coverage is invariant under relabelling sources. If deleting some source from
a ten-source floor walk gave a relabelling of this walk, relabelling back
would give one of the checked insertions. So no ten-source floor walk restricts
to this walk. This is an exhaustive check of one family, not an exclusion of
k = 10. Insertions into other nine-source floor walks are unchecked.

## 4. Reproduction

From the repository root:

```sh
~/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/connector-char4-floor-bounds/verify.py
~/git/integer-mult-bounds/.venv/bin/python3.12 -O -W error -B research/connector-char4-floor-bounds/verify.py --skip-insertions
~/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/connector-char4-floor-bounds
~/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/connector-char4-floor-bounds --check-source-history
```

Expected marker:
`PASS_CONNECTOR_CHAR4_FLOOR_BOUNDS c4_excludes_k>=21 walk9_has_no_ten_source_extension`.
The verifier uses only the standard library. The full run takes about 25 s
locally; `--skip-insertions` takes under a second. It prints a receipt hash
bound to all six package files. Three mutation controls must be rejected: the
walk with its first two events swapped, the sorted run walk, and a comparison
that requires Theorem P to be strictly tighter than the multiset count at
k = 22.

## 5. Limitations

The result covers only the unsigned, immutable-source, complete-call interface
of #4231. Theorem P is proved for every even c and checked numerically for
c ≤ 12, k ≤ 200. The extension check covers one nine-source walk. Input
admission, coefficient preparation, dispatch and physical costs are unknown.
No consumer is instantiated. Proof-kernel checks and independent human review
are not claimed.

## Open next questions

These are recorded with first steps in [TASK.json](TASK.json).

1. What is N(4) exactly, within 9 ≤ N(4) ≤ 20? A ten-source floor walk
   restricts to ten nine-source floor walks, none a relabelling of the known
   one. Generating inequivalent nine-source walks and running the same sweep is
   the natural next step.
2. Can the carry condition give a much smaller bound? Write each stage as
   u + 2h with u, h ∈ {0, 1}. A mask also needs Σh + e_2(u) = 0 over F_2 in
   every coordinate, where e_2 is the second elementary symmetric function of
   the four parity bits. Heuristically this removes a 2^−k fraction of
   multisets, but the k conditions are not independent.
3. Does any concrete consumer use a characteristic-four batch of more than four
   sources at a favourable complete invoice?

## Credit

Produced by Nick Petalas. The interface and the floor c(k + 2^k − 1) are
#4231's. The nine-source walk, the every-c deletion lemma and the multiset
bound are #4248's; the deletion lemma and counting idea extend #4232's F3
versions. The connector interface and prefix-boundary readout criterion come
from Ross Richardson's [#943](../universal-connector-boundary/README.md).
Apache-2.0.
