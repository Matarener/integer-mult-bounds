# Independent audit of the PR4100 free-word tensor lift

**Positive scoped audit; no new κ.** The four actual PR4088 programs satisfy
their complete 723-register shear contracts in the rational free group algebra
on their 72 unary generators. Their termwise specialization therefore preserves
the endpoint for every positive tensor multiplicity. The tensor-lift proposal,
source programs and original symbolic engine are predecessor work; this result
adds a separately written exact checker, independent assessment and failure
controls for that specific implication.

The [proof](PROOF.md) keeps scalar coefficients fixed and maps each unary word
to its tensor power. In particular `G-I` maps to `G^{⊗f}-I`; tensorizing the
whole difference or a scalar-weighted operator would be incorrect. The 723
register roles stay fixed while their internal vector space changes. All 91
private dirty buffers are independent inputs in the formal certificate.

## Evidence and limits

- [INDEPENDENT.json](INDEPENDENT.json): no retained evaluator imported; all
  723 output functionals, both orientations, all four THREE/FOUR base/extra
  programs: 5,784 checks, 6,680 nonzero endpoint terms, zero surviving nonempty
  operator words. Only adjacent inverse letters cancel.
- [RESULT.json](RESULT.json): authenticated retained forward/dual/reverse and
  cleanup-boundary checks, plus 24 noncommuting F101 tensor specializations.
- [INDEPENDENT-REAL.json](INDEPENDENT-REAL.json): a separate Codex agent's
  exact-rational signed-permutation implementation, 24 concrete dirty-input
  specializations at multiplicities 1, 2 and 3, with scalar/phase controls.
- [MUTATIONS.json](MUTATIONS.json): erasing actual correction G59 yields
  output115 error `(I-G59)x273`; dropping SCALE119(-1/2) yields output119
  error `-3*x119`. Baseline output functionals pass before each mutation.
- [Independent review](INDEPENDENT-REVIEW.md): source interpretation, proof,
  event ordering and native interface limits. All agents are AI; no independent
  human acceptance or formal-kernel theorem is claimed.

The formal computation proves the finite identity in a universal algebra. The
written representation argument supplies the quantifier over all positive
multiplicities. Finite numerical specializations are supplemental controls.
Native realization and recipe receipts, physical placement, common cover,
precision, fixed-tape costs, analytic assembly, recovery and the complete
multiplication theorem remain outside this audit. No new supplier, paid profile,
outer admission or selected-frontier change is claimed.

## Sources and reproduction

Base: canonical main `12fa8c5c844be21bfefb38a19503fbd867a11244`, priority 7.
Audited proposal: PR4100 `337d04939571a637aeab54a0f58f54fde811663a`.
Literal programs: PR4088 `72d7efc181edb21806a878f174847c96dd410ab0`.
[SOURCES.json](SOURCES.json) binds original paths through the base commit;
[SOURCE-PINS.json](SOURCE-PINS.json) binds ten minimal byte-identical exports,
their original commits, Git blobs, SHA256 hashes and lengths. The direct
checkers authenticate those exports before use. No full predecessor package is
copied, and no network, native runner or third-party Python dependency is needed.

From the repository root, using Python 3.12:

```sh
python3.12 -B scripts/research_package.py --package research/free-word-tensor-lift-audit --check-only
python3.12 -B scripts/research_package.py --package research/free-word-tensor-lift-audit
```

The eight registered commands replay the three implementations and the actual-program mutation controls normally and with
optimization. The last oracle prints its deterministic JSON receipt; compare it
with `INDEPENDENT-REAL.json`. Package/source integrity checks authenticate bytes
and metadata, not mathematical acceptance. The selected baseline orientation
command stopped because this sparse checkout omits its `ASSEMBLY.json`; this
package does not claim a fresh selected-supplier or historical outer replay.

## Open next questions

Does the actual native recipe/frame and rank-child interface realize this
specialization on the physical caller with a complete cost invoice? This matters
because the algebra alone does not implement a legal native supplier. Start by
reusing pinned phase-sensitive native recipe and finite admission evidence
(including PR4180 where applicable). Identify the uncovered tensor/frame/child
coordinate interface, then audit its placement and complete charged caller.
This is a distinct review; it is not discharged here. See [TASK.json](TASK.json)
for the structured scope, stop rule and remaining obligation.

## Credit

Prepared for ToikY with substantial OpenAI Codex assistance. Cinna Davis's
PR4100 supplies the tensor-lift argument and PR4088 supplies the literal providers.
The retained engine/audit credits Sagar Thakrar (PR3687) and roger-sato (PR3693).
The byte-identical [source notice](source/NOTICE.md) retains the wider native,
geometry, compiler, owner and staged-provider lineage. The proof and review
distinguish reused work from this audit. New material is Apache-2.0.
