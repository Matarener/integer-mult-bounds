# Deterministic bad-header counting for the auxiliary BIT recurrence

This is a scoped exact counting theorem with finite evidence. It answers the
bad-packet-rate question left open by
[PR4215](https://github.com/CrocSwap/integer-mult-bounds/pull/4215), without
rechecking its normal-form identity. It improves the sufficient bound in
Cinna Davis's [PR4100](https://github.com/CrocSwap/integer-mult-bounds/pull/4100)
from `2m^3/q` to the asymptotically sharp `(r+1)/q` for one fixed rank-r
request. No new kappa, supplier admission or complete multiplication theorem
is claimed.

For `m=64`, the largest paid rank in the retained BIT profile is `r=42`.
Consequently every request has bad fraction less than

```
43 / 618970019642690137449562111 < 10^-16.
```

The old sufficient numerator is `524288`. The rank-seven polynomial predecessor
is credited below. This audit does not retune the recurrence or claim any
resulting exponent gain.

The open decision is whether BIT.md's deterministic fallback charge follows
from its complete-header premise. The answer is yes under the fixed-request,
equal-multiplicity premises below. A probability notation is just a normalized
finite count here; no random headers or typical inputs are needed.

## Exact complete-cover law

Let F_q be a finite field, `q>=2`, and fix `1<=r<m`. Put `s=m-r` and

```
A_s=(q-1)q^s+1,
[m choose r]_q = product_(i=1..r) (q^(s+i)-1)/(q^i-1).
```

For a uniformly counted rank-r idempotent P in dimension m, or equivalently
`P=G P0 G^-1` over the complete GL_m cover for any fixed rank-r projector P0,

```
Pr[every leading principal minor of sizes 1,...,r is nonzero]
    = A_s^r / (q^r [m choose r]_q).

#good rank-r idempotents = [q^(s-1) A_s]^r.

Pr[bad] < (r+1-q^(-r))/q < (r+1)/q.
```

The coefficient r+1 is sharp to first order: for fixed m and r,
`lim_(q -> infinity through prime powers) q Pr[bad] = r+1`.
These are counts over complete finite sets, with no randomness assumption on
the algorithm or data. Bounds greater than one are harmless.

### First pivot

Let N_d(t) count pairs of d-vectors whose dot product is t. Directly counting
the zero and nonzero first vectors gives

```
N_d(t)=(q^d-1)q^(d-1)+[t=0]q^d.
```

For a uniform G, put `u=e_0^T G`, `v=G^-1 e_0`. Every pair with `uv=1`
has the same number of completions: choose the remaining rows of G as an
ordered basis of the annihilator of v. Split both vectors across the r image
and s kernel coordinates of the coordinate projector. Therefore

```
Pr[P_(0,0)=t] = N_r(t) N_s(1-t) / N_m(1),
Pr[P_(0,0)!=0] = (q^r-1) A_s / (q(q^m-1)).
```

Any fixed rank-r idempotent is conjugate to the coordinate projector, so
right translation of the complete GL cover proves the same distribution for
it. Uniform G also induces the uniform distribution on rank-r idempotents,
because all conjugacy fibres have the same stabilizer.

### Schur deletion

On `a=P_(0,0)!=0`, write

```
P = [[a,b],[c,D]],    S=D-c a^-1 b.
```

The identities from `P^2=P` are `bc=a-a^2`, `bD=(1-a)b`,
`Dc=c(1-a)` and `D^2=D-cb`. Substitution gives

```
S^2 = D-cb-c a^-1(1-a)b = D-c a^-1 b = S.
```

Invertible block elimination gives `rank P=1+rank S`, so S has rank r-1.
Conjugating P by `diag(1,K)` preserves the nonzero first pivot and conjugates
S by K. This action is transitive on all rank-(r-1) idempotents of dimension
m-1. Thus the conditional distribution of S is uniform. It is nonempty, as
`diag(1,S)` supplies a preimage for every S.

For k>=2, block determinant elimination gives
`Delta_k(P)=a Delta_(k-1)(S)`. If g(m,r) denotes the good fraction, then

```
g(m,r) = ((q^r-1) A_s / (q(q^m-1))) * g(m-1,r-1),
g(s,0)=1.
```

Iterating leaves s fixed and gives the displayed exact fraction. There are
`[m choose r]_q` image subspaces, by counting ordered independent bases.
For each image there are `q^(rs)` complementary kernels, the graphs of
linear maps from any one fixed complement into the image. Hence there are
`q^(rs) [m choose r]_q` rank-r idempotents. Multiplication by the good fraction
gives the exact integer count above.

### The sharp leading coefficient

At the stage with rank i and dimension s+i, the conditional bad probability is

```
beta_i = (q^i+q-1)(q^s-1) / (q(q^(s+i)-1))
       < 1/q + (q-1)/q^(i+1).
```

The strict inequality uses `(q^s-1)/(q^(s+i)-1)<q^(-i)`.
Since `Pr[bad]=1-product_(i=1..r)(1-beta_i)`, the union/product inequality gives

```
Pr[bad] <= sum_(i=1..r) beta_i
         < (r+1-q^(-r))/q.
```

For fixed s and i, `q beta_1` tends to 2 and `q beta_i` tends to 1 for i>=2.
Products of two or more beta factors are O(q^-2). This proves the limit r+1.
It is a scoped obstruction to a smaller uniform first-order coefficient in
this complete-cover pivot model, not an obstruction to different normalizers.

### Relation to the earlier polynomial argument

Chris R / Clear1nsight's
[PR3950](https://github.com/CrocSwap/integer-mult-bounds/pull/3950) already proves
the degree-m Cauchy-Binet/Jacobi numerator bound for the R437 rank-seven caller,
including deterministic complete covers, all high lifts and per-request pricing.
Those facts are predecessor work. This package's addition is the exact all-pivot
law, Schur-deletion proof, sharp coefficient r+1, and binding to BIT.md's full
rank profile. It does not claim to discover the degree-m bound or deterministic
interpretation.

Concurrent [PR4227](https://github.com/CrocSwap/integer-mult-bounds/pull/4227)
supplies exact rank-one and corank-one densities at the retained normalizer.
Those endpoint cases are concurrent work, included here as controls and as
parts of the unified statement. This contribution answers its first open
question with the intermediate-rank law and supplies the full BIT-profile
binding. Its published endpoint formulas agree numerically with our distinct
projector census: at m=4, q=3, rank one has 495 good of 1080 and corank one
has 343 good of 1080. Neither package is supplier admission or proof-kernel
acceptance.

There is also a short alternative numerator description. Replace the first k
rows of G by the corresponding rows of `G P0` to obtain H_k. Then
`H_k G^-1` has those rows of `G P0 G^-1` followed by identity rows, proving
`det H_k=det G Delta_k`. Its degree is at most m, agreeing with the predecessor.
The verifier checks this identity, but does not treat another replay of the
predecessor count as the new result.

## Binding to the retained caller

The audited sources are pinned in [SOURCES.json](SOURCES.json) at base
`12fa8c5c844be21bfefb38a19503fbd867a11244`.

- `BIT.md` sections 2 and 3 specify a complete low-matrix GL cover, all high
  matrices with equal multiplicity, frozen older fields, and a per-request
  fallback allowance. Those are the premises used here. This audit does not
  construct their physical enumeration or prove their storage/time bounds.
- `controlled_normalizer.prepare` forms
  `P=G[:,axes] G^-1[axes,:]`, with fixed coordinate axes for a request. It begins
  with `P C`, where C reverses columns. Its pivot at physical column `m-1-k`
  is the ordinary kth pivot of P. The pivot is
  `Delta_(k+1)/Delta_k`, with `Delta_0=1`. Thus the source's unit-pivot guard
  tests precisely these leading principal minors, not a different corner.
- The source reads ancestor weights separately and forms the unweighted
  projector without them. Such weights cannot bias this classification.
  The theorem is uniform in the original fixed projector, so other fixed
  image/kernel charts do not change the counting argument.

For an odd prime q and `w>=1`, reduction maps `GL_m(Z/q^w)` onto
`GL_m(F_q)`. Each low G has exactly `q^(m^2(w-1))` lifts `G+qH`, and every lift
is invertible because its determinant is a unit. A leading minor is a unit
exactly when its reduction is nonzero. Thus all lifts have the same decision,
and the bad fraction is exactly the low-class fraction. This counts complete
packets, including arbitrary correlated payload and spectator data. It says
nothing about incomplete packets.

Let request j have bad set B_j, and suppose each low header supplies equal
payload volume for each request. Its fallback sum is bounded separately by
`|B_j|` times the stated fallback envelope. Summing those bounds over j needs
no independence, disjointness or common good intersection. In BIT.md, replacing
each request's fraction by `eta=10^-16` gives exactly the conservative tariff
`eta * (32*64^2*sum_r H_r) / W * max T` already written there. This is the
counting justification for that term, conditional on the quoted physical
packet/child-cost premises. The fallback implementation itself is unaudited here.

The retained complete Lucas certificate supplies the prerequisite
that `q=2^89-1` is prime. Its existing checker is registered as a prerequisite,
not presented as a new primality result.

## Finite evidence and controls

The separately implemented verifier uses determinant expansions and direct
conjugation. It imports the retained normalizer only for the final caller
comparison. Across m=2 at q=3,5,7,11 and m=3 at q=3 it exhausts 37,431 raw
matrices, finds 26,976 GL headers, and checks 98,880 projectors using every
nonempty proper coordinate-axis set. It checks 132,576 numerator identities,
every entry of the exact first-pivot distributions, the uniform Schur fibres,
and the new exact all-pivot law. These counts describe matrix/axis
presentations, not distinct projectors.

A separate census constructs every four-coordinate projector by a canonical
RREF image basis and every left inverse of that basis. It enumerates each
projector once, rather than each conjugating header. At q=2, ranks 1,2,3 have
120,560,120 projectors and 36,100,27 good ones. At q=3 the corresponding totals
are 1,080,10,530,1,080 with 495,3,249,343 good. All 13,490 projectors agree
exactly with the theorem. Canonical pivot positions and RREF free entries
uniquely specify the image; choosing the nonpivot columns of the left inverse
uniquely specifies its complementary kernel. This proves census completeness.

At m=3, q=3, every rank-one axis has 5,760 bad headers out of 11,232; every
rank-two axis has 6,528. There are 10,080 presentations with the first minor
nonzero but a later requested minor zero. This rejects omitting later pivots.

Over Z/9, the verifier checks every lift of every GL_2(F3) header, for both
rank-one axes: 7,776 charts, 4,536 good and 3,240 bad. The source agrees with
every decision and every successful pivot ratio. The 1,728 cases where a
minor is nonzero but not a unit reject a nonzero-only test. A further 1,536
three-coordinate charts compare both rank-one and rank-two source guards;
542 pass and 994 reject with the intended guard. Four shared finite rows in
PR3950 agree numerically: bad counts 20/48, 144/480, 468/2016 for rank one in
dimension two, and 6528/11232 for rank two in dimension three. The predecessor
F17 row is not rerun.

Two scope controls prevent overclaiming. The identity-only low cover with
axis 1 is entirely bad. For the two rank-one requests at m=2, q=3, each bad
set has 20 of 48 headers, while their union has 40. Neither arbitrary
subcovers nor a simultaneous-good interpretation follows from a per-request
count. A sixth control rejects treating successive pivots as identically
distributed. These are deliberately altered premises, not predecessor errors.

## Reproduce

From the repository root, with CPython 3.12 and the standard library:

```sh
~/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/bit-deterministic-bad-headers
~/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/bit-deterministic-bad-headers/verify.py
~/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/bit-deterministic-bad-headers --check-source-history
```

Expected marker: `PASS_BIT_DETERMINISTIC_BAD_HEADERS`. Normal and optimized
registered runs check the same predicates. The direct verifier also accepts
`--receipt /absolute/scratch/path.json`; it generates the counts and binds them
to SHA256 hashes of every package file and declared live source. Receipts are
run outputs, not hand-authored certificates.

## Limits and code review notes

The all-parameter claim rests on the written proof above. The finite counts
supplement it. Executed fields are prime fields; extension fields rely on the
written proof. There is no proof-kernel or independent human review. Complete
GL64 enumeration, physical source/owner/packet admission, all-size stock,
fallback realization, recursive storage, tape costs, precision and downstream
multiplication obligations are unrun. The selected frontier is unchanged.

Power-of-ten review: every new enumeration is bounded by the fixed case table
or a 256-header cap; matrices have dimension at most four. Functions fit within
60 lines and there is no recursion. Contracts use explicit exceptions and run
under optimized Python. Source bytes are checked before importing one named
normalizer. Managed Python allocation is a rule-3 deviation: only one matrix
presentation is live per census iteration. Counters and Schur-fibre histograms
are bounded by the fixed case table and the finite projector count. The
bounded standard-library iterator and fixed-path source import are rule-8/9
deviations for a checkable numerical replay, with no generated code or user-selected callback. Revisit these limits before
accepting configurable search sizes. Strict warnings and normal/optimized
replays provide the available interpreted-code diagnostics.

## Open next questions

1. Bind this deterministic count to an emitted complete physical header stream,
   including fresh stock, unchanged ancestor fields and equal high-packet
   multiplicity. This matters because a sparse/adversarial subcover can fail
   completely. Start with one actual recursive caller's serialized enumeration;
   the full fixed-tape compiler and stock obligations remain blockers.
2. Sharpen the count of fallback children by their actual orientations before
   repricing the recurrence. Start with `FALLBACK.md`'s 16,637 swap upper bound
   and the retained program's orientation flags. The physical fallback contract
   must be audited; the counting proof here does not price it.

Structured questions and their blockers are in [TASK.json](TASK.json).

## Credit

This package was produced by Nick Petalas. Cinna Davis supplies PR4100's
auxiliary construction and original per-request bound. Chris R / Clear1nsight
supplies PR3950's rank-specific polynomial and complete-cover caller argument.
The retained normal-form and controller lineage credits source527, commdata2338
and Jose Manuel;
Ross Richardson supplies predecessor fallback algebra. PR4215 supplies the
explicit open counting question. Existing source files and credit are unchanged.
New material is Apache-2.0. Independent human and formal proof-kernel review
are unclaimed.
