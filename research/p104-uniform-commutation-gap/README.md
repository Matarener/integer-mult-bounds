# Uniform completion does not match a port-dependent chart

Partial certificate. No new κ. Selected κ stays `0.001672660197076918`.

This is not the adjacent completed-call pair requested by discussion #1166
comment 19034066. That request asks for one pair whose encoded exit matches
the next encoded entrance on every data and helper role, plus the intertwiner
and the replacement bill. The certificate below shows why uniform commutation
does not answer that request, and it stops before naming a pair.

## Result

Address space `(F_2)^4`, character basis of size 16. For `u` in that space,
`X_u` is diagonal with `X_u|z⟩ = (-1)^{u·z}|z⟩`, and

```text
C_u = ((1+i) I + (1-i) X_u) / 2.
```

Then `C_u|z⟩ = |z⟩` when `u·z = 0` and `i|z⟩` when `u·z = 1`. In particular
`C_0 = I`. For `u ≠ 0` the odd set has size 8, `C_u ≠ I`, and `C_u^{-1}` acts
by `-i` on that set. `X_u - X_v` differs on exactly 8 characters when `u ≠ v`.

**Uniform match.** If both banks carry the same chart `C_u`, conjugation fixes
every character-diagonal bank block, scalar or not: those entries commute. Exit chart `C_u` therefore equals entrance chart `C_u` on every
character. A uniform completed transform really does preserve that encoding.

**Port-dependent gap.** Let the exit chart on a data line be `T = C_u` for
`u ≠ 0`, and let the next entrance expect the common chart `F = C_0 = I`.
Then `F T^{-1} ≠ F`. On every odd character the transported amplitude is
`-i` times the entrance amplitude. All 15 nonzero `u` fail. One data role is
enough: this candidate does not match every data role. Helper roles are not
in the model, so their agreement is not claimed.

**Old correction.** In ordered coordinates, with `H = I`, `K = T^{-1}`, and
`L = [[D, H T], [0, I]]`, `P = [[I, 0], [K, I]]`,

```text
P L - L P = [[-H, 0], [K (D - I), H]].
```

The identity is checked on all 16 characters for `u = 1` and a non-scalar
diagonal `D`. On input `(A, 0)` the first bank moves by `-A`, which is not
zero. Reusing `P` unchanged does not intertwine `L`. The literal-slot factor
`-H K = -T^{-1}` acts by `i` on the odd character, not by `-1`. The bookkeeping
permutation `Pi` from the predecessor is not applied here.

**Published gate, arithmetic only.** With the predecessor's named inventory
`n = 104`, 72 helpers per fiber, `N = 10816`, `W = 36608` and rank 81, the
favorable scaffold gives lower mass `3009344` and capacity `2965248`, excess
`44096`. At `a = 0` the moment ratio equals that integer ratio and is already
greater than 1. Hypotheses (a)–(e) of that scaffold are not re-proved. This
arithmetic is why the session does not build the pair inside the scaffold.

## What this does not establish

No adjacent pair, owner map, helper match, dirty restoration, or replacement
bill. No chronological correction program and no supplier. The real-exponent
comparison `(r/81)^{1-a} ≥ r/81` for `0 < a < 1` is the predecessor's argument;
only the `a = 0` ratio is rechecked here. Opposite orientation, tape, routing,
and all-size transfer stay open.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3.12 -B research/p104-uniform-commutation-gap/verify.py
python3.12 -B scripts/research_package.py --package research/p104-uniform-commutation-gap
```

Expected marker:

```text
PASS_P104_UNIFORM_COMMUTATION_GAP address=F2^4 charts=16 odd_half=8 uniform_match=true port_u_nonzero_match=false ordered_defect=-H A gate_excess=44096 no_new_kappa
```

## Open next questions

1. Is there one explicit adjacent pair, with port-dependent source charts
   allowed, whose exit matches the next entrance on every data role and every
   helper role? The first step is one data line and its helper block, with
   the charts written down. Blocker: this model has no helper roles and does
   not search pairs. Uniform commutation does not supply the pair.
2. Do hypotheses (a)–(e) of the published 44,096-excess scaffold hold for one
   actual producer? The first step is to bind one local call's mass 2,576 and
   progress 2,312 to that producer. Blocker: those hypotheses were not replayed.

## Credit

The ordered encoding, the commutator, and the scaffold integers are the
two-axis gate in PR #3954 (Chris R / Clear1nsight). The request to build a
matched adjacent pair, and the warning that uniform commutation is not that
pair, are discussion #1166 comment 19034066. The chart formula is restated
and checked here; that package is not imported. Predecessor lineage named
there remains theirs, including Rohan Arun, Chafik Boukhalfa, and Adam Gall.

Prepared by unpaidmoon with substantial Cursor Grok assistance. No independent
human or formal-kernel review is claimed. Apache-2.0.
