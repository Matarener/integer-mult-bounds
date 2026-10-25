# A two-hub obstruction to characteristic-two marked transfer

## Statement

Over any field of characteristic different from two, take independent
E,F,G,H,K. Mark E,F and index nine queries by `gdthxykzw`:

    g=G, d=E+F, t=E+F+G,
    h=H, x=E+G-H, y=F+G-H,
    k=K, z=E+G-K, w=F+G-K.                 (1)

The six queries h,x,y,k,z,w are the edges of K3,2 with terminal potentials
0,E+G,F+G and independent internal potentials H,K. There is no edge H-K.
The unreplaced queries are g,d,t. Reversing an old edge orientation does
not change any subset span.

A marked support transfer assigns independent e,f and nine arbitrary
query images over a characteristic-two field, in any ambient dimension,
such that for every indexed query subset S, in both marked orientations,

    E outside span(F,Q_S) implies e outside span(f,q_S),
    E in span(Q_S) implies e in span(q_S).           (2)

No such transfer exists. The images may depend on the entire graph.
They need not be endpoint differences, have fresh internal directions,
preserve g,d,t, preserve unmarked dependences, or have bounded rank.

Thus the exceptional single-star transfer of PR3573 cannot extend to
every finite graph by choosing graph-dependent images. This theorem
does not say that the literal pair tariff can be lowered, nor that its
floor holds for every graph. It excludes this sufficient support-transfer
method on the specified graph.

## The exact premises

Reusing lower-case letters for arbitrary new images, (2) forces these
seven source exclusions:

    e outside span(f,g,h,k);  f outside span(e,g,h,k);
    e outside span(f,h,x);    e outside span(f,g,x);
    e outside span(f,g,h,z);
    f outside span(e,g,y);    f outside span(e,h,y).  (3)

It also forces fourteen reader containments:

    e in span(g,h,x);         f in span(g,h,y);
    e in span(g,k,z);         f in span(g,k,w);
    e in span(t,h,y);         f in span(t,h,x);
    e in span(t,k,w);         f in span(t,k,z);
    e,f in span(d,x,y);       e,f in span(d,z,w);
    e,f in span(g,t,x,y).                           (4)

Both programs verify these predicates over Q separately from their
complete 512-subset table. WITNESS.json supplies an integer separating
functional for every source predicate and a decomposition with
denominator dividing two for every reader predicate. The programs
check those certificates entry by entry. Consequently (3)-(4) hold in
the old configuration over every characteristic different from two.
No extrapolation from a few tested primes is needed. The other subset
ranks in RESULT.json are measured over Q only.

## The all-field contradiction

Suppose (3)-(4) hold over a characteristic-two field L. Put
W=span(e,f) and U=span(g,h,k). The first two exclusions give W intersect
U=0. Indeed any nonzero vector ae+bf in U would put e in span(f,U)
when a is nonzero, or put f in U when a is zero.

The reader e in span(g,h,x) and the source exclusion involving h,x
force g to be nonzero. The same reader and the exclusion involving g,x
force h outside span(g). If k were in span(g,h), the reader
e in span(g,k,z) would contradict the exclusion involving g,h,z.
Therefore e,f,g,h,k are five independent vectors, regardless of the
original proposed ambient dimension.

The first four readers now give

    x=a e+u g+v h,       y=b f+s g+r h,
    z=c e+u' g+v' k,     w=b' f+s' g+r' k,         (5)

where a,b,c,b' are nonzero. The h,x and g,x exclusions imply u,v
are nonzero. The g,y and h,y exclusions imply s,r are nonzero.
The g,h,z exclusion implies v' is nonzero. We need no nonzero
assumption on u',s',r'.

The reader e in span(t,h,y) forces t in W+span(g,h), since e is
outside span(h,y). Likewise e in span(t,k,w) forces t in W+span(g,k).
Independence gives

    t=A e+B f+C g.

The readers e in span(t,h,y) and f in span(t,h,x) give A and B
nonzero. Comparing the f,g coefficients in the first reader equation
and the e,g coefficients in the second gives

    C=A u/a=B s/b.                                  (6)

In particular C is nonzero.

The containments e,f in span(d,x,y), with x outside W, imply

    span(d,x,y)=W+span(x).

The left side has at most dimension three and contains both the
two-dimensional W and x. Similarly span(d,z,w)=W+span(z). Modulo W,
the images of x and z are u g+v h and u' g+v' k. They are independent
because v,v' are nonzero and g,h,k are independent. Intersecting the
two three-dimensional spaces therefore gives d in W.

It follows that the non-W parts of x and y are proportional. Write

    lambda=s/u=r/v,       R=x+lambda^(-1)y
                           =a e+(u b/s)f.          (7)

All the displayed divisors are nonzero. Characteristic two supplies
the plus sign in (7). Equation (6) now gives

    t=(A/a)(R+u g).

Consequently span(g,t,x,y)=span(g,x,R). Its intersection with W is
exactly the line span(R). To see this, a combination of g,x,R lying
in W must have zero h coefficient, forcing the x coefficient to be
zero because v is nonzero. Its g coefficient must then also be zero.
This one-dimensional intersection cannot contain both e and f,
contradicting the final two readers in (4).

This proves impossibility over every characteristic-two field in
every dimension. Finite field search is not the impossibility proof.
Any graph containing these same six terminal-to-hub edges with fresh
H,K has the same obstruction, since restricting a proposed transfer
to these nine queries preserves (3)-(4). Subdivisions, arbitrary graph
minors and edge-minimality are not classified here.

## A concrete literal factorization has no support-shrinking completion

WITNESS.json realizes all twenty-one premises in one exact rational
factorization. For each source premise it stores a functional phi
with phi(E)=1, phi(F)=0, or the opposite values, vanishing on that
premise's queries. For each reader premise it stores coefficients
expressing the corresponding mark using exactly allowed query indices.
Default readers at source-witness rows use ghx for E and ghy for F.
Functionals at reader-witness rows are the relevant coordinate functional.

There are twelve E rows and nine F rows. Order E rows first, then F
rows, and insert a zero companion port after each row. This gives 42
ports, partitioned into binary Gram-I groups of sizes 24 and 18.
Pair every row with its companion into a complete two-port plane.
Let a,b be the alternating-half indicators supported on the E and F
rows. Their other halves are untouched indicators.

Define q_i(p)=phi_p(Q_i) on an active row and zero at its companion.
Let u_i(p) be its stored reader coefficient, again zero at companions.
The checked identity sum_i u_i(p) Q_i=E or F, followed by evaluation
at phi_r, proves every entry of

    aa^T+bb^T=sum_i u_i q_i^T.                       (8)

Both implementations check all 1,764 entries. The actual query and
reader ranks over Q are five and six.

Suppose any characteristic-two field admitted an exact realization
of the same right-hand target using nine pairs u'_i,q'_i whose scalar
supports are contained term by term in those of u_i,q_i. At every
stored source row, its coordinate functional is one on its marked
indicator, zero on the other, and zero on the specified q'_i. Hence
the seven exclusions (3) hold for a,b,q'_i. At every stored reader
row, (8) expresses a or b using only the specified q'_i. Hence (4)
holds as well. The contradiction above rules this out, without a
rank or span restriction on the new literal factors.

This is an obstruction to simultaneous scalar support inclusion.
It is stronger than failure of a chosen abstract boundary map. It
does not exclude a different characteristic-two realization with
nonincluded supports or a smaller Gram tariff obtained by another
argument.

For binary Gram-I labels, each rectangular complete-plane charge is
twice the number of active rows where both factors are nonzero. The
measured nine charges are

    [4,8,12,4,10,8,0,4,4], total 54, baseline 42.

The independent program builds the actual rectangular binary Gram
matrices and computes their ranks. This witness loses by twelve.
Neither the bill nor this construction is claimed optimal.

## Positive boundary and remaining obligations

The retained exceptional single-star map from PR3573 still passes all
64 subsets over Q and GF4. Its unreplaced d,t images use the one hub
direction. The second independent hub forces d into W and t into
W+span(g), which is precisely the freedom that the contradiction
removes. Merely having a cycle is not claimed to characterize failure.

The original working hypothesis allowed either a transfer or an
obstruction for a two-hub cyclic graph. This negative result settles
that finite attachment question. It does not classify all exceptional
graphs, prove their minimum literal tariff, supply a cheaper decoder,
change the coverage identity, or establish a physical supplier or kappa.
Acquisition, coefficient execution, dirty restoration, frames, hosting,
precision, stock, compiler/all-size admission, complete consumers and
both supplier invoices remain unrun. No selected frontier is changed.

The proof is author-written. Independent human and formal proof-kernel
review are unclaimed. Credit retains Philippe Van Velzen's expanded
identity, ctoth's coverage question, the actual-reader lineage, and
Nick Petalas's PR3506/3524/3535/3547/3557/3573. The new result is the
arbitrary-map K3,2 obstruction and its explicit literal realization.
