# Nine-channel canonical delivery bound

For PR5745's fixed source and immutable one-frame payload contract, any
completion using at most nine channels costs at least **8 H8**, for every
positive nondecreasing canonical transport tariff. The known eight-channel
construction attains the paid bound. Joint nuisance cancellation and
arbitrary repeated contacts in each channel's frame are allowed.

The source-specific certificate proves that no sum of two temporal response
spaces of grade below eight contains a nonzero clean mode. This rules out
two low-grade channels in any nine-channel rank-one-nuisance completion.
See [PROOF.md](PROOF.md) for the complete argument and scope.

**Related work:** PR5823 separately proposes the all-finite-channel bound for
concave power tariffs. This package is a differently checked, nine-channel
result for a broader tariff class, not the first solution of that power-tariff
problem. Its entire certificate was not replayed here.

## Reproduce

Extract this archive, change into this directory, then run:

```sh
python3 -B verify.py
python3 -O -B verify.py
```

Both commands recompute the response spaces and pair certificate, compare
the complete semantic RESULT.json, and print PASS_NINE_CHANNEL_DELIVERY_BOUND.
No network or third-party library is required. Tested with CPython 3.14.4 on
macOS. The checks take a few minutes. `--write-result` intentionally regenerates
the result; omit it for verification.

`source/` contains the unchanged predecessor archive and exact proof/code
snapshots. The verifier reads only two data members from the archive and
executes none of its archived Python code. It retains two source-level paths:
instrumented predecessor cuts.py and the new independent.py. Source pins are
in SOURCES.json. No repository, CI or GitHub submission is implied.

## Open next questions

- For arbitrary nondecreasing tariffs and k>=10, determine whether higher
  dimensional nuisance cancellation can overcome the pair obstruction. First
  inspect three-frame sums, then check a complete payload solution and cost.
  Pairwise exclusion alone is insufficient; the abstract control shows why.
- For the project's concave power tariffs, inspect or independently replay
  PR5823 before spending effort on more fixed-frame immutable-channel searches.
- To pursue a paid improvement outside that contract, specify a moving-frame,
  changed-word or recomputed-payload mechanism and charge its transport,
  restoration and ordinary operations before constructing a larger caller.

Prepared for Nicholas with substantial OpenAI Codex assistance. Apache-2.0.
Predecessor attribution and limitations are retained in PROOF.md and source/.
