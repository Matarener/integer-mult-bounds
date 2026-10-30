# Independent ordinary rational-matrix check

This component retains the complete separately implemented C09 review checker.
It imports no candidate or historical arithmetic. Its only mathematical input
is the authenticated original `CUBIC-FOUR-CALL-GATE.json`; the wrapper supplies
that fixed path. The source itself is unchanged.

The full three-cycle acts on `(1,N,N^2)` and injectively represents the whole
cubic algebra. The checker reconstructs every prefix of all four normalization
fixtures on all nine rational input columns, including evolving augmentation.
It verifies the excluded operator-dependent four-factor target and literal
inverse, and rejects a matrix with the right primitive value but wrong
augmentation.

A distinct two-dimensional rational matrix is used only for necessary primitive
specialization. This engine reconstructs the full interaction resolvent and
noncentral target defect, pure-layer coefficient formulas and their remainder,
the reversed literal pair inverse, and polynomial projectors with nontrivial
Jordan blocks. The fixtures do not purport to realize the impossible common
image/kernel equality case in the written obstruction.

Twelve actual algebraic defects must fail their named predicates. Each same
mutant then runs with only that predicate removed outside the rejection handler.
The complete receipt retains every matrix and prefix. Normal and optimized
Python 3.12 records are identical.

These finite checks support identities and sensitivity. The universal query
and layer bounds are the written arguments in `../cubic/PROOF.md`, not a finite
enumeration. This independent implementation is an AI mathematical review
context, not independent human acceptance, formal-kernel verification or a
native caller. Prepared with substantial OpenAI Codex assistance.

From the installed package root, the standalone command is

```
python3.12 -B independent/check.py \
  --historical-receipt /absolute/package/cubic/frozen/CUBIC-FOUR-CALL-GATE.json \
  --output /absolute/external/new-independent.json
```

The normal package command is `python3.12 -I -O -B verify.py --stage independent`.
This contract summary is new integration documentation; the unchanged original
review is pinned separately in top-level `ORIGINS.json` as documentary provenance.
