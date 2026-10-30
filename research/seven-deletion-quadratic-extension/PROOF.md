# Quadratic extension and the sharp seven-deletion boundary

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.

## Theorem and scope

Use the doubled E8 root lines and FRAME0 ordering from Josie Elliston's
PR1650. Let P112 be the complement of FRAME0. For every X subset of P112 with
|X|<=7, set L=P112 minus X and let M_L be the incidence matrix of **all**
orthogonal eight-line frames contained in L, with columns L.

1. The kernel of M_L over every characteristic-zero field is exactly the
   35-dimensional space of restrictions of ambient trace-zero quadratics.
   Each such extension is unique.
2. For every live pivot frame F in L and each pivot coordinate k, condition
   D of Andrey Mas's PR1560 holds: the frame incidence on I_k has rank
   |I_k|-7 and its kernel is the span of the seven canonical h_kl vectors.
   No W, G or nonempty-block premise is needed for this conclusion.
3. Seven is sharp for the all-pivot conclusion. Josie Elliston's PR1668
   supplies eight-deletion examples with W, G and nonempty blocks but not D.
   Those examples and their discovery remain predecessor work.

This is a finite, complete computational proof plus uniform linear algebra.
The orbit cover, root geometry and E7 support theorem are credited inputs.
The new certificate checks the global incidence rank on every deletion class;
it does not repeat the earlier search for one passing pivot per class.

No new rigidity floor, physical supplier or kappa follows. PR1650 already
supplied rigidity at P105 through a suitable pivot. This result removes the
choice of pivot from the D obligation and completes the precise extension
handoff. It does not prove G or W for every pivot. It does not address nine
or more costly terms, native realization, routing, ownership, restoration,
precision, preparation or the full recursive bill. The selected .00310045
frontier and its main-transform bottleneck are unchanged.

## 1. Uniform injectivity of quadratic evaluations

The roots have norm squared eight. On the real vector space of symmetric
trace-zero 8 by 8 matrices with the Frobenius inner product, put
R_v=vv^T-I. Then

```text
<R_v,R_v> = 56,
|<R_v,R_w>| = 8 for distinct root lines,
sum_v <H,R_v> R_v = 192 H.
```

The verifier checks the last identity on a full rational basis of 35 forms,
the first two identities on the complete root set, and zero sums on all
2025 frames. Thus the full evaluation operator has squared norm identity
192 I. For any t deleted root lines, the Gram matrix of their R_v has
operator norm at most 56+8(t-1), by the absolute row-sum bound. For t<=17
this is at most 184<192. The remaining evaluations are therefore injective.
This argument proves a bound for every deletion set; it is not a sample.

In our theorem t=8+|X|<=15. Thus the restrictions of trace-zero quadratics
have dimension 35 on L. They lie in ker(M_L), since the eight equal-length
orthogonal roots of a frame have sum of outer products 8I. It remains to
prove rank(M_L)>=|L|-35. The next section supplies this lower bound for
every X. Together the bounds give equality and the extension assertion.

The real positivity argument produces a rational matrix rank statement.
Every such nonzero rational minor stays nonzero in every characteristic-zero
field. Both the injectivity and the extension conclusion therefore hold over
all those fields, without an order or positivity assumption on the field.

## 2. Complete deletion cover and new rank certificate

The retained PR1650 source constructs the 120 lines and all 2025 frames.
Its eight FRAME0-stabilizer generators generate a group H of order 172032.
The verifier rebuilds H, checks that each generator is a permutation fixing
FRAME0 and preserving every frame, and checks the full orbit-cover chain.
These maps come from orthogonal root reflections and preserve quadratic
restrictions and the incidence problem.

For deletion sizes zero through three, the package regenerates the complete
orbits directly. They have 1,1,5,24 representatives. For sizes four through
seven it uses the retained PR1650 data, and checks every candidate transporter:

| Deleted lines | Candidates checked | Representatives |
|---|---:|---:|
| 4 | 2517 | 180 |
| 5 | 18782 | 1614 |
| 6 | 156627 | 19295 |
| 7 | 1651528 | 242802 |

The triple orbits cover all 227920 triples. Every k-subset has a (k-1)-subset;
move that subset to a retained representative and add its remaining point.
Each resulting candidate is checked to be an actual H-image of its listed
k-unit. This induction proves coverage of all subsets, without trusting a
claimed count of distinct orbits or the original grouping algorithm.
The new package checks source hashes, all indices and lengths, all unit
memberships, every transporter and the absence of trailing cover data.
The data and this induction are Josie Elliston's predecessor contribution.

For all 263922 retained units of sizes 0 through 7, the new verifier enumerates
all frames disjoint from FRAME0 and X and row-reduces their incidence modulo3.
It obtains rank112-|X|-35 in every case. A nonzero minor modulo3 is a
nonzero integer minor, so this is a lower bound over Q. Section 1 supplies
the matching upper bound. Transport through H gives the rank for every X.

For speed, a ternary row has two disjoint bit planes, for coefficients 1 and 2.
The code implements the nine field additions by Boolean operations; its
row reduction uses only nonzero pivot scaling and row additions. A retained
PR1650 routine orders the rows by new columns before elimination. It changes
only row order. The new packed elimination is checked against separate dense
modulo3 elimination on 512 matrices, all nine scalar additions and deficient
frame-family controls. It stops once the required lower bound is reached;
the matching upper bound is the written geometric proof, not that stop rule.
The registered parts partition the complete unit list with disjoint strides.
No pivot from the retained unit records is used by this rank calculation.

## 3. Seven canonical directions remain independent

Fix a root a in P112. Among the other root lines, 56 are nonorthogonal to a.
For each such doubled root b, put u_b=2b-(a dot b)/4 a. These vectors lie in
a-perp. Exact full-geometry checks give

```text
||u_b||^2 = 24,
sum_b u_b u_b^T = 192 I - 24 a a^T,
```

and each u_b has exactly one distinct twin with absolute inner product24.
Its inner product with every other distinct vector has absolute value8.
On a-perp the sum is192 I. Four of the 56 lines belong to FRAME0. At most
seven more are in X. For any removed set of at most 11 projected vectors,
its Gram operator norm is at most24+24+9*8=120<192. Therefore the surviving
projected vectors span all seven dimensions of a-perp.

At a live pivot F, put a=F[k]. The other seven pivot roots are a basis of
a-perp. The functions h_kl(i)=G_ik G_il on I_k are the corresponding cross
terms. Since G_ik is nonzero on I_k and the projected vectors there span
a-perp, these seven functions are independent. Other pivot roots are
orthogonal to a and hence do not remove any of the 56 vectors. This proves
independence for every deletion set in scope and every live pivot, with no
W, G or block-completeness hypothesis.

## 4. Every local kernel vector is canonical

Take z in the kernel of the live-frame incidence on I_k. Extend z by zero to
all other live lines, including the whole pivot. This new function has sum
zero on every live frame, so Sections 1 and 2 give a unique trace-zero ambient
quadratic q extending it. In particular q(a)=0. Its restriction to a-perp
therefore has trace zero.

The full E7 slice orthogonal to a has 63 root lines. Exactly four belong to
FRAME0 and at most seven more to X. On all the other orthogonal lines q is
zero. If the restriction were nonzero, it would have support at most 11.
Nick Petalas's PR5238 theorem gives minimum support 12 for a nonzero rational
trace-zero restricted quadratic. The package replays its complete
134217727-word binary certificate and root-transitivity check. The same
bound holds over every characteristic-zero field: a nontrivial solution of
the rational linear equations imposing trace zero and the stated zeros
would also give a nontrivial rational solution, since ranks do not change.
Thus the restricted quadratic is zero.

A symmetric quadratic whose restriction to a-perp is zero and whose value
at a is zero consists only of cross terms between a and a-perp. Its values
on I_k are in the span of the seven h_kl. Conversely those seven vectors
have zero sums on every full frame, because the pivot roots are orthogonal.
Section 3 proves their independence. Hence the local kernel has dimension 7
and its rank is |I_k|-7, which is D. This holds for every live pivot at once;
no census of individual pivots is substituted for the argument.

## 5. Sharpness and acceptance limits

The two retained PR1668 fixtures have eight deleted lines and all live
frames. The replay checks W, G, nonempty blocks, the exact rational rank
loss, an eighth independent integer kernel vector, and damaged-vector
rejection. Restoring any one deleted line gives 128 checked pivot-coordinate
ranks across the two fixtures, consistent with the new theorem. The global
incidence rank is 69 on both 104-line boundary sets, so quadratic extension
still holds there: sixteen missing roots are within the uniform injectivity
bound. These D failures therefore do not imply extension failure. Their
counterexamples are credited results, not new discoveries.

The complete finite rank certificate is not a proof-kernel certificate.
The source orbit cover and E7 support code are independently replayed, but
this is not independent human review. The packed-versus-dense comparison is
an algorithmic cross-check, not an exhaustive equivalence proof of arbitrary
program execution. Its nine-case arithmetic proof and ordinary elimination
argument supply that general justification. See RESULT.json and VALIDATION.md
for the executed commands, full coverage and portability checks.

## Credit and sources

- [Josie Elliston PR1650](https://github.com/CrocSwap/integer-mult-bounds/pull/1650): complete deletion orbit cover, data, geometry and row-ordering method.
- [Josie Elliston PR1668](https://github.com/CrocSwap/integer-mult-bounds/pull/1668): sharp eight-deletion boundary, D4 explanation and exact witnesses.
- [Andrey Mas PR1560](https://github.com/CrocSwap/integer-mult-bounds/pull/1560): the D/G/W structural criterion and projector proof.
- [Nick Petalas PR5238](https://github.com/CrocSwap/integer-mult-bounds/pull/5238): sharp trace-zero E7 support twelve and its complete binary certificate.
- [JoyboyBrian's handoff](https://github.com/CrocSwap/integer-mult-bounds/discussions/1502#discussioncomment-19145642): the extension/support reduction and its precise open quantifiers.

PR1616, Aaron Wang PR1649 and the retained Brett Halligan, themilkman216 and
DreamingOfClouds lineage supply prior E8 geometry and incidence work. All
source files and notices stay byte-exact. SOURCES.json binds their canonical
main objects. The new contribution is the uniform quadratic-injectivity and
cross-term bounds, the complete global rank certificate, and the resulting
all-pivot theorem. No global literature priority is claimed.
