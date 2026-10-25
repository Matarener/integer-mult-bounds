# First F0 Gaussian caller: exact admission contract and same-grid obstruction

The first rank-positive child in the literal F0 retained core is zero-based
event **9894**, `['climb','A',546,0,4,1]`: ordinary dirty helper **L546**, frame I
to the frame with axis `[459]`. The preceding 9,894 events do not write it.
This audit binds that actual caller to the arithmetic premises of upstream
[PR3884](https://github.com/CrocSwap/integer-mult-bounds/pull/3884)'s six-tape kernel.

**Exact obstruction:** the arbitrary-helper source contract does not admit
unconditional substitution on the helper's unchanged input grid. A valid
nonconstant real impulse in L546 reaches the child unchanged. The actual recipe
returns `(1+i)/2` at address 0 and `(-1-i)/2` at address 459. The first axis has
odd numerators, and the byte-exact tape program rejects with `nonexact half`.
Increasing the magnitude width does not repair this parity failure.

The exact same-grid divisibility domain is one even-parity condition on the
four real/imaginary mantissas of each coordinate pair, after the right monomial.
On the 512-coordinate native slice this is an index-2^256 sublattice of Z^1024.
One extra fractional bit is necessary and sufficient for this rank-one child's
arithmetic at lambda=1. For original component bound M>=1, a sufficient signed
width is `bit_length(M)+4`. [PROOF.md](PROOF.md) gives the argument and scope.

**This is not an obstruction to the already finer PR3303 format.** Its proposed
quantum at lambda=1 is `h*2^-71`, with width `P+215`, for original components in
`h Z` with magnitude below `2^P h`. L546 is unchanged, so its entry mantissas
in that format have 71 trailing zero bits. Its first-axis numerators are even
and fit that width. That arithmetic implication is checked separately here.
Supplying the original bounded entry grid and a physical implementation of
that format remain premises of PR3303, not established caller allocations.

The native computation here uses one 512-coordinate nine-axis slice, with
identity spectator coordinates fixed. This slice suffices to falsify universal
same-grid admission. The full producer has N=2^(73*lambda) coordinates per owner;
the slice is not a full payload execution or its physical cost bill.

## Connection and cost ledger

| Obligation | Evidence / status |
| --- | --- |
| Actual event and next instruction | Bound to event 9894 / L546 / frame 0 to 4; next is `L546 -= L561` in frame 4. |
| Reachable nonconstant helper | Entire literal prefix replayed exactly; no target writes; its helper adapter at event 7948 is identity under the pinned native semantics. |
| Unchanged original-grid arithmetic | **Fails** without the exact parity restriction above. |
| One-bit finer-grid arithmetic | Sufficient under explicit component bound M and width; preparation is an unmetered fixture, not a physical adapter implementation. |
| Existing PR3303 finer format | Conditional first-child parity/range implication checked; caller admission and the full predecessor theorem are not inferred. |
| Two data windows | Logical mutable helper named; physical intervals, head origins and encoding are **unknown**. |
| Four disposable scratch windows | Last-write CLEARs prove C0..C7 zero, with no remaining retained-core scalar access. Four component half-slices of C0/C1 are a legal **abstract** scratch candidate; six separate physical tapes, origins and paid access remain unbound. |
| Kernel on supplied windows | Credited exact tariff READ=6NW, WRITE=6NW, MOVE=20NW. A successful N=512, W=5 fixture costs 81,920 cell actions. |
| Input layout, right/left monomials, grid conversion, address/control | Arithmetic checked where stated; physical charges **unknown**. |
| Adjacent ADD, helper return, F17 consumer, full recursive bill | **Unknown**; a single child changes frame and does not discharge the whole caller's borrowed-helper return. |

**No fully costed physical connection is established.** The precise obstruction
is to unconditional unchanged-grid substitution; a preallocated finer grid
escapes it. The audit narrows and stops here. Unknown costs are not zero.
Out-of-contract rejection is not a nondestructive scan: scratch packing precedes
the parity check. Evenness also does not guarantee range: numerator +8 in signed
four-bit execution gives -4 instead of the correct +4; the wider control works.

## Reproduction and evidence

Python 3.12+, standard library only, from the repository root:

```sh
python3 -I -Werror -B research/qq16-f0-first-caller/verify.py
python3 -I -O -Werror -B research/qq16-f0-first-caller/test_verify.py
python3 -B scripts/research_package.py --package research/qq16-f0-first-caller
```

The verifier compares every field of committed RESULT.json, authenticates the
inputs before use, replays the full witness prefix, checks all 1,024 Gaussian
basis columns of the actual native recipe, all 16 pair parity classes, and 20
dense signed tape/native cases at widths 5 through 68. Successful tape controls
check values, scratch cleanup, head returns, exterior sentinels and exact counts.
Tests add 81 independently calculated signed pairs, source/recipe/prefix/receipt
corruptions, unchanged-grid width controls, overflow and borrowed-scratch rejection.
`--write-result` explicitly regenerates only this package's receipt. Ordinary
verification is read-only. See VERIFICATION.json for actual runs and environments.

Canonical/scientific base `20ecf2891d80b5acf18d980b2164fb44ea7faa90`, priority
revision 6. The draft source-binding head was `653366fcee6d7574db15a92e250c64e88a7133be`;
its successful hosted Python 3.12 replay was inspected, separately from the new
checks. No complete F0/B1, all-size, physical, selected cold, Lean or human review
is claimed. No supplier admission, new kappa or selected-frontier change follows.

## Provenance and coordination

Explicit continuation of [fork PR10](https://github.com/Clear1nsight/integer-mult-bounds/pull/10)
and PR3884; no random card drawn. Current canonical AGENTS.md, autoresearch.md,
CONTRIBUTING.md, revision-6 priorities, family gate and selected record were read.
Live QQ16 PR bodies, Discussion index and the original
[handoff](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166?sort=new#discussioncomment-19030049)
were checked. The overlap helper reported missing remote coverage because `gh`
is absent; connector/browser checks supplement it without exhaustive coverage.
Canonical QQ16 package READMEs were also searched for this exact event, L546,
first-caller and six-tape terms; that does not search every nested proof or diff.

`vendor/tapes.py` is byte-identical to PR3884 head
`2be0f348b79f58073b7eb3ce568b9e4db6e0426f`, with its original notice retained.
Its SHA256 is checked before compilation. This retained export avoids needing
an unmerged predecessor commit in a cold checkout; the generic Git-history
checker alone does not authenticate that external origin. Canonical live inputs
are pinned in SOURCES.json and declared in VERIFY.json. Frozen inputs are unchanged.

Credit Ali Romman and the retained QQ16/native lineage; Douglas Colkitt's
joint-query source and arbitrary-helper contract; Nick Petalas PR3270/3303 for
the existing sufficient numerical formats; Tekalign PR3017 for exact native
vectors; Sricharan Vagvala for native rounded-components event semantics; ToikY
PR3652 and PR3671 for source/output conventions; Sagar Thakrar PR3241/3377 and
Dugongue PR3394 for distinct physical boundaries. PR3181's interior grid work
and PR3908's reported consumer-budget obstruction are adjacent results, not
independently verified dependencies. Elementary parity/grid facts are not
claimed as new; this contribution binds them to the literal first caller.

New audit by Chris R / Clear1nsight with substantial OpenAI ChatGPT assistance.
Apache-2.0. No independent human or proof-kernel acceptance is claimed.

## Open next questions

1. Can a real caller supply the PR3303 entry grid and bounded dirty-state range
   at this cut? First bind its physical encoding and input contract to L546;
   numerical format sufficiency does not establish that entry protocol.
2. Can the supplied windows be connected affordably? Assign two data and four
   disposable scratch intervals, then meter right monomial, any conversion,
   kernel, left monomial and adjacent ADD without free relocation. The actual
   allocation, addressing/control and continuation/restoration bill are blockers.
3. Before a larger implementation round, independently check PR3908's fixed
   profile/coverage budget. If it applies, a changed consumer/profile/coverage
   premise needs its own favorable full budget. This audit does not expand the family.
