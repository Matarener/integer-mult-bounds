# Depth-four chain connector: a row model and the 4m minimum for 33 <= m <= 64

This package extends open question 1 of
[#4263](https://github.com/CrocSwap/integer-mult-bounds/pull/4263) from
characteristic 32 to characteristic 64. The contribution was produced by Nick
Petalas.

The complete calls are `z_l += B_l z_{l-1}` for l = 1, 2, 3, 4, with x = z_0
immutable and z_1, z_2, z_3 and y = z_4 holding arbitrary dirty data. The maps
are arbitrary and the coefficients lie in a nonzero unital ring of exact
characteristic m. For a nonzero residue c the word must restore z_1, z_2 and
z_3 and add `c B4 B3 B2 B1 x` to y. There are no sign or inverse calls.

```text
shortest length = 4m   for every 33 <= m <= 64 and every c != 0 (mod m)
```

| m | 2 | 3 | 4 | 5 | 6 to 32 | 33 to 64 |
|---|---:|---:|---:|---:|---:|---:|
| shortest length | 12 | 18 | 20 | 25 | 4m | 4m |
| source | #4249 | #4249 | #4249 | #4249 | #4263 | this package |

The new results are:

1. **Finite certificate.** One witness for each of the 1,520 pairs (m, c) with
   33 <= m <= 64 and 1 <= c < m, each using every call exactly m times.
2. **Scoped proof (Lemma 2).** An exact criterion for a balanced word in terms
   of a partition and two monotone profiles. It holds for every m and is what
   makes the witnesses compact and quick to find.
3. **Scoped proof (Lemma 3).** For prime m, the partition needs at least three
   rows strictly between 0 and m.

With #4249 and #4263, which are open and not rechecked here, the depth-four
minimum is known exactly for 2 <= m <= 64. No all-m theorem, no new κ, no
supplier admission and no change to the selected frontier.

## Argument

**Lemma 1 (floor; #4249).** A word is correct for c iff every scattered
subword count N[i..j] of i(i+1)...j is 0 mod m, except N[1..4], which is c mod
m. So each call appears a positive multiple of m times, and every correct word
has at least 4m calls. A word with exactly m copies of each call is *balanced*.

**Lemma 2 (row model).** Call 1 commutes with calls 3 and 4, and call 4 with
calls 1 and 2. So a balanced word is fixed, up to its action, by three objects:

- the subword of calls 2 and 3. Let f(p) be the number of calls 2 before the
  p-th call 3. The cells above this lattice path form a partition λ in the
  m × m box: column p has height m − f(p). Write ℓ(q) for its row lengths,
  q = 1..m, top row first.
- the levels of the calls 1. A call 1 with a calls 2 before it has row level
  r = m − a. Let ρ(q) be the number of calls 1 with r >= q.
- the levels of the calls 4. A call 4 with b calls 3 before it has level b.
  Let β(p) be the number of calls 4 with b >= p, and B(L) = β(1) + ... + β(L).

Conversely, every partition λ in the box and every pair of nonincreasing
profiles ρ, β with values in [0, m] come from a balanced word. The word is
correct for c iff

```text
(i)   Σ_q ℓ(q)        ≡ 0        (iv)  Σ_q ρ(q) ℓ(q)     ≡ 0
(ii)  Σ_q ρ(q)        ≡ 0        (v)   Σ_q B(ℓ(q))       ≡ 0
(iii) Σ_p β(p)        ≡ 0        (vi)  Σ_q ρ(q) B(ℓ(q))  ≡ −c      (mod m)
```

*Proof.* Count each interval by the calls that complete it. N[2..3] = Σ f(p) =
m² − |λ|. A call 1 at level a precedes m − a calls 2, so N[1..2] = Σ ρ(q), and
N[3..4] = Σ b = Σ β(p). For N[1..3], N[2..4] and N[1..4] use

```text
Σ_{p <= b} (f(p) − a)^+ = b (m − a) − C(m − a, b),
```

where C(r, b) is the number of cells of λ in rows 1..r and columns 1..b. This
holds because column p has (m − a) − (f(p) − a)^+ cells in rows 1..m − a.
Summing over the calls gives N[1..3] = m N[1..2] − Σ ρ(q) ℓ(q),
N[2..4] = m N[3..4] − Σ B(ℓ(q)) and N[1..4] = N[1..2] N[3..4] − Σ ρ(q) B(ℓ(q)).
Reduce mod m. ∎

A row of length m drops out of (i), (iv), (v) and (vi) once (iii) holds. It
contributes only to (ii). So each witness here has one full row, used to settle
(ii), and three to five rows strictly between 0 and m. The witnesses store
(λ, ρ, β) directly.

**Lemma 3 (two short rows are not enough for prime m).** Let m be prime. If λ
has at most two rows with 0 < ℓ < m, every correct word has c ≡ 0.

*Proof.* Rows of length 0 and m drop out of (i), (iv), (v) and (vi). One short
row contradicts (i). Two short rows ℓ_1 >= ℓ_2 must satisfy ℓ_1 + ℓ_2 = m. Then
(iv) reads (ρ_1 − ρ_2) ℓ_1 ≡ 0. Since ℓ_1 is a unit, ρ_1 ≡ ρ_2, and (vi) becomes
ρ_1 (B(ℓ_1) + B(ℓ_2)) ≡ 0 by (v). ∎

### What did not give an all-m law

A uniform family was looked for and not found. These local searches are not
part of the package:

- Designs whose block lengths are all small constants or m minus small
  constants, with at most four blocks per letter in the 2/3 path and up to three
  levels each for calls 1 and 4, gave no witness that works for the same c at
  m = 101, 103 and 107.
- One full row, three short rows, ρ = 0 on the last short row, and calls 4 at
  one level b plus filler at level 1, covers only some residues: none at m = 7
  and m = 8, and 5 of the 10 nonzero residues at m = 11.
- The constraint that blocks a simple parametric proof is the budget: ρ(1) and
  the number of calls 4 must stay at most m while (ii) and (iii) hold.

## Evidence and reproduction

From the repository root, with CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/depth4-chain-rowmodel/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -O -W error -B research/depth4-chain-rowmodel/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/depth4-chain-rowmodel
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/depth4-chain-rowmodel --check-source-history
```

Any CPython 3.12 can replace the local interpreter path. The verifier writes no
files and runs in about a second. It prints a JSON receipt with the SHA-256 of
every package file and input, then
`PASS_DEPTH4_CHAIN_ROWMODEL moduli=32 witnesses=1520`. It checks:

- For every witness: the shapes of λ, ρ and β, the five vanishing sums of
  Lemma 2 and the predicted coefficient c.
- The word built from the record: length 4m and exactly m copies of each call,
  the interval conditions of Lemma 1 by one counting pass, and separately the
  UT5(Z/m) product I + c e_{1,5}.
- One literal replay per witness with dirty registers in (Z/m)^2 and random
  2x2 maps, which generally do not commute. It checks that z_1, z_2 and z_3 are
  restored and y gains exactly c B4 B3 B2 B1 x.
- Lemma 2 on 4,000 random records with 2 <= m <= 9: the sums decide
  correctness exactly as direct counting does, and give the same c when the
  word is correct. Lemma 3 on random records with two short rows and prime m.
- Five rejection controls on the witness for (m, c) = (37, 5): a wrong
  coefficient, a changed ρ(1), a shortened row, a moved call-4 level and a
  dropped call.

The witnesses were found by a randomized solver in the row model: draw the
short rows and the call-4 level, keep draws that satisfy (i) and (v), and solve
(iv) and (vi) for the top two values of ρ. The solver is not part of the
package. The verifier checks the records and the words themselves, so it does
not matter how they were found.

## Limitations

The certificate covers only 33 <= m <= 64. It is a finite certificate per
(m, c), not an all-m theorem. The values for m <= 32 come from #4249 and #4263
and are not rechecked here. Lemmas 2 and 3 are proved in this README and only
spot-checked by the verifier. Independent human and formal proof-kernel review
are unclaimed. Every call carries its complete implementation price.
Admission, dispatch, routing of the three intermediates and word-dependent
physical costs are extra. No supplier caller, precision analysis, outer
multiplication theorem or new κ is supplied.

## Open next questions

The structured questions in [TASK.json](TASK.json) give first steps and
blockers.

1. Is the depth-four minimum exactly 4m for every m >= 6? Lemma 2 turns this
   into a question about one partition and two profiles. A parametric choice of
   four short rows, ρ and β that keeps ρ(1) <= m and at most m calls 4 for
   every c would settle it.
2. Is three short rows enough for every prime m >= 7? Lemma 3 shows two are
   not. 436 of the 1,520 witnesses here use three.
3. Does a row model of the same kind describe depth five, with two interior
   paths, and give the floor 5m there?

## Attribution and scope

The chain model, the interval-count reduction, the floor and the m <= 5
depth-four minima come from
[#4249](https://github.com/CrocSwap/integer-mult-bounds/pull/4249). The
witnesses for 6 <= m <= 32 and the three-interleaving lemma come from
[#4263](https://github.com/CrocSwap/integer-mult-bounds/pull/4263). Ross
Richardson's [#943/#934 lineage](../universal-connector-boundary/README.md)
supplies the complete-call dirty-connector interface. The new results here are
the row model of Lemma 2, Lemma 3 and the 1,520 witnesses for 33 <= m <= 64.
Subword counts, unitriangular matrices and lattice-path partitions are
classical tools; no novelty is claimed for them. Exact pins are in
[SOURCES.json](SOURCES.json).

The `connector-alphabet-change` card is explicitly changed to this side
question, as in #4249 and #4263. The alphabet stays unsigned and complete.
Apache-2.0.
