# The mixed-negative Q8 count region with the call-block rank floor

## Result

For the mixed-negative Q8 register model of PR3570/PR3578/PR3589, the
inherited necessary conditions are the two count inequalities and the trace
parities. Adding the exact block rank data of the same model gives one more
necessary condition, `n_g >= t_g`, and the boundary of the resulting region
carries forced rank values.

```text
admissible (n_i, n_j) at size n, endpoint shape (t_i, t_j):
    n_i + n_j = n,  n_i = t_i (mod 2),  n_j = t_j (mod 2),
    2n + n_i >= 6t - t_i,              2n + n_j >= 6t - t_j,
    n_i >= t_i,                         n_j >= t_j.          (floor)

rank floor:  rank(X_g Y_g) = rank(P_g) = t_g <= min(n_g, t)
             because rank(X_g Y_g) <= min(rank X_g, rank Y_g) <= min(n_g, t).
```

Two consequences that bound the still-open ten-call four-target question.

```text
t = 4 balanced (2,2), ten calls:  (2,8) (4,6) (6,4) (8,2)
t = 4         (3,1), ten calls:  (3,7) (5,5) (7,3)     the floor removes (1,9)
t = 4         (4,0), ten calls:  (4,6) (6,4)           the floor removes (0,10) (2,8)
   PR3578's stronger homogeneous pair already forces the single split (6,4).
```

At the ten-call boundary the equality case is rigid. Equality in the
`g`-inequality is equivalent to `rank(X_g) + rank(Y_g) = n_g + t_g`; both ranks
are at least `r = 3t - n`, so equality forces

```text
rank(X_g) = rank(Y_g) = r,   dim(im Y_g cap ker X_g) = r - t_g,
and X_g is injective when r = n_g.
```

For the balanced `(2,2)` shape at ten calls that makes the minority block
saturated: `rank(X_g) = rank(Y_g) = n_g = t_g = 2`, `r = 2`, `X_g` injective,
and `im Y_g cap ker X_g = 0`. The package exhibits explicit rank data with
exactly that profile, so the floor does not already exclude the profile; it is
rank data, not a word.

The region is not vacuous and not weak. Over all `90` endpoint shapes with
`t <= 12` it is nonempty, its minimum never beats the published
parity-rounded `11t/5` value, and it is strictly stronger than that value for
`10` shapes, including `(0,5)`, `(0,8)`, `(1,9)` and `(0,10)`.

The region is **not** attained at three targets: it admits `n = 7` for both
shapes `(3,0)` and `(2,1)`, while the delivered minimum is nine. That is the
first shape family where the inherited necessary conditions leave a gap, and
it is exactly where the sign-sensitive degree-two coefficient of PR3536 is
needed.

## Status correction carried with this package

The predecessor census package `research/q8-min-length-census` lists

> Is the `t = 3` minimum seven or nine?

as an open question. That question is already answered at nine for both
three-target shapes: PR3536 proves the half-call scalar-core bound and
transports the retained PR3471 three-role exclusion through seven calls
(its retained `pr3471-README.md` covers shapes `(3,0)` and `(2,1)` and all
`24 + 8` ordered endpoints). The predecessor's open-questions list is stale
on that point; this package records the answered status and does not
re-derive it. Its other two open questions, the balanced four-target ten-call
decision and the sharp uniform constant, remain open.

## Reproduce

Use CPython 3.12 from a repository root:

```sh
python3.12 -Werror -B scripts/research_package.py --package research/q8-count-region-rank-floor
python3.12 -B scripts/check_research_commit.py --package research/q8-count-region-rank-floor --check-source-history
```

Direct replay also works from a source export without Git or network:

```sh
python3.12 -I -Werror -B research/q8-count-region-rank-floor/verify.py
python3.12 -I -O -Werror -B research/q8-count-region-rank-floor/verify.py
python3.12 -I -O -Werror -B research/q8-count-region-rank-floor/test_package.py
```

The package is self-contained: standard library only, no Git objects, no
network, no third-party dependency. `RESULT.json` is the exact finite
receipt; [VALIDATION.md](VALIDATION.md) states coverage and limits.

## Evidence

- `90` endpoint shapes with `t <= 12`, each with an exactly computed
  admissible region, region minimum, parity-rounded `11t/5` comparison and
  boundary equality list.
- The floor's effect at the ten-call boundary of every open `t = 4` shape,
  with the removed splits enumerated explicitly.
- A complete finite lattice check of the boundary equality statement: in
  every equality case, equality `a + b = n_g + t_g` over admissible rank
  values `a, b >= r` is attained only at `a = b = r`.
- An explicit `F2` rank fixture for the `(2,8)` profile at `t = 4`, checked
  with an independent pivot-based rank routine.

## Sources and limits

The model and both count inequalities are inherited unchanged from
Nick Petalas/PR3570, PR3578 and PR3589, with the sign-sensitive chronology of
PR3536 and the retained three-role exclusion of PR3471 used only for the
status statement. The proof reasoning is restated in [PROOF.md](PROOF.md);
no predecessor file is a hidden premise.

This is a **necessary-condition refinement**, not a decision.

- No ten-call word is constructed and no ten-call word is excluded at any
  role count. The open `{10,12}` questions of PR3589, PR3570 and PR3578 are
  unchanged; this package only narrows the label splits a ten-call word
  would have to use.
- The rank fixture is rank data, not an executable word, and does not
  satisfy the endpoint equations.
- No physical caller, scalar/restoration/hosting/precision invoice, complete
  supplier, multiplication theorem or improved kappa is supplied. The
  selected frontier `0.001672660197076918` is unchanged.
- Independent human and formal proof-kernel review are unclaimed.

## Open next questions

- With the split list narrowed, does a ten-call balanced `(2,2)` word exist
  at `(2,8)`? The equality case forces an injective rank-two minority block,
  which is a small finite target for a search over two calls and eight calls.
- Does the rank floor combine with PR3589's cubic-equality ranks to exclude
  `(2,8)` or `(4,6)` outright? Both are rank-tight on one label, so the
  question is whether the two tight orientations are simultaneously
  satisfiable by a word.
- Does the `(1,9)` removal change any retained four-target count summary
  elsewhere in the register lineage?

## Credit

Produced by Nick Petalas with AI assistance. Nick Petalas/PR3570 supplies the
mixed cubic identity, PR3578 the two-orientation boundary-rank method,
PR3589 the two count inequalities and the four target ranks, PR3536 the
half-call scalar core, and PR3471 the retained three-role exclusion. Only the
block rank floor, the exact region computation, the boundary equality
statement and the status correction are new here. Independent human and
formal proof-kernel review are unclaimed.
