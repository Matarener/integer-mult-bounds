# Actual source continuation PC envelope

The historical PR2753/PR589 selected caller's complete instruction count N obeys

    12,295,296 G + 78,175 <= N <= 59,884,739,136 G + 78,175,
    G=|GL64(F_q)|, q=213·2^80+1.

The source continuation label needs359,385–359,398bits. The certificate derives
these bounds from the actual288calls, hosting occupancy and fallback compiler,
without visiting GL64 classes or residual factories. [PROOF.md](PROOF.md) gives
the all-plan argument; [RESULT.json](RESULT.json) records exact integer hashes,
source counts and bounded verification.

The unchanged FiniteFields/Tape codec and literal call/return header statements
roundtrip a guaranteed in-range address beyond Py_ssize_t. The code checks the
actual serialized extent and reads/writes/moves. This is a projected header
fixture, not a physical recursive/payload replay or a known recursive site.

The crucial remaining boundary is explicit: an upper count does not provide
exact instruction indexing, factory/identity preservation, or rejection of
forged PCs in the gap between N and the upper bound. A production adapter needs
an exact index/domain provider and its cost proof. We do not replace len with an
unverified count or alter the production source. This package is a scoped bound
and interface audit, not selected PR5413 supplier admission or a new kappa.

## Reproduce

Python3.12, standard library, no Git needed for scientific replay:

```sh
python3.12 -I -B research/selected-continuation-pc-envelope/verify.py
python3.12 -I -O -B research/selected-continuation-pc-envelope/verify.py
```

The source manifest pins15live inputs. Tests include actual small projector
plans and Cursor traces, source successor/stage mutations, length overflow,
codec bounds, typed receipt and source-byte controls. All sources remain intact.

## Open next questions

- Build the exact outer prefix/index provider while preserving original Residual
  identities and ordered factory observations; certify its domain separately.
- Validate restored PCs against that exact domain before side effects when the
  old malformed-header rejection contract must be preserved.
- Bind the resulting lookup/header costs and current source admission through
  the selected loader. Runtime plan mutation scans remain a separate cost.

Canonical claim: [Discussion2319](https://github.com/CrocSwap/integer-mult-bounds/discussions/2319#discussioncomment-19173371).
Base32890bc5de034ab8fc93ac88ead7279a6a416d04, priority7. Root refreshed359openPRs,
4760Discussion records and7402local notes before assignment. Unpublished work,
all historical diffs and later updates are outside that novelty coverage.

JoyboyBrian, with substantial OpenAI Codex assistance. Credit Jose Manuel's
source caller/compiler/codec and PR2234 prime witness; retain all predecessor
notices and Apache-2.0. Earlier PR4791/PR5495 provide motivation only, not an
unmerged scientific dependency. No human or formal-kernel acceptance claimed.
