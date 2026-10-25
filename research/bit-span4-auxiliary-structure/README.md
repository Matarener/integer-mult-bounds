# Span four with any number of dirty auxiliary registers

**Partial classification. No new κ.** Selected κ stays `0.001672660197076918`.

## Scope and evidence

Catalogue card `bit-new-register-model`, priority revision 6, base
`bb4bccbf42844d2801487450727c2f63e10d1d0f`. The card asks whether a larger or
nonabelian register model escapes the scoped three-register obstruction. This
package keeps the abelian rank-one alphabet and allows any number of dirty
auxiliary scalar registers, which is a larger register count inside that
alphabet. The question is then cut down to rational frame span exactly 4, for
three invertible `3×3` data targets. That is the first dimension the
dirty-auxiliary lemmas do not exclude at eight calls.

[`PROOF.md`](PROOF.md) states the classification. In brief:

- Full support of the normalized rank-one generator needs at least nine calls.
- A zero coordinate puts the span in block-upper-triangular form `1+1+1` or `1+2`.
- `1+1+1` needs at least nine calls.
- `1+2` needs at least eight. The only remaining eight-call shape is three calls
  on the `1×1` block and five calls on the `2×2` block, with projected `2×2`
  frame span exactly 3 and no strictly upper call.
- Every span-four word shorter than eight calls is impossible.
- Spans 5 and 6 at eight calls remain open. The five-call `2×2` word is not
  excluded.

Lemmas 1 and 2 of
[`research/bit-dirty-auxiliary-registers`](../bit-dirty-auxiliary-registers/README.md)
are cited for every register count and are not re-proved. The span-four
coordinate change is the one in
[`research/bit-three-register-lower-bound`](../bit-three-register-lower-bound/README.md) §3
and
[`research/three-register-no-target-flag`](../three-register-no-target-flag/README.md) §6.
Section 6 of that note prices the `2×2` block at six calls only for exactly
three scalar registers. This package does not extend that sentence. Open PR
#3537 treats nine coordinate projectors beside one idle dirty auxiliary; the
general span-four shape is outside that calculation.

The verifier checks the determinant and minor identities, the rank factorization
`I + XTY^T`, all 28 and 120 idempotent pairs at register counts 3 and 4, all 64
support patterns, the call-budget arithmetic, a nine-call restored-auxiliary
word, deletion and mutation failures, and a cancelling pair that shows a
degree-1 balance does not forbid five calls. It pins the cited headings in the
three source READMEs.

## Reproduce

From the repository root, with Python 3.12:

```sh
python3 -I -B research/bit-span4-auxiliary-structure/verify.py
python3 scripts/research_package.py --package research/bit-span4-auxiliary-structure --check-only
```

The expected verifier line is `PASS_SPAN4_AUXILIARY_STRUCTURE`. No compiler,
network, or third-party Python package is required. The script uses exceptions
rather than assertions, so `python3 -O` still runs the checks.

## Open next questions

1. Does a five-call word exist for three invertible `2×2` targets, rational
   frame span exactly 3, and at least one dirty auxiliary register? It is the
   only remaining route to an eight-call span-four word for three invertible
   `3×3` targets. A useful first step is an arbitrary-register two-relation
   disjoint-subset argument, at relation rank exactly 2. The search is blocked
   by `120^5` ordered words at four registers, and a degree-1 tensor balance is
   too weak: a cancelling pair `B, -B` multiplies to the identity and adds two
   calls without changing that balance.

2. Spans 5 and 6 for three data registers, eight calls and dirty auxiliaries
   remain exactly as in the dirty-auxiliary handoff. The same two-relation
   analysis is the first step, and the same projector-count growth is the
   blocker. Clean ancillas are a different hypothesis and are not claimed here.

## Credit

The model and the low-span / one-relation lemmas used as dependencies come from
Ali Romman's PR #468 (`research/bit-three-register-lower-bound`) and from the
dirty-auxiliary extension in `research/bit-dirty-auxiliary-registers` (waynenilsen,
PR #468 lineage). That line credits eumemic's PR #288 and huxint's PR #203.
David Govea's three-register target-free span-four argument is
`research/three-register-no-target-flag`; its six-call `2×2` step is limited
there to three scalar registers and is not reused as an auxiliary bound. Open
PR #3537 is the coordinate-projector special case.

Prepared by unpaidmoon, with substantial drafting and checker implementation by
Cursor Grok. The predecessor lemmas were cited rather than re-derived. No
independent human review is claimed. New work is Apache-2.0.
