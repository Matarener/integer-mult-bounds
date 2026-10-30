# All-size integral synthetic-transform identities

This package gives an explicit coefficient-path proof of the retained exact
synthetic transform and extends its integral scaled-inverse identity to every
commutative coefficient ring. For a nonempty finite list of axis powers
2<=t_i<=r dividing r=2^ell, and every address-bit permutation L preserving records,
the unnormalized operators satisfy

    U_- = L B W_-,     U_+ = W_+ B^-1 L^-1,
    U_+ U_- = U_- U_+ = M I,     M=product_i t_i.

B reverses frequency bits within each axis. W_± have entries
`y^(±sum_i (2r/t_i)j_i k_i)` in `R[y]/(y^r+1)`. If 2 is a unit, dividing
each operator by M gives normalized composite `I/M`. A characteristic-two
control shows why the integral identity alone does not imply invertibility.
The boundary is sharp: either integral operator is invertible exactly when
2 is a unit in the coefficient ring. Its determinant is a signed monomial
unit times `2^(M log2(M)/2)`. An explicit nonzero residue kernel proves the
obstruction without assuming the coefficient ring is a field.
The proof also establishes the retained mixed-long/short exact-K slot formula
and common-offset chunk admission for every finite permitted shape and K.

The original source already proves the complex identities. The earlier
[layout audit](../synthetic-layout-independent/README.md) independently checks
finite matrices and explicitly excludes an all-size theorem. This contribution
adds a direct all-size corroboration and integral base-change statement, with
no field or root-evaluation assumption. It reports no source defect or new
transform algorithm. [PROOF.md](PROOF.md) states all hypotheses and the exact
one-path calculation; its universal claim does not come from finite tests.

## Reproduction and evidence

Use Python 3.12, standard library only, from the repository root:

```sh
python3.12 -I -Werror -B research/synthetic-allsize-identity/verify.py
python3.12 -I -Werror -B research/synthetic-allsize-identity/test_controls.py
python3.12 -B scripts/research_package.py --package research/synthetic-allsize-identity
python3 -B scripts/check_research_commit.py --package research/synthetic-allsize-identity --check-source-history
```

Set TMPDIR to an existing private external directory for the CLI controls.
`verify.py --write-receipt PATH` regenerates the finite receipt to an explicit
path for comparison. Direct verifiers also run from a Git-free committed export
containing the four declared canonical inputs.

RESULT.json records 349,524 coefficient paths, 1,980 layouts and 13,020 common
chunk rounds. It checks 450 complete ring-module columns across 29 shapes,
both integral scaled inverses, and base change to Z/2, Z/4, Z/9 and Z/15.
Normalized composition is checked over the two odd composite rings. Controls
also test 116 nonzero kernels over Z/2, Z/4, Z/6 and Z/10. Other controls
change inverse signs/order, named-slot reading, layout restoration, negacyclic
signs and normalization. The real optimized CLI rejects changed or missing
source bytes and altered receipt coverage. ENGINEERING.md gives bounds and
retained-code limits. These checks support the written proof; they are not
proof-kernel verification.

This settles an exact-algebra audit implication used by
[PR2298's outer proof](../selected-conservative-outer/PROOF.md). It does not
supply Q_p between rounds, a production native/ordinary/hosting refinement,
physical tape restoration or cost, a complete outer round, supplier admission,
or an improved integer kappa. The selected frontier is unchanged. Independent
human and formal proof-kernel review are unclaimed.

## Open next questions

Connect a reviewed production root to one completed outer synthetic round with
its actual Q_p boundary, named-slot descriptors, borrowed tapes and complete
movement invoice. PR3493's explicit dimension and signed-format adapters are a
starting point. Production premises and impractical constants remain blockers.
The exact identities here alone justify no further native search or exponent
substitution. TASK.json records this scoped handoff.

## Attribution

Nick Petalas. Apache-2.0. The retained transform and its complex proof are from
the pinned source, whose original notices remain unchanged. Its lineage credits
Nussbaumer and Quandalle, Harvey and van der Hoeven, and Douglas Colkitt's audit.
The canonical `synthetic-layout-independent` package from mightyOil supplies
the unchanged literal indexed engine and the earlier finite independent audit.
Jose Manuel's PR2298 identifies the outer use of the exact identity; his
PR3477/3385 and PR3493 concern separate production and boundary obligations.
No pending runtime or proof is imported. Exact canonical blobs and hashes are
in SOURCES.json; all are ancestors of this contribution's publication head.
