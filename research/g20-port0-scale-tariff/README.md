# Port-0 G20 marker: unit-scale coefficient, unpriced head map

One authenticated ENTRY marker from the PR #5805 route manifest is eight exact
rational half-scales. Its coefficient lies in the proved `unit_scale` set, and
the matching RETURN twin restores the cover over `Q^8`. The published
`2048 V` fibre bill becomes `2080768 f^2 V` transitions only after each named
cover call is presented as its own `[P] x [Q] x [S]` fibre. The marker does
not provide that presentation. No new kappa is claimed.

The marker is event `21502`: call `1`, stage `1`, owner `0`, owner bank `0`,
port `0`, phase `ENTRY`, word
`af5261a8c087e8c2917cdc280302d07d75b8fe098e31581d21c1ba2d53b42313`.
The RETURN twin is event `36518`. [PROOF.md](PROOF.md) records the rational
products, the `Q = 5` witness (`2*3 = 6` against `1`, and `3/2` against `4`),
and the family histogram: `6868` scale factors outside `{±1,±2,±1/2}` and
`25840` non-integral ADD factors.

## Reproduction

Python 3.12 and the standard library. From the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/g20-port0-scale-tariff
```

Direct checks:

```sh
python3.12 -I -B research/g20-port0-scale-tariff/verify.py
python3.12 -I -O -B research/g20-port0-scale-tariff/verify.py
python3.12 -I -B research/g20-port0-scale-tariff/oracle.py
```

Expected tokens: `PASS_G20_PORT0_ENTRY_SCALE_TARIFF_GAP` and
`PASS_G20_PORT0_SCALE_ORACLE`. The commands read [RESULT.json](RESULT.json)
and do not rewrite it. Explicit `--emit` on `verify.py` prints a candidate
receipt to stdout.

[FROZEN.json](FROZEN.json) is an extract of PR #5805
`RESULT.json` and port 0 in `WORDS.json` at
`b895ae7770a97276ae0e9c13fb0c51cbed4fd00a`. The recorded SHA256 values are
`4d55a2f3b8acd1335bea0d05552ccaa2281623fab1c65ad6648519ac516172de` and
`c74b8446503425fb4964921e8651b3931f917c62a21565d9569e9f6399ea571b`.
Those blobs are not objects of canonical main `de5ec2e7a6074068452f45b1a191b5c72832df4a`,
so the verifier checks the extract rather than a `head:` pin. Recomputing the
manifest from `GLOBAL.jsonl` was not repeated.

The selected-record baseline on this base returned
`PASS_RESEARCH_BASELINE_BINDINGS_ONLY` with kappa `62009/20000000`.
That command is a binding check, not the scientific replay
`make frontier5599-verify`, which was not run.

## Scope

Task `bit-helper-contract`, priority revision 8. The card asks for a review of
the #5679/#5708 chain before another G20 search. #5782, #5798, #5801 and #5805
already cover native maps, the global caller, dyadic words and the conditional
marker-to-word join. #5807, #5820 and #5828 are open shorter-word searches.
This package takes the released #5805 question for one owner-marker: the
physical coefficient tariff. Scope status is **changed** because the result is
that tariff gap, not a new helper split. [TASK.json](TASK.json) records the
reason.

## Open next questions

Present one active coordinate of event `21502` as a literal `[P] x [Q] x [S]`
owner tape, with a proved head map from
`half*N^2 + row*N + active[i]*f + lane`, and attach the `2048 V` bill to that
tape. The missing head map, descriptors and cache/carry/commit/padding moves
block any import into the #5708 fee. A separate next factor is one manifest
ADD of coefficient `3/2`, which is outside unit shear and outside the proved
unit-scale set.

## Credit

Ali Romman supplied the G20 construction and the global caller audit. ToikY
supplied the dyadic words and the #5805 marker binding. JoyboyBrian supplied
the signed-dyadic scaling machine and the ordered and affine shears, with the
retained David Arias / Charles Bethin tape lineage. Dugongue and ai-nanachi
retain the earlier G20 source credit. The new extract, rational check,
modular witness and conditional count were prepared by unpaidmoon with
substantial Cursor Grok assistance. Apache-2.0.
