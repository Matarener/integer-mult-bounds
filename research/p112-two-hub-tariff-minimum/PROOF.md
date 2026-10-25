# The two-hub literal actual-reader tariff is exactly 54

## Statement

Work over any field of characteristic zero. Take the nine queries of PR3583,
indexed `gdthxykzw`, in the basis `E,F,G,H,K`:

    g=G,  d=E+F,  t=E+F+G,
    h=H,  x=E+G-H,  y=F+G-H,
    k=K,  z=E+G-K,  w=F+G-K.                        (1)

with marks `E` and `F`, and with the twenty-one premises that PR3583 proved
unavoidable: seven source exclusions

    e outside span(f,g,h,k);  f outside span(e,g,h,k);
    e outside span(f,h,x);    e outside span(f,g,x);
    e outside span(f,g,h,z);  f outside span(e,g,y);
    f outside span(e,h,y),                                    (2)

and fourteen reader containments

    e in span(g,h,x);   f in span(g,h,y);
    e in span(g,k,z);   f in span(g,k,w);
    e in span(t,h,y);   f in span(t,h,x);
    e in span(t,k,w);   f in span(t,k,z);
    e,f in span(d,x,y); e,f in span(d,z,w);
    e,f in span(g,t,x,y).                                     (3)

**Theorem.** Give each premise row `p` an evaluator functional `phi_p` and a
reader coefficient vector `u^(p)` with `sum_i u_i^(p) Q_i = mark(p)`, subject
to the row conditions stated below, and build the nine rectangular
complete planes of PR3583 from them. Then the total measured charge is at
least **54**, and the retained PR3583 witness attains 54. In particular the
42-charge baseline is unattainable: **every** literal actual-reader
factorization of this certificate loses exactly twelve.

This settles the question PR3583 left open when it wrote that neither the bill
nor its construction is claimed optimal. The excess is not a defect of one
witness. It is forced.

The charge is PR3583's own measured model: for binary Gram-I labels each
rectangular complete plane is charged twice the number of active rows where
both factors are nonzero, and each row contributes a zero companion port, so
there are 42 ports and 21 rows.

## The row model

A **literal actual-reader factorization** assigns to every premise row `p`

* an evaluator `phi_p` in `Q^5` with `phi_p(mark(p)) = 1` and
  `phi_p(mark(other)) = 0`;
* a reader vector `u^(p)` in `Q^9` with `sum_i u_i^(p) Q_i = mark(p)`;

such that additionally

* on a **source** row, `phi_p(Q_i) = 0` for every query `i` of that row's
  premise, and `supp(u^(p))` lies inside one of the seven reader premise sets
  of `mark(p)`;
* on a **reader** row, `supp(u^(p))` lies inside that row's premise query set.

Writing `q_i` for the port vector with `(q_i)_p = phi_p(Q_i)` and `u_i` for the
port vector with `(u_i)_p = u_i^(p)`, both zero at companions, and `a`, `b` for
the alternating-half binary indicators on the E-rows and F-rows, the PR3583
identity `a a^T + b b^T = sum_i u_i q_i^T` holds, and the charge is

    2 * sum_p cost(p),    cost(p) = #{ i : u_i^(p) != 0 and phi_p(Q_i) != 0 }.

PR3583 restricted a source row's reader to the default sets `ghx` and `ghy`.
The model admits all seven reader premise sets there, and The model also admits
every rational `phi_p` rather than only the integral separators PR3583's own
checker required. Both relaxations enlarge the admissible set, so the bound
below is conservative in the safe direction: the true minimum is at least the
number proved here, and the retained witness attains that number, so the two
coincide.

## Proof

**Step 1. Every row pays at least one unit.**

Fix a row `p`. Its reader identity and its evaluator condition give

    1 = phi_p(mark(p)) = sum_i u_i^(p) phi_p(Q_i).              (4)

If every index with `u_i^(p) != 0` had `phi_p(Q_i) = 0` the right side would
be zero. So some index has both factors nonzero and `cost(p) >= 1`. Summing
over the twenty-one rows,

    total charge  >=  2 * 21  =  42.                          (5)

This step is arithmetic on the model; it holds for every admissible
factorization and every field in which the coefficients live.

**Step 2. Six reader rows pay at least two units.**

On a reader row the mark is in the span of the row's premise queries, so the
mark's component on every premise query must be recorded wherever the reader
actually uses that query. The `E`-bearing queries are exactly `d,t,x,z` and the
`F`-bearing queries are exactly `d,t,y,w`, read off (1).

Take the `E` row `e in span(d,x,y)`. The only subsets of `{d,x,y}` spanning
`E` are the full triple: `E` is in none of the three singletons and in none of
the three pairs, and the solving coefficients `(1/2,1/2,-1/2)` are then
unique because `d,x,y` are linearly independent. Two of `d,x,y`, namely `d`
and `x`, are `E`-bearing, so `cost(p) >= 2`.

The same computation for `e in span(d,z,w)` gives the unique coefficients
`(1/2,1/2,-1/2)` on `(d,z,w)`, of which `d` and `z` are `E`-bearing, so
`cost(p) >= 2`.

For `e in span(g,t,x,y)`, the only `E`-bearing queries in the premise are `t`
and `x`. `E` is in the span of none of the twelve subsets of `{g,t,x,y}` that
omit `t` or omit `x`, so every reader carrying `E` on this row must use both
bearing queries and `cost(p) >= 2`. This last enumeration over subsets is the
only finite table used in this proof; both programs replay it, the first by
exact rational linear feasibility over all admissible evaluators and the
second by an exact integer span table, and they agree.

Exchanging `E` with `F`, `x` with `w` and `y` with `z` gives the same bound for
the three `F` rows `f in span(d,x,y)`, `f in span(d,z,w)` and
`f in span(g,t,x,y)`. Six rows therefore pay at least two units and the
remaining fifteen pay at least one:

    total charge  >=  2 * (21 + 6)  =  54.                    (6)

**Step 3. The bound is attained.**

The retained PR3583 witness has evaluator supports and reader supports equal
to its premise sets at reader rows and to `ghx`/`ghy` at source rows. Its nine
measured charges are

    [4, 8, 12, 4, 10, 8, 0, 4, 4],   total 54.               (7)

`verify.py` recomputes (7) from the retained bytes and also checks all 1,764
entries of `a a^T + b b^T = sum_i u_i q_i^T`. So (6) is a minimum, not only a
lower bound.

**Step 4. Where the twelve go.**

Every source row pays exactly one unit, and eight of the fourteen reader rows
pay exactly one. The whole excess of twelve sits in the six two-unit reader
rows, two units each, because their mark is carried by two mark-bearing
queries simultaneously and no alternative reader support avoids paying for
both.

## What this does not establish

This is an exact finite optimum for one fixed row model over one fixed
certificate. It is not a graph classification, not edge-minimality, not a
literal tariff for the wider coverage identity, not a physical or supplier
cost, and not a kappa or selected-frontier statement. It says nothing about
characteristic-two realizations: PR3583 proved none of these supports exists
there, which is a different and strictly stronger statement about a different
object. Nothing here lifts the 42-port factorization to other graphs.

Independent human and formal proof-kernel review are unclaimed. Credit
retains Nick Petalas's PR3506/3524/3535/3547/3557/3573/3583 chain, Philippe
Van Velzen's expanded identity, ctoth's coverage question and the
actual-reader lineage.