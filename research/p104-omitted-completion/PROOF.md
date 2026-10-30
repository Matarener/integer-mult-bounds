# The omitted endpoint operator has rank eight

All statements below concern chart-normalized payloads. The frame changes in
section 5 are separate obligations.

## 1. Exact object and conditional interpretation

Use the two unchanged PR2586 inputs pinned in `SOURCES.json`. The word has
5,398 events and 358 initial public banks. Original private banks start at zero.
The native interpretation is conditional on the exact covariance
`U(old,new) = J_new J_old^-1`, including its phase. This premise is inherited
from the PR2586/native lineage and the PR3416 covariance result. This package
binds every occurrence to its source frames and recipe rank. It does not
independently prove the native matrix identity.

Writing a physical bank in frame `f` as `J_f q` gives normalized payload `q`.
A native transport leaves `q` unchanged. Every ADD has equal source and target
frames, so it updates `q_target += c q_source`. Signs act by minus one.
This gives rational linear maps on the 358 public normalized payloads after
eliminating the eight zero-initialized private banks. The verifier proves all
eight erased payloads are the zero linear form in both maps below.

Let `F` be the complete word's normalized endpoint map. Define `S` by the
PR3446 terminal-history projection, extended by the identity on omitted public
banks. Its construction is fully specified here, without importing PR3446 code:

1. Let `L` contain Y22 through Y32, Y63 through Y103, D27 through D31,
   G27 through G31, and Q7.
2. Observe each ADD at event at most 4516 whose source is in `L` and whose
   target is outside `L` and is not the private C bank. There are 675 events.
3. Retain their full syntactic histories and the final histories of `L` and
   those ADD targets. Whenever a retained history reads an initial public bank,
   also retain that bank's full terminal history. Whenever a private allocation
   is retained, retain its erasure history. Repeat to a fixed point.

Histories include each target's old value, source reads, signs and transports,
even if their scalar coefficients later cancel. The forward bitset construction
retains exactly 4,027 events and 265 initial banks. Its sorted event-list hash
matches PR3446's published `66113bcd...c676dc8`. This is the projection being
completed, rather than an algebraically minimized alternative slice.

## 2. The full residual

Set `Delta = F-S`. Exact rational execution establishes the following identities
entry by entry. A separate reverse-covector calculation checks all 358 rows of
both `F` and `S`, for 716 complete row comparisons.

- `Delta` vanishes on all 265 retained output banks.
- Among the 93 omitted output banks, 52 X rows are nonzero and 41 rows vanish.
  The latter are 38 N banks and G2, G3, G9.
- Every nonzero residual column is a Y input. Write `R` for the nonzero
  52 by 104 block of `Delta`. It has 2,500
  nonzero entries. Its exact sparse representation is authenticated by the
  matrix digest in `CERTIFICATE.json`.
- Both maps preserve every Y payload. Every full non-X row is its own identity
  row. Every full X row is its own identity row plus a Y-only linear form.

The 696 omitted ADDs whose source is retained and target is omitted are not the
entire omitted program. In total the slice omits 794 ADDs, 104 signs and 473
transports. The complete terminal difference includes all of these operations.
In particular, adding 696 isolated increments at the endpoint is not the
calculation used here.

Let `K` denote the 358 by 358 matrix obtained by embedding `R` in its X output
rows and Y input columns. Since `S` preserves Y, `K S = K`. Thus

```
F = S + K = (I + K) S.
```

Also `K^2=0`, because X and Y banks are disjoint. The normalized completion is
an invertible shear with inverse `I-K`. It requires no reads of omitted N/G
payloads and leaves those payloads unchanged. This is an endpoint identity,
not permission to omit their physical frame changes.

## 3. Exact factorization and sharp query dimension

Use row order

```
X0, X33, X101, X102, X11, X12, X15, X24
```

and column order

```
Y0, Y10, Y100, Y101, Y102, Y103, Y11, Y12.
```

The corresponding minor of `R` has determinant `-1/128`. Equivalently, that
minor of `2R` has determinant `-2`. This proves rank at least eight over Q,
Q(i), and every field of characteristic other than two.

Let row `i` of `A` be twice the complete Y row of `R` at the named basis X bank.
For each X row, solve for its coefficients in these eight basis rows using the
specified minor. The resulting 52 by 8 matrix `C` has integer entries. The
verifier checks the reconstruction on every one of the 5,408 entries, not just
the minor columns. Consequently

```
R = C A / 2.
```

Both matrices, with every integer coefficient, are in `CERTIFICATE.json`.
`A` has 385 nonzeros and entries in {-2,-1,1,2}. `C` has 209 nonzeros and
entries in {-3,-2,-1,1,2,3,4}. This proves rank at most eight and completes the
rank proof. These identities have coefficients in Z[1/2], so they also prove
the characteristic-other-than-two assertion.

Any factorization of this fixed endpoint matrix through `q` linear query values
has rank at most `q`, hence `q >= 8`. This is a bound on linear summary dimension
in such a factorization. It is not a lower bound of eight simultaneous helper
banks, a native-rank tariff, or a restriction on arbitrary interactive programs.
No sparsity optimality is asserted for the displayed `A,C`.

## 4. One arbitrary dirty helper suffices algebraically

Let `M` be a Z[i] module embedded in a Q(i) vector space. Suppose the X
targets start in `M` and the Y inputs belong to `2M`. Every `A_i Y/2` belongs to `M`, since `A` is integral. The prior
projection's sufficient Y entrance is `4M`, which satisfies this condition.
This does not independently prove that projection's native or scalar entrance
contract. The present `2M` statement concerns the endpoint completion alone.

Borrow one helper with arbitrary value `h` in `M`. For each `i=0,...,7`, perform
these four normalized operations, in this order:

```
X <- X - C[:,i] h
h <- h + A[i,:] Y / 2
X <- X + C[:,i] h
h <- h - A[i,:] Y / 2.
```

The two X changes sum to `C[:,i] A[i,:]Y/2`. The helper returns exactly to its
initial dirty value after each iteration. No X value is read by a gather, so
previous X updates do not affect subsequent queries. Summing the eight updates
gives `RY`, proving the claimed completion and arbitrary dirty restoration.
All intermediate helper and target payloads remain in `M` under the stated
domain. Gathering the eight queries concurrently into eight helpers gives the
same identity, but is unnecessary for peak algebraic workspace.

Expanding each matrix entry into one weighted transvection gives exactly
`2*(385+209) = 1188` nonzero weighted updates. These include halves and integer
coefficients up to four. This count is not a bill in the source instruction
alphabet and does not price frame adapters, scalar expansion or native calls.
The standard-library replay checks every one of the 104 Y unit columns at twice
a module element, with three arbitrary dirty values, in addition to six complete
word/projection fixtures. Rational identities establish the general statement;
these finite fixtures check the actual schedule and failure paths.

An arbitrary `M` entrance cannot be inferred uniformly. For `M=Z[i]`, the
certificate identifies a coefficient `1/2` or `-1/2` in `R`, so a unit input
in that Y coordinate produces a nonintegral scalar residual. We claim sufficiency of `2M`, not a general
classification of correlated entrance domains.

## 5. Physical frame and cost boundary

All 93 omitted public banks remain in their initial frames in the projection,
and all 93 full-word final frames differ. The authenticated gap list records
both endpoint frames for each bank. The dimension pairs are:

| Omitted banks | Number | Projection frame dimension | Full final dimension |
|---|---:|---:|---:|
| X | 52 | 1 | 9 |
| N | 38 | 0 | 9 |
| G | 3 | 0 | 9 |

The 41 zero normalized residuals therefore still need physical frame changes.
Moreover, normalized Y readouts and X updates are not automatically legal
same-frame physical ADDs. The actual retained Y endpoints have dimension eight.
A common chart, legal adapters, source restoration and a complete paid native
implementation of the summary program remain unknown.

The new proved obligation is the exact omitted normalized endpoint operator and
its one-dirty-helper factorization. Native covariance is inherited. Physical
access/routing, ownership, adapter recipes/costs, numerical heights and precision,
recursive realization, idle/cleanup charges and a complete supplier invoice are
not supplied. The selected frontier is unchanged. The unchanged-profile stop
remains in force, and this package does not begin another construction round.
A follow-up must first bind a concrete physical caller and all adapter costs to
the displayed coefficient program, then apply a fully charged budget screen.
