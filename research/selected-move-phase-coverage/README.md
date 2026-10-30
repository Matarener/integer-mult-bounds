# Selected MOVE phase coverage: a corrected handoff

**Source-coverage finding with one independent finite operator check; no new κ.** The selected #5599 checker already compares both signed Pauli conjugations and the exact image of `|0>` for every distinct local MOVE pair. The latter fixes absolute phase. Its registered path covers all 3,447 MOVE occurrences (2,887 distinct ordered pairs, including 11 owned occurrences). These are inventory counts, not 3,447 newly replayed operators.

The added value is a correction to the proposed next task in [#5837](https://github.com/CrocSwap/integer-mult-bounds/pull/5837), head `764e7bd6d615d92019445bec92e2a473af021878`. Its [README](https://github.com/unpaidmoon/integer-mult-bounds/blob/764e7bd6d615d92019445bec92e2a473af021878/research/native-scalar-chart-lift/README.md) says the selected native checker “only compares width-1 signed Pauli recipes” and proposes an absolute-phase group-identity census. The existing checker includes that phase comparison. A fresh census should be justified as independent verification of existing coverage, rather than a newly missing algebraic implication. The predecessor's scalar proposition is unaffected, and its physical tape limitation is valid.

Scientific base: canonical main `de5ec2e7a6074068452f45b1a191b5c72832df4a`, priority revision 8. Selected source: #5599, `09dd0965711ca7eeb169057a420abab1c9052137`. Exact bytes are in [SOURCES.json](SOURCES.json). The four execution-chain files below are unchanged between those commits. [TASK.json](TASK.json) records the refined `uniform-transfer-audit` scope. The canonical public context is [the #5837 handoff](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19209962).

## Existing coverage, traced to its entry point

All source links below resolve in the pinned base tree; these are source-inspection findings, not a new execution of the full selected suite.

| Source | What it already does |
| --- | --- |
| [VERIFY.json](../p104-helper-subspace-splits/VERIFY.json) | Registers normal and optimized `verify.py`, including native maps. |
| [verify.py](../p104-helper-subspace-splits/verify.py), `run` and `main` | Authenticates inputs, reconstructs the split word, runs `L.replay(word)` and `L.native(word)`, then structurally compares both reconstructed WORD and RESULT to saved artifacts unless `--write` is explicit. |
| [local.py](../p104-helper-subspace-splits/local.py), `replay` | Checks every MOVE's current source chart, ownership, nesting and paid rank. |
| [local.py](../p104-helper-subspace-splits/local.py), `native` | Traverses every MOVE without a public/private exclusion; caches only repeated ordered frame pairs. Lowers `chart(a).adjoint().then(chart(b))`, checks the independent chart circuit and rank, and separately covers helper endpoints and main adapters. |
| [native_verify.py](../p104-native-channel/vendor/native_verify.py), `equal` | Requires both `tableau(actual) == tableau(expected)` and `state(actual) == state(expected)`. `state` uses exact Gaussian integer pairs and a dyadic denominator, including global phase. |
| `local.native`, wrong-phase control | Increments the first recipe's left phase modulo four and requires rejection. |

The source circuit order means “execute the old chart's adjoint, then the new chart.” For column vectors the resulting matrix is `C_b C_a^{-1}`. This note does not invert that order.

The [selected proof](../p104-helper-subspace-splits/PROOF.md) already invokes exact phases and all-width frame induction. The [maintainer review](../../docs/research/pr-intake-evidence/pr5599-completion/PROOF-REVIEW.md) explicitly records signed-Pauli and absolute-phase checks while retaining universal native implementation as an assumption. Its prior complete replay is inherited evidence; it was not rerun here.

## Why this is exact matrix equality, and what lifts

Let `U,V` be invertible operators on `n` binary axes with equal signed conjugations of every `X_j,Z_j`. Then `W = V^{-1}U` commutes with those generators. Commutation with all `Z_j` forces `W` to be diagonal in the computational basis, since different bit strings have different joint eigenvalues. Commutation with each `X_j` equates diagonal entries along every edge of the connected Boolean cube. Hence `W = cI`. Exact equality `U|0> = V|0>` forces `c=1`, because `V|0>` is nonzero. Thus `U=V`, including absolute phase.

Consequently `U^(tensor f) = V^(tensor f)` for every integer `f>=1`. The mixed-product identity also gives `(AB)^(tensor f) = A^(tensor f) B^(tensor f)`, so products and inverses lift gatewise. This elementary implication is already part of [Matarener's #5442 argument](../allwidth-caller-certificate/PROOF.md); no new theorem priority is claimed and its converse/Burnside argument is not needed here.

The premise is the declared width-`f` tensor semantics of the operators. Tensor power is not additive: a width-one linear relation among distinct operators need not lift with fixed external coefficients. Scalar ADD/SCALE coefficients remain outside tensor powers. A central phase that belongs to a native operator remains inside them. This distinction is why the phase check matters, but it does not supply a physical arbitrary-width executor.

## New bounded evidence: the actual first MOVE

Zero-based event 9589 is `["MOVE",224,3,0,false]`, from frame `[]` to `[11]`. Independently of the retained `state` and `tableau` equality routines, [verify.py](verify.py) compares all 512 basis columns of its lowered rank-one recipe with

```text
U = ((1+i) I + (1-i) X_11 Z_3)/2,
X_11 |x> = |x xor 11>,   Z_3 |x> = (-1)^(x_0+x_1) |x>.
```

Bits are numbered from zero. The canonical basis completion has columns `(11,1,2,4,16,32,64,128,256)`. Its diagonal form is `q(x)=2*x_3*(x_0+x_1) mod 4`. With `K=D_q P_G`, the frame is `K C_1 K^{-1}`. Conjugating the nontrivial branch gives `P_G X_1 P_G^{-1}=X_11` and `q(x xor 11)-q(x)=2*(x_0+x_1) mod 4`, proving the displayed formula. Bits 0, 1 and 3 are active; all six untouched bits are included in the exhaustive columns.

The independent recipe evaluator applies its two monomial records directly and adds the two Gaussian numerators over denominator two. The compiler supplies only the candidate recipe; neither its own state evaluator nor the retained interpreter decides the new equality verdict.

All 512 columns match. Incrementing `left.phase` by one changes every column to exactly `iU`; toggling `left.offset` bit zero changes every column and is separately detected. Only after that independent verdict, the retained checker is called diagnostically: the original passes; the phase mutant has the same signed tableau and fails specifically with `phase-only control: exact global phase`. At the origin:

| Address | Original numerator / 2 | Phase mutant numerator / 2 |
| --- | --- | --- |
| 0 | `1+i` | `-1+i` |
| 11 | `1-i` | `1+i` |

[RESULT.json](RESULT.json) is the generated exact receipt. All 3,447 occurrences are counted, but **only this one ordered pair is newly executed**. The general all-width consequence is the written argument, not a finite width sweep.

## Reproduce

CPython 3.12, standard library only, from the repository root:

```sh
python3 -I -W error -B research/selected-move-phase-coverage/verify.py
python3 -I -O -W error -B research/selected-move-phase-coverage/verify.py
python3 -B scripts/research_package.py --package research/selected-move-phase-coverage
python3 -B scripts/check_research_commit.py --package research/selected-move-phase-coverage --check-source-history
```

The direct verifier is read-only and works in the official Git-free export. It authenticates every live source before import and isolates import bytecode caches. Expected status is `PASS_INDEPENDENT_FIRST_MOVE_CLOSED_FORM`; normal and optimized receipts agree. [VALIDATION.md](VALIDATION.md) records actual commands/results, internal review and unrun obligations. A source-integrity pass is not a mathematical proof.

## Open next questions

The remaining useful task is physical: bind this same rank-one recipe to an actual arbitrary-width owner/tape interface. Specify the complete input vector, spectators, entry/exit layout and head positions, both monomial normalizers, the rank-one child, owned/borrowed scratch and restoration. Prove that the literal address/phase operations realize its tensor power for every permitted `f`, and attach every preparation, movement, normalization and return charge to the actual caller tariff. Start with this event and its dynamically lowered recipe; stop at the first missing head map, primitive contract or cost inequality. Another width-one group census does not fill that gap.

The current `native` function synthesizes recipes during verification and saves counts plus a recipe-payload hash; it does not emit an arbitrary-width tape program. The older [selected-monomial-tape-lift](../selected-monomial-tape-lift/README.md) and [selected-control-reservations](../selected-control-reservations/README.md) concern #5413's 145-axis caller and provide relevant record/address contracts, not automatic admission of #5599's changed caller. Exact source/layout compatibility must be proved before reuse. No implementation expansion is undertaken or reserved here.

All five selected framework assumptions remain. No full native census, selected cold replay, complete body/controller proof, cost improvement, rounded multiplier, Lean check or physical implementation is claimed. The shared compiler supplies the tested recipe; the closed-form oracle is independent of both state engines but shares the documented monomial grammar. The general checker implementation is not formally verified.

## Credit and review status

Prepared for **DLamdata**, with substantial **OpenAI Codex assistance**, including two native agents for independent mathematical checking and skeptical source review. This is internal AI review, not independent human or proof-kernel review. Apache-2.0.

Credit unpaidmoon for #5837 and the precise follow-up question; Ali Romman for #5599 and the source verification path; Pierre-Loic Doulcet / hexapode for #5565; Mark / Matarener for #5442 and the algebraic/physical distinction; Chris R / Clear1nsight for independent caller/native verification; and Dugongue, icekylinx, David Arias, Cinna Davis, Gareth Davidson, Cao Yifan, zxv, Jacob Alan Sussman and the retained Clifford/controller/compiler lineage. Frozen predecessor files and the selected frontier are unchanged.
