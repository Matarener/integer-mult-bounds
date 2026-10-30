# Maximum-mass destination channels at n = 2^g - 1: at most 4g - 3

**A scoped written proof with exact finite corroboration. It has not been independently
reviewed. It makes no kappa, precision-invoice or rounding claim.**

## Result

In PR628's balanced reserved-depth dirty word, inject separate unit errors at the destinations
of distinct completed leaves. Read one register at one later cut. Philippe Van Velzen's PR2177
([`leaf-destination-transport-bound`](../leaf-destination-transport-bound/README.md))
proves that every channel has mass at most H = floor(log2 n). Its Theorem M3 bounds the number
of mass-H channels by 2F(floor(n/2)), but only when n + 1 is not a power of two. For the
excluded all-ones sizes it records only the census value 4g - 3 for g = 3..7.

**Theorem.** For n = 2^g - 1 and g >= 3, in either orientation and at any cut and register, at
most 4g - 3 channels have mass g - 1. Hence

    E_k(2^g - 1) <= k(g - 1) - max(0, k - (4g - 3))   for every k >= 1.

Before this result, PR2177's M1, E_k <= k(g - 1), was the only proved bound at these sizes.
The count is attained for g = 3..6 (9, 13, 17, 21) by the exact check here. There
E_k(2^g - 1) = k(g - 1) for k <= 4g - 3. The written proof covers the upper bound for every
g >= 3. Attainment for g >= 7 is not proved.

The count splits as 2F(b) + 3 with b = 2^(g-1) - 1. The 2F(b) = 4g - 6 channels are the
source-dirty U-phase channels of M3. The extra 3 come from the ceil half V = 2^(g-1), whose
floor log now equals H. Bounding V's two contributions separately would give 6. The new step
pairs the (V,V') channels with V''s own channels through PR2177's Corollary I. Together they
number A + 2c' <= 3: the sign-minus phase V' has at most one, and when it has one, V's mirrored
cut lies in its first two phases, where at most one exists. [PROOF.md](PROOF.md) gives the
complete argument and the per-phase table.

## Scope

All-ones sizes n = 2^g - 1, g >= 3; both orientations; every cut and register; separate
error symbols, as in PROOF3 Part B. The proof cites PR2177's Theorem 1 case table,
Corollary I, Lemmas L1 and X, and PROOF3's Lemma F and M3 source-dirty argument as premises.
Not covered: lower-order channel counts, conjecture C1 (one universal cut), E_infinity for
these sizes, internal leaf intermediates, correlated or rounded errors, and kappa. Card
`uniform-transfer-audit`, scope changed to this transport sub-question (see
[TASK.json](TASK.json)).

## Reproduce

Python 3.12, standard library only. From the repository root:

```sh
python3.12 -B research/all-ones-full-mass-channels/verify.py
python3.12 -B scripts/research_package.py --package research/all-ones-full-mass-channels
```

Expected final line: `PASS_ALL_ONES_FULL_MASS_CHANNELS` (about 25 s). The verifier compares its
word generator with PR2177's pinned `check2.gen` for n = 1..64. It then checks Lemma G
(h = 1..5), Lemma P2 (h = 2..5), and every class bound and the 4g - 3 maximum for g = 3..6. It
also requires an understated bound and the ceil-half split mutation to fail.

## Open next questions

- **Attainment for every g.** Construct one cut and register with 2F(b) full U-phase channels
  and three V-related channels for all g >= 3, as an explicit family like PR2177 Theorem 2.
  This would make E_k(2^g - 1) = k(g - 1) for k <= 4g - 3 a theorem.
- **Lower mass levels.** The largest number of mass H - 1 channels at one cut is still
  census-only for every n. ywz65's `leaf-omega-profile` fixes it only at the Omega cut of
  n = 2^h. Conjecture C1 (that Omega is the universal maximizer) also remains open.

## Credit

Produced by Nick Petalas. The model, Theorem 1, Corollary I, Lemmas L1, X and F, Theorem M3 and
the all-ones census are Philippe Van Velzen's (PR2177). Retain woklerx
(`leaf-destination-transport`), Charles Bethin (PR1416), Arham Tahir (PR1374), Adam Gall
(PR2067), Hanson Sun (PR1085) and Chafik Boukhalfa (PR628 `compose`). ywz65's
`leaf-omega-profile` proves the separate fixed-cut profile for powers of two. The new
contributions are Lemmas G and P2, the case-5 pairing bound and the resulting theorem.
Exact pins are in [SOURCES.json](SOURCES.json). Apache-2.0.
