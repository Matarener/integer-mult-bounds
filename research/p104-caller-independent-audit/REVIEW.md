# Review boundary

The new independent implementation uses exact Z4 phase polynomials, a free
Laurent matrix and explicit field injections. Retained canonical compiler and
literal gate descriptions are reused; the phase anchor uses the separate
dense integer Gaussian-dyadic engine published in PR5548. Native comparisons
check every signed Pauli image plus a nonzero exact column. For these Clifford
gate circuits, equal conjugations imply a scalar quotient and the column fixes
that scalar. The source rank/profile assertions are externally checked under
both Python modes; compiler internal assertions are not the sole evidence.

Absolute phase conventions are explicit. The scalar global-phase control
checks the zero-frequency spectral anchor; it is not a full mutated-source
replay. Query ownership/correction controls check source/destination separation,
the emitted chronology and exact Q versus Q^-1 phase. They do not prove the
underlying owned-erasure assumption. Fresh helper disjointness and before/after
normalizer placement are checked under the retained all-input local ABI.
No spectator is counted as an additional independent productive field.

The forward caller's literal free-Laurent endpoint is exact. All34 exponents
are represented; byte packing is injective on the checked range, and overflow
fails instead of wrapping. Integral coefficients are exact, not rounded
rational approximations. Wrong exterior sign and missing-idle controls rerun
the complete matrix and must reject. Compact canonicalizers specify base9 maps
and all265 coordinate positions, with complete inverse basis checks.

The untouched paid-native inventory and the complete-caller raw inverse
transpose are not replayed. Contact inverses are narrower. Precision/tape,
storage, erasure and compiler/outer applicability remain written obligations.
The abstract ordinary-pass census is not a new Turing-machine or precision
theorem. No new complete economic profile or κ follows from this package.

Original scientific pair:100.9167seconds, sampled peak82.35MiB, cap150seconds/
512MiB, exact complete output equality, no scientific exclusions. Operational
traces record timing/RSS separately. The old resource failure remains history;
the combined memory changes fix execution but do not isolate one causal culprit.
Portable registered replay and read-only export validate the publication
wrapper separately. Hosted CI, archival merge and selected admission are
distinct statuses, to be recorded with their actual heads and evidence.
