# Validation

Complete registered replay passed on Python3.12.14 at `f0625d20bcc175e0865d1d5cf3f7852fe2287679` on2026-10-19: the full producer reconstruction, independent dense/native replay, seeded word, pressure proof, independent ring/fresh-path reconstruction, and controls. The later publication commit adds the final integrity review and this record; scientific code, adapters, frozen inputs and registration remain unchanged.

```sh
python3.12 -B scripts/research_package.py --package research/r429-full-target-interface
```

The retained full log SHA256 is `664412ad94dfda752def14082f78c0ee3a0f5c2b5e9eb5ad9bfabd4be96b4da0`. Every field of all five scientific receipts and every regenerated word byte is compared. The historical gzip container hash is preserved provenance; regenerated compression differences are accepted only when decompressed bytes match exactly.

Independent native and caller checkers also passed normal and optimized standalone runs. Source controls passed both modes through the actual repository launcher's private cache prefix, including nested poisoned-cache rejection. Nineteen input/origin bindings and the complete stdlib import closure were independently reviewed. The two historical prose/comment corrections are explicit and do not change mathematics.

This finite replay and the written conditional all-L caller proof are separate from source-history availability, exported-byte controls and automatic hosted CI. The PR records exact-head CI when available. No human peer review, formal-kernel proof or full native supplier admission is claimed.
