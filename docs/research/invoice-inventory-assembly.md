# Assemble a complete invoice without losing item identities

Use a fixed source inventory when several components share one bill. The tool
requires every inventory item to be assigned exactly once in total. It rejects
omissions, excess use, unknown items, and changed source bytes before it emits
an invoice. Paid and target identities remain separate throughout assembly.

```sh
python3 -B scripts/assemble_recursive_inventory.py INVENTORY.json ASSIGNMENT.json \
  --source word WORD.json --source controller CONTROLLER.json \
  > invoice.json 2> receipt.json
```

The inventory has schema `integer-mult-invoice-inventory/v1`, the ordinary invoice
`contract`, a `sources` object from names to SHA-256 hashes, and `items`. Each item
has a unique `id`, a pinned `source` name, `side` (`paid` or `targets`), integer
`rank`, and positive integer `count`. Use the same stable ID for the same source
occurrence. Do not give one physical target several IDs.

The assignment has schema `integer-mult-invoice-assignment/v1` and a `components`
object. Each named component has a list of `{ "id": ..., "count": ... }` claims.
A component cannot repeat an ID; combine its counts explicitly. Different
components can divide an aggregate item count, but their total must equal the
inventory count. No component can change an item's side, rank, or source.

For example, two target items A and B can both have rank four. Assigning A twice
and omitting B gives the expected aggregate histogram `{4:2}`, but is wrong by
identity. This checker rejects it. Aggregate invoice comparison alone cannot
detect that error.

Standard output is an ordinary invoice for the existing comparison tools.
Standard error is a receipt with exact input/source/output byte hashes, coverage
counts, and each component invoice. Check the exit code and retain both files.
Invalid input exits 2 without an invoice; standard error then contains an error.

The proof is integer conservation. For every ID, assigned counts are positive,
never exceed its declared count, and finally equal it. The tool then sums those
same assigned counts by side and rank. Thus the component sum equals the complete
declared inventory, without any implicit target credit or missing declared item.

## Frozen selected-bill example

`tests/fixtures/invoice-ledger-selected5599/RESULT.json` is an exact copy of
`research/p104-helper-subspace-splits/RESULT.json` at main commit
`de5ec2e7a6074068452f45b1a191b5c72832df4a`. Its SHA-256 is
`1d92e587915052110dfb3aca8890df5afdaf496164efa5a4a52e69ceeb3c70f3`.
The adjacent inventory groups literal receipt fields into local paid work,
local helper targets, query work, whole idles, and main targets. Local counts
are multiplied by `full_forward_calls`; query count is `query_shears * ports`.
The assignment builds these five components and reproduces all 66,726 paid jobs
and 13,048 target credits in `complete_cost`. These are aggregate identities,
not separate event-level source witnesses.

Limits: 16 sources, 64 MiB per source, 16,384 inventory items, 128 components,
65,536 assignments, 8 MiB per JSON input, and ordinary invoice count limits.
Sources are streamed for hashing. No source program is executed.

## Open next questions

Generate stable item IDs directly from checked source events. Independently
prove that the inventory includes all fees and contains only independent target
credits. Hashes authenticate bytes, not those semantics. This checker does not
replace the selected source exporter, native replay, compiler proof, or κ review.

Credits: zxv's invoice interface; Pierre-Loic Doulcet's P104 word; Ali Romman's
complete caller and helper accounting; Cinna Davis's controller; Jacob Alan
Sussman's productive recursion; and retained predecessors. Prepared for Ali
Romman with OpenAI Codex assistance. Apache-2.0.
