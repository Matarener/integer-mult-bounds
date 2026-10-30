# A P104 helper split using different input and output bases

This package improves the complete conditional exponent saving from
**0.00310915222 to 0.00311024570**, building on Ali Romman's
[PR5713](https://github.com/CrocSwap/integer-mult-bounds/pull/5713), head
`a5348f7143f95fe0046b92b96172e30763c7d731`.
The increase is 0.00000109348, approximately 0.0352% over that source.
This is a modest improvement; the selected frontier is unchanged.

The initial helper basis can use main inputs at zero-dimensional frames.
Those inputs have arbitrary values: they are not initialized zeros. An actual
coframed relation later restores the old helper and permits a new independent
helper to take its place. A different, legal output combination restores the
remaining fields. Requiring the same combination at both boundaries would
miss this split. The construction adds no paid recursive transport.

## Complete cost

For `H_r = r^(1-kappa)`, one local call changes the signed invoice by

```
paid:          unchanged
targets:       +H2 +H7 -H9
targets-paid:  H2 +H7 -H9 > 0.
```

Strict subadditivity proves the positive gain for `0 < kappa < 1`. All added
ordinary work is separately funded. The complete caller uses eighteen LOCALs.

| Quantity | Verified value |
|---|---:|
| Conditional kappa | 0.00311024570 |
| Strict raw crossing enclosure | (0.00311024572012, 0.00311024572013) |
| Complete paid jobs | 66,348 |
| Complete productive fields | 12,976 |
| Complete rank surplus | 760 |
| Local independent inputs / owned labels | 744 / 9 |
| Local owned lifetimes / peak simultaneous | 11 / 2 |
| Distinct native maps checked | 2,917 |
| Local scalar / routing allowance | 221,474 / 5,166,000 |

Original helper708 retires at rank two. New helper743 starts there and follows
the original continuation to rank nine. All nine owned identifiers shift by
one, without a new lifetime. The 25,546-instruction word contains 89 initial
basis additions, one retirement addition and three cleanup additions. At the
cleanup contact, the exact current146 value replaces a 118-term terminal
functional; the proof verifies both its version and the required order.

## Reproduction and checks

```sh
python3 -B scripts/research_package.py --package research/p104-two-boundary-helper-split
python3 -B scripts/check_research_commit.py --package research/p104-two-boundary-helper-split --check-source-history
```

Expected marker: `PASS_P104_TWO_BOUNDARY_SPLIT_KAPPA_00311024570`.
The registered normal and optimized commands check the exact construction,
all 753 arbitrary-input columns, separate dense transpose, actual binary
coframes and owned intervals, every native map and absolute phase, and the
complete physical caller. The price replay uses two exact moment engines,
compiler completion and all 54 strict plus four functional outer predicates.
Complete WORD, WITNESS and RESULT payloads are compared; compression container
bytes are not used as mathematical equality.

Ten actual instruction/boundary mutations are rejected, covering missing or
wrong retirement/cleanup, reversed cleanup order, the obsolete fresh decoder,
wrong helper boundaries and an omitted owned-identifier shift. Two further
invoice controls reject an unpaid query and an invented target. Inherited
caller, phase, cutoff and BIT controls remain active. See [PROOF.md](PROOF.md).

Separate agents derived the input basis and output correction, verified the
exact intermediate146 value, and replayed all scalar columns and ownership
without importing the constructor. Compact receipts are retained in `evidence/`.
The final caller-audit and publication checks are reported in
[VALIDATION.md](VALIDATION.md). Independent AI checks are not independent human
or formal mathematical acceptance.

## Source custody, credit and limits

Main provenance is `df0137efd35e11b4445734bf612bdd4c7ebc330c`.
The exact 21-file PR5713 export is authenticated before source imports; all
nested source checks remain active. Git-history metadata binds the archive
retained in this branch; `archived_files` separately preserves its exact
origin-head and payload pins. Replay needs no cached pending-PR Git objects. The complete price adapter differs only
by the explicit substitutions in `PRICING-EDITS.json`. Frozen predecessors and
shared framework files are unchanged.

Credit Ali Romman's PR5713 temporal update and predecessor proofs, Joel
Pulikkan/GamingPuzzled's PR5684, the retained helper-split constructions, and
the caller, native and pricing authors listed in NOTICE. Chris R/Clear1nsight's
PR5550 and the maintainer's PR5599 review supply the separate caller lineage.
The elementary linear basis identities are standard; the contribution is this
source-specific construction, legal schedule and complete invoice. Prepared
for flyingviper with substantial OpenAI Codex assistance, including separate
verification and literature agents. Apache-2.0.

The native all-width, owned erasure, compiler, precision/tape and
analytic/recovery assumptions remain. COPY is an ADD into an ideally initialized
owned zero with numerical residuals retained. No complete rounded multiplier
or huge uniform word is materialized. This package claims neither a large gain,
a general optimality result, nor admission to the selected frontier.

## Open next questions

- Independently inspect the two boundary functionals and early cleanup order;
  both matter to the endpoint identity.
- Find another pair of legal boundary functionals at an actual coframed cut,
  with the complete native, helper and ordinary bill included.
- Audit one remaining source-specific framework assumption before promoting
  a complete supplier into the selected result.

Concrete first steps and blockers are recorded in `TASK.json`.
