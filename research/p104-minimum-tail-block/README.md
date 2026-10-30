# Minimum block length 112 for a fixed two-tail gate family

The fixed PR5756 two-tail/capacity inequalities, with a variable integer block
exponent, are feasible exactly at lengths **112 and above**. At the minimum,
the unique integer cutoff/floor pair is `(16,17)`. A rational witness is
`offset=1/7`, `decay=1951/2000`. This shortens the predecessor's fixed block
length 128 by `1/8` within the stated inequality family.

Claim type: a scoped written proof using explicitly cited scalar bounds from
Ali Romman's [PR5775](https://github.com/CrocSwap/integer-mult-bounds/pull/5775).
Those bounds are premises, not audited or independently replayed here.
[PROOF.md](PROOF.md) gives the complete model, case split and new exact integer
comparisons. The new result changes the block exponent, leaving the complete
paid/target bill and both charged tails explicit.

A complete changed compiler, all other gates, physical realization and new
carrier-size or kappa claims remain open. The selected frontier is unchanged.
The theorem also applies when block lengths must be even or offsets rational.

## Reproduce

From the repository root, using standard-library CPython 3.12:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/p104-minimum-tail-block/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/p104-minimum-tail-block
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/p104-minimum-tail-block --check-source-history
```

Expected direct output:

```text
PASS_MINIMUM_TAIL_BLOCK minimum=112 cutoff=16 floor=17 excluded_lengths=109 controls=10
```

`VERIFY.json` registers warning-strict normal and isolated optimized commands.
The verifier uses exact rational arithmetic and integer powers. It enumerates
all 109 lengths from 3 through 111 as finite corroboration of the monotonicity
proof, checks the new witness and the unique minimal integer pair, and rejects
ten semantic or source-corruption controls. Controls distinguish the old decay,
old offset, larger completion floor, strict reserve/capacity equalities, and
unsupported lower bounds or thresholds. They do not audit the source theorem.

The direct command is read-only and Git-free. Optional `--receipt /absolute/path`
writes a generated receipt outside this package, binding every package file to
its SHA256 and recording the actual interpreter version. No receipt is required
as an input and no handwritten receipt is supplied. `SOURCES.json` pins the
historical catalogue and selected record. `ORIGINS.json` authenticates three
verbatim predecessor files retained locally, so no unmerged Git object or
network fetch is needed to reproduce the new arithmetic.

## Open next questions

Can length 112 be realized by a complete charged compiler for this invoice?
First specify its changed block decomposition and rederive normalization,
exit, rounding and nonrecursive costs. Then check the remaining gates against
the exact source. The missing block rule and complete cost ledger prevent a
carrier-height or admission conclusion. [TASK.json](TASK.json) records this
question and the scope change from the independent-moment card.

## Implementation limits

The script has no recursion, network calls, solver, dynamic imports or local
source-module execution. File inputs have a 128 KiB cap and an exact three-file
allowlist. Its largest explicit loop has 109 iterations. Public arithmetic
checks cap finite test lengths and widths at 4096; the written theorem covers
unbounded lengths by monotonicity. Explicit exceptions remain active under
optimized Python. All functions are below 60 lines.

Power of Ten rule 3 has a managed-runtime deviation in `verify.py`: Python's
exact integers, fractions and JSON parser allocate dynamically. The file cap,
fixed source inventory and bounded arithmetic inputs limit live data. There
are no persistent buffers or background processes. Normal and optimized runs
exercise these bounds and the invalid-input paths. A fixed-allocation port
would be needed if this offline checker were used in a real-time environment.
Python supplies no static pointer-dereference or compile-time allocation
checks; direct local values and explicit calls keep the equivalent paths
visible. The registered warning-strict replays provide recurring diagnostics.

## Credit

New block-threshold proof and checker produced by Nick Petalas. Credit
Ali Romman's PR5775 for the fixed-length envelope and cited scalar premises;
Joel Pulikkan / GamingPuzzled's PR5756 for the complete invoice; and the retained
Ali Romman PR5751, flyingviper PR5718, P104/native/controller and Jacob Alan
Sussman, zxv and Cao Yifan compiler lineage. The retained predecessor files
are unchanged. Elementary monotonicity and integer-power comparisons are
classical. Independent human and formal proof-kernel review are unclaimed.
Apache-2.0.
