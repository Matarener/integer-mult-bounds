# Credit and licenses

Brian Ross contributed the conceptual search strategy, proposed transferring
the constraint-search approach developed in his earlier Jane Street work,
selected this research direction, and provided oversight and substantive
challenge of the result. Code, encodings, computational experiments, proof
checking and documentation were prepared with substantial OpenAI Codex
assistance.

The exact model and prior bounds build on Hanson Sun's
`bit-gl3-mixed-targets-seed18` and Josie Elliston's
`bit-gl3-mixed-targets-length10`, including its three-register `engine3.cpp`.
The nine-call upper bound is the existing direct construction.

New package code and documentation are Apache-2.0, as in the repository.
Vendored DRAT-trim source is by Marijn Heule and retains its MIT license in
`third_party/drat-trim/LICENSE`. Glucose/PySAT and Z3 are separately installed
dependencies; their executables are not redistributed.
