# Four mixed affine targets need exactly ten paid calls

This contribution is produced by Nick Petalas. Claim type: scoped written
algebraic proof with finite exact corroboration. No new kappa.

Cinna Davis's [PR #1745](https://github.com/CrocSwap/integer-mult-bounds/pull/1745)
left the paid minimum for `diag(h,h^-1,tx,ty)` between eight and ten calls.
The exact minimum is **ten**, even with arbitrary free binary scalar mixing
and any finite number of restored dirty spectators. Here `h=aba tx` in
AGL_2(F2), and the only paid labels are `a,b,tx,ty` with binary rank-one
idempotent role couplings. All original inputs are arbitrary.

The [proof](PROOF.md) separates the paid alphabet. Forgetting translations
leaves two coordinate swaps, requiring six a/b calls. The homogeneous
translation block has rank four, requiring four tx/ty calls. Since these
letter classes are disjoint, the lower bounds add. The existing direct
word attains ten. The new contribution is the sharp lower bound and its
uniform dirty-workspace implication. The upper word and predecessor's
six/seven-call searches are credited, and their searches are not replayed.

## Evidence and reproduction

From the worktree root, using CPython 3.12 and only the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/affine-four-target-sharp-ten/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/affine-four-target-sharp-ten/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/affine-four-target-sharp-ten
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/affine-four-target-sharp-ten --check-source-history
```

Use another CPython 3.12 path on another machine. The direct marker is
`PASS_AFFINE_FOUR_TARGET_SHARP_TEN minimum=10 linear_floor=6 translation_floor=4`.
The checker prints a generated receipt bound to all package file hashes.
It writes no files and needs no Git, network, solver or predecessor code.
The registered manifest runs the normal and optimized commands separately.

The checker verifies all 576 affine quotient products, all 651 binary
rank-one idempotents through five roles with each of the four paid labels,
and both endpoint bounds through eight roles. Exact row-span enumeration
corroborates elimination on all 146 matrices in the declared small domains.
Nine full formal witnesses include scalar conjugations involving dirty
spectators. A separate set-valued faithful regular-action interpreter checks
all 1,344 original input basis columns across those witnesses. All ninety
single-paid-call omissions fail. Boundary controls cover invalid couplings,
extra labels, wrong h/h^-1 order, dirty leakage, invisible representation
kernels and the different charge of an added h label.

The universal result follows from the written rank inequalities, not from
finite circuit enumeration. Small proof representations never certify a
positive formal endpoint. The witness checker retains all 24 group-algebra
coefficients, and the second interpreter uses the faithful regular action.

## Scope, provenance and credit

Canonical base is `de5ec2e7a6074068452f45b1a191b5c72832df4a`, priority revision 8.
The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19217827)
proposed an eight/nine-call search. The first new step supplied a direct
proof excluding both lengths, so no solver search was needed. The
`connector-alphabet-change` card is marked changed in [TASK.json](TASK.json).
This is a mechanism-screening side result for a fixed restricted alphabet,
rather than an added operation or a supplier improvement. It identifies
that this particular target has no formal paid-call sharing headroom.

[SOURCES.json](SOURCES.json) pins the catalogue, selected record and
predecessor README as historical provenance. These are bibliographic inputs;
the standalone proof/checker consumes no predecessor executable or receipt.
No predecessor file, source archive or selected-frontier file is changed.

Credit Cinna Davis / 1337isnot1337 for PR #1745's target, exact alphabet,
open interval and direct word; Gareth Davidson / bitplane for PR #1333's
affine register framework; commdata2338 for PR #1414's two-swap minimum;
Adam Gall for PR #1941's related cut method; and eumemic, Ali Romman,
David Govea and the contributors retained in those sources for the register
lineage. Elementary block ranks, regular representations and subadditivity
are standard tools. The new separated bound and this package are produced
by Nick Petalas. Apache-2.0.

## Limitations and unrun obligations

The theorem requires exact formal group-algebra equality, a fixed linear
word, binary scalar mixing, the four stated paid labels, rank-one idempotent
couplings, and full restoration of arbitrary dirty spectators. It does not
cover larger paid alphabets, clean-only boundaries, erasure, nonlinear or
adaptive programs, or specialized nonfaithful address actions.

No native supplier, implementation tariff, frame/owner/hosting contract,
movement, stock, precision, tape bill, productive credit or complete recursive
invoice is supplied. No new multiplication exponent follows. The selected
cold replay, Lean, Docker and predecessor scientific suites were not run.
Independent human and formal proof-kernel review are unclaimed.

The code has no recursion and caps its role domain at eight and matrix
sizes at 256. All checked loops have fixed finite domains or at most twelve
instructions per witness. Python and its exact containers allocate dynamically;
this bounded managed-runtime verifier is not a fixed-allocation program.
Callback controls have an explicit finite target list. Warning-strict normal
and optimized execution supplies interpreter diagnostics. Whole-repository
lint and static typing are outside this isolated package.

## Open next questions

Can a concrete native operation justify adding one label that escapes the
separated charge? Begin with one explicit additional affine label and a
complete entrance/exit, scalar, frame, restoration and recursive invoice.
The h label demonstrates the mathematical change, but its native price is
unknown. A larger fixed-alphabet search on this same target cannot beat ten.
