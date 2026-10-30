# Exact dyadic attainment of P104 spectral correction ranks

The correction-rank bounds in [PR6181](https://github.com/CrocSwap/integer-mult-bounds/pull/6181)
are attained over the original ring R=Z[i,1/2], not only modulo13. One explicit
common code Q, used at both endpoints with no scratch, gives exact rank832 for
the spectral target (alpha,beta)=(1,169) and exact rank1664 for (13,13).
This answers the predecessor's exact-lift handoff. It does not give a native
implementation, a paid invoice or a new multiplication saving.

## Construction

Use [PR3979's triangular congruence](../p104-tensor-code/PROOF.md)
A=U^t P U, detU=1, with n=104,r=8 and M=UU^t. Set

```
X = U^-t tensor U^-t,   Y = U^-t tensor U,
Q = diag(X,Y),          L = PM tensor M.
```

For F=upper(-I tensor A) lower(A tensor I), QFQ^-1 is exactly
upper(-Pc) lower(L). Against T=upper(-alpha Pc) lower(beta Pr), with
alpha beta=169, the correction is

```
E = [ -Pc L +169 Pc Pr    (alpha-1)Pc ].
    [ L-beta Pr                0      ]
```

When alpha=1, E factors through D=Pr(M tensor M-169I). Its rank is at most832,
and its modulo13 rank is832 since M remains invertible. For alpha=beta=13,
the upper/lower images lie in Pc/Pr, giving rank at most1664; PR6181's modulo13
complete-pair invariant gives the matching lower bound. All coefficients and
inverse-code coefficients are dyadic. No division by13 or scratch is needed.
`PROOF.md` gives the ordered algebra, quantified limits and an explicit integral
rank-two witness for the predecessor's requested n=2,r=1 starting example.

## Evidence and reproduction

The standard-library checker reconstructs the actual104-port congruence from
the pinned fixture and checks exact small complete endpoints independently of
the factored argument. The full21632-square operator is not materialized.
Windows11 / CPython3.12.11 normal and optimized registered runs pass and
produce identical receipts: six literal endpoint cases (dimensions8 and32),
two factored P104 endpoints and eight rejecting controls. The actual coupling
minor uses nonpivot columns `[0,1,2,3,4,10,18,27]` and has determinant1/8;
the832 and1664 factored minors both have determinant1 modulo13.
`CERTIFICATE.json` contains the complete receipt; `VALIDATION.json` records
the commands, environment, scoped AI review and limitations.
The lower bound for arbitrary common codes/restored scratch is cited from
PR6181; this package does not re-prove every predecessor theorem by execution.

From repository root:

```sh
python3.12 scripts/research_package.py --package research/p104-dyadic-spectral-attainment
python3 scripts/check_research_commit.py --package research/p104-dyadic-spectral-attainment --check-source-history
```

The registered commands use normal and optimized CPython3.12 with warnings as
errors. `SOURCES.json` binds the proofs and fixture; source_matrix in PR3979's
checker supplies the credited root-enumeration/pivot convention, but its code
is not imported. All source commits are retained in current main history.

## Limits

The construction uses the stronger explicit PR3979 congruence. The abstract
premises A^2=13A and rank(A mod13)=8 alone do not supply this particular Q.
The two target pairs above are established; no minimum for every individual
factorization alpha beta=169 is asserted. Rank is over Q(i), not a native-call
count. The same persistent code and exact scratch return remain the contract.

## Open next questions

Can this correction be delivered at a legal physical caller cut within a
favorable full allowance? First specify the ordered chart conjugates, physical
source/receiver maps, entry/exit costs and dirty restoration. No such native
recipe, ownership schedule, precision/tape account or complete signed bill is
supplied here. This is the stopping point required by the family expansion
gate. Current selected #6030 and its five assumptions remain unchanged.
No hosted CI, independent human review or proof-assistant certification is
claimed. Structured next questions and the scope refinement are in `TASK.json`.

## Credit

Nick Petalas owns PR6181's joint-bank obstruction, modular rank bounds/sharpness
and exact-lift question. Chris R / Clear1nsight owns PR3979's triangular
congruence, tensor protocol and original scalar invoice. PR3961 and the
PR3882/3940/3943/3954 caller lineage retain their credit, as do ToikY's word audit,
Rohan Arun/PR1972, Chafik Boukhalfa/PR1991, Adam Gall/PR1940, Josie Elliston/E8,
Sagar Thakrar/PR1012, Douglas Colkitt, Dominik Scholz and the retained native,
compiler and geometry authors. No predecessor discovery is claimed here.
The common Q attaining the exact endpoint bounds, proof and new checker were
prepared by AAAmirinu with substantial OpenAI Codex assistance, including
separate derivation and checker work. Apache-2.0.
