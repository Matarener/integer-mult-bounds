# Unsigned connector: depth-two blocks on six, seven and eight sources for large c

Take the unsigned dirty connector of
[#4231](https://github.com/CrocSwap/integer-mult-bounds/pull/4231) over a ring
of characteristic c, with k immutable sources and all 2^k − 1 nonzero
binary-mask outputs. Every legal word needs at least c(k + 2^k − 1) complete
calls, and N(c) is the largest k at which that floor is attained.
[#4248](https://github.com/CrocSwap/integer-mult-bounds/pull/4248) proved
N(c) ≥ 2c. Nick Petalas's
[#6035](https://github.com/CrocSwap/integer-mult-bounds/pull/6035)
(`research/connector-five-halves-growth`) gave a five-source depth-two block
in every c ≥ 5, so N(c) ≥ ⌊5c/2⌋. Its open question 1 asks whether any
characteristic has a depth-two block on six or more sources, valid for all
large c.

This package answers it for large c:

- **Theorem S.** There is a depth-two block on six sources in every
  characteristic c ≥ 8, on seven sources in every c ≥ 12, and on eight
  sources in every c ≥ 27.
- **Corollary.** N(c) ≥ k⌊c/2⌋ + 2(c mod 2) with k = 6 for c ≥ 8, k = 7 for
  c ≥ 12 and k = 8 for c ≥ 27.

So N(c) ≥ 3c for even c ≥ 8, N(c) ≥ 7c/2 for even c ≥ 12, and N(c) ≥ 4c for
even c ≥ 28.

The claims are a scoped proof with a finite core, checked by a stdlib
verifier. There is no new κ, no consumer, no selected-frontier change and no
multiplication theorem. For c = 5, 6, 7 the six-source question is still open
(search notes below). Characteristic four is untouched: #4271 excludes
five-source depth-two blocks there.

| c | #4248: 2c | #6035: ⌊5c/2⌋ | this package |
|---:|---:|---:|---:|
| 8 | 16 | 20 | **24** |
| 9 | 18 | 22 | **26** |
| 12 | 24 | 30 | **42** |
| 13 | 26 | 32 | **44** |
| 14 | 28 | 35 | **49** |
| 27 | 54 | 67 | **106** |
| 28 | 56 | 70 | **112** |

Every value satisfies #4248's counting condition C(ck + c − 1, c) ≥ 2^k − 1;
the verifier checks this for 8 ≤ c ≤ 128.

## 1. Interface and depth

These are #4248's, as restated in #6035. A floor word has a source walk w of
length ck that uses each source exactly c times. Let q_t ∈ (Z/c)^k count
source events modulo c after t steps. The word is correct exactly when every
nonzero mask m has readout boundaries t_1 ≤ … ≤ t_c with
q_(t_1) + … + q_(t_c) = m in (Z/c)^k. A walk has **depth d** if every nonzero
mask is a sum of at most d prefixes. #4248's concatenation lemma joins walks
on disjoint source sets whose depths sum to at most c into a floor walk;
spare readouts go to boundary 0. Its deletion lemma makes the attaining set
of k an initial segment.

## 2. Lifted templates with base multiplicity u

#6035 uses a base walk with each source six times. The same argument works
with any base multiplicity u. A **template** (k, u, W, a) is a walk W on k
sources, each used u times, with cut positions 0 ≤ a_j < u. Let n_t(j) be the
number of events of source j among the first t events of W. The lifted prefix
L_t ∈ Z^k has L_t(j) = n_t(j) if n_t(j) ≤ a_j, and n_t(j) − u otherwise.

**Template identity** (finite check). For every nonzero m ∈ {0,1}^k there are
base boundaries t_1 ≤ t_2 with L_(t_1) + L_(t_2) = m as integer vectors.

**Expansion.** For c ≥ u − 1, form W_c by replacing the (a_j + 1)-th event of
each source j with a run of c − u + 1 copies of j. At c = u − 1 that event is
deleted. Each source then occurs (u − 1) + (c − u + 1) = c times.

**Lemma.** If a template satisfies the identity, W_c has depth two on k
sources for every c ≥ u − 1.

*Proof* (#6035's, with 6 replaced by u). Let τ(t) be the boundary of W_c that
follows the first t events of W, after the whole run if event t was
expanded. If n_t(j) ≤ a_j, the count of source j at τ(t) is n_t(j) = L_t(j).
Otherwise it is n_t(j) − 1 + (c − u + 1) = n_t(j) + c − u, which is L_t(j)
modulo c. So q_(τ(t)) ≡ L_t (mod c), and t_1 ≤ t_2 gives τ(t_1) ≤ τ(t_2).
For a mask with L_(t_1) + L_(t_2) = m in Z^k, reduction modulo c gives
q_(τ(t_1)) + q_(τ(t_2)) = m. ∎

**Theorem S** follows from the three templates in
[CERTIFICATE.json](CERTIFICATE.json):

- k = 6, u = 9, a = (5, 4, 4, 4, 4, 5), a 54-event walk. Valid for c ≥ 8.
- k = 7, u = 13, a = (6, 7, 7, 6, 7, 6, 6), a 91-event walk. Valid for c ≥ 12.
- k = 8, u = 28, a = (12, 15, 12, 12, 11, 11, 14, 16), a 224-event walk.
  Valid for c ≥ 27.

The verifier checks the three identities (63, 127 and 255 masks) with integer
arithmetic. That is the only finite step the proof needs.

**Corollary.** Concatenate ⌊c/2⌋ copies of the k-source block on disjoint
source sets. For odd c, append #4248's depth-one block a b a^(c−1) b^(c−1) on
two more sources. The depths sum to at most c, so the concatenation lemma
gives a floor walk on k⌊c/2⌋ + 2(c mod 2) sources, and the deletion lemma
covers every smaller k.

## 3. What the verifier checks

[verify.py](verify.py) uses only the standard library, imports no
predecessor code and runs in about 3 s.

1. The three template identities, with integer arithmetic.
2. For every u − 1 ≤ c ≤ 64 (six and seven sources) and 27 ≤ c ≤ 40 (eight
   sources): W_c uses each source c times,
   every nonzero mask is a sum of two prefixes modulo c by direct search, and
   each lifted readout pair maps through τ to a correct readout. This is a
   control on the lemma, not part of the proof.
3. Eight literal floor words, simulated with generic coefficients over Z/c
   as in #4248: one and two six-source blocks at c = 8 (6 and 12 sources),
   two six-source blocks plus the pair block at c = 9 (14 sources), one and
   two seven-source blocks at c = 12 (7 and 14 sources, up to 196,764 calls),
   one seven-source block with the pair block at c = 13 (9 sources), and one
   eight-source block alone and with the pair block at c = 27 (8 and 10
   sources). Every output must equal its mask, the connector must return to
   its dirty value and every operator must be called exactly c times. The
   full-size corollary words (24 sources at c = 8, for instance, with
   2^24 − 1 outputs) are not simulated; they rest on the cited concatenation
   lemma, as in #6035.
4. The corollary table above, and #4248's counting condition for every
   8 ≤ c ≤ 128 (a consistency control).
5. Nine mutation controls must be rejected: the unexpanded six-source base
   walk read in characteristic 10, the c = 8 block read in characteristic 7,
   the c = 12 seven-source block read in characteristic 11 (83 of 127 masks),
   every cut moved one event later (all three templates), the six-source walk
   with base events 2 and 3 exchanged, five six-source blocks at c = 8
   (depth 10 > 8), and a floor word with one readout call dropped. The receipt
   is a fingerprint for comparing runs, not a pinned integrity check.

Expected marker:
`PASS_CONNECTOR_DEPTH_TWO_6_7_8 k6_every_c>=8 k7_every_c>=12 k8_every_c>=27 …`.
It also prints a receipt hash bound to all six package files.

## 4. Search notes (local only, not proofs)

The templates came from simulated annealing over base walks and cut vectors
under the integer criterion (score: number of covered masks). The search
programs and logs are not committed. On 8 cores, with 240–360 s per run:

- Positive control: k = 5, u = 6 is found in under 1 s in each of four runs,
  matching #6035. k = 5, u = 5 peaks at 28 of 31, matching #6035's report and
  the c = 4 obstruction of #4271.
- k = 6: found at u = 9, 10 and 12. Not found at u = 6 (52/63), 7 (59/63) or
  8 (62/63, four runs).
- k = 6 directly modulo c, each source c times: not found at c = 5 (52/63),
  6 (58/63) or 7 (62/63), two runs each.
- k = 7: found at u = 13 (twice), 14 and 16. Not found at u = 10 (115/127),
  11 (121/127) or 12 (124/127).
- k = 8: found at u = 28, 32 and 40. Not found at u = 20 (252/255) or
  24 (254/255).

These are search failures, not exclusions.

## 5. Reproduction

From the repository root, with CPython 3.12:

```sh
python3.12 -W error -B research/connector-depth-two-large-c/verify.py
python3.12 -O -W error -B research/connector-depth-two-large-c/verify.py
python3.12 -B scripts/research_package.py --package research/connector-depth-two-large-c
python3.12 -B scripts/check_research_commit.py --package research/connector-depth-two-large-c --check-source-history
```

## 6. Limitations

The result covers only the unsigned, immutable-source, complete-call interface
of #4231. It relies on #4248's prefix criterion, concatenation lemma and
deletion lemma, which are cited and not re-derived. Theorem S is proved for
every c ≥ 8 (six sources), c ≥ 12 (seven) and c ≥ 27 (eight). The direct
block check runs for c ≤ 64 (c ≤ 40 for eight sources), and literal floor
words only for the eight small cases above.
Fixed call prices must include their full implementation. Input admission,
coefficient preparation, dispatch and physical costs are additional and
unknown. No consumer is instantiated. Proof-kernel checks and independent
human review are not claimed.

## Open next questions

These are recorded with first steps in [TASK.json](TASK.json).

1. Do six-source depth-two blocks exist for c = 5, 6, 7, seven-source ones
   for 8 ≤ c ≤ 11, and eight-source ones for 12 ≤ c ≤ 26? Local annealing
   reached 62 of 63 masks at c = 7.
2. Is there a k-source depth-two block for every k once c is large? The
   minimum characteristic found so far grows quickly (8, 12, 27 for
   k = 6, 7, 8). Depth-two counting allows k up to about 2 log₂(kc). A family
   with k growing like a log c would give N(c) ≥ (a/2) c log c, matching the
   O(c log c) counting bound up to a constant and answering #6035's question 3
   (is N(c)/c unbounded?). A first step is k = 9 at larger base multiplicity,
   then an explicit recursive template.
3. Is there a depth-three block on more than 3k/2 sources, where k is the best
   depth-two size at the same c? This is #6035's question 2 in the new regime.
4. Does any concrete consumer use a characteristic-c batch at a favorable
   complete invoice? The abstract call counts change no supplier or κ.

## Credit

The lifted-template criterion, the expansion, the Theorem T proof that the
lemma above generalizes, and the open question are Nick Petalas's #6035. The
interface and lower bound are from #4231. The prefix criterion, depth notion,
concatenation and deletion lemmas, N(c) ≥ 2c, the depth-one pair block and the
generic simulator are from #4248 (with the deletion lemma of
[#4232](https://github.com/CrocSwap/integer-mult-bounds/pull/4232)). The c = 4
obstruction is #4271's. The verifier's word builder and simulator are adapted
from `research/connector-five-halves-growth/verify.py`. New work: the two
templates, the base-multiplicity generalization and the corollary, produced by
Claude Opus 5.5 (Anthropic) in an unattended session for JosieElliston.
Apache-2.0.
