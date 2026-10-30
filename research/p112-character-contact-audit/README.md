# Independent all-character audit of P112 isolated contacts

This fills the **full512-character phase re-enumeration** gap explicitly left by James Reed's PR4204 aggregate/receipt review. Ross Richardson's original contact construction and proof remain predecessor work, frozen at **d81ccede589450c7c6e428e3fac172d9e603a805**. The new result is an independently implemented source-bound phase/word audit, plus a separate universal dirty-helper identity calculation. No predecessor checker or compiler is imported or executed by either independent program.

## Exact result and reproduction

The primary checker reconstructs the8880 serialized phase operators on every one of512 Walsh characters from binary projectors. It validates phase bytes, hashes, quadratic polars, constants and ranks. It then visits every5824contact x512character x2signs, checking all3 raw input columns of each exact Gaussian-integer endpoint matrix: **5,963,776 signed cases /17,891,328 column cases**. All57,512 chronological source-plus-one operation records, including34,528 native occurrences, are regenerated exactly. The minus-sign result is for the explicitly specified parameterized word; it is not an execution of the author's minus-sign controller branch. All frozen ports and frames are input data, not re-derived supplier endpoints.

The endpoint for entrance frames P,Q, common frame L, exit frames S,T and central a=+/-1 is

```
[[S P^-1,       0, 0],
 [a T P^-1, T Q^-1, 0],
 [       0,       0, I]].
```

The helper is an arbitrary dirty raw input, returned literally. A separately frozen free-group-ring program verifies this identity for arbitrary invertible, potentially noncommuting frame maps. Its wrong-inverse-order control fails on actual noncommuting2x2 integer matrices while scalar-only tests pass; direct delivery requires P=Q. This mechanical calculation and the written cancellation derivation are not a formal-kernel proof. Agreement on the full Walsh basis implies the stated isolated complex512-coordinate linear endpoint.

The primary implementation's pure Gaussian3x3 cache is keyed by every dependency (branch, all five phase exponents and sign); all finite cases are still visited. Its272 distinct keys do not replace the source-phase enumeration. Separate source/receipt integration checks do not constitute a second all-character implementation. Negative controls expose global phase, omitted helper return/precompensation and wrong delivery; a constant global phase can preserve rank/polar data and still fail exact endpoint agreement.

Python3.12, stdlib only:

```sh
python3.12 -B scripts/research_package.py --package research/p112-character-contact-audit
```

Six registered normal/optimized commands recompute scientific results and bindings without writing package files. SOURCE-PINS retains the unchanged compressed source container, proof, README, NOTICE and license. SOURCES binds those bytes through a public own-branch source ancestor, separately from their predecessor origin. Receipts, proof, independent provenance and separate review accompany the package.

## Scope and remaining obligations

This checks isolated published contacts and the specified algebraic word. It does not independently generate the ports from the original supplier word, run every native compiler lowering, audit Laurent B4 or scheduling DP, build a shared chronological caller, certify physical helper delivery/invoice, or establish any supplier, multiplication theorem or kappa improvement. No merge or selected-frontier change. Human/formal-kernel acceptance remains open.

## Open next questions

Independently bind one actual all-edge compiler or shared caller to these identities under a separate scoped budget. A shared chronological schedule must discharge its own restoration, layout, precision and paid-work obligations. The isolated finite phase result does not supply those premises.

## Sources and predecessor credit

Ross Richardson, with substantial OpenAI Codex assistance, supplies PR4204's contact construction, frame choices, dirty-helper word and original phase proof/checks. Retain its PR425/433/523/531/kernel92 and NOTICE lineage (including icekylinx, chafreaky, RohanArun, DreamingOfClouds, Dugongue and eumemic). James Reed/rcfc-jreed supplies the earlier27-check aggregate/receipt audit and explicitly named coverage gap (issuecomment6293939468); that work is separate. Classical frame change and dirty-helper cancellation are not claimed as new general mathematics. This contribution is by ToikY with substantial OpenAI Codex primary implementation, separately frozen oracle, integration and separate proof/code review assistance. Apache-2.0; original unchanged NOTICE/license exports retained. No independent human or formal-kernel acceptance.
