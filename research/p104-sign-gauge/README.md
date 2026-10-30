# P104 sign propagation saves 974 scalar primitives per full call

**Finite complex-supplier circuit improvement; no new kappa.** On the accepted
PR5599 word, carrying whole-role signs across native frame moves and owned
lifetimes reduces the complete ordinary scalar allowance from **220232 to
219258**, including all **112 final sign restorations**. The caller's 18 full
invocations save 17532 real-component primitives. This is an exact tariff
comparison, not a measured runtime speedup.

| Quantity | Original | Replacement |
|---|---:|---:|
| Complete local events | 25475 | 25253 |
| SCALE events | 757 | 535 |
| Real scalar allowance | 220232 | 219258 |
| Paid native calls | 3447 | 3447 |
| Public inputs / productive helpers | 748 / 540 | 748 / 540 |
| Owned lifetimes / peak | 8 / 1 | 8 / 1 |

The literal MOVE itinerary, independent endpoints, helper targets, COPY/CLEAR,
ADD operand order and coefficient magnitudes remain identical. Every negative
nonunit SCALE retains its positive magnitude. The generated complete word is
[WORD.json.gz](WORD.json.gz); [RESULT.json](RESULT.json) is the exact receipt.
[PROOF.md](PROOF.md) derives the invariant, native-width rule and full cost.

## Reproduce

Python 3.12 and its standard library, from the repository root:

```sh
python3 -B scripts/research_package.py --package research/p104-sign-gauge
```

Expected: `PASS_P104_SIGN_GAUGE saved=974 full_calls_saved=17532
events=25475->25253 no_new_kappa` in normal and optimized modes, then
`PASS_REGISTERED_RESEARCH_PACKAGE`. Direct replay is also Git/network-free:

```sh
python3 -I -B research/p104-sign-gauge/verify.py
```

Direct replay requires this package plus the two source files named in
[VERIFY.json](VERIFY.json), preserving their repository-relative paths.
The normal command is read-only. Add `--write` to the direct command to
explicitly regenerate only this package's word and receipt. Verification
compares decompressed complete word data, not gzip container hashes.

The base is **df0137efd35e11b4445734bf612bdd4c7ebc330c**. The consumed source
is `research/p104-helper-subspace-splits/WORD.json.gz`, SHA256
`bbb072bced5824a8d9094c49be2fc51fbfdd05fb2b7dab8106e1275053075099`, from
Ali Romman's PR5599 at `09dd0965711ca7eeb169057a420abab1c9052137`.
The tariff is pinned to that package's `local.py`. [SOURCES.json](SOURCES.json)
binds actual Git blobs and hashes at the canonical base. Selected-record and
catalogue pins are historical provenance. No unmerged commit is required.

## Scope, checks and overlap

The sparse rational checker covers every aligned source cut and arbitrary
input row, and the dense integer/dyadic reverse check covers all **571536
endpoint coefficients**. Exact per-role scalar prefix envelopes are equal.
Chart/owned-state checks and six semantic rejection controls run every time.
[VALIDATION.md](VALIDATION.md) records additional portability and corruption
checks, with reused source-checker coverage identified separately.

OS assignment seed **34** selected the complex-supplier track. The three
candidates, preflight, stopping rule and bounded overlap survey are in
[CLAIM.md](CLAIM.md). No pinned sprint issue existed, so coordination is local.
The catalogue card is explicitly marked **changed scope**: this is an ordinary
scalar circuit result, not the card's changed recursive-profile gate. No
broader scan or optimality claim is made.

Ross Richardson's **PR919** and Scratch-net's **PR1153** already normalize
signs inside historical same-frame runs. This application carries signs
through the whole selected P104 word, explicitly treating native MOVE and
owned COPY/INIT/CLEAR. It credits their method and does not add historical
savings to this word's independently counted bill. Newer helper-retirement,
paid-basis and contact-rewrite work changes different objects and costs.

The paid and target histograms do not change; **selected kappa stays
0.00310045**. The five inherited framework assumptions remain. Native request itineraries
are compared unchanged, but recipes are not freshly replayed; full caller/admission,
rounded arithmetic, tape realization and production adoption are outside
this contribution. A finite certificate is not a full multiplication theorem.

## Open next questions

1. **Production adoption:** does the ordinary backend preserve exact sign
   negation on its reached signed grid without extra representation passes?
   This determines whether the scalar allowance saving becomes an implemented
   saving. Start by binding one actual negative SCALE and final correction to
   the retained backend. The concrete rounded/tape implementation is required.
2. **Changed words:** does the same compiler save work on a later P104 word?
   This matters only when that word is independently worth adopting. Run the
   deterministic transformation and its full checks on one pinned word; do not
   transfer this receipt or add predecessor savings. No new search is needed.

## Credit and license

Prepared for **Charan / theon199 with substantial OpenAI Codex assistance** in
analysis, code, verification and writing; no subagents or independent human
review. New work is Apache-2.0. [NOTICE](NOTICE) retains predecessor attribution.
Ali Romman supplies the selected split word, tariff and transpose-check method;
Pierre-Loic Doulcet, Joel Pulikkan, DreamingOfClouds, thu-nmrc, Gareth Davidson,
David Arias, Cinna Davis, Jacob Alan Sussman, zxv and Cao Yifan supply the
retained source/native/caller/compiler lineage. The existing source NOTICE and
all its earlier geometry, BIT and analytic credit remain intact.
