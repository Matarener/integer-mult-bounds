# A typed joint module for one polarized cross-cube block

This proof supplies one directed `H_ab` side primitive. It is not all of H,
the reciprocal pair, a K-core schedule, a Gaussian-job caller, or a kappa
claim. The emitted module has 512 source fields and 512 reader fields, hence
1,024 independent original inputs. The reciprocal primitive would use 1,024
source fields and 1,024 reader fields and has a separate invoice.

The rank-one scalar identity and Clifford synthesis are standard algebra.
The contribution here is the source-bound polarized rectangle contract,
its four coframe groups, actual flag paths, exact phase compilation and
complete owned-cache lifecycle. Retain the #5439 geometry author and the
P112/E8, native-word, #4929, normalizer and Clifford predecessors credited in
the pinned sources. This work used substantial OpenAI Codex assistance.

## 1. Literal port data and charts

The pinned normalizer file gives the original 112 binary labels and the eight
root columns. The pinned polarized-channel file describes all 64 terms

`H_ab = sum_(j=1)^64 a_j b_j^t`

with exact dyadic coefficients. Its predecessor geometry checker verifies
this equality against every entry of the 512-by-512 block. This module does
not substitute the rank of a support pairing for a Gaussian-call invoice.

Every channel has 68 source ports and 68 reader ports. The literal supports
fall into four pairs `(S_g,R_g)`, each with 16 channels. Each pair has 128
distinct source fields and 128 distinct reader fields. Every field occurs in
exactly one pair. These facts, including membership and every coefficient,
are regenerated from the pinned channels in `module.py`.

The raw three-block labels live in 27 coordinates but span the nondegenerate
25-space of equal block parities. `PROGRAM.json.gz` records an explicit
orthonormal basis of this space. Dotting a raw label against this basis gives
its 25 physical coordinates, preserving all pairings. For every group,

`dim S_g=dim R_g=8`, `S_g perpendicular R_g`,

and their radicals coincide in a six-space D_g. Their joint span has dimension
10 and radical D_g. Every source q belongs to S_g and has norm one. Every
reader q has norm one, is outside S_g, and satisfies `S_g subset q-perp`.

For an ordered full binary basis G, use the pinned native monomial

`K_G = D_Q P_G`, where `Q=I+G^-T G^-1` over F2,

with the pinned Z4 diagonal convention (diagonal linear phases are 0 or 1).
Put `C_A=product_(j in A) C_j` and `R=C_all`. The actual canonical frame word
`K_G.adjoint().then(C_A).then(K_G)` represents

`Phi_(G,A) = K_G C_A K_G^-1`.

This order matters: `.then` appends a gate acting on the left. All executable
frames, monomial wrappers and paid children are supplied as literal words.
Reader `q-perp` endpoints use the explicit ordered basis starting with S_g,
completed within q-perp; no unrecorded replacement by another chart is made.

## 2. Exact native full-Gaussian conjugation

The main source exit uses the monomial `T_G=R K_G R^-1`. Here is its absolute
zero-column phase, valid for every dimension n.

Write `G^-1 e_j=v_j`, and put

`d_j=floor(wt(v_j)/2) mod2`.

If q is the Z4 quadratic phase used in D_Q, expansion of binary Hamming
weight gives

`q(y)+wt(G^-1 y)=wt(y)+2 d dot y mod4`.

Indeed the polar cross terms cancel modulo four. The coefficient of y_j on
the left, after subtracting wt(y), is
`alpha_j+wt(v_j)-1`, where `alpha_j=(1+wt(v_j)) mod2` is 0 or 1. This equals
`2 floor(wt(v_j)/2) mod4`, proving the formula.

Let `a=(1-i)/2`. For the pinned child convention `C=H diag(1,i) H`,

`R^-1|0> = a^n sum_x i^wt(x)|x>`.

Applying K_G and the preceding identity yields `Z_d R^-1|0>`. Consequently

`T_G|0> = R Z_d R^-1|0> = (-i)^wt(d)|d>`.

The exact signed tableau of T_G has Gaussian rank zero. Its tableau fixes
the remaining monomial address/quadratic data; the displayed column fixes
its global phase. `frame_tools.py` therefore emits a literal P/D/X/phase
word for T_G without a 2^25 state vector. The code checks the signed tableau,
including its predicted offset, against that word. The written calculation
is the universal phase proof. Root's independent small-dimension dense tests
are corroboration, not the universal argument.

## 3. Paid paths, with literal chronology

Fix a group and write `Phi_S=K C_[0,8) K^-1`. For a source with input line q,
choose a full basis beginning with q and then completing S. The rank-one and
rank-eight frames for this flag are connected to the declared input line
frame and the common Phi_S by monomial gauges. Every such low-rank gauge is
checked with an exact signed tableau and a fresh sparse Gaussian-integer
absolute-column evaluator. The paid part between them is exactly the seven
children on flag axes 1 through 7. Thus the source input line reaches S with
one H7, with no hidden Gaussian in either wrapper.

For its exit, the exact identity is

`R Phi_S^-1 = T_G C_[8,25) K^-1`.

Execution is therefore **K^-1, then 17 children, then T_G**. This is the
correct chronological order and has an explicit analytic absolute phase.
It carries the source to the canonical full R25 frame.

A reader starts at ground and reaches Phi_S by K^-1, eight children, K.
Choose its ordered q-perp basis to start with the eight S vectors, then add
16 vectors to span q-perp. A monomial, phase-correct gauge changes the common
S frame to this flag's S prefix. The subsequent paid part is precisely the
16 flag children on axes 8 through 23. Its endpoint is the recorded rank-24
q-perp frame. Since reader q is orthogonal to S and not in S, this is an
actual containing flag; orthogonality alone is never used to declare an ADD
between distinct frames ordinary.

For all 512 fields of each kind the emitted paths have histogram

`paid = {7:512, 8:512, 16:512, 17:512}`.

The source line services are the **entry contract**, not an erased bill.
A complete caller must supply and fund them once. No target credit is inferred
from a mixed reader endpoint, and the module does not fund its caller's final
termination.

## 4. Actual common-frame gather and arbitrary old values

At one group's cut all 128 source fields and all 128 reader fields are
physically in the identical Phi_S chart. Original source x_s and reader y_r
values are arbitrary and independent. This is a stronger condition than
merely saying that their possible flags contain related subspaces; the paid
paths above establish the actual chart.

For a channel `(a,b)`, borrow owned C0 with logical value zero in that same
chart. Perform

`C0 += sum_s b_s x_s`,

`y_r += a_r C0` for each reader,

`C0 -= sum_s b_s x_s`.

All operations are ordinary scalar ADDs at the common chart. They have the
same action physically because Phi_S is linear. The source fields never
change logically; source and reader role sets are disjoint. Thus the last
sum uses exactly the same original source versions, and C0 is exactly zero.
The arbitrary old y_r is retained with coefficient one. No reader is assumed
zero and no original input is cleared.

All 16 channels in the group are executed while those fields stay at Phi_S.
Only after the group's last gather do main fields leave the common chart.
There is one zero-retag into the group chart, one explicit CLEAR_ZERO after
the cache has already been uncomputed, and one zero-retag back to its original
ground chart. The same C0 is then available for the next group. Over four
groups the actual lifecycle is

`13056 ADDs, 4 CLEAR_ZERO, 8 ZERO_RETAG, one owned zero cell`.

No independent COPY and no 408-helper bank is used. A general borrowed dirty
cell at S can instead be restored by the four-stage subtraction/gather/read/
ungather protocol checked by `check.py` (272 ADDs per channel). That alternative
does not make a fresh independent dirty input available at S for free; the
emitted full module uses owned zero C0 and claims no helper target for it.

## 5. Full local endpoint and widths

Let x denote the 512 original source values and y the 512 original reader
values. The exact scalar interpreter checks every original column and emits
the resulting rows. Its logical map is

`(x,y,C0=0) -> (x, y+H_ab x, C0=0)`.

The physical endpoint is

`source_s: Phi_[q_s] x_s -> R25 x_s`,

`reader_r: y_r -> Phi_(q_r-perp) (y_r+sum_s H_ab[r,s]x_s)`.

This triangular logical map is invertible and retains every independent
original input. It is a side-map primitive, not 512 autonomous Gaussian jobs
on original y. The emitted endpoint rows, per-reader frame words, path
references and monomial definitions are factorized in `PROGRAM.json.gz`.

All Clifford identities include absolute phase. Equality of signed tableaux
fixes a Clifford operator up to scalar; one exact absolute column fixes that
scalar. The low-rank gauges use literal Gaussian-integer column arithmetic;
the high-rank source exits use section 2 instead of a dense vector. Every
literal one-copy operator identity tensor-lifts to every positive field width
under the inherited columnwise semantics. In particular a one-copy phase
opcode theta lifts to scalar `i^(f theta)`, not silently to `i^theta`. Scalar
ADD identities hold at every width by linearity. No width-one matrix-sum
relation is extrapolated to a uniform-width identity.

## 6. Verification and exact limits

Normal and optimized `module.py` runs compare the scientific MODULE fields
and the **canonical decompressed** PROGRAM payload. Container gzip hashes are
environment metadata. Semantic controls use actual interpreters: an appended
phase i has the same signed tableau but a different absolute column; replacing
S by the different reader R chart requires a positive-rank Gaussian transport;
omitting an emitted uncompute ADD leaves C0 nonzero. These are rejected.

The module changes the producer contract from separated full helper banks to
a joint main-field common-frame gather, so the scoped #5439 separated-lift
obstruction is not its invoice. This does not prove that the new contract is
compatible with the K-core, reciprocal side block or any whole caller. Global
flag chronology, all other H pieces, terminal jobs, precision, ordinary work
and outer admission remain separate obligations. No unsupported target
credit, all-H theorem, whole-caller profit or kappa is claimed.
