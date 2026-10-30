# PR6030's support-local layer: exact uniform specialization

**Scoped conditional audit; no new κ.** The selected PR6030 supplier satisfies the retained deferred-layer cost implication under its compiler, stock and physical contracts. Its normalized ordinary-tree moments are below `2^-47005` and `2^-94010`. The current BIT atom is `1/250`; the historical `0.003` stock estimate needs that substitution. [PROOF.md](PROOF.md) gives a source-bound weighted-potential argument and an explicit symbolic sufficient reservation threshold.

This answers the open audit request in [PR6110](https://github.com/CrocSwap/integer-mult-bounds/pull/6110) at `7f82486e987e556a221085092d8f7aff271ecb35`. That predecessor binds outer formulas but leaves its suggested PR1673 replacement unverified. The [canonical coordination comment](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19239759) records this investigation.

## What the audit adds

The generic deferred argument is already written in PR1673's later review and, more directly, the selected-pinned `FINITE-TEMPLATE-CLOSURE.md` and `OUTER-TRANSFER-AUDIT.md` §5. This package credits and specializes them; it does not propose a new deferral method or find a contradiction in the selected claim.

- Use the **compiled uniform** supplier: rank `N=2^65807000000000`, productive fields `W`, paid rank-one calls `P`, with retained contract `P/W<N^(1-U)`. Its child width is `floor(e/N)` and child volume is `v/W`. The raw mixed P104 histogram is not this ordinary recurrence.
- At `sigma=1-b` and `tau=1-a`, exact products `H(U-b)=47005` and `H(U-a)=94010` give the compressed moment bounds. All internal and leaf margins are strictly positive at PR6030.
- With the current atom `alpha=1/250`, a conservative product-stock reserve is `R<=3h/128+C(log2 h+h^alpha L^3+1)`, `L=max(1,ceil(log2 p))`. For fixed unknown implementation constant `C>=1` and fixed finite base threshold `M`, a sufficient tail threshold is

  `ceil(max(M,16,(192C)^2,(192C L^3)^(250/249)))`.

  Above it, `R<=5h/128<h/16`. The polylogarithmic degree is `250/83`. This is a symbolic bound, not an evaluated practical cutoff.
- The tree potential and geometric phase sum give `O(V g^(1-q) polylog p)`. Whole-row padding must be removed after each exact completed phase. The old `1-c` charge is replaced by this changed algorithm, not satisfied by choosing a positive `c` for logarithmic `K`.

## Evidence and limits

`verify.py` authenticates 11 source inputs and seven selected-manifest bindings, checks the exact substitution, certifies 48 integer threshold fixtures and 528 row-padding fixtures, and rejects 12 mutations covering exponent boundaries, stale atom, insufficient stock/base thresholds, ceiling children, compounded padding and nonidentity row return.

`independent_check.py` was derived by a separate Codex agent before comparison with the lead. It uses a strong-induction proof and a different exact toy implementation: 4,152 stopped-recursion cases, 255 deferred schedules, three parameter rejection controls and an eager-reservation failure family. It imports no source pricing or replay engine. Finite fixtures corroborate the written arguments; they do not establish infinite claims by extrapolation.

Both programs are standard-library Python and run normally and with `-O` in under a second locally. [VALIDATION.md](VALIDATION.md) records commands, results and publication checks. [REVIEW.md](REVIEW.md) records internal review and shared dependencies.

The retained compiler inequality, whole-child volume law, arbitrary dirty complete-field endpoint, support router, local node tariff, BIT stock law and exact return/padding deletion are premises. Exact rounding-residual disposal is not supplied. No physical supplier, uniform word, numerical compiled `W/P/C`, new frontier, full selected replay, Lean proof or human review is claimed. All five framework assumptions remain.

## Reproduce

From the repository root, after activating the project's working Python environment:

```sh
python -B scripts/research_package.py --package research/p104-6030-deferred-layer
```

The registered command runs both checkers in normal and optimized modes. For a Git-free export, run these from the export root (or use absolute script paths from any working directory):

```sh
python -I -B research/p104-6030-deferred-layer/verify.py
python -I -B research/p104-6030-deferred-layer/independent_check.py
```

Add `-O` for the optimized controls. Export all declared `VERIFY.json` inputs; the direct checkers need no Git, network or third-party dependencies and write no files.

## Sources and overlap

Scientific base: canonical main `721c03822c421b7f7fcbb2598993b947c4d88419`, priority revision 8. The authoritative selected record is PR6030, κ `781451/250000000`; priority prose still names PR5599. [SOURCES.json](SOURCES.json) binds exact base blobs and SHA256s. PR6110 is a motivation/citation, not a runtime or Git-history dependency.

Initial overlap covered all 8,348 local note records, 374 open PRs, and 5,770 Discussion records, with complete pagination and no reported coverage warnings. Relevant closed/merged work was checked through local sources, the ledger and a targeted live search; no all-closed-PR inventory is claimed. Source-body inspection found the existing transfer proof that title searches had missed. `complex-stopped-recursion-cost` is the nearest recurrence audit, on PR4100's different mixed tree. Its proof method is credited, not rerun or presented as newly invented here. Absence of another matching title is not evidence of novelty.

## Open next questions

1. Add an explicit citation to the already-selected finite-template and outer-transfer sources in a future maintainer review, with the current atom and uniform recurrence. This would make the dependency easier to audit. First compare the source-bound map here with the selected review; no frontier change is needed.
2. Bind an actual current supplier/ordinary BIT execution to the complete stock, node-local movement and exact padded-row return contracts. Start with one emitted child/row boundary and its physical lifetime; an unmaterialized uniform program and a positive exponent margin do not themselves prove that implementation.

## Credit

Prepared for [DLamdata](https://github.com/DLamdata) with substantial OpenAI Codex assistance in source audit, mathematics, implementation, independent derivation, review and writing. All internal reviews are AI reviews.

Retain DreamingOfClouds' PR6030/PR5907 construction; Ali Romman's P104/compiler chain; Vlado Vojdanovski's PR1673 support-local wrapper; philippeVV's independent PR2044 support/stock review; zxv's PR4359 finite-template and outer-transfer proof; Jacob Alan Sussman's compiler lineage; Cao Yifan's higher-moment strictification; Douglas Colkitt's selected review and retained compact-control proofs; JoyboyBrian's PR4965 conditional recurrence audit; and JosieElliston's Claude-assisted PR6110 source-binding audit. The current BIT atom/stock contract is retained from the query-thinned-controller lineage. Original contributors and source-specific notices remain in the unmodified sources. New work is Apache-2.0.

Submission refresh: canonical upstream remained at the scientific base. The refreshed snapshot covered 374 open PRs and 5,771 Discussion records, plus the full committed local inventory and this new package; no warnings. See [evidence/overlap.json](evidence/overlap.json).
