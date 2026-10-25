# Independent P8-extension audit

20 October 2026. This is a local, exact result for one six-query coefficient
matrix and one physical embedding of its three marks. It is not a classification
of P8 extensions or a global decoder lower bound.

The standalone standard-library replay is `independent_check.py`; its compact
receipt is `INDEPENDENT-RESULT.json`. It authenticates the original candidate and
label-data bytes, imports no producer code, and exhausts the objective without
branch-and-bound pruning. The other checker uses branch-and-bound. Both rebuild
all coverage and record a comparable digest of all 324 source-stratum minima.
Default replay is read-only; `--write-receipt` explicitly replaces this
checker's receipt. No scratch file, Git checkout metadata, or network is used.

## Representation and characteristic obstruction

Use coefficient coordinates `(c0,c1,c2,h)` and queries

```
q0 = h                 q1 = c1+c2+2h
q2 = c0+c2+h           q3 = c0+c1+h
q4 = 2c0+c1+c2         q5 = c0+h.
```

The first five queries together with the three marks restrict to the literal
P8 representation `[I4|D]` in Choe--Oxley--Sokal--Wagner, Example 11.8 (11.6),
Appendix A.4 (A.1), as cited in this package's source metadata.
The exact entries `2` have not been replaced by ternary `-1` entries.
The independent replay verifies rank four, all 70 maximal minors, and exactly
the ten declared nonbases. Every nonzero maximal minor has absolute value a
power of two.

The stated all-characteristic obstruction also passes an independent algebra
check. Basis replacements force the zero/nonzero pattern of D. Seven nonzero
entries forming a spanning tree in the row/column bipartite graph can be scaled
to one, leaving

```
0 1 1 a
1 0 1 b
1 c 0 1
d 1 e 0.
```

The two corresponding 2x2 incidences give `b=e=1`. The four remaining incidences
give `c+1-cd=0`, `d+a-acd=0`, `d+a-ad=0`, and `1+c-ac=0`.
The replay expands these six formal determinants, not sampled evaluations.
The first two imply `d=ac`; the fourth implies `d=c+1`; the first then implies
`(c-1)(c+1)=0`. Since `d` is nonzero, `c+1` is nonzero, hence `c=1` and `d=2`.
This excludes every characteristic-two representation of the marked matroid.
It does not exclude weaker support transfers or prove any tariff saving.

## Exact source and reader reduction

The physical marks are axis zero of ordinary roles 8, 14 and 15:

```
groups:  17,18,29,30,31,32
marks:   {0,67}, {7,64}, {1,75}.
```

Let C contain these three disjoint indicator columns, F=`[C|h]`, and A be the
fixed 4x6 matrix above. For any original rank-four F, an exact recovery
`F A R = C C^T` forces `A R[:,p]=e_j` at each port of mark j, and zero at every
other port. The reader columns outside the six marked ports can therefore be
zeroed. After that, h outside those six source ports can be zeroed without
changing the endpoint: every retained reader has zero fourth demand. Both
operations only shrink physical supports.

For each remaining scalar source coordinate x, the six query entries are
affine functions of x. Their complete zero roots are `{0,-1}` at mark 0 and
`{0,-1/2,-1}` at marks 1 and 2. Any other x has no additional zero, and replacing
it by zero can only delete query incidences. Thus 2^2*3^4=324 source patterns
cover every rational h of original rank four. Some resulting F have rank three;
they are included only with the inherited coefficient equations `A r=e_j`.
The extra readers available for an independently posed rank-three F are not
included or excluded by this result.

For each actual reader port, enumerate all 64 query subsets whose span contains
its unit demand. Every feasible subset contains an inclusion-minimal one. Such
a minimal set is independent: a dependent column could be removed without
changing its span. Its unique rational recovery uses every member. The replay
finds exactly 5,6,6 minimal supports for the three demands, and reconstructs all
their coefficients by inverting their Gram matrices. The two physical copies
of a mark choose independently; no equal-reader assumption is imposed.

These give 5^2*6^4=32,400 reader support patterns for every source pattern.
Replacing arbitrary reader supports by minimal ones only shrinks whole-group
costs. Every listed source/reader combination really has the coefficient
endpoint, so this finite optimization is exact for the retained constraints.

## Literal whole-group invoice and result

Every tariff is recomputed from complete physical triads using binary rank,
including all nonselected payload axes. All 64x64 group rectangles are rebuilt.
The replay exhausts all 324*32,400=10,497,600 objective cells without pruning.
Its digest uses the ordered product of twice-h alphabets `(0,-2)` for the first
two ports and `(0,-1,-2)` for each of the other four. Each digest row records
twice-h, literal embedding rank, six source masks and exact minimum. The minima
are

```
cost      18  21  22  23  24  25  26
strata    10  10  13  24  25  60 182.
```

There are 306 rank-four and 18 relaxed rank-three strata. Six rank-four strata
attain 18. Consequently every rational rank-four exterior h for this fixed
matrix, marking and placement has cost at least 18. Equality is attained, so
this local mechanism cannot improve the canonical three-mark baseline.

The original `h=c0_left-c0_right` has minimum 21. The stronger specialization
`h=-c0_right` has minimum 18. It changes source group masks from
`[3,63,49,13,63,1]` to `[2,62,49,13,63,1]`, termwise subsets; all 384 reader-mask
tariff comparisons confirm dominance. One exact equality witness uses

```
c0 = q5-q0,   c1 = q3-q5,   c2 = q2-q5,
```

with reader group masks `[3,0,48,12,0,63]` and charges `[3,0,6,6,0,3]`.
Both fixed witnesses are independently checked on all 112^2 scalar entries.

Each of the six rank-four minimizing strata has a unique minimal-reader
optimizer, and all omit q1 and q4, the two dense P8-specific queries. After
reader columns outside the six marked ports have been deleted, either dense
query has strictly positive cost with any remaining nonzero reader; therefore
extending that minimal-reader optimizer cannot add either query at the same
price. This statement is about those six finite strata after the stated
reductions, not every exterior h or unreduced reader before them. The collapsed
rank-three stratum `h=-c0` has 24 further tied minimal
patterns that do use dense queries, so no such assertion is made for it.

An underpriced invoice and a corrupted reader coefficient are rejected by
separate controls. A rank-collapse control sets h=0: the literal query q5 then
recovers c0 alone, although `A e5=e0+e3`, explicitly demonstrating an extra reader
outside the inherited coefficient constraints. Nothing here claims a
better-than-334 global decoder,
another physical placement, another ninth point, or all readers of a genuinely
rank-three source embedding.
