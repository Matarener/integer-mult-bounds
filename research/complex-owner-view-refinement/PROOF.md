# Original selected complex owners and their common view

Copyright 2026 Sagar Thakrar. Apache-2.0.
Prepared with substantial OpenAI Codex assistance.

This is a source-bound refinement of the `local_cover_sweep` branch of
`SelectedBinding.group` in PR3385, at
`7e5a187214126d31afc241a8f89f4a652352b58c`. It proves the direction of the
owner selector and the entrance/exit composition for every orthogonal cover
label. The accompanying finite check binds the formulas to all 144 original
selected local calls and their 101,376 owner occurrences. The theorem is
conditional on the declared packet and operator endpoints below; it is not
a physical execution of the selected cover.

## 1. Matrix convention and hypotheses

Let $V=\mathbb F_2^{73}$, with column vectors and the standard dot product,
and let $G=O(73,2)$. Fix one selected local call. Its roles
$i=0,\ldots,703$ have distinct family labels $F_i$, orthogonal owner
charts $\sigma_i\in G$, and literal data-alignment vectors
$\eta_i^{\mathrm{in}},\eta_i^{\mathrm{out}}\in V$. Both alignment vectors
are zero for helpers. A physical packet is indexed by a pair $(F,g)$,
where $g\in G$.

There are two different representations in the source:

* `Owner.sigma_columns` is the tuple of **columns** of $\sigma_i$.
* `cover.act`, `cover.multiply`, and the monomial field `matrix_rows`
  interpret their tuples as **rows**.

Consequently, passing `sigma_columns` to those row-based functions represents

\[
 R_i=\sigma_i^T=\sigma_i^{-1}.
\]

No additional transpose is to be inserted. In the local branch the source
variable named `g = cover.unrank(cover_index)` is the **common** label, called
$d$ throughout this proof. The physical owner label will instead be
$g_i=dR_i$.

The following endpoint premises delimit the refinement.

1. The inherited `OrthogonalCover` encoder is a bijection between its valid
   ordinals and $G$, and decoding followed by encoding preserves a matrix.
   This package uses its retained proof and bounded actual ordinal checks;
   it does not enumerate or independently reprove the full cover encoder.
2. The selected source data and finite binding are immutable. The literal
   local program denotes a well-defined operator $A$ on the 704 gathered
   packets, with any private work initialized and returned as its contract
   requires. Native calls, scalar operations, child returns, and local
   monomial recipes have their declared exact endpoints. In particular,
   importing or matching their compiled instructions is not a proof of
   their physical implementations.
3. Gathering and scattering select the indicated complete packets without
   aliasing other packets. The monomial backend realizes its declared
   forward/inverse permutation and translation on every active tensor
   coordinate, with the same action on each applicable column and with
   all declared spectator fields preserved. Packet extents, backing,
   ownership, precision, clean scratch, and the paid access contract are
   inherited premises, not consequences of the finite matrix checks here.
4. The data-alignment bit vectors have the meanings assigned by the pinned
   selected phase specification. This package binds those literal vectors
   and their pullbacks; it does not reprove the complete phase specification
   or the global chronological operator identity.

## 2. Binding the charts and literal alignments

The source constructs the charts from the pinned selected archive. The
following observations also explain why the reconstructed charts are
orthogonal, beyond simply testing their matrices.

For a literal port $q$, the source has $q\cdot q=1$, and chooses a
missing coordinate $m<9$. Thus $v=q+e_m$ has $v\cdot v=0$. The map

\[
 T_v(x)=x+(v\cdot x)v
\]

is an orthogonal involution. `port_basis` returns the columns of $T_v$
after swapping input coordinates $0,m$. It is therefore an orthogonal
basis with first column $q$, supported on the first nine coordinates
except for the unchanged higher coordinate axes.

The stage-zero data chart is the identity. At a later selected stage $s$,
`data_route` uses the eight vectors

\[
 v_j=b_{1+j}+e_{9+8(s-1)+j},\qquad 0\le j<8.
\]

Their self-products and pairwise products are zero: the $b_{1+j}$ are
orthonormal, and the eight new coordinate axes are distinct and outside
their support. The corresponding transvections commute. Their product is
exactly the simultaneous XOR formula in `data_route`, so this chart too is
orthogonal. The finite binding also checks the literal route
`[1, stage, port]`, rather than inferring it from a register number alone.

For a helper the raw idle-child axes determine the active positions in the
port basis. The serialized spectator completion supplies precisely the
first unused positions needed to complete the first nine coordinates.
Appending all remaining positions gives a permutation of the port basis.
The source hashes these exact columns and requires equality with the
emitted chart dictionary. The independent ledger reconstructs these
choices from the raw records, including all 10,002 emitted helper charts.
It does not substitute a generic identity chart for a helper.

For each data owner the source stores

\[
 \texttt{entry}_i=R_i\eta_i^{\mathrm{in}},\qquad
 \texttt{exit}_i=R_i\eta_i^{\mathrm{out}}.
\]

These are precisely the results of `act(sigma_columns, alignment[...])`
under the row convention. For helpers the `Owner` defaults give zero for
both fields. The finite ledger checks these fields separately from the
chart equality and checks distinct families separately for each call.
Families may recur in different chronological calls.

## 3. Owner selection for every common label

By definition of the common view, the physical and common labels satisfy

\[
 g_i\sigma_i=d.
\]

There is exactly one solution,

\[
 g_i=d\sigma_i^{-1}=dR_i.
\]

The source selector
`(owner.family, cover.rank(multiply(d, owner.sigma_columns)))` is therefore
the correct physical packet. This proves the composition for every
$d\in G$, including noncommuting $d,R_i$. The reversed product $R_i d$
would not solve the defining equation in general.

The retained separating example is the actual call-zero helper at role
224, family 13006, port 14, with route `[3, 4, 0]`. For the tested cover
$d=T_{15}T_{30}$, applying the correct product $dR_i$ to $e_0$ gives
602, whereas the reversed product gives 518. Integers here encode binary
vectors. This is a control against a real composition-order error, not a
claim that the frozen source makes that error.

## 4. Entrance, exit, and the local operator

Write $P_L|x\rangle=|Lx\rangle$ and
$X_a|x\rangle=|x+a\rangle$. Products of operators act rightmost first.
In particular

\[
 P_LX_aP_L^{-1}=X_{La}.
\]

The generated global monomial literals have zero scalar, linear, and
quadratic phase fields. Hence the following calculations include their
full declared action, not only their underlying affine maps.

For role $i$, `group` first emits the inverse of the literal $d$, then
the translation by `entry` when that vector is nonzero. Its entrance is

\[
 E_i(d)=X_{R_i\eta_i^{\mathrm{in}}}P_d^{-1}
       =P_d^{-1}X_{g_i\eta_i^{\mathrm{in}}}.
\]

Equivalently its address map is

\[
 x\longmapsto d^{-1}x+R_i\eta_i^{\mathrm{in}}
              =d^{-1}(x+g_i\eta_i^{\mathrm{in}}).
\]

After the complete local word, the source emits the exit translation
followed by the forward literal $d$. Thus

\[
 L_i(d)=P_dX_{R_i\eta_i^{\mathrm{out}}}
       =X_{g_i\eta_i^{\mathrm{out}}}P_d,
 \qquad y\longmapsto dy+g_i\eta_i^{\mathrm{out}}.
\]

For helpers both translations disappear. For a data owner entrance and
exit need not be each other's inverses: they bind the source's two
different boundary alignments.

Let $E(d)$ and $L(d)$ be these blockwise maps on the 704 selected
packets. Under the endpoint premises in section 1, the emitted group
implements exactly

\[
 L(d)\,A\,E(d).
\]

The local word may mix its packet roles; nothing in this assertion assumes
that $A$ commutes with a translation or with a chart. For a single-role
operator the corresponding expression is

\[
 X_{g_i\eta_i^{\mathrm{out}}}\,P_d A P_d^{-1}\,
 X_{g_i\eta_i^{\mathrm{in}}}.
\]

The identities hold independently on the backend's declared tensor
coordinates. Their lifting to actual tapes, including spectator
preservation, remains conditional on that backend's endpoint contract.

## 5. Packet partition and reusable ownership

For this fixed call let

\[
 \Omega_d=\{(F_i,dR_i):0\le i<704\}.
\]

If $(F_i,dR_i)=(F_j,eR_j)$, distinct families first give $i=j$.
Right multiplication by $\sigma_i$ then gives $d=e$. Therefore the
sets $\Omega_d$ are pairwise disjoint. Conversely, for any selected
family $F_i$ and any physical label $g\in G$, taking $d=g\sigma_i$
places $(F_i,g)$ in exactly one such set. Thus the sweep partitions all
cover packets of each of the call's 704 selected families, and touches no
other family.

This is a partition of mathematical packets, not a proof that an
unpriced physical random access exists. A physical implementation may
reuse its work tapes between groups only under the gather, scatter,
scratch-cleanup, and ownership premises stated above. Nor does this
partition permit reordering different chronological calls, whose owner
families can overlap.

## 6. Evidence and attribution boundaries

The universal statements above quantify over every $d\in O(73,2)$.
The finite replay instead checks the exact original owner ledger and the
instructions returned by all 144 unchanged local group constructions at
an explicitly chosen nonidentity matrix. Its symbolic cover adapter
preserves the actual matrices used in selectors while avoiding enormous
ordinal enumeration. It is declared separately from the bounded calls to
the actual rank/unrank implementation. Neither finite mechanism is being
used to infer a universal matrix identity by sampling.

Jose Manuel's PR3385 supplied the controller, the row/column convention,
the owner formulas, and the selected bindings. Its existing check already
uses a nonidentity cover for a terminal-translation control; the present
separating control concerns owner composition and all literal local-owner
bindings. The owner/common-view algebra has earlier binary-lane lineage
in [PR2569](https://github.com/CrocSwap/integer-mult-bounds/pull/2569),
`research/selected-source-packets`, at
`898ff36fe2cd05f733de6b26c88a4c4741b06237`.

[PR3106](https://github.com/CrocSwap/integer-mult-bounds/pull/3106),
`research/selected-first-prefix`, at
`1a9da866330d31d7b6edc5f514802a3ab2176f88`, already proves the packet
partition and a physical whole-family first-prefix refinement for call
zero's data roles 119 and 169. Their charts are identities and their
entrance translations vanish. That result explicitly retains the full
helper-chart census as a premise. This package independently binds the
original complex controller's complete owner ledger and noncommuting
composition, with its literal data pullbacks; it does not reclaim that
prefix result or originate the general routing algebra. The selected
phase and helper-chart work inherited by PR3385 retains its own source
attribution in the frozen proof and manifest.

No full selected physical payload, outer multiplication transfer,
uniform cost invoice, new supplier, or changed T74 caller is proved here.
This is a written algebraic refinement with finite source-binding checks,
not a proof-assistant kernel certificate.
