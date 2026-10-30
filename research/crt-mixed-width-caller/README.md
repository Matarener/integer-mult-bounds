# Explicit-width synchronized CRT caller

This supplies the literal mixed-width row/idle decoder and whole
balanced-tree caller for Cinna Davis's PR4100 `CRT.md:76–92`.
The CRT algebra and Beneš compiler are predecessor work. All-target
omission is already proved in PR4169; mixed-width reservoir allocation
is already proved in PR4174. This adds their explicit logical caller
binding, rather than claiming those results again.

[PROOF.md](PROOF.md) treats every power-of-two axis count, ell>=2,
pairwise coprime `2<=s_i<2^h_i`, and declared widths
`h_i in {ell-1,ell}`. Long axes use every global row. Short axes have
two literal idles, with **no target bit or table query**. Removing
idles recovers each source word exactly in order. Declared coordinate
widths are never silently shrunk to fit their moduli.

The synchronized whole tree equals the retained arithmetic CRT
caller on every padded tuple. Reversing levels and rows gives its
inverse. Valid padding is preserved at whole-network/level endpoints;
intermediate switches can legitimately pass through invalid target
values. Globally invalid tuples are permuted bijectively and need
not be pointwise fixed.

## Evidence and reproduction

[verify.py](verify.py) authenticates the three predecessor inputs in
[SOURCE-PINS.json](SOURCE-PINS.json) by SHA256 and Git blob and compiles
those exact bytes, without cached predecessor bytecode. It reproduces
[RESULT.json](RESULT.json), covering:

- All **16,384** padded tuples for moduli `(5,7,11,13)` and widths
  `(3,3,4,4)`, including all **5,005** globally valid tuples, two tree
  levels and genuinely mixed simultaneous target heights.
- All **64** tuples with moduli `(5,3)` and wider declared widths
  `(3,3)`, retaining dirty values beyond the minimal target table.
  Supplied ell=4 deliberately makes every axis short; its two idle
  rows remain present rather than normalizing ell down to max width.
- All **32** tuples with moduli `(7,3)` and widths `(3,2)`, binding
  the microscopic invalid-target mutation to a genuine CRT caller.
- Whole forward/inverse source comparisons, both inverse compositions,
  distinct destinations covering each full rectangle, actual-row target
  omission toggles and literal idle checks. Decoder checks cover
  ell=2 through16; the written proof is quantified for all ell>=2.

The main mutation returns `(1,3)` instead of `(1,2)` when it incorrectly
disables a micro-switch after the target temporarily becomes invalid.
Another witness prevents claiming that all globally invalid tuples
are pointwise fixed. Input controls reject malformed width, row,
axis-count, coprimality and strict-padding declarations. The minimal-width
compiled source helper is used only within its own width domain;
its wider-input failure is documented as a finite API boundary.

Python 3.12, standard library only, from the repository root:

```sh
python3.12 -I -B research/crt-mixed-width-caller/verify.py
python3.12 -I -O -W error -B research/crt-mixed-width-caller/verify.py
```

Default verification reproduces and compares the stored receipt without
rewriting it. `--write-result` explicitly regenerates it. All checks
remain active under optimized Python.

## Open next questions

Bind the decoded rows and explicit declared widths to the full uniform
control evaluator, including CRT reconstruction/modular inverses,
transported split-axis descriptors, current intermediate states,
cleanup and head returns. The earlier sequential Beneš component
addresses one part of that tariff; this host caller does not price it.

The fixtures use canonical logical axes, without executing reservoir
placement, compact repair or an ordinary interchange. No tape/E tariff,
full physical CRT implementation, precision/native/outer theorem or
new kappa is claimed. The selected frontier is unchanged.

## Credit

Cinna Davis supplies PR4100's CRT/network construction. Hiroki
KUMAZAKI (@kumagi), PR4169/4174, supplies the existing arbitrary-source
inverse/omission and reservoir/descriptor audits. Douglas Colkitt,
OpenAI and the retained routing/compact-control lineage keep their
predecessor credit; the pinned NOTICE preserves the source details.
New work is the explicit row/idle/declared-width caller binding and
its independent corroboration. Prepared with substantial OpenAI Codex
assistance. Apache-2.0. No independent human review or proof-assistant
formalization is claimed.
