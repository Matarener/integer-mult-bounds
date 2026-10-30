# Three asynchronous helper hubs

This package gives conditional **kappa 0.00312265044**, from
[PR5774](https://github.com/CrocSwap/integer-mult-bounds/pull/5774) at
`7d6ec0cdef31d0c37b7d2563e709979caa0d5eae` and kappa 0.00312192127.
The increase is **0.00000072917**, or about **0.0233565%**.
This is below the donor's one-percent target. The selected frontier is unchanged.

The new mechanism collects one independent helper input at earlier scalar
contacts, keeps its difference from a fresh input in an owned buffer, and
injects that difference at later contacts. The contacts need not occur at one
meeting. Four paid query subdivisions supply the missing access points.
Three rank-nine targets become two rank-five/rank-four pairs and one
rank-eight/rank-one pair. All original inputs remain arbitrary.

[PROOF.md](PROOF.md) gives the temporal identity and the full price.
[PLAN.json](PLAN.json) fixes the three constructions. [WITNESS.json](WITNESS.json)
binds their exact histories, bases, queries and local bills. [RESULT.json](RESULT.json)
records the complete replay. The raw crossing is strictly inside
`(0.00312265047577, 0.00312265047578)`.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/p104-asynchronous-helper-hubs
```

Expected markers are `PASS_P104_ASYNC_HELPER_HUBS_KAPPA_00312265044` and
`PASS_REGISTERED_RESEARCH_PACKAGE`. The standard-library verifier authenticates
the complete predecessor export before import. It checks all 795 input columns,
a separate dense transpose, 2,926 native maps and phases, 1,124 helper normalizers,
208 main adapters, the physical caller, two rational price engines, the compiler
and all outer predicates. Each mode has a 600-second limit.

The complete bill has **66,906 paid calls and 13,444 productive targets**.
Rank surplus remains 760. Ten word/caller/invoice controls and the native phase
control must fail. [VALIDATION.md](VALIDATION.md) separates completed checks from
publication and independent-review obligations.

## Limits

The five inherited assumptions remain: `native_all_columns`, `owned_erasure`,
`compiler`, `precision_tape` and `analytic_recovery`. The large uniform word and
rounded multiplier are not materialized. These are author checks, not independent
human or formal acceptance. No global optimum follows from the discovery search.
The result does not establish the larger breakthrough requested by the donor.

## Open next questions

Can several independent channels share the same paid access points? Can a
changed temporal channel remove a paid rank? [TASK.json](TASK.json) states the
first steps and the remaining physical and pricing obligations. A pairing matrix
or favorable partial bill alone is not an independent productive interface.

## Credit and coordination

Prepared by Ali Romman with substantial OpenAI Codex assistance; no subagents.
Apache-2.0. PR5774 supplies the thirteen retained native copies. PR5751 supplies
the earlier paid meetings. flyingviper's PR5718 supplies the distinct boundary
bases. [NOTICE](NOTICE) retains the complete P104, native, controller, compiler,
BIT and contributor lineage, including Joel Pulikkan's dimension-four basis.

The canonical investigation is
[Discussion5600](https://github.com/CrocSwap/integer-mult-bounds/discussions/5600#discussioncomment-19200475).
The construction was first found on PR5751 and then rebuilt on the stronger,
released PR5774 source. Its gain is measured against PR5774. No PR is merged or
closed, and no selected-result record is changed.
