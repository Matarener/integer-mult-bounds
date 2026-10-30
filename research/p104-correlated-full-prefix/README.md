# A maximal correlated P104 entrance for the complete first prefix

The exact finite certificate gives index `2^868` in the Gaussian Newton lattice
B9 for the maximal source module admitting Y27=y, Y26=-y through all 2,025
prefix events. Its Gaussian elementary exponents 0 through 4 have multiplicities
`68,153,177,95,19`. The module still contains 4B9 with relative index `2^1180`.
[PROOF.md](PROOF.md) proves the necessary and sufficient congruence reduction;
[RESULT.json](RESULT.json) records the complete matrix digest and exact ranks.

This closes PR3449's noncone admission question for its fixed two-source family.
The old 257-event slice entrance has index `2^280`. The full-prefix module is
smaller by index `2^588`. An explicit nine-term slice-admitted source fails at
event 1190's additional D10 quarter read, with requested value `(-1+i)/2`.
A separate seven-term source outside 4B9 passes the complete prefix. These are
algebraic indices, not resource savings or a favorable complete supplier bill.

The statement covers scalar ADD products and completed coordinate C-factor
outputs, including their equality with literal signed-floor execution. It does
not assert that each individual floor half equals division by two. Other Y
inputs may independently lie in 4B9, N inputs in 2B9 and the other initial
public fields in B9. Physical preparation of this entrance remains open.
No supplier, new kappa or selected-frontier change is claimed.

## Reproduce

Python 3.12 and the standard library suffice. From the repository root:

```sh
python3.12 -W error -B scripts/research_package.py --package research/p104-correlated-full-prefix
python3.12 -O -W error -B research/p104-correlated-full-prefix/verify.py
python3.12 -O -W error -B research/p104-correlated-full-prefix/independent.py
python3.12 -O -W error -B research/p104-correlated-full-prefix/fixtures.py
python3.12 -O -W error -B research/p104-correlated-full-prefix/test_controls.py
```

For local temporary CLI fixtures, set TMPDIR to an owned external directory.
Default replay leaves scientific files unchanged. `verify.py --emit` and
`fixtures.py --emit` print receipts without writing files.

The primary reconstructs every column on B9's 512 Gaussian basis generators.
It checks all 42 active C-factor/addend checkpoints and removes 18 identically
zero congruence blocks. The 24 retained blocks have 12,288 Gaussian rows.
The secondary imports no primary or predecessor executable. It uses forward
dependency sets, direct integer butterflies and a separate subgroup-order
algorithm, and must match the complete matrix digest and all four images.
Both algorithms pass all 256 small Z/4 matrix cases. All 256 small Gaussian
pair residues and actual optimized Git-free acceptance, Boolean-receipt,
corrupt-source and missing-source CLI controls pass.

The separate physical fixture executes all 2,040 events through the first
collector, with a nonzero dirty product baseline and an admitted correlation
outside 4B9. It checks exact scalar products, every native C factor and strict
zero private erasure; an altered cleanup sign fails. This fixture supplements
the universal congruence argument and does not supply a recursive child price.

Standalone replay needs this package and the two declared files in
`research/p104-rounded-collector/inputs/`. Their canonical-main hashes are in
SOURCES.json. Retained predecessor proof texts are in this PR's own history;
inputs/ORIGINS.json records their byte hashes and source paths. No unmerged
predecessor commit is a runtime dependency. Registered replay additionally
validates Git provenance. Publication checks are:

```sh
python3.12 -W error -B scripts/check_research_commit.py --package research/p104-correlated-full-prefix --check-source-history
python3.12 -W error -B scripts/export_research_package.py export --package research/p104-correlated-full-prefix --output OWNED_DIR/source.tar
python3.12 -W error -B scripts/export_research_package.py check OWNED_DIR/source.tar
ruff check --no-cache --line-length 100 --select E,F,B,PLE,PLW,RUF research/p104-correlated-full-prefix
```

## Open next questions

Can a real caller prepare a source in this full-prefix module and afford its
noncone consumers? Start with the explicit 24 congruences and the seven-term
admitted source, then bind the initial source ownership and the six nonzero
recipient outputs to actual call histories. Complete preparation, routing,
restoration, finite-width and consumer costs are blockers. An algebraic index
must not be entered as a free saving. The family expansion gate and the
unchanged-profile supplier stop remain.

Can a changed complete word preserve a cheaper caller entrance? Start with an
explicit changed source/recipient contract and rederive its complete matrix
and invoice. The rest of the 5,398-event word, arbitrary multi-source
correlations and tensor depth are outside this result. Clear1nsight's concurrent
[58-bank cone classification and encoder claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/2750#discussioncomment-19009685)
is a separate scope; none of its provisional claims is a premise here.

## Scope and credit

Scientific base is canonical main `6f100d4bb5083f8c35d96fd95a539811c62f245c`,
priority revision 6. The [canonical investigation](https://github.com/CrocSwap/integer-mult-bounds/discussions/2750#discussioncomment-19009899)
records the distinct full-prefix claim. TASK.json retains the original
`p104-side-correction` card and explicit scope change.

Credit Nick Petalas/PR3449, PR3426, PR3406 and PR3416; Clear1nsight/PR3382 and
PR3423; ywz65/PR2586; Arham Tahir/PR2665; Tekalign/PR3025; Ross Richardson/PR3068;
and the retained native, geometry and compiler lineage. engine.py adapts the
bounded Gaussian arithmetic from PR3449. Original proof bytes and notices are
unchanged. Nick Petalas. Apache-2.0.

The retained Newton-alphabet and native/physical semantics remain explicit
predecessor premises. Actual preparation, physical ownership/routing,
restoration, a favorable full supplier bill, other source correlations,
all-depth/all-size transfer, independent human/formal review, Lean, Docker,
selected cold replay and hosted-CI acceptance are unclaimed. Engineering
constraints and exact verification boundaries are in [ENGINEERING.md](ENGINEERING.md).
