# Literal raw CRT shuttle to the binary callee

The actual `Raw.shuttle` owner uses numeric LEFT/BLANK framing, while the
completed binary elementary interchange expects aligned three-bit ports.
This package supplies the paid literal bridge: encode payload and descriptors,
initialize and dispatch the existing binary program, install its output,
decode into the same raw owner, and retire every encoded bank.

The29 fixed roles include RAW, both actual u/t descriptor banks and20 encoded
callee roles. Runtime instructions are only local tests/writes, unit moves,
fixed jumps and halts. No host encoder, decoder, transpose or allocation callback
survives. The binary child uses {raw BLANK4,ONE1}; the enclosing caller remains
explicitly five-symbol. [PROOF.md](PROOF.md) states the all-width port contract,
complete instruction tariff and retained-bank proof.

The source initializer constants are extracted from unchanged Raw code:
u=(2,1,1024,12), t=(2,4,256,12), each196608 payload bits. Their eight raw
words are literally initialized/retired at costs281/389 instructions.
Each separate actual call has3,146,057 retained cells including raw input and
both descriptor banks. A shared u→t history requires3,146,075 cells: the extra18
falsify max-of-standalone-total accounting. The t history figure is derived
from the source per-role theorem; FULL.json records the historical actual u execution; the publication refresh
replays only the light checks and preserves that receipt unchanged.

Small tests include H0 identity, growing/shrinking histories, all16 independent
H2 columns, a separately written sparse interpreter, exact retained capacities,
wrong decoded-bit and missing-install controls. Default replay is read-only;
`--write` authors only a missing typed receipt. Source and receipt corruption
controls remain effective with assertions disabled.

```sh
python3.12 -B scripts/research_package.py --package research/raw-crt-binary-shuttle-bridge --check-only
python3.12 -I -B research/raw-crt-binary-shuttle-bridge/verify.py
python3.12 -I -O -B research/raw-crt-binary-shuttle-bridge/verify.py
# Source-sized science needs a reserved heavy slot:
python3.12 -I -B research/raw-crt-binary-shuttle-bridge/verify.py --full
```

This is an executable replacement call boundary, not a patch to the original
Raw class or a complete twelve-shuttle/rotation/ROM/repair execution. Upstream
payload production, full binary caller lowering, global allocation, native
supplier, precision and outer multiplication remain outside scope. No recursive
invoice/frontier changes or new κ. Error rollback is not promised.

## Open next questions

Compose one remaining literal raw rotation/current-y ROM boundary on these
actual owners, with complete production and restoration costs. The current
source raw word is not fully lowered. A whole two-symbol implementation also
needs its upstream raw/ROM representation and stock invoice; the child-only
binary theorem does not provide those. Structured questions are in TASK.json.

## Credit

JoyboyBrian with substantial OpenAI Codex assistance; Apache-2.0.
Jose Manuel and retained PR2809/2753 authors supply the elementary lineage;
JoyboyBrian/PR5162/5188 supply raw and literal sources; Ali Romman supplies
binary lowering; Hiroki KUMAZAKI/PR5286 supplies retained backing. Cinna Davis,
Hiroki KUMAZAKI, Douglas Colkitt/OpenAI and retained notices retain CRT credit.
All original sources remain unchanged. No human or formal-kernel acceptance.

[Resumed canonical claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/4709#discussioncomment-19233740);
[original released claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/4709#discussioncomment-19173365).

Publication was resumed on canonical main
`721c03822c421b7f7fcbb2598993b947c4d88419`, priority revision8, selected
PR6030. All eight live scientific inputs are unchanged. The original revision7
card and source pins remain frozen; this result makes no claim about the new
selected construction. The registered hook includes the source-sized `--full`
command and will require its separate resource budget when run in hosted CI.
