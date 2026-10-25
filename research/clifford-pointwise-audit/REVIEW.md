# Internal review and resolution

Prepared for DLamdata with substantial OpenAI Codex assistance. Apache-2.0.
These are native AI reviews, not independent human or formal-kernel review.

## Independent derivation

The verifier agent read the pinned theorem and independently derived the fixed
Pauli-character, transvection, residual-form, rational-tail and Fourier steps
before comparing with the lead's executable evidence. It did not read or import
predecessor scientific code. Its exhaustive binary-matrix implementation is
retained as `verify_symplectic.py`. Normal/optimized receipts were identical;
six actual defects were rejected in both modes. The lead inspected its code and
compared its complete nonzero-trace histogram with the independently generated
literal-matrix histogram. The independent derivation found no substantive gap.

## Skeptical proof review

A second agent read the frozen proof and developed its analysis before reading
the source README/bounds implementation or any lead result. It independently
checked all four rational tail bounds and all central-phase filters. No
substantive defect was found. Its useful clarifications were incorporated:

| Concern | Resolution |
|---|---|
| Ordinary Hadamard is outside Z[i,1/2]; does the full projective lift exist? | AUDIT section1 gives Gaussian-dyadic H' and a direct transvection lift. Literal generation retains (H')^2=iI. |
| Fixed Paulis can anticommute. Are their signs a character? | AUDIT section3 cancels the identical Pauli multiplication phase explicitly; isotropy of the fixed space is not assumed. |
| Does counting residual forms assume an unjustified converse? | AUDIT section4 uses only an injection and counts singular forms in an upper bound. The independent checker tests actual preimages and injectivity. |
| Four tests can be misread as covering changing coefficients or arbitrary scales. | AUDIT section6 and executable counterexamples retain both exclusions. |
| Finite agreement may be mistaken for an all-size proof. | AUDIT separates universal reasoning/classical inputs from every finite check; README states their precise domains. |
| Source includes later repair/application claims. | Core scope is explicit throughout; no passive-caller, paid-repair, invoice or selected construction is endorsed. |

## Shared assumptions and implementation overlap

Both agents necessarily read the same mathematical statement. Classical
Clifford generation/order, stabilizer normal forms, symplectic structure,
character orthogonality and exact arithmetic are shared assumptions. The lead's
Gaussian-matrix orbit is related to the predecessor's projective Choi orbit;
it is not represented as a wholly unrelated algorithm. Its explicit central
extension and phase-boundary controls complement the separate exhaustive
binary-matrix/residual-form path. No predecessor executable is imported.

All tested assertions use explicit exceptions and remain active under `-O`.
Source/receipt corruption controls require specific failure diagnostics.
Mutation jobs are serial and operate only on temporary copies. A copied
read-only package is made writable only inside that temporary test directory.
The original package and its source inputs remain unchanged during replay.

## Review scope still open

The original handoff also requests an actual passive-contract audit. That part,
PR5526's later 104-return repair theorem and invoice, PR5531's application,
native frontend correctness, physical costs, selected cold replay and the full
multiplication theorem remain outside this contribution. External Claude
review was not required or obtained.

## Final package review

Both agents subsequently reviewed the frozen 15-file contribution. The independent
reviewer confirmed the unchanged independent checker and both complete trace
histograms, and tested Hermitian positive/singular/indefinite fixtures. The skeptical
reviewer authenticated both retained documents against exact-head Git blobs and
independently checked literal H-prime, S and CNOT fixtures. Neither reran the lead's
suite. No blocking defect was found.

One wording ambiguity was resolved: two matrix mutation controls change a required
mathematical expectation (the first-overlap count and H-prime square), rather than
mutating the gate implementation. They are now named
`wrong-first-overlap-expectation` and `wrong-H-square-expectation`; the erased-width
control really does change Gram construction. The affected driver was rerun.
This clarification changes neither mathematical evidence nor source pins.
