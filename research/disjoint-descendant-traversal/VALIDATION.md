# Validation and implementation bounds

The finite certificate was executed on macOS 27.0.1 arm64 with CPython
3.12.15, using `/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12`.
Warning-strict isolated normal and optimized runs pass. Both registered
commands pass within one second each against a 120-second command timeout.
The package runner's metadata and live-input hash validation pass.
The committed-byte/source-history check is run after committing the package.
Hosted checks are reported in the PR body and are not claimed here.

The observed output is

```text
PASS_DISJOINT_DESCENDANT_TRAVERSAL additions=30676 roles=32216 no_new_kappa
PASS_REGISTERED_RESEARCH_PACKAGE research/disjoint-descendant-traversal outcome=completed
```

Each replay checks 2,371,600 integer coefficient positions, 32,216 compiled
roles, 61,352 literal disjoint-mixer scalar additions, both frame orientations,
104,897 distinct nontrivial transitions, the complete historical invoice and
six rejecting controls. The new checker reconstructs integer supports without
using the constructor's cached supports as its oracle. It compares the caches
only after reconstruction. Explicit exceptions preserve these checks under
`-O`. The dense dirty integer roundtrip is one additional test; the written
elementary inverse proves the all-input statement.

The baseline orientation returned `PASS_RESEARCH_BASELINE_BINDINGS_ONLY`.
No predecessor circuit census, selected cold replay, Lean, Docker, historical
suite or current supplier admission was run. The construction's phase check
uses the retained general enclosure case proof, not explicit h22 residual
orthonormal bases. CI success remains separate from mathematical acceptance.

## Engineering choices

The Autonomous local run playbook stopped at the first strictly improved
verified circuit. Build the Lever changed the deliverable into a deterministic
constructor and literal-map verifier. Prove It Works required checking the
actual compiled slot embedding and literal scalar operation count, in addition
to the output matrix. The search is not shipped as a new census or expanded
into further circuit variants.

The Power of Ten inspection is scoped to the two new Python files and their
retained constructor/compiler/frame entry points. Every new function is under
60 physical lines. The fixed input is h=22 and subset sizes at most three;
there is no user-controlled search or unbounded retry. Source metadata is
bounded to 16 rows. New DAG checks enforce at most 41,441 allocated nodes,
the 1,540 inputs plus at most 39,900 unshared additions plus the zero node.
Every complete integer support has at most 1,540 bits; compiled storage has
32,216 slots. The factor-order reversal preserves the 39,900 unshared bound.

Two explicit deviations retain the finite existing implementation rather than
change shared scientific code. The tensor constructor and planner use recursive
calls on strictly smaller ground sets, starting at 22 points. Balanced sum
recursion has depth at most 11 for at most 1,540 terms. A conservative bound
of 64 nested constructor/planner/sum frames suffices for these fixed inputs.
The managed Python runtime allocates integers, dictionaries and lists during
replay; the fixed finite domain and node bound constrain live data, rather
than prohibiting allocation. Inherited compiler assertions are supplemented
by new explicit slot, pivot, alias, freshness and coefficient checks that run
under optimization. No shared API or dependency configuration is changed.
The six bounded control callbacks are the only new indirect test targets;
each mutation is restored with `finally` before further verification.
