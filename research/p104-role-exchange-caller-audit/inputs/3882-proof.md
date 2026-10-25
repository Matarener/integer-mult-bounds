# Exact boundary and sharp residual replacement bound

## 1. Algebra and inherited channel

Let D be `Z[i,1/2]`, the Gaussian dyadic ring. All identities below hold for arbitrary elements of a free D-module, hence coordinatewise on arbitrary finite arrays. No input target is zero, and no dirty helper is clean. Write x and y for the original 104 source and target fields. The retained channel has normalised boundary `(x,y,h) -> (x,v=y+A x,h)` for 72 independent dirty fields h. This boundary theorem and its native chart interpretation are inherited from PR1972/PR1991.

The source extraction constructs the 120 unoriented doubled E8 root representatives in canonical sorted order and deletes the 16 retained F0/C vectors. The resulting matrix R satisfies `RR^t=104I`. Set `A=R^t R/8`. The eight chosen pivot columns J are an orthogonal frame, so `R_J^t R_J=8I` and `R_J R_J^t=8I`. With `B=R_J^t R_N/8`, direct multiplication gives

```
A = [[I, B], [B^t, B^t B]]
```

in J,N order. Thus `v_J=y_J+x_J+B x_N` and `v_N=y_N+B^t(x_J+B x_N)`. Every nonzero entry of B is a signed half. The finite verifier checks each entry and every identity used here.

## 2. A source-consuming tail without a clean bank

All source arrays finish in FULL. First lift every Y target from its existing eight-dimensional hyperplane to FULL. The following common-chart equations are then legal scalar operations on the available banks.

For each unchanged nonpivot source, add its signed half to each incident pivot X and subtract that same signed half from the corresponding pivot Y. The two streams may be interleaved because no nonpivot source has yet been changed permanently. They give `X_J=q=x_J+B x_N` and `Y_J=w_J=x_J+y_J`.

Next subtract `B^t q` from X_N and then add Y_N. This gives

```
X_N = x_N - B^t q + v_N = x_N+y_N = w_N.
```

Return X_N to the target hyperplanes indexed by N and Y_J to those indexed by J. The residual banks X_J and Y_N remain in FULL. This is an explicit output-role assignment, not a claim that data movement or arbitrary caller relabelling is free. The 72 inherited dirty-helper banks are never targeted or read by this tail. Their inherited logical restoration is therefore preserved.

The literal scalar schedule halves each X_N once, applies all of its incident unit additions and subtractions, and doubles it before proceeding. It then halves each pivot q once, applies its incident scatter subtractions, and doubles it. Finally it performs 96 direct X_N += Y_N additions. This uses 1,248 unit Gaussian ADDs, 104 halves, and 104 doubles. Every arithmetic source and target is in FULL. The 104 initial lifts and 104 final descents are rank-one pairs, for 208 formal native occurrences. They require their usual paid native implementation, not free frame relabelling.

The inverse boundary is explicit. From `(w,q,v_N)`, compute `x_N=w_N-v_N+B^t q`, then `x_J=q-B x_N`, and finally `y=w-x`. These are D-linear equations. Their existence proves an invertible encoding, but not the cost or legal availability of a physical downstream decoder.

The statement does not preserve the original source bank. In particular, Y_N still contains the original channel-produced v_N, whereas the eight would-be residual values v_J are replaced by q. Requiring the original source outputs again changes the contract and demands a priced continuation.

## 3. Why every old residual cannot be retained

Consider the tempting alternative boundary that returns all corrected sums w and all old residuals v, with arbitrary dirty helpers restored and no other persistent source-dependent output. Its data matrix is

```
T = [[I,I], [A,I]].
```

The previously known covariance identity implies `A^2=13A`, with A of rational rank eight. Hence `C=I-A` has eigenvalues 1 with multiplicity 96 and -12 with multiplicity eight, and `det(T)=det(C)=12^8`. This determinant was already implicit in the predecessor correction certificate; the new use is its odd-prime obstruction to this changed return contract.

Reduce D modulo 3. The quotient is the field F9 because `z^2+1` is irreducible over F3 and 2 remains invertible. The matrix R has rank eight modulo 3 since `RR^t=104I=2I`. Therefore A is an idempotent of rank eight, C has rank 96, and T has rank 200 rather than 208. The primary checker separately eliminates both C and T modulo 3. Since all entries of these particular matrices are rational dyadics, their rank over F3 equals their rank after scalar extension to F9.

A reversible D-linear circuit must remain invertible modulo 3. This includes arbitrary invertible D-linear recoding, exact dyadic scaling, phase multiplication, and invertible dyadic native chart changes. Appending any number of arbitrary dirty inputs and returning them unchanged only adds an identity block, so it cannot repair T's eight-dimensional defect. Clean temporary banks that are returned to zero likewise do not provide a final source-dependent observation.

Now keep every w output but permit replacing k of the old v outputs by arbitrary D-linear outputs. Modulo 3, replacing k scalar rows increases rank by at most k. Reversibility therefore requires `200+k >= 208`, or `k >= 8`. Our boundary replaces exactly the eight v_J outputs and has the explicit D-linear inverse in section 2. Eight is thus the exact minimum in this residual-row replacement model.

For arrays with d Gaussian coordinates, the naive defect has dimension 8d. Replacing k whole arrays contributes at most kd scalar rows even when arbitrary cross-coordinate D-linear mixing is allowed, so the whole-array minimum remains eight. This is a count of changed residual outputs, not a transport-rank, lifetime, storage-width, or recursive-cost lower bound.

A related necessary statement holds when all v outputs are retained and extra persistent clean-carrier output coordinates are allowed. They must supply at least 8d independent residues modulo 3. This does not establish a physical attaining carrier scheme or allow an arbitrary dirty bank to be treated as clean.

## 4. Scope controls

The ordinary source-preserving correction shear `[[I,0],[C,I]]` is invertible over D for every C. The verifier checks its full rank modulo 3 as a positive scope control. Thus the argument is not an impossibility theorem for correcting P104.

The lower bound also does not cover division by an odd Gaussian prime, nonlinear rounding/residue encoders, nonzero private erasure, extra persistent source-dependent outputs, restricted correlated input domains, or a consumer that requires fewer sums or a different residual contract. Those are separate hypotheses and have their own implementation and price obligations. In particular, the ideal dyadic argument does not silently validate the literal signed-floor execution on arbitrary integer arrays.

The fixed-cover support and source-preconditioner models preserve different data contracts. Reading and modifying channel Y, consuming X, and replacing residual outputs are explicit changes here. The result neither repeats the 208-flag static cover nor refutes the 23-dimensional preconditioner obstruction reported in PR3810.

## 5. Exact evidence and budget boundary

The primary implementation replays every new scalar instruction on 280 independent columns, including all original dirty variables. It verifies every sum, every residual, every helper, and every final frame dimension. Its separate inverse calculation uses the boundary equations rather than reversing the instruction list. The second implementation rebuilds the root geometry by a different enumeration and evaluates the endpoint in quarter-integer coefficients with a block ordering distinct from the primary schedule. It compares the full 280 by 280 endpoint digest.

With normalised integer x,y inputs, every scalar prefix coefficient is a multiple of one quarter. A quarter is actually attained, so two fractional bits are sharp for this scalar instruction list. The maximum row one-norm is 26, including the channel-exit input rows; this bounds each real component by 26H when every original component is at most H. Neither statement includes the native frame-conversion arithmetic or proves that an outer physical producer supplies these normalised integer inputs.

The formal added native profile is 208 H1. The retained profile therefore becomes `(1282,58,86,104,48,24,8,8)` and has mass 2576. Under the unchanged width-nine, 280-role bare mass relaxation, `2576/(9*280)=46/45>1` already fails. This is the predecessor terminal-tariff stop applied to the same numeric profile, not a lower bound for all changed consumer laws. Owner routing, a physical residual consumer or decoder, literal native admission, precision, tape, and complete all-size hosting remain unresolved. Their costs are unknown, not zero.
