# Exact universal axis capacity of the reservoir majorant

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: scoped mathematical proof with exact finite corroboration.
The object optimized here is the inherited conservative factor-3 envelope.
Its failure is not failure of the actual repair algorithm or actual error.

## Contract

Use Hiroki KUMAZAKI's PR4174 constructor, at the source pinned in
SOURCES.json. An accepted layout has integers p>=1, c=ceil(log2(p+2)),
ell>=max(2,c), a power of two d>=65536, and d widths in {ell-1,ell}.
If a widths equal ell, its address length and maximum batch are

```text
L = d(ell-1)+a,  0<=a<=d,
G = 64(ell+c),
r_max = floor(L/(100G)) = floor((d(ell-1)+a)/(6400(ell+c))).
```

The minimum allowed d is 65536 because the constructor requires a power
of two at least 51200. Every displayed parameter tuple passes its batch
positivity and volume checks: L/(100G)>=d(ell-1)/(12800ell)>=d/25600>2.
No requirement L<=p is imposed by this constructor.

James Reed's PR4923 proves the conservative factor 3. PR4924/4925 derive
the printed-envelope ratio. We cite those arithmetic premises, without
replaying their verifiers or claiming their results as new. Relative to
C_E times the printed room, the conservative ratio is

```text
R = 3 r_max ((p+2)/2^c)^64.
```

The question is exactly whether R<=p/6400 for every accepted ell and width
pattern, at fixed p,d. C_E cancels. It is not evaluated or given a value.
This is a different question from R<=1/6400 or from evaluating the real E.

## The maximum batch is attained

Put k=floor(d/6400). Then

```text
max_(ell,a) r_max = k.
```

For the upper bound, L<=d ell and ell/(ell+c)<1, so
r_max<d/6400. Since d is a power of two and 6400=2^8*25, d/6400 is not an
integer; hence r_max<=k. Define the positive remainder delta=d-6400k.
For all widths equal ell, r_max>=k if and only if

```text
d ell >= 6400k(ell+c),
(delta) ell >= 6400kc.
```

Thus the maximum is attained at the finite precision

```text
ell_* = max(2,c,ceil(6400kc/delta)),  a=d.
```

This supplies an actual accepted layout, not merely a limiting supremum.
The minimum constructor precision and the open upper limit d/6400 both
matter. Replacing the floor by a rounded or floating-point limit is unsafe.

## The sharp capacity criterion

Define the nonnegative integer

```text
M(p) = floor(p 2^(64c) / (19200 (p+2)^64)).
```

The following conditions are equivalent:

1. Every accepted layout at p,d has R<=p/6400.
2. 19200 floor(d/6400) (p+2)^64 <= p 2^(64c).
3. floor(d/6400)<=M(p).
4. d<=6400(M(p)+1)-1.

The maximum-batch theorem proves the equivalence of 1 and 2, including
necessity by the attaining all-wide layout. Integer division proves 2 iff
3, and the definition of floor proves 3 iff 4. Equality is accepted.

Consequently let D(p)=6400(M(p)+1)-1. If D(p)<65536, no allowed dyadic axis
count passes uniformly in precision. Otherwise the largest allowed dyadic
count is 2^floor(log2(D(p))). All smaller allowed dyadic counts pass; every
larger allowed dyadic count has the explicit failure at ell_* above.

The simple sufficient condition 3d<=p follows as a corollary: then
19200k<3d<=p and ((p+2)/2^c)^64<=1. Unlike L<=p, it does not restrict ell.
It is a sufficient corollary, not the sharp criterion.

## No cutoff in p alone

For each fixed p, M(p) is finite. Choose a power of two

```text
d >= max(65536, 6400(M(p)+1)).
```

Then floor(d/6400)>=M(p)+1. The accepted all-wide layout at ell_* fails
the conservative inequality. This works for every p, however large.
Therefore no finite cutoff in p can make this majorant hold on all layouts
accepted by the constructor with unbounded d. A caller must control d or
supply a different bound. This does not assert that actual repair fails.

## Explicit boundary witnesses

At p=131070=2^17-2 and d=65536, c=17, M(p)=6, and k=10. For all-wide
layouts the inequality holds exactly when r_max<=6. For arbitrary width
patterns, all-wide maximizes r_max at each precision. The first failing
precision is therefore

```text
ceil(6400*7*17/(65536-6400*7)) = 37.
```

At ell=36, L=2359296, G=3392, r_max=6, and the ratio of the majorant to
the p/6400 allowance is 3840/4369<1. At ell=37, L=2424832, G=3456,
r_max=7, and that ratio is 4480/4369>1. Thus every allowed width pattern
passes for 17<=ell<=36, while the all-wide pattern fails at 37. These
layouts both have L>p. The verifier constructs them with the pinned Layout.

At p=2^24-2, M(p)=873 and D(p)=5593599. The largest uniformly covered
dyadic axis count is 4194304=2^22; the next count 8388608=2^23 fails at
its attaining precision. This classifies the entire precision/width family
at that p. It does not repeat PR4926's one-layout ratio 12.

## Verification and limits

The proof above supplies the unbounded quantifiers. The verifier checks
finite arithmetic boxes, all width-count patterns in its stated boxes,
the attaining precisions and their preceding seam, exact capacity neighbors,
and four actual Layout fixtures. It never executes predecessor verifiers,
the descriptor census, the repair program or the real E polynomial.
RESULT.json gives generated counts, source hashes and all control results.
Normal replay is read-only and rejects a changed receipt under -O.

Native operations, simultaneous carry correctness, evaluator implementation,
physical repair, memory, routing, restoration, all-size caller integration,
compiler and outer multiplication remain separate obligations. The selected
frontier is unchanged. No kappa, supplier admission or complete multiplication
theorem is claimed. Independent human and formal proof-kernel review are unclaimed.

## Code constraints

The new verifier has no recursion. Every enumeration has a fixed finite range
stated in the code and the receipt. Functions stay below 60 physical lines.
Explicit exceptions enforce contracts and receipt comparison under -O.

Power of Ten rule 3 has a managed-runtime deviation in verify.py: CPython
allocates integers, containers and source Layout prefixes. The finite fixture
has d<=65536; algebraic axis counts up to the stated finite probe exponent
are represented as integers rather than materialized axes. File reads are
capped at 1 MiB. The verifier releases one Layout before constructing the
next. These bounds limit live algorithmic data; runtime internals are not
allocation-instrumented. A native fixed-storage implementation would be
required before allocation-prohibited use.

Rules 8 and 9 have a source-execution deviation for the four Layout fixtures:
runpy executes exactly one SHA256-authenticated, repository-pinned allocator
and the checker calls its Layout constructor. It imports no predecessor
checker, accepts no user-selected executable, and has no network or Git
runtime dependency. The official read-only Git-free replay exercises this
boundary. The source retains its own implementation and attribution; its
unrelated routines are not changed or claimed compliant here.

Warning-strict normal and optimized replay provide the local diagnostics.
No static type checker is configured for this standalone package.
