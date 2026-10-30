# The exceptional single-hub literal charge is 48

## Statement

Work over any field of characteristic zero. Use the exceptional single-hub
star of PR3573, with independent `E,F,G,H`, marks `E,F`, and queries

    g = G,  d = E+F,  t = E+F+G,  h = H,
    x = E+G-H,  y = F+G-H.

In coordinates `(E,F,G,H)` these are the six columns

    g=(0,0,1,0), d=(1,1,0,0), t=(1,1,1,0),
    h=(0,0,0,1), x=(1,0,1,-1), y=(0,1,1,-1).

The extremal premises, rederived by enumerating all 64 subsets, are exactly
the table in PR3573:

| Mark | Minimal reader subsets | Maximal source subsets |
| --- | --- | --- |
| E | ghx, dthx, gdhy, thy, dxy, gtxy | gx, thx, ty, ghy |
| F | gdhx, thx, ghy, dthy, dxy, gtxy | tx, ghx, gy, thy |

A maximal source subset `S` is one for which the mark lies outside
`span(other mark, Q_S)` and enters that span after every added query.
A minimal reader subset is one that spans the mark and has no proper
subset that does. Monotonicity makes these twenty rows the certificate:
six readers and four sources for each mark.

**Theorem.** In the relaxed literal actual-reader model below, every
admissible factorization has total charge at least **48**, and the witness
in `WITNESS.json` attains 48. The one-unit baseline is `2 * 20 = 40`, so
the excess is exactly **8**. That excess sits on four reader rows,
`E,F` crossed with `{dxy, gtxy}`, each of which pays two units rather than
one. The GF4 hub-dependent transfer of PR3573 still satisfies every subset
implication, so the excess is not an obstruction to that star transfer.

## The row model

This is the model minimized in PR3698, restricted to these twenty premises.
For each premise row `p` choose an evaluator `phi_p` and a reader `u^(p)`
with `sum_i u_i^(p) Q_i = mark(p)`, such that

* `phi_p(mark(p)) = 1` and `phi_p(other mark) = 0`;
* on a source row, `phi_p` vanishes on every query of the premise, and the
  support of `u^(p)` lies in one of that mark's six minimal reader sets;
* on a reader row, the support of `u^(p)` lies in that row's premise.

Companions contribute a zero port, so there are 40 ports. With `a` and `b`
the indicators of the active E and F rows,

    a a^T + b b^T = sum_i u_i q_i^T,

where `(q_i)_p = phi_p(Q_i)` and `(u_i)_p = u_i^(p)` on active rows. The
charge is `2 * sum_p cost(p)`, and

    cost(p) = #{ i : u_i^(p) != 0 and phi_p(Q_i) != 0 }.

PR3698's coordinate functional is one admissible evaluator. The minimum
below allows every rational evaluator with the two mark conditions. That
is the same safe relaxation as PR3698: a lower bound in the larger model
is a lower bound in the smaller one.

## Proof

**Step 1. Every row pays at least one.**
The reader identity and the evaluator give

    1 = phi_p(mark(p)) = sum_i u_i^(p) phi_p(Q_i).

Some index has both factors nonzero, so `cost(p) >= 1`. Twenty rows give
charge at least 40.

**Step 2. Four reader rows pay at least two.**
On each of these four premises the only spanning subset is the whole
premise, and the reader coefficients are unique.

For `E` on `dxy` they are `(1/2, 1/2, -1/2)`. Every admissible evaluator
has the shape `phi = (1, 0, α, β)`, hence

    phi(d) = 1,  phi(x) = 1+α-β,  phi(y) = α-β,

and `phi(x) - phi(y) = 1`. The value on `d` is never zero, and `x` and `y`
cannot vanish together. All three coefficients are nonzero, so `cost >= 2`.
The same shape `phi = (0, 1, α, β)` on the `F` row `dxy`, whose unique
coefficients are `(1/2, -1/2, 1/2)`, gives `phi(d) = 1` and
`phi(y) - phi(x) = 1`.

For `E` on `gtxy` the unique coefficients are
`(-1/2, 1/2, 1/2, -1/2)` on `(g,t,x,y)`. Then

    phi(t) - phi(g) = 1,  phi(x) - phi(y) = 1.

Each pair contributes at least one visible query, so `cost >= 2`.
For `F` on `gtxy` the unique coefficients are
`(-1/2, 1/2, -1/2, 1/2)`, and the same two differences are `1` and `-1`.

Thus four rows pay at least 2 and sixteen pay at least 1:

    sum of costs >= 24,  charge >= 48.

**Step 3. Both bounds are attained.**
`WITNESS.json` gives one admissible `(u, phi)` per row. Its twenty costs
are sixteen 1s and four 2s. Both programs recompute the reader identity,
the evaluator conditions, the source vanishings, and all `40 * 40` entries
of the Gram identity. One attaining per-query charge split, for
`g,d,t,h,x,y`, is

    [0, 20, 4, 8, 6, 10],  total 48.

That split is a property of this witness. Another minimum witness can move
charge between queries. The total cannot.

**Step 4. Where the coordinate count overstates the excess.**
If `phi` is forced to be the mark's coordinate functional, a query
contributes exactly when its mark coordinate is nonzero. Under that
stricter reading the minimum bearing counts on the E readers are

    ghx:1, dthx:3, gdhy:1, thy:1, dxy:2, gtxy:2,

and on the F readers

    gdhx:1, thx:1, ghy:1, dthy:3, dxy:2, gtxy:2.

The rows `dthx` and `dthy` look like cost 3. They are not. Their unique
readers are `(1,-1,1,1)` on `(d,t,h,x)` and `(d,t,h,y)`. The evaluator
`phi = (1,0,-1,0)` on the E row, and `phi = (0,1,-1,0)` on the F row,
kills every query except `d`. The relaxed cost is 1. The two-bearing
mechanism of PR3698 survives here only on `dxy` and `gtxy`.

## The exceptional transfer still works

Over GF4, with `w^2 + w + 1 = 0` and independent `e,f,g,h`, the PR3573
hub map

    d' = e+f+w(g+h),  t' = e+f+g+w h,
    g' = g,  h' = h,  x' = e+g+h,  y' = f+g+h

preserves all 128 oriented subset implications: a reader containment in
the old star remains a reader containment, and a source exclusion remains
a source exclusion. This is the point of the handoff. The `K3,2`
certificate of PR3583 has no characteristic-two transfer, and its literal
charge is forced from 42 up to 54. This star still has its transfer, and
its literal charge is forced only from 40 up to 48.

## What this does not establish

The result is the exact minimum of one finite row model on one certificate.
It is not a graph classification, not a charge bound for a third hub, not
a literal tariff for the wider coverage identity, and not a physical or
supplier cost. The per-query split above is not unique. No new kappa and
no selected-frontier change follows. Acquisition, dirty restoration,
frames, hosting, precision, stock, all-size admission and both supplier
invoices are unrun.

The mathematical argument is the pairing above together with the finite
enumeration. Independent human and formal proof-kernel review are
unclaimed.
