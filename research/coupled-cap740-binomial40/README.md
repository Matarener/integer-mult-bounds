# Binomial certification of a tiny T740 endpoint refinement

This keeps PR3148's complete coupled T740 construction and improves its
conditional multiplication saving over PR3361 by about **3.609 × 10^-36**:

    kappa = 0.001729777494678597011886903656817803609 - 10^-62 - 10^-86.

The change is only certified rounding slack. It is not a cheaper word, a
runtime speedup, or a selected-frontier update. The 40-digit endpoint was
already contained in PR3361's published root bracket; this package supplies
a separately implemented positive-binomial enclosure and finer outer release.
The full rational, exact comparison and complete generated inequalities are
in `CLAIM.json` and `RESULT.json`.

## Reproduction

From the repository root, with Python 3.12 or later and standard library only:

```sh
python3 -B research/coupled-cap740-binomial40/verify.py
python3 -B research/coupled-cap740-binomial40/test_controls.py
python3.12 -B scripts/research_package.py --package research/coupled-cap740-binomial40
```

The verifier authenticates all live sources, compares the full regenerated
result against the frozen certificate, and writes no package files. Optional
`--output PATH` writes a fresh result and refuses an existing file.
`SOURCES.json` records PR3361's original head, path, Git blob and SHA-256.
The identical vendored claim is pinned to this branch's first commit, so replay
does not require that pending package or its Git objects to be installed. The registered replay reuses
source-bound finite/native evidence. It is not the complete cold replay.

For the unchanged supplier's full fresh reproduction, use its documented
`research/coupled-carrier-cap740/FETCH.txt` and isolated dependencies, then:

```sh
nice -n 15 ionice -c 3 env OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
  python3 -B research/coupled-carrier-cap740/reproduce.py \
  --repo . --work /tmp/t740-fresh-unused --jobs 2
```

`VALIDATION.json` records this session's actual completed and outstanding
checks separately; neither stored receipts nor CI status stand in for them.
`COLD-REPLAY.md` records the original controller timeout and the unchanged
full release continuation, without conflating their exit statuses.

## What is checked

The new fixed-point positive-binomial engine uses no log/exp implementation
from the retained checkers. Its positive remainder bound, directed rounding,
and exact square-root calibration are described in `PROOF.md`. All three
engines accept C and reject C+10^-40. Added unpaid children also reject.
The unchanged modern outer engines derive K and pass 63 strict inequalities
and 17 rejection controls. The retained bootstrap passes its 47 rows and four
controls. The full source-bound baseline receipt checker retains ten controls.
Actual subprocess tests reject disabled assertions, altered public claims,
altered result certificates and missing source pins; a copied package replay
leaves all package bytes unchanged.

## Comparison and scope

- Main base: `6f100d4bb5083f8c35d96fd95a539811c62f245c`; reviewed selected
  saving remains `0.001672660197076918`.
- Supplier: Jeremy Diviney's PR3148,
  `f2927a4b8afcf0701a6b945e14f30de1d94f5176`, on dcharb78's PR3133,
  `51eb9c4ee9e4722010d308aa3309e039d3940cc2`.
- Exact comparator: dataisfire's PR3361,
  `f9de2024916a347d939ed256a7a2e9e68d633684`.
- Larger donation-overlay headlines inherit the published PR3187/3296
  operator objections. The session rechecked current PR3251
  `3ffd42b3ee1c1841b4ab355dc1f6ee1f5740f9d6`: all six owner-0/port-0 moves
  together change ten operator entries at character 2^72. This is a binding
  of the credited existing counterexample, not a new operator theorem.

PR3148 and PR3361 are archived on main as of
`20ecf2891d80b5acf18d980b2164fb44ea7faa90`. Archive acceptance is not
mathematical validation. Both are conditional
contributor constructions, distinct from the maintainer-reviewed selected record. The same 663,549 physical
families, 91 private buffers, 2,717,280 owner rows and 1,479/2,048 prefix
charge are retained. All-size/compiler, physical common-label/mutable-source
realization, whole-call hosting, precision/tape, exact recovery, analytic
transfer and BIT H1-H5 remain assumptions. Uniform compiler coefficients/stock,
physical rational SCALAR/COPY/CLEAR and zero-allocation contracts are not
established by this finite replay. No complete formal multiplication
theorem, human review or maintainer acceptance is claimed.

The session's bounded circuit searches found no profile improvement; see
`EXPERIMENTS.json` for their exact scope and local artifact hashes. They are
not global impossibility claims or additional supplier admission.

## Open next questions

1. Can a joint B-warp/consumer redesign remove the PR3133 double-cone lock
   without restoring the saved cost elsewhere? First specify one exact
   arbitrary-dirty interface and its full frame/consumer bill. Fixed-word
   packing is already at its cap; another owner seed cannot answer this.
2. Can the actual uniform physical caller obligations for the rank-seven
   construction be discharged? Follow the live PR3342/3385/3442 work rather
   than treating finite source/native evidence as a complete all-size proof.
3. Independent human review of the supplier and modern transfer remains
   valuable. Additional decimal digits alone do not provide that coverage.

## Credit

Positive-binomial enclosures are established repository practice, including
0x-chad's [PR678](https://github.com/CrocSwap/integer-mult-bounds/pull/678),
davidNbreslauer's [PR960](https://github.com/CrocSwap/integer-mult-bounds/pull/960),
steph4n-gh's [PR1052](https://github.com/CrocSwap/integer-mult-bounds/pull/1052),
ToikY's [PR2943](https://github.com/CrocSwap/integer-mult-bounds/pull/2943), and
RossRichardson's [PR2974](https://github.com/CrocSwap/integer-mult-bounds/pull/2974).
This implementation imports none of those engines and claims no priority for
the technique. Its scope is the explicit T740 endpoint and outer release.

SovereignSteak, with substantial OpenAI Codex assistance, supplies the new
binomial implementation and scoped refinement. Retained credit: dataisfire
(PR3361 reuse/precision recipe); Jeremy Diviney (PR3148 allocation/full
release); dcharb78 (PR3133 coupled folds); Marius-Paul Dumitrean, Nick Petalas,
Jeremy Kothe, Mason Hale, Yiyang Lu, Dugongue, Tekalign, icekylinx and the
retained supplier lineage; Arham Tahir and Sagar Thakrar's independent audits;
Gonzalo Mier's precision precedents; Vlado Vojdanovski, Chafik Boukhalfa and
the credited gauge-free/union/outer authors; Tim Trudgian's cited prime result;
DreamingOfClouds and eumemic's BIT supplier. Existing notices remain in their
original packages; the reused PR3361 notice is retained in `vendor/`.
New files are Apache-2.0.
