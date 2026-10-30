# Validation

Executed on macOS arm64 with CPython 3.12.13 and the Python standard library.
The source base is canonical main
`6cf7a683f447b9f1e2333791907fd92be5009a63`.

The registered replay passed in normal and optimized Python modes. Both
returned `PASS_ALTERNATING_PLANE_SPECTRAL_COPY` and
`PASS_REGISTERED_RESEARCH_PACKAGE`. Each replay took about three seconds.
The complete generated receipt matched RESULT.json.

The checker reconstructs all 336 ports and 6,720 ordered graph edges. It
checks the integer annihilating polynomial, exact spectral multiplicities,
all 651 four-space minors modulo a verified prime, all native phase/rank
controls, the 336-column tariff control and four rejected corruptions.
NumPy/SciPy were used only in discovery. They are not replay dependencies.

Committed-byte comparison and the official source-export integrity check passed.
Normal and optimized direct replays also passed in the Git-free export. A
forged receipt with copy floor 671 was rejected. All eight package files
retained their hashes after the corruption was restored. Source pins were
checked by the registered metadata replay. The optional full-history check
refused this shallow checkout; full ancestry was not verified.
Hosted CI and independent review have not been checked. No selected replay,
Lean, Docker, full caller, precision/tape or outer compilation was run.
The artifact proves no new kappa. No selected or predecessor file was edited.
