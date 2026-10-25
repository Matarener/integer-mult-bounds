# An all-bank hybrid controller with two terminal code applications

This is an exact abstract controller construction and a conditional scalar
cost improvement. It does not admit a physical BIT supplier or improve its
rank mass. The historical scientific source is
`20ecf2891d80b5acf18d980b2164fb44ea7faa90`.

## Contract and coefficient ring

There are \(B\ge1\) pairs \((X_j,Y_j)\), with all \(2B\) entering banks
\((x_j,y_j)\) arbitrary and independent. Work over the integral free group
algebra on independent invertible operators \(a_0,a_1,\ldots,a_{2B}\).
Only adjacent inverse cancellation is permitted; operators do not commute.
The result specializes to arbitrary invertible linear operators on a module.
Transpose symbols are separate operators, with multiplication order reversed
under transpose; no equation \(a_s^T=a_s^{-1}\) is used.

The abstract coded local maps are

\[
 F_s(X,Y)=(a_sX,\;Y+a_sX),\qquad
 B_s(X,Y)=(X-Y,\;a_s^{-1}Y).
\]

Clean locals replace \(a_s\) by \(I\). A bridge of coefficient \(c\) from pair
\(s\) to pair \(d\) is

\[
 X_d\mathrel{+}=cX_s,\qquad Y_s\mathrel{-}=cY_d.
\]

The `recipe(B)` function in the pinned `global_k.py` has \(2B+1\) locals,
\(3B-3\) bridges, and one final exchange, hence \(5B-1\) events. It begins
with \(F_0,B_1\) on pair 0, advances through the adjacent pairs using the
two opposite bridge signs, then returns through the descending bridges.

Each local's dirty helpers must restore for **every** entering helper value,
and its copied field must obey its own zero-entry/cleanup lifetimes.
Those are imported local contracts. No public bank is assumed clean or used
as zero scratch. The added controller operations act only on the public
banks; the formal boundary is direct summed with the identity on the
arbitrary restored helpers.

The actual R429 local identity supplies this map on binary VALUE functions.
Its signed integer lift can have even target helper leakage. Consequently,
the signed free-group theorem is an abstract result and cannot be applied to
that actual integer lift merely because its reduction modulo 2 agrees.
Native ADDRESS frames, global phase, mixed helper owners, source access,
COPY legality and rounded precision remain separate obligations.

## Clean-tail identity for every \(B\)

Cut immediately after the first reverse local \(B_1\). Let its current pair
be \((U,V)\); all other pairs still enter as \((x_j,y_j)\). Use only clean
locals after that cut and keep every original bridge and its sign.
The tail before the final exchange sends

\[
 (U,V),(x_1,y_1),\ldots,(x_{B-1},y_{B-1})
 \longmapsto
 (U,U+V),(-y_1,x_1),\ldots,(-y_{B-1},x_{B-1}).
 \tag{1}
\]

Here is an induction on the literal ladder, not an extrapolation from a
finite list of bank counts. Put \(s_0=U\) and
\(s_j=-y_j-s_{j-1}\) for \(j\ge1\), and put
\(z_0=U+V,\ z_j=x_j\) for \(j\ge1\).

For \(B>1\), the first positive bridge, clean forward local, and negative
bridge leave \(X_0=s_0,\ Y_0=z_0+x_1\) and present the next pair as
\((x_1,y_1+s_0+x_1)\). In general, pair \(j\ge1\) enters its clean reverse
local as \((x_j,y_j+s_{j-1}+x_j)\); the reverse local sets
\(X_j=s_j\). If \(j<B-1\), the next two bridges and forward local leave

\[
 X_j=s_j,\quad Y_j=x_j+x_{j+1},
 \quad (X_{j+1},Y_{j+1})=(x_{j+1},y_{j+1}+s_j+x_{j+1}).
\]

For the last pair, the forward local leaves \(Y_{B-1}=x_{B-1}\).
Thus after the forward ladder, every \(X_j=s_j\);
\(Y_j=z_j+x_{j+1}\) for \(j<B-1\), and \(Y_{B-1}=x_{B-1}\).
In the descending bridge from \(j\) to \(j+1\), its source \(X_j\) has not
yet changed, so
\(X_{j+1}=s_{j+1}+s_j=-y_{j+1}\).
Its target \(Y_{j+1}\) has already become \(x_{j+1}\), so the simultaneous
dual shear leaves \(Y_j=z_j\). This proves (1).
For \(B=1\), the tail is just the clean forward local, also giving (1).

In particular, the entirely clean controller ends
\((X_j^{out},Y_j^{out})=(x_j,-y_j)\); this becomes the identity in
characteristic 2.

## The two-code construction

Keep only \(F_0\) and \(B_1\) coded. Do not insert either historical immediate
source-code pullback. Directly after these two locals,

\[
 U=-y_0,\qquad V=a_1^{-1}(y_0+a_0x_0).
\]

By (1), the terminal current-word pair is

\[
 X_0=-y_0,\qquad
 Y_0=-y_0+a_1^{-1}(y_0+a_0x_0).
 \tag{2}
\]

At the terminal cut after the original idle-owner returns, use the
historical conditional promotion of \(Y_0\) to the common FULL frame.
The entire new logical correction is

```
Y0 -= X0
Y0 := a1 Y0
Y0 += X0
Y0 := a0^-1 Y0
```

Equation (2) changes successively to
\[
 a_1^{-1}(y_0+a_0x_0),\quad y_0+a_0x_0,\quad a_0x_0,\quad x_0.
\]
The arbitrary \(X_0=-y_0\) is untouched. Demote \(Y_0\) by the historical
second normalization and perform the original bank exchange. Every pair now
has the same all-input endpoint as the original clean controller.
Both past codes act only at the common terminal FULL cut. No new public,
private, or dirty helper bank is introduced.

This proves the logical construction for every \(B\ge1\). It does not extend
the historical physical bank tiling to those parameters: the source
`recipe` is algebraically defined at \(B=1\), but its native driver accepts
only odd stage counts at least 5 and emits its old tiling only at nine
stages. The nine-stage \(B=4\) physical premises must still be supplied.

## Historical six-code word and exact scalar improvement

The historical word additionally applied \(a_0^{-1}\) to \(X_0\) after
\(F_0\), and \(a_1^{-1}\) to \(X_0\) after \(B_1\). Equation (1) gives its
preterminal pair
\[
 X_0=a_1^{-1}((I-a_0)x_0-y_0),\quad Y_0=a_1^{-1}x_0.
\]
Its terminal operations \(a_1\) on both banks, followed by
\(X_0\mathrel{-}=Y_0\), source preparation \(Y_0\leftarrow a_0Y_0\),
\(X_0\mathrel{+}=Y_0\), and source unpreparation
\(Y_0\leftarrow a_0^{-1}Y_0\), also close. Thus the historical construction
itself extends to all \(B\), with six additional code applications.

With the same historical tariff of 1,499 scalar ADDs for a literal code or
its inverse and 111 scalar ADDs per complete bank shear, the added
controller bills are
\[
 6(1499)+2(111)=9216,\qquad
 2(1499)+2(111)=3220.
\]
The exact difference is **5,996 scalar ADDs per replica**. These are the
added controller operations, not the entire supplier's scalar cost.
The unchanged recipe contributes \(3B-3\) bridges, each two bank shears;
the \(2B+1\) local supplier costs retain their own inventories.

Both words keep the same two conditional 111-child normalization sweeps,
so the normalization bill remains 222 rank-one native children. With the
historical *complete owner-return comparison* of 60 rank-mass units saved
per coded local, relative to the fully coded comparator the hybrid adds
\[
 (2B-1)60+222,
\]
and relative to the entirely clean controller it saves
\[
 2(60)-222=-102.
\]
Increasing \(B\) does not repair that deficit in this fixed comparison.
For \(B=4\), the first number is 642. The old 492 and 309 allowances belonged
to a particular planning calculation at beta .002 and .003; they are not
uniform allowances or a newly checked asymptotic theorem.
Mixed owners, the full rank histogram/width recurrence, source access,
native implementation and precision are not waived by the scalar saving.

## Restricted two-occurrence optimum

Fix the two coded locals \(F_0,B_1\), keep every other local clean, and
permit only additional single-bank primitive applications of one
\(a_s^{\pm1}\), determinant-neutral scalar mixing, and logical frame
normalization. The required endpoint remains the all-clean signed endpoint.
Composite code words count each primitive occurrence. Additional coded
locals, operator-valued shears or unpriced composite operators are excluded.

Specialize \(a_0=t,\ a_1=u,\ a_s=1\) for \(s\ge2\), over the rational
function field \(\mathbb Q(t,u)\). The coded first pair contributes
determinant \(t/u\); the clean locals and scalar shears have determinant 1,
and the unchanged final exchange has determinant \((-1)^B\).
The added operations must therefore have determinant \(u/t\).
One allowed code occurrence can change at most one of the independent
\(t,u\) exponents by one. At least one occurrence of each is necessary, so
at least two are required. The displayed construction attains two.

This proves optimality of **additional generator occurrences in that
alphabet**, not physical circuit optimality, a scalar-ADD lower bound for
all implementations, or a minimum number of frame-normalization sweeps.

## Selected native early-promotion obstruction

Independently reconstruct the actual binary P012 code
\(A=I+WR\), where \(W\) is the pinned \(K\) with rows 0,1,2 deleted.
Its actual off-diagonal entry is \(A[3,0]=1\).
The pinned R438 root labels and full E8 root data reconstruct the two
selected routes. The discovery path for port 0 is empty; for port 3 it is
`0 -> 64 -> 3`. Each selected route is the symmetric involution
\[
 \rho_p=\begin{pmatrix}P_p&A_p\\A_p^T&0\end{pmatrix},\qquad
 A_p^TA_p=I_7,\quad A_pA_p^T=I_8-P_p.
\]
Here \(P_p=q_pq_p^T/4\) and the vectors are exactly those in the pinned word.

For the source root-line vector \(v=2e_0\in P_0\),
\[
 \rho_0v=v,\qquad
 T v=(\rho_3^{-1}\rho_0)v=2e_{10},
\]
where coordinate 10 is the third fresh coordinate. This vector lies
outside the target \(P_3\), over the rationals and over \(\mathbb F_{101}\).
Thus the relative route does not carry the source promoted-frame fiber
into the target promoted-frame fiber.

The ADDRESS convention is a forward point push \(v\mapsto Tv\), so the
corresponding VALUE push is \(g(w)=f(T^{-1}w)\). Directly, the target
root-line vector is \(v_3=2e_3\in P_3\), and the independently computed
inverse route gives \(T^{-1}v_3=2e_{10}\).
Take the binary source VALUE function \(f(w)=1\) exactly when
\(w_{10}=0\) over \(\mathbb F_{101}\). It is constant along source
\(P_0\), which has no fresh component. But its forward VALUE image has
\(g(0)=1\) and \(g(v_3)=0\), so it is not constant along the target
\(P_3\). This is the actual source-to-target admission failure, without
switching the push/pull orientation.

As a dual check, the same coordinate indicator is constant along target
\(P_3\), but \(f(T0)=1\) and \(f(Tv)=0\), so its pullback is not constant
along source \(P_0\). These separators avoid presuming that a point delta
is admissible on an entire quotient fiber.

This is one selected off-diagonal native admission failure. The checker
reconstructs only two routes and one ordered off-diagonal pair; it does
not claim to replay the predecessor's 12,210-pair theorem. It excludes the
free future-code admission used in that early-promotion proposal. It does
not exclude a changed promoted-input factory, a proved current-word
normalization cancellation, or a different controller. The historical
undo/code/redo workaround still has its stated 111+111 child bill, before
source access and precision.

## Evidence and remaining boundary

The standalone checker uses its own elementary matrix algebra over the
free group ring. It authenticates and extracts only `recipe` from its
source, independently reconstructs the event list, and replays both
controllers for \(B=1,\ldots,12,16,32\), on all \(2B\) symbolic inputs.
It checks both inverse products and chronological gatewise
inverse-transpose propagation, with independent transpose symbols.
These finite fixtures verify the implementation; the ladder induction
above is the all-\(B\) proof. Neither is a formal-kernel proof.

Controls remove actual terminal operations, alter a code direction or
bank, change a compensation sign, restore a stale coded \(F_2\), and change
one actual inverse-code direction. The signed endpoint is involutive, so
repeating the complete forward word would be a vacuous inverse control.
Deleting a normalization deliberately leaves the abstract logical endpoint
unchanged and is rejected only by the declared native inventory check.
That distinction is recorded, not hidden.

No actual integer R429 map without target helper leakage, native global
phase, mixed-owner hosting, full supplier histogram, physical source-access
cost, whole-word rounding/COPY certificate, or outer multiplication theorem
is established here. No new conditional kappa is claimed.

The controller and geometry lineage is retained from the old
DreamingOfClouds/eumemic/PR555,543,545,510 work, Ali Romman's R438 deletion
and source builder, Sagar Thakrar's transported R438 hosting, and the prior
source-code preparation interface in Ali Romman's PR1862. The six-code
hybrid and original selected route witness are preserved predecessor work.
This contribution adds the all-bank clean-tail proof, the two-code
construction, its restricted occurrence lower bound, and an independent
exact audit. Substantial OpenAI Codex assistance was used; new material is
Apache-2.0.
