# Thirty shared-hub transfers and the exact coherent boundary

## Claim and definitions

Work over a characteristic-zero field with the seven displayed points

    P0=E, P1=F, P2=G, P3=E+F, P4=E+G,
    P5=F+G, P6=E+F+G.

The marked pair is one of 01, 03, 34. Choose two of the other five
points as ports e,f. There are thirty such placements. Representatives
and scalings are exactly as displayed. Invertible ambient changes are
allowed. No assertion about the other marked pairs or independently
rescaled terminal potentials follows from the old non-Fano symmetries.

For independent marks A,B and indexed queries Q, a marked support
transfer to independent marks a,b and queries q over a second field means
these implications for every query subset S, in both marked orientations:

    A outside span(B,Q_S) implies a outside span(b,q_S),
    A in span(Q_S) implies a in span(q_S).                 (1)

A coherent boundary map assigns one vector p_i to every old P_i, with
independent marked images. It must satisfy (1) for both of these lists:

* All five unmarked points, mapped to their assigned p_i.
* The three unreplaced points and P_e-P_f, mapped to those p_i and
  p_e-p_f, respectively.

The subtraction requirement is part of coherence. The new ambient
dimension is unrestricted. A different map may be used for each placement.

The new conclusions are:

1. Exactly twenty-nine placements admit a coherent map to a
   characteristic-two field. The explicit maps in MAPS.json use GF4.
2. The unique exception is marks E,F and ports E+G,F+G. No coherent
   map exists over any characteristic-two field, in any dimension.
3. Every one of the thirty *single-hub stars* admits some GF4 transfer.
   At the exception this map changes unreplaced queries using the hub
   direction, so it is not a coherent boundary map.
4. The twenty-nine coherent maps preserve (1) through every finite
   graph attached to the same three terminals. They therefore preserve
   the actual-reader pair floor in the retained complete-plane model.
   The exceptional hub map proves that floor for its one star only.

The old coefficient field can be any characteristic-zero field. All
finite old rank predicates are defined over Q, and extending Q preserves
rank. The new finite field need only be GF4. No all-odd-characteristic
old-field or all-characteristic-two-field existence claim is made.

## Exact graph criterion

Give a finite undirected multigraph terminals with potentials 0,P_e,P_f.
Give each internal vertex a fresh independent potential, independent of
the full old ambient space. Each oriented edge is its endpoint difference.
Unreplaced old queries remain. The new graph uses the same indexed edges,
terminal potentials 0,p_e,p_f and fresh independent internal potentials.
Loops, repeated edges, isolated terminals and cycles are allowed.

For an edge subset S, its span intersected with the old ambient space is
exactly the span D(S) of terminal differences within the connected
components of S. In a linear combination belonging to the old space,
coefficients at internal vertices cancel. In each component the remaining
terminal coefficients sum to zero, so they are combinations of terminal
differences. Conversely, a signed path sum realizes each such difference.
Adding unreplaced queries or the other mark preserves this intersection
formula, by projecting onto the fresh internal directions.

The five terminal partitions therefore contribute exactly

    0, span(P_e), span(P_f), span(P_e-P_f), span(P_e,P_f).

Four cases are subsets of the base list. The fifth is the difference
list in the definition of coherence. Thus those two finite tests are
necessary and sufficient for a fixed boundary map to preserve (1) for
every finite graph. Necessity follows by joining each desired terminal
block by a tree. The three-edge star H,P_e-H,P_f-H realizes all five
partitions already. A fresh-H star transfer with unchanged old boundary
images is therefore also equivalent to coherence.

This argument proves an unbounded graph theorem from the finite
premises. It does not enumerate all finite graphs.

## The twenty-nine coherent constructions

Encode GF4 as 0,1,2=w,3=1+w, with w^2+w+1=0. Begin with the seven binary
coordinate columns above, interpreted in GF4. The table lists all changes.
Marks remain unchanged. Each row supplies one map for the indicated ports.

| Marks | Ports | Changed columns |
| --- | --- | --- |
| 01 | 23 | P3=(1,1,w) |
| 01 | 24 | P3=(w,1,0) |
| 01 | 25 | P3=(w,1,0) |
| 01 | 26 | P2=(0,0,w), P3=(w,1,0) |
| 01 | 34 | P3=(1,w,0) |
| 01 | 35 | P3=(w,1,0) |
| 01 | 36 | P3=(1,1,w) |
| 01 | 45 | No coherent map exists |
| 01 | 46 | P3=(w,1,0) |
| 01 | 56 | P3=(w,1,0) |
| 03 | 12 | P1=(0,w,0), P4=(w,0,1) |
| 03 | 14 | P1=(0,w,0) |
| 03 | 15 | No changes |
| 03 | 16 | No changes |
| 03 | 24 | No changes |
| 03 | 25 | No changes |
| 03 | 26 | P4=(w,0,1) |
| 03 | 45 | P4=(w,0,1) |
| 03 | 46 | No changes |
| 03 | 56 | No changes |
| 34 | 01 | P0=(w,0,0), P5=(1+w,1,1) |
| 34 | 02 | P0=(w,0,0), P5=(1+w,1,1) |
| 34 | 05 | P5=(w,1,1) |
| 34 | 06 | P0=(w,0,0), P5=(1+w,1,1) |
| 34 | 12 | P1=(0,w,0), P5=(w,1,1) |
| 34 | 15 | P5=(0,1,w) |
| 34 | 16 | P5=(w,1,1) |
| 34 | 25 | P5=(0,w,1) |
| 34 | 26 | P5=(w,1,1) |
| 34 | 56 | P5=(w,1,1) |

The exact finite rank proof is the complete subset check in both programs.
Each coherent row checks all 32 base subsets, 16 difference-list subsets
and 64 star subsets, in both source/reader orientations. The independent
program uses integer minors over Q and every GF4 linear annihilator,
without importing the primary implementation. Their complete predicate
streams and counts agree. RESULT.json fixes the ordered stream hash.

The retained original three templates admit thirteen coherent placements.
Both implementations rederive that comparison. The new table admits
sixteen additional placements, one of which was already repaired by
PR3557. Thus fifteen coherent placements here are new relative to that
follow-up. This is a statement about the exact supplied representatives,
not a new classification of all marked non-Fano configurations.

## The exceptional coherent map is impossible

Write the exceptional base queries as

    g=G, d=E+F, b=E+G, c=F+G, t=E+F+G,
    r=b-c=E-F.

Suppose a coherent transfer exists in a characteristic-two field L.
Use e,f for its independent marked images, and reuse g,d,b,c,t,r for
the images. Coherence requires r=b-c. The following old predicates
force their corresponding new predicates by (1):

    e in span(g,b);       f in span(g,c);
    e in span(c,t);       f in span(b,t);
    e,f in span(d,r);     e,f in span(g,t,r);           (2)

    e outside span(f,g);  f outside span(e,g);
    e outside span(f,b);  f outside span(e,c);
    e outside span(f,t).                              (3)

Both exact programs independently check these eight reader and five
source premises in the old coordinates. The contradiction below is a
written proof over every L, with arbitrary ambient dimension.

First g cannot be zero: otherwise e in span(g,b) would contradict e
outside span(f,b). The first two exclusions in (3) now make e,f,g
independent. Indeed a nonzero relation involving g and e,f would either
put e in span(f,g), put f in span(e,g), or force g=0.

The first two readers in (2) give

    b=lambda e+mu g,       c=nu f+xi g,

where lambda,nu are nonzero. The next two relevant exclusions in (3)
give mu,xi nonzero as well. The readers e in span(c,t) and f in span(b,t)
put t in both span(e,c) and span(f,b). Therefore t is in span(e,f,g),
and for nonzero A,B its coordinates satisfy

    t=A e+B f+C g,
    C=A mu/lambda=B xi/nu.                            (4)

The nonzero e and f coefficients follow because c alone cannot span e
and b alone cannot span f. Thus C is also nonzero.

Since the independent e,f both lie in span(d,r), that two-vector span
is exactly span(e,f). In particular r=b-c has zero g coefficient, so
mu=xi. Equation (4) then gives A/lambda=B/nu=k, where k is nonzero.
Characteristic two yields

    r=lambda e+nu f,
    t=k(r+mu g).

Consequently span(g,t,r)=span(g,r). Its intersection with span(e,f)
is the single line span(r), since e,f,g are independent and lambda,nu
are nonzero. It cannot contain both e and f, contradicting (2).
No ambient dimension or choice of characteristic-two extension avoids
this contradiction. This excludes coherent boundary maps, not every
possible transfer for the resulting star or every decoder.

## A hub-dependent map still exists at the exception

The exceptional old star has independent E,F,G,H, marks E,F and query
order g,d,t,h,x,y:

    g=G, d=E+F, t=E+F+G, h=H,
    x=E+G-H, y=F+G-H.

Over GF4 choose independent e,f,g,h and assign

    d'=e+f+w(g+h),    t'=e+f+g+w h,
    g'=g, h'=h,      x'=e+g+h, y'=f+g+h.              (5)

The minimal reader and maximal source subsets are as follows. These
are all the extremal premises; the programs derive the implications
from all 64 subsets rather than assuming the table.

| Mark | Minimal reader subsets | Maximal source subsets |
| --- | --- | --- |
| E | ghx, dthx, gdhy, thy, dxy, gtxy | gx, thx, ty, ghy |
| F | gdhx, thx, ghy, dthy, dxy, gtxy | tx, ghx, gy, thy |

The complete GF4 tests verify every premise under (5). Since containment
is monotone under adding queries, extremal containment and noncontainment
also suffice to establish all of (1). This finite rank proof gives a valid
star transfer. In (5) the unreplaced d and t use the hub coordinate h.
They therefore cannot be old boundary images with H fresh relative to
the entire new old-ambient space. This explains precisely why (5) does
not contradict the coherent impossibility proof or supply an arbitrary
graph map.

## Actual-reader consequence and limits

Use the support-to-tariff proof retained in
research/p112-query-series-transfer/PREDECESSOR-PROOF.md. Its exact
source, original provenance and credit are recorded in SOURCES.json
and ORIGINS.json. For a literal operator

    aa^T+bb^T=sum_i u_i q_i^T

in one of the proved configurations, source implications give new
characteristic-two query values supported inside the old queries.
Reader implications give new readers supported inside the old readers.
Their product is the same two-indicator target. The complete-plane
support closure preserves inclusion, so the charged F2 Gram rectangle
rank of every term cannot increase.

Appending the untouched alternating-half indicators and expanding the
full binary Gram identity over GF4 gives I_(2n). The unchanged terms
charge 2n-m_A-m_B. Rank subadditivity gives

    sum_i C(u_i,q_i) >= m_A+m_B.

This holds for every finite positive even binary-orthonormal group
partition in the retained model, with arbitrary external reader
coordinates. It covers all thirty specified stars. For the twenty-nine
coherent placements it also covers every finite three-terminal graph
attachment with fresh internal directions. It does not settle the
exceptional placement for arbitrary graphs whose maps may depend on
the graph. No cheaper literal bill is established.

This is a scoped algebraic result. Other marked pairs or terminal
scalings, larger/repeated interfaces, arbitrary graph-dependent maps
at the exception, odd-characteristic old configurations, masked
identities and changed closure remain open. Acquisition, coefficient
execution, dirty restoration, physical frames, hosting, precision,
stock, compiler/all-size admission, complete consumers, both supplier
invoices and the multiplication theorem are unrun obligations. No new
kappa or selected-frontier change follows. The mathematical proof is
author-written; independent human and formal proof-kernel review are
unclaimed.

Credit retains Philippe Van Velzen's expanded-identity argument, ctoth's
coverage question, the actual-reader lineage through PR3414/3463/3472/
3489/3491/3505, and Nick Petalas's PR3506/3524/3535/3547/3557. The new
contribution is the complete exact thirty-placement classification,
the all-field coherent obstruction and the separate exceptional hub map.
