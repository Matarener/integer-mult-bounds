# Materialized shared-update and two-block P104 hybrid

This package supplies the missing emitted construction and complete replay for
[PR5806](https://github.com/CrocSwap/integer-mult-bounds/pull/5806). Its actual
conditional **kappa is 0.00312360607355**, an increase of **0.00000024550355**
over exact PR5802. PR5806 supplied the composition and its informal funding
proof. The new work is the source-bound constructor, complete scientific replay,
strict interval price and an attained parameter bound. The selected frontier
is unchanged.

The word has 25,982 instructions, 770 independent public inputs and 28 owned
labels. The 30 owned lifetimes have peak 13 live fields. The complete caller
has 13,444 productive targets, 66,906 paid calls and rank surplus 760. Every
query, helper replacement, COPY, CLEAR, route and scalar allowance is charged.
Owned fields receive no productive credit.

The raw crossing lies strictly between **0.00312360607454** and
**0.00312360607455**. The claimed value is the largest 1e-14 grid point with
the tested saving one grid step above it and the fixed 1e-12 reserve. The next
point fails that reserve. This is a parameter optimum under that contract,
not a global construction optimum. The actual paid profile changed; the result
is not more digits of the parent root.

## Construction and verification

`construct.py` implements the protected-trace recipe in the retained
[construction note](inputs/construction.md). It first applies the eight original
R22 hunks, then the 102 scalar contacts and sixteen native edits of the second
block. It locates each original hunk in the full common source before it uses
the protected trace. It keeps all complementary events in order. The three
accumulated sums and their source values remain intact.

The [proof](PROOF.md) states the complete boundary and source dependencies.
The frozen PR5802 local checker is unchanged. The price checker has an explicit
edit list for the new invoice, parameters and fixed-reserve certificate. The
primary sparse replay and separate dense transpose cover all 798 input axes
and 636,804 endpoint coefficients. The complete native maps, absolute phases,
helper matchers and physical p16/a7 caller are checked on the actual word.
Two exact rational interval engines check the full price. All three compiler
tails, finite completion, 54 strict outer rows and four functional checks pass.
The receipt records controls for source, query, ownership and invoice defects.

## Reproduction

Use Python 3.12 and the standard library:

```sh
python3.12 -B scripts/research_package.py --package research/p104-materialized-shared-hybrid
```

The direct verifier works without Git. `--output NEW_DIR` writes the two
constructed artifacts in a new directory. Replay compares typed canonical JSON
and decompressed word bytes. The complete predecessor export and exact edit data are retained. The two
large paper words are already in that export chain; their decoded hashes bind
them to PR5806 without duplicate JSON copies. No unmerged Git object or network
fetch is needed.

## Limits

The five framework assumptions remain: native_all_columns, owned_erasure,
compiler, precision_tape and analytic_recovery. The fixed finite hybrid is
materialized; the much larger uniform compiler word and rounded multiplier
are not. These are author checks. Independent acceptance and hosted scientific
replay remain separate. See VALIDATION.md for the exact evidence and limits.
No PR is merged or closed, and the selected result is not changed.

## Open next questions

Can a new source region improve this exact hybrid? Check active claims first,
then preserve every arbitrary input and charge the complete changed word.
Independent scientific review can start with the protected event mapping and
the second-block insertion at its intermediate source ordinal.

## Credit

PR5806 / Dugongue supplied the exact composition and informal proof. Credit
Ali Romman's accumulated updates, asynchronous hubs and retained copies;
Joel Pulikkan / GamingPuzzled for R22; the second-block source; flyingviper;
Cinna Davis, David Arias, Gareth Davidson, Cao Yifan, zxv, Jacob Alan Sussman
and every retained native, controller, compiler, BIT and analytic contributor.
See NOTICE and inputs/NOTICES.md. New materialization and checks: Ali Romman
with substantial OpenAI Codex assistance, no subagents. Apache-2.0.
