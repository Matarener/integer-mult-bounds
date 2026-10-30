# Paired-stage loss at m = 4 under the chronology cut is exactly 10

**Finite certificate, scoped to a necessary-condition model. No new κ.**

In the binary normalized paired-stage controller of
[PR #5631](https://github.com/CrocSwap/integer-mult-bounds/pull/5631), take
m = 4 stages (n = 6 fields, L = 8 calls). Impose the earlier rank and pairing
conditions together with PR #5631's mixed chronology coefficient (*). Then every
query system, chronological order, stage pairing and compatible projector
choice has loss

    D = 4m - sum_c rank E_c >= 10,

and 10 is attained. The earlier bound at this size was D >= 2. Stage targets
can keep at most 6 of the 16 possible ranks.

PR #5631 asks whether a constant-loss family can satisfy chronology at all
sizes. This answers the first open size. It does not decide the asymptotic
question. See [PROOF.md](PROOF.md) for the model, the reduction lemmas and the
controls.

## Census

| | Gram systems |
|---|---:|
| all query Gram systems at L = 8 (every order) | 35,008 |
| no assignment satisfies the conditions | 23,564 |
| minimum D = 10 | 2,400 |
| minimum D = 12 | 4,760 |
| minimum D = 14 | 3,084 |
| minimum D = 16 | 1,200 |

The census is exhaustive over three things. First, it covers every Gram matrix
K = (v_i u_j). Equal K means the systems are conjugate. Second, it covers every
compatible rank-two projector u b + a v for each call. Third, it covers all 105
pairings, with every pairwise-commuting choice of stage targets. A reversal
symmetry halves the work, and the histogram is reweighted by orbit size.

Controls:

- At m = 3 the same code finds D = 0, so the search is not vacuous.
- An optimal m = 4 word, with stage ranks 0, 0, 2 and 4, passes PR #5631's own
  `chronology.mixed` routine unchanged.
- Exchanging that word's first two calls makes the routine report a defect.

Locally, a second implementation in NumPy, without the orbit reduction,
reproduced the full histogram. A sample with (*) removed gave minimum D of
4 to 6 on 11 of 12 random systems, so the cut is what raises the loss to 10.
Those two runs are local evidence and are not registered.

## Limits

These are necessary conditions. Passing them does not make a caller: other word
coefficients, native realization, restoration and price are unchecked. The
model has no thin calls, no idle maps, separate ports and characteristic two.
The result moves no price exclusion. PR #5631 already rejects m <= 47 using
D >= 2. No m = 5 census and no all-size lemma is claimed.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
~/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/paired-stage-chronology-m4
# or directly:
python3.12 -B research/paired-stage-chronology-m4/verify.py                       # witness and controls, < 5 s
python3.12 -O -B research/paired-stage-chronology-m4/verify.py --shard K --shards 7  # K = 0..6
```

Each shard checks about 2,500 orbit representatives against its histogram and SHA256
in [RESULT.json](RESULT.json). A shard takes about 130 CPU seconds, or about
35 s of wall time with four processes. `--jobs` sets the process count.
The verifier imports the pinned `research/paired-stage-chronology-cut/chronology.py`
unchanged; its hash is in [SOURCES.json](SOURCES.json).

## Open next questions

1. **Does the loss grow with m?** If D grows linearly, PR #5631's argument
   excludes every paired-stage size at κ >= 0.003. The first step is an m = 5
   census, or a paired analogue of Cinna Davis's minimum-query
   private-projector lemma that bounds the number of rank-four stages. The
   blocker is size: n = 8 gives 2^13 projectors per call, so pure enumeration
   needs a structural reduction.
2. **Why is the rank sum at most 6?** Classifying the 2,400 optimal systems
   and their rank patterns could give a proof that generalizes.

Structured versions are in [TASK.json](TASK.json).

## Credit

Model, mixed coefficient cut and `chronology.mixed`: Ali Romman (PR #5631),
building on PR #5617, Cinna Davis's private-projector lemma, and the P104
source contributors credited there. The m = 4 census, reduction lemmas and
verifier were produced by Nick Petalas. Apache-2.0.
