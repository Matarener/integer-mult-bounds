# Encoded physical sparse XOR batch

I implement one simultaneous XOR batch from a borrowed encoded list of
source/target bit positions. I use fixed fields `(u,t,y,b)`, preserve complete
opaque Gaussian records and borrowed inputs, restore dirty controls and
non-target bits, and return a protected output with owned work erased.

The previous physical Compact controller advances its selected positions by
a uniform stride. I now read distinct source positions and disjoint target
guards from one tape. Sources may lie inside guards. I execute twelve B1
interchanges and ten rotations per complete row, followed by full exceptional
repair. I omit the older controller's extra highest-bit operation.

Under the retained ordinary/source premises, I prove the complete invoice

    12 K_q V(1+H^tau) + O(V + M A^6 + delta M A(R+A)),
    tau=332353/332929,
    delta=min(1,k(2/2^G+8*2^G/2^K)).

I define the actual input lengths and fixed-tape bound in [PROOF.md](PROOF.md).
With its finite guard and actual long-record domain, I obtain
`O(V(1+H^tau))` time and `O(V)+F_q` space. I charge the interchanges at the
supplied width H, including inactive high digits. I retain the source-admissible
q, completed ordinary and physical-refinement assumptions.

PR1673 already supplies the unequal-gap algebra. My contribution is the
encoded pair-list lowering, physical return and resource argument. I do not
provide full reservoir placement, matching/color scheduling, a complete
support router or an enclosing multiplication theorem.

## Interface and replay

Use one cold process and keep `sparse_sources.opened()` active for construction
and invocation. Within that cohort, construct `SparseEngine(native)` with a
fresh admitted Ordinary using `Profile(1,577)`. The source loader compares all
23 backend files with the retained rate proof before enabling the new code.

The run signature is

```python
engine.run(payload, widths, pairs, pair_count, position_bits,
           K, G, record_bits, outer_rows)
```

Supply a fixed four-element tuple of Count widths, one borrowed binary pair
tape, and canonical Count parameters. Encode each pair as source then target,
each in exactly `position_bits=max(1,ceil(log2 N))` least-significant-first
bits. End the tape after the last pair. Supply heads at their origins. Consume
the returned output before reuse. I retain the successful-admitted-execution
contract and the maximum-preceding-extent qualification for backing storage.

With Python 3.12 and the standard library:

```sh
python3.12 -B scripts/research_package.py --package research/physical-sparse-xor-batch
```

For an official committed export outside Git, run each declared `VERIFY.json`
command from its extraction root. The two retained exports and routing
references supply the transitive runtime/proof inputs without network access.
I record finite execution, negative controls and limitations in
[EVIDENCE.md](EVIDENCE.md).

## Open next questions

Can a complete arbitrary-support router use this batch with a paid reservoir
and matching/color schedule? Start by choosing the reservoirs before coloring,
recomputing pair positions after placement, and charging H for each batch.
Implement that scheduler and its exposure/inverse before applying the global
support bound to a physical caller. I have implemented the batch after placement.

Can the resulting router share one authenticated runtime cohort with the
[PR3599 actual-width T74 root](https://github.com/CrocSwap/integer-mult-bounds/pull/3599)?
Start with one complete exposed packet, preserve actual long records, and
restore the original address interpretation. The combined root/router factory,
outer error/packing argument and inherited scientific review remain open.

## Sources and attribution

I start from canonical main `20ecf2891d80b5acf18d980b2164fb44ea7faa90`, priority
revision 6. I coordinate in the existing
[T74 investigation](https://github.com/CrocSwap/integer-mult-bounds/discussions/2612#discussioncomment-19009513).

Jose Manuel (`jmbarrancoml`), with substantial OpenAI Codex assistance in
mathematics, implementation, verification and source analysis. Apache-2.0.
I claim no independent human or formal-kernel review and leave the selected
frontier unchanged.

I retain Douglas Colkitt's compact construction and the notices in PR2250;
Vlado Vojdanovski's PR1673 unequal-gap and support-router arguments;
Jose Manuel's PR3055 physical Compact and PR3562 ordinary-rate proof;
David Arias, Nick Petalas, Adam Gall and the remaining native/borrowing lineage
inside those exports. Hiroki Kumazaki's PR3576 records concurrent retuned
factory work. Nick Petalas's PR3581 proves a B1-only materialized-exposure
obstruction; I use the richer controlled-rotation/repair alphabet and retain
its complete charges.
