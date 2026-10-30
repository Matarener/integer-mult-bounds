# QQ16 paired recovery: range and rounding audit of PR4106

**The800-unit scalar allowance saving survives in a common sufficient finite
format.** For every lambda>=1, t=lambda-1, both frozen words admit component
quantum `q=h2^(-9-3t)` and signed width `W=P+28+6t`, provided borrowed entry
components lie in hZ with magnitude<2^P h. No extra candidate width is required
for the specified exact pair-first numerical reference. This is a uniform
sufficient-format comparison, not an optimal-width or recursive supplier claim.

| Quantity | PR4015 baseline | PR4106 candidate |
|---|---:|---:|
| Logical scalar allowance |26944|26144|
| Unit ADD sites |1920|1820|
| Explicit numeric primitive bill per owner |(12352+2240lambda)N|(12152+2240lambda)N|
| Sufficient signed component bits |P+28+6t|P+28+6t|
| Sufficient component quantum |h2^(-9-3t)|h2^(-9-3t)|

Here N=2^(73lambda) complex coordinates per owner. The numeric reference includes
Gaussian interiors, shifts, zero stores, monomial signs, out-and-back permutation
copies and a buffer. It saves200N real additions, a different unit from800 logical
allowance. Physical addressing, movement/placement, actual recursive workspace,
usage and supplier caps remain unpriced.

Two independent all-depth magnitude representations certify the result. Their
largest envelope is171043<2^18, including new shared-sum intermediates. A separate
error interpreter gives identical224 endpoint error polynomials for both words,
without assuming independent rounding errors. Under exact non-overflowing common
grid additions and deterministic isolated callbacks, the fixed-point queries and
outputs are relatively bit-identical. Floating significand rounding can differ:
a literal query-cut example yields Q0=4 versus6 at precision2. That example does
not claim full rounded-caller reachability.

Read [PROOF.md](PROOF.md) for the main argument and scope, with separate
[range](range-proof.md), [rounding](rounding-proof.md) and [cost](cost-proof.md)
notes. [RESULT.json](RESULT.json) contains the conclusion, fixed-word structural
binding and remaining premises. [SOURCES.json](SOURCES.json) pins five canonical
semantic/proof inputs plus historical provenance; [PREDECESSORS.json](PREDECESSORS.json)
pins the retained PR4106/4015 words, construction and proofs. No predecessor
executable is imported. Endpoint/frame correctness is inherited from those proofs;
this package replays numerical obligations on the whole frozen schedules.

From the repository root:

```sh
python3 -B scripts/research_package.py --package research/qq16-paired-precision --check-only
python3.12 -B scripts/research_package.py --package research/qq16-paired-precision
```

The registered commands include type-sensitive whole-receipt comparison,
source-first authentication, meaningful corruption controls and normal/optimized
Git-free read-only replay. Success is `PASS_QQ16_PAIRED_PRECISION_CONDITIONAL`.
Tests and AI adversarial review support the stated proof; they are not formal or
human certification. Earlier source package proofs and selected kappa are not
cold-replayed here.

## Open next questions

The next viable step is a single actual recursive native/caller contract: pin its
entry lattice/range, output error versus width, native interiors, private return
and tariff/layout. The proof supplies a91101 B2^(3t) logical-cut error margin and
an explicit width-tariff break-even threshold. Neither a real selected supplier
connection nor its physical bill has been supplied, so no new kappa is claimed.
The source-selected value remains836330098538459/500000000000000000.

Credit: PR3985 native reduction; PR4015 streaming/hosting; PR4106 scalar pairing;
PR4003 residual; ywz65/#2707, Arham Tahir/#2681, Ali Romman and retained native
lineage; NickPetalas/#3303 producer grid; ToikY/#3652 independent review;
Tekalign/tekuuu/#4030 distinct frame gate. New audit by Chris R / Clear1nsight
with substantial OpenAI Codex assistance. New work Apache-2.0; retained notices
and attribution remain in vendor proofs. See TASK.json for the assigned scope,
family gate, overlap limits and agent responsibilities.
