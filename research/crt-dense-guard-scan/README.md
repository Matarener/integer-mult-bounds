# Literal CRT dense guard-mask scan

This package lowers the ordered scan already proposed in
[`CRT.md:238-253`](../unconditional-batched-crt/CRT.md) to a marker-driven
three-tape program. From an **admitted ordered stencil** of L fixed-alphabet
cells it writes the complete `M=2^L`-bit bad-address mask, preserves the
stencil, blanks all private work and returns every head. All padded address
bits are enumerated; inactive control bits, target parity and spectators
remain unconstrained when marked SKIP.

The exact normal-program census is `8ML+15M+13L+18` cell/head actions and
`M+2L+6` visited cells, including input, output and markers. This gives
`O(ML)` time and `O(M+L)` space with three fixed tape roles and finite control.
Under the source's `L=Theta(p), R=Theta(p), V=MR`, the detector is `O(V)`.
Geometry-to-stencil production and admission remain explicit **unpriced**
dependencies. No complete caller or new kappa result is claimed.

`machine.py` is the literal cell/head program. It neither reads a host
length/address/head coordinate nor calls a predicate/E callback. Its emulator
uses numerical coordinates and action totals solely as observers. The stencil
alphabet packs kind, interval boundaries and two threshold bits in one fixed
product alphabet. `PROOF.md` proves enumeration, MSB comparison, cleanup and
the exact census, and separates this supplied-stencil interface from the
unimplemented geometry producer. The permanent left sentinels belong to the
initial tape infrastructure; cleanup restores blank data and erases the
private right marker while retaining those sentinels.

Run from the repository root with Python 3.12 and the pinned sources present:

```
python3 -I -B research/crt-dense-guard-scan/verify.py
python3 -I -O -W error -B research/crt-dense-guard-scan/verify.py
```

Both commands authenticate the three source files against `SOURCE-PINS.json`
and compare a fresh replay with `RESULT.json`; they do not rewrite it.
`--write-result` explicitly regenerates the receipt. The package uses only the
Python standard library and explicit checks that remain active under `-O`.

Executed source binding exhausts 49,408 addresses in three predicate-projection
fixtures, rather than claiming a full production reservoir invocation:

| G | H | Y | K | target positions | back SKIP bits | addresses | good |
|---:|---:|---:|---:|---|---:|---:|---:|
| 1 | 2 | 10 | 5 | 0,5 | 0 | 16,384 | 256 |
| 2 | 3 | 9 | 7 | 1 | 0 | 32,768 | 13,824 |
| 1 | 1 | 5 | 5 | 0 | 1 | 256 | 32 |

Every output bit is compared with both retained `good` and `linear_guard`.
All-SKIP L=1..3 fixtures exercise the smallest complete counters. Mutations
detect wrong lower/upper strictness, wrong MSB significance, a whole-K guard
with unadjusted K-1-bit thresholds, omitted counter low bit and omitted owned
output return. Malformed geometry/stencil rejection tests belong to the
unpriced host admission adapter. Semantic/source comparisons, observer totals
and hashes are verification work, not hidden runtime registers or steps.

Cinna Davis already supplied the predicate and ordered-scan proposal.
Hiroki KUMAZAKI (@kumagi), PR4169 and PR4174, supplied arbitrary-source repair
and reservoir/descriptor audits; those open PRs are credited, not imported.
Douglas Colkitt/OpenAI's stream and compact-control framework and the pinned
source NOTICE retain their ancestry. This contribution is the literal
lowering and quantitative audit, with substantial OpenAI Codex assistance,
Apache-2.0. No independent human or new formal-kernel review is claimed.

## Open next questions

The next obligation is a uniformly encoded, charged geometry/threshold
producer and admission path at the transported caller. Extraction, sorting,
repair, payload routing, full E evaluation, ordinary callees, precision,
native/outer composition and the selected frontier are outside this result.
