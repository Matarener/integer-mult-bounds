# Vendored files

Byte-identical copies. They are copied, not pinned, because these PR heads are not
reachable from canonical main. `verify.py` checks their SHA256 values before use.

| Vendored file | Source | Head | Git blob |
| --- | --- | --- | --- |
| `pr4263-witnesses.json` | [#4263](https://github.com/CrocSwap/integer-mult-bounds/pull/4263) `research/depth4-chain-connector/witnesses.json` | `2183322b32a5975ecb4a6aec2ec8f43ac08b1aec` | `9ed64a2d86c108fdc9f11844c073e17805b6053f` |
| `pr4280-witnesses.json` | [#4280](https://github.com/CrocSwap/integer-mult-bounds/pull/4280) `research/depth4-chain-rowmodel/witnesses.json` | `cf55a416933c298f6230080ce110c3ad0dd6e66a` | `535fc4bd8b000cd706c8e50183f2c80d836fa288` |

Both are Nick Petalas's (Apache-2.0, as those packages state). The (6, 5) depth-three word
is quoted from #4249's PROOF.md at head `03b8a19d7442edebb3565064631f6ca2408d731e`.
