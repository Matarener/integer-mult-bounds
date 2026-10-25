# Verification and its boundaries

There are two distinct replays. The registered Python replay checks source
binding and independent arithmetic controls. The explicit Lean replay freshly
checks the proof terms. Neither a stored JSON receipt nor a successful Python
run substitutes for invoking the kernel.

## Registered source replay

From the repository root:

```sh
python3 scripts/research_package.py --package research/k8-helper450-lean-row --check-only
python3.12 scripts/research_package.py --package research/k8-helper450-lean-row
```

[VERIFY.json](VERIFY.json) declares the exact commands, live inputs, and
120-second per-command limits. This path uses Python 3.12 and the standard
library. The generic runner supplies private bytecode-cache storage and invokes
the checks with `-I -O -Werror -B`.

The source replay authenticates the input bytes before executing the retained
translator/generator. It binds the selected archive member, complete forward
word, source-index map, constructor inventory, active ADDs, and three protected
blocks. Regeneration must reproduce all 14 original forward Lean source hashes
from PR2944's retained `KERNEL.json`.

Seven control groups independently check the scalar row using exact
`Fraction` arithmetic, mutate the active sign/target/partner or omit an ADD,
write the protected partner inside the middle block, distinguish COPY from
CLEAR, reject malformed scalar events, reject changed source bytes, and check
the unchanged generator's output. These controls test the adapter boundary and
the claimed invariant; they are not a proof of arbitrary Python serialization.

## Fresh kernel replay

Provide an existing Lean project whose `lean-toolchain`, `lake-manifest.json`,
and dependency checkout revisions match the pinned repository files:

```sh
python3.12 -I -O -Werror -B research/k8-helper450-lean-row/check_lean.py \
  --lake-project /path/to/matching/lean/project
```

The required compiler is `leanprover/lean4:v4.21.0`; Mathlib is pinned at
`308445d7985027f538e281e18df29ca16ede2ba3`. The other dependency revisions come
from the authenticated manifest. Compiled libraries must already exist for the
dependencies actually imported by the proof. The supplied cache has nine
dependency checkouts and eight compiled library paths; the unimported `Cli`
package needs no compiled library. The driver verifies the compiler version,
manifest bytes, and all nine Git HEADs, then uses that cache read-only. It does
not invoke Lake, fetch dependencies, or modify the supplied project. Compiler binaries and
precompiled dependency artifacts remain part of the stated trusted environment;
Git HEAD checks alone are not an independent rebuild of those artifacts.

The driver regenerates the original forward sources and compiles the pinned
semantics, the new generic proof, and the concrete proof into a private temporary
directory. `--work-dir /path/to/existing/scratch` chooses its parent directory.
The temporary directory is removed on success or failure. Inputs and package
sources are checked again after compilation.

The concrete proof works over the original 97 generated blocks, each of length
at most 256. Append/flatten identities give the unchanged complete word and
the four avoidance predicates. The full run succeeds with the default stack.
Compilation uses `-j1` and warnings as errors, with a 180-second limit per
compiled module; each rejected false-claim invocation has a 60-second limit.

Without `--write-receipt`, a fresh run compares the resulting evidence with this
package's retained `KERNEL.json`; the compiler's platform-description text is
normalized for comparison. To record a new result without overwriting an
existing file:

```sh
python3.12 -I -O -Werror -B research/k8-helper450-lean-row/check_lean.py \
  --lake-project /path/to/matching/lean/project \
  --write-receipt /path/to/new-kernel-receipt.json
```

Five theorem roots are queried with `#print axioms`: the two generic
`Helper450Row.inverse_adds_*` theorems and the concrete `helper450_restored`,
`helper450_unit_row`, and `helper450_hS` theorems. The driver rejects missing
reports and axioms outside `propext`, `Classical.choice`, and `Quot.sound`.
It also rejects proof-source escape hatches such as `sorry`, `admit`, and
`native_decide`. The exact root-specific lists must be read from the fresh
receipt, not inferred from this allowed set.

The fresh run reports exactly `propext` and `Quot.sound` for the two generic
roots. The three concrete roots additionally use `Classical.choice`.

Kernel controls cover a wrong second sign, an intervening CLEAR of the
partner, and aliased helper/partner coordinates. Positive controls retain
scalar-neutral relabels and demonstrate that a restored row can still have a
leaking input column. These keep the claimed assumptions and conclusion
separate from physical or whole-state restoration.

## Recorded evidence

- Registered source replay: **PASS**, CPython 3.12.15. Both registered commands
  passed with `-I -O -Werror -B`; the seven control groups took 1.463 seconds.
  The launcher reported `PASS_REGISTERED_RESEARCH_PACKAGE`. Metadata and input
  pin checks also passed. [RESULT.json](RESULT.json) explicitly records
  `fresh_lean_build: false` for this source/receipt replay.
- Fresh kernel run: **PASS**, completed 2026-10-17 at 22:48:55 UTC in
  **591.5 seconds**. Lean reported version 4.21.0,
  `x86_64-unknown-linux-gnu`, commit `6741444a63ee`, Release. The run compiled
  21 source files and rejected all three false-claim invocations. The five
  root-axiom reports and source hashes are retained in [KERNEL.json](KERNEL.json).
- The external PR2944 `KERNEL.json` is archived provenance for the existing
  typed word and its generated-source hashes. It does not certify the new
  helper450 theorem; this package's fresh receipt records that check.

The recorded kernel invocation, from the repository root, was:

```sh
/tmp/imb-loop-9963-i12/bin/python3.12 -I -O -Werror -B \
  research/k8-helper450-lean-row/check_lean.py \
  --lake-project /root/projects/integer-mult-bound-ci-performance/formal/lean \
  --work-dir /root/projects/imb-loop-9963/.scratch/iteration-12 \
  --write-receipt research/k8-helper450-lean-row/KERNEL.json
```

The supplied cache was read-only. All generated `.olean` files were confined
to the driver's private temporary directory and removed after the run. The
session-specific interpreter and scratch paths are historical environment
details; use the portable command above with your own matching cache.

The strongest claim remains the scalar row of the exact retained forward
typed word for all 1,024 initial coordinates. The source adapter, backward
word, isolated input column, physical recipes, ownership, and full selected
cold replay remain outside that claim. See [README.md](README.md) for the
precise word decomposition and predecessor attribution.
