# Why free helper endpoints are the audited P104 contract

## Setting
A P104 local word has 735 public registers: 104 X sources r, 104 Y targets r+112, and 527 helpers.
Frames are subspaces F of F_2^9 with native charts T_F. Each helper h has an initial frame A_h and a
final frame B_h with A_h ⊂ B_h. A MOVE F → G applies T_G T_F⁻¹ and is paid at rank dim G − dim F. An
ADD/COPY/SCALE requires its registers to sit in one common frame.

## Lemma 1 (chart invariant)
Let x_k be the independent inputs. If every register r starts with physical content T_{A_r}(x_r), then
after every event its physical content is T_{cur(r)}(row_r · x). Here row_r is the exact rational row
replayed by `local.replay`.

*Proof.* MOVE: T_G T_F⁻¹ T_F(v) = T_G(v). Same-chart ADD: T_f(u) + q·T_f(v) = T_f(u + q v), by linearity of T_f.
COPY and SCALE are the same. INIT/CLEAR of owned fields set the row and the content to zero. ∎

## Lemma 2 (helper autonomy)
`local.replay` requires every helper row to end as {h:1}, every main row to have the literal expected
form, and every owned row to end at zero. By Lemma 1, the module therefore maps a helper input
y = T_{A_h}(x_h) to T_{B_h}(x_h) = T_{B_h} T_{A_h}⁻¹ y. It does not contaminate any other output. ∎

## Proposition (delivered target)
`native()` lowers U_h = T_{B_h} T_{A_h}⁻¹ = M_left · G_r · M_right. Here M_left and M_right are Clifford
monomials and G_r is the canonical rank-r native Gaussian with r = dim B_h − dim A_h. Exact signed-Pauli images and a dense
phase anchor are checked; the independent #5550 checker repeats both checks. Feed the module M_right⁻¹ z for an
arbitrary fresh z, and apply M_left⁻¹ to its helper output. The composite is then G_r z. So every helper
delivers one productive rank-r Gaussian on an arbitrary fresh input. The two monomials are ordinary
routes, priced in `local_routes` and bounded by #5550's ordinary census.

The proposition does not depend on A_h being the zero frame. A higher start reduces the credited rank r
by exactly the dimension of the removed climb. Nothing beyond the paid MOVEs and the two priced
monomials enters the delivered target.

## Consequence for #5561
The #5561 words change only helper initial/final frames, frame labels and MOVE stops. Their legality
against the #5551 word is #5561's own `retime.py`. The unmodified `local.py` replay and native maps
accept them, and #5561's verifier passes. The #5550 checker, with only its input lines swapped, binds all 527
helper endpoints by exact native checks. It reproduces the invoice from MOVEs and native ranks, and fits the
ordinary census inside the retained allowance (`verify.py`). Hence hypothesis (c) adds nothing to the
contract under which #5545 was audited.

## Precedent
- #5545 (audited by #5550): 192 nonzero helper starts and 65 below-FULL finals.
- T74 entering helpers: S_E = T_FULL T_E⁻¹ = L_E (C_[w] ⊗ I) R_E, with paid wrappers (#458, Lemma A).
- Hyperplane-ended helpers: residual T_U T_E⁻¹ with pair wrappers R_(E,U), L_(E,U) (#591 review).
- The one recorded failure of an entering helper (PR2478 audit of T74) came from that emitter's separate
  zero-frame precondition phase, which ran before the entry adapters. A P104 word is a single chronology
  checked by Lemma 1, and it has no such phase.

## Not covered
Retime legality, pricing, strictification and outer funding of #5561. Validity of the #5551 parent.
Inherited local all-input native semantics and the five framework assumptions. Human or proof-kernel
acceptance.
