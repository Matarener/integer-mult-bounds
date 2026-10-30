# Proof: exact κ region of the selected outer ledger

## Setting

The selected #5599 result (`research/p104-helper-subspace-splits/pricing.py`)
calls `ledger(params)` from
`research/pr4359-p7-padding/dependencies/compiler-refill/endpoint.py`. That
function recomputes zxv's PR4359 outer parameter ledger: 54 strict checks and
3 functional checks. `pricing.py` adds a fourth functional check,
`β(1-atom)` with `atom=1/250`. Call the 58 expressions *the ledger*; it is
satisfied when every expression is strictly positive.

Inputs: κ, the complex uniform saving U, and the admitted BIT saving B.
Free parameters: b, a, q, ε, β, r0, stop, layout. (`tested_saving` and `d`
are passed through but no check reads them.) Write OLD for the ledger constant
`OLD_BASELINE = 0.001730970419199163702738` and M = min(U, B, 1/32).

**Theorem.** Some choice of the free parameters satisfies the ledger if and
only if OLD < κ < M.

## Necessity

Nine checks give the chain. Each name is the ledger's own key; `verify.py`
checks every closed form against the loaded function on random exact inputs.

| Check | Expression > 0 |
|---|---|
| `improvement_over_user_baseline` | κ − OLD |
| `main_transform_above_kappa` | εq − κ |
| `epsilon_below_one` | 1 − ε |
| `q_positive` | q |
| `q_below_effective` | a − q |
| `actual_bit_above_effective` | B − a |
| `complex_above_effective` | b − a |
| `new_complex_uniform_saving_above_b` | U − b |
| `complex_below_one_over_32` | 1/32 − b |

From q > 0 and ε < 1, εq < q, so κ < εq < q < a. Then a < B, and
a < b < min(U, 1/32). Hence κ < min(U, B, 1/32), and κ > OLD directly. ∎

## Sufficiency

Let OLD < κ < M and d = (M − κ)/7 > 0. Take PR4359's own `family` shape:

    q = κ+3d, a = κ+4d, b = κ+5d,
    ε = 1−d, β = 1−3d, r0 = d/10, stop = layout = d.

Then 0 < κ < q < a < b < M ≤ min(U, B, 1/32), and d < 1/224. Write
σ = 1−b, τ = 1−a, λ = 1−(q+a)/2, c = 3/32, ξ = ε(1+q) − c + layout,
key = β+1−ε. Since σ−τ = a−b < 0, internal = τ; leaf = σ + d·b.

- Ordering rows: B−a, b−a, U−b, 1/32−b, a−q, b−q and q are positive by
  construction. `leaf_saving_above_effective` = (1−d)b − a = d − d(κ+5d) > 0
  because κ+5d < 1. `q_below_leaf` = (1−d)b − q exceeds it.
- λ rows: λ−τ = (a−q)/2, λ−σ = b−(q+a)/2, λ−internal = (a−q)/2,
  1−q−λ = (a−q)/2, 1−internal−q = a−q, 1−q−leaf = (1−d)b − q. All positive.
- ε, β rows: 1−ε = d, ε−β = 2d, 1−β = 3d, 1−ε−r0 = 9d/10,
  1−key = 2d, 1−β−2(1−ε) = d, ε−a > 0, β > 0, 80−β > 0, r0, stop,
  1−stop and layout are positive.
- ξ rows: ξ − 1/2 = ε(1+q) + d − 19/32 > 0 since ε > 1 − 1/224.
  ε − ξ = 3/32 − εq − d > 0 since q < 1/32 and d < 1/224. 2 − ξ > 0.
  3 − 2ξ − β − r0 > 0 and 3 − 2ξ − β > 0 since ξ < ε < 1 and β+r0 < 1.
- Main row: εq − κ = (1−d)(κ+3d) − κ = d(3 − κ − 3d) > 0.
- Other margins above κ: a − κ = 4d; fused = 1−ε+qβ = εq + d(1−2q) > εq;
  group BIT router = 1−ε+aβ = a + d(1−3a) > a; group scans = 1−ε+β ≈ 1;
  boundary matrix = c+ξ−ε = εq + d > εq; sparse union = εq + d + 13/32;
  polynomial = ε; microbox = 79−ε−β. Each exceeds κ < 1/32.
  `gaussian_above_main` = d(1−2q) > 0.
- Constant rows: 2^45 − 7^16, 2, 5 and 7/2 are positive.
- Functional rows: 1−β, β(1−3/1000), 79−ε−β and β(1−1/250) are positive. ∎

## Consequences

1. The 58 outer checks lose only strict slack: the supremum of admissible κ
   is exactly min(U, B, 1/32), and it is never attained.
2. At the selected values U = 21703153/7000000000 and B = 17/5000, the
   supremum is U. The selected κ = 62009/20000000 sits 3/7000000000 below it.
3. At the selected κ, the ledger accepts any admitted BIT saving B > κ.
   The admitted .0034 has 5991/20000000 of headroom. The PR4359 negative
   control B = .0027 fails only because .0027 < κ.
4. For any target κ > .01, the ledger requires exactly U > κ and B > κ.
   It rules out κ ≥ 1/32 for every pair of suppliers.

## Scope

This is a scoped proof about the ledger's parameter arithmetic. It does not
prove the outer theorems the ledger encodes, the five inherited framework
assumptions, native or compiler costs, or any supplier admission. It changes
no κ and no selected frontier.
