# Actual odd-E8 negative exit: an all-width ordinary ADD lower bound

For the frozen PR5464 E caller, the specified negative Gaussian target requires Q^-1 B_E^-1 Q. Its actual global spectral coefficients supply a surviving nonmonomial fresh-stage path, so every exact ordinary postdecoder needs at least max(0,2f-216) ADDs at tensor width f. A fixed-size ordinary recoding cannot complete that target. More strongly, for f>=4198 the required decoder is outside the entire columnwise monomial-Clifford algebra, even with arbitrarily many operations and f-dependent coefficients. Arbitrary cross-column permutations are outside this stronger statement.

This source-bound application credits the existing fresh-stage separation/contraction lemma and derives new actual E coefficients; it does not repeat the source's failed naive B_E^-1 check or extrapolate its small fixture. PROOF.md states the target, all-width argument, complete invoice boundary and open next questions. No paid-decoder lower bound or new kappa is claimed.

Run python3 -I -B research/odd-e8-negative-exit-algebra/verify.py, also with -O. Exact source bytes are authenticated before use. Sparse phase checks avoid dense2^25 arrays. Source proofs retain their attribution; substantial OpenAI Codex assistance, Apache-2.0.

## Open next questions

Can a paid decoder, an already-paid IDLE, or an ordinary program using cross-column operations whose count grows with f fit the full caller budget? Begin with the complete original-input identity, preserved histories, precision and cleanup invoice; those interfaces are not priced by this support obstruction.
