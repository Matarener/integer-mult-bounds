# Strict-volume least borrowing on Count tapes

The complete encoded selector now admits PR3503's exact strict padding rule
S<2q^k, using stock-capped trials and materializing the final radix power only
once. The [proof](PROOF.md) establishes exact minimum selection and the new
final-size bound 2q^k<=q S_D(floor(e/w)). This closes the Count-selector gap
left by the strict row adapter and extends PR3518's conditional setup bound
O(h^3+w^2 h^4) operations and O(wh) cells to the wider predicate, with
h=1+ceil(log2(e+1)).

The cap is floor(S/2)+1. Equality S=2q^k rejects. The selector preserves exact
stock and returns genuine q^k rather than a saturated surrogate. It keeps the
original atom width fixed, enforces 2k<e and body>=m, and returns seven owned
Counts plus the fit flag. It is opt-in and installs no ordinary callback.

This is a setup implementation and conditional interface result. PR3503
already proved the possible one-digit saving and fit enlargement. PR3518
already proved saturation for covering. Their proofs and the full runtime
source closure are retained as actual dependencies, with exact origins in
[PREDECESSOR.json](PREDECESSOR.json). No unmerged Git object or network is
needed for scientific replay. Frozen predecessor notices are unchanged.

## Evidence and reproduction

Python 3.12 with the standard library suffices. Use an existing private
external TMPDIR for source extraction and controls. From the repository root:

```sh
python3.12 -W error -B scripts/research_package.py --package research/encoded-strict-borrowing
python3.12 -W error -B scripts/check_research_commit.py --package research/encoded-strict-borrowing --check-source-history
```

The four actual direct commands also work in a committed Git-free export:

```sh
python3.12 -I -W error -B research/encoded-strict-borrowing/verify.py
python3.12 -I -O -W error -B research/encoded-strict-borrowing/verify.py
python3.12 -I -O -W error -B research/encoded-strict-borrowing/independent.py
python3.12 -I -O -W error -B research/encoded-strict-borrowing/controls.py
```

[RESULT.json](RESULT.json) records 990 literal complete plans, 4096 threshold
boundary decisions including 32 rejected equalities and 192 final-bound checks with 14 sharp equalities, seven invalid-input and
ownership/failure controls, and a separate 2880-case exhaustive/slab census.
The latter finds 680 one-digit savings among jointly fitted cases and 53
newly fitted cases. These are finite domain counts, not asymptotic claims.
Seven actual optimized CLI mutations check strictness, final exact rows,
compatibility, the changed predicate, retained source/proof drift and typed
receipt comparison.

At reduced e=17,q=2,m=2,r=1,W=Q=1,w=1, strict selection returns k=7,
stock=216,rows=128. Covering needs k=8. At e=5, strict selection returns
k=2,stock=6,rows=4 while covering has no fit. These are genuine GL2-derived
stocks, not arbitrary threshold examples.

The literal million-width setup returns k=49,depth=19, exact rows
562949953421312 and stock 609359740010496, using a maximum observed Count
tape extent of 63 cells. PR3518's covering evidence returns k=50 on the same
parameters. An uncapped upper trial would request a 500000-bit power by
arithmetic; that power was not executed or timed. The observations concern
runtime Count tapes, not Python heap size or a speed factor.

## Consumer and scope limits

The old padding planner rejects q^k<S. Passing the new plan alone through
its old ordinary factory is insufficient. A later caller must explicitly
compose the strict-padding adapter and retain the completed-callee, ownership,
pointwise fresh-row/spectator restoration and complete cost premises.
Zero-added-row checks alone do not establish those semantic premises.

No payload/C0, selected GL64, fixed-role microtransition table, actual selected
stock coefficient, physical caller, supplier, cutoff, kappa or selected-frontier
change is supplied. Full-cover, completed leaves, source access, fresh fields,
all recursive children, frame/routing costs, private buffers, restrictions,
cleanup, precision/tape and outer transfer remain separate obligations.
Full selected cold replay, Lean/Docker and formal-kernel verification are not
part of this result. Independent human and formal proof-kernel review are unclaimed.

## Open next questions

1. Compose the selector and strict-padding adapter at one actual ordinary
   caller. Check both padded returns, the genuine other high field, immediate
   restrictions and no-fit fallback. The completed physical C0 and its full
   invoice remain blockers. Setup agreement is not payload evidence.
2. Refine the conditional 26-role setup allowance to the production fixed-role
   compiler. Start with exact arithmetic scans, tape access, initialization,
   final power and disposal. The source-wide all-size refinement is still
   required before supplier admission.

[TASK.json](TASK.json) records these questions, the changed catalogue scope,
priority revision, overlap coverage and stopping decision. [ENGINEERING.md](ENGINEERING.md)
records the implementation bounds and verification limits.

## Credit

Nick Petalas. Apache-2.0. Credit Hiroki Kumazaki's PR3502 encoded selection,
Nick Petalas's PR3503 strict padding, PR3518 saturation and PR3486/3246 stock
lineage, Jose Manuel's PR2899 arithmetic and PR2786/2808 source closure,
Tekalign's ordinary consumer connection, David Arias's PR2753 caller and
Ross Richardson's live/physical format distinction. Their retained sources
preserve the full earlier BIT, geometry, hosting, assembly and compiler credit.
