# Proposed conditional κ = 0.0023: local review and submission draft

The proposed conditional exponent saving is **23/10000**, approximately
**32.8727% above** @rohanarun's [#4181](https://github.com/CrocSwap/integer-mult-bounds/pull/4181),
the leading conditional κ claim located in the checked public PR records.
This compares exponent-saving endpoints. This package records a local finite
replay and a draft submission; independent mathematical acceptance remains open.

Read the [PR description](PR-BODY.md) for the construction story, exact invoices,
useful equations, all nine outer costs, literature, attribution and next steps.
The [standalone bibliography](LITERATURE.md) covers the full delivered research
trail and distinguishes direct use from motivation and unsuccessful probes.

## Scientific entry points

- [Frozen claim and exact source bindings](../kappa-rebuild/CLAIM.json).
- [Outer transfer argument](../kappa-rebuild/transfer-audit/OUTER-TRANSFER-AUDIT.md).
- [Finite integer compiler](../kappa-rebuild/architecture/FINITE-PRECOMPILATION.md).
- [Delayed BIT cover and common weight](../kappa-rebuild/bit/DELAYED-COVER-BRIDGE.md).
- [Explicit finite ranks](../kappa-rebuild/controller/EXPLICIT-TEMPLATE-BOUNDS.md).
- [New precision and storage constants](../kappa-rebuild/transfer-audit/FINITE-TEMPLATE-CLOSURE.md).
- [Local validation receipt](evidence/VALIDATION.json) and [review notes](VALIDATION.md).

The finite uniform ranks `2^276540184361` (complex) and `2^6552928412`
(BIT before cover) specify enormous fixed templates by algorithm. Their full
words and constants have not been materialized. Small rank-57/rank-50 examples
check ownership and complements; they do not achieve the limiting savings.

## Reproduce the supported critical replay

From a checkout containing the committed inputs:

```sh
python3 -B research/kappa-0023-productive-jobs/verify.py --check-only
python3 -B research/kappa-0023-productive-jobs/verify.py --out /absolute/path/to/new-replay
```

Python standard library only. The output directory must be new and outside the
checkout. The runner authenticates the import, copies its exact inputs, executes
the original 23 stages sequentially in dependency order and compares all 59
regenerated artifacts. It leaves the original checkpoint untouched. Read
[VALIDATION.md](VALIDATION.md) for the stale-pin ordering repair and narrowly
scoped host-metadata/compression comparison rules.

## Import scope and preservation

[IMPORT.json](IMPORT.json) binds 365 unchanged delivered files, including all
240 current-round files, and 16 canonical-main inputs. The remaining imported
files supply the critical dependency closure and attribution. One historical
predecessor README conflicted with main; its bytes are retained under
`predecessor-notices/`, leaving the canonical file unchanged.

The complete 3,454-path cumulative overlay remains in the user's Downloads.
This focused contribution is not an assertion that every predecessor package
or historical search is reproduced by its subset. No frozen source, shared
verification code, selected certificate or frontier record is modified.
Scoped `.gitattributes` additions preserve the original research bytes in Git.
Seven dependencies are stored privately under this review package and mapped
to their historical destinations only in the fresh replay, keeping the existing
`kappa-next-regime` package untouched.
The original [delivery receipt](DELIVERY-VERIFICATION.json) is attributed supplied
evidence; its full-base application was not rerun because that exact ZIP is absent.
The reported historical 332-entry recovery discrepancy remains unresolved.

`PR-BODY.md` is the complete PR description. Its literature section mirrors
`LITERATURE.md`; edit both together.

## Open next questions

1. Independently review the compiler, native lift, delayed cover and outer
   support argument together; begin with the source/exit recurrence and
   common-weight condition. External acceptance and inherited assumptions remain open.
2. Tighten the superpotential or find smaller successful fixed ranks without
   losing integer batching and complete constants; the current templates are impractical.
3. Test a geometry-aware H boundary decoder against the actual owner/query
   spaces and a complete bill. Direct endpoint correction currently loses.
4. Change the binding complex job tariff; more BIT saving alone does not
   advance this checkpoint. The [PR description](PR-BODY.md#open-next-questions) gives the first tests and blockers.

Prepared with substantial OpenAI/Codex assistance. Apache-2.0 for new
review material; original notices and third-party licenses are retained.
