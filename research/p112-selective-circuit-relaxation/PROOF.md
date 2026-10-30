# The three-hub Dowling dictionary still transfers selectively to F4

21 October 2026. Local exact deduction inspired by a signed-graph configuration. No improved decoder or new multiplication bound.

## Candidate and primary provenance

Thomas Zaslavsky, [Signed Graphs and Geometry](https://people.math.binghamton.edu/zaslav/Tpapers/sggm.pdf), Section 5.6, PDF page 24, gives the complete signed-graph vector configuration consisting of coordinate vectors and pairwise sums/differences. Take its rank-three instance. Mark the three positive links

`a=e0+e1`, `b=e0+e2`, `c=e1+e2`,

and use its six other points as queries. In the marked basis, after harmless nonzero column scalings, the query columns are

```
q0=( 1, 1,-1)    q3=(0, 1,-1)
q1=( 1,-1, 1)    q4=(1, 0,-1)
q2=(-1, 1, 1)    q5=(1,-1, 0).
```

This gives three genuinely dense signed hubs and three shared differences. It is different from a single total-sum hub and from the fixed rank-four P8 extension. Nevertheless its selective recovery obligations are too weak to retain its full characteristic-dependent incidence structure.

## Explicit support-dominating replacement

Over `F4=F2(w)` with `w^2+w+1=0`, replace those columns by

```
b0=(1,1,1)      b3=(0,1,1)
b1=(w,1,1)      b4=(1,0,1)
b2=(1,w^2,1)    b5=(w,1,0).
```

Every column has exactly the original nonzero coordinates. For every subset S of the six queries and every target axis e_j,

`e_j in span_Q {q_i:i in S}` implies `e_j in span_F4 {b_i:i in S}`.

The standalone exact replay `verify.py` checks all 192 requests using rational and F4 elimination. Every target has 42 recoverable old supports, all retained among 43 new supports. Each has ten inclusion-minimal old supports.

There is also a short explanation. All query pairs are independent. The nine two-query target recoveries are the three pairs inside each of

`{q0,q1,q3}` for a, `{q0,q2,q4}` for b, `{q1,q2,q5}` for c.

They all survive. The rational query configuration has just four dependent triples: those three displayed triples, and `{q3,q4,q5}`. Every old independent triple stays independent over F4. The last triple becomes independent; its old span contained none of the three marked axes. Thus releasing this query-only dependence loses no target recovery. Larger supports contain a pair recovery or a rank-three basis, so the implication follows for all supports.

The primary signed-graph source supplies the configuration. The marked choice, explicit F4 replacement, selective-transfer argument, and P112 consequence are local deductions.

## Arbitrary actual readers and physical placements

Let C contain any three disjoint nonzero indicator columns, including unequal numbers of copies, and let the actual query matrix be `C Q`. Suppose arbitrary rational actual readers R satisfy

`C Q R = C C^T`.

Injectivity of C gives `Q R=C^T`. At an actual port belonging to mark j, its active query indices therefore span e_j over Q. Choose F4 recovery coefficients on those same indices using the implication above. At every port outside the marked indicators choose the zero reader. This constructs `R'` with no larger reader support and

`C B R' = C C^T` over F4.

Because the indicators are disjoint and Q and B have the same coordinate-zero patterns, every actual query has unchanged support. Consequently every complete physical-group source/reader rectangle shrinks or stays the same. Binary rectangle rank is unchanged by extension from F2 to F4, so every term tariff weakly decreases in the transfer.

For three ordinary canonical P112 projectors the expanded binary endpoint is I18. Rank subadditivity forces bill at least 18 for this entire dictionary, for every physical placement and every actual reader, including asymmetric paired copies. The appropriate unchanged canonical bill applies to other marked copy multiplicities. Keeping all other canonical projectors gives the full invoice floor 334.

Nonzero rescaling or duplication of a query ray causes no difficulty: absorb scalings in its reader, and assign duplicate copies the same transferred query with their original separate supports. This is not a theorem about arbitrary extensions by new query rays.

## Why full matroid nonrepresentability is not enough

The replacement is deliberately not a representation of the complete old matroid: the query-only difference triangle has rational rank 2 and F4 rank 3. That change is a positive control, not an error. A decoder needs the marked target recoveries, and is allowed to gain extra recoveries. Screening new dictionaries only by characteristic-dependent full-matroid representability therefore retains false leads.

The replay additionally checks all 512 subsets of the augmented nine-element configuration `[I3|Q]` versus `[I3|B]`: this query-only triangle is the **only** subset whose rank changes. Thus the F4 representation is exactly its circuit-hyperplane relaxation.

## General query-only relaxation lemma

Let `N=[I_r|A]`, `r>=2`, be the augmented matroid with marked basis E and query columns. Let H be a circuit-hyperplane containing no marked element. Relax H, and suppose the relaxed matroid has a characteristic-two representation. Normalize its marked basis to I_r and call the remaining columns B.

Then B has the same coordinate-zero pattern as A and preserves every old marked recovery. Relaxation adds H to the set of bases; H has size r, every proper subset is independent, and every proper superset already has rank r because H is a hyperplane. Thus the rank of only H changes, from `r-1` to r. For a query set S and marked e, the equality `rank(S+e)=rank(S)` can be lost only if S+e=H, impossible because H has no marked element. When S=H the old equality was false because H is a hyperplane avoiding e; the change can only add a recovery. Finally, a coordinate A_ij vanishes exactly when q_j lies in the span of `E minus e_i`. The determining set contains marked elements and cannot be H, so the zero condition is unchanged.

This proves a support-dominating characteristic-two decoder transfer whenever such a representable query-only relaxation is supplied. It applies successively to several query-only relaxations. It does **not** assert that a suitable relaxation or representation always exists. The local Dowling witness supplies both explicitly.

### Conditional stressed-hyperplane corollary

The same conclusion holds for a query-only **stressed hyperplane** H: each
r-element subset of H is a circuit. Ferroni, Nasr and Vecchi, [Stressed
Hyperplanes and Kazhdan-Lusztig Gamma-Positivity for Matroids](https://arxiv.org/pdf/2110.08869),
arXiv:2110.08869v2, Theorem3.4 and Proposition3.7, establish this relaxation
and show that ranks increase exactly for sets S contained in H with |S|>=r.
For our marked-recovery application, none of those sets previously spanned a
marked target, because H avoids the marked basis. A set containing a marked
target never changes rank. Coordinate-zero tests contain r-1 marked elements,
so they also remain unchanged. Normalizing a supplied characteristic-two
representation therefore gives the same support-dominating transfer. The paper
does not guarantee such a representation; that remains a separate premise.
The six-query witness above uses the circuit-hyperplane special case.

The next mechanism must obstruct **selective** recovery after permissible query-only dependences are released. Enlarging or physically repricing this six-query dictionary is unnecessary.

## Self-contained full-group invoice argument

The only scientific inputs are the canonical indicator supports and physical
groups in `research/p112-rational-decoder-gate/CANDIDATE.json`, and their binary
nine-coordinate labels in `research/adaptive-kernel-demotion/inputs/DATA-PHASES.json`.
The replay authenticates both SHA256 pins before using them. No pending
sparse-transfer package or theorem is an input.

Write g(p) for the complete physical group containing scalar port p, and v_a
for the binary vector at physical coordinate a. Expand a scalar matrix M to
rows/columns indexed by (p,a), a in g(p), by

`E(M)[(p,a),(q,b)] = M[p,q] <v_a,v_b>_F2`.

The replay checks all 111556 entries of `E(CC^T)=I334`. For an outer product
`u v^T`, delete zero scalar rows and columns. The remaining expanded matrix is
obtained from the binary pairing rectangle between the complete group unions
touched by u and v by row/column replication and nonzero scalar scaling.
Its rank over F4 is therefore at most the binary rank of that full rectangle,
which is the term tariff. Extension of F2 to F4 does not change the rank of a
binary matrix. Thus rank subadditivity gives `334 <= sum tariffs` for every
F4 factorization of this endpoint.

For any subset of canonical marks, retain only its expanded coordinates. Its
endpoint is the corresponding principal identity submatrix: other scalar
rows and columns are zero. The replay checks each of the 57 canonical term
tariffs equals its expanded dimension: three costs 3, fifty-three costs 6,
and the residual-bearing cost 7, summing to 334. Hence any three ordinary
marks give I18 and baseline18. It checks one such 18-by-18 restriction
explicitly; the all-entry I334 identity and all mark dimensions establish
the same conclusion for every choice of three ordinary marks.

The selective replacement proved above weakly shrinks each term's physical
rectangle. Applying the F4 rank lower bound to the transferred decoder yields
the same lower bound for the original rational decoder. This prices whole
physical groups, not individual selected scalar coordinates.

## Replay

`python3 -I -O -Werror -B research/p112-selective-circuit-relaxation/verify.py`

The default is read-only and compares the saved JSON receipt. `--write-receipt` explicitly regenerates it. This finite certificate supports the stated fixed-dictionary theorem; it is not a census of rank-three configurations.

Prepared for flyingviper with substantial OpenAI Codex assistance. Separate Codex agents audited the mathematics and implemented independent exact checks; no independent human or formal-kernel review is claimed. Repository contribution: Apache-2.0.
