# Aggregate padding on twelve tapes

A new two-phase counter construction reduces ywz65's
[PR #2636](https://github.com/CrocSwap/integer-mult-bounds/pull/2636)
five-coordinate padding/restriction interface from seventeen tapes to twelve.
Mutable counter contents decrease from 2D cells to D, where D is the sum of
the descriptor widths. The complete scan has the uniform sufficient action bound

```text
192N + 16D + 80,
```

including initialization, payload traffic, all head returns and zero-counter
cleanup. N is the binary-padded rectangle volume. This is a scoped constructive
proof with finite corroboration, produced by Nick Petalas. No new kappa is claimed.

The immutable q-1 descriptor supplies both countdowns. First count the q genuine
positions. Then load its fixed-width bitwise complement R-q and count the padding
positions using the same physical counter. Zero padding length carries immediately.
The singleton case uses an empty counter. No new descriptor or decoded coordinate
is needed. [PROOF.md](PROOF.md) proves correctness, ownership and the action bound.

The comparison uses the predecessor's stated 17-tape, 2D-cell and
1024N+128D+128 contract as a cited premise. Its verifier and scientific counts
are not replayed. The new machine and independent mixed-radix oracle are standalone.
The result is neither a minimum-tape theorem nor a wall-clock performance claim.

## Reproduction

From the repository root, with the standard-library CPython 3.12 interpreter:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/single-counter-aggregate-padding/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/single-counter-aggregate-padding/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/single-counter-aggregate-padding
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/single-counter-aggregate-padding --check-source-history
```

Another CPython 3.12 path may replace the local path. The direct command also
runs from a Git-free package directory. Expected marker:
`PASS_SINGLE_COUNTER_AGGREGATE_PADDING`. The verifier prints a generated receipt
bound to all package file hashes; it writes nothing.

Evidence covers 516 full scan cases, 1300 exhaustive payload scans, 257 complete
coordinate cycles and thirteen rejection/mutation controls. Every successful
scan checks the independent payload oracle, all twelve physical heads, immutable
input/descriptors, protected boundaries, D zero counter cells, and the complete
action bound. Restriction tests include arbitrary nonzero discarded padding.
Finite cases corroborate the uniform written proof; they do not prove it by
extrapolation. Warning-strict normal and optimized checks are registered.

## Scope and provenance

Canonical base is `721c03822c421b7f7fcbb2598993b947c4d88419`, priority revision 8.
The selected metadata baseline passed at kappa 0.003125804. The task explicitly
changes `uniform-transfer-audit` to this local physical-resource construction,
relevant to the `precision_tape` and `owned_erasure` interfaces. No complete
selected assumption is discharged. [TASK.json](TASK.json) records that change;
[SOURCES.json](SOURCES.json) retains exact predecessor and catalogue provenance.

The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19246892)
reserves the same one-counter construction. Live open PRs, recent account work,
handoffs and local locks were checked before claiming. Searches of main README
text and merged PRs included the general five-coordinate, one-counter and
two-phase forms. Cached overlap covered 407 open PRs and 5818 Discussion records;
its sparse local text coverage was 70/8348 notes. Relevant source and adjacent
padding packages were separately read. These are bounded overlap checks, not
a literature-wide novelty guarantee.

The source is ywz65's PR2636, retained at
`c1e173b7af38603bc7660a8829e75006e93645d3`. PR2457 supplies aggregate-before-padding;
commdata2338's PR2399, Jose Manuel's PR2234 and Adam Gall's PR2087 retain the
preceding descriptor, parking and supplier credit. Binary countdown amortization
and complement arithmetic are classical. The new contribution is their shared
physical counter, successful ownership contract and complete uniform bound.
All predecessor files and credit lines retain their bytes. Apache-2.0.

## Limitations

Canonical descriptors, owned zero counters and fresh output are inputs. Descriptor
production, allocation, ancestor parking, the completed fast callee and selected
caller integration remain external. Successful well-formed entries are covered;
malformed calls need not restore state. No compiled transition table, physical
allocator, all-size supplier admission, stock/precision theorem, selected scientific
cold replay, Lean or Docker run is supplied. Independent human and formal
proof-kernel review are unclaimed.

## Open next questions

- Can an actual completed exchange use the twelve-tape scan within its fixed
  tape inventory? Start at PR2457's complete callee boundary and count its
  simultaneous tapes, payload intervals, head returns and ancestor parking.
  The actual callee/ownership interface remains the blocker.
- Can one shared physical work tape hold several coordinate counters while
  retaining linear complete movement? Start with two unequal widths and include
  travel between their delimiters. The present proof relies on separate heads
  and gives no such serialization bound.
