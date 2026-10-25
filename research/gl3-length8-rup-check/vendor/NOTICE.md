# Vendored files

Byte-identical copies from
[PR #4331](https://github.com/CrocSwap/integer-mult-bounds/pull/4331) at head
`08be02a3141f773c7d73faf344db7c45dfb9110d`, under
`research/gl3-lrat-independent-check/source/`. They are copied because that head is not
reachable from canonical main. `verify.py` checks their SHA256 values, and the CNF and
proof hashes against `CERTIFICATES.json`.

| Vendored file | Git blob |
| --- | --- |
| `length7.cnf` | `729d0117e352bbab6205c64473303629f138ceed` |
| `length7.rup.gz` | `367a877e42af51923c9818380b1c410ecfa7ce63` |
| `CERTIFICATES.json` | `75af63d806197aa9a6d4caf57b8a9e5d811ee26c` |

The length-eight inputs are **not** vendored (33 MB). They are the same PR's
`length8.cnf` (blob `2c2866e55fe4487c98ec3dfe81c99c4a5b33b7c9`) and `length8.rup.gz`
(blob `aaa09a8243e32f2eaefc8b572b965216ceccb0f2`), pinned here by the SHA256 values in
`CERTIFICATES.json`.

The encodings, certificates and proofs are Brian Ross's lineage (with OpenAI Codex
assistance), retained by ToikY in #4331 under their stated licenses.
