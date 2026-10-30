OWNED QUERY ADAPTERS — SCOPED MATHEMATICAL HANDOFF

Outcome: no new κ value was established. The strongest open claim observed at the final checkpoint is PR #4470, conditional κ = 0.00302015. Canonical main still selects conditional κ = 0.0023. These are different statuses.

1. Sufficient two-port construction

Let V be a vector space over a field K. Let A and B be invertible K-linear maps on V, and let λ ∈ K. Store arbitrary independent logical values x and y physically as Bx and Ay. Assume the native model permits scalar COPY and ADD, explicitly clearing an owned temporary, and a paid exact implementation of U = A B⁻¹ with all its monomial factors and absolute phase.

Then the logical shear (x, y) ↦ (x, y + λx) has a construction that leaves both persistent charts unchanged and invokes U once:

clear temporary; copy Bx into temporary; apply U; add λ times temporary into Ay; clear temporary.

Proof. Immediately after U, the temporary equals A B⁻¹ Bx = Ax. The destination becomes Ay + λAx = A(y + λx). The source remains Bx, and the temporary returns to zero. This calculation holds for every x and y and for an arbitrary initial temporary because the first clear removes it. It does not erase or assume anything about an arbitrary persistent input. If λ = 0, omit the entire episode.

If exact native lowering gives Fourier rank d for U, the recursive bill is one rank-d job when d > 0, no productive credit for the temporary, and its full monomial/scalar implementation. A rank-zero U still has its finite monomial implementation. There is one extra owned field. Relative to the original ADD, clear/copy/clear are three additional scalar operations, with the actual source primitive allowances for coefficients and routes. The temporary must not alias a live C0 or any persistent field.

This is a sufficient construction under the stated native operations. It does not establish the inherited all-size native lift, precision, stock, tape, analytic or recovery assumptions.

2. Sufficient shared-bridge construction

Under the exact primitive and nonaliasing assumptions of Section 1, let I and J be disjoint sets of source and destination fields. Suppose every source uses chart B and every destination uses chart A. Let the requested simultaneous coefficient matrix factor as M[j,i] = u[j] v[i]. Then all updates

y[j] ↦ y[j] + Σ_i M[j,i] x[i]

can share one paid U = A B⁻¹, with one owned temporary and no productive credit for that temporary.

Proof. Clear the temporary, form Σ_i v[i] Bx[i] by explicit scalar copies/additions, apply U once, then add u[j] times that temporary to each Ay[j], and clear it. Linearity gives U(Σ_i v[i] Bx[i]) = A Σ_i v[i] x[i]. Sources and unrelated fields are untouched, and all destination equations follow. Scalar coefficient costs and the complete owned stock are charged. If source and destination sets intersect, or intervening operations do not commute, this proof does not authorize gathering them.

This covers one-source broadcasts, one-destination accumulation and rational rank-one rectangles. It is not a claim that these elementary linear-algebra ideas are new to the literature or to all prior PRs.

3. Restricted search representation

Write D(A,B) for the exact Fourier rank of C_A C_B⁻¹. At an LL-ADD contact, split its common chart vertex into an independent source port and destination port, connected by a paid metric edge D(A,B)^(1−κ). The first construction implements that edge. Existing field transports remain on the field rails. Fixing helper endpoints preserves every productive helper rank; fixing endpoints of each nonordinary warp preserves its actual operator and charge. Owned C0 and all eight rank-eight center calls remain charged.

For the pinned source, this produces 34,790 vertices, 50,067 paid edges and 16,089 potential query bridges, with 1,790 fixed vertices. The initial graph reproduces the full PR #4470 paid profile exactly. The final plateau state also has exactly that same rank histogram. No κ improvement follows.

The portable C++17 discovery engines tested all 1,224 single-label expansions, 2,415 swaps among 70 frequent labels, and 60 passes allowing only identical-histogram plateau moves. No accepted improvement was found. Floating costs and integer-rounded cut capacities make these bounded search observations, not exact optimality or impossibility theorems. The expanded model can strictly help other instances: a checked four-terminal control saves one unit, and 30 binary graph controls match exhaustive optima.

4. Reproduction and limits

README.md states the portable replay and its limits. The new replay checks seven pinned physical frame pairs in both orientations, decodes native recipes including absolute phase, checks rational shear/shared-bridge controls, and recomputes every snapshot distance and its initial complete paid profile. It does not reconstruct or certify a new full native supplier. The campaign-specific exporter and research dependencies are excluded.

The numerical search observations are frozen in SEARCH-RESULTS.json. Optional C++17 replay uses run_search.py. No new κ, selected-frontier update, global optimum, novelty or Linux execution is claimed. Any improved future candidate still needs both full physical orientations, all arbitrary-input columns, complete owned stock and scalar costs, exact controller/moment/compiler checks and every outer obligation.

Credit the retained native and Clifford authors, PR #4359, #4416, #4440, #4441, #4447 and #4470; see ATTRIBUTION.md. Source-only DAG retrieval was not a fresh Lean kernel audit. Prepared for Dugongue with substantial OpenAI assistance. Apache-2.0.
