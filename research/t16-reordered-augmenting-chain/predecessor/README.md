# Compose a further cycle with PR3366's neutral unlock

Conditional finite-composition **κ = 0.001673628681907313**, improving the
latest [PR3366](https://github.com/CrocSwap/integer-mult-bounds/pull/3366) by
`261943251/250000000000000000 = 1.047773004e-9`.
The complex side still binds. This is a packing witness, not an optimum or
complete multiplication theorem.

Starting from PR3366's exact owner map, rotate rows `(43909,0,60)` forward.
The three bins' idle ranks change from `(2,1,3)` to `(0,3,3)`.
The complete paid delta is `-H1-H2+H3`. PR3366's five-helper construction and
all seven earlier cycles are retained. The selected word, helper widths,
144-call order, suppliers and complete physical invoice stay fixed.

The profile is
`{1:349709,2:60192,3:62327,4:20448,5:11808,7:2,8:1152,16:2,48:4880}`.
Rank mass remains1,041,408 and deficit5,120. There are69,120 complete helper
roles and10,005 actual charts. Prefix397 is paid at512; row coefficient16,469.
See [PROOF.md](PROOF.md) for the strict concavity argument and scope.

## Reproduction

Standard-library CPython3.12, from the repository root:

```sh
python3.12 -Werror -B scripts/research_package.py --package research/t16-post-unlock-cycle
python3.12 -Werror -B research/t16-post-unlock-cycle/verify.py --work /absolute/new/output
```

The verifier authenticates43 canonical inputs, reconstructs PR3366 from
canonical PR2169 data plus a236-row patch, applies the exact cycle, audits
the full owner map and regenerates OWNERS/PLAN/SPEC. It runs unchanged
11-stage strict admission, both exact supplier prices, both seven-step
bootstraps and all47 strict outer inequalities per tariff path. The entire
typed physical invoice is compared, allowing only three freshly bound source
identifiers to differ. Private search or solver tools are not needed.

Exact predecessor: PR3366 head
`3f59a00257b3e29ad54e349f826d5ffdc59f7cfb`.
Its construction, original delta, source export, result, README and proof are
retained under `predecessor/`. Its unchanged admission wrapper is `replay.py`.
The canonical predecessor payload digest is
`96f0dc4e3b8f08cdfd385992e8675f033ed83bcd61bb14f8f6b9671b8c125fe3`.
Canonical source base is `6f100d4bb5083f8c35d96fd95a539811c62f245c`.

## Relation to parallel work

PR3366 superseded our previous PR3359. Reusing its new map reveals a direct
cycle that was unavailable on3359. PR3369's direct-cycle obstruction concerns
that earlier map, so this result does not contradict its scope. A private
mixed-call solver independently found a37-role rearrangement with the same
paid gain; this contribution publishes the simpler three-role witness.
The alternative is preserved privately for future composition.

## Scope and credit

The selected all-size/compiler, common-label/mutable-source, whole-call
hosting, precision/tape, exact recovery, analytic and bit H1–H5 premises
remain. Native local ancestry is reused by source binding. Fresh full cold
native rebuilding, formal-kernel verification and independent human review
are not claimed. Selected-result.json is unchanged.

Credit Nick Petalas for PR3366/3354/3338, Pierre/hexapode for PR3359,
Gonzalo Mier for PR3308, Philippe Van Velzen for PR2169, George Lydakis,
Rohan Arun and Jeremy Kothe for the packing lineage, Josie Elliston for the
independent owner auditor, Hao Yan for the T16 controller and the retained
compiler/native/bit/moment authors. Original notices remain. New work by
Pierre (hexapode), with substantial OpenAI Codex assistance from four
concurrent agents. Apache-2.0.

## Open next questions

Can a mixed-call exchange move several helpers through one bin to pool more
residuals? Preserve this full map, nominate explicit moves and replay the
complete invoice. No global packing or multi-exchange optimum is claimed.
