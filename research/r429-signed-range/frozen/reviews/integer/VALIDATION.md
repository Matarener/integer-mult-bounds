# Local validation of the independent integer audit

The final independent checker ran on the package's four frozen inputs with
bundled Python 3.12.14, standard library only:
`-I -O -B -Werror`. It passed in 5.490 seconds under a 60-second process cap.
This run included all four complete parent/candidate orientation replays, both
integer roundtrips for each word, the all-sign transfer certificate, all four
attaining prefix witnesses, and nine semantic negative controls.

A second execution copied only the checker and its four compressed inputs
into a Git-free directory whose path contains spaces. It omitted the optional
`--out`, used relative explicit input paths, and produced a byte-identical
receipt on stdout in 3.959 seconds. In particular the compressed matrix input
was accepted by its unchanged decoded-byte hash.

A separately recompressed, scientifically changed candidate input was
rejected with `authentication: signed_word`. This authentication check is
separate from the nine post-authentication semantic controls.

The optional complete endpoint export was decoded independently into its four
652-by-651 dense integer matrices. Every matrix digest agreed with the final
receipt; no endpoint export needs to be bundled because the checker regenerates
it from the frozen inputs.

From the package root, reproduce with:

```sh
python3.12 -I -O -B -Werror \
  frozen/reviews/integer/check_integer.py \
  --parent-word frozen/parent/WORD.json.gz \
  --signed-word frozen/candidate/WORD.json.gz \
  --raw-word frozen/geometry/WORD.json.gz \
  --matrices frozen/geometry/MATRICES.json.gz \
  --out /tmp/b04-integer-receipt.json \
  --endpoint-out /tmp/b04-integer-endpoints.json
```

`--out` and `--endpoint-out` are optional file outputs; choose external fresh
paths. Without `--out`, the complete deterministic JSON receipt goes to stdout.
No Git checkout, source optimizer, network access or third-party package is
needed.

The final local checker SHA256 is
`96e6fe96e72111e691dac904fc3991b2ddca440509ffaf5bf4a990d27c33e522`.
The uncompressed deterministic receipt SHA256 is
`c887cf32e5640221e038e4358df6422fbc1f32d3f3c5b6ab3b14cc1723bce1fd`.
The compressed receipt preserves exactly those decoded bytes.
The reviewer also retains machine-readable local evidence in `VALIDATION.json`.

These are local package checks. No sign search, native-vector or precision
replay, recursive supplier audit, formal-kernel proof or hosted CI was run
by this independent reviewer.
