# Source-bound audit of the actual P104 tensor words

## Scope, sources and operator order

Chris R / Clear1nsight's PR3979, scientific head
`a8a1d744811cd7d1f9c43ec7ccbae85ef9695b61`, supplies the construction, words,
counts and comparison audited here. Canonical main is
`20ecf2891d80b5acf18d980b2164fb44ea7faa90`. The new result is a compositional
exact check at the actual 104 ports and all 21,632 data coordinates. It is not
a new code, a criticism of the predecessor's written derivation, or a full
multiplication/native audit. The unchanged exported sources retain their
authorship and earlier P104/native/caller credit.

All arithmetic below is coordinatewise over the Gaussian dyadic ring
`R=Z[i,1/2]`, under the predecessor's common-FULL-chart scalar contract.
Temporarily modified donors must return. No physical chart transport or owner
reassignment is inferred. Number data by
`index(bank,i,j)=(bank*104+i)*104+j`. The first eight axis coordinates are the
original pivot ports `(0,1,3,6,22,31,93,103)`; the remaining ports retain
canonical lexicographic order. Operators act on column vectors, the rightmost
operator executes first, and `K_r=K tensor I`, `K_c=I tensor K`. Axis zero
varies i at fixed j; axis one varies j at fixed i.

The canonical P104 fixture is authenticated by SHA256
`516c06f6ec3cb84be588c546108de897650288576dd5fbf5fe44b9c5546ad8a4`.
The primary checker obtains the frozen source's actual words and B2=2B; the
independent checker reconstructs roots from a different full ternary/sign
enumeration and never imports a primary or predecessor executable. Both bind
all 768 B2 entries to SHA256
`88e9a726e8c8aec055bfd7cd024883b5c8ecbda0cd6471e591a08c43a108a535`,
using ASCII `json.dumps(b2,separators=(',',':'))` without a newline. This is the
explicit bridge between literal-word checking and the independently rebuilt
geometry, rather than agreement only on dimensions or support counts.

## Every literal event has an exact local meaning

The authenticated source builders generate four complete words: encoder,
decoder, coded Gram pair and specified uncoded reference Gram pair. No
predecessor evaluator, result routine or receipt supplies their semantics.
For every event the primary checker verifies opcode, arity, integer indices
and signed-unit ADD coefficient. Its localization checks that both donors and
recipients lie in the declared bank/fiber. Every word is consumed to its end;
truncation, extra events and a move to another fiber cannot be ignored.

On the 104 independent local coordinates, an exact sparse Fraction interpreter
certifies the four sweep maps `U,U^-1,U^t,U^-t`. On 208 independent two-bank
local coordinates it certifies the lower/upper M shears and lower/upper A
shears, including complete source return. These are eight distinct local maps.
Every other fiber's full localized event sequence is checked equal to its
certified pattern. Within a fixed sweep, different fibers have disjoint
supports, so these local maps compose to their stated global tensor factors.

The coverage is 416 encoder fibers, 416 decoder fibers, 16 coded-pair fibers
and 208 reference-pair fibers: **1,056 actual fiber instances**. The four
words together contain **763,392 literal events**, all checked. This is the
sum of one copy of each of the four audited words, not the length of a single
two-pair experiment. Pattern reuse avoids redoing identical arithmetic; it
does not replace inspection of any event or restrict input values.

Each event index is below `2*104^2`. Therefore the words extend by logical
identity on every additional independently arbitrary helper coordinate,
including the named 72-per-fiber auxiliary banks. This is stronger than
checking only zero dirt or two sentinels, but is solely a logical index fact.
It does not execute their physical completion, native return or ownership.

## Global algebra on all coordinates

Let P select the first eight coordinates. The independent reconstruction
checks the actual Gram matrix A, all B entries, and

```
U = [I B;0 I],   U^-1 = [I -B;0 I],
A = U^t P U,    M = U U^t,    N = M^-1 = U^-t U^-1.
```

The encoder sweeps execute `U_c^-t` before `U_r` on X and `U_c` before
`U_r^-t` on Y. Thus their global map and the certified decoder are

```
L = U_r U_c^-t,
C = diag(L,L^-t),        C^-1 = diag(L^-1,L^t).
```

There is no cross-bank slot permutation. The uncoded lower stage and subsequent
upper stage are

```
S = [I 0; A_r I],        R = [I -A_c;0 I].
```

Their chronological pair is RS. The two-bank coded fibers implement

```
S_hat = C S C^-1 = [I 0; P_r M_c I],
R_hat = C R C^-1 = [I -M_r P_c;0 I].
```

For example, the lower coefficient factors as
`(U^-t A U^-1) tensor (U U^t)=P tensor M`. The upper coefficient is
`M tensor P`. These factors retain the displayed order; replacing M by
`U^t U` is generally incorrect. The independent checker proves both C
inverse identities, both Gram conjugations, and the full endpoints

```
C^-1 (R_hat S_hat) C = RS,
C^-1 (R_hat S_hat)^2 C = (RS)^2.
```

The same C is used on both sides of the internal boundary. These equalities
hold on every independent real/imaginary component of both banks, including
the Gram kernel. They are not tests of a sampled dense input.

### Exact contraction without a huge dense matrix

Each bank-to-bank block is stored as a finite sum `T=sum_k c_k A_k tensor B_k`
of real dyadic 104-by-104 factors. Matrix products preserve this form. Its
exact Frobenius square is

```
||T||_F^2 = sum_(k,l) c_k c_l
           <A_k,A_l>_F <B_k,B_l>_F.
```

This follows by expanding each entry and separating the two tensor indices.
All factor entries are integers divided by powers of two; the implementation
performs integer multiplication and common-denominator addition. There is no
floating point, tolerance or probabilistic contraction. Since T is real,
this sum is zero exactly when every entry of T is zero. Checking all four
two-bank residual blocks therefore proves equality on all **21,632 data
coordinates**, while avoiding their 467,943,424-entry dense operator.
The independent checker verifies eight global block identities in this way.
Its zero contractions combine with the literal-fiber audit above; neither
checker alone is claimed to certify the entire evidence chain.

## Counts, comparison and the omitted identity requirement

Counting every generated event gives the predecessor's invoices:

| Word | Unit ADD/SUB | Halves | Doubles |
| --- | ---: | ---: | ---: |
| Entry plus exit | 319488 | 43264 | 43264 |
| Coded uncorrected Gram pair | 26240 | 3328 | 3328 |
| Specified uncoded Gram pair | 241280 | 41600 | 41600 |

For k repeated identical **uncorrected Gram pairs**, the charged addition
comparison is `319488+26240k` against `241280k`; each scaling category is
`43264+3328k` against `41600k`. At k=1 the code loses 104448 additions and
4992 operations in each scaling category. At k=2 it saves 110592 additions
and 33280 in each scaling category. Since the respective inequalities are
`215040k>319488` and `38272k>43264`, two is the first positive integer winning
all three columns. This compares precisely these existing words, not optimal
uncoded algorithms, runtime, or an identified physical repeated consumer.

The required identity shears are different. Their coded coefficients are
`N_r M_c` and `M_r N_c`; the Gram words contain only `P_r M_c` and `M_r P_c`.
The independent checker verifies the identity conjugations and

```
N-P = U^-t (I-A) U^-1,        A^2=13A.
```

Over Q, `(I-A)^-1=I-A/12`. Hence N-P has rank 104 and, since M is invertible,
each omitted tensor side has rank **10816**. This is an algebraic-rank fact,
not a dyadic primitive, native-child tariff or cost lower bound. A nonzero
kernel payload `(-Bz,z)` is retained by U even though its pivot query vanishes;
the omitted identity side acts nontrivially on it. The original PR already
owns these completion warnings and rank claims.

Positive exact residual norms additionally separate reversed U/transpose
order, reversed Gram-stage order and omitted lower/upper identity completion.
The original modulo-13 spectral-normalization result is outside this audit.

## Remaining obligations and stopping rule

This closes a bounded all-coordinate software/algebra audit of the pinned
scalar words. Physical chart conjugation, actual adjacent/repeated consumers,
identity-side implementation, copied-center endpoint correction/wrappers,
dirty-helper completion, owners/routing/holding/control/tapes, signed-floor
precision and all-size/native admission remain unresolved or inherited. Scalar
ADD/scale counts are not native rank units. No new physical bill, passing
supplier inequality, kappa change, human acceptance or proof-kernel certificate
is claimed. Stop dependent construction until a named consumer and favorable
complete allowance are supplied.

Prepared by ToikY with substantial OpenAI Codex assistance, including separate
AI implementation/review contexts. Apache-2.0; all predecessor credit is retained.
