# Validation

At proof commit 934b3120df770d04377cce1ec7dc7520ac1b4f28, the registered
Python 3.12.13 commands passed in normal and optimized modes. Each replay
checks all six trace witnesses, literal 2-by-2 and 3-by-3 traces, changed
witness rejection, the curvature blocks through n=32 and all eleven rational
price bounds. No numerical search is part of this replay.

All 21 committed package files passed the byte and owner-execute-mode
preflight. The official export and its offline integrity check passed. A
fresh, read-only, Git-free export passed the optimized direct verifier in
8.5845 seconds with an empty PATH. All 22 exported files, including the export
receipt, kept their bytes and modes. Separate mutations of each of the three
frozen source copies failed before scientific replay.

The selected source certificate is checked by SHA256 and Git blob ID. The
portable algebra helpers retain their exact PR6168 bytes and attribution.
The metadata and source pins passed. Direct main-base and helper-head ancestry
checks passed. Full-history preflight is unavailable in this shallow checkout.
The later validation-only commit does not change the checked executable bytes.

The written rank and trace arguments are author-side proofs. Independent
scientific review and proof-kernel checking remain absent. The native source,
selected full caller, compiler and outer theorem were not rerun. No selected
frontier change or kappa increase is claimed. Hosted CI for this extension is
reported in the PR after publication; a local pass is not a hosted CI pass.
