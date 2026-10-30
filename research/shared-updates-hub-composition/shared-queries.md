# Composing actual sum acquisitions with the two protected P104 blocks

Dugongue, with substantial OpenAI Codex assistance. This is an informal source-bound composition proof. Its positive result is a complete local word combining PR 5802's three pending-sum acquisitions with the two released block changes already composed in updated PR 5795. It preserves the main endpoint, all independent helper inputs and every owned lifetime. It supplies exact paid and productive lists for the hybrid; the separate funding proof must use these full lists.

The proof uses literal source records and retained source identities. No constructor, scalar replay, rank routine, numerical evaluator, solver or Lean check was executed here. Existing source validation statements remain predecessor evidence, rather than a new replay of the composite.

## 1 Frozen source and exact edit direction

The common base is PR 5786 at `6b936acd68a7e0f9062037900f0fe9bc4b6fdd25`. Its decoded endpoint is

    T=I+sum_(r in the 104 live ports) e_(r+112)e_r^T.

Original helpers remain arbitrary independent inputs. The base has 770 public fields and 25 owned labels. Its retained native-copy and asynchronous-hub constructions are part of this source, not newly claimed changes.

The sum-acquisition branch is PR 5802 at `9bab1ca917ec4d1a4e60f4eb8c81d7ef92908a62`. Its fixed PLAN and WITNESS create three additional owned buffers, changing only the ten old chart fibres identified below. The two-block branch is updated PR 5795 at `206cb717c0c07737d61637b93f7502ca48850348`, using the R22 edit list from PR 5739 and the second block from PR 5796 at `4b30391e633ba0c7c674f03586ae97d443e9bc9c`.

Construct the hybrid by starting with the released PR 5802 word and applying the two-block edits through their protected record identities. Do not rerun the old graph-node numbers on the changed word. Do not use the old raw HUNKS positions as new indices. The old PR 5795 constructor's hard-coded 25-owned-label assertion must become a declaration for the actual 28-owned-label input; it is not a mathematical obstruction.

## 2 Literal footprint of the three acquisitions

All event indices in this table refer to the COMMON PR 5786 base, not to later step inputs. An interval begins immediately after its MOVE, or at its INIT/entrance, and ends at the next listed chart boundary. End denotes the word's exit. The changed old frame is replaced by the last column.

| Acquisition | PLAN node in its own step input | Role | Common-base start | Common-base next boundary | Old frame | New frame |
|---|---:|---:|---|---|---:|---:|
| 146 | 744 | 744 | original entrance | MOVE 17302 | 531 | 529 |
| 146 | 1738 | 146 | MOVE 13102 | MOVE 17822 | 531 | 529 |
| 146 | 1979 | 772 | INIT 13785 | MOVE 13789 | 531 | 529 |
| 146 | 3777 | 731 | MOVE 17297 | End | 531 | 529 |
| 173 | 1854 | 173 | MOVE 13473 | MOVE 17816 | 559 | 549 |
| 173 | 1969 | 791 | INIT 13761 | MOVE 13763 | 559 | 549 |
| 151 | 745 | 745 | original entrance | MOVE 17359 | 543 | 541 |
| 151 | 1793 | 151 | MOVE 13285 | MOVE 17819 | 543 | 541 |
| 151 | 1975 | 771 | INIT 13774 | MOVE 13778 | 543 | 541 |
| 151 | 3799 | 706 | MOVE 17354 | End | 543 | 541 |

The table is obtained by reading the source boundary records in order. The first step creates one INIT and one owned MOVE and removes the public role-146 MOVE and the later role-731 MOVE. Thus the boundary-node ordinal is shifted by one between those edits. This identifies step 2 nodes 1854 and 1969 with base nodes 1853 and 1968. Step 2's two new boundary records and two removed records restore its offset after the old owned-791 MOVE. Step 3's node 1793 is therefore the old role-151 node 1792; its node 1975 is the old owned-771 node 1974; its final role-706 node is again 3799. No scalar history or graph transformation needs to be executed to read these identities.

The six actual source updates are:

| Common-base index | Literal operation |
|---:|---|
| 13104 | ADD role 146 from role 640, coefficient -1/2, frame 531 |
| 13110 | ADD role 146 from role 641, coefficient -1/2, frame 531 |
| 13475 | ADD role 173 from role 613, coefficient 1, frame 559 |
| 13481 | ADD role 173 from role 611, coefficient 1, frame 559 |
| 13287 | ADD role 151 from role 630, coefficient -2, frame 543 |
| 13293 | ADD role 151 from role 628, coefficient -2, frame 543 |

The PR 5802 step-local indices 13478/13484 and 13290/13296 differ because preceding insertions and removals have already happened. Their source operands and coefficients are precisely the common-base records above.

Three existing COPY frames change, with roles and coefficients retained:

    COPY 791 <- 173, coefficient 1: frame 559 becomes 549;
    COPY 771 <- 151, coefficient 1: frame 543 becomes 541;
    COPY 772 <- 146, coefficient 1: frame 531 becomes 529.

Every copied decoded value stays the source value at its real version. None of these six roles belongs to the block support below.

## 3 The actual protected block support

Put

    P={41,42,65,106,240,400,401,403,405,410,741,
       57,81,92,224,225,227,229,234,742}.

The literal PR 5802 `protected` contract compares the COMPLETE subsequence of every instruction whose destination lies in P, or whose ADD/COPY source lies in P. It also retains each P role's original initial and final frame. Its retained receipt states equality of all 1704 such events, not merely equality of a list of destination labels.

The ten modified old fibres have roles

    U={744,146,772,731,173,791,745,151,771,706},

which is disjoint from P. The six selected source roles are 640,641,613,611,630,628, also outside P. The new buffers have owned roles 795,796,797 and no independent productive input.

The original R22 changes operate on P roles and change the helper boundaries of 741 and 405. The second block operates on the P roles 57,81,92,224,225,227,229,234,742 and changes helper boundaries 742 and 225. PR 5795 appends frame 1092 with basis `[11,21,38,448]`; PR 5802 uses only the old 1092 frames numbered 0 through 1091 and appends no chart. Thus this new frame number does not collide with a sum chart.

The source boundary changes are disjoint as well. The sum branch changes original helper boundaries only on 744,731,745,706; the two-block branch changes only 741,405,742,225. A productive debit is therefore never counted twice.

## 4 Lifting the block rewrite through the protected projection

Let pi_P be the subsequence of all instructions that touch P in the precise destination/source sense above. An instruction omitted from pi_P acts only on the complementary fields. It consequently commutes, as an exact linear operator, with a P-only instruction.

**Lemma 1.** Suppose a replacement of a run of P-only instructions has the same full decoded transfer on its P fields, with its supplied changed native boundary frames. If a larger word has the same pi_P sequence and P boundary frames as the source, the same replacement can be installed in that larger word while retaining every complementary instruction in its own order.

**Proof.** Between successive projected records, every hidden instruction touches only complementary fields. Within the selected P-only run these hidden instructions commute with each P-only instruction, so move them to the run boundary without changing their relative order. Apply the exact old/new P transfer equality, then restore the hidden instructions to their original gaps. Any instruction crossing between P and its complement belongs to pi_P and therefore cannot be hidden or passed through the run. Its order is retained. Native chart validity at such crossing contacts follows from the same projected source records and the same actual operand charts. QED.

The original R22 edit has exact scalar-transfer identities on its affected fields, already supplied by PR 5795. It contains no COPY, INIT or CLEAR. Its old/new 9-by-9 transfer and its separate 2-by-2 scalar edit are the retained sufficient identities; its other edits are native moves. The second block changes 102 scalar contact frames while keeping their coefficients and order. Its logical transfer is therefore unchanged without using any new scalar relation.

**Theorem 2.** Apply those two block changes to the protected projection of the PR 5802 word. The resulting hybrid has the same decoded endpoint T, 770 arbitrary independent public inputs, and the same 30 owned lifetimes as PR 5802. The three pending-sum read barriers, actual source versions and delivery equations remain valid.

**Proof.** The hypotheses of Lemma 1 hold by the literal projected-record and boundary equality. None of the sum sources, destinations, new buffers, or old changed fibres is in P. A P-only block has no internal read or write of those complementary fields. Hence the pending destination remains unread until its same delivery, and its two source values are collected at their same source events. Outside the block windows, equal decoded P transfers give equal state for subsequent cross-contact instructions. Induct over the two block replacements and over the remaining unchanged chronology. The owned INIT/COPY/CLEAR events of PR 5802 stay in the same order; the block edits contain none. The new sum buffers therefore still begin scrubbed, deliver their actual sums and return zero. QED.

This is a directional source construction, not a claim that two old executable constructors commute when handed the wrong schema, raw indices or graph-node IDs.

## 5 Exact native maps and phases are a union of parent maps

For an exact native coframe C_F, every affected transition is the literal operator C_B C_A^(-1), including its full scalar phase. No source operation is replaced by a binary rank label alone.

Every transition on U and on the new owned sum buffers has precisely its PR 5802 input/output frame pair; the two-block edits do not touch those roles. Every changed transition on P has precisely its PR 5795 pair; PR 5802 retained that complete protected field trail. Unrelated transitions retain their common source pairs. Thus the hybrid requests no new unseen frame-pair matcher: use the union of the two parent phase-correct lowering recipes. A scalar contact involving both P and its complement is an unchanged projected record, so it retains its actual common frame.

The existing frame 1090 is reused only after its R22 basis is identified. New frame 1092 is appended exactly as in updated PR 5795. All helpers retain their actual two-sided input/output Gaussian matching; no helper's final frame dimension replaces that whole-job grade.

## 6 Complete local and whole-caller bills

Relative to the common PR 5786 base, PR 5802 has

    Delta P_A=-6H1+4H2+2H6-2H7,
    Delta T_A=-2H1+2H2+2H7-2H8.

The two blocks together have

    Delta P_B=2H1+2H4-2H5,
    Delta T_B=-2H1+2H4+2H5-2H8.

By Theorem 2 the native and boundary supports of the edits are disjoint, so their COMPLETE signed inventory changes add. The hybrid local profiles are

    P={1:2231,2:456,3:498,4:100,5:157,6:9,7:6},
    T={1:22,2:7,3:4,4:107,5:10,7:9,8:18,9:385}.

These lists include every new accumulated query, every changed block transition, all eight changed helper boundaries and all old target debits. They contain 3457 paid calls and 562 helper targets per local instance. Paid native rank mass remains 5918. No owned buffer is productive.

The unchanged complete physical p16/a7 caller uses 18 forward local instances, all 15 thin-query shears and all 3120 whole idle jobs. Its productive-field count remains 13444 and its paid-call count is 66906. Rank-mass surplus remains 760. Main interfaces, the two physical path lengths, idles and target matchers are unchanged.

Relative to PR 5802, the hybrid's full signed-moment gain is exactly

    18*(-4H1+4H5-2H8),

where H_r=r^(1-C). Its sign at a requested exponent and all higher-moment/ordinary guards must be proved from the same hybrid lists; the κ values of the two parent PRs are not added. The separate funding argument uses this exact change.

## 7 Owned storage and ordinary costs

The hybrid retains 28 owned labels, 30 owned lifetimes and peak 13 simultaneous live owned fields from PR 5802. All public labels remain the same 770 independent inputs. The two block edits change no lifetime or COPY event; their extra operations are already the supplied native block changes. The sum acquisition and its three real source-version buffers are charged once.

Every native conversion, scalar action, basis change, copy, scrubbing pass, clear, route, header and phase normalizer receives its actual finite ordinary cost. The original two-block scalar contact coefficients and scalar primitive count are retained. Its new native transitions use the existing retained matcher service. Fresh combined coefficient-height, query-norm, stock and suspended-instance bounds are required in the complete compiler application. No invocation of the obsolete 25-owned-label check or predecessor scalar threshold proves those bounds automatically.

## Attribution and exact evidence level

PR 5802 contributes the actual three sum acquisitions; updated PR 5795 contributes the released two-block composition; PR 5786 contributes asynchronous helper hubs; PR 5774 contributes retained native copies; PR 5739/5756 and PR 5796 contribute the two scalar blocks and their bases. Preserve Ali Romman, Joel Pulikkan/GamingPuzzled, flyingviper, Cinna Davis, Pierre-Loic Doulcet/hexapode, Scratch-net, DreamingOfClouds, thu-nmrc, Chris R/Clear1nsight, David Arias, Gareth Davidson, Cao Yifan, Jacob Alan Sussman, zxv and every retained P104/native/BIT/precision/analytic notice.

The additional result here is the actual protected-projection composition theorem, its ten-fibre source table, exact sum operands and full hybrid invoice. It is an informal proof conditional on the exact retained source facts identified above and the unchanged five framework assumptions. It is not a new executed operator/native/phase/caller replay. The selected frontier is not changed by this note. New text is Apache-2.0.
