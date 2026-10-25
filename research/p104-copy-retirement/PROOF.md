# Literal private-copy lifetimes and a paid replacement

All indices below are zero-based in the pinned 4,058-event PR1972 word retained
by PR1991. This is a fixed-word ownership and changed-local-route result.
It is not a universal lower bound on P104 copies, encoders or suppliers.

## The actual eight lifetimes

Let q_j be the exact normalized row in Q_j when it is copied. Sparse rational
induction from all 280 independent inputs gives

    q_j = h_Qj + sum_i a_ji x_i,

with coefficient 1 on h_Qj, coefficient 0 on all other dirty inputs, and the
source coefficients recorded in RESULT.json. No zero-input assumption is used.
The original source gather produces these rows; they are not an assumed query.

| Query | C initialization | Copy | Rank-seven descent | Last C read | C erase | Delivery helpers |
|---|---:|---:|---:|---:|---:|---|
| Q0 | 2461 | 2462 | 2463 | 2468 | 2469 | D0–D4 |
| Q1 | 2470 | 2471 | 2472 | 2475 | 2476 | D5–D7 |
| Q2 | 2477 | 2478 | 2479 | 2483 | 2484 | D8–D11 |
| Q3 | 2485 | 2486 | 2487 | 2491 | 2492 | D12–D15 |
| Q4 | 2493 | 2494 | 2495 | 2499 | 2500 | D16–D19 |
| Q5 | 2501 | 2502 | 2503 | 2506 | 2507 | D20–D22 |
| Q6 | 2508 | 2509 | 2510 | 2514 | 2515 | D23–D26 |
| Q7 | 2516 | 2517 | 2518 | 2523 | 2524 | D27–D31 |

Each private C starts at zero in the same eight-dimensional chart W_j as Q_j.
Copying sets its normalized row to q_j. The literal transport takes C to a
one-dimensional chart L_j contained in W_j; every reader is an addition
D_k += C in that L_j chart. The private row remains q_j until erase. Since its
h_Qj coefficient is 1, it is not zero. The inherited owned-private erase
semantics permit discarding C; this does not permit discarding a public dirty
Q_j or D_k. Only one C is live at a time, and none is live after event 2524.
There is therefore no surviving C role at the completed #3882 boundary whose
future lifetime can be silently credited as retirement of the paid descent.

The 32 D helpers are actual consumers, not hypothetical available banks.
RESULT.json records their first downstream reads and their cleanup events
3579, 3581, ..., 3641. The cleanup subtracts the corresponding q_j after both
roles reach FULL. Q_j itself remains unchanged from copying until its FULL
transport at 3570+j, and is restored by the final source cleanup.

## Removing delivery is observable downstream

Remove all eight private intervals while retaining every public event.
At each D_k in the j-th group, the missing addition leaves normalized defect
−q_j. The later public program is linear. The exact complete replay shows:

* X, Q and G final rows are unchanged;
* all 32 D returns have defect −q_j;
* the target defect and the complete public defect each have rational rank 8.

The eight independent h_Qj columns already attain rank 8. In particular, take
one h_Qj arbitrary and every other logical input zero. This is an explicit
permitted dirty input, not a probability or generic-rank argument.

Continue both original and mutilated words through the actual pinned #3882
schedule. That schedule acts only on X/Y and is invertible in normalized rows.
Our new evaluator uses its unchanged geometry/program builders but not its
arithmetic evaluator. The 104 physical sum slots (Y_J, X_N) still have defect
rank 8. All 32 D defects survive unchanged because the tail never touches D.
Thus correct sums and dirty returns cannot be obtained by simply deleting the
copies or their 32 uses. This is not a proof against changing the producer,
consumer, other delivery operations or output contract.

## A concrete copy-free local replacement

Write T_j = Gamma_Lj Gamma_Wj^{-1}. Replace each private interval by:

1. apply T_j directly to Q_j;
2. perform the same D_k += Q_j additions in L_j;
3. apply T_j^{-1} to Q_j.

At the entrance let the physical query be Gamma_Wj q_j and each D value be
Gamma_Lj d_k. The exact endpoint is

    Q_j -> Gamma_Wj q_j,
    D_k -> Gamma_Lj (d_k + q_j).

Every other role is untouched. This equals the original private-copy block on
all arbitrary inputs. Eight block substitutions consequently preserve the full
280-row channel endpoint and the actual #3882 continuation. There are no
private zero/copy/erase events, and no dirty role is erased. The maximum local
register count drops from 281 to 280; this is a local workspace observation,
not a global width or recursive saving.

The source certificate supplies the forward native recipes. RETURN-RECIPES.json
contains eight newly lowered reverse recipes. native.py independently checks
the physical label mapping at each literal event, exact signed Clifford action,
global phase, both rank-seven child charges, 8,192 Gaussian columns (512 in each
direction for each block), and the identity T_j^{-1} T_j. It rejects a changed
global phase. It reuses the credited exact compiler/interpreter and does not
repeat the complete inherited channel's native proof.

## The price and its scope

The original eight private descents cost 8*7 = 56 rank mass. The replacement
uses eight descents and eight returns, costing 112. The query-freeing saving
is eight zero operations, eight copies, eight private erases and one peak
local array; the positive recursive-child bill increases by 56.

For the restricted direct-Q route, this rank cost is sharp under the retained
nested transport tariff. A path from dimension 8 through dimension 1 and back
to dimension 8 has sum of absolute dimension jumps at least 7+7. The two direct
transports attain that bound. If restoration is delayed until the existing
FULL consumer, the 8 -> 1 -> 9 path costs at least 15, versus the original
private drop 7 plus Q's existing 8 -> 9 lift 1, again seven extra. This bound
fixes the same delivery chart, same Q owner and same later public consumers.
It excludes replacement encodings, coupled roles, altered production or new
non-nested/native primitives.

| Complete local bill | Original channel | Copy-free replacement |
|---|---:|---:|
| Native profile, ranks 1 through 8 | 1074,58,86,104,48,24,8,8 | 1074,58,86,104,48,24,16,8 |
| Rank mass | 2368 | 2424 |
| Scalar array additions | 2624 | 2624 |
| Native transport occurrences | 1410 | 1418 |
| zero / copy / erase | 8 / 8 / 8 | 0 / 0 / 0 |
| Total events | 4058 | 4042 |
| With the unchanged #3882 208-H1 tail | 2576 | 2632 |

The positive-child counts include all eight returns. Their actual Gaussian
monomial wrappers are retained in the recipe file, not treated as positive
recursive children. We do not claim a runtime saving: wrapper execution,
precision, signed-floor behavior, memory/routing/control and all-size admission
remain separate obligations. Unknown physical costs are not assigned zero.

As a conditional substitution into #3954's stated 208-call, m=81, W=36608
scaffold and the same persistent-progress allowance, its already failing
M_0 numerator excess grows from 44096 to 55744. Granting all 208 correction
rank units per local call for free would leave 832 excess for the original
COPY56 channel and 12480 for this replacement. These are scoped favorable
relaxations, not an actual two-axis construction or a general P104 barrier.
For 0 <= a < 1, (r/81)^(1-a) >= r/81, so failure at zero also fails every such
moment under those same hypotheses. The replacement does not justify another
dependent construction round. A new route must eliminate real work with a
changed producer/consumer or coverage contract and price every obligation.
