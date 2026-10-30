# Independent audit of #6129's nearest-even Walsh-stage bound

**Audit of an open PR; no new κ, no selected-frontier change.**

[PR #6129](https://github.com/CrocSwap/integer-mult-bounds/pull/6129)
(Nick Petalas, head `f496734450c346468c66818c1c35521165b0cdda`) claims that J
distinct normalized Walsh factors `H0=(1/2)[[1,1],[1,-1]]`, each followed by
nearest-even rounding to a common grid h, have sharp sup-norm error

    h a_J,   a_J = J/3 + (1-(-1/2)^J)/9,

with sharp error `h a_(J-1)` on outputs whose stored value over h is odd. It
also claims that CubeJerry's
[PR #6119](https://github.com/CrocSwap/integer-mult-bounds/pull/6119) surrogate
(head `bdfe5a10d488b5f774e906d8d4588dc8da25e7ba`) has exact global
normalized error `3h/4`, which is 3/16 at h=1/4.

**Verdict: no error found.** I checked PROOF.md step by step and reproduced
every stated number with engines that share no code with #6129 or #6119.

## Proof review (PR #6129 PROOF.md)

| Step | Status |
| --- | --- |
| R is odd and `R(s+2k)=R(s)+2k`; signs absorbed into leaves | correct. Nearest-even is symmetric at ties. Negating a subtree's leaves negates every stored value in it. Distinct axes give disjoint leaves. |
| Upper bound (3): even `u+v` is exact with equal child parities; odd `u+v` gives an even root, local error 1/2 and mixed parities | correct. `b_j <= max(a,b)` needs `b_(j-1) <= a_(j-1)`. The `d_j` induction supplies it without circularity. |
| `d_j=(1-d_(j-1))/2`, `1/4<=d_j<=1/2` | correct. The second line of (3) dominates the exact branch because `d_(j-1)<=1`. |
| Witnesses (4): E_j children are (0, a), (-1, b), and the root `R(-1/2)=0` adds +1/2. O_j children are (0, a), (2, a), and the root 1 is exact | correct; all signed errors are positive. |
| Closed form and `a_J<J/2` for J>=2, ratio → 2/3 | correct |
| Period `2^(J+1)` per input | correct. After k<=J stages the exact displacement is divisible by `2^(J+1-k)`, which is even. |
| #6119 application | correct. `a=4` is an integer, so upper and inverse are exact on the grid. The lower inverse leaves `h(R(k/2)-k/2)` in {0, ±h/2}, and that rounds to 0 under ties-to-even. |

Two clarifications for readers. They are not errors.

1. The Walsh law depends on parity tie-breaking, not on ties-to-even itself.
   Ties-to-odd gives the same a_J (engine D). The #6119 application does need
   ties-to-even: under ties-to-odd, the echo temporary is left at ±h for every
   odd k, so the echo would not be the identity.
2. Nearest rounding alone does not give the saving. Floor rounding attains
   the stagewise bound J/2 at every J<=5. Ties-away-from-zero already reaches
   J/2=1 at J=2. Every rule here obeys `R(s+2t)=R(s)+2t` except ties-away.

The same integer sequence, `2^J a_J = ((3J+1)2^J-(-1)^J)/9` (0, 1, 3, 9, 23,
57, ...), is the sharp dyadic rotation switch tariff in
`research/dyadic-rotation-switch-tariff` (also Nick Petalas). Both proofs
reduce to the slope recurrence `d_j=(1-d_(j-1))/2`. This is a structural
remark only. Neither result is used here.

## Independent engines (`verify.py`, stdlib, about 50 s)

- **A. Residue-tracking tree sets.** For one output tree with sign pattern
  σ, I enumerate every leaf residue mod `2^(J+1)`. After each stage I keep
  the complete set of (stored value mod `2^(J+1-k)`, exact signed error). By
  `R(s+2t)=R(s)+2t`, the root residue mod M/2 is determined by the child
  residues mod M when M>=4. This needs only the period lemma, not #6129's
  "children can be shifted by any even amount" step. The engine covers every
  sign pattern for J<=4, the all-plus pattern for J<=7, and both output
  parities. The even-output maximum equals a_J and the odd-output maximum
  equals a_(J-1) for every J<=7 (for example, 313/128 at J=7). For J<=4, the
  (parity, |error|) set is identical across all 2^J sign patterns.
- **B. Literal network.** This is an exhaustive check of the 8-point network
  (J=3) on `[-3,0]^8` (65,536 inputs) in three stage orders, over every
  output coordinate. The maximum is exactly 9/8, and no input exceeds it.
- **C. #6119 surrogate.** I rebuilt the 12-wire surrogate (exposure, pad,
  echo m=1/2 and a=4, active H0, unpad, restore, tail H0, six rounded maps) in
  integer units of h/8. I checked it exhaustively over each spectator fiber
  modulo 8h (8,192 inputs), plus 300 random period-8h shifts. The sup is
  exactly 3h/4. #6129's original-coordinate witness (0,0,-1/4,0,-1/2,0,0,0)
  attains it. *Local-only cross-check, not in the verifier:* on 3,000 random
  grid inputs, my rebuild agrees exactly with #6119's own `program()`/`forward(rounding=True)`
  at the head above.
- **D. Controls.** Ties-to-odd gives the same law. Floor gives exactly J/2.
  Ties-away-from-zero reaches 1 at J=2. Under ties-to-odd, the echo is dirty
  on odd residues.

Engine A uses the period lemma. Its proof is short and is given above and in
#6129. The verifier only samples it, on 400 random literal J=3 networks. So
engine A is a complete check *given* that lemma, not a proof-free
exhaustion. Engine B is literal for J=3 on a box only. All-J correctness rests
on the written proof, which I found correct.

## Reproduce

```sh
python3 scripts/research_package.py --package research/nearest-even-walsh-error-audit --check-only
python3.12 scripts/research_package.py --package research/nearest-even-walsh-error-audit
```

## Not covered

This audit makes no claim about #6119's arbitrary-defect theorem or its
mutation checks. It also does not cover bit costs, range guards, reversible
history or any PR6030 child or supplier. These remain separate obligations
of #6129 and #6119.

## Open next questions

- Whether a rounded echo is clean depends on the tie rule (engine D). Which
  native rounded compilers on main rely on a ties-to-even cancellation like
  #6119's lower inverse? A first step is to grep the retained rounded
  shear/echo packages and look for `m=1/2` half-tie cancellations.
- Does the sharp law survive when a non-Walsh gate sits between two rounded
  stages (for example a grid shear)? #6129 excludes this case. A first step
  is to put one intervening shear into engine A and enumerate it.

## Credit

The theorem, proof and witnesses are Nick Petalas's (#6129). The surrogate and
the deferred-row context are CubeJerry's (#6119, with OpenAI Codex assistance)
and Vlado Vojdanovski's (PR1673), with the lineage credited in #6129. This
audit and its engines were prepared by Josie Elliston with Claude Opus 5.5
(Anthropic) assistance. Apache-2.0.
