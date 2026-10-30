# A bit-free complex supplier for the selected word is not profitable

**Scoped negative result. No new κ; the selected record is unchanged.**

`research/kappa01-outer-repair` shows that the bit side could be built from
three complex calls (`SWAP = (H D)^3`), so κ would depend on the complex side
alone, provided the complex supplier is itself **bit-free**. The open task listed
there is "a strict augmented moment with all native children included". This
package prices that augmented moment on the selected local word in several ways.
Each way stays negative, and it finds where the obstruction comes from.

## Where the complex side uses the bit side

In `upstream/build/sections/05-layers.tex` the only bit-side call is the
chunk swap (`lem:chunk-swap`, cost `O(V L^τ)`). It sits inside the packed
selected-bit row additions that implement the basis change `P_M` of every
edge (`P_M ∏ C_{e_j} P_M^{-1}`). The cyclic shifts, single-bit operations,
scalar gates and role splitting are linear time. The recurrence
`F(e) ≤ (s/W)F(e/m) + O((eK)^τ)` is what ties the complex exponent to τ.

## Results (`verify.py`, about 40 s, standard library)

The savings below solve `Σ n_r (r/73)^(1−a) = 896/9` per call. The base is the selected
local profile `{1:2412, 2:418, 3:432, 4:142, 5:82, 8:8}` plus all 1,646 idle units
in rank-51 children, which is the optimistic relaxation of
[complex-local-word-ceiling](../complex-local-word-ceiling/README.md) (it reproduces
its ceiling a = 0.00169005). At a = 0 the base leaves room for only
**about 35 rank-1 children per call**.

| Variant (interior segment `A`..`exit_adapters`) | backward | forward |
|---|---:|---:|
| Control: ADAPTER-FUSION *relative* compiler, total rank mass | 232,198 | 239,648 |
| Saving | −1.045 | −1.056 |
| **Lazy directions** (align only the child's Walsh directions, defer the rest), mass | **114,114** | **127,308** |
| Saving | −0.900 | −0.930 |
| Layout changes forced by children alone (exact per register) | 0 | 8 |
| **Layout changes forced by ADD gates, any schedule** (≥ ⌈conflicts/2⌉) | **≥ 105** | **≥ 106** |
| Greedy shared-layout schedule (upper bound) | 2,921 | 3,177 |
| Saving even at the lower bound, 2 rank units per change | −0.0081 | −0.0082 |

*Lazy directions.* A child `F_r P_M` equals `P_M ∏ C_{M⁻¹e_j}`. This identity is checked
on the native Clifford tableau of `involutive-walsh-lift/native.py` for 200 random
cases. So a child only needs its r directions to be distinct coordinates of the
stored layout. The other parts of the map and all translations stay pending. The cost of
entering children drops five-fold (about 125k → 25k). ADD alignment then dominates
(54k–67k), followed by returning layouts (30k).

*Lower bound.* At an ADD, take the children on both registers since their previous
gate and until their next one. If their directions (transported to the gate's common
frame) are not linearly independent, one layout change must fall in those four
windows. A change lies in one window, and a window is adjacent to at most two gates.
Even the bound is about six times the whole budget. It also matches a simple count:
one layout holds at most 8 mutually orthogonal port lines out of 112, so about 104
data wires must change layout around each centre.

**Skew kernels (no address map at all).** In the paper's form an edge is
`∏_{v ∈ ONB(residual)} C_v`. Without `P_M`, data stay canonical, ADDs are free,
and a kernel along v of weight w only has to flip w−1 extra address bits of the
partner stream (split/merge, linear time). Using minimum-weight residual bases,
the forward word has these direction weights:
`{1:1146, 2:1514, 3:1549, 4:985, 5:49, 6:174, 7:169}` (mean 2.73).

| Flip procedure | saving |
|---|---:|
| one pass per bit | −0.262 |
| 8-tape multiway split (3 bits per pass) | −0.165 |
| 256-tape multiway split, **one recursion level only** | −0.155 |

Only 512 of the 3,494 children have an orthonormal residual basis. The other
2,982 (degenerate or alternating residuals) use a minimum-weight basis without
orthonormality, which is optimistic. Moreover, masks multiply down the recursion
(Kronecker weights). So the per-level multiplier tends to the mean weight for any fixed
number of tapes. A positive saving needs a mean multiplier ≤ about 1.005, i.e. fewer than
0.5% skew directions.

**Pass-model lemmas** (checked exhaustively or on random samples):
1. Flipping a weight-W mask has longest decreasing subsequence exactly 2^W.
2. That length is submultiplicative under composition, and a split-merge pass with T tapes realises only
   LDS ≤ T. Hence at least W/log₂T passes.
3. Prefix (block) reversals form a basis of the masks, so their minimum number equals the run
   boundaries (2 per isolated bit).
4. Any bit-reordering layout keeps the LDS.
5. Mask weights multiply under Kronecker products.
6. A controlled block reversal is one pass and equals the shear `x[0..t] ^= f(x_high)·ones`.
   It has a single control per pass, so aligning f columns costs ≥ f passes, a term linear in the width.

## What this does and does not show

Within the subspace-label networks of sections 03/05 and without transposition, a
complex supplier cannot be both bit-free and profitable. The rank saving needs many
non-orthogonal lines in a small label space. These lines cannot share one layout, so
the cost appears as layout changes (2 rank units each, against a margin below 1 unit
per data pair) or as growing skew masks. The one escape is a cheap address
permutation, and that is the bit supplier: XOR-by-mask reduces to transposition plus
one reversal. So the pass-model bound is not an unconditional multitape bound, and
it cannot be one without new lower bounds for transposition and, through section 10, for multiplication.
The circular route "bit side from three complex calls" therefore does not close for this
word and family. Everything is restricted to the interior segment that ADAPTER-FUSION
used; external adapters, helper jobs and the nine-stage route would only add cost.

## Reproduce

```sh
python3 scripts/research_package.py --package research/bit-free-complex-supplier --check-only
python3.12 scripts/research_package.py --package research/bit-free-complex-supplier
```

The verifier prints `PASS_BIT_FREE_COMPLEX_SUPPLIER` and rewrites `RESULT.json`.
It needs full Git history, because the canonical word is read from the pinned selected-replay
archive through `involutive-walsh-lift/sources.py`.

## Open next questions

The structured list is in [TASK.json](TASK.json).
1. Is there a complex network outside the subspace-label family whose saving does not
   need many non-orthogonal lines at one gate? None is known here.
2. What is the exact minimum number of layout changes for this word (105 … ~3,000)? A CP-SAT
   set cover over gate windows would settle it. It only refines the gap.
3. Is there an unconditional lower bound for XOR-by-mask permutations on multitape machines?
   This is blocked by open lower-bound problems.

## Credit

Prepared by Mark (Matarener) with Claude (Anthropic) assistance. The Walsh identities, the
adapter compiler and its control numbers come from `research/kappa01-outer-repair`. The native
retarget word and Clifford tooling come from `research/involutive-walsh-lift`. The coverage law
and ceiling model come from `research/complex-local-word-ceiling`. The predecessor attributions in those packages
are retained. New work is Apache-2.0. No independent human review.
