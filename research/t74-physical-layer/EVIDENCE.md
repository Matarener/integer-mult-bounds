# Verification evidence

I verified the native, binding and physical groups on macOS 26.5 arm64 with
CPython 3.12.13 and numpy 2.2.6. The new checks use `-I -O -Werror -B`;
I run retained assertion-based native checkers with assertions enabled.
The registered runner isolates bytecode caches. I reran the affected native
and binding groups after adding modular endpoints and direct-constructor
source authentication. The final manifest covers 14 checks in three commands.

I reconstructed the exact PR2979 source through its pinned predecessor chain.
I fetched missing PR2894 commit `18d03c447886895ef9abf888398178e0428533ca`.
I changed no predecessor files in the repository. The 637-file derived source
matches manifest `751b46364742cbb947f7db07c130ff09085b38b52c520d3b47f2dadc1e21ba80`.

I ran the retained sparse native driver on both changed words with one BLAS
thread. Each provider passed transport, ledgers, local replay, wrappers and
exact phase/warp checks. I compare all seven proof-relevant generated artifact
identities against the frozen inputs, including decompressed gzip payloads.
These source checks retain their authors' scope.

I ran the new compiler under `-I -O -Werror -B`. Each orientation/provider
contains 22,748 source events and 29,782 compiled instructions. Each has 3,517
positive children, with profile

    {1:2445,2:706,3:232,4:108,5:18,8:8}.

I retain 91 explicit zero-buffer releases and 107 zero operations (including
the centre starts/ends). The compiled instruction digests are:

| Provider | Orientation | SHA256 |
|---|---|---|
| base | forward | `0d134143fbea5abaac24a1ea1ee575a4657de87835f6563cff92186d681d0263` |
| base | backward | `3b024792bf684ff05c88fa9caf998b8fefa77716ab7509e2fce73ee8f62d0921` |
| extra | forward | `d468032f5d78732be593f3d0f72386be2613e5ac3ff3509b54a3e56aaa9c0a87` |
| extra | backward | `ff23ef17c3ae31a31dbd77eda8478d4a5eaafaf628bf2fdfbe133c07a922e7b4` |

I check the following additional boundaries:

| Check | Result |
|---|---|
| Local compiler controls | Missing release, premature release, wrong warp frame and an unpaid positive-rank warp reject |
| Modular compiled endpoints | Four actual programs, each with 632 role vectors and 512 addresses; modulus 65537, i=256 |
| Global source | 666 calls, 2,222 events, 420,912 owners, 8,659 helper charts and 52,184 idle tails |
| Production dispatch | Four provider/orientation groups, each with 632 owner selectors; a changed native warp phase rejects |
| Monomials | 3,782 affine maps and inverse words; 2,248 phase signatures; eight spaced tensor cases |
| Reduced physical execution | 2,048 input bits, ten child calls/returns, preserved borrows and blank private work |
| Private release failure | A nonzero Z packet rejects with source and descriptors preserved |
| Normalized root | Four direct packets and one reduced fast packet with five child calls/returns |
| Scalar/height inventory | 36 literals; 41,928,770 passes per cover; prefix denominator at most 8 and L1 norm at most 9 |
| Layer budget | Strict sigma=0.9983 moment and the margins in LAYER-BOUND.md |

The monomial coefficient/affine receipt has SHA256
`8abe62ca25033caee95d5657da28d6cb05edd2ce2aeec7837e29f8b94acaa9d7`.
The reduced physical output has SHA256
`a383807b25825da02358121301bbae054048bcedea1ac3dfa1102e87967a51e9`.
The normalized direct/fast output receipts have SHA256
`4fced21f9e114bff265815a79dfe0b02e2989a195c87a6c5a16b7041193fd760`
and `75b19b9d75e245f1720eaccc048c366a7a68cf7741805e908b0a2222067d4b40`.

For the complete modular arrays, I obtain:

| Provider | Orientation | SHA256 |
|---|---|---|
| gauge44 | forward | `2fbc9b619425174e41b8b40dfbc3cdc84d775a2445c5c4ee2070a3eb2ea54ca1` |
| gauge44 | backward | `1765a6a6491bf1e8b2700bb83d4e92310ff7c319e7ce43d3eda61a07c50b6c02` |
| extra | forward | `76169e4772620d786ddfd4f945a019b4ee129ee013a4b8be792e767054164f6a` |
| extra | backward | `2d3ca7dafc6fe3795de735916e16e65b2eb17f266bf05c94e0d8de8ad50f8063` |

I do not infer universal complex equality from modular samples. The native
proofs and written refinement supply separate mathematical obligations.
I execute reduced physical/root geometry, not the production O73 payload,
native GL64 factory or full guard width. The source-relative layer theorem
retains its native, hosting, ordinary-backend and long-record assumptions.
I have not established the enclosing multiplication transfer or obtained
independent human or full formal-kernel review.
