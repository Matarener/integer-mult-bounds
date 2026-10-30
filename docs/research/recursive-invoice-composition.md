# Add complete component invoices

If a linear relaxation selects component multiplicities, use the
[exact LP certificate checker](rational-lp-certificates.md) to replay its bounds.

Use positive integer multiplicities to add invoices with the same declared
contract. For example, add three copies of A and two copies of B:

```sh
python3 -B scripts/combine_recursive_invoices.py \
  --term 3 A.json --term 2 B.json > combined.json 2> combined-receipt.json
python3 -B scripts/compare_recursive_invoices.py OLD.json combined.json
```

Standard output is an ordinary invoice for the existing comparator. Standard
error holds a JSON receipt with each source hash, multiplicity, output byte count
and output hash. Keep both files and check the command exit code. On a validation
error the tool exits 2 and emits no invoice; standard error then holds the error,
not a receipt. Shell redirection can still create an empty output file.

When components share a fixed source inventory, use the
[identity-preserving assembler](invoice-inventory-assembly.md) to reject omitted
items and duplicate credits before adding their bills.

For each rank and each side, the result is the sum of multiplicity times count.
Paid jobs and target credits stay separate. Repeating a file twice has the same
arithmetic result as adding its multiplicities. Inputs are read and hashed once
per listed term; the tool does not modify them. Output uses exact UTF-8 bytes
with LF newlines, so the receipt hash also works on Windows.

All contracts must match. A matching declaration does not prove that components
have disjoint lifetimes, independent targets or compatible native boundaries.

For fixed helper lifetimes, the [minimum-pool allocator](helper-lifetime-allocation.md)
constructs a slot map and checks a matching lower-bound witness.

Charge shared adapters, restoration, routes and compiler work in the complete
construction bill. Do not add claimed κ values or count the same target twice.

The tool accepts at most 128 terms. Multiplicities are integers in `1..10^60`.
The combined invoice must satisfy the same count, support and rank limits as each
input. It never truncates a count or drops a target to make the result fit.

This is exact histogram arithmetic, not a new construction or theorem. Credit
the existing signed-invoice comparator, mightyOil's T16 moment-order audit and
their retained predecessors for the schema and accounting context. Prepared for
aliromman with OpenAI Codex assistance. Apache-2.0.

To replace paid jobs with an inner construction, use
[matched-target substitution](recursive-invoice-substitution.md). It consumes
the serviced target, retains other credits and requires an explicit fee bill.
