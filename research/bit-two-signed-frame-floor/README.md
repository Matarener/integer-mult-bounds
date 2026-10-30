# Two signed added rank-one frames still require eight calls

**Scoped proof with exact corroboration.** Allowing either sign for two added
nonzero symmetric rational rank-one addresses does not lower the eight-call
minimum for the PR2085/2112 four-target endpoint. Arbitrary finite restored
dirty workspace and free address-independent binary mixing are allowed.
This closes the short-word non-positive-frame question in Josie Elliston's
[PR6111](https://github.com/CrocSwap/integer-mult-bounds/pull/6111).

The new contribution is an elementary **signed-to-positive reduction**.
The final positive-case exclusion is PR6111's theorem; the one-extra case
uses [PR6079](https://github.com/CrocSwap/integer-mult-bounds/pull/6079).
Both sources are archived and `partially_reviewed` in the current central
ledger. They are explicit mathematical dependencies; their scientific
replays and independent acceptance are not claimed here.

## Result and proof

Let A=diag(1,0), B=diag(0,1), P=[[1,1],[1,1]]/2 and
Q=[[1,-1],[-1,1]]/2. The complete endpoint is
`diag([A+P],[A+Q],[B+P],[B+Q],1,...)`. Each paid factor is
`I+([F]-1)N`, with binary rank-one idempotent N and
`F in {A,B,P,Q,R,S}`. R and S may be positive, negative, coincident,
opposite, or duplicates of old frames. They remain nonzero and rank one.

[PROOF.md](PROOF.md) gives all hypotheses and the width-independent proof.
For a hypothetical word using both additions in at most seven calls,
determinant conservation gives
`rR+sS=M=4I-aA-bB-pP-qQ`, with at most five old calls.

- If M is indefinite, a scalar projection requires both 1 and 2 in
  `{0,rho,4-rho,4}`, which is impossible.
- If M has rank one, both additions lie on its line. Exact target support
  or a first-order character with capacity two and demand four excludes it.
- If M is positive definite, evaluating on the two kernels forces R and S
  positive. PR6111 then applies.

The direct eight-call word attains the minimum. Negative frames really can
appear at longer lengths: replace one A call by 2A followed by -A to get
an exact nine-call word. This is not an all-length positivity theorem.

There is no native supplier, paid-profile saving, new κ or discharge of any
selected framework assumption. The selected conditional result remains
`781451/250000000`. Formal paid calls do not automatically price physical
operations, and all native/caller/compiler/precision/recovery obligations
remain separate.

## Evidence and reproduction

Python 3.12, standard library only:

```sh
python3.12 -B scripts/research_package.py --package research/bit-two-signed-frame-floor
python3.12 -I -W error -B research/bit-two-signed-frame-floor/verify.py
python3.12 -I -O -W error -B research/bit-two-signed-frame-floor/verify.py
```

Expected markers are `PASS_SIGNED_TWO_FRAME_SUPPORT` and
`PASS_TWO_SIGNED_FRAME_REDUCTION`; the registered runner executes both modes.
The direct verifier needs only this package and its two declared README
inputs. It uses no Git, network, nonstandard package or predecessor code.

The elementary check reconstructs all 462 profiles as 422 positive-definite,
20 indefinite, 16 singular-span and four singular-character cases. It also
checks the two-summand determinant/sign identity on 576 rational fixtures
and the three-summand counterexample `-A+2A+B=I` to any overgeneralization.

The separately written checker uses integer subset equations in the rational
basis (A,B,P), rather than the primary check's physical matrix entries.
It applies **no PSD or positive-trace filter** to candidate splits. Its
complete classification gives 435 empty profiles, seven free families and
32 pinned splits across twenty profiles. Positivity of every pinned split
is checked afterward. All 148 concrete opposite-sign residual splits fail
literal target support. Twenty-four control checks include negative rotated
frames, zero/rank-two rejection, the nine-call signed word on four/six roles,
omitting its negative call, the ordinary eight-call positive control and
a changed target. Controls include positive fixtures; “24” is not a count
of rejected mutants. The independent inventory digest is
`ed1b074151ab497af3c585f532ad0b0dd4c0cecb4b764721e4109f448d434443`.

These are exact finite checks, not finite extrapolation to arbitrary widths
or denominators. The written proof supplies those quantifiers. Local
environment: CPython 3.12.14, macOS arm64. Normal/optimized registered replay,
source metadata and committed-byte/export checks are separate obligations.
No formal proof kernel, independent human review or selected cold replay
is claimed.

## Coordination, sources and scope

Canonical main was fetched before work, and this branch starts at
`3f0152a32eeebac0df11946dbd50cabe5a7f7839`, priority revision 8.
[Canonical claim/status](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19270802).
Task `bit-new-register-model` has **changed scope**, recorded with the full
original card in [TASK.json](TASK.json): a formal alphabet theorem rather
than a native larger/nonabelian construction.

The expansion decision is to settle this explicitly open sign hypothesis
before any implementation campaign. Three added positive frames were
considered as a different mechanism and remain unreserved. This result
does not justify more search inside the now-excluded two-frame short model.

Current handoffs and all-state searches for signed/two/rank-one frames,
three positive frames and PR6111 were inspected on October 29, 2026.
PR6148 excludes one eight-call half-frame example; PR6186 accelerates
PR6111's positive checker. Neither supplies this signed reduction.
The offline helper searched 24 of 8,567 local notes with no usable remote
snapshot. Sparse local coverage and bounded live searches are not a proof
of novelty or coverage of unpublished work.

The selected record, source manifest, certificate, review, baseline script
and all 1,227 previously materialized orientation inputs are unchanged from
the preceding successful binding-only orientation at main `721c03822`.
That orientation is reused after a Git-diff check, not described as a fresh
scientific replay. The selected record hash remains
`9b8d0eea95b3bf0dfcb7938a732a6439b87a2685dec2a5ab9e525b3b34debbfa`.

[SOURCES.json](SOURCES.json) pins the exact canonical theorem READMEs:
PR6111 head `961b749fa40a1117d0746064528d2dfa290c57e0` and PR6079 head
`44745c427f710e406cb2d2c6de458b7f93d81f01`. Catalogue and selected record
are historical provenance. Predecessor bytes remain unchanged.

## Open next questions

Can three or more signed additions beat eight? The two-summand kernel
argument fails already at `-A+2A+B=I`. Start with one explicit three-frame
candidate and its determinant/support constraints; an exact word and full
native invoice would still be required for a multiplication improvement.
No larger search or follow-up is reserved. Structured relevance, first
step and blockers are in TASK.json.

## Credit

Prepared by **apoursh** with substantial OpenAI Codex assistance in proof,
implementation and separate agent mathematical/code audits. Apache-2.0.
Agent reviews are not independent human or proof-kernel acceptance.

Josie Elliston/Claude retains PR6111's positive two-frame theorem and support
classification; JoyboyBrian retains #6104's question and split formulation;
apoursh retains PR6089/6079's classification and single-frame result;
Nick Petalas retains PR2910's determinant method; Cinna Davis retains the
PR2085/2112 model and endpoint; Philippe Van Velzen and the retained BIT
lineage keep their prior floor and framework credit. Kernel, determinant
and rank algebra are classical; no literature-wide priority is claimed.
