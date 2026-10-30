# Bounded-depth connector blocks: depth two caps at log₂ c + O(log log c) sources

**Scoped upper bound for the unsigned dirty connector; no new κ.**
In the unchanged interface of PR4231/PR4248, a depth-d block on k sources in
characteristic c ≥ 2 satisfies

```text
2^k − 1 ≤ k · min(k, c) · binom(kc + d − 2, d − 1).
```

For d = 2 this is `2^k − 1 ≤ k² c · min(k, c) ≤ k³c`, so every depth-two block has
`k ≤ 1 + log₂ c + 3 log₂ k` sources. Trivial pair counting allows about
2 log₂ c. Consequences:

- The reflected-Gray blocks of [PR6071](https://github.com/CrocSwap/integer-mult-bounds/pull/6071)
  (k = 1 + ⌊log₂ c⌋) are within O(log log c) of the largest possible
  depth-two block. A depth-two block "near k ≈ 2 log₂ c", which PR6071's
  open question 1 suggests looking for, does not exist once c is large.
- Every floor word built by PR4248's concatenation (blocks with depths
  summing to at most c, each mask read inside each block) using blocks of
  depth at most two has
  `n ≤ c · max(2, K₂(c)/2) = (1/2 + o(1)) c log₂ c` sources. PR6071's
  `(1 + ⌊log₂ c⌋)⌊c/2⌋` lower bound attains this, so **1/2 is the sharp
  leading constant for depth ≤ 2 block concatenations**.
- More generally, such concatenations of blocks of depth at most D give at most
  `(1 − 1/D + o(1)) c log₂ c` sources. A leading constant above 1/2 needs
  blocks of depth at least three; reaching the counting constant 1 needs
  depth that grows with c, or reads that are not organized in blocks.

The general constant of N(c)/(c log₂ c) stays open in [1/2, 1]. This
package proves no new lower bound.

```sh
python3.12 -I -W error -B research/connector-bounded-depth-cap/verify.py
```

Expected (about 2 s, standard library only):
`PASS_CONNECTOR_BOUNDED_DEPTH_CAP sources=1 census_cases=8 identity_checks=1031591 gray_blocks=21 gray_masks=741 cap_beats_trivial_from=2^6 controls=4 sha256=499b979ff5d691fd`.
Add `--table` to print the census and the capacity table below.

## Interface and definitions (inherited)

The interface is [PR4248](../connector-depth-blocks/README.md)'s unsigned
immutable-source, one-dirty-connector model, unchanged; no operation is added.
A floor word calls every source operator B_j exactly c times. Let q_t ∈ Z^k
be the integer count vector of the first t source calls of a word W, so
q_0 = 0 and q_{kc} = c·1. PR4248 says W has **depth d** on its k sources if
every nonzero binary mask m is congruent modulo c to a sum of at most d
prefixes q_t. Blocks of total depth at most c concatenate to a floor word,
and deleting a source keeps the depth (PR4248, PR6071).

## Theorem (weight identity)

**Lemma.** If `q_{a_1} + ... + q_{a_e} ≡ m (mod c)` for a binary mask m, then
`a_1 + ... + a_e ≡ |m| (mod c)`.

*Proof.* Each source call increases one coordinate by one, so the coordinate
sum of q_t is t. Sum the congruence over all k coordinates. ∎

**Theorem.** A depth-d block on k sources at characteristic c ≥ 2, with
d ≥ 1, satisfies `2^k − 1 ≤ k · min(k, c) · binom(kc + d − 2, d − 1)`.

*Proof.* Since q_{kc} ≡ 0 ≡ q_0, every read can use a boundary in
{0, ..., kc − 1}, and reads at boundary 0 pad any representation to exactly
d reads. So each nonzero mask m is represented by a multiset
{a_1 ≤ ... ≤ a_d} of these kc boundaries, and the multiset determines m.
Fix the sub-multiset {a_1, ..., a_{d−1}}: there are binom(kc + d − 2, d − 1)
choices. By the lemma, a_d ≡ |m| − (a_1 + ... + a_{d−1}) (mod c). The
weight |m| lies in {1, ..., k}, so it takes at most min(k, c) residues mod c.
Each residue has exactly k representatives in {0, ..., kc − 1}. So at most
k · min(k, c) values of a_d are possible, and each value determines m. ∎

Only additivity and the c-fold call count are used. The ring may be any
nonzero unital ring of characteristic c; the bound concerns schedules that are
correct for arbitrary compatible maps, as in PR4248.

**Depth two.** `2^k − 1 ≤ k² c · min(k, c) ≤ k³c`. Since `2^(k−1) ≤ 2^k − 1` for k ≥ 1,
`k ≤ 1 + log₂ c + 3 log₂ k`. For d ≥ 2 write K_d(c) for the largest k that the exact theorem inequality
`2^k − 1 ≤ k · min(k, c) · binom(kc + d − 2, d − 1)` allows (the verifier and
table use this exact form, not the k³c relaxation); set K₁ = 2 by PR4248
Lemma C. By deletion, no block has more than K₂(c)
sources.

**Fixed depth d ≥ 2.** `binom(kc + d − 2, d − 1) ≤ (kcd)^(d−1)`, so
`k ≤ 1 + 3 log₂ k + (d − 1)(log₂ c + log₂ k + log₂ d)`. Since k = O(d log c),
`k/d ≤ (1 − 1/d) log₂ c + O(log d + log log c)`.

**Concatenation.** Let a floor word be a concatenation of blocks of depths
d_i ≤ D with Σ d_i ≤ c. Depth-one blocks carry at most two sources
(PR4248 Lemma C), so `n = Σ k_i ≤ c · max_{1 ≤ d ≤ D} K_d(c)/d`. For D = 2
this is `n ≤ c · max(2, K₂(c)/2)`, which is `(1/2 + O(log log c / log c)) c log₂ c`.
PR6071 gives `n ≥ (1 + ⌊log₂ c⌋)⌊c/2⌋ + 2(c mod 2)`. Both ratios to
c log₂ c tend to 1/2. For D ≥ 3 the ceiling is `(1 − 1/D + o(1)) c log₂ c`;
no matching construction is supplied for D ≥ 3.

**The general constant is at most 1.** PR4248's count `2^n − 1 ≤ binom(cn + c − 1, c)`
and `binom(N, c) ≤ (eN/c)^c` give `2^n − 1 ≤ (e(n + 1))^c`, so
`n ≤ 1 + c log₂(e(n + 1))`. With PR6071's `n < 4c(⌈log₂ c⌉ + 1)` this is
`n ≤ (1 + O(log log c / log c)) c log₂ c`. So N(c)/(c log₂ c) has liminf at
least 1/2 (PR6071) and limsup at most 1. This sharpening of the counting
asymptotic is routine and is stated only to fix the interval.

The same lemma applied to a whole floor word (d = c, k = n) gives
`2^n − 1 ≤ n · min(n, c) · binom(cn + c − 2, c − 1)`. For n ≥ 2 this is
weaker than PR4248's counting bound `binom(cn + c − 1, c)`, because
`n · min(n, c) · c ≥ 2nc ≥ cn + c − 1`; the general constant 1 is untouched. The gain comes only when k is much smaller than c,
which is the regime of fixed-depth blocks.

## Capacity table

Exact evaluation of the largest k allowed (c = 2^e). "Trivial" is the
multiset count `2^k − 1 ≤ binom(kc + 1, 2)` for depth two. The ratios use
the D = 2 ceiling `c · max(2, K₂/2)` and PR6071's lower bound.

| c | Gray k | K₂ (this) | trivial depth two | K₃ | K₄ | lower / (c log₂ c) | depth ≤ 2 upper / (c log₂ c) |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2^8 | 9 | 21 | 24 | 35 | 49 | 0.5625 | 1.3125 |
| 2^16 | 17 | 30 | 41 | 54 | 76 | 0.5313 | 0.9375 |
| 2^32 | 33 | 48 | 75 | 88 | 128 | 0.5156 | 0.7500 |
| 2^64 | 65 | 83 | 141 | 156 | 228 | 0.5078 | 0.6484 |
| 2^128 | 129 | 149 | 271 | 287 | 425 | 0.5039 | 0.5820 |
| 2^1024 | 1025 | 1054 | 2069 | 2091 | 3127 | 0.5005 | 0.5146 |
| 2^4096 | 4097 | 4132 | 8217 | 8243 | 12353 | 0.5001 | 0.5044 |

The new depth-two cap is stronger than pair counting from c = 2^6 on.
Convergence to 1/2 is only logarithmic in log c. **At practical c the cap is
loose**: at c = 2^8 it allows 21 sources, against 9 from Gray and 8 from
PR6061's largest finite template, and the upper ratio is above 1. The table is an evaluation of the
proved inequality, not a search for blocks.

## Verification

`verify.py` is standard library only and writes no files.

- Source pin: the SHA256 of PR4248's README, the inherited definition.
- Exhaustive census of every floor word for (k, c) = (2, 2..5), (3, 2..4) and
  (4, 2): 39,288 words. For each word and each depth d ∈ {1, 2} (and d = 3
  when kc ≤ 9), every multiset of boundaries that represents a binary mask is
  checked against the weight identity, and for every fixed sub-multiset and
  weight the number of admissible last reads is checked to be at most k.
  1,031,591 identity checks pass. The census confirms that no three-source
  word has depth one (PR4248 Lemma C).
- Twenty-one reflected-Gray blocks (k = 1..7, three values of c each), built
  separately from PR6071's README statement, have depth two on literal
  words and satisfy the identity on every representing pair.
- The capacity table, the closed form `K₂ ≤ 1 + log₂ c + 3 log₂ K₂` at every
  tabulated c, and exact Fraction comparisons of both ratios at c = 2^4096
  (the printed table rounds them to six decimals).
- Four controls are rejected: a word with a missing call, the identity with
  the wrong modulus, PR6071's block with its downward suffix not reversed
  (loses depth two), and depth one on three sources at c = 3. The table
  itself is arithmetic on the proved inequality, not an independent check of
  the theorem.

Finite checks support the written proof; they do not establish the
all-parameter theorem, which rests on the proof above. No AI or human
proof-kernel review is claimed beyond the review noted in the PR.

## Scope, task and overlap

Base `721c03822c421b7f7fcbb2598993b947c4d88419`, priority revision 8. The
chooser drew `connector-alphabet-change` (seed
`9aa6e642b3ad1c5695053de603870c91`). **Scope changed**: the alphabet stays
fixed. This follows the general-family handoff in PR6071's open question 1
(sharp leading constant of N(c)/(c log₂ c)) and settles its depth-two part.
It is a local interface side result. It does not pass a supplier budget gate,
add a native consumer or change the selected record.

Nearest work, all crediting the retained connector lineage:

- PR4231/PR4248 (Nick Petalas): interface, floor, prefix criterion,
  concatenation/deletion, Lemma C (depth one carries at most two sources)
  and the counting upper bound. This package is the depth-d analogue of
  Lemma C. Pinned input: `research/connector-depth-blocks/README.md`.
- PR6035 (Nick Petalas, merged as `research/connector-five-halves-growth`),
  PR6057 (zxv), PR6061 (JosieElliston): finite depth-two blocks on five to
  eight sources.
- PR6071 (apoursh), head `a0f08278dd755e0bf228855e45c5efaa3b8ad97a`: the
  Gray-walk depth-two blocks and N(c) = Θ(c log c). Its open question 1 is
  the question addressed here. Pending; used for comparison and to rebuild
  its block in the verifier, not as an executable dependency.

The overlap search (`scripts/find_overlap.py --task connector-alphabet-change`,
live discussions and open PRs, searches for "leading constant" and Gray) found
no earlier upper bound on depth-two block size beyond pair counting. That is
not a novelty certificate.

## Open next questions

1. **Is there a depth-three block family with k ≈ 2 log₂ c?** It would raise
   the lower constant to 2/3, the most the theorem allows for depth three.
   *Why:* depth ≤ 2 blocks are now capped at 1/2, so this is the cheapest
   possible improvement of the lower constant. *First step:* search
   small c (8 to 32) for depth-three blocks with k > 2 + 2 log₂ c and look
   for structure among the first-read pairs that extend to a mask. Informal remark, not checked by the verifier: a Gray pair
   plus one extra read does not suffice, because the extra read's prefix must
   lie in {−1, 0, 1}^k mod c, and a monotone prefix chain has at most 4k + 1
   such values. *Blocked by:* no construction known.
2. **The general constant in [1/2, 1].** Concatenations of depth ≤ D blocks
   are capped at 1 − 1/D. Do words with unbounded block depth, or reads that
   cross block boundaries, beat 1/2? *First step:* sharpen the global count
   by also using the coordinate structure of each read, not only its weight.
3. **Exact depth-two capacity at small c.** The cap is loose at practical c
   (21 against 9 at c = 2^8). *First step:* exact search at c = 8..16 to see
   whether depth-two blocks beyond Gray plus O(log log c) exist; balanced
   Gray codes (Bhat–Savage) suggest about log₂ c + log₂ log₂ c is reachable.

## Credit

Prepared by JosieElliston with substantial Anthropic Claude (Claude Code,
session 40) assistance. Nick Petalas supplies PR4231/4248/6035 and the retained
Ross Richardson PR934/943 and Riquelme Soares lineage; apoursh's PR6071
supplies the Gray-walk construction and the open question; zxv's PR6057 and
PR6061 supply finite depth-two blocks. Reflected Gray codes and balanced Gray
codes are established combinatorics. Apache-2.0; no predecessor file changes.
