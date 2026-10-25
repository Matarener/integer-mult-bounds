# P104 tensor-code literal-word audit

This independently checks the actual scalar programs in [Chris R / Clear1nsight's
PR3979](https://github.com/CrocSwap/integer-mult-bounds/pull/3979) at frozen head
`a8a1d744811cd7d1f9c43ec7ccbae85ef9695b61`. Every one of **763,392 literal
operations** is covered by **1,056 fiber instances, disjoint within each sweep**, reduced to eight
exact local linear maps. A separately implemented exact tensor calculation checks
eight global identities, comprising 32 bank blocks, on all **21,632 data
coordinates**. No coordinate sampling or floating tolerance is used.

The contribution is source-bound implementation coverage. The tensor code,
algebraic conjugation and protocol savings belong to PR3979. Its written proof
already addresses arbitrary inputs; this audit adds exhaustive actual-instance
word coverage beyond its small-grid basis tests and actual dense fixtures. It
does not supply a new code, physical repeated caller, admitted supplier or κ.

## Evidence and reproduction

From the repository root, with Python 3.12 and no third-party requirements:

```sh
python3.12 -B scripts/research_package.py --package research/p104-tensor-word-audit
```

The three registered commands are `verify.py`, `independent.py` and
`test_verify.py`. Direct replay also works from a Git-free committed package
export containing the declared canonical P104 fixture. A package-directory copy
alone omits that external input. `SOURCES.json` pins its exact bytes and the
three package-local predecessor exports; neither an unmerged predecessor commit
nor network access is needed for replay.

`verify.py` authenticates the frozen constructor before calling its word builders
and geometry constructor. Those builders are the object under review. It never
calls the predecessor evaluator, invoice or result routine. The checker consumes
every event, validates its global data index, bank, axis, sign and chronology,
and evaluates one full basis map for each distinct 104- or 208-coordinate fiber.
Every other fiber is checked for exact program equality after its own physical
index localization; a cached pattern cannot hide an altered later fiber.

`independent.py` imports neither primary nor predecessor code. It reconstructs
the roots and all 768 signed-half coefficients by a different enumeration. Both
checkers bind this complete ordered coefficient array to the same canonical
digest. It proves the global block identities by exact factored Kronecker
products and Frobenius-square contractions; zero means every matrix entry is
zero. Four deliberately wrong global expressions have strictly positive norms.
See [PROOF.md](PROOF.md) for the composition argument and conventions.

`test_verify.py` runs 12 semantic word mutations and seven actual CLI damaged
source/invoice cases under both normal and optimized Python: 38 rejections,
plus four separate independent-checker fixture rejections. It also replays the
actual 104-port primary checker normally and optimized from an inode-disjoint,
read-only Git-free closure and verifies unchanged source bytes. These are
software checks and a scoped exact algebra certificate; no human or proof-kernel
review is implied.

## Recomputed original invoice

| Named word | Unit ADD | Half | Restoring double |
| --- | ---: | ---: | ---: |
| Encoder plus decoder | 319,488 | 43,264 | 43,264 |
| One coded Gram pair | 26,240 | 3,328 | 3,328 |
| One specified reference Gram pair | 241,280 | 41,600 | 41,600 |

The claimed two-pair saving is confirmed: 110,592 ADDs and 33,280 halves and
doubles each, with entry and exit paid. One pair loses 104,448 ADDs. These
are PR3979's results against its specified reference, with no optimality claim.
The correct identity-shear coefficients remain `N tensor M` and `M tensor N`,
where `M=UU^t`, `N=M^-1`; the omitted side maps each have rational rank 10,816.
Algebraic rank does not price native calls. Helpers are untouched by the literal
data indices, which proves logical identity extension only.

## Open next questions

1. **Actual repeated consumer and shared charts.** Pin one chronological physical
   producer/consumer pair and write every data/helper owner and ordered chart
   conjugate. This determines whether a shared code can be used at all. No such
   physical pair is constructed here; scalar conjugacy does not discharge it.
2. **Complete paid identity caller.** After that interface is fixed, compile the
   required `N-P` side maps and code boundaries and price every native transport,
   helper, routing and finite-width precision charge. First test the complete
   favorable family gate; the isolated repeated-Gram saving cannot justify
   construction expansion. All-size and multiplication-theorem admission remain
   separate obligations.

## Attribution and scope

Chris R / Clear1nsight owns PR3979's tensor construction, scalar word builders,
original proof, invoice and side-map analysis. Its source files are retained
byte-for-byte in `source/`. PR3961 supplies the preceding representation mismatch;
PR3882/3940/3943/3954 retain the caller lineage. ToikY's PR3956 adapter comparison
and PR3966 phase gauge are context, not dependencies of this certificate.
The retained source credits Rohan Arun/PR1972, Chafik Boukhalfa/PR1991, Adam
Gall/PR1940, Josie Elliston and the E8 predecessors, Sagar Thakrar/PR1012,
Douglas Colkitt, Dominik Scholz and the native/compiler/coverage/terminal-floor
contributors named in the preserved source. Their claims outside this scope
were not replayed here.

New audit, packaging and tests: ToikY with substantial OpenAI Codex assistance,
including separate AI math and test contexts. Apache-2.0. Only this scoped package
is added; canonical main, frozen predecessors and the selected frontier are
unchanged. `TASK.json` records handoff-first selection, overlap coverage and the
change from the catalogue card's original chronological-correction question.
