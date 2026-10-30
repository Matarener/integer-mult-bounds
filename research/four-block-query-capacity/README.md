# Four bounded-rank queries have exact capacity 2 floor(4r/3)

This contribution was produced by Nick Petalas. Apache-2.0.

**Scoped proof with finite corroboration; no new κ.** Over any field of
characteristic two, let Q be a central formal involution. Allow arbitrary free
constant invertible bases and paid operations I+Q N with N²=0 and rank N≤r,
on exactly n independent coordinates with no auxiliary workspace. Then

```text
Q I_n is attainable in at most four paid calls
    if and only if n is even and n ≤ 2 floor(4r/3).
```

The least maximum paid rank at even n is ceil(3n/8). Every successful word has
total paid rank at least 3n/2, and an explicit balanced schedule attains both
minima. Four rank-two queries cannot twist six coordinates. Four rank-three
queries do twist eight coordinates. The proof permits scalar mixing across
all coordinates; it is not limited to separate-port lower bounds.

[PROOF.md](PROOF.md) gives the quantified argument and constructor. The new
step factors the query Gram complement, then applies rank subadditivity to
its four complementary block idempotents. This strengthens the elementary
n≤3r capacity bound. The construction distributes three-query two-coordinate
exchange words over four positions, omitting a different position for each pair.

The question comes from Matarener's [PR #6114, Open next question 1](https://github.com/CrocSwap/integer-mult-bounds/pull/6114).
Credit Cinna Davis / 1337isnot1337 for the minimum-query simplex and controller
lineage, Ali Romman for [PR #5617's coupled-port Gram framework](https://github.com/CrocSwap/integer-mult-bounds/pull/5617),
and the retained native/caller contributors credited in their sources.
Their results are cited as predecessors, without replaying their evidence.
The two merged proof documents are pinned as historical provenance in
SOURCES.json. Pending #6114 is bibliographic context, not a runtime dependency.

## Reproduce

From the repository root, using the interpreter used for local checks:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/four-block-query-capacity/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/four-block-query-capacity/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/four-block-query-capacity
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/four-block-query-capacity --check-source-history
```

Elsewhere use a CPython 3.12 path. The verifier uses only the standard library,
imports no repository engine, reads no predecessor data and writes no files.
It emits `PASS_FOUR_BLOCK_QUERY_CAPACITY` and a generated JSON receipt bound
to SHA256 hashes of its package files. No receipt is handwritten.

The direct check constructs 392 feasible instances for rank caps 1 through 24,
checks 17,696 original coefficient columns, checks 170 Gram factorizations
and four mixed-basis witnesses, and runs ten rejecting controls. It also
enumerates all 16, 512 and 65,536 binary matrices in dimensions two, three
and four. The square-zero counts by rank are respectively [1,3], [1,21]
and [1,105,210]. All pair sums decide the corresponding four-summand feasibility
questions. These finite checks corroborate the written proof.

## Verifier bounds

The executable fixes rank caps at 24 and dimensions at 64. Gram checks use
dimension at most 16, hence total rank at most 24. Exhaustion stops at 65,536
matrices; pair-sum sets have at most 65,536 entries. Every loop is bounded by
these limits or a fixed four-call word, and the checker uses no recursion or
subprocesses. Python allocates dynamic objects; this is a managed-runtime
deviation from fixed-allocation guidance, with the live collections bounded
by those constants. Package hashing reads at most sixteen local files.
Warning-strict normal and optimized runs are registered; all mathematical
checks use explicit exceptions and remain active with assertions disabled.

## Limitations

This is an abstract algebraic interface result, not a finite multiplication
certificate or a complete multiplication theorem. A higher-rank query still
needs a legal physical native realization, arbitrary-input and helper contracts,
paid scalar bases, restoration, and a favorable complete signed invoice.
Constant bases are granted for free only in the theorem's declared model.

The theorem does not cover extra clean or dirty workspace, characteristic zero,
an infinite-order Q, non-square-zero paid matrices, independent stage variables
or nonconstant free maps. No selected supplier replay, full framework proof,
physical implementation, outer-ledger change or proof-kernel check was run.
Independent human and formal proof-kernel review are unclaimed.

## Open next questions

- Can a physically legal multi-bank native job realize the rank-three query in
  the eight-dimensional four-call construction? Begin with its four explicit
  shear blocks and specify all returned helpers and actual paid ranks. A native
  realization and complete signed invoice remain missing.
- What is the exact capacity at six or more calls in this same model? Begin with
  the Gram complement and attainable omission schedules. This package stops at
  four calls; it supplies no theorem for that larger domain.

Structured relevance, first steps and blockers are in TASK.json. This changes
rather than completes the original card's physical consumer/invoice assignment.
