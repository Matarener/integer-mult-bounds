# All local-Clifford invariant P104 lattices are scalar multiples

This contribution was produced by Nick Petalas. Apache-2.0.

**Scoped mathematical proof with finite corroboration. No new kappa.**
Every nonzero Gaussian-integer module of fields on an r-bit cube, invariant
under each local P104 butterfly and each single-bit i phase, is a Gaussian
scalar multiple of the known Newton lattice:

    L = alpha B_r,  alpha in Z[i] nonzero,
    B_r = { sum_S a_S x_S : (1+i)^|S| divides a_S }.

Thus no different lattice shape in this fixed alphabet repairs the uniform
quarter-division boundary. For every alpha and r>=1, the explicit field

    f(x) = alpha (1+i)^max(r,4) x_1...x_r

belongs to L and has integral f/4, while f/4 is outside L. Source-dependent
divisibility filtrations, changed alphabets and nonlinear entrance domains
remain possible; this is not a universal supplier obstruction.

Clear1nsight's [PR3382](https://github.com/CrocSwap/integer-mult-bounds/pull/3382)
already proves the Newton lattice's exact lifting, phase closure and maximal
integral entrance. Those are cited premises. The new step is the identity

    i(A-iI)(B-iI) = E_00,
    A=[[1,1],[0,i]], B=[[1,0],[i,i]],

which yields every matrix unit. Tensoring gives the full integral matrix
algebra on all coefficient coordinates. Its invariant modules are precisely
J^N for Gaussian ideals J; principality gives the classification above.
[PROOF.md](PROOF.md) gives the all-rank argument and the universal quarter
witness. Classical matrix-unit and principal-ideal methods retain their credit.

## Reproduction and evidence

From the repository root, with standard-library CPython 3.12:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B -W error research/clifford-lattice-rigidity/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -O -B -W error research/clifford-lattice-rigidity/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/clifford-lattice-rigidity
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/clifford-lattice-rigidity --check-source-history
```

Any CPython 3.12 interpreter can replace the local path. Expected marker:
`PASS_CLIFFORD_LATTICE_RIGIDITY ranks=1..7 scalar_classes_only quarter_closure=excluded no_new_kappa`.

The verifier constructs all four local matrix units and checks all sixteen
products; tensors them through rank seven; exhausts all 67 additive subgroups
of `(Z[i]/2)^2`, retaining exactly the three scalar-ideal modules; and checks
the necessity of the phase premise. Signed scalar-ideal fixtures and 49 integral
quarter counterexamples corroborate the universal proof. No predecessor code
is imported or run. The all-rank result is a written proof, not an extrapolation
from these checks.

Every run prints a generated SHA256 receipt for the six package files and
writes nothing. Explicit exceptions keep all checks active under optimization.
Generic metadata, committed-byte/source-history checks and hosted CI remain
separate from mathematical acceptance.

## Limits and decision

The theorem fixes all local bit butterflies and single-bit i phases, and
requires Gaussian-module closure. It does not classify a smaller caller-specific
alphabet, nonadditive/correlated states or domains exact only after a whole word.
The quarter result excludes a uniform lattice closed under every integral
quarter; it permits a stronger source contract such as `4L -> L`.

No codecs, physical owners, native realization, movement, full precision/storage
policy, complete signed invoice, fast recursive implementation or actual caller
are supplied. No frontier, supplier or multiplication theorem is changed.
No selected cold replay, Lean/Docker execution, independent human review or
formal proof-kernel acceptance is claimed. Stop at this classification; a
construction needs a changed boundary and its own complete budget.

The verifier fixes rank<=7 and at most 128 coordinates. Tensor tests have
21,844 row/column pairs in total; the module census has at most 67 subgroups
of a 16-element space and four expansion rounds. Each function is under
60 lines, and receipts read six files capped at 200 KB each. Python-managed
allocation is the explicit Power of Ten deviation; live collections are bounded
by these domains. No recursion, network, subprocess, external mutable state or
dynamic code loading is used. Both registered modes use warnings as errors.

## Open next questions

1. Can a pinned caller maintain a divisibility filtration through quarter ADDs?
   First trace its actual scalar coefficients and phase/butterfly generators.
   A paid codec, independent target contract, native/recursive costs and physical
   storage remain blockers. The uniform-lattice obstruction does not settle this.
2. Can a smaller actual local-generator alphabet retain a nonhomothetic
   lattice that helps a complete bill? First fix that exact alphabet and every
   required prefix; omitting the phase already allows skew lattices. No
   smaller-alphabet classification or favourable cost is supplied here.

Structured questions and scope are in [TASK.json](TASK.json).

## Sources and credit

Credit Clear1nsight's PR3382 for the Gaussian Newton lattice, all-rank maximal
integral entrance, coefficient intertwiners, exact lifting and actual collector
binding. Credit Ross Richardson's PR3068 for the earlier phase/quarter closure
boundary; Tekalign's PR3025/3033 for the floor word; Nick Petalas's PR3035/3037
for the distinct period lattice; Arham Tahir's PR3046 for inverse-domain work;
and ywz65's PR2586 with the retained P104/native, Clifford, geometry and numerical
lineage. The classical Clifford/Barnes-Wall context remains credited by PR3382.
These predecessors are cited, not recertified as this contribution.

[SOURCES.json](SOURCES.json) pins the statements, task catalogue and selected
record at canonical main `19fdb086ea96af9a9f87936a2b888e10af4ed810`, priority
revision 8. The original helper-inventory card is explicitly changed to this
numerical-interface obstruction; no complete productive/paid invoice is asserted.

The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19221619)
predicted an exactness theorem already covered by merged PR3382. The
[scope correction](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19221942)
credits that overlap. This package claims only the subsequent rigidity theorem
and its uniform quarter-closure consequence.
