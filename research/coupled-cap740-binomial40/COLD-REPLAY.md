# Session cold replay and release continuation

The small package replay authenticates stored supplier evidence. The separate
session run rebuilt the retained bootstrap and native providers from fresh
inputs. Consult `VALIDATION.json` for actual completion status; this document
does not assert a pending run passed.

The session layout is a workspace containing `research/` (the isolated Git
checkout), `.venv/`, `logs/`, `evidence/` and external replay directories.
The exact repository base, source hashes and isolated dependency versions are
recorded in `VALIDATION.json`. Obtain the supplier's declared dependencies
using `research/coupled-carrier-cap740/FETCH.txt` in the checkout.

From the checkout, the original command was:

```sh
nice -n 15 ionice -c 3 env OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
  ../.venv/bin/python -B research/coupled-carrier-cap740/reproduce.py \
  --repo . --work ../replay-t740-cold --jobs 2
```

It exited 1 when the unchanged controller's complete-admission subprocess
exceeded 3,600 seconds. The fresh retained bootstrap, both current native
providers and discovery stages had completed. The full release was still
running. The original output directory and timeout log are preserved.

The continuation uses the generated, manifest-authenticated package and the
fresh, authenticated native cache. From the workspace, its core command is:

```sh
.venv/bin/python -B \
  replay-t740-cold/run/candidate/package/verify_release.py \
  --main replay-t740-cold/run \
  --work replay-t740-release-continuation \
  --native-cache replay-t740-cold/run/native/native-cache --jobs 2
```

The output directory must not exist. This runs the complete release verifier
unchanged, including its native-receipt checks, retained parent admission,
word reconstruction, exact owner and frame checks, strict global replay,
geometry controls and modern outer checks. It does not reuse partial output
from the failed release directory or relax a mathematical predicate.

The session wrapper `continue_t740_release.py` additionally authenticates the
complete source, cache, external inputs and generated package before and after
the command. It binds the final receipt to the package manifest and exact outer
claim. On successful completion, `validation-logs/` includes that wrapper and
the actual receipts. To reuse the wrapper with this layout, copy it to the
workspace root first; its paths are relative to its own location. The wrapper
produces a separately named continuation receipt and never rewrites the failed
controller result. The original documented one-command replay remains a
recorded timeout on this machine.

The final packaging step also checks the literal allocation against the pinned
supplier's payload/order/dispatch hashes and compares the reproduced rational
κ to PR3148's exact stored composition. The candidate's finer endpoint is
then checked separately by this package's three moment engines and unchanged
outer transfer. Neither the cold supplier replay nor these arithmetic checks
discharges the all-size conditional obligations listed in `PROOF.md`.
