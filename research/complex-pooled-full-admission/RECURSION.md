# Joint bound and the exact conditional boundary

Prepared for Ross Richardson with OpenAI Codex assistance. Apache-2.0.

This note prices Rohan Arun's PR4181 pooled fill using Cinna Davis's PR4088
words and yssite's PR4180 admission architecture. It supplies a complete
profile comparison, a source-bound joint arithmetic certificate and the
conditional recurrence implication. It does not turn finite admission into
an unconditional multiplication theorem. The completed release and its actual
invoice must be bound separately; `joint_bound.py` reports that distinction.

This note preserves the finite and legacy arithmetic branch. The later
source-specific physical binding and conservative `kappa=1/580` composition
are proved separately in [PHYSICAL-GLOBAL.md](PHYSICAL-GLOBAL.md) and
[OUTER-JOIN.md](OUTER-JOIN.md). They retain explicit source/analytic premises
and do not certify the stronger legacy number in this note. Statements below
about gaps left by finite arithmetic refer to that arithmetic, not a claim
that the companion physical work is absent.

The scientific base is `12fa8c5c844be21bfefb38a19503fbd867a11244`.
The consumed PR4181 head is `4ed92bed95dd483f5662e98ef246b258c3cfe64f`;
PR4180 is `15a4153e734a8d1d485c6d3bea9b1a8201328a4c` and PR4088 is
`72d7efc181edb21806a878f174847c96dd410ab0`. Frozen files retain their
original attribution. Historical statements below keep their original
compiler, exact-return and cost assumptions.

## 1. All local returns and idle children

The complete local profiles, including the rederived inverse cleanup, are

```
L3 = 2487 H1 + 713 H2 + 224 H3 + 102 H4 + 20 H5 + 8 H8,
L4 = 2489 H1 + 713 H2 + 227 H3 +  99 H4 + 20 H5 + 8 H8.
```

The pooled selector uses FOUR at chronological ticks `t < 1080`, then THREE.
It uses three active provider IDs, with counts
`gauge44:1568, extra:592, extra-four:1080`. The fourth local word
`gauge44-four` is available in the inherited four-word catalogue but has no
call in this selector. An active registry must reflect this actual dispatch;
the four-word catalogue is not four positive provider multiplicities.

The literal fill supplies every one of 1,321,920 helper roles in 725,760 bins,
with complete idle profile

```
I = 22788 H3 + 1620 H5 + 138492 H48.
```

Thus `H = 2160 L3 + 1080 L4 + I` is exactly

```
{1:8060040, 2:2310120, 3:751788, 4:327240,
 5:66420, 8:25920, 48:138492}.
```

Its rank mass is 23,431,680 = 65,088*360. The ambient dimension is 73,
the live stock is `W=896*360=322560`, and the deficit is
`73W - sum rH[r] = 115200 = 320*360`. Every child has rank at most 48;
`73^2=5329 > 2*48^2=4608` supplies the inherited two-level halving guard.

These identities do not replace the chronology or operator proof. The owner
walk must use the selected width at each call, and the all-character phase
and observer audit must run on this new fill. The old arithmetic selector's
operator receipt cannot certify changed owner axes. Completed local calls
restore arbitrary ordinary helper inputs; the 91 allocated private work
buffers, eight centers and coefficient workspace also need their explicit
return/clear contracts. Private owned-zero work is a distinct resource from
arbitrary dirty helper input.

## 2. Strict profile improvement for every relevant power

Against PR4088/PR4180's complete profile, the old cost minus the new cost is

```
20 H1 + 25 H3 - 30 H4 + 5 H5.
```

This is the difference after including idle compensation. It has rank mass
zero and removes 20 complete children; a local rank calculation alone would
not establish it. For `p=1-a`, its power bill is

```
5 * 4^p * F(p),
F(p) = 4 * 4^(-p) + 5 * (3/4)^p + (5/4)^p - 6.
```

The sum of exponentials is strictly convex, `F(1)=0`, and

```
F'(1) = (15 log 3 + 5 log 5 - 24 log 4)/4 < 0,
```

because the exact integer inequality `3^15*5^5 < 4^24` holds. Hence for
every `p<1`, strict convexity gives `F'(p)<F'(1)<0` and `F(p)>F(1)=0`.
In particular the new complete profile has strictly smaller moment for
every `0<a<1`, under the same stock, ambient width and call contract.
If the historical conservative extra rank-one charge proportional to total
child count were used, its reduction by 20 children improves this comparison
as well. No such extra charge is silently removed from BIT.

## 3. Exact moments and the unchanged BIT supplier

The native complex moment is

```
mu_c(a) = (1/W) sum_r H[r] (r/73)^(1-a).
```

PR559's exact-cover correction omits only an additional complex bad-residue
fallback. Its premises require a uniform exact complex cover, with all
routers and adapters already paid. A changed implementation with exceptional
residue classes would need a new analysis. A fixed finite provider selector
is not itself a width-dependent residue selector.

The source bracket is

```
C = 0.001730980255989036959962,
C < root < C + 10^-24.
```

`joint_bound.py` independently encloses the actual normalized moment below
one at `C` and above one at `C+10^-24`. It uses 384-bit outward integer
rounding, a positive atanh series with its explicit geometric tail, and a
positive exponential series with its explicit tail. It independently repeats
the PR4088 bracket and the selected BIT bracket. It does not execute the
predecessor's moment functions.

The unchanged PR589 BIT profile is

```
{1:381024,2:400416,3:22752,4:26880,5:29376,6:17376,7:26784,42:288},
m_b=64, W_b=28416.
```

With `J=sum H_b[r]`, its full moment remains

```
mu_b(a) = (sum_r H_b[r](r/64)^(1-a)
           + (32*64^2*J/10^16)(1/64)^(1-a)) / W_b.
```

The admitted lower endpoint is
`B=0.001733427039589844234749`, with the exact fallback retained.
Thus `B-C=0.000002446783600807274787 > 10^-24`: the old BIT supplier is
strictly above even the new complex root's upper endpoint. No replacement
by PR4183 is needed. Its newer logical `p=1` result does not automatically
satisfy the stronger primitive, physical and outer hypotheses used here.
Replacing only BIT while keeping the selected complex endpoint leaves the
selected assembly unchanged; the certificate includes that rejection control.

## 4. The full recursive implication and its costs

Assume the completed native complex supplier acts on arbitrary full payloads,
with exact restored source and spectator coordinates, and that its dispatcher
realizes every rank-r call once on `1/W` of the parent volume. At integer
width `e=73f+t`, first handle `0<=t<73` remainder axes with paid elementary
operations, then recurse on widths `rf`. There are no same-width children.
The finite depth bound

```
D(e)=0 for e<73; otherwise D(e)=1+D(48 floor(e/73))
```

is monotone and `O(log(2e))`. Supplying rows divisible by `W^D(e)` permits
all branches, including unequal leaf depths. The inherited full cover/physical
implementation must supply the corresponding group and private reserves.
Rows are padded once at the outer boundary and may be removed only after
their pointwise return. The normalization by live `W` is not permission to
omit the larger physical stock.

For elementary local toll, `F(e)<=sum_r H[r]F(r floor(e/73))/W+K` and
`mu_c(a)<1` imply `F(e)=O(e^(1-a))` by strong induction. Floors only shrink
the power majorant; monotonicity of the actual running time is unnecessary.
This elementary recurrence is not the whole outer layer. With compact
operations supplied by ordinary BIT at exponent `tau`, complex moment
exponent `sigma=1-b`, and stop width `d^theta`, the unequal-width weighted
tree argument gives

```
internal exponent chi = tau+(1-theta)*max(sigma-tau,0),
leaf exponent         = sigma+theta*(1-sigma).
```

Complete cost retains both terms, compact field/row preparation, finite
routers, all scalar and coefficient work, source access, descriptors, rewinds,
COPY/CLEAR, parent bridges, private work, stock and precision. The inherited
strict layer inequalities require both exponents and the preprocessing
exponents below the chosen layer exponent. An exact finite child word alone
does not establish this input-size recurrence.

For this source family the complete physical inventory is
`322560+408+8+91+2=323069`. The expected bound is a 2,646-bit complete
physical stock, actual local prefix 95, block depth 18 and stock l2 exponent
1323. Therefore the full prefix is `95+37+18+1323+1+4=1478`, charged at
2048 bits. The physical row coefficient is 19549, below 20161. These are
source-bound invariants to be freshly checked on the pooled release, not
automatically inherited receipts. The finite invoice also retains `G=2^30000`,
`E=2^100000` and `C0=2^210000`, with the actual scalar, coefficient, wrapper,
adapter and router counts. The parent driver executes their original guards;
the optional receipt binder cross-checks the actual new invoice and sums all
3,240 selected calls independently.

An exact completed child preserves the required return lattice. Substituting
rounded children requires a separate error/cleanup theorem: approximate
subtraction does not prove an exact private ERASE or exact helper return.
Likewise a finite group cardinality and a finite invoice do not construct a
uniform physical address generator or prove its tape tariff. These remain
the explicit all-size hypotheses.

## 5. Two different outer maps

For a comparison using the selected PR1094 parameter convention, let

```
eta=beta=10^-24,
s=min(B,(1-beta)C)-10^-27,
a0=384599/10^10,
a_(j+1)=s(1-s)+s a_j,  j=0,...,6,
q=(1-2 eta)a7.
```

The largest `10^-18` grid point strictly below `(1-eta)q/(1+q)` is

```
kappa_legacy = 0.001727989140903569.
```

The exact ceiling is approximately
`0.0017279891409035694232259263143154912346868927440763`.
The same independent formula reproduces the selected
`0.001672660197076918` from its actual complex endpoint and BIT endpoint.
The candidate's gain is `0.000055328943826651` over that selected number,
and `0.000000001136380736` over PR4088 under the same map. This comparison
requires the new supplier to pass the original finite invoice and a fresh
instantiation of the inherited all-size contract. The named contract is the
same, but the selected review does not establish it for the changed source.
Section 7 makes this quantifier distinction explicit.

The modern PR1786/1758/2180 lineage uses a different analytic construction:
fine source-prime padding, gauge-free interiors, a radix-distributed union
schedule with paid per-visit tags, and the explicit Strassen boundary
`tau=45/16`. It retains additional proof premises beyond the selected map.
For endpoint precision 24, its exact parameter algebra is

```
r=10^-104, delta=(1025/1024)r,
epsilon=1-delta, beta_outer=1-3delta,
b=C-r, q=C-2r, a=(b+q)/2.
```

Since `0<C-epsilon*q<10^-70` and `C*10^70` is integral, its floor/backoff
gives exactly

```
kappa_modern = C - 10^-70 - 10^-46
 = 0.0017309802559890369599619999999999999999999998999999999999999999999999.
```

The ordinary bootstrap must reach the effective `a`; a twelve-stage legacy
receipt alone does not prove that very close rate. Conditional on the
inherited arbitrary-strict-rate bootstrap, choose `s=C-r/2`. Its closed form
`a_j=s-(s-a0)s^j` reaches above `a=C-3r/2` in 38 stages, checked exactly.
All cutoff constants must be carried: if `ell_j` bounds `log2 C_j`, choose
`L_j gap_j^2>=36`, `L_j gap_j>=2(4+ell_j)`, and propagate
`ell_(j+1)>=max(PAYLOAD,ell_j+ceil(L_j(a_(j+1)-a_j)))+1`.
For finitely many positive gaps those cutoffs exist. This is a conditional
existence argument, not a claim that the retained twelve-stage executable
receipt is a 38-stage replay. It relies on the same uniform-cost theorem.

The parent release must run all 63 modern strict ledger inequalities and its
17 controls, together with the ordinary admission and all 47 retained legacy
rows. Arithmetic cannot prove the fine-prime, conditioning or physical
implementation lemmas. Root-as-kappa is valid only under these named modern
premises and its strict margins; it is not the selected `a/(1+a)` map.

## 6. Evidence and permitted conclusion

Without `--release-work`, the certificate reports
`PASS_JOINT_CONDITIONAL_ARITHMETIC_NOT_SUPPLIER_ADMISSION`.
Its six controls reject missing idle children, using the root as the legacy
kappa, omitting modern padding, a BIT-only joint gain, omitting the BIT
fallback, and the old profile claimed at the new root.

With `--release-work WORK`, it requires the completed ordinary and release
statuses in `WORK/admission`, exact new selector and profile, complete native
surcharge models, both outer ledgers, actual restored columns, complete call
cost sums, stock and precision reserves. It records hashes of those actual
files and reports that they are bound. This extra check does not re-execute
the parent engine or replace its source/log/product authentication.

After the parent driver completes and binds the full new release, the
permitted result is a **fully invoiced finite conditional kappa improvement**
at the stated historical mathematical interfaces. The new integration credit
is admission of PR4181's already-published fill; its root and construction
remain attributed to PR4181 and its predecessors. No selected-frontier
change, unconditional multiplication exponent, formal-kernel proof of the
whole algorithm, or independent human review follows.

The finite calculation itself leaves uniform native/source generation and
common-label lifting; arbitrary-input whole-call hosting with exact return;
the common fine-grid precision and exact cleanup contract; physical tape
routing, stock and live-storage bounds; the original BIT H1-H5/ordinary
bootstrap; and the chosen legacy or modern analytic transfer theorem as
separate proof obligations.
PR4183's logical BIT admission alone closes none of the missing complex/outer
obligations. A rounded-child implementation would need a further theorem;
the exact recursive-return model used here does not assume one.

## 7. Inherited hypotheses versus their new source instance

The selected review is specific about its scope. In
[`community-batch1099-review.md`](../../docs/research/community-batch1099-review.md),
the construction review admits twelve owner refinements on the **same**
seven-slot local word with the unchanged strict T16 compiler. Its independent
owner and pricing audits extend their tested input, not their inherited
interface scope. The final paragraph leaves all-size compilation,
common-label/mutable-source realization, whole-call hosting, precision/tape,
exact recovery, analytic transfer and BIT H1-H5 conditional. The selected
construction already permits mutable-source cells; allowing such cells is
therefore not by itself a new hypothesis here.

Let `S0` be that selected source and `S1` the present pooled source. Separate
the following obligations:

* `F(S)` is the finite word, native operator, chronological owner, controller,
  complete profile, stock and invoice certificate for that actual source.
* `U(S)` says that, for every recursive width and admissible full payload,
  the emitted source and its common-cover charts have the declared exact
  completed-child action, pointwise source/spectator/helper return, legal
  private work, and uniform physical implementation within those invoices.
  It includes the address generation, routing, copying, storage lifetime,
  common-grid precision and tape costs needed to realize the recurrence.
* `B` is the unchanged selected BIT/ordinary-primitive and H1-H5 contract;
  `L` is the retained legacy analytic and exact-recovery transfer.

The inference used in Sections 4 and 5 has the form

```
F(S1) and U(S1) and B and L
    imply T(n) = O(n (log n)^(1-0.001727989140903569)).
```

The full release establishes the finite evidence `F(S1)`. It does not prove
`U(S1)`. In particular, `U(S0)` is not logically `U(S1)`: a theorem only about
the selected word cannot be transferred by changing its profile argument.
If the inherited compiler hypothesis is stated universally for every legal
finite source in this class, `U(S1)` is an application of that same unresolved
hypothesis. If it is stated only for the selected source, its scope must
explicitly be extended to `S1`. These are the same *kinds* of mathematical
interfaces, with a newly required source-specific instantiation, rather than
a proof that every unresolved obligation is byte-for-byte unchanged.

The changed instance includes the three active provider programs and their
fixed 3,240-entry selector, the new owner-axis embeddings, the 91 allocated
private buffers and their exact clear/return rules, and the larger complete
physical stock. PR4088's
[`PROOF.md`](../staged544-mixed-fourth-entry/PROOF.md), Section 3, explicitly
requires its uniform implementation hypothesis to cover the finite mixed
selector and all four catalogue words. The pooled selector uses only three;
this does not remove the implementation obligation. The native/all-character
identities and [operator proof](OPERATOR-PROOF.md) establish the declared
algebra and tensor-phase lift, while their common-cover physical embeddings
and recursive invocation contract remain conditional. The fixed selector
adds no width-dependent exceptional residue class; the pure complex moment
still requires PR559's uniform exact-cover premise.

There is no additional rounded-child premise hidden in the legacy conclusion.
[`three-stage-cover-assembly.tex`](../../notes/three-stage-cover-assembly.tex)
requires every completed child to be the exact Gaussian-dyadic tensor on all
roles, preserves the incoming odd-denominator exponent and explicitly forbids
rounding at recursive returns. The borrowing lineage's
[`PROOF-LOCAL.md`](../selective-borrowing-outer-retune/vendor/pr2260-selective-borrowing-kappa/PROOF-LOCAL.md)
retains that contract: tensor phases scale with multiplicity, dyadic Horner
arithmetic is exact, and only the completed outer layer truncates. Its
active-depth bound is

```
A(e) <= A(48 floor(e/73)) + s floor(e/73) + E,
A(e) <= 2(s+E)e,
A_layer(d) < 32*73*(s+E)^2*d.
```

Here `s` and `E` must be the freshly invoiced complete quantities for `S1`.
The release checks the finite guard against `C0=2^210000`; uniform realization
of that common grid and its cost remains in `U(S1)`. Replacing exact children
with rounded approximations would require a separate conditioning and exact
cleanup argument and would not follow from this conditional saving.

Thus the legacy comparison needs no new BIT theorem and no modern
fine-prime/union-schedule transfer. After full finite admission it gives a
strictly larger conditional exponent under the inherited contract schema,
explicitly applied to the new source. It does not complete the unresolved
uniform recursive implementation or establish an unconditional kappa gain.
