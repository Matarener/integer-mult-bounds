# Unsigned connector: a five-source depth-two block in every c ≥ 5, so N(c) ≥ ⌊5c/2⌋

Take the unsigned dirty connector of
[#4231](https://github.com/CrocSwap/integer-mult-bounds/pull/4231) over a ring
of characteristic c, with k immutable sources and all 2^k − 1 nonzero
binary-mask outputs. Every legal word needs at least c(k + 2^k − 1) complete
calls. Let N(c) be the largest k at which that floor is attained.
[#4248](https://github.com/CrocSwap/integer-mult-bounds/pull/4248) proved
N(c) ≥ 2c for every c by concatenating depth-one two-source blocks. Its open
question 2 asks how N(c) grows, and names a depth-d block with more than 2d
sources, valid for every large c, as the way to raise the constant.
[#4271](https://github.com/CrocSwap/integer-mult-bounds/pull/4271) showed that
no five-source depth-two block exists at c = 4.

This package shows:

- **Theorem T** (proof, finite core checked): one explicit 30-event template
  gives a five-source depth-two block in **every** characteristic c ≥ 5.
- **Corollary** (proof): N(c) ≥ ⌊5c/2⌋ for every c ≥ 5. This improves 2c by
  ⌊c/2⌋, for example N(5) ≥ 12, N(6) ≥ 15, N(7) ≥ 17 and N(8) ≥ 20.

The claims are a scoped proof plus a finite certificate. There is no new κ,
no consumer, no selected-frontier change and no multiplication theorem.
Characteristic four is untouched: 9 ≤ N(4) ≤ 17 stands.

## 1. Interface and depth

The interface, prefix criterion and depth notion are #4248's. A floor word has
a source walk w of length ck that uses each source exactly c times. Let
q_t ∈ (Z/c)^k count source events modulo c after t steps. The word is correct
exactly when every nonzero mask m has readout boundaries t_1 ≤ … ≤ t_c with
q_(t_1) + … + q_(t_c) = m in (Z/c)^k. A walk has **depth d** if every
nonzero mask is a sum of at most d prefixes. #4248's concatenation lemma joins
walks on disjoint source sets whose depths sum to at most c into a floor walk;
spare readouts go to boundary 0.

## 2. Theorem T: the lifted template

[CERTIFICATE.json](CERTIFICATE.json) gives the base walk on sources 0–4,
each used six times,

```text
W = 0 2 1 4 3 2 0 3 1 0 4 1 4 4 2 0 3 3 1 2 4 3 1 2 0 4 3 1 2 0
```

and cut positions a = (3, 3, 2, 2, 3). Let n_t(j) be the number of events of
source j among the first t events of W. Define the **lifted prefix**
L_t ∈ Z^5 by L_t(j) = n_t(j) if n_t(j) ≤ a_j, and n_t(j) − 6 otherwise. So
coordinate j runs 0, 1, …, a_j, then a_j − 5, …, −1, 0.

**Template identity** (finite check). For every nonzero m ∈ {0,1}^5 there are
base boundaries t_1 ≤ t_2 with L_(t_1) + L_(t_2) = m **as integer vectors**.
The verifier finds a pair for all 31 masks.

**Expansion.** For c ≥ 5, form W_c by replacing the (a_j + 1)-th event of each
source j with a run of c − 5 copies of j. At c = 5 that event is deleted.
Each source then occurs 6 − 1 + (c − 5) = c times.

**Proof of Theorem T.** Let τ(t) be the boundary of W_c that follows the first
t events of W (after the whole run, if event t is expanded). Count source j at
τ(t). If n_t(j) ≤ a_j, the expanded event has not occurred and the count is
n_t(j) = L_t(j). Otherwise it is n_t(j) − 1 + (c − 5) = n_t(j) + c − 6, which
is L_t(j) modulo c. Hence q_(τ(t)) ≡ L_t (mod c). For a mask m with
L_(t_1) + L_(t_2) = m in Z^5, reduction modulo c gives
q_(τ(t_1)) + q_(τ(t_2)) = m. So W_c has depth two on five sources. ∎

The argument needs c − 5 ≥ 0. It cannot reach c = 4, where #4271 excludes
every five-source depth-two block.

## 3. Corollary: N(c) ≥ ⌊5c/2⌋ for every c ≥ 5

Concatenate ⌊c/2⌋ copies of W_c on disjoint five-source sets. For odd c,
append #4248's depth-one block a b a^(c−1) b^(c−1) on two more sources. The
total depth is at most c, so #4248's concatenation lemma gives a floor walk on
5⌊c/2⌋ + 2(c mod 2) = ⌊5c/2⌋ sources. #4248's deletion lemma makes the
attaining set an initial segment, so the floor is attained for every
k ≤ ⌊5c/2⌋.

| c | #4248: 2c | this package: ⌊5c/2⌋ | counting: first excluded k (#4248) |
|---:|---:|---:|---:|
| 5 | 10 | **12** | 30 |
| 6 | 12 | **15** | 38 |
| 7 | 14 | **17** | 47 |
| 8 | 16 | **20** | 55 (#4255) |

The counting column is #4248's and #4255's upper bound, quoted, not rechecked.

## 4. What the verifier checks

[verify.py](verify.py) uses only the standard library and takes about 2 s.

1. The template identity for all 31 masks, with integer arithmetic.
2. For every 5 ≤ c ≤ 64: W_c uses each source c times, every nonzero mask is
   a sum of two prefixes modulo c by direct search, and each lifted readout
   pair maps through τ to a correct readout. Item 1 is the only finite step the
   proof needs; item 2 is a control.
3. For c = 5, 6, 7: the concatenated floor walks on 12, 15 and 17 sources. It
   builds the literal words of 20,535, 196,692 and 917,616 calls and simulates
   them with generic coefficients over Z/c, following #4248's simulator. Every
   output must equal its mask, the connector must return to its dirty value,
   and every operator must be called exactly c times.
4. Five mutation controls must be rejected: the unexpanded c = 6 block read in
   characteristic seven, the c = 5 block read in characteristic four, every cut
   moved one event later, three depth-two blocks at c = 5, and a floor word
   with one readout call dropped.

Expected marker:
`PASS_CONNECTOR_FIVE_HALVES depth_two_k5_every_c>=5 N(c)>=floor(5c/2)`.
It also prints a receipt hash bound to all six package files.

## 5. Search notes (local only, not proofs)

The template came from simulated annealing over 30-event base walks and cut
vectors under the integer criterion. The same search with five events per
source (cuts of a 25-event walk) peaked at 28 of 31 masks over 30 runs, which
matches the c = 4 obstruction of #4271. Direct searches modulo c found
depth-two five-source blocks at c = 5, 6, 7 and 8 separately. The search
programs and logs are not committed.

## 6. Reproduction

From the repository root:

```sh
~/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/connector-five-halves-growth/verify.py
~/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/connector-five-halves-growth
~/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/connector-five-halves-growth --check-source-history
```

## 7. Limitations

The result covers only the unsigned, immutable-source, complete-call interface
of #4231, and relies on #4248's prefix criterion, concatenation lemma and
deletion lemma, which are cited and not re-derived. Theorem T is proved for
every c ≥ 5; the direct block check runs for c ≤ 64 and the literal word
simulation for c ≤ 7. Fixed call prices must include their full
implementation. Input admission, coefficient preparation, dispatch and physical
costs are additional and unknown. No consumer is instantiated. N(c) for c ≥ 5
remains open between ⌊5c/2⌋ and the counting bound. Proof-kernel checks and
independent human review are not claimed.

## Open next questions

These are recorded with first steps in [TASK.json](TASK.json).

1. Does any characteristic admit a depth-two block on six or more sources?
   One valid for all large c would give N(c) ≥ 3c. The lifted integer
   criterion with more cut points per source is a direct first search.
2. Is there a depth-three block on eight or more sources valid for every large
   c? It would give density 8/3 > 5/2.
3. Is N(c)/c unbounded? Counting gives O(c log c); this package gives ⌊5c/2⌋.
4. Does any concrete consumer use a characteristic-c batch at a favorable
   complete invoice? The abstract call counts change no supplier or κ.

## Credit

This package was produced by Nick Petalas. It builds on the interface and lower
bound of #4231, the prefix criterion, depth notion, concatenation and deletion
lemmas and N(c) ≥ 2c of #4248, the deletion lemma of
[#4232](https://github.com/CrocSwap/integer-mult-bounds/pull/4232), the
counting bounds of #4248 and
[#4255](https://github.com/CrocSwap/integer-mult-bounds/pull/4255), and the
c = 4 depth-two obstruction of #4271. The word builder and generic simulator
in verify.py are adapted from research/connector-depth-blocks/verify.py.
New work is Apache-2.0.
