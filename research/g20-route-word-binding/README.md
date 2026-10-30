# Exact G20 route-marker to normalizer-word binding

This fills the specific incidence and direction gap left by [PR #5801](https://github.com/CrocSwap/integer-mult-bounds/pull/5801). It binds the actual PAID_PORT_ROUTE records from Ali Romman's [PR #5798](https://github.com/CrocSwap/integer-mult-bounds/pull/5798), head eaa9cc8c15d8e994d7b81b0cda3f6dd63b0db826, to the frozen RIGHT words at eb92cbdf211f0c3717ff6fa71af47ec38f8e412d. The source audit already establishes the complete global endpoint, marker placements and retained fee. Those are predecessor results, not new claims here. [Canonical claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/5777#discussioncomment-19205398).

The stream markers identify stage, owner, port and phase. They do not supply a physical lowering or specify a word direction. This certificate gives an explicit **conditional single-ROW-cover plan**: with local projector P=WQW^-1 and native cut h=gS, choose ENTRY S=W^-1 and RETURN W. Then hPh^-1=gQg^-1 and the borrowed cover returns to g. This is a model-qualified interpretation, not a newly decoded instruction hidden in the source marker.

Native address halves are a different notion from owner banks. The native pairing is x_i with x_(15-i). In physical contiguous order, applying W to both paired halves is diag(W,JWJ), with J the eight-coordinate reversal. It is generally not diag(W,W). The proof and independent oracle distinguish this column-address conjugation, function pullback and ROW right update. One cover-matrix word changes both native halves through the cover encoding; a second full ROW word per native half is not charged by this declared model.

## Exact evidence and scope

The actual stream contains **7,548** route markers, each bound to one word under this cover plan: 3,774 in each direction. RESULT.json retains every event/call/stage/owner/port/phase/program binding and coefficient ledger. The selected words total **202,640 ADDs and 73,916 SCALEs**. Lifting their factors gives **25,735,280 ordered_shift and 9,387,332 unit_scale calls times f^2**, without another native-half factor. Seven recomputed controls reject missing markers, owner/phase/direction/program/stage misbinding and source drift. ORACLE.json independently scans the source stream, checks the join and tests the exact cover and paired-address identities. The independent checks include 222 word products, 111 cover conjugations, 1,776 literal paired basis columns and all 18 ordinal layouts. Two further controls preserve aggregate counts while breaking actual bank restoration. Neither checker imports the other or a predecessor implementation.

Only nonzero thick stages have internal route markers. Stage embedding uses the actual thick-stage ordinal in the 18-stage inventory, central coordinate 0 and its seven-coordinate block in dimension 127. This is the same chosen compatible layout as #5801; a retained literal physical head map is still unproved.

Positive coefficient counts describe the declared single-cover plan. For N=127f they lift every factor across all N cover-matrix rows and f lanes. Each coefficient retains a named positive ordered_shift or unit_scale tariff, potentially dependent on radix, width and tape parameters. These symbolic counts are not a unit-cost model, a complete route invoice or absorption into the source's finite fee.

This package does not rerun or newly admit the full native/global caller. Its physical head map, old-low cache COPY/CLEAR, carries, low-type commit, padding, movement, restoration schedule, primitive implementation and tariffs remain open. Compiler, stock, precision/tape, analytic recovery and all five inherited framework assumptions remain. No new kappa, selected-frontier change or full multiplication theorem follows.

## Reproduction

Python 3.12 and the standard library suffice:

```sh
python3.12 -B scripts/research_package.py --package research/g20-route-word-binding
```

The registered commands run normal/optimized primary checks and the separate optimized oracle. Frozen package-local inputs authenticate by raw SHA256 and Git blob identity. Default runs compare complete canonical JSON receipts, preserving numeric-type distinctions. Explicit --emit generates a candidate on stdout and never rewrites a receipt. Injected faults are controls, not allegations about predecessor code.

SOURCES.json separates main-context provenance from vendored unmerged input origins. Committed-byte/source-history checks cover the declared main ancestry; raw source bindings do not claim those input heads are publication ancestors. Official export and read-only Git-free empty-PATH replay are separate integrity checks, not scientific acceptance. TASK.json records the changed formal-interface-lemma scope. No Lean build or native replay ran.

## Open next questions

Bind this conditional cover plan to the retained literal physical route and price all caches, carries, low-type commit, padding, movement and return. The source markers alone cannot choose among physical lowering models. Prove that missing ABI and coefficient-specific tariffs before importing the counts into the source's full caller invoice. The structured next question and blocker are recorded in TASK.json.

## Credit

Ali Romman with substantial Codex assistance supplied the G20 construction/audits and rational normalizer witnesses; retain Dugongue, ai-nanachi, PR #5679/#5708/#5782 and all source credits. JoyboyBrian supplied the earlier ROW generator and named P2 schedule, with its retained predecessors. PR #5801's ToikY/Codex operation words are frozen predecessor work in this package. The new contribution is the exact marker-to-word binding, explicit conditional cover convention and independent reflected-address audit, by ToikY with substantial OpenAI Codex assistance using separate primary/oracle/proof-review contexts. Classical conjugation is not claimed as a new general theorem. Apache-2.0; full attribution is in NOTICE.
