# Staged entries on the other helpers of PR3734: none found that pays

PR3605 staged helpers 644 and 660 and PR3734 staged helper 544, each lowering one hosted width
from 8 to 7. This package asks whether the same mechanism lowers any other helper of PR3734's word,
from 9 to 8 or from 8 to 7, and whether it pays. **No new κ.**

## Result

On PR3734's word (both providers), no profitable staged width reduction was found:

- **The identity is not the obstacle.** An exact prefix identity exists for 25 width-8 helpers and
  for all 38 width-9 helpers whose blocking contacts are reads of the helper before its first producer.
- **With the other frames fixed, no construction exists.** The general form allows releases into any
  frame-compatible register, targets included. 9,862 (helper, raise, cut) cases were checked per
  provider, with no compatible identity. The same code, run on the parent words, rediscovers the three
  published staged entries: 544 on PR3682's word, and 644 and 660 on PR3133's word, with the same
  donors and coefficients.
- **With frames re-solved, only helper 472 becomes width 7.** Feasibility is checked by an exact
  minimal-assignment test. 472 is staged by `624 −= 472` and `628 −= 472/2` before its producer B538,
  with entrance `span(429,51)`. The word passes PR3734's frame bill, hygiene and full arbitrary-dirty
  semantics on both providers.
  - The frame cascade costs `Δbill {1:+15, 2:−9, 3:−2, 4:+2}` per call.
  - An exact dual certificate (2,551 patterns) shows that every owner fill of this inventory and bill,
    for any clock and any replica count, has its root below `0.0017305031`. The parent inventory's
    ceiling is `0.001730578437266246818740` (attained by PR3802 and PR3815). With these frames, 472's
    staged entry therefore lowers the reachable κ by at least `7.5e-8`.
  - In PR3862's width-unit terms, 472's signature saves at most `0.98619` of local cost per unit
    against an 8→7 price of `0.98774`, a net of `−0.00154` per unit. PR3734's signature
    `{1:+3, 2:+1, 3:−2}` nets `+0.00326`.
- **No width-9 helper can be staged, and no other width-8 helper either.** A width-9 helper must also
  leave the zero-frame compensation. For every placement tried, the exact test fails: a target leaves
  its port hyperplane, or exceeds its cut level.

**Why.** For 544, 644 and 660, the donors' next frames already contained the raised entrance. For
every other candidate, the producer's frame and the recipients' next frames meet only in the old
entrance. The new direction must therefore propagate, and it reaches either a target that excludes
it or a partner whose rank-2 climb it splits. For 472 it enters 624 and 628 before B999 and splits
the rank-2 climbs of 426, 433, 435 and 437. Among 313 active donors, {624, 628} is the only donor set
of size three or less, so the cascade is forced. A local frame optimiser on B, an A+B optimiser and
a retiming search (4,200 slots, run by a parallel session; local-only) recover nothing.

[FINDING.md](FINDING.md) gives the exact staged-entry condition, the census passes, the exactness
argument for the feasibility test, and the 472 analysis.

## Reproduction

```sh
python3.12 -B scripts/research_package.py --package research/staged-entry-census-3734
```

`verify.py` uses the standard library only and takes about 15 s. It rebuilds and audits the 472
word on both providers, with three controls (flipped release, releases after the producer, pure
retiming that is scalar-correct but frame-infeasible). It rebuilds 544, 644 and 660 on their
parent words, checks the exact certificate (tight to 1e-10, with the parent bracket and a perturbed
dual as controls), and authenticates and re-summarises the recorded census.

The census itself uses numpy 2.5.4 and scipy 1.18.1. It is recorded in `evidence/` with its commands
(`evidence/CENSUS.json`). `python3.12 -B research/staged-entry-census-3734/replay_subset.py` reruns
a subset in about 2.5 minutes and must reproduce the recorded rows: the three positive controls,
fixed frames for 457, 472 and 640, re-solved B windows for 472, and A windows for 461. It is not
registered, because float decisions may differ across BLAS builds. The full census took about 20 min
per provider for fixed frames, about 1 h on five cores for B windows and 12 min for A windows.

## Scope and limits

- The census samples cuts: 24 per helper plus the producer cut with fixed frames, and 5 or 6 per
  helper with re-solved frames, with at most 4 placements per release recipient. Infeasibility is
  proved per placement, not over all placements.
- Release vectors tried: greedy sparse strict solutions, an L1-weighted solution, a dense fallback and
  pure retimings. The exhaustive enumeration of donor sets of size three or less was run for 472 only.
- Fixed throughout: the other helpers' entrances and terminals, the prelude and the native warp maps.
  Joint staged entries are not searched, and the clock is not changed.
- Re-solved costs come from local optimisers, not an exact frame solver. The 472 certificate holds for
  the constructed frames. Neither optimiser (B frames; A and B frames) improves them. But the B
  optimiser, started from minimal frames, only recovers PR3734's own bill to within two rank-1 climbs,
  about 1e-7 in κ, which exceeds the 7.5e-8 gap. A cheaper frame assignment of the 472 scalar word is
  therefore not excluded.
- Against PR3945's 4→5 widening, with 472's cascade assumed unchanged on that word, the ideal ceiling
  also drops by `7.5e-8`. This is a float estimate from a local profile inferred from PR3945's
  published histogram; PR3945's words were not used.
- All of PR3734's conditional hypotheses are inherited. No selected-frontier change, no
  unconditional theorem and no formal proof is claimed.

## Open next questions

The three structured questions are in [TASK.json](TASK.json):

- **Joint staged entries.** Do two or more helpers staged together pay where single ones do not, as
  for 644 and 660 in PR3605?
- **Absorbing the cascade.** Can the partners' terminals or entrances take the 472 cascade, or does
  472 pay on PR3945's word?
- **Unsampled cuts.** The census samples cuts and placements; running every cut is a matter of compute.

## Sources and credit

Stacked on PR3734's head `fa041037a3374eaa08feeca0b26a5d6893194147`; only this directory is added. The
following are imported from PR3734's package, not copied, and their attribution is kept:

- `audit_core.py` and `audit_verify.py` (Sagar Thakrar, PR3687/3693): frame bill and semantics;
- `rational_price.py` (dataisfire);
- the words, and the parent words in `REPLAY-INPUTS.tar.gz`.

`code/ceiling.py` adapts PR3815's exact dual certificate (ChaloupeMusic) to a parameterised inventory.
The staged-entry mechanism is due to Ross Richardson (PR3605) and dataisfire (PR3734). The width-unit
prices are due to Sagar Thakrar (PR3862) and ToikY (PR3890).

Prepared by Erwan Secousses (ChaloupeMusic) with substantial assistance from Claude (Anthropic,
Claude Code). There is no independent human or formal review. Apache-2.0.
