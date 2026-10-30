# The hub excess is exactly 4h(h+1) for every hub count

## Setting

This is the model of unpaidmoon's
[PR4145](https://github.com/CrocSwap/integer-mult-bounds/pull/4145)
(`research/p112-third-hub-extremal/PROOF.md`), unchanged. Work over a field of
characteristic zero. For \(h \ge 1\), take independent \(E,F,G,V_0,\ldots,V_{h-1}\)
and the \(3+3h\) queries

\[
g=G,\quad d=E+F,\quad t=E+F+G,\qquad
v_j=V_j,\quad x_j=E+G-V_j,\quad y_j=F+G-V_j .
\]

A **minimal \(M\)-reader** is a query set whose span contains the mark \(M\)
while no proper subset's span does. A **maximal \(M\)-source** is a query set
\(S\) with \(M \notin \operatorname{span}(O,S)\), where \(O\) is the other
mark, such that adding any further query puts \(M\) in the span. Each reader
and each source is one row. A reader row costs the least number of its queries
that an evaluator \(\phi\) with \(\phi(M)=1,\ \phi(O)=0\) must leave nonzero;
a source row costs the least number of nonzero queries over every minimal
\(M\)-reader, with the evaluator also vanishing on the source. The charge is
twice the summed row costs, and the baseline is twice the number of rows.
`verify.py` implements these definitions literally as paid-set searches.

PR4145 proves that the \(h(h+1)\) masks of its families A–C give
\(2h(h+1)\) rows of cost exactly 2 for every \(h\), so the excess is at least
\(4h(h+1)\). It establishes the extremal table, and hence equality, only for
\(h \le 3\). This file proves equality for every \(h\).

**Theorem.** For every \(h \ge 1\):

1. the minimal \(E\)-readers are exactly the \(3h(h+1)\) sets listed in PR4145
   (six per hub, six per pair of hubs);
2. the maximal \(E\)-sources are exactly the \(2^{h+1}\) sets: anchor \(g\)
   with, for each hub, \(\{x_j\}\) or \(\{v_j,y_j\}\); or anchor \(t\) with, for
   each hub, \(\{v_j,x_j\}\) or \(\{y_j\}\);
3. the \(F\) rows are the images of the \(E\) rows under \(\sigma\) below;
4. every row outside families A–C costs exactly 1.

Hence the table has \(2\bigl(3h(h+1)+2^{h+1}\bigr)\) rows, the minimum charge is
\[
16h(h+1)+2^{h+3},
\]
and the excess over the one-unit baseline is exactly \(4h(h+1)\).

At \(h=1,2,3\) this gives charges 48, 128 and 256, as PR4145 reports. At
\(h=4\) and \(h=5\) it gives 448 and 736, with excesses 80 and 120.

**Symmetry.** The linear map \(\sigma\) exchanging \(E\) and \(F\) and fixing
\(G\) and every \(V_j\) fixes \(g,d,t,v_j\) and exchanges \(x_j\) with \(y_j\).
It maps \(E\)-rows bijectively to \(F\)-rows of the same cost. So it suffices
to treat \(M=E\), \(O=F\).

Only integer vectors occur below. Over a field of characteristic zero their
linear relations are those over \(\mathbb Q\), so the finite checks over
\(\mathbb Q\) in `verify.py` apply to every such field.

## Readers

**Lemma 1 (hub shape).** Let \(S\) be a minimal \(E\)-reader. Then \(S\) is
linearly independent, the expression \(E=\sum_{q\in S}\lambda_q q\) is unique
and every \(\lambda_q\ne0\). For each hub, \(S_j=S\cap\{v_j,x_j,y_j\}\) is
empty or one of
\[
a=\{v_j,x_j\},\quad b=\{v_j,y_j\},\quad c=\{x_j,y_j\},\quad m=\{v_j,x_j,y_j\},
\]
and the hub contributes \(\lambda_{x_j}(E+G)+\lambda_{y_j}(F+G)\). For kinds
\(a,b,c\) this is a nonzero multiple of
\[
w_a=E+G,\qquad w_b=F+G,\qquad w_c=E-F .
\]

*Proof.* If \(S\) were dependent, subtracting a multiple of a relation would
zero a coefficient and give a smaller reader. The \(V_j\)-coordinate of the
expression gives \(\lambda_{v_j}=\lambda_{x_j}+\lambda_{y_j}\) (absent queries
have coefficient 0). A single query cannot satisfy this with a nonzero
coefficient. For \(\{v_j,x_j\}\), \(\lambda_{v_j}=\lambda_{x_j}\) and the
contribution is \(\lambda_{x_j}w_a\); for \(\{v_j,y_j\}\) it is
\(\lambda_{y_j}w_b\); for \(\{x_j,y_j\}\), \(\lambda_{y_j}=-\lambda_{x_j}\) and it
is \(\lambda_{x_j}w_c\). \(\square\)

**Lemma 2 (no repeated kind, no full hub).** In a minimal \(E\)-reader no two
hubs have the same kind among \(a,b,c\), the kinds \(a,b,c\) never all occur,
and no hub has kind \(m\).

*Proof.* Each case gives a nontrivial relation inside \(S\), contradicting
independence: \((v_i+x_i)-(v_j+x_j)=0\) for two hubs of kind \(a\), and
likewise for \(b\) and \(c\);
\((v_i+x_i)-(v_j+y_j)-(x_k-y_k)=0\) for kinds \(a,b,c\). If hub \(j\) has kind
\(m\), any other touched hub \(i\) contains one of \(a,b,c\), and the same
two-term relations with hub \(j\) apply. So hub \(j\) is the only touched hub
and \(S=\{v_j,x_j,y_j\}\cup C\) with \(C\subseteq\{g,d,t\}\). Here
\(\operatorname{span}(S)=\langle V_j\rangle\oplus\bigl(\langle w_a,w_b\rangle+
\operatorname{span}C\bigr)\), so independence forces
\(2+|C|\le3\). Since \(E\notin\langle w_a,w_b\rangle\), \(|C|=1\). For each
\(q\in\{g,d,t\}\) the unique solution of
\(E=\lambda_x w_a+\lambda_y w_b+\mu q\) has \(\lambda_y=0\) (\(q=g\)),
\(\lambda_x+\lambda_y=0\) (\(q=d\)) or \(\lambda_x=0\) (\(q=t\)). Each
makes a coefficient of \(S\) zero. `verify.py` checks these three systems.
\(\square\)

**Lemma 3 (reduced circuits).** In the seven vectors
\(E,\ g,\ d,\ t,\ w_a,\ w_b,\ w_c\) of \(\langle E,F,G\rangle\), the independent sets
\(T\subseteq\{g,d,t,w_a,w_b,w_c\}\) expressing \(E\) with all coefficients
nonzero are exactly the nine sets
\[
\{g,w_a\},\ \{d,t,w_a\},\ \{g,d,w_b\},\ \{t,w_b\},\ \{d,w_c\},\ \{g,t,w_c\},\
\{d,w_a,w_b\},\ \{t,w_a,w_c\},\ \{g,w_b,w_c\}.
\]

*Proof.* A finite check of all 63 nonempty subsets by exact elimination
(`verify.py`, `check_core`). For example
\(E=w_a-g=d+w_a-t=\tfrac12(d+w_c)=\tfrac12(d+w_a-w_b)\). \(\square\)

**Proposition 1 (all readers).** The minimal \(E\)-readers are exactly the
lifts of the nine sets of Lemma 3, where each \(w_\kappa\) in \(T\) is
replaced by the kind-\(\kappa\) pair of a hub, distinct kinds using distinct
hubs. There are \(6h+3h(h-1)=3h(h+1)\) of them, and they are the PR4145 list.

*Proof.* By Lemmas 1 and 2, a minimal reader \(S\) determines
\(T=C\cup\{w_\kappa:\kappa\text{ a hub kind in }S\}\) with distinct kinds. The
expression of \(E\) descends to \(T\) with nonzero coefficients. \(T\) is
independent: a relation on \(T\) lifts, through \(w_a=v_j+x_j\),
\(w_b=v_j+y_j\), \(w_c=x_j-y_j\), to a nontrivial relation on \(S\). So \(T\) is
one of the nine sets.

Conversely, lift one of the nine sets with an injective hub assignment. The
lifted expression of \(E\) has every coefficient nonzero. A relation
\(\sum\mu_q q=0\) on the lift satisfies \(\mu_{v_j}=\mu_{x_j}+\mu_{y_j}\) on
every hub, so each hub's part is a multiple of its \(w_\kappa\). The relation
descends to \(T\), where it is trivial, and then every \(\mu_q=0\). An
independent set expressing \(E\) with full support is a minimal reader.
Distinct choices give distinct sets. Six of the nine sets use one hub kind
and three use two, so the count is \(6h+3h(h-1)\). Writing out the lifts gives
the PR4145 list: one-hub sets \((g,v_j,x_j)\), \((d,t,v_j,x_j)\),
\((g,d,v_j,y_j)\), \((t,v_j,y_j)\), \((d,x_j,y_j)\), \((g,t,x_j,y_j)\), and the
two orientations of \(\{d,w_a,w_b\}\), \(\{t,w_a,w_c\}\), \(\{g,w_b,w_c\}\) on
each pair of hubs. \(\square\)

## Sources

**Lemma 4 (all sources).** The maximal \(E\)-sources are exactly the sets
\(Z_\phi=\{q:\phi(q)=0\}\) for linear functionals \(\phi\) with
\(\phi(E)=1\), \(\phi(F)=0\), \(\phi(G)=\gamma\in\{0,-1\}\) and each
\(\nu_j=\phi(V_j)\) chosen so that hub \(j\) has a zero query. These are the
\(2^{h+1}\) sets of part 2 of the theorem.

*Proof.* The queries with \(F\) span the whole space \(\mathbb F^{3+h}\). Let
\(S\) be a maximal source and \(W=\operatorname{span}(F,S)\). If
\(\dim W\le 1+h\), some query \(q\) lies outside \(W+\langle E\rangle\).
Maximality gives \(E\in W+\langle q\rangle\), hence \(q\in W+\langle E\rangle\),
a contradiction. So \(W=\ker\phi\) for a unique \(\phi\) with \(\phi(E)=1\),
and \(\phi(F)=0\). Every query in \(W\) belongs to \(S\), else adding it would
keep \(E\) outside. Thus \(S=Z_\phi\), and \(\phi\) is the only functional
with \(\phi(E)=1\) vanishing on \(F\) and \(Z_\phi\). Conversely, if \(\phi\) is
so determined, \(\operatorname{span}(F,Z_\phi)=\ker\phi\) and \(Z_\phi\) is a
maximal source. Distinct \(\phi\) give distinct sets.

Now
\(\phi(g)=\gamma\), \(\phi(d)=1\), \(\phi(t)=1+\gamma\),
\(\phi(v_j)=\nu_j\), \(\phi(x_j)=1+\gamma-\nu_j\), \(\phi(y_j)=\gamma-\nu_j\).
The vanishing conditions must determine the \(h+1\) unknowns
\(\gamma,\nu_j\). A hub condition is one of \(\nu_j=0\), \(\nu_j=1+\gamma\),
\(\nu_j=\gamma\). If \(\gamma\notin\{0,-1\}\), neither \(g\) nor \(t\)
vanishes and these three are pairwise incompatible. At most one condition
holds per hub, so at most \(h\) conditions bound \(h+1\) unknowns and
\(\phi\) is not determined. If \(\gamma=0\), \(g\) vanishes and hub \(j\)
vanishes on \(\{v_j,y_j\}\) (\(\nu_j=0\)) or \(\{x_j\}\) (\(\nu_j=1\)), and on
nothing otherwise, leaving \(\nu_j\) free. If \(\gamma=-1\), \(t\) vanishes and
the hub options are \(\{v_j,x_j\}\) (\(\nu_j=0\)) or \(\{y_j\}\)
(\(\nu_j=-1\)). Each hub must choose an option, which gives \(2\cdot2^h\)
sets. \(\square\)

## Costs

**Lemma 5 (cost one outside A–C).** Every \(E\)-reader outside families A–C
and every \(E\)-source costs exactly 1.

*Proof.* For a minimal reader \(S\), the only spanning support inside \(S\) is
\(S\). A paid set \(P\subseteq S\) is admissible exactly when some \(\phi\)
with \(\phi(E)=1\), \(\phi(F)=0\) vanishes on \(S\setminus P\). So the cost is
the least number of queries of \(S\) on which such a \(\phi\) is nonzero.
It is at least 1 because \(\sum\lambda_q\phi(q)=\phi(E)=1\).

Take \(\gamma=0\) if \(g\in S\) and \(\gamma=-1\) otherwise, with every
\(\nu_j=0\). The six non-family reduced circuits of Lemma 3 are
\(\{g,w_a\},\{d,t,w_a\},\{g,d,w_b\},\{t,w_b\},\{t,w_a,w_c\},\{g,w_b,w_c\}\). With
\(\nu_j=0\), the hub values are \((v,x,y)=(0,1+\gamma,\gamma)\). For
\(\gamma=0\), pair \(a\) shows one nonzero, \(b\) none and \(c\) one. For
\(\gamma=-1\), pair \(a\) shows none, \(b\) one and \(c\) one. The core values are
\(g=\gamma,\ d=1,\ t=1+\gamma\). Exactly one value is nonzero in each case:
\(x_j\) in \(\{g,w_a\}\), \(d\) in \(\{d,t,w_a\}\) and \(\{g,d,w_b\}\),
\(y_j\) in \(\{t,w_b\}\), and the \(w_c\) hub in the two three-element sets.

For a source \(S=Z_\phi\), \(\operatorname{span}(F,S)=\ker\phi\). An evaluator
vanishing on \(F\) and \(S\) with value 1 at \(E\) must equal \(\phi\). So the
cost is the least number of nonzero \(\phi\)-values on a minimal reader. For
\(\gamma=0\), take the reader \((g,v_0,x_0)\): \(\phi(g)=0\) and exactly one of
\(\phi(v_0)=\nu_0\), \(\phi(x_0)=1-\nu_0\) is nonzero when \(\nu_0\in\{0,1\}\).
For \(\gamma=-1\), take \((t,v_0,y_0)\): \(\phi(t)=0\) and exactly one of
\(\nu_0\), \(-1-\nu_0\) is nonzero when \(\nu_0\in\{0,-1\}\). \(\square\)

*Proof of the theorem.* Parts 1–3 are Proposition 1, Lemma 4 and the
symmetry. Families A–C are the reduced circuits \(\{d,w_c\}\), \(\{g,t,w_c\}\)
and \(\{d,w_a,w_b\}\). Their \(h+h+h(h-1)=h(h+1)\) masks per mark cost exactly 2
by PR4145, and every other row costs 1 by Lemma 5 and \(\sigma\). The summed
cost is the row count plus \(2h(h+1)\). Doubling gives the charge and the
excess \(4h(h+1)\). \(\square\)

## What the program checks

`verify.py` checks Lemma 3 by enumeration, the three Lemma 2 systems, the
per-hub source cases of Lemma 4, and every Lemma 5 witness on the closed-form
table for \(h\le 12\). As an independent control it enumerates every query
subset of the \(h\)-hub star for \(h\le 4\) (opt-in \(h=5\)), compares the
census with the closed-form table, and recomputes each row cost by exhaustive
paid-set search. `test_controls.py` checks that three mutations are rejected
and that the cost-two readers at \(h=2\) are exactly families A–C.

The proof covers every \(h\); the census is not part of it.
