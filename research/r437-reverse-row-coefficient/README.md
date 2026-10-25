# r437-reverse-row-coefficient

**Partial finite certificate. No new κ. Selected κ stays 0.001672660197076918.**

## Result

On the PR #4067 two-window R437 carrier, the cancellation-free row-l1 coefficient is unchanged in the forward direction and strictly larger in reverse:

| Orientation | Composed word | Candidate phases | Delta |
|---|---:|---:|---:|
| Forward row-l1 | 49347 | 49347 | 0 |
| Reverse row-l1 | 1113998 | 1123650 | +9652 |
| Scalar ADDs | 24208 | 24211 | +3 |
| Forward children | 2915 | 2915 | 0 |

The norm rule starts each of the 659 data registers at 1 and the copy buffer at 0. Each scalar ADD applies `norm[d] += norm[s]`. A forward open copies the opened register into the buffer; a forward close clears it. Reverse swaps those two copy operations and walks the record list backward. Moves do not change norms. The coefficient is the maximum norm attained.

Both words share the maximizing reverse ADD: register 158 adds register 223, and the source norm at that ADD stays 8689. The destination already holds the whole +9652 before that ADD. Both coefficients have bit length 21 (`2^20 = 1048576`, and neither integer is a power of two). A 21-bit width cap still covers 1123650. The composed-word integer 1113998 does not.

The published PR #4067 `price()` builds its moment from the rank profile and the bad-event surcharge `32*64*64*E/10^16`. It does not read row-l1. This replay checks that the forward child count E stays 2915, so that surcharge term is the same number for both words. The local moment improvement therefore leaves the reverse precision coefficient unpaid. This package does not re-execute `host.py` or rebuild the 288-call schedule. The published global ADD increase 864 equals `3 * 288` only after that external call count; the certificate here is the per-word increase of three scalar ADDs.

## Scope

Task card `uniform-transfer-audit`, priority revision 6, base `bb4bccbf42844d2801487450727c2f63e10d1d0f`. Scope status is **refined**: one precision implication for this finite carrier, not an all-size or compiler theorem. The original card is copied verbatim in [TASK.json](TASK.json).

Item 12 of the chronological open handoff list on Discussion #1166, after dropping items already delivered or covered by an open PR through #4126. The concrete piece is open question 2 of PR #4067, the bounded coefficient half of the obligation named from Discussion #1166 comment 19040062. The pooled catalogue regeneration remains open and is not this result.

Ordered eligible list used for that cut:

1. Invoice-level audit of composed T488 literal ownership (comment 19022532 Q1).
2. Priced physical rank-8/u2 source and consumer contract (comment 19029639).
3. Payload subspace and injective encoder for the integer-shear image (comment 19032401).
4. Independent review of the #3942 interaction reduction (comment 19032637 task 1).
5. One adjacent completed-call pair for the P104 two-axis gate (comment 19034066).
6. One row/column pair with fiber tags `z⊗q_j` and `r_i⊗z` (comment 19034676).
7. One changed P104 caller with a compatible literal encoding (comment 19034741).
8. Caller fusing source normalization with the joint interface (comment 19035513).
9. One physical K/adjoint/frame boundary and its tag price (comment 19036235).
10. Many-axis prime producer at the encoded caller boundary (comment 19037887).
11. q2 event 58 target-local gap (comment 19039339).
12. This package: reverse row coefficient of the PR #4067 carrier.

## Inputs

`inputs/R437-COMPOSED-WORD.json.gz` has SHA-256 `e432182d5b62c8bbefeb871fce30317234d707e5e18d4295e65ac21f7fd8365e`. `inputs/CANDIDATE-PHASES.json.gz` has SHA-256 `47c092cf409ac09c4386e5e59ea539d7406f65f746ddcf62a595353507c16607`. Both byte strings were copied from PR #4067 head `a95f11c52e3ca1e4c5171b3c20d8f4b0815aee2e` on Clear1nsight/integer-mult-bounds. They are not Git objects at this package base, so [SOURCES.json](SOURCES.json) pins only the selected record and the task catalogue. `verify.py` checks the two SHA-256 values before walking. The candidate word is the composed word with phases A, B, C and D replaced.

## Reproduce

From the repository root, Python 3.12, standard library only:

```sh
python3 scripts/research_package.py --package research/r437-reverse-row-coefficient --check-only
python3.12 -B scripts/research_package.py --package research/r437-reverse-row-coefficient
```

Direct checks:

```sh
python3 -B research/r437-reverse-row-coefficient/verify.py
python3 -B research/r437-reverse-row-coefficient/independent.py
python3 -B research/r437-reverse-row-coefficient/test_verify.py
```

`independent.py` rebuilds records with numeric opcodes and does not import `verify.py`. `test_verify.py` checks a two-register synthetic orientation (forward 4, reverse 5), rejects feeding the composed word in as the candidate, and duplicates the peak ADD `158 += 223`, which moves the reverse coefficient from 1123650 to 1132339.

Not run: Lean, Docker, the selected cold replay, hosted CI, `host.py`, and the pooled compiler.

## Open next questions

1. Regenerate the replica-indexed pooled source codebook and native requests for this exact word, then price the complete physical caller. The extra reverse coefficient and the three scalar ADDs are caller inputs. Start from the PR #4067 candidate template and the early SOURCE 87 move. Blocker: the compiler is outside this package, and frozen request identifiers are not transferable.

2. Name one charged precision or stock envelope and test whether its reverse allowance is at least 1123650. An envelope with at least 9652 of slack above 1113998 can still cover the candidate. This package shows that the bare integer 1113998 does not, and that the published moment bracket ignores row-l1. Blocker: no named slack-bearing envelope is an input here.

## Credit

The two-window carrier, the stated coefficients 1113998 and 1123650, and the host moment bracket are from Chris R / Clear1nsight, PR #4067, with the lineage that package credits: ai-nanachi / PR #3647 for R437, Ali Romman / PR #1043 for the SOURCE 77 carrier, Sagar Thakrar / PR #3700 and PR #2423 for OQ4, and Rohan Arun for pooled context. This package rederives the row-l1 identity and the coverage comparison; it does not replace that host receipt.

New checks and this note by unpaidmoon, with substantial Cursor Grok 4.7 assistance. Apache-2.0. No independent human review and no formal-kernel acceptance are claimed.
