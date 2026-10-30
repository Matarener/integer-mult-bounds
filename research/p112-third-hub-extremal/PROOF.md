# The third hub adds crossed two-bearing rows

## Statement

Work over any field of characteristic zero. For an integer \(h \ge 1\), take
independent marks \(E,F\) and independent internal potentials \(G,V_0,\ldots,V_{h-1}\).
Index \(3+3h\) queries by

\[
g=G,\quad d=E+F,\quad t=E+F+G,
\]
\[
v_j=V_j,\quad x_j=E+G-V_j,\quad y_j=F+G-V_j.
\]

This is the one-hub star of PR3573 when \(h=1\), and it is that star with the
hubs \(k,z,w\) of PR3583 adjoined when \(h=2\). The third hub is \(h=3\).

A subset of queries is a **minimal reader** for a mark when the mark lies in
the span of those queries and in no proper subset. It is a **maximal source**
when the mark lies outside the span of the other mark and those queries, but
enters that span after every added query. The relaxed literal actual-reader
model is the one minimized in PR3698 and again for \(h=1\) in the single-hub
charge argument: each extremal row chooses an evaluator with value 1 on its
mark and 0 on the other mark, and a reader supported on a minimal reader set
of its mark (the row's own premise, if the row is itself a reader). The cost
of a row is the number of queries where the reader coefficient and the
evaluator are both nonzero. The charge is twice the sum of the row costs.
Companions contribute a zero port, so the one-unit baseline is twice the
number of rows.

**Theorem.** In this model, for every \(h \ge 1\), the charge exceeds the
one-unit baseline by at least \(4h(h+1)\). For \(h \le 3\) the excess is
exactly that number, and the minimum charges are

| hubs | rows | baseline | minimum charge | excess |
| --- | ---: | ---: | ---: | ---: |
| 1 | 20 | 40 | 48 | 8 |
| 2 | 52 | 104 | 128 | 24 |
| 3 | 104 | 208 | 256 | 48 |

At three hubs there are 24 two-bearing rows, not only the four rows
\((d,x_0,y_0)\) and \((g,t,x_0,y_0)\). Twelve of them are crossed five-query
readers, two for each pair of hubs. The excess 48 is not the twelve-unit
\(K_{3,2}\) excess. That twelve is the separate 21-premise certificate of
PR3583/PR3698, whose charge this package recomputes as 54.

## The two-bearing families

Write \(\phi\) for an evaluator with \(\phi(E)=1\) and \(\phi(F)=0\). Then
\(\phi(d)=1\), \(\phi(t)-\phi(g)=1\) and \(\phi(x_j)-\phi(y_j)=1\). The same
identities with the marks exchanged cover \(F\).

**Family A.** For each hub \(j\), the three queries \(d,x_j,y_j\) are linearly
independent: the minor on coordinates \(E,F,G\) equals \(-2\). The unique
expression of \(E\) is
\[
E=\tfrac12 d+\tfrac12 x_j-\tfrac12 y_j.
\]
Every coefficient is nonzero, so the triple is a minimal reader, and every
admissible reader uses all three queries. Since \(\phi(d)=1\) and
\(\phi(x_j)-\phi(y_j)=1\), at least two of the three evaluator values are
nonzero. The cost is at least 2. The evaluator with every free coordinate 0
kills \(y_j\) and leaves \(d\) and \(x_j\), so the cost is exactly 2. The same
triple is a minimal \(F\)-reader of cost 2.

**Family B.** For each hub \(j\), the four queries \(g,t,x_j,y_j\) are
linearly independent on \(E,F,G,V_j\). The unique expression of \(E\) is
\[
E=-\tfrac12 g+\tfrac12 t+\tfrac12 x_j-\tfrac12 y_j,
\]
so the quadruple is a minimal reader and every reader uses all four queries.
The two differences above force at least one visible query in \(\{g,t\}\) and
at least one in \(\{x_j,y_j\}\). The cost is at least 2, and the same zero
free coordinates attain 2. The quadruple is likewise an \(F\)-reader of cost 2.

**Family C.** For each pair \(i<j\), both of the five-query sets
\[
(d,v_i,y_i,v_j,x_j)\qquad\text{and}\qquad(d,v_i,x_i,v_j,y_j)
\]
are minimal readers of cost exactly 2 for each mark. On the first set the
unique expression of \(E\) is
\[
E=\tfrac12 d-\tfrac12 v_i-\tfrac12 y_i+\tfrac12 v_j+\tfrac12 x_j.
\]
The five vectors meet the coordinates \(E,F,G,V_i,V_j\) in a matrix of
determinant \(-2\), so they are independent and no proper subset can produce this
expression. Every reader therefore uses all five queries. An evaluator cannot
kill \(v_i,y_i,v_j,x_j\) simultaneously: killing \(v_i\) and \(y_i\) forces the
\(G\)-coordinate to vanish, while killing \(v_j\) and \(x_j\) forces it to be
\(-1\). The zero free coordinates attain cost 2, with \(d\) and \(x_j\)
visible. Exchanging the two hubs' \(x\) and \(y\) gives the second set, and
exchanging the marks gives the \(F\) rows.

These \(h(h+1)\) masks are pairwise distinct, and each contributes two rows.
That is \(2h(h+1)\) rows of cost at least 2. Every other extremal row costs at
least 1, so the excess charge is at least \(4h(h+1)\) for every \(h \ge 1\).

## The extremal table for at most three hubs

Both programs enumerate every query subset for \(h \le 3\). One reduces rows
over the rationals. The other uses only integer cross-multiplication. They
agree, and the extremal table is exactly the following list.

Minimal \(E\)-readers:

- for each hub \(j\), the six sets
  \((g,v_j,x_j)\), \((d,t,v_j,x_j)\), \((g,d,v_j,y_j)\),
  \((t,v_j,y_j)\), \((d,x_j,y_j)\), \((g,t,x_j,y_j)\);
- for each pair \(i<j\), the six sets
  \((d,v_i,y_i,v_j,x_j)\), \((t,x_i,y_i,v_j,x_j)\),
  \((d,v_i,x_i,v_j,y_j)\), \((g,x_i,y_i,v_j,y_j)\),
  \((t,v_i,x_i,x_j,y_j)\), \((g,v_i,y_i,x_j,y_j)\).

Minimal \(F\)-readers are those sets with each hub's \(x\) and \(y\) exchanged.
Maximal \(E\)-sources are obtained by choosing an anchor and, independently
for each hub, one of two bundles:

- anchor \(g\), and for each hub either \(\{x_j\}\) or \(\{v_j,y_j\}\);
- anchor \(t\), and for each hub either \(\{v_j,x_j\}\) or \(\{y_j\}\).

Maximal \(F\)-sources are those sets with \(g\) and \(t\) exchanged. There are
\(3h(h+1)\) readers and \(2^{h+1}\) sources on each mark. The count of rows is
therefore \(2\bigl(3h(h+1)+2^{h+1}\bigr)\) for \(h \le 3\). This shape is a
checked classification, not a proof for every larger \(h\).

On this table the search finds cost 1 for every row outside families A–C, and
cost 2 on every family row. The search allows every rational evaluator and
every reader supported on the legal premise, which is the same safe relaxation
as PR3698. Equality follows:

\[
\text{excess charge}=4h(h+1)\qquad(h\le 3).
\]

In particular the third hub has 104 rows, charge 256 and excess 48. Twenty-four
of the rows are two-bearing. Twelve of those use two hubs at once, so the new
hub does add two-bearing rows beyond \(dxy\) and \(gtxy\).

## The twelve-unit certificate is a different list

PR3698 minimizes the same row model on 21 premises of the two-hub star, not on
every extremal subset. Those premises are the seven source exclusions and
fourteen reader containments named in PR3583. Both programs recompute that
restricted minimum and obtain charge 54, excess 12, with the six extra units
of cost on
\[
(d,x_0,y_0),\ (d,x_1,y_1),\ (g,t,x_0,y_0)
\]
for each mark. The crossed five-query readers are absent from that list, which
is why its excess is 12 rather than the full two-hub excess 24. Adding the
third hub to the complete extremal table does not repeat that twelve.

## What this does not establish

The result is the exact minimum of one finite row model on the complete
extremal table for at most three hubs, plus a lower bound of the same shape
for every larger hub count. It is not a graph classification, not a
charge-transfer lemma, and not a characteristic-two obstruction. PR3573's GF4
map and PR3583's characteristic-two failure are not rerun. Nothing here is a
physical tariff, a supplier admission, or a change in \(\kappa\). The selected
conditional exponent stays \(0.001672660197076918\).

The equality \(4h(h+1)\) is checked through \(h=3\) only. A fourth hub has
\(2^{15}\) query subsets and is a separate computation. Acquisition, dirty
restoration, frames, hosting, precision, stock and both supplier invoices are
unrun.
