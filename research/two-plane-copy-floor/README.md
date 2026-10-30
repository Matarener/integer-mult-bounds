# Two-plane mixing cannot lower the additive COPY mass

**Sharp scoped negative result. No new κ.** For any two of the selected 56
matched planes, the minimum full-plane support-pairing COPY mass is **8**,
even with arbitrary rational or complex coefficients and any finite number
of scalar messages. The proof holds over every coefficient field. It covers
both the identity endpoint and the strict two-plane scalar fitting mask.

This closes the arbitrary-coefficient cancellation and overcomplete gaps
left by Gonzalo Mier's [PR3990](https://github.com/CrocSwap/integer-mult-bounds/pull/3990)
and [PR3997](https://github.com/CrocSwap/integer-mult-bounds/pull/3997), which
screen binary, generic rational and signed-ternary **bases**. The new result
is a short rank inequality, not a larger coefficient census.

For a decoder partitioned into disjoint plane pairs, total COPY mass is at
least **224**, even after arbitrary mixing inside each pair. Retaining the
favorable plane-port coverage model of Jeremy Diviney's PR2203, the complete
zero-saving lower invoice is **65,632 / 65,408 = 293/292 > 1**, before any
additional expense. Thus this restricted mechanism cannot improve the
supplier. The 224 independent-block baseline and this budget ratio are
predecessor results; extending their rejection to arbitrary pair-local
factorizations is new here.

## Proof and precise boundary

[PROOF.md](PROOF.md) gives the all-field argument. For two orthonormal label
blocks of sizes `p,q`, let `c` be their binary cross rank. The joint Gram rank
is at least `p+q-c`. Every scalar rank-one message's tariff dominates

\[
 (p-c)\operatorname{rank}M_{AA}+(q-c)\operatorname{rank}M_{BB}
       +c\operatorname{rank}M.
\]

Rank subadditivity bounds the whole identity by `p²+q²`; separate coordinate
messages attain it. For planes, `p=q=2`, so the exact answer is eight.

This theorem prices **separate scalar messages on complete plane closures**.
It is not a bound for shared native operations, different closures/readers,
nonlinear messages, or globally mixed three-or-more-plane decoders. The
pairwise bounds must not be added for overlapping messages.

The mass floor also does not exclude every local power-cost improvement.
An explicit six-term identity for an orthogonal pair has tariffs
`(4,4,0,0,0,0)`, preserving mass eight but reducing the concave COPY-only bill
relative to `(2,2,2,2)`. It still fails the unchanged complete budget. Its four
zero-COPY terms are not asserted to be free physical operations. This fixture
is included to prevent overinterpreting the negative result.

## Exact evidence and reproduction

From repository root, Python 3.12, standard library only:

```sh
python3.12 -I -B scripts/research_package.py --package research/two-plane-copy-floor
```

Expected: `PASS_TWO_PLANE_COPY_FLOOR` in normal and optimized modes,
`PASS_INDEPENDENT_TWO_PLANE_F2`, and finally
`PASS_REGISTERED_RESEARCH_PACKAGE ... outcome=negative-result`.

The registered commands authenticate the selected archive and matching, check
all **1,540 pairs / 13,860 atom inequalities**, all **682** binary cross
matrices for block sizes 1–3, exact rational cancellation and complex phase
fixtures, the six-term identity, and seven rejection controls.

The no-import independent checker computes geometry by image-set enumeration
and solves a separate shortest-path problem for each of the five tariff
classes: all 65,536 binary four-by-four matrices are possible states and all
225 nonzero binary rank-one matrices are allowed moves. It stops when the
identity is settled at cost eight; all cheaper finite binary decompositions
are thereby excluded. Underpricing a self-copy changes the exact optimum to
six, so the check detects an actual cost failure. This finite corroboration
does not prove the arbitrary-field theorem; the written argument does.

The full recomputed receipt is [RESULT.json](RESULT.json). Actual packaging,
source-history, export and corruption-check results are in
[VALIDATION.md](VALIDATION.md). No selected cold replay, native supplier,
Lean build or hosted-CI success is claimed.

## Sources, task and full-cost decision

Base: `12fa8c5c844be21bfefb38a19503fbd867a11244`, canonical main, priority
revision 7. [SOURCES.json](SOURCES.json) records exact Git blobs, SHA256 pins,
and predecessor heads; runtime inputs are the selected data-phase archive
and retained matching certificate. All predecessor code remains unchanged,
and neither verifier imports it. New material is confined to this package.

OS assignment seed **27**, complex-supplier track. The picker nonce is
`0000000000000000000000000000001b`. Seed-selected plane pair `(0,28)` has
ports `(0,1)/(86,37)`; the same analytic test then covers every pair. The three
candidate tasks, rejected alternatives, local claim and explicit scope change
from the positive supplier card are in [TASK.json](TASK.json).

The overlap helper's remote refresh lacked `gh`; live GitHub connector PR
queries and public Discussion 1163/1166/1167 reads supplemented it. The
available connector cannot post to Discussions, and no pinned sprint issue
was found, so the claim is local. Search coverage is not a novelty guarantee.

The full-cost screen grants ideal hosting and zero **additional** cost for
access, coefficients, adapters, preparation, restoration and owners. These
costs are unknown, not implemented as zero. The retained base coverage and
COPY mass alone already fail. There is no justification here for a larger
pair-local construction campaign. Selected κ remains
`0.001672660197076918`; inherited all-size/compiler, realization,
precision/tape, analytic and bit-interface obligations remain untouched.

## Open next questions

- A genuinely joint three-plane decoder is outside the rank dual's scope.
  Start with one exact endpoint and all 49 closure-pair tariffs, then price
  its complete coverage model. Native access, restoration and hosting remain
  blockers; a larger coefficient search on two planes is not a new mechanism.
- The equal-mass larger-copy fixture needs a changed caller or coverage law
  before it could help. First exhibit that literal caller and charge all four
  cross terms; stop if the zero-saving deficit persists. No physical compiler
  or completed consumer for that fixture is provided.

## Credit

Prepared for **@CubeJerry**, with substantial **OpenAI Codex** assistance in
derivation, implementation, verification and writing. The two checkers use
different algorithms, but were written in the same AI session; no independent
human review or formal proof-kernel acceptance is implied. Apache-2.0.

Credit Gonzalo Mier (PR3990/3997), Cinna Davis (PR1825/2126), Adam Gall
(PR1889), Jeremy Diviney (PR2203), ctoth's team and Philippe Van Velzen for
the contracts, native payload accounting and earlier baselines. Nick Petalas's
PR3383 proves a distinct fixed-row-space recoding tariff; it is credited and
not invoked as a premise. His PR3489 covers a different two-indicator target
with at most four terms; PR3505 gives a broader reader-floor criterion when
an augmented matroid has a characteristic-two representation. The present
two-plane rank dual needs neither a term bound nor that representation premise.
The selected Rohan Arun / Jeremy Kothe / Hao Yan
complex construction and DreamingOfClouds / eumemic bit lineage remain
unchanged. Repository tools retain their original authors' credit.
