# Exact native and direct physical controller

The complete raw unit has 17 main pairs, 19 native supplier invocations,
and 16 directly paid shears. Its productive and paid profiles are the
integer dictionaries in `parameters.py`. Their rank masses are 260798
and 259998. This note proves the new physical construction and identifies
the finite source gates. `PROOF.md` supplies the conditional transfer.

## 1. Source-bound local supplier

The local source is the arbitrary-input `THREE-base` reconstruction in
PR4359, retained by the committed PR4416 source export. It has 224 main
fields and 408 autonomous helper fields. Every input is arbitrary, and
every helper has a distinct physical owner.

The final supplier incorporates the fresh-helper boundary retiming from
[PR4441](https://github.com/CrocSwap/integer-mult-bounds/pull/4441), pinned
at head `ccdae89b2ab9ced24ee3e7adfdb670ef80d223d9`. Its source package is
retained at [../fresh-helper-boundary/](../fresh-helper-boundary/).
The updated PR4441 head
`5f9d871c6bd1b9e34db5a7ea5ef08a908e94db39` retains these same native
source bytes and also combines the retimed supplier with the p17
native/direct controller at conditional saving `0.00300105`. That
updated head and its complete dependency changes are retained in the
publication ancestry.

`local_supplier.py` authenticates and regenerates the modification:
117 helper entrances, 42 helper exits and 395 scalar contact frames change.
Scalar order and coefficients, all main boundaries, every warp's physical
entry and exit, and the owned center program remain fixed.

Here is why this retiming preserves the main operator. A field in frame
$S$ has physical value $C_S z$. A paid nested transport
$C_T C_S^{-1}$ changes its frame without changing its logical value $z$.
At a common frame, scalar addition satisfies

\[
C_S z_i+aC_S z_j=C_S(z_i+az_j).
\]

The generator inserts the required positive nested transport before each
next contact and completes each field to its declared final frame.
Induction through the unchanged scalar actions and warp words preserves
every logical row for arbitrary inputs. Main entrance and exit frames
stay fixed, so their physical forward and backward operators stay fixed.
No finite-order relation on the free warp symbols is used.

A helper with new entrance $S$ and exit $T$ implements
$C_T C_S^{-1}$ on its arbitrary physical input. Its productive width is
$\dim T-\dim S$. The exact Clifford compiler verifies that this is the
Gaussian rank of the complete boundary operator and provides both
monomial factors around a standard positive Gaussian child. Those factors
need not be an inverse pair. Apply their inverses at the input and output
boundaries of the complete local invocation. Every helper has a fresh
independent owner, so these normalizers attach to its whole job without
changing any other field's boundary.

Two independent retained interpreters replay both resulting orientations
on all 632 arbitrary persistent input columns, together with an arbitrary
owned-center entry column that is legally cleared. Every helper remains
logically autonomous. The phase compiler checks all 320 distinct new
transport or helper-boundary recipes in both orientations, retaining the
absolute phase through exact tableaux and Gaussian dyadic state vectors.
Unchanged edges retain their authenticated source phase evidence.

The same gauge induction applies at each permitted column multiplicity
under the source all-column contract. Every new fixed coordinate and
phase generator uses its permitted block lift. This is a chronological
identity of frame transports and scalar actions; the argument does not
infer an all-column implementation by taking the tensor power of a sum.

This retiming replaces the preliminary fifteen-tail-pruned supplier.
It subsumes all fifteen earlier terminal-climb deletions; no additional
pruning gain is applied. The final local productive helper profile is

```
H = {4:26, 5:2, 7:29, 8:42, 9:309}.
```

The eight original center paths retain their complete rank-eight requests.
The inherited center recipes verify their products including phase.
Every remaining query is counted:

```
L = {1:2253, 2:515, 3:445, 4:102, 5:40, 8:8}.
```

The pointwise real-scalar allowances are 158120 forward and 158168
backward. These counts are regenerated from the unchanged scalar words.
The ideal formal prefix row-$\ell_1$ maxima remain 457 and 169.
Every new transport and helper boundary monomial contributes its actual
movement and phase records to the finite program. A rank-zero normalizer
is still a paid finite operation.

## 2. Literal direct shear

For a source port let $q\in\mathbf F_2^9$ be its specified odd vector.
The complete source phase data supplies eight vectors $b_1,\ldots,b_8$
orthonormal and perpendicular to $q$. Thus the matrix with columns

\[
P=(q,b_1,\ldots,b_8)
\]

is orthogonal over $\mathbf F_2$. All 112 actual port choices are checked;
their $q$ weights are three or seven.

Write $X_q$ for address translation by $q$, and define the physical
Gaussian line operator by its exact kernel

\[
C_q=\frac{1+i}{2}I+\frac{1-i}{2}X_q.
\]

If $\Pi_P$ is the address permutation induced by $P$, then

\[
C_q=\Pi_P C_{e_0}\Pi_P^{-1},\qquad
C_q^2=X_q,\qquad C_q^{-1}=X_q C_q.
\]

These are literal equalities with global phase one. In particular the
inverse uses the same positive Gaussian child and one extra translation.
`native_geometry.py` checks both kernels using exact tableaux and the
absolute phase, independently lowers them to rank one, and checks the
two nonzero coefficients of all 512 coordinate columns. Omitting the
inverse translation is rejected at all 112 ports.

The direct forward stage acts on arbitrary physical arrays as follows:

1. Allocate an owned zero work stream and copy the complete source $X$.
2. Apply the input route $\Pi_P^{-1}$ to that copy.
3. Pay one rank-one Gaussian request on the copy.
4. Apply $\Pi_P$, then translate by $q$, giving $C_q^{-1}X$.
5. Add the copy to $Y$, retaining $X$, and release the copy.

The resulting main map is exactly

\[
S_y(Q^{-1}):(X,Y)\longmapsto(X,Y+C_q^{-1}X).
\]

The dual construction copies $Y$, applies $C_q$, subtracts it from
$X$, and releases the copy. It implements $S_x(-Q)$. The selected
controller uses only direct forward stages, but both kernel orientations
are checked.

The work stream includes the original field's complete control and
spectator ranges. It receives no productive output credit. Its transformed
value can be discarded after the read under the retained
[copy/transform/read/discard contract](https://github.com/CrocSwap/integer-mult-bounds/blob/da637c87c89482bc4c86be36bd0071b3d400dbed/notes/copied-centers-lemma.tex).
That source explicitly covers complex inverse transforms and nonzero
temporary erasure. No inverse query is required to uncompute an owned
stream that is discarded through this interface.

For $f$ columns the address space has dimension $9f$. The address map
is $P\otimes I_f$, or its column-order version $I_f\otimes P$. Its
induced permutation on value arrays is the product of the per-column
permutations. The single recursive request has rank **$f$**, with active
span of the vectors $q\otimes e_j$ for $1\le j\le f$ over
$\mathbf F_2$. The inverse translation repeats $q$ in every column.
The request has the full current ancestor weight. Its invoice contains
one rank-$f$ request, with every whole-field route charged.

Each of the 1792 direct episodes is charged one paid request, 64
pointwise real-scalar primitives per full field volume, and an allowance
of eight nonrecursive full-stream movement/control records. Those records
cover initialization, copy, the two routes, inverse translation, read/add,
and release. The copy remains owned across the recursive call. Its bank
is included in the expanded stock bound until release.

## 3. Specialize the exact controller

The original complex local operators are

\[
F_s=D_sS_y(Q^{-1}),\qquad B_s=D_sS_x(-Q).
\]

The coefficient operators $Q,D_0,\ldots,D_{34}$ commute. Their symbols
form the rational Laurent ring used to factor the full p17 controller.
The exact retained-idle mask is 280378328416255, and the scalar boundary
words come from the source factorization. The pinned original rational
controller code is replayed by `controller/make_direct_case.py`.

[PR4440](https://github.com/CrocSwap/integer-mult-bounds/pull/4440),
at head `40e22a83ed660d3d6074c4f2dbf14bfb621eee51`, independently gives
the same query-thinning mechanism and p17 schedule. The combination of
that interface with the retimed supplier is also present in updated
PR4441. This package contributes an independent source-bound physical
certificate, the bounded controller search, a separately replayed p6
BIT supplier, and a refinement of the certified endpoint.

Set $D_s=I$ for the internal even stages

\[
s=2,4,\ldots,32.
\]

Leave $D_0$, every odd stage, and $D_{34}$ unchanged. This ring
homomorphism preserves the exact factorization. The sixteen specialized
local stages become the directly paid shears just proved. They have no
native helpers. The nineteen retained stages each receive 408 fresh
arbitrary helper owners.

The factory verifies every collapsed Laurent coefficient over the
rationals. A separate event interpreter replays the actual right boundary,
specialized local/idle/scalar word, and left boundary on every one of
the 34 main input columns. It compares all 1156 entries with the exact
diagonal, including the signs of every $Q$ power. Wrong native reverse
sign and wrong direct orientation controls are rejected.

## 4. Surviving native contacts on the full carrier

The proof keeps all original 281 address axes. Stage $s>0$ has its
original fresh eight-axis block. Unused even-stage axes remain arbitrary
spectators; they receive no productive rank from a deleted $D_s$.

The contact compiler keeps the original full-prefix reference frames at
each surviving native stage. These are invertible coordinate gauges used
to prove the physical operator identity on arbitrary inputs. They do not
assert that the incoming numerical values were previously produced by
every reference-frame transform.

For example, let $A_X,A_Y$ denote the reference entry frames and
$B_X,B_Y$ the exit frames. The exact contact checks prove

\[
B_XA_X^{-1}=B_YA_Y^{-1}=D_s,
\]

and prove that the cross term is $D_sQ^{-1}$ forward or $D_sQ$
backward, with the latter's scalar minus sign in the native word. Every
old spectator factor cancels in these quotients. Therefore changing
earlier stages to direct shears does not invalidate a surviving local map.

`native_geometry.py` checks all 8512 entry/exit contacts over the full
281-axis carrier. Each route is explicitly orthogonal and involutive,
fixes the actual $q$, and has the required complete quadratic phase and
physical translation. Both orientations are checked by exact polynomial
identities, retaining their inverse translations.

## 5. Idle and endpoint phases after specialization

Every literal idle window is specialized with the same stage mask.
An empty stage list is identity and incurs no Gaussian query. All sixteen
middle windows disappear this way. The initial and terminal windows have
positive ranks $16,24,\ldots,72$, each appearing 448 times in the paid
invoice. Each complete positive window is paid once per physical owner.

For a window containing stage zero, use the source's eight $q$-orthogonal
old axes and its exact `translation_after`. Append only the fresh axes
whose stage factors remain active. Other windows use only their selected
fresh axes. The verifier checks the complete Gaussian phase and the
independence of every such axis set. No old split tariff is substituted
for a complete idle request.

For a specialized output monomial

\[
Q^{\epsilon}\prod_sD_s^{a_s},\qquad
\epsilon\in\{-1,1\},\quad a_s\in\{0,1\},
\]

the target width is $1+8\sum_s a_s$. If $a_0=1$, its positive old
axes are all nine old coordinates; otherwise its old axis is $q$.
Append the selected active fresh blocks. A negative $Q$ power requires
translation by $q$, which is explicitly checked and charged.

The resulting 3808 main targets have ranks $17,25,\ldots,73$, each with
multiplicity 448, and rank 153 with multiplicity 224. The nineteen local
suppliers contribute 7752 additional distinct targets. The complete
census is 11560 independent productive fields and 69273 paid requests.
Their scalar allowance is 3500584, including every direct episode.
Their rank-one surplus is exactly 800.

`certificates/HYBRID-GEOMETRY.json.gz` contains the full contact, route,
kernel, endpoint and idle recipes. The native gate regenerates its
canonical JSON payload and compares the payload exactly; it does not
depend on the gzip implementation's stream encoding.
