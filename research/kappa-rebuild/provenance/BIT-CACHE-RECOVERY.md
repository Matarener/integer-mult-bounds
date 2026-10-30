# BIT, cache, and relay recovery record

## Status

This is a **new recovery record**, created on 2026-10-21 after the execution workspace reset. It is not a replacement for the missing repository, the earlier cumulative checkpoint, or the complete scientific receipts produced before the reset.

The original BIT and cache sources are unavailable. Their recorded hashes and previously reported outcomes are preserved in [LOST-BIT-CACHE-PINS.json](LOST-BIT-CACHE-PINS.json). A recorded hash cannot recover its file. No approximate reconstruction has been placed under a missing source's original filename.

The self-contained [RELAY-PROBES.js](RELAY-PROBES.js) and [RELAY-PROBES.json](RELAY-PROBES.json) are runnable recovery artifacts. The relay function was retained in the tool runtime across the filesystem reset. Its wrapper, explanatory checks, noncommuting example, and this record are new. **They establish no new native supplier and no new κ.**

## Reproduce the surviving probe

From the recovered workspace root, run:

    node recovery/RELAY-PROBES.js

This requires Node.js and no external package. It writes recovery/RELAY-PROBES.json and records the source SHA-256 inside that receipt. An optional first argument chooses another output path.

The receipt is deterministic. The finite menus complete in about one second in the replacement workspace. The principal exact checks concern integer operators and row ranks over the prime field F_65521. The cost screen uses ordinary double precision and is explicitly not an interval-certified admission test.

## Model and interpretation

For one of the eight correction channels, write t=L U, a=A, and v=t+a. The actual earlier construction has

\[
LK=13I,\quad C=[L,I],\quad B=\begin{bmatrix}-K\\11I\end{bmatrix},
\quad CB=-2I,\quad H=I+BC,\quad H^2=I.
\]

The compressed state tracks all t coordinates, all a coordinates, and one arbitrary cache coordinate for each local stage. It never assumes an initially zero cache.

The default forward functional exchange occurs after the H update. It maps C X to the incoming dirty cache value and saves the old C X in that cache. The default backward exchange occurs before the negative H update and swaps C Y with its dirty cache by changing the selected A coordinates. The script also allows the latter target exchange before a forward update.

The observed final rows are selected A, all caches, and the ordinary final Y functions. The missing ordinary X corrections are tested against their span. The productive restoration test additionally demands the original independent cache coordinates.

A modular rank gap is used conservatively. In these negative menus the observation matrix has its full possible row rank; a larger stacked modular rank proves that the required rows are outside the rational observation span. A zero modular gap by itself would not prove rational feasibility. The selected positive below is therefore checked as a complete exact integer matrix and given explicit equations.

This model grants common scalar charts. It does not establish native owner equivalence, physical frames, legal child phases, bank hosting, or correction costs.

## Completed bounded menus

| Menu | Cases | Result |
|---|---:|---|
| Additive relay with coefficient 0 or ±1, p=1 through5 | 15 | Main gap p−1; main plus cache gap p |
| Independent additive coefficients from −2 through2, p=3 | 125 | Gaps2 and3 throughout |
| Every subset of the standard exchanges, p=1 through4 | 680 | Productive restoration gap p throughout |
| Every bank assignment, p=1 or2 | 3,152 | Reusing a bank alone leaves productive gap p |
| Added target exchanges before forward stages, p=1 | 864 | 66 zero-gap scalar cases |
| Same extension, p=2 with the original distinct bank assignment | 256 | No zero-gap productive case |

The scripts do not silently promote any of these finite menus into a universal lower bound. Earlier exploratory menus mentioned in the research conversation are not reproduced here if their exact generating code did not survive.

### A pure negative-dirt relay cannot leave its source unchanged

After a forward exchange, the source function equals d_forward. If a proposed next cache is set to −d_forward while that source function remains unchanged, the outputs obey the exact relation

\[
C X_{\rm out}+P_{\rm next}=0.
\]

That makes the map singular. Additional independent untouched registers do not remove this output relation. A reversible relay must change the source function, retain another independent dirt component, or use a different chronological contract.

The receipt contains a small exact matrix witness. This does not exclude all catalytic relays.

## The positive p1 target-entry relay

The simplest new zero-gap scalar case uses one arbitrary eight-field bank P. Its chronological operations are:

1. Add H X to Y.
2. Before the backward update, exchange C Y and P, changing only the selected A coordinates.
3. Subtract H Y from X.
4. Before the last forward update, exchange C Y and the same P again.
5. Add H X to Y, then perform the terminal signed swap.

There are no forward source exchanges in this selected variant. With v=C X_initial and P_initial=d, the exact endpoint is

\[
P_{\rm out}=d,\qquad
X_{U,\rm out}=X_U-Kv,\qquad
Y_{U,\rm out}=Y_U-K(v+d),\qquad
C Y_{\rm out}=-v-d.
\]

Thus the required source function is observable as

\[
v=-C Y_{\rm out}-P_{\rm out}.
\]

In the coordinate order (L X_U, L Y_U, X_A, Y_A, d), the complete matrix is

\[
\begin{pmatrix}
-12&0&-13&0&0\\
-13&1&-13&0&-13\\
10&1&11&1&-1\\
12&-1&12&0&12\\
0&0&0&0&1
\end{pmatrix}.
\]

The source checks this matrix exactly. Omitting the second target-entry exchange restores the productive information deficit and is a negative control.

The physical issue is now specific: the function can be algebraically recovered, but adding K v into the final ordinary X holes is still unpaid. Cache movement and actual owner charts must also be verified. This endpoint is not the desired full outer operator.

### Exact paired-query admission gate

Suppose the first exchange uses C1 and selected-coordinate insertion E1, with C1 E1=I. If Y0 is the target before that exchange, then

\[
Y_1=(I-E_1C_1)Y_0+E_1d.
\]

If the later exchange instead reads C2, the returned bank equals

\[
P_{\rm out}=C_2(I-E_1C_1)Y_0+C_2E_1d.
\]

Restoring d for every independent Y0 and d requires

\[
C_2(I-E_1C_1)=0,\qquad C_2E_1=I.
\]

Consequently C2=C2 E1 C1=C1. Actual physical transports must be included before making this comparison. Transporting arbitrary bank contents does not by itself turn one owner function into another.

The source includes the negative example C1=(1,1), C2=(2,1), E1=(0,1)^T. Both queries have the same right inverse, yet the returned bank is d+Y0_U. This catches the precise mistake of assuming that equal channel count or equal insertion geometry implies equal functions.

### A more promising changed premise: the same future query at both contacts

The complex agent identified a useful next gate: earlier causal geometry may permit a future query chart at a current pre-Y contact. That source is unavailable after the reset, so its applicability must be reauthenticated.

If both exchanges can deliberately use the same future query Q and right inverse E, QE=I, then the bank return does not require the intervening kernels to be equal or commute.

Set T=I−EQ and let H0, H1, H2 be the actual three kernels, expressed in one correctly transported chart. The full equations are

\[
Y_0=Y+H_0X,\qquad
Y_1=TY_0+Ed,\qquad
X_1=X-H_1Y_1.
\]

The second exchange gives

\[
Y_2=Y_1+E(QY_0-QY_1)=Y_0,\qquad P_{\rm out}=QY_1=d,
\]

because T²=T, TE=0, QT=0, and QE=I. After the last forward update and terminal swap,

\[
X_{\rm out}=Y_0+H_2X_1,\qquad Y_{\rm out}=-X_1.
\]

The recovery script verifies this identity with explicit noncommuting reflection matrices. It does not import the false premise H0=H1=H2.

This is the strongest next finite native gate: prove that one chosen future Q and E are legal at both contacts, emit their actual frame path, and compare the full remaining correction invoice with the productive-helper budget. A failure of that geometry should stop this particular construction before a large search.

## A dyadic catalytic reflection identity

The literature lead was [Folkertsma et al., Fast Cliffords When Your Quantum Memory Is Full](https://arxiv.org/html/2609.40144v1), especially its dirty-workspace cancellation construction. That construction starts from a primitive whose workspace is already restored. An accumulating dirty logger does not satisfy that premise.

For our dyadic setting, define

\[
U(B/2):(x,d)\mapsto(x+\tfrac12Bd,d),\qquad
L(C):(x,d)\mapsto(x,d+Cx).
\]

The chronological three-factor map R=U(B/2)L(C)U(B/2) satisfies

\[
R(x,d)=\left(x+\tfrac12B(Cx+d),\,Cx\right),
\qquad (Cx,d)\mapsto(-d,Cx).
\]

Therefore R² sends (x,d) to (Hx,−d). A final sign change of the cache gives (Hx,d), restoring arbitrary dirty state. After merging adjacent U factors, this uses two C queries and three B scatters.

The source verifies a small exact dyadic instance, and rejects omission of the final cache sign and substitution of CB=−I. This identity is useful only if the required queries and scatters are physically available and affordable. It supplies no free native contacts.

## Exact-bill screen for the productive p1 hosting proposal

The complete frozen identity supplier was reported to add eight rank-eight calls to each **unpruned** clean-J word. It cannot be attached directly to the newer pruned bill.

With H_r=r^(1−κ), the reported THREE profiles are:

| Profile | H1 | H2 | H3 | H4 | H5 |
|---|---:|---:|---:|---:|---:|
| Pruned | 2,453 | 716 | 224 | 74 | 48 |
| Unpruned | 2,487 | 713 | 224 | 102 | 20 |

Their difference is 34H1−3H2+28H4−28H5, with zero rank-mass difference.

For p1, 408 extra productive helper fields give width632 and outer rank25. The balanced residual is 129H1+84H2. The resulting numerical screen is:

| κ | Allowance after raw pruned supplier and residual | Extra complete identity cost | Remainder |
|---|---:|---:|---:|
| .001745 | 148.923223219 | 191.692397443 | −42.769174225 |
| .004 | 52.601345502 | 191.296597415 | −138.695251913 |

Thus this already-complete local identity fallback fails the relaxed budget at both requested targets. It does not resolve the productive-cache controller.

The originating profile receipt is missing. These values are a transparent recomputation of profiles supplied in the surviving agent messages, not a replacement for authenticating that receipt.

## What was completed before the reset, and is now missing

The JSON pin catalog records the exact known hashes of three BIT documents and five cache source/document/receipt files. These are expected hashes for future recovery, not verification of currently present files.

The prior BIT scope contained finite native positive constructions. For its strongest 16-output variant, the recorded counts improved from582 helpers and38,415 ADDs to382 helpers and20,439 ADDs, with full finite margin gain83.3295445158 atκ=.004. The full h19 forest screen still failed:24,167,112 helpers and108,002,708 ADDs, with moment1.00631395 atκ=.004. No global BIT supplier or κ increase was established.

The cache primitive had four provider variants and a full640-input operator audit. The cheaper suffix preserved the raw-J main operator, restored all408 native helpers, and produced P_out=d+C X_initial with8H9 and4,224 additional scalar allowance. It used no additional owned temporary field. The cache itself was not restored and received no productive-output credit. The earlier prefix comparison cost8H1+8H9 and8,560 scalar allowance and used one reusable owned temporary.

The cache reproduction command, after authenticating and restoring its sources and dependencies, was:

    python3 -B research/kappa-accounted-composition/cache/dirty_log_forward.py

Its historical generation produced18 artifacts. They are currently unavailable. Their existence and previously reported audit outcomes are not a fresh replay.

## Recovery order

1. Restore the attached base and the latest fully packaged cumulative checkpoint into a new checked location.
2. Authenticate restored files against the recorded pins and the package's own complete manifests. Preserve all scopes the user has not said were merged.
3. Recover the newest research sources only from authentic saved bytes. Do not manufacture old hashes, receipts, or missing generation outputs.
4. Re-run this self-contained relay receipt independently.
5. Authenticate the future-query contact geometry, then test the same-Q two-exchange relay with actual owner operators, every arbitrary dirty input, chronological cuts, and the complete bill.
6. Continue to require a whole supplier and outer admission before reporting a new κ.

