# Unsigned connectors attain their call floor on Θ(c log c) sources

In the unchanged unsigned dirty-connector interface of
[PR4231](https://github.com/CrocSwap/integer-mult-bounds/pull/4231), let N(c)
be the largest source count attaining the complete-call floor in characteristic
c ≥ 2. This package proves the explicit lower bound

```text
b(c) = 1 + floor(log₂ c),
N(c) ≥ b(c) floor(c/2) + 2(c mod 2).
```

Together with the counting upper bound of
[PR4248](https://github.com/CrocSwap/integer-mult-bounds/pull/4248), this gives
**N(c) = Θ(c log c)**. In particular N(c)/c is unbounded. The new ingredient
is a constructive depth-two block for every k ≥ 1 and c ≥ max(2, 2^(k−1)),
obtained from a binary reflected Gray path. The proof below covers all these
parameters; finite replay supports its implementation.

This answers [PR6035](https://github.com/CrocSwap/integer-mult-bounds/pull/6035)
open question 3 and the general-family handoff in
[PR6061](https://github.com/CrocSwap/integer-mult-bounds/pull/6061) open question 2.
It is a scoped connector theorem, with no new κ or selected-frontier change.

## Exact interface and floor

Let R be any nonzero unital ring of characteristic c ≥ 2. There are n immutable
source rows x_j, one arbitrary borrowed dirty row z, and arbitrary dirty output
rows y_m for every nonempty binary mask m on the sources. Compatible R-linear
maps B_j and A_m are arbitrary. The permitted complete calls are only

```text
B_j: z   += B_j x_j
A_m: y_m += A_m z.
```

Each call restores its private scratch and heads, preserves all other rows,
and acts independently of its old target. Coefficients remain immutable and
outputs are unobserved until completion. The required action is
`y_m += sum_(j in m) A_m B_j x_j`, with x_j and z unchanged. No signed calls,
scalings, extra connectors, direct products, free copies or source updates are
introduced. In particular the downward flips used to DESIGN the walk below
are not downward or inverse executable calls.

Identity specialization, as in PR4231, forces each B_j and A_m to appear a
positive multiple of c times. Thus every universal word costs at least
`c(n + 2^n − 1)` complete calls. A floor word calls every operator exactly c
times. Project such a word onto its cn source calls and let q_t be their integer
prefix-count vector, including q_0 = 0. Calling A_m at c boundaries is correct
exactly when the sum of their q_t vectors is m modulo c. Repeated boundaries
are allowed; boundary zero supplies padding. This criterion uses additivity,
not invertibility of the maps, commutativity between A and B, or primality of c.

A depth-d block uses each of its sources c times and represents every binary
mask as a sum of at most d source prefixes modulo c. Concatenating disjoint
blocks adds their depths because each completed block has prefix zero modulo c.
These are PR4248's prefix and concatenation lemmas; their proofs also follow
immediately from the displayed criterion.

## A covering-walk construction

**Lemma.** Suppose g_0,...,g_L is a finite walk in {0,1}^k, starts at zero,
visits every mask, and changes exactly one coordinate at each step. Repeated
vertices are allowed. Let f_j be the total flips of coordinate j. If c ≥ 2 and
f_j ≤ c for every j, there is an explicit depth-two block on these k sources.

**Proof.** Let A be the subsequence of upward-flip labels, and B the subsequence
of downward-flip labels, both in their original order. For time t, let U_j(t)
and D_j(t) count upward and downward flips of coordinate j so far. Then
`U(t) − D(t) = g_t`. Write u(t) = sum_j U_j(t) and d(t) = sum_j D_j(t).
Form the unsigned source word

```text
W = A · (0^(c−f_0) 1^(c−f_1) ... (k−1)^(c−f_(k−1))) · reverse(B).
```

Every exponent is nonnegative and every source occurs exactly c times. Let M
be the middle word. Two actual source boundaries are

```text
a(t) = u(t),          s(t) = kc − d(t).
```

They obey `0 ≤ a(t) ≤ |A| ≤ |A|+|M| ≤ s(t) ≤ kc`. The prefix at a(t) has
count vector U(t). At s(t), the unexecuted suffix consists of the reversal of
the first d(t) downward labels in B, so its count vector is D(t). Consequently

```text
q_a(t) = U(t),       q_s(t) = c·1 − D(t),
q_a(t) + q_s(t) = c·1 + g_t ≡ g_t (mod c).
```

This proves the claim for every visited mask. Use its first visit if it occurs
repeatedly. The zero mask can instead use the empty list of reads. Both
boundaries are chronological, even if they coincide. All executable events
are positive source calls. ∎

**Gray specialization.** For integers 0 ≤ i < 2^k set `g_i = i xor (i >> 1)`.
This lists every mask once: the map on k-bit vectors is triangular with unit
diagonal, hence invertible. Transition i−1 to i flips coordinate v₂(i), so
coordinate j flips exactly `2^(k−1−j)` times. The largest flip count is
`2^(k−1)`. The lemma therefore gives a depth-two block whenever
`c ≥ max(2, 2^(k−1))`. This is the classical reflected Gray path; Gray codes
themselves are not claimed new.

For example, at k=3 and c=4 the Gray labels are `0,1,0,2,0,1,0`, giving
`A=0,1,2,0`, `B=0,1,0` and
`W=0,1,2,0,1,1,2,2,2,0,1,0`. Its twelve events contain each source four times,
and the lemma gives all seven nonzero masks using two prefixes each.

## Growth theorem and complete words

Set b = b(c). Concatenate floor(c/2) disjoint b-source Gray blocks. For odd c,
append PR4248's depth-one two-source block
`a b a^(c−1) b^(c−1)`: prefixes at boundaries 1, 2 and c+1 represent a, a+b
and b respectively. The total depth is at most c. For each nonzero global mask,
select the reads for its nonzero block masks, then pad to exactly c reads at
boundary zero. Sort reads chronologically and interleave the corresponding A_m
calls with the source word. Different output calls preserve z and can share a
boundary. The resulting word has exactly

```text
n = b floor(c/2) + 2(c mod 2) sources,
cn source calls and c(2^n − 1) output calls.
```

The connector returns to z_0 since each B_j appears c times. Each output gains
`c A_m z_0 + sum_j m_j A_m B_j x_j`, with the first term zero. Arbitrary initial
y_m is preserved additively. This proves the floor bound for arbitrary compatible
maps over R, including composite characteristic and singular noncommuting maps.
The argument is constructive, but constructing all 2^n−1 output schedules is
exponential in n. Large examples below are evaluations of a proved formula,
not full-word simulations.

Deleting source events and retaining only masks on the surviving sources
preserves the prefix identities and exactly c calls per remaining operator.
Thus attainable source counts form an initial segment, as in PR4248.

For completeness, the inherited counting argument gives an explicit finite
upper bound. A floor word has at most cn distinct prefix vectors modulo c
(the initial and final boundaries coincide). There are at most
`binom(cn+c−1,c)` multisets of c such vectors, so floor attainment requires

```text
2^n − 1 ≤ binom(cn+c−1,c).
```

Put m=ceil(log₂ c) and n₀=4c(m+1). The elementary inequality
`c! ≥ (c/3)^c` follows by induction from `(1+1/c)^c < 3` (bound its binomial
expansion by `sum_(j≥0) 1/j! < 3`). Hence

```text
binom(cn₀+c−1,c) < [3(n₀+1)]^c,
3(n₀+1) = 12c(m+1)+3 ≤ 16c(m+1)
          ≤ 16·2^m·2^m = 2^(2m+4) ≤ 2^(4m+3) = 2^(n₀/c−1).
```

Here m≥1 and m+1≤2^m. Therefore the count is less than
`2^(n₀−c) < 2^n₀−1`, excluding n₀; deletion excludes all larger n too.
Consequently

```text
b(c) floor(c/2) + 2(c mod 2) ≤ N(c) < 4c(ceil(log₂ c)+1).
```

This proves Θ(c log c) and `liminf N(c)/(c log₂ c) ≥ 1/2`, without asserting
an optimal leading constant.

The finite templates in PR6035 and PR6061 remain stronger at small c. In
particular PR6061 reaches six, seven and eight sources at c≥8, 12 and 27,
whereas the corresponding reflected-Gray thresholds are 32, 64 and 128.
Retain the maximum of established bounds when comparing pointwise values:

| c | PR6061 eight-source lower bound | This construction |
|---:|---:|---:|
| 256 | 1,024 | 1,152 |
| 257 | 1,026 | 1,154 |
| 512 | 2,048 | 2,560 |
| 1,024 | 4,096 | 5,632 |

## Cost and outstanding supplier obligations

With positive fixed complete-call prices p_Bj and p_Am, the map-call bill is
exactly `c(sum_j p_Bj + sum_m p_Am)`, attaining PR4231's lower bound in that
pricing model. A conditional full caller bill remains

```text
I + sum_F P_F + D_W + c(sum_j p_Bj(L) + sum_m p_Am(L)).
```

I pays input admission and layout; P_F pays reusable coefficient preparation;
D_W pays schedule construction/storage, instruction reads and dispatch.
Every p_F must include source/coefficient access, arithmetic, target update,
private scratch restoration, head returns and frames. These costs are not set
to zero. The required n source rows, 2^n−1 output rows and one dirty connector
also need a concrete admitted layout. No physical prices, native consumer,
transfer schedule, supplier recurrence or favorable complete multiplication
invoice are supplied. The local algebra and call counts are proved; those
integration obligations remain open. The selected κ stays 0.003125804.

## Task, provenance and overlap

Base: `721c03822c421b7f7fcbb2598993b947c4d88419`, priority revision 8.
The original `connector-alphabet-change` card is retained in [TASK.json](TASK.json).
Scope is **changed**: the alphabet stays fixed. This follows the released
all-size-family handoff rather than another fixed-k search, and resolves the
asymptotic capacity gap between linear constructions and the counting bound.
It is a local interface side result, not passage of the family-level supplier
budget gate. The card's orientation control passed unchanged:
`PASS_UNIVERSAL_CONNECTOR_BOUNDARY pairings=945 max_coverage=31 queries=74 leaves=182`.
The selected baseline's binding check passed; its full cold replay was not run
because this package changes no selected construction or shared code.

Canonical coordination:
[claim and result](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19233477).
Live handoffs, recent PRs and all-state Gray/connector and N(c)/log searches
were checked. The offline helper searched only 11 of 8,348 HEAD notes, with no
usable remote cache; that incomplete coverage is not evidence of novelty.
The live comparison found:

- PR4231 and PR4248: exact interface, floor, prefix/deletion/concatenation and
  counting lemmas; pinned canonical READMEs in [SOURCES.json](SOURCES.json).
- PR6035, head `119de1d7fca5124fa8d01ea49d258560aca618e6`: five-source lifted
  template and the unbounded-ratio question; canonical README pinned.
- PR6061, head `babc5e99421403284fa530e9f135b618f31805bb`: stronger finite-size
  thresholds and the explicit all-k handoff; motivation/comparison only.
- [PR6057](https://github.com/CrocSwap/integer-mult-bounds/pull/6057), head
  `f92bd41f60564175bd68f944e9d6450da8965734`: parallel six-source construction;
  motivation/comparison only.
- [PR5372](https://github.com/CrocSwap/integer-mult-bounds/pull/5372) uses a
  clean helper row and Gray ordering; [PR1185](https://github.com/CrocSwap/integer-mult-bounds/pull/1185)
  treats characteristic-two one-root connector optima and general Gray upper
  bounds, with source multiplicities not constrained to c each. Their contracts
  and results differ from this characteristic-dependent growth theorem.

No pending-PR bytes or predecessor executable code are required. The direct
verifier checks the exact SHA256 of the three declared canonical README inputs;
the registered metadata check additionally validates historical Git provenance.

## Reproduction and evidence

From the repository root with Python 3.12 (standard library only):

```sh
python3.12 -I -W error -B research/connector-gray-growth/verify.py
python3.12 -I -O -W error -B research/connector-gray-growth/verify.py
python3.12 -B scripts/research_package.py --package research/connector-gray-growth
python3.12 -B scripts/check_research_commit.py --package research/connector-gray-growth --check-source-history --check-modes
```

`construct.py` provides the covering-walk and reflected-Gray constructors,
block composition and literal complete-call iterator. `independent.py` uses a
separate recursive Gray construction and literal 2×2 matrix execution over Z/c.
`verify.py` binds sources and audits the production implementation, including
all target masks in the small composed examples. All local modules are loaded
from source bytes; verification writes no files and needs no Git or network.
Finite replay does not prove the all-parameter theorem; that proof is above.

On CPython 3.12.14 / macOS arm64, normal and optimized direct runs agree
(about 0.9 seconds each). The production audit covers 36 blocks with k=1..12
at c=max(2,2^(k−1)), that threshold plus 1, and plus 7: 24,534 nonzero masks
and 135,798 source events. It also checks 14 repeated/backtracking covering
walks, five complete compositions for c=2..6 (847 outputs, 4,778 literal calls),
and the first counting failure for every c=2..128 (92,001 comparisons).
The separate implementation covers 27 blocks and five compositions with
52,682 literal calls. Its recursion gives a second Gray-path implementation;
its grouped-boundary interpreter differs from execution of the production
call iterator.

All 27 combined controls are rejected: they include malformed/under-capacity
walks, incorrect prefix witnesses, an unreversed downward suffix, source-count
corruption, dropped source/output calls, padding moved to a nonzero prefix,
and an over-depth composition. Guards and semantic controls are distinguished
in the verifier; every check stays active under `-O`. The counting transcript
SHA256 is `35d273c15d655535a3016e226a4c8295dd2db44cca3ae5e47acfbfc00e9e3e76`.
These counts describe bounded tests, not exhaustive coverage of all c or maps.
Independent Codex proof/code checks are AI-assisted reviews, not independent
human or proof-kernel verification. No native multiplication replay is claimed.

## Open next questions

Structured versions are in [TASK.json](TASK.json).

1. What is the sharp leading constant of N(c)/(c log₂ c)? This construction
   gives at least 1/2. First sharpen the counting asymptotic and look for
   depth-two blocks near its `k ≈ 2 log₂ c` capacity. The present Gray split
   only certifies `k ≈ log₂ c`; no matching construction or upper constant
   is proved here.
2. Can a concrete characteristic-c consumer use these larger batches at a
   favorable complete invoice? First specify its immutable-source interface
   and price I, P_F, D_W and every complete primitive, including output layout.
   No such consumer or price schedule is currently supplied; source capacity
   alone cannot settle this question.

## Credit

Prepared by **apoursh** with substantial OpenAI Codex assistance, including
separate construction, literal-execution and mathematical-audit agents.
Nick Petalas supplies PR4231/4248/6035 and their retained Ross Richardson
PR934/943 and Riquelme Soares lineage. JosieElliston's PR6061 supplies the
finite-block progress and explicit general-family handoff; zxv's PR6057 is
parallel finite-block work. Classical reflected Gray codes are established
combinatorics. This package adds their upward/reversed-downward realization
in the unchanged unsigned connector contract and the resulting growth theorem.
Predecessor attribution and frozen bytes are preserved. Apache-2.0.
