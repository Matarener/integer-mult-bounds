# Proof notes for the PR5551 native, caller and funding audit

All statements concern the fixed P104 local word `research/p104-joint-contact/WORD.json.gz` (PR5551) on
canonical main `5e0052ca0aa3036a3afa8b0438927377c8d97d53`, and its complete invoice in
`research/p104-joint-contact/RESULT.json`.

## Layer 1: replay and delta

`replay()` is new code that imports nothing from the source packages. Frames are bases of subspaces of F2^9;
their spans are built as sets. For every event it checks:

- MOVE: the register is in the source frame, its ownership flag is correct, and the target span strictly contains
  (public) or is strictly contained in (owned) the source span. The paid rank is the dimension gap.
- ADD, COPY, SCALE: the coefficient is nonzero and the destination (and source) registers are in the event's
  frame, so the scalar operation runs in a common chart. COPY writes only into a cleared owned field.
- INIT and CLEAR: owned lifetimes, peak occupancy one.

At the end every public register is in its final frame, no owned field is live, and the 735 + 8 rational rows
equal the identity on public registers plus X added into Y = X + 112 for the 104 live ports.

For the delta, the non-MOVE programs of PR5545 and PR5551 are equal after removing frame labels. Comparing the
spans of the frame labels event by event gives exactly 6 ADD and 15 SCALE chart edits; the six ADD sites are
listed in RESULT.json and match PR5551's construct.py. The paid multisets differ by 2H1 − 3H2 + H3 − H4 + H5,
and every public initial and final span is unchanged, so the helper target profile and the productive targets
are unchanged.

## Layer 2: caller and target binding

The PR5550 checker is used as in PR5567: four literal input lines are replaced in a temporary copy (word path,
helper profile, invoice, local route count from the MOVE count). The positive control runs the patched checker
on the PR5545 word and invoice and reproduces the complete frozen PR5550 output byte for byte, so the patch
preserves the checker. On PR5551 the checker recounts the invoice from the MOVEs and native ranks, requires it to
equal PR5551's `complete_cost`, and checks all productive targets, helper normalizers and ordinary costs.
PR5550 reports `paid_native_maps_replayed: false`; layer 3 supplies that check.

## Layer 3: native maps

For a MOVE from frame A to frame B the native operator is chart(A)⁻¹ chart(B). The canonical compiler
`clifford_exact.lower_child` lowers it to a recipe D·P·X·phase·(rank C gates)·D·P·X·phase. The literal
definition is `adjoint(frame(A)) + frame(B)` from `native_verify.py`. PR5548's dense interpreter evaluates
both circuits exactly, with Gaussian-dyadic integers, on each of the 512 basis inputs. We require

1. exact equality of every column, including absolute phase;
2. squared norm one for every column;
3. exactly 2^rank nonzero entries in every column, where rank is the paid rank of that transition.

The same is done for each distinct helper endpoint pair (chart(initial)⁻¹ chart(final), credited rank
dim final − dim initial) and for the 208 intrinsic main adapters (input C-gate into chart, chart into the output
C-gate and Fourier transform), which must lower at rank zero. Checking a phase fault with an unchanged signed
tableau and a flipped child sign shows that the comparison sees what tableau checks miss.

Condition 3 binds each paid job to an actual native Gaussian of the charged rank. Together with layer 1, which
fixes which maps occur and how often, this checks the native paid-map inventory of the word, not only the
maps new relative to PR5545.

## Layer 4: funding

The moment margin at κ is Σ_targets n·r^(1−κ) − Σ_paid n·r^(1−κ). Each power is computed as exp((1−κ)·ln r)
with 80 significant digits and widened by a relative 10⁻⁷⁰, which is far above the rounding error of the
Decimal ln/exp. Bisection on the grid 10⁻¹⁴ gives the largest grid point with a certified positive margin and
the next with a certified negative margin. They equal PR5551's `raw_root_interval`. The engine shares no code
with PR5551's two moment engines or its funding peer.

## Not covered

The uniform compiler for all recursion levels, owned erasure, precision and tape costs and analytic recovery are
inherited premises. The outer conjunction and certified κ constant are PR5551's own verifier checks and are not
repeated here.
