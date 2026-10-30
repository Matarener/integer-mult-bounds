# Exact attainment budgets for hidden power windows

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: scoped mathematical proof with exact finite corroboration.
It answers Open next question 1 of Karnaugh33's
[PR6139](https://github.com/CrocSwap/integer-mult-bounds/pull/6139), at head
`3b9de03623e8bf05af49f9f9c5fc7a426cbde9e5`. No new kappa is claimed.

For h>=1, take integer call profiles on ranks 2^j, 0<=j<=2h+2, with at
most N calls per profile. Require h-fold endpoint zeros at p=0,1 and a
positive window between two interior roots. Put

```text
S=6^h/2,  L=floor(N/S),  Z=floor((L-1)/2).
```

The predecessor's window-width bound is `w >= log_2((Z+1)/(Z-1))`.
We prove it is attainable exactly when

```text
L in {4n^2-1, 4n^2 : n>=3} union {2n(n+1) : n>=4}.
```

[PROOF.md](PROOF.md) gives every attaining residual quadratic and its
allowed common padding. At h=1,N=432 there are two residuals,
`30x^2-71x+42` and `28x^2-71x+45`. Outside the listed set, the cited bound
is unattainable; the actual optimum there remains open. Attainability does
not say every profile at that budget attains the bound.

## Evidence and reproduction

The exact verifier compares the classification with a divisor oracle through
L=4096 and a complete positive-coefficient oracle through L=96. It constructs
signed profiles and checks counts, rank mass, exact endpoint multiplicities,
window signs, budget remainders, both families and rejection controls. It uses
only integers and fractions, with no repository imports, network or predecessor
execution. It finds 100 attaining normalized budgets and 101 residuals, builds
606 profiles and checks 768 padding cases. The full small oracle enumerates
142880 triples and makes 2760 eligible residual/budget comparisons. Controls
include 19 rejected inputs, five semantic cases and nine large-integer cases.
A generated stdout receipt binds all six package files by SHA256.

From the repository root:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/hidden-window-attainment-budgets/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -O -B research/hidden-window-attainment-budgets/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/hidden-window-attainment-budgets
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/hidden-window-attainment-budgets --check-source-history
```

Another CPython 3.12 path may replace the displayed interpreter. The direct
marker is `PASS_HIDDEN_WINDOW_ATTAINMENT_BUDGETS`. Registered replay and
committed bytes/source ancestry are separate checks. Hosted CI status is
recorded in the PR body.

## Scope, sources and limits

This is an arithmetic side result about exact signed power invoices, explicitly
changed from the source-recount card in [TASK.json](TASK.json). It identifies
exactly when the available fixed-budget lower bound is sharp. It does not
re-evaluate the predecessor's N=1000 census.

The source bound and question are cited at their exact public head. They are
written context, not runtime imports or foreign Git dependencies. The new
classification proof is self-contained. Base catalogue, selected record and
accounting documentation are provenance-only pins in [SOURCES.json](SOURCES.json).
[VERIFY.json](VERIFY.json) has no external live inputs. Base main is
`721c03822c421b7f7fcbb2598993b947c4d88419`, priority 8.

The theorem holds for all positive integer h,N. The reusable reference functions
accept 1<=h<=16 and 1<=N<=2^256 and reject larger inputs. Finite verification
uses fixed smaller domains. Managed Python allocation and function dispatch in
rejection controls are documented Power of Ten deviations. Every loop is bounded
by the declared domains; the largest oracle has 4097 buckets. Checks remain
active under `-O`. Warning-strict replay is registered for both modes; no shared
diagnostic configuration changes.

No native word, independent targets, source compatibility, restoration, compiler,
stock, precision/tape or complete consumer is supplied. The five framework
assumptions remain. Selected cold replay, predecessor scientific replays, Lean
and Docker were not run. Independent human and formal proof-kernel review are
unclaimed.

## Open next questions

Determine the exact minimum width at normalized budgets outside the classified
set. Begin with discriminant-sensitive optimization of `Delta/z^2` and a
certificate of its minimum. That integer optimization remains the blocker;
the present result only settles equality in the cited bound. This follow-on
is not pursued here.

## Credit

Karnaugh33 supplies the bound, the first family at L=4n^2-1 and the second
family's n=4 example. The complete classification, adjacent budgets and general
second family are the new contribution. zxv's PR6049 supplies the minimal-support
framework and retains Nick Petalas's PR5174 and Ali Romman's rank-budget lineage.
Classical quadratic/discriminant identities retain their credit. No global
literature-priority claim is made.
