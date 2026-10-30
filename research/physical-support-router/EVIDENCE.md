# Evidence and scope

I developed this package from canonical main
`20ecf2891d80b5acf18d980b2164fb44ea7faa90`, with priority revision 6, on
macOS arm64 and Python 3.12. I freeze the official PR3608 export from
`c6020096322012f7cc41236c3ac15a6b6cd3f8b9`, SHA256
`c5767f3744338bb022a5d18863566da19c26a657be8b23b3a2ae775c431c7af5`.
I retain its nested source archives and attribution.

## Bounded evidence

I check the encoded planner against an indexed coordinate-basis oracle after
compilation. The runtime cannot call that oracle. I check 34 permutations on
zero through four listed coordinates, four reduced-policy fast cases, a
standard-policy case with n=4096,p=64 and five listed coordinates, and a
no-gap fallback with n=956,p=65536,k=2. The latter has N=10H but no untouched
ell-bit record block. I include cycles of lengths three, five and six, a
two-edge sparse batch, multiple reservoir choices, and exact tail CNOTs.

I execute a complete 2,048-bit fast three-cycle through actual physical
operations. I observe six external B1 swaps, four sparse batches and two exact
CNOTs. The sparse batches contribute 48 B1 calls and 40 controlled rotations;
I observe the retuned 1/577 selector on all 54 total B1 calls. I prepare and
restore the actual suffix once. I also feed an actual forward output through
the inverse on the same reused cohort. I compare every output bit against its
independent input provenance in each leg.

The full fast fixtures use q=2, original one-bit records, n=11,p=2 and an
explicit compiled G=1,K=5 guard policy. After physical preparation, I group
the one-bit suffix into two-bit records and route the complete ten-bit prefix.
I include exceptional repair through the retained sparse engine. These fixtures
check the complete execution and restoration; they do not test the production
bad-set density or asymptotic runtime. I test production G,K,ell with encoded
metadata and prove its rate in PROOF.md.

I execute a literal three-cycle with four-bit opaque records and three outer
rows, followed by empty and fixed-point identity descriptors on the same
router. I check preserved payload/descriptor/Count bytes, canonical heads,
erased owned bodies and markers, consumed child outputs and fixed-pool usage.
I reject eleven descriptor, semantic and ownership controls, including omitted
post-placement reindexing. I authenticate one cold source cohort and reject
altered source bytes and a symlink in place of the archive.

## Development corrections

The first controls exposed two implementation/API mismatches. I had passed
compiled multipliers zero and one to a retained helper that requires at least
two; I now construct zero or keep the operand for those fixed branches. I had
also used the pool's initialized-marker check after final marker erasure in
the checker; I now inspect the closed blank baseline. I corrected the trailing
descriptor fixture to append at the actual tape end. I made these corrections
before publication and retained the corresponding controls.

## Reproduction receipt and limits

I passed all seven registered Python 3.12 commands. I measured 0.277 seconds
for source checks, 0.246 for finite budget controls, 8.632 for metadata,
0.296 for literal packets, 71.515 for the fast forward packet, 144.140 for
the two-leg physical round trip and 0.287 for rejection controls. I observed
at most 44 router scratch leases, below the written 128-lease upper bound
and the fixed 256-role allocation. These measurements describe this local
fixture run, not the asymptotic runtime or a production packet.

I declare the seven Python 3.12 commands in VERIFY.json. The publication PR
records the final committed-byte check, source-history check, official export,
Git-free replay, unchanged regular-file comparison and exact-head CI result.
I keep those final commit-dependent receipts outside this file to avoid a
self-referential hash.

I do not treat finite execution, green CI or archival intake as scientific
admission of the inherited all-size premises. I have not executed a production
GL64/O(73,2) packet, completed a formal machine refinement, integrated the T74
root, or proved the enclosing multiplication/error/packing theorem.

Jose Manuel (`jmbarrancoml`), with substantial OpenAI Codex assistance.
I claim no independent human or formal-kernel review. Apache-2.0.
