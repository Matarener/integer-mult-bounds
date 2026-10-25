# Unsigned five-source connector in every characteristic

This package classifies the unsigned five-source dirty connector by the
characteristic c of its coefficient ring. Characteristic two is the only
exception to the per-operator floor:

| Characteristic c | Exact complete-call optimum, all 31 nonzero binary masks |
|---|---|
| 0 | no finite restoring word exists |
| 2 | 74, from Ross Richardson's [#943](../universal-connector-boundary/README.md) |
| 3 | 108 = 3 · 36, from [#4225](https://github.com/CrocSwap/integer-mult-bounds/pull/4225) |
| 4 | **144 = 4 · 36**, explicit walk below |
| c ≥ 5 | **36c**, run walk below |

For every c ≥ 3, each of the 36 operators is called exactly c times. The
optimum therefore holds for every positive fixed complete-call tariff,
at `c (sum_j c_Bj + sum_m c_Am)`. More generally, for k sources with k ≤ c,
the exact optimum is `c(k + 2^k - 1)` calls under every positive tariff.

This is a **scoped proof with a finite certificate**. It is uniform in the
row length and the maps, within the abstract complete-call contract below.
It is not a complete multiplication theorem. There is no new kappa and no
selected-frontier change.

## Exact boundary

Let R be a nonzero ring with identity, not necessarily commutative, and let
c be the additive order of 1 in R, with c = 0 when that order is infinite.
All rows are arbitrary, distinct and length L over R: k read-only sources
x_j, the 2^k − 1 output rows y_m, and one borrowed dirty connector z.
For arbitrary R-linear maps B_j and A_m of compatible dimension, implement

```text
y_m += sum_(j: bit_j(m)=1) A_m B_j x_j,    m = 1, ..., 2^k - 1;
x_j and z unchanged.
```

The only operations are the unsigned complete calls `B_j: z += B_j x_j` and
`A_m: y_m += A_m z`, with the call contract of #943 and #4225. Sources and
coefficients are immutable. Each call preserves other rows, restores its
private scratch and heads, and acts independently of its old target. Outputs
are unobserved until completion. No signed call, scaling, extra connector,
direct product, frame change, free copy or overwrite is admitted. The signed
alphabet is a different interface and is not studied here.

## Lower bound in every characteristic

Fix any legal word. Let b_j and a_m count its B_j and A_m calls. Specialize to
L = 1 with every map equal to the identity of R. After the word,
`z = z0 + b_j x_j + (other sources)`. Take x_j = 1 and all other inputs zero.
Restoration forces `b_j · 1 = 0` in R, so c divides b_j. Now take every source
zero and z0 = 1. Then y_m gains `a_m · 1`, which must vanish, so c divides a_m.

Each A_m is called at least once, since its requested row is nonzero for
x_j = 1 with j in m. Each B_j is called at least once, since the singleton
output for j depends on x_j and only B_j transmits x_j. Hence:

- If c = 0, then b_j ≥ 1 and b_j = 0 together are impossible. No finite word
  restores the connector, for any k ≥ 1.
- If c ≥ 1, every one of the k + 2^k − 1 operators is called a positive
  multiple of c times. Every legal word has at least `c(k + 2^k - 1)` calls,
  and its positive fixed-price bill is at least c times the price sum.

The zero ring (c = 1) is excluded. There every target is zero and the empty
word suffices.

## Attaining words

Project a word onto its B events, and let q_t ∈ Z^k count source calls among
the first t events. By additivity alone, at boundary t,
`z = z0 + sum_j q_t[j] B_j x_j`, where an integer multiple acts through the
additive group. If A_m is called at boundaries t_1, ..., t_c, it adds

```text
c A_m z0 + sum_j (q_t1[j] + ... + q_tc[j]) A_m B_j x_j.
```

Integer multiples of a vector depend only on their residue modulo c, and
c A_m z0 = 0. The readouts are therefore correct exactly when the prefix sum is
congruent to the binary vector of m modulo c. Boundaries may repeat. Distinct
output calls commute because they preserve z and have distinct targets. No
commutation of A_m with B_j, and no commutativity of R, is used.

**Run walk, for k ≤ c.** Call each source c times consecutively:
`B_0^c B_1^c ... B_(k-1)^c`. Boundary c·j + 1 has prefix e_j, and boundary 0
has prefix zero. For mask m of weight w ≤ k ≤ c, read A_m once at boundary
c·j + 1 for each j in m, and c − w times at boundary 0. The prefix sum is the
indicator of m, and the word has `ck + c(2^k - 1)` calls. With k = 5 this
settles every c ≥ 5.

**Characteristic four, five sources.** The run walk cannot reach the
all-ones mask, because four single-coordinate prefixes have at most four
nonzero coordinates. The length-20 walk

```text
B0 B2 B3 B4 B3 B2 B1 B0 B0 B2 B1 B0 B1 B3 B3 B4 B4 B2 B1 B4
```

calls every source four times. The verifier enumerates all 10,626 multisets of
four boundaries from its 21 boundaries and covers all 31 masks. Mask 31 uses
boundaries (1, 13, 14, 17). The literal 144-call word is in
[CERTIFICATE.json](CERTIFICATE.json).

**Characteristic three, five sources.** This is #4225's walk
`B0 B4 B4 B0 B0 B1 B3 B2 B2 B1 B3 B3 B4 B2 B1`, reused as a fixture with
credit. The regenerated lexicographically first readouts agree with that
package's published examples: mask 1 at (0, 0, 1), mask 31 at (0, 3, 8).

**Characteristic two.** #943 proves the five-source F2 optimum of 74 calls by
the same identity specialization plus an exhaustive census of 945 pairings.
Both halves transfer to any ring of characteristic two. The prime subring of
R is F2, and F2 matrices act R-linearly on R^L while preserving F2^L, so a word
correct over R is correct over F2. Conversely, #943's prefix identity uses
only integer multiples modulo two. That census is cited, not rerun here.
Hence 72 = 2 · 36 is unattainable in characteristic two, and only there.

## Remaining costs

As in #4225, let I pay input admission and layout, P_F reusable coefficient
preparation, and D_W instruction storage, reads, dispatch and schedule
construction. A conditional completed caller bound for c ≥ 3 and five sources
is `I + sum_F P_F + D_W + c (sum_j c_Bj(L) + sum_m c_Am(L))`. Each c_F must
already include its source and coefficient access, arithmetic, target update,
private scratch restoration, head returns and frames. The fixed-price theorem
optimizes only the map-call sum. Word-dependent I, P_F or D_W can change a
physical optimum, and none of them is set to zero.

The call counts and algebra are **proved**. The displayed total is a
**constructive conditional upper bound** once complete primitives exist.
A consumer over a ring of characteristic at least three, its physical
primitive prices, admission and transfer obligations are **unknown here**.

## Verification and source binding

From the repository root:

```sh
~/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/unsigned-connector-characteristic/verify.py
~/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/unsigned-connector-characteristic
~/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/unsigned-connector-characteristic --check-source-history
```

Expected marker:
`PASS_UNSIGNED_CONNECTOR_CHARACTERISTIC c3_calls=108 c4_calls=144 run_cases=41`.
The registered commands run the verifier normally and with `-O`. Checks use
explicit exceptions, so they stay active in optimized Python.

The verifier regenerates CERTIFICATE.json and requires byte equality. For the
characteristic-3 and characteristic-4 walks, it searches all boundary
multisets for readouts, then checks the literal words. A generic simulation
tracks the coefficients of z0 and every B_j x_j modulo c in z and in each
A_m image. Dense runs use dirty rows and pseudo-random singular,
noncommuting matrices over Z/c, with L = 1, 2, 3 and three seeds each.
The run walk is checked for all 41 pairs with 2 ≤ c ≤ 9 and k ≤ min(c, 7).
Every word calls each operator exactly c times.

Eight semantic controls must be rejected: a dropped readout, a readout moved
to the next boundary, a relabelled source call, the characteristic-4 word
read in characteristic 8, the run walk at (c, k) = (4, 5) and (2, 3), and
reversed matrix-factor order for both explicit words. The verifier binds
the #943 README and the provenance files listed in SOURCES.json by SHA-256.
It prints a receipt of all six package-file hashes. It does not write files.

The card's first step, `research/universal-connector-boundary/verify.py`,
was run unchanged as a positive control. It passed with 945 pairings, maximum
coverage 31, 74 queries and 182 leaves. These finite checks support the
written proof. They are not a proof-kernel certificate.

The verifier has no recursion, dynamic evaluation or subprocesses. Every loop
is bounded by a fixed walk, at most 10,626 multisets, a word of at most 1,206
calls or L ≤ 3. No function exceeds 60 lines. Every file read has a 128 KiB
cap. Python allocates during computation, a Power of Ten rule 3 deviation
limited to this bounded offline check. The registered 30-second timeouts are
the compensating control.

## Open next questions

The structured questions are in [TASK.json](TASK.json).

1. In characteristic four, where does the floor `4(k + 2^k - 1)` first fail as
   k grows past five? The run walk settles only k ≤ c. The separate F3
   n-source threshold question is not answered here.
2. Does a concrete caller with coefficients of characteristic at least three
   use the 36c-call batch at a favorable full invoice? First identify an
   immutable-source, unobserved-output consumer and price all 36 primitives,
   admission and dispatch.

## Credit

This contribution was produced by Nick Petalas. It builds on Ross Richardson's
#943/#934 prefix-connector lineage and its characteristic-two census, on
Riquelme Soares's #4189 unsigned-F3 one-source result, and on the
characteristic-three walk of #4225. No predecessor credit line or frozen
package is changed. Independent human and formal proof-kernel review are
unclaimed. Apache-2.0.
