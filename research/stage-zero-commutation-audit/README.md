# Actual stage-zero Gaussian commutation

**Scoped written proof and exact source-bound check; no new kappa.** This answers
open question 1 of Mark / Matarener's [PR #4457](https://github.com/CrocSwap/integer-mult-bounds/pull/4457)
at `dd40f88a4d45a0ae2487eb24f935516f749cefef`: the source-specified complex
caller satisfies `[D0,Q]=0`, including its actual port phases. The argument
does not require the port direction to be a standard coordinate axis.

The check binds all **112 ports** to native labels and initial caller maps.
It reconstructs the rank-eight normalization **with its nonzero translation
at every port**. Omitting that translation changes the operator; retaining
it preserves commutation. The native implementation and whole-call adapter
contract remain premises. This does not replay the complete 632-field word,
admit a supplier, or change the selected result.

## Operator proof

For `a` in `F_2^9`, let `T_a e_x = e_(x xor a)` and define

    C_a = ((1+i) I + (1-i) T_a) / 2.

These are the literal line-column coefficients in the pinned
`native_common.py`, not a claim about arbitrary canonical-frame Cliffords.
Its Fourier character at `xi` is `i^(a dot xi mod 2)`.
Since `T_a T_b = T_(a xor b) = T_b T_a`, all `C_a`, inverses and translations
commute. In particular,

    C_a^-1 = ((1-i) I + (1+i) T_a) / 2 = T_a C_a.

For the actual port normal `q`, set `Q=C_q` and
`F9=product_(j=0..8) C_(2^j)`. The caller's `stage_frame` definition is

    D0 = F9 Q^-1,
    D0 Q = Q D0 = F9.

Every noninitial multiplier is a product on fresh axes; thin stages substitute
the identity. These and the retained idle products commute with the same
port's `Q` and `D0`. Different ports may have different `q`: the controller's
pair operations and scalar boundaries act separately on each port. This
justifies the per-port substitution into the commuting Laurent identity,
without allowing arbitrary replacements of `F9` or port-mixing gates.

Complex conjugation preserves the identity. For every positive column
multiplicity `f`, tensor-product composition gives

    D0^tensor(f) Q^tensor(f) = (D0 Q)^tensor(f)
      = (Q D0)^tensor(f) = Q^tensor(f) D0^tensor(f).

Spectator identities also preserve it. This tensors **completed operators**;
it never distributes a tensor power over a sum. It does not prove that the
inherited native implementation realizes those operators at every multiplicity.

## Actual caller binding

Base: canonical main `2a13eb1827784206202db90e5dc8327cf8a250db`, priority
revision 7, selected conditional kappa `23/10000`. [SOURCES.json](SOURCES.json)
pins every main input by Git blob and SHA256. The verifier executes no
predecessor Python code; those source pins identify the audited definitions
and trigger replay if the contract changes.

1. `DATA-PHASES.json` and the THREE-base canonical word agree on the 112
   ordered port normals, X input lines, identity Y entrances, full X exits,
   and complementary eight-spaces at Y exits. The normals have Hamming
   weights **3 (77 ports)** and **7 (35 ports)**.
2. `p3_native_cover.py::contacts` specifies initial references `(Q,I)` and
   completed references `(F9,F9 Q^-1)`. Both diagonal reference ratios are
   therefore `D0`. The 112 stage-zero entries in `P3-NATIVE-COVER.json.gz`
   contain **448 identity coordinate maps**, with zero affine shift and
   global phase. Every map and inverse is checked, fixing a common coordinate
   system. This is a check of the declared caller records; their full native
   realization is retained as a separate premise.
3. `complex_controller_factor.py::serialize_case` states `D0=F9 Q^-1`.
   `native_common.py` and `frame_exchange.py` identify the reference operators
   as commuting `C_a` products, keeping phase corrections separate from
   abstract frame labels.
4. The #4440 controller (compressed here, preserving its exact original bytes) at
   `40e22a83ed660d3d6074c4f2dbf14bfb621eee51` starts with
   `LOCAL(0,0,forward)`, then stages 1 through 34 exactly once: 19 full calls
   and 16 query shears. Its
   [proof, sections 1–2](https://github.com/1337isnot1337/integer-mult-bounds/blob/40e22a83ed660d3d6074c4f2dbf14bfb621eee51/research/query-thinned-controllers/PROOF.md)
   retains the initial native call unchanged. This check binds the emitted
   caller and retains that local raw-map implementation premise.

## The required translation

For the recorded orthonormal complement `B=(b_1,...,b_8)` perpendicular to
`q`, set `G_B=product C_(b_j)`. The first retained idle is `D0 D1`; its last
eight axes are exactly the fresh standard axes of `D1`. Removing them leaves

    D0 = T_t G_B,
    F9 = T_t Q G_B.

Here `t` is the source's `translation_after`, nonzero in **all 112 cases**:
weight 4 in 77 cases and weight 8 in 35. Thus `F9=Q G_B` without the recorded
translation would be false in these coordinates. The translation is an
existing fixed monomial operation, not a new free recursive job. It commutes
with `Q`; no cost improvement is claimed.

Port 0 gives a concrete witness:

    q = 11; B = [13,14,7,16,32,64,128,256]; t = 15.

On input `e_0`, output 0 of `D0-G_B` is exactly **-1/16**. Independently of
the kernel calculation, all 512 Fourier characters per port verify

    |xi| - (q dot xi mod 2)
      = sum_j (b_j dot xi mod 2) + 2(t dot xi mod 2)  (mod 4).

This includes the absolute phase at zero. A separate Gaussian-dyadic
convolution calculation, using integer pairs and powers of two only, gives
the same operator. Each `D0` kernel has 256 nonzero coefficients of squared
modulus `1/256`. Kernel equality proves equality on **every** address input:
all other basis columns are translates of the zero-input column.

## Evidence and reproduction

Python 3.12, standard library only:

```sh
python -B scripts/research_package.py --package research/stage-zero-commutation-audit --check-only
python -B scripts/research_package.py --package research/stage-zero-commutation-audit
python -I -O -B research/stage-zero-commutation-audit/verify.py
python -B research/stage-zero-commutation-audit/check_export.py
```

[RESULT.json](RESULT.json) is deterministic; normal replay compares it and
`--write` is authoring only. Checks cover 114,688 commutator coefficients in
both conjugate orientations, 57,344 Fourier characters, the 448 initial maps
and the retained p17 initial call.

Controls reject all 112 omitted translations, 112 substitutions of `Q` for
`Q^-1`, and 112 deliberately noncommuting phase insertions. Two additional
controls reject a wrong port normal and an altered initial map. At port 0,
putting `Z_1` before `F9` yields commutator coefficient `(1+i)/16` on input
`e_0`, output 0. This exposes the boundary of the convolution argument.

Environment and verification status are in [TASK.json](TASK.json). The selected
baseline orientation command was attempted but stopped on an omitted selected
claim file in this sparse checkout. No full selected cold replay, BIT caller,
outer ledger, rounded implementation, resource-cost audit, formal proof-kernel
check or independent human review is claimed.

The registered replay also creates a disposable export containing only this
package and its declared inputs. It runs with `-I -O -B`, compares the exact
receipt, and rejects changed source bytes and a changed expected receipt.
No Git checkout, network request or predecessor module import is needed in
that exported verifier.

## Overlap and credit

Canonical thread: [Discussion #4461](https://github.com/CrocSwap/integer-mult-bounds/discussions/4461).
The initial refresh covered 314 open PRs, 3,312 Discussion records and all
5,731 local README/TASK notes. #4457 already covered the transport audit first
considered; this follows its explicit open question 1 instead. #4455's
invoice/moment checks and #4448's native tariff audit remain complementary.

Credit to **Mark / Matarener** for #4457's commutation question and adversarial
example; **zxv** for the physical caller, phase utilities, controller and
#4359 construction; **Cinna Davis / 1337isnot1337** for #4440's query-thinned
controller and #4441/#4447 successors; **Jacob Alan Sussman** for the
mixed-target compiler. Phase conventions retain the QQ16/native lineage and
**ywz65**'s `qq16-current-frame-consumer/native_support.py`, as credited by
the source. Retained controller data is Apache-2.0 with this predecessor
attribution. No priority claim is made for commuting translations.

Prepared for **mihir-s-05** with substantial **OpenAI Codex assistance**;
no subagents. New work is Apache-2.0.

## Open next questions

The named commutation implication is closed for these source-specified
operators. The remaining separate question is whether each inherited native
invocation and whole-call adapter realizes the raw maps at every column
multiplicity. Start with a pinned audit of one complete invocation, keeping
phase, spectators and return conditions. That requires a separately scoped
physical replay; neither this algebra nor #4457's finite sampled lifts
substitutes for it. [TASK.json](TASK.json) records the same boundary.
