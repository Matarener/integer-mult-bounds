# Unsigned F3 connector: the surcharge above the floor grows with n

For n immutable sources, all 2^n − 1 nonzero binary-mask outputs and one
arbitrarily dirty restored connector over F3, write the optimum as
3(n + 2^n − 1) + 3X(n). The floor is the first term and X(n) is the excess.
This package shows:

- **Deletion step** (proof): if X(n) ≥ 1 then X(n − 1) ≤ X(n) − 1. With the
  seven-source exclusion of
  [#4250](https://github.com/CrocSwap/integer-mult-bounds/pull/4250)
  (X(7) = 1), this gives **X(n) ≥ n − 6 for every n ≥ 7**.
- **Eight sources, exact** (proof plus finite certificate): a 30-event path in
  which two sources occur six times serves all 255 masks with readout triples.
  It gives a 795-call word, and the deletion step gives 795 as a lower bound.
  **The eight-source optimum is 795**, the floor 789 plus six.
- **Nine sources** (finite certificate): a 39-event path with four doubled
  sources gives a 1572-call word, so 1569 ≤ opt(9) ≤ 1572.
- **Counting** (proof): together with the deletion step, a triple count gives
  the lower-bound table below. It becomes larger than n − 6 from n = 17.

This answers #4250's open question 1 for n = 8. The claims are scoped proofs
plus finite certificates. There is no new κ, no selected-frontier change and
no multiplication theorem.

## 1. Interface (from predecessors)

The interface is that of
[#4232](https://github.com/CrocSwap/integer-mult-bounds/pull/4232) (head
`86ad339efc9f817846479431d8cc0f04edf95fb9`). Rows are n read-only sources
x_j, outputs y_m for m = 1, …, 2^n − 1 and one borrowed dirty connector z. For
arbitrary F3-linear maps B_j and A_m the word must add
`sum_(j in m) A_m B_j x_j` to every y_m and restore x and z. The only calls
are unsigned `B_j: z += B_j x_j` and `A_m: y_m += A_m z`. The maps may be
singular and need not commute.

## 2. Every legal word is a source path with readout lists

This sharpens #4232's floor-word description to all words. Let the source
path be the subsequence of B calls, with length P, and let q_t ∈ F3^n count
the source events of each kind modulo three after t of them. An A_m call made
after t source events adds A_m z0 + Σ_j (q_t)_j A_m B_j x_j. If A_m occurs at
boundaries t_1, …, t_a, output m receives

```text
a·A_m z0 + Σ_j (q_t1 + … + q_ta)_j A_m B_j x_j.
```

With 1×1 identity maps and independent x_j and z0 this forces three
conditions, and the display shows that they are also sufficient for every
choice of maps:

1. each source occurs a positive multiple of three times (restoring z, as in
   #4225 and #4232);
2. each mask m has a positive multiple of three readouts;
3. the readout boundaries of m sum to m: q_t1 + … + q_ta = m in F3^n.

Write the counts as 3(1 + e_j) for source j and 3(1 + r_m) for mask m, with
e_j, r_m ≥ 0. Then the call count is the floor plus 3X with
X = Σ_j e_j + Σ_m r_m. Since q_0 = q_P = 0, the boundary values take at most
P distinct points.

## 3. Deletion step

Fix a legal n-source word and a source j. Define its **load** as
load_j = e_j + Σ_(m ∋ j) r_m.

**Lemma.** Deleting source j gives a legal (n − 1)-source word with excess at
most X − load_j.

*Proof.* Remove every B_j call. Map each old boundary t to the new boundary
τ(t) after the same non-j events. The new count vector at τ(t) is q_t with
coordinate j removed. For an (n − 1)-mask m', its two preimages are m' and
m' + e_j, where the second also contains j. Keep the readout list of the
preimage with fewer readouts, move it to the boundaries τ(t) and use it for
m'. Its sum projects to m', so condition 3 holds. Conditions 1 and 2 are
untouched, so the new word is legal. Mask e_j has no image and is dropped.
The new excess is

```text
X' = Σ_(i≠j) e_i + Σ_(m'≠0) min(r_m', r_(m'+e_j))
   = X − e_j − r_(e_j) − Σ_(m'≠0) max(r_m', r_(m'+e_j))
   ≤ X − e_j − Σ_(m ∋ j) r_m = X − load_j.  ∎
```

**Corollary.** If X ≥ 1 then some source has load at least one. If some e_j
is positive, take that j. Otherwise some r_m is positive; take any j in m.
So X(n − 1) ≤ X(n) − 1 whenever X(n) ≥ 1. With X = 0 the lemma is #4232's
floor deletion lemma.

**Induction.** #4250 excludes the floor at n = 7 and #4232's 405-call word
attains floor + 3, so X(7) = 1. The floor deletion lemma gives X(n) ≥ 1 for
every n ≥ 7. The corollary then gives X(n) ≥ X(n − 1) + 1 for n ≥ 8, so
X(n) ≥ n − 6.

At n = 8 the lemma says more: since X(7) = 1, every source of an optimal
eight-source word has load at most one.

## 4. Counting bound

Take a word whose path has E extra source triples, so P = 3n + 3E. Masks with
three readouts use a multiset of three among at most P boundary values, so
at most C(3n + 3E + 2, 3) of them exist. Every other mask has r_m ≥ 1. Hence

```text
X(n) ≥ min over E ≥ 0 of  E + max(0, 2^n − 1 − C(3n + 3E + 2, 3)).
```

This counts boundaries cyclically, so at E = 0 it improves #4232's
C(3n + 3, 3) to C(3n + 2, 3). It is zero for n ≤ 13. Combined with the
deletion step, the verifier checks the table to n = 64:

| n | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 | 17 | 18 | 19 | 20 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| X(n) ≥ | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 14 | 21 | 30 | 42 |
| counting alone | – | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 5 | 9 | 14 | 21 | 30 | 42 |

## 5. Certificates

[CERTIFICATE.json](CERTIFICATE.json) lists the paths. The eight-source path,
with sources 0 and 1 occurring six times, is

```text
5 5 3 7 0 3 1 4 1 1 7 7 1 4 4 0 1 1 2 0 6 0 0 2 2 0 5 6 6 3
```

Every one of the 255 masks has a readout triple, so the word has
30 + 3·255 = 795 calls. The nine-source path has sources 0 to 3 doubled and
39 events. Its word has 39 + 3·511 = 1572 calls.

The verifier picks the lexicographically first triple for every mask, builds
the literal call list and simulates it with generic coefficients: z is a
formal sum over z0 and the B_j x_j terms, and each A_m call left-multiplies
it. Every output must equal its mask row with no z0 term, and z must
restore. It also applies the deletion map of section 3 to every source of
both words and of #4232's 405-call word, simulates each result and checks its
excess against the lemma. Every deletion of the 405-call word gives a 207-call
six-source floor word. Four mutation controls must be rejected.

## 6. Search evidence (local only, not a proof)

Bounded simulated annealing over paths, with swaps of two events, produced
the certified words. For n = 9 with three doubled sources (excess 3) the best
of four runs served 499 of 511 masks. That is a search failure, not an
exclusion; X(9) is 3 or 4. For n = 10, fourteen runs of at most 400 s each
with five, six or seven doubled sources reached at most 993 of 1023 masks, so
no n = 10 upper bound is certified here. For n = 8, runs over 27-event paths with one
doubled source stopped at 244 of 255 masks, which the lemma explains: such a
word would have excess 1. The annealing source and logs are not committed.

## 7. Reproduction

From the repository root:

```sh
~/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/f3-n-source-connector-excess/verify.py
~/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/f3-n-source-connector-excess
~/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/f3-n-source-connector-excess --check-source-history
```

Expected marker:
`PASS_F3_N_SOURCE_CONNECTOR_EXCESS opt8=795 excess_lb=n-6 exact_n=8`. The
verifier is standard-library only, runs in about 2 s and prints a receipt
hash bound to all six package files.

## 8. Limitations

- The lower bound rests on #4250's computer census for n = 7, which this
  package cites and does not replay. The deletion step and the counting bound
  are written proofs; no proof-kernel check or independent human review is
  claimed.
- Exact optima are known only for n ≤ 8. For n = 9 the gap is one triple.
- The result covers only the unsigned, immutable-source, complete-call
  interface over F3. Admission, coefficient preparation, dispatch and physical
  costs are additional and unknown. No consumer is instantiated.

## Open next questions

1. Is the nine-source optimum 1569 or 1572? An excess-3 word needs a 36-event
   path with three doubled sources, or another mix with the same excess.
2. What are the exact optima for n = 10..16, where the deletion step beats
   the counting bound?
3. Can the deletion step remove more than one excess unit per source, for
   example by averaging loads over all sources?

## Credit

Produced by Nick Petalas. The interface, the floor deletion lemma and the
405-call seven-source word are from #4232. The seven-source exclusion is from
#4250. The mod-three count argument is from #4225. The F3 alphabet and
one-source handoff are Riquelme Soares's #4189. The connector interface and
prefix-readout criterion originate in Ross Richardson's #943. Apache-2.0.
