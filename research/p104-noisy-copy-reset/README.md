# P104 precision with additive COPY and reset residuals

The strongest pinned pending P104 word has 25,984 events, 770 public fields and
29 owned coordinates. This package proves a source-bound precision lemma for a
new completed-operation contract. COPY adds into its destination, so it retains
a reset residual. INIT and CLEAR can leave bounded residuals. Every completed
operation can add a stated relative defect. See [PROOF.md](PROOF.md).

The exact all-prefix scores are J=56,663,088, K=2,428,962 and G=1,361,937.
The largest ideal input norm is 131,072. Sufficient guard bits are **26 for all
prefixes, 23 for final public fields, and 22 for final owned residuals**. These
are the least integers for the stated bounds, not a minimum physical precision.
A final owned residual is not an exact zero return.

The replay checks the complete arbitrary-input endpoint. It checks every final
signed defect coefficient in both directions, attains the independent defect
and input gains by literal scalar execution, and rejects six invalid claims.
One control shows why an overwrite COPY error transition loses a reset residual.
PR5819 uses exact resets, so that control does not refute its stated theorem.

The caller is PR5811 at `33d7760d0a6fea6394aefd014eea68f0af02a92e`.
The precision method comes from PR5819 at
`05c15af1393f7d737fa316b507638a50f20d4925`. Its source is retained unchanged.
`PRECISION-EDITS.json` declares each change in the adapted `precision.py` module.
The verifier checks those edits before it loads either module.

Run `python3 -B scripts/research_package.py --package research/p104-noisy-copy-reset`.
The standalone command is `python3 -B research/p104-noisy-copy-reset/verify.py`.
Python 3.12 and its standard library suffice. `RESULT.json` records the complete
scores, hashes, guard calculation and controls. Source authentication precedes
replay. The package supports a read-only Git-free export and Python optimization.

This is an informal scoped lemma, not a Lean theorem, a new kappa, or supplier
admission. Native unitary gauges remain a premise. The exact owned-erasure,
compiler, precision-tape and analytic-recovery obligations keep their status.
The current selected frontier is unchanged.

## Open next questions

- Implement and price a completed reset and additive COPY which meet these local
  allowances on the actual signed-query tape. Start with the 30 nonzero erasures.
- Bind the native unitary norm premise to an admitted child operation, including
  its rounding, basis conversion and restoration.
- Prove the exact owned-zero return contract, or state and price a changed outer
  interface which can accept the final residual. This lemma does neither.

See `TASK.json` for the recorded scope change and structured next steps.

Credit Adam Gall, ywz65, PR2878, PR5819, Mason Hale/PR5811, and the P104 hub,
accumulation and block authors. Both source NOTICE files are retained in inputs.
Ali Romman with substantial OpenAI Codex assistance in proof, code and checks.
Apache-2.0. No independent scientific acceptance is claimed.

The source manifest pins replay inputs to copies in this publication history.
Its `retained_predecessors` records keep each original head, path, blob and
SHA256, plus its exact retained file or archive member. Each source was checked
byte-for-byte before this rebind. This removes an unavailable side-commit
dependency from clean CI; no source bytes or scientific checks are changed.
