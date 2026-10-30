# Proof notes for the PR5827 / PR5907 audit

All statements concern the fixed P104 local words on canonical main `19fdb086ea96af9a9f87936a2b888e10af4ed810`:
`research/p104-unread-path-resynthesis/inputs/pr5811-WORD.json.gz` (PR5811),
`research/p104-unread-path-resynthesis/WORD.json.gz` (PR5827) and
`research/p104-helper468-rung-removal/WORD.json.gz` (PR5907), with the complete invoices in each package's `RESULT.json`.

## Layer 0: sources

PR5907 pins a tar archive of the PR5827 package and runs its chain from there. Every archive member is compared
with the file at the same path on canonical main and must be equal byte for byte, so the PR5907 chain runs the
canonical PR5827 code. PR5907's own `construct.py` then regenerates its word from the pinned PR5827 word and
`EDIT.json.gz`. The decompressed payload must equal the shipped word. The two gzip containers may differ only in
header byte 9 (the OS code), and that byte is reported. That byte is why PR5907's own byte-for-byte check fails
on Linux.

## Layer 1: replay and deltas

`replay()` imports nothing from the packages. Frames are bases of subspaces of F2^9, and their spans are built as
sets. For every event it checks:

- MOVE: the register is in the source frame and its ownership flag is correct. The target span strictly contains
  the source span (public) or is strictly contained in it (owned). The paid rank is the dimension gap.
- ADD, COPY, SCALE: the coefficient is a nonzero dyadic rational, and the destination and source registers are in
  the event's frame, so the scalar operation runs in a common chart. COPY writes only into a cleared owned field.
- INIT and CLEAR: owned lifetimes, erasure in the declared frame.

At the end every public register is in its final frame and no owned field is live. The 770 + 29 rational rows must
equal the identity on public registers, plus X added into Y = X + 112 for the 104 live ports. Owned rows must be
zero. For each helper (a public register that is not a main port) the initial span must lie strictly inside the
final span. Its credited target rank is the dimension gap.

PR5811 → PR5827: the programs agree outside one window of seven events starting at index 13815. The paid multisets
differ by −H1 − H4 + H5. Boundaries, frames, ports and the helper profile are equal. The identity of the window is
implied by the full endpoint check on both words.

PR5827 → PR5907: frames, live ports and port frames are equal. The boundary charts differ in exactly five entries:
initial 557 (3→105) and 765 (245→263), final 455 (105→925), 557 (105→925) and 765 (127→742). The helper ranks of
455, 557 and 765 become 7, 6 and 3 (from 1 each). The paid delta is −4H1 + H4 + H6 + H7 and the target delta is
−3H1 + H3 + H6 + H7. The paid and target rank masses both rise by 13, so the surplus is unchanged. Per local call
the moment margin changes by H1 + H3 − H4. That is positive for 0 < t < 1, because 4^t < 1 + 3^t.

## Layer 2: invoice

The invoice is rebuilt from `research/p104-productive-controller/CONTROLLER.json`. Each LOCAL event adds the local
paid and helper profiles. Each QUERY_SHEAR adds 104·H1. Each IDLE over L blocks adds 208·H_{8L}. Each diagonal term
adds 104·H_{1+8s}. The same totals are then built from the closed formula

    P = 18 P_local + 1560 H1 + 208 Σ_{L∈{7,8}} Σ_{j=1..L} H_{8(j+1)}
    T = 18 T_local + 208 H145 + 208 Σ_{L∈{7,8}} Σ_{j=1..L} H_{1+8(j+1)}

The two must agree with each other and with the author's `complete_cost`.

## Layer 3: native maps

For a MOVE from frame A to frame B the native operator is chart(A)⁻¹ chart(B). The canonical compiler
`clifford_exact.lower_child` lowers it to a recipe. The literal definition is `adjoint(frame(A)) + frame(B)`
from `native_verify.py`. PR5548's dense interpreter evaluates both circuits exactly, with Gaussian-dyadic
integers, on each of the 512 basis inputs. We require

1. exact equality of every column, including absolute phase;
2. squared norm one for every column;
3. exactly 2^rank nonzero entries in every column, where rank is the paid rank of that transition.

The same check runs for each distinct helper pair (chart(initial)⁻¹ chart(final), credited rank
dim final − dim initial). The 208 intrinsic main adapters must lower at rank zero. The inventory is the union over
PR5827 and PR5907 of 3,163 operators. Seven of them are new in PR5907: MOVE 3→712, 3→925, 105→925, 712→127 and
helper pairs 3→925, 105→925, 263→742. One is used only by PR5827: MOVE 593→859. A phase-only fault (same signed
tableau) and a flipped child sign on map 3→712 are both rejected.

## Layer 4: funding

The moment margin at κ is Σ_targets n·r^(1−κ) − Σ_paid n·r^(1−κ). Each power is exp((1−κ)·ln r), computed with 80
significant digits and widened by a relative 10⁻⁷⁰. Bisection on the grid 10⁻¹⁴ gives the largest grid point with
a certified positive margin and the next one with a certified negative margin. These must equal each author's
`raw_root_interval`.

At the tested saving s the decimal engine also checks the three charged tail ratios, with cutoff 16, floor 17 and
offset 1/7:
α = M_P(1−s)/M_T(1−s) < 1 − 10⁻¹², γ = M_P(1−s+1/7)/(16^{1/7} M_T(1−s)) < 125/128 and
δ = 17·|T|/(16^s M_T(1−s)) < 125/128.

The derivative of the margin in κ is −Σ_T n ln r · r^{1−κ} + Σ_P n ln r · r^{1−κ}. It is bounded above on
[0, .0034] by taking target terms at exponent 1 − .0034 and paid terms at exponent 1. The bound is negative, so
each crossing is unique there. The engine shares no code with the authors' two moment engines.

## Not covered

The uniform compiler for all recursion levels, owned erasure, precision and tape costs and analytic recovery are
inherited premises. The compiler threshold and the outer conjunction are checked only by the authors' verifiers.
