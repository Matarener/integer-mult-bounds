# An alternate map for the failed shared-port star

## Exact claim

Fix independent rational vectors E,F,G,H and marks E,F. In query order
`d,b,t,h,x,y`, use

    d=E+F, b=E+G, t=E+F+G, h=H,
    x=G-H, y=F+G-H.                                  (1)

This is exactly PR3547's failed attachment at ports G,F+G. A marked
support transfer into a field L consists of independent marks e,f and
six indexed vectors d',b',t',h',x',y' satisfying, for every query subset S,

    E outside span(F,Q_S) implies e outside span(f,Q'_S),
    F outside span(E,Q_S) implies f outside span(e,Q'_S),
    E in span(Q_S) implies e in span(Q'_S),
    F in span(Q_S) implies f in span(Q'_S).            (2)

There is such a transfer into a characteristic-two field L if and only if
L has more than two elements. The binary impossibility permits arbitrary
ambient dimension and does not assume a graphic form for the new queries.
Every field of characteristic two with an element w outside {0,1} admits
the explicit map below. GF4 is sufficient.

Moreover, the same map restores the actual-reader pair floor for every finite
graphic attachment to the two specified old ports. The old field is any
characteristic-zero field. This is one exact placement, not a classification
of PR3547's other failed cases or of odd-characteristic old configurations.

## All finite premises

The following lists are exact for (1). A reader list gives the minimal
query subsets spanning the marked vector. A source list gives the maximal
query subsets for which that marked vector remains outside the span after
the other mark is added.

| Mark | Minimal reader subsets | Maximal source subsets |
| --- | --- | --- |
| E | dbt, dxy, bhx, thy, dbhy | bth, hxy, btxy |
| F | bt, xy, dbhx, dbhy, dthy | by, tx, bhx, thy |

Both exact checkers derive these lists from every one of the 64 subsets.
For readers, checking the displayed subsets implies the conditions for all
supersets. For sources, checking the displayed subsets implies the conditions
for all subsets. Thus this table contains every obligation in (2).

## Construction over every characteristic-two field larger than F2

Take b',h',x',f as an independent basis and set

    e=b'+h'+x', t'=b'+f, y'=x'+f, d'=e+w f,          (3)

where w is neither 0 nor 1. Then e,f are independent. For the two reader
pairs bt and xy, their sums are f. The E reader triples bhx and thy sum to
e. The triples dbt and dxy give e using f and d'. The sum dbhx is w f;
the sum dthy is also w f; and the sum dbhy is (w+1)f. Both w and w+1
are invertible. Consequently every reader subset in the table spans its
required mark.

For E, adding f to the three maximal source subsets gives respectively
span(b',h',f), span(h',x',f), and span(b',x',f). Each misses e.
For F, span(e,b',h',x') is span(b',h',x') and misses f.
Also e=t'+h'+y', and t',h',y',f are independent, so span(e,t',h',y')
misses f. Finally, in span(e,b',y'), the coefficient of h' forces the
coefficient of e to vanish in any proposed expression for f; the remaining
b' and x' coordinates then force the other coefficients to vanish.
The same argument, using h',b',x', applies to span(e,t',x').
These are the other two F source subsets. This proves every condition.

In the coordinates e,f,g,h', choose b'=e+g and x'=g+h'. The concrete
map is

    d'=e+w f, b'=e+g, t'=e+f+g, h'=h',
    x'=g+h', y'=f+g+h'.                             (4)

MAP.json uses GF4 with w squared plus w plus 1 equal to zero. Integers
0,1,2,3 encode 0,1,w,1+w. The substitution changes the old d query
within the marked plane. It is different from PR3547's fixed template
which added wG to d.

## No binary transfer in any dimension

Suppose (2) holds over F2. Drop primes in this paragraph.
The reader bhx puts e in span(b,h,x). The F source condition for bhx
says f is outside span(e,b,h,x), hence f is outside span(b,h,x).
The E source conditions for bth, hxy and btxy imply e is outside each
of span(f,b,h), span(f,h,x), and span(f,b,x). Therefore b,h,x are
independent and all their coefficients in e are nonzero. Over F2 this
forces e=b+h+x. Thus b,h,x,f are independent, even if the alleged map
uses a larger ambient space.

The F reader bt gives f in span(b,t). The reader and independence rule out t=0. The F source tx rules out
t=f. Since b and f are independent, the only remaining possibility
is t=b+f. Likewise the reader xy and source by force y=x+f.

The E reader dxy forces d into span(e,x,f) with nonzero e coefficient.
Indeed e is outside span(x,f), so its expression must use d with
coefficient 1. The reader dbt similarly forces d into span(e,b,f).
The independence just proved gives

    span(e,x,f) intersect span(e,b,f) = span(e,f).

Hence d=e+v f for a binary scalar v. The F reader dbhx excludes v=0,
so d=e+f. Now

    d=b+h+y,

and span(d,b,h,y)=span(b,h,y). It does not contain e: otherwise
f=e+b+h+y would lie in span(b,h,y), which contradicts independence
of b,h,x,f with y=x+f. More directly, the h and b coefficients in an
expression for e force both to be 1, the x coefficient forces that of
y to be 1, and the f coefficient then cannot be zero. This contradicts
the E reader dbhy. No binary transfer exists.

The obstruction is a proof about every F2 configuration. Merely changing
w to 1 in (4) is a weaker finite control; that control fails both reader
conditions on subset dbhy, mask 43, as the checkers confirm.

## Arbitrary finite attachments at the same two ports

Start with the five queries G,d,b,F+G,t in old ambient span(E,F,G).
Map them to g,d',b',f+g,t' as in (4). Replace G,F+G by an arbitrary
finite undirected multigraph with terminal potentials 0,G,F+G and fresh
independent potentials on internal vertices. Every edge is its oriented
potential difference. Use the same graph over L, with terminals 0,g,f+g
and fresh independent internal potentials. Loops, parallel edges and
cycles are permitted.

For a chosen edge subset, its span intersected with the old ambient
space is exactly the span of terminal differences inside its connected
components. To see the forward inclusion, coefficients at each internal
vertex must cancel. In each component the remaining terminal coefficients
sum to zero, and hence are combinations of terminal differences. A path
sum proves the reverse inclusion. Appending any old query or other mark
does not change this projection argument.

For three terminals the five partitions give just

    0, span(G), span(F+G), span(F), span(G,F+G).

The star (1), with hub H, realizes all five. Since (3) proves transfer
for every star subset, it proves exactly the same marked conditions for
every graph edge subset. This is an unbounded proof, not an enumeration
of all finite graphs. The primary program also checks all 32 base subsets
and all 16 subsets of the difference configuration d,b,t,-F.

## Actual-reader consequence and limits

Apply the retained support-to-tariff proof in the canonical live input
research/p112-query-series-transfer/PREDECESSOR-PROOF.md. For a literal
operator aa^T+bb^T=sum u_i q_i^T in this characteristic-zero indexed
configuration, (2) constructs characteristic-two factors with every old
query and reader zero preserved. Complete-plane support closure preserves
inclusion, so each binary Gram rectangle's charged rank cannot increase.
Expanding the full alternating-half indicator identity over GF4 gives
I_(2n). The unchanged indicator terms charge 2n-m_A-m_B. Rank
subadditivity then gives the original actual-reader floor

    sum_i C(u_i,q_i) >= m_A+m_B.

The inherited proof covers every finite positive even binary-orthonormal
partition and arbitrary external readers. Its exact bytes, provenance,
and credit are retained through SOURCES.json and ORIGINS.json. The
finite field extension is used only in the support argument, not as a
new physical decoder operation. No literal saving is claimed. PR3547's
retained six-term literal control still costs 14 against baseline 4.

Other failed placements, repeated or larger-port attachments, other old
characteristics, masked identities and changed closure remain open.
Acquisition, coefficient execution, dirty restoration, physical frames,
hosting, precision, stock, compiler/all-size admission, a complete consumer
and both supplier invoices are not supplied. No new kappa or selected
frontier change follows. The mathematical proof is author-written;
independent human and formal proof-kernel review are unclaimed.

Credit stays with Philippe Van Velzen's expanded-identity argument, ctoth's
coverage question, the actual-reader lineage through PR3414/3463/3472/3489/
3491/3505, and Nick Petalas's PR3506/3524/3535/3547. This contribution
adds the alternate map, its exact binary obstruction and the resulting
restored shared-port family.
