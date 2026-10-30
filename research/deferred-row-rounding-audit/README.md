# Audit the numerical boundary of deferred-row deletion

**Scoped proof and concrete counterexample; No new κ.** This checks one
precision implication at the completed-row boundary inherited by selected
PR6030 and retained explicitly in concurrent PR6115. It does not allege a bug
in the selected implementation: the selected finite-template source keeps a
fixed fine grid and says that children are never rounded at return.

For an implementation with declared numerical defects, final row deletion is
a norm-one projection. Internal defects in a row destined for deletion can
still reach retained data before that boundary. [PROOF.md](PROOF.md) gives a
sharp suffix-matrix error bound, a deferred-phase composition rule, and the
source's required `2^g` scaling for raw H recovery. Physical deletion and
owned erasure remain separate obligations.

## Exact result

The four-shear word in PROOF.md is exactly identity on arbitrary retained and
temporary inputs. Rounding its temporary value `1/2` to zero at one internal
cut produces **retained error 2**. The sole rounding error has size `1/2`.
This falsifies the shortcut that an internal error is harmless merely because
its row will eventually be deleted, and an endpoint-norm-only error allowance.
The retained amplification can be arbitrarily large in the stated family.

Conversely, a defect only in a completed discarded row has no retained effect.
For one explicit internal channel, keeping discarded output rows in the error
norm overstates retained error by exactly **4097**. This is a channel-specific
comparison, not a precision improvement for a complete supplier.

The complete finite deferred fixture has a **sharp normalized defect-box bound
1**, and **raw bound 4**, for six noise sites with coordinate defects at most
`1/8`. The verifier constructs attaining defects. Under a particular nonlinear
nearest-even quantizer, all **6,561** inputs in `{-1/4,0,1/4}^8` have normalized
error at most **3/16** (raw **3/4**). The box bound is sharp for independent
bounded defects; it is not claimed optimal for that quantizer.

A further exact control shows that omitting the final cleanup shear preserves
the retained output while violating the full padded endpoint. A retained-only
comparison therefore cannot certify clean return. The checker verifies both
the full 12×12 phase and the final 8×8 retained operator.

## Reproduce

CPython 3.12, standard library only, from the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/deferred-row-rounding-audit
```

Expected: normal and optimized runs print `PASS_DEFERRED_ROW_ROUNDING_AUDIT`,
and both private-copy fault suites print `PASS_ROW_ROUNDING_MUTATIONS`.
The registered replay takes seconds. It changes no source or expected file.

The fixed completed coverage is:

- All 144 coefficients of the padded phase and all 64 of the retained map,
  compared with an independent closed Walsh formula for the latter.
- Exact rational suffix matrices at all six noise sites, with an attaining
  forward execution for the sharp box bound.
- All 6,561 nonlinear ternary-cube inputs through a separate integer-only
  quantizer; 81 distributed cases cross-checked against dense Fraction
  execution. Seed 66 selects the cross-check slice.
- 1,300 exact arbitrary-input echo/channel cases, plus the literal rounding
  counterexample and completed-residual/omitted-cleanup controls.
- Ten actual private-copy mutations rejected in each Python mode; unchanged
  and restored private copies pass. Faults cover source drift, omitted cleanup,
  wrong deletion, premature clearing, ignored padded-input defects, omitted
  recovery scaling, wrong rounding and missing expected evidence.

No Monte Carlo or floating point is used. This is a finite corroboration of
the written conditional proof, not formal verification of all implementations.
The small program intentionally includes temporary cross-row mixing. It is
an explicit numerical-interface surrogate, not an emitted PR6030 child,
native circuit, compact-control geometry or priced physical program.

## Sources, overlap and the one pivot

Exact canonical base: `721c03822c421b7f7fcbb2598993b947c4d88419`, priority
revision 8. The selected result is `781451/250000000 = 0.003125804`, PR6030;
its original audited head is `772dd10a5859a1d15f4851feb371519789213ad8` and
the retained portability repair is `746ee5e1160ae64a15a81b2a432d5566142db850`.
All consumed files have Git-blob and SHA256 pins in [SOURCES.json](SOURCES.json).
The checker authenticates the support/closure/outer files against the selected
manifest and follows the selected certificate. No source verifier is imported.

The actual selected support note is the archived PR1673 copy beneath
`research/kappa-observation-integration/release-work/current/package/vendor/pr1673/`.
The later main-tree copy has additional T74 wording; its coefficients are not
transferred here. The selected `FINITE-TEMPLATE-CLOSURE.md` fixed-grid sentence
is checked explicitly so this hypothetical rounding contract cannot be
misreported as a defect in that exact program.

OS assignment seed **66**, adversarial audit. The original local claim took
PR6110's open cost-transfer question, head
`7f82486e987e556a221085092d8f7aff271ecb35`. During the prepublication refresh,
DLamdata's [PR6115](https://github.com/CrocSwap/integer-mult-bounds/pull/6115),
head `643891684cf7890e22f4256ae22ae441040d10cd`, supplied that cost audit,
including the current BIT-stock specialization. The duplicate draft was
preserved locally and withdrawn from this contribution. The single pivot
was to the numerical row-deletion boundary left separate by PR6115.

This result is distinct from PR6115's weighted recursion/stock proof and
PR6109/6110's outer-row mapping. It imports none of their executable code.
JoyboyBrian's PR5081, head `4c49fff7fdfa4ddda6ef615575b6762b3f46f9cd`, already
audits a computed-input nonlinear error recurrence at a different, actual
Tensor compression caller. That general principle is not new here. This
package's added scope is the deferred-row defect channels, sharp projected
coefficient, and retained-versus-clean-return counterexample; it supplies no
new actual Tensor or PR6030 physical replay.
The standard telescoping-error and norm arguments are credited as standard;
the contribution is the scoped row-interface audit, sharp channels and
reproducible failure controls. [TASK.json](TASK.json) records the three original
candidates, scope change and stopping rule.

The overlap helper had sparse local coverage (13/8,348 note records) and no
remote cache because `gh` was absent. Live connector PR searches and direct
Discussion 1163/1166/1167 reads supplemented it. The only open issue was
unrelated issue 913, and the available connector has no Discussion-posting
operation, so the authorized local-claim fallback was used. Historical diffs,
all sparse notes and unpublished work were not exhaustively searched. Final
source/overlap checkpoints and executed checks are in [VALIDATION.md](VALIDATION.md).

## Scope

The proof assumes correct exact linear operations, specified rounding-defect
bounds on reached inputs, sufficient numerical range, exact placement and
retained-coordinate selection. It does not grant free reversible deletion,
change the selected fixed-grid design, derive actual native precision, or
discharge any of the five selected framework assumptions. No selected cold
replay, native census, proof kernel or independent human review is claimed.

## Open next questions

1. Bind the suffix-error calculation to one actual emitted child/row boundary.
   Start with a complete event list including exposure, all temporary-row
   reads, restoration and deletion. The missing emitted physical program and
   its gate error/range contracts are the blockers.
2. Price the exact retained-row projection and disposal under the owned-erasure
   and fixed-tape contracts. A norm-one mathematical projection alone supplies
   no physical erasure protocol or cost reduction.

## Attribution

Prepared by **@CubeJerry with substantial OpenAI Codex assistance** in proof,
implementation, adversarial review and writing. The two finite implementations
have the same assisted author; no delegated agents or independent human review.

Credit Vlado Vojdanovski (PR1673 support-local/deferred construction), zxv and
the finite-template/outer-transfer authors, DreamingOfClouds and Ali Romman's
P104 lineage, Douglas Colkitt's application review, JosieElliston's PR6110
handoff, DLamdata's concurrent PR6115 cost audit, and all retained source
attribution. Credit JoyboyBrian's PR5081 computed-domain error audit as related
prior work. New work is Apache-2.0. Upstream and frozen sources are unchanged.
