# Encoded physical support router

I implement a complete coordinate-permutation router around the physical
sparse XOR batch from [PR3608](https://github.com/CrocSwap/integer-mult-bounds/pull/3608).
I receive a complete binary address rectangle, opaque records, arbitrary outer
rows and an encoded permutation on k listed coordinates. I prepare actual
long records, factor the permutation into two involutions, place and restore
reservoirs, execute colored XOR batches and exact tail gates, then restore the
original record interpretation. I preserve borrowed inputs and return protected
output through one shared B1/native cohort.

Under the retained completed B1 and sparse-batch arguments, I prove

    O(V*(k+1)^tau*(log2 p)^(1+tau)) time,
    O(V) space plus fixed compilation,
    tau=332353/332929.

I require fixed positive c,C0,A0, `c*p<=n<=C0*p`, `k<=2*p^.997` and
`log2(R+1)<=A0*p`. I give an explicit uniform cutoff for the literal fallback
in [PROOF.md](PROOF.md). The lower address bound and actual record preparation
are part of the theorem's hypotheses and construction. I leave the combined
T74/multiplication caller and the selected frontier unchanged.

## Implementation boundary

I number coordinates from the least significant end, with
`output[pi(i)]=input[i]` for coordinate values. I validate sorted distinct
sources, distinct images, equal source/image sets and exact descriptor extent.
I allow listed fixed points. I encode numerical parameters and loop indices
on Count tapes and compile variable instructions onto one binary tape.

I use the standard policy `ell=ceil(log2 p)^2`, `G=4ceil(log2 p)+6`, `K=64G`.
For a nonidentity permutation I choose `H=floor(k/2)G` and require
`n-ell>=10H` plus an untouched ell-bit block outside the actual low suffix.
I perform two physical B1 swaps to prepare and restore that suffix. I route
inside the remaining prefix and recompute pair positions after each reservoir
placement, before sorting the metadata and assigning target colors.

I execute at most 18K sparse batches, each with its inherited twelve H-bit B1
swaps and complete repair. I also pay at most 36 reservoir swaps, 18K exact
tail CNOTs and the two suffix swaps. If the fast geometry fails, I execute at
most k single-coordinate swaps. I preserve the predecessors' successful-input
ownership contract; I make no interrupted-operation recovery claim.

## Evidence and replay

```sh
python3.12 scripts/research_package.py --package research/physical-support-router
```

I use Python 3.12 and the standard library. I authenticate the official PR3608
export and open its retained cohort once per command. I check all 23 ordinary
backend files against its retained rate source before executing the router.
[VERIFY.json](VERIFY.json) declares seven bounded commands.

I check 34 small permutations, reduced-policy fast plans, a standard-policy
4,096-coordinate plan, and a literal fallback with enough reservoir space but
no untouched block. I execute complete 2,048-bit fast packets and an actual
forward/inverse round trip on one reused physical cohort, with separate input
bit provenance for each leg. I also execute literal and identity packets with
multiple outer rows and opaque multi-bit records. I check malformed descriptors,
omitted reindexing, premature output reuse and physical allocation during a call.

I distinguish the finite fixtures from the all-size proof. The fast physical
fixtures use an explicit compiled `G=1,K=5` policy and q=2's elementary B1
branch. I check the production guard policy through encoded planning and the
written rate argument; I have not run its exponentially large full packets.
I retain the ordinary/sparse universal premises and their scientific-review
status. [EVIDENCE.md](EVIDENCE.md) records coverage and initial corrections.

## Open next questions

1. Bind this router to the actual-width T74 root on one full packet and one
   physical cohort. Start from PR3599, retain the original record boundaries,
   expose the root support, execute the root and undo the exposure. The shared
   factory, complete root/restore invoice and caller contract remain open.
2. Bind the enclosing multiplication caller's full address span to its online
   precision. The generic root API gives no lower bound `n>=c*p`. Start from
   the retained global coarse rectangle and online precision relation; keep
   the offline setup precision separate and include the error/packing ledger.

I coordinate in [Discussion2612](https://github.com/CrocSwap/integer-mult-bounds/discussions/2612#discussioncomment-19009513).
[TASK.json](TASK.json) records the revision-6 task, overlap check and expansion
decision. I stop at the standalone router and leave admission of the enclosing
supplier open.

## Attribution

Jose Manuel (`jmbarrancoml`), with substantial OpenAI Codex assistance in
mathematics, implementation, source analysis, verification and prose.
I claim neither independent human review nor formal-kernel verification.
Apache-2.0.

I retain RaD/hipotures's arbitrary-coordinate routing lineage from PR20,
recorded by Zhihao Chen in [PR23](https://github.com/CrocSwap/integer-mult-bounds/pull/23),
head `661ebabc1076c9f525d7ce4967c876b203fa9827`; Vlado Vojdanovski's
[PR1673](https://github.com/CrocSwap/integer-mult-bounds/pull/1673), head
`85ddaa312e463cfaca98d49a2a262994551cec4e`, for the support-sensitive router;
and Douglas Colkitt's compact chronology and guard/repair construction.
I add the complete encoded physical composition to those mathematical sources.

I freeze my PR3608 head `c6020096322012f7cc41236c3ac15a6b6cd3f8b9`, including
its PR3055 physical Compact and PR3562 retuned ordinary inputs. The nested
archives retain the native/borrowing sources, contributors and notices.
I also retain Hiroki Kumazaki's PR3576 factory credit and Nick Petalas's PR3581
B1-only exposure boundary as adjacent work. I use controlled rotations and
exceptional repair between B1 calls, beyond that boundary's operation alphabet.
