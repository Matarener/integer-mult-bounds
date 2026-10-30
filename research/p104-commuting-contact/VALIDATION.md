# Verification record

The source word is PR #5580 (`research/p104-event-contact-step`) at `6efa248cf456d6101d757e9d09ba29711d18a13a`. The base is canonical main `5e0052ca0aa3036a3afa8b0438927377c8d97d53`. The selected record is unchanged.

The registered warning-strict normal (`-W error -B`) and optimized (`-W error -B -O`) replays both pass and print `PASS_P104_COMMUTING_CONTACT_KAPPA_00308520`.

Exact checks performed by `verify.py`:
1. SHA256 and Git blob authentication of `inputs/pr5580-WORD.json.gz`, `inputs/pr5580-pricing.py`, `common.py`, and all 33 payloads in `inputs/pr5545-source-closure.tar.gz`.
2. Deterministic regeneration of `WORD-FIXED-ENDPOINTS.json.gz` (25,136 events, local paid delta `-4 H1 - 4 H4 + 4 H5`) and `WORD.json.gz` (25,133 events, local paid delta `-8 H1 - H3 - 2 H4 + 4 H5`, local target delta `-H8 + H9`) from `construct.py`.
3. Arbitrary-input symbolic forward replay (`L.replay`) of the PR #5580 base word, the Stage A fixed-endpoint word, and the Stage A+B headline word across all 743 rows.
4. Dense dyadic reverse-chronology transpose verification (`L.reverse_columns`) across all $743 \times 743 = 552,049$ entries.
5. Exact signed Pauli image and global phase verification (`L.native`) across all 2,918 distinct native chart transitions and 208 free main adapters.
6. Complete physical controller verification (`C.physical`) and dual-moment interval verification (`P.run`) certifying `(0.00308415555080, 0.00308415555081)` for Stage A and `(0.00308521055201, 0.00308521055202)` for Stage A+B (`KAPPA = 0.00308520`, `TESTED = 0.0030852005`, `66,726` paid calls, `12,814` productive fields, surplus `760`).
7. Five negative controls (`missing_source_transport`, `mismatched_commuted_frame`, `wrong_scalar_coefficient`, `non_nested_return`, `unchanged_word`) plus retained native-phase, BIT, and cutoff controls.
