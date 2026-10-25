# Sharp exactness for one actual correlated P104 producer

Put pi=1+i and let B=B9 be the Gaussian Newton module on the nine-bit cube.
For f(x)=sum_S a_S x^S, membership in B means pi^|S| divides a_S.
All frames, events and wrappers below are literal PR2586 data, authenticated
by SOURCES.json. The inherited PR3382 alphabet theorem says these wrappers,
coordinate C gates and their inverses are B-automorphisms and have exact
signed-floor execution on B. PR3416 supplies native covariance, including
global phase. Their exact proof texts are retained unchanged in inputs/.
These are explicit inherited premises, not admissions of a complete supplier.

## Actual source boundary

Backward slicing the six first-collector inputs at cut 2025 gives 257 events,
200 transports and 57 ADDs, on 58 initial banks. A separate forward dependency
calculation gives the same closure. The slice includes exactly two reads from
Y27 and Y26. The D31 window is:

```text
1090  D31 += Y27/4       frame F=[157,56,2]
1092  D31 = T D31        F to G=[152,56,5,2], rank one
1129  D31 += Y26/4       frame G
```

There is no other D31 write in this interval. Both Y sources have only native
transports before their reads. Their paths are [131,1056] and [130,1057,1097].
Write A_F and A_G for their ideal initial-to-read maps. Covariance gives
T=A_G A_F^-1. The recipe is T=L C_0 R, with the actual archived wrappers L,R.
The bit is address bit zero. Define the B-automorphism W=R A_F.

Set initial Y27=y, Y26=-y for arbitrary y in B. All other initial Y sources
in this slice may be arbitrary elements of 4B. Its six initial dirty D/Q
dependencies may be arbitrary elements of B. The source roles remain distinct.
The special fixtures set these other inputs to zero.

The question is exact stagewise Gaussian arithmetic in this dependency slice.
It asks whether every division is integral and every literal floor pair
agrees with its ideal pair. It does not ask whether a different rounded
trajectory happens to have the same final value. The rest of the full prefix
reads these same Y banks elsewhere, so its noncone output obligations are
expressly outside this theorem.

## Necessary and sufficient local condition

Let w=W y. Then the correlated slice executes exactly if and only if

    w(x) in 4 Z[i] for every x,
    w(x+e0)-w(x) in 4 pi Z[i] for every x with x0=0.                 (1)

The first quarter adds A_F y/4. Since R is a Gaussian signed permutation,
integrality of this ADD is equivalent to the first condition. Immediately
before the transport the destination is d+A_F y/4, where d belongs to B.
After R its state is R d+w/4. The baseline R d belongs to B.

For Gaussian integers a,b the ideal pair is

    C(a,b)=((a+b+i(a-b))/2, (a+b-i(a-b))/2).

Its outputs are integral exactly when pi divides a-b. This is also exactly
when the literal signed-floor pair equals that ideal pair, by PR3382's
displayed discrepancy formula. The B baseline already satisfies this parity
condition. It follows that the rank-one stage is exact precisely when the
second condition of (1) holds. The final wrapper preserves integrality.

In that case T(A_F y/4)=A_G y/4 is integral. The second source therefore
has an integral quarter and cancels the entire correlated contribution.
The destination becomes T d in B. Both source paths stay in B throughout.
All other slice quarter sources are in 4B, so every remaining slice event
stays exact on B and all six collector inputs are in B at cut 2025.

Conversely, failure of the first condition makes the literal quarter ADD
nonintegral. If the first holds and the second fails, the ideal pair at
1092 is nonintegral and the literal floor pair disagrees. Thus (1) is the
maximal exact source set for this correlated slice, even with fixed zero
dirty inputs. Arbitrary B dirty values cannot remove either obstruction.

This argument proves exactness on the entire module by a parity induction.
It does not infer a nonlinear all-input theorem from basis tests alone.

## Explicit Newton module and sharp index

Write w(x)=sum_S a_S x^S. Boolean evaluation and its inverse, Boolean
differences, have integer coefficients. Consequently values divisible by
4 are equivalent to all a_S divisible by 4. The first difference along
bit zero has coefficients a_S for S containing zero. Its values are
divisible by 4pi exactly when those coefficients are. Combining these
conditions with w in B proves

    M = { w : pi^k(S) divides a_S },
    k(S)=max(|S|,4+1_{0 in S}),
    exact original-source domain = W^-1 M.                          (2)

Both 4 and pi^4 differ by a Gaussian unit. Every exponent in (2) is
necessary and sufficient; reducing any restricted exponent by one gives
an explicit failing monomial while retaining membership in B.

Let e(S)=k(S)-|S|. The multiplicities of e=0,1,2,3,4 are respectively
326,112,56,16,2. Thus

    B/M is isomorphic to the direct sum over S of Z[i]/pi^e(S),
    log2 [B:M] = 112+2*56+3*16+4*2 = 280.

Equivalently each of the two classes, zero absent or present in S, contributes
4+3*8+2*28+56=140. The Gaussian residue field at pi has cardinality two.
Because W is a B-automorphism it preserves 4B, and each e(S)<=4. Hence

    4B is contained in W^-1 M,
    [W^-1 M : 4B] = 2^(2048-280) = 2^1768.

This is an algebraic index, not a storage saving or operation count. The new
source domain is strictly larger than the independent 4B requirement.
It refines PR3426's arbitrary ideal correlation and single integral trace
by classifying all stagewise exact inputs in this named correlated slice.

## Computational evidence

The primary binds every native occurrence to the literal source and extracts
the exact slice. All 512 monomials pi^k(S) x^S execute the actual window
exactly. All 186 restricted one-pi weakenings fail: 93 at a quarter and 93 at
the ideal pair. Eight basis inputs are pulled back through the actual R and
Y27 source path, checked in B, then replayed through all 257 slice events.
All six collector inputs are exactly zero. Six of these sources lie outside
4B. These finite fixtures supplement the universal proof above.

The separate implementation imports no primary executable or arithmetic.
It obtains the source cone by forward histories, checks all 4096 four-real-
component residues modulo eight for the pair condition and reconstructs
the coefficient histogram. Eight pair residues are admitted. Modulo eight
suffices because the relevant divisibility numerators have denominator eight;
adding eight changes their integral quotients without changing parity.

Controls test each obstruction separately, exact dirty translation, a wrong
correlation sign and an intermediate outside B. Actual optimized Git-free
CLI runs accept the canonical package and reject a Boolean index receipt,
a changed immutable source and a missing source. Receipt equality uses
canonical JSON bytes, so Boolean true cannot impersonate integer one.

## Limits and next decision

The theorem is conditional on the retained alphabet and native covariance
proofs. This package authenticates their texts and binds the source paths;
it does not rerun their full predecessor suites. No full 2025-event prefix
domain, general rounded-domain classification, actual correlated preparation,
all-depth tensor theorem or external-recipient implementation is claimed.
The complete-prefix result would need the additional noncone reads, including
Y26 into D12 at 1096 and Y27 into D10 at 1190.

PR3423's unchanged-profile cost stop remains. There is no paid caller,
ownership, restoration, routing, precision, consumer or full supplier invoice
here. No new kappa, selected frontier change or complete multiplication
theorem follows. Independent human and formal proof-kernel review are unclaimed.

Credit Nick Petalas/PR3426 for the ideal correlated entrance and actual source
pair, Clear1nsight/PR3382 and PR3423 for the Newton and producer contracts,
Nick Petalas/PR3416 for the native covariance certificate, ywz65/PR2586 for
the physical word, Arham Tahir/PR2665 for retained inputs, Tekalign/PR3025,
Ross Richardson/PR3068 and the retained geometry, compiler and precision
lineage. Apache-2.0. Frozen predecessor texts and their notices are unchanged.
