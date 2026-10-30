# Exact dirty-endpoint tests with bounded live signs

This contribution was produced by Nick Petalas. Apache-2.0.

## Result

Scoped written mathematical proof with exact finite corroboration. For a word
of L rational ADD, signed QUERY, signed APPLY and SWAP instructions on r
arbitrary dirty roles, let k be the maximum number of signs that have appeared
but will appear again. Complete identity at every assignment is decidable in

    O(L * 2^(k+1) * (r^2+1)^3)

rational operations, with at most 2^k(r^2+1) retained actual prefix matrices.
Bit complexity is 2^k times a polynomial in the ordinary input size. A failed
identity returns an actual sign assignment. Repeated signs remain correlated,
and every input and returned role participates in the endpoint.

In the commuting diagonal-sign native subclass, this decides equality at every
positive tensor width. Two words can be compared by appending the inverse of
the second to the first; k is measured on the concatenation. No small k is
asserted for the selected caller or the general hardness construction.

[PROOF.md](PROOF.md) gives the theorem, homogeneous span invariant, field and
bit bounds, native interpretation and exact limitations. The algorithm is

```text
for each instruction
  branch new signs; preserve every live sign
  transform actual prefix matrices within each live-sign assignment
  forget signs at their last use; retain a homogeneous span basis
check every final representative against the complete identity
```

The extra homogeneous coordinate distinguishes I from -I. A basis consists
of genuine prefixes with genuine assignments, so a failing representative
is a concrete counterexample rather than a formal linear combination.

## Source and novelty boundary

Hiroki KUMAZAKI's [PR #5716](https://github.com/CrocSwap/integer-mult-bounds/pull/5716),
head `946acb3a36953216dd9a39f0c5222a40a9e90cd3`, explicitly asks for a useful
restricted class with a tractable complete-endpoint identity test. This
package answers that open question with the bounded live-sign hypothesis.
Its CNF audit and Ali Romman's [PR #5369](https://github.com/CrocSwap/integer-mult-bounds/pull/5369)
reduction are cited, not rechecked as this contribution. Barrington retains
the classical five-role branching-program method.

Reachable-span reduction and concrete witness retention are classical; see
Stefan Kiefer's [weighted-automata notes](https://arxiv.org/abs/2009.01217),
Section 2 and its Schutzenberger/Tzeng references. The new contribution is
the live-sign-conditioned complete-endpoint application and explicit bound,
not a new general equivalence algorithm or a literature-priority claim.
zxv's [PR #5235](https://github.com/CrocSwap/integer-mult-bounds/pull/5235)
handles independent formal operators, and
[PR #5441](https://github.com/CrocSwap/integer-mult-bounds/pull/5441) handles
already supplied fixed transfer tables across tensor columns. Neither is
the repeated-sign lifetime bound proved here. Their methods retain credit.

Canonical base is `de5ec2e7a6074068452f45b1a191b5c72832df4a`, priority revision 8.
[SOURCES.json](SOURCES.json) pins the question and grammar documents; the direct
verifier checks their hashes without executing predecessor code. Selected
metadata and the task card are provenance only. This explicitly changes the
`formal-interface-lemma` card to an informal algorithmic side result; no proof
assistant build or selected assumption discharge is claimed.

The initial overlap cache covered 470 open PRs and 5,432 Discussion records
with complete reported pagination. Its local filesystem search was sparse,
so separate main-tree README searches and merged-PR searches were also used.
These searches do not cover unpublished work or every historical code diff.
[Advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19217826).

## Reproduction and evidence

From the repository root, with CPython 3.12 and its standard library only:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/sign-frontier-identity/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/sign-frontier-identity/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/sign-frontier-identity
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/sign-frontier-identity --check-source-history
```

Elsewhere substitute a CPython 3.12 executable. Expected direct status is
`PASS_SIGN_FRONTIER_IDENTITY`; registered replay ends with
`PASS_REGISTERED_RESEARCH_PACKAGE`. Each registered command has a 120-second
timeout. The direct checker writes a generated JSON receipt to stdout, binding
every package file by SHA256; redirect it outside the checkout if desired.
It neither reads a saved expected receipt nor writes files into the package.

The finite checks include:

- All 1,555 words of length zero through four over the declared six-gate
  alphabet, with 4,097 exhaustive sign assignments.
- 216 structured words on two, three and five roles, with 9,216 exhaustive
  assignments. A separate column-vector interpreter checks every input column,
  complete endpoint verdict and returned counterexample.
- Two 128-sign families. The width-zero negative family retains two matrices
  and returns a literal witness although its all-positive assignment is the
  identity. The width-one positive family preserves repeated-sign cancellation.
  Each processes exactly 512 candidates. These families are not exhaustively
  enumerated over their sign assignments.
- An eight-live-sign identity visiting all 256 live keys, with 1,020 candidate
  updates, plus five capacity/inverse fixtures. These cover the 4,096-gate
  limit, label 4,095, 64-bit coefficients, the empty one-role word and a mixed
  ADD/QUERY/APPLY/SWAP inverse.
- Eighteen invalid-input/capacity rejections and three semantic controls for
  homogeneous scalar phases, correlated repeated signs and independent signs.

The infinite statement rests on the written invariant and bit argument;
finite comparisons corroborate the implementation. Local normal/optimized
registered replay, source metadata and committed-byte/source-history checks
are separate from hosted CI and independent scientific acceptance.

## Limitations

The executable accepts 1..5 roles, at most 4,096 gates, frontier limit at most
eight, sign labels 0..4,095 and exact fractions with numerator/denominator
length at most 64 bits. It rejects larger inputs rather than narrowing its
verdict silently. The written theorem does not require these implementation
caps. It is an exact code API, not a native-source parser or general compiler.

Only commuting diagonal signs are covered. Arbitrary affine address changes,
quadratic phases, nonlinear leaves, rounding, ownership, physical routing,
precision/tapes and paid supplier costs need separate contracts. The test
does not supply a faster physical word or a new multiplication theorem.
No new kappa or selected-frontier change. Independent human and formal
proof-kernel review are unclaimed. No predecessor scientific suite, selected
cold replay, Lean or Docker run was performed.

## Implementation inspection

The bounded executable uses no recursion. All loops range over validated
inputs, finite sign branches, at most 256 live assignments and at most 26
representatives per assignment. An input check precedes frontier allocation.
State and witnesses are local to one decision. Scientific checks use explicit
exceptions and remain enabled under optimization. Functions stay below 60
physical lines. Warning-strict normal/optimized execution and AST compilation
provide the available standard-library diagnostics; no external static
analyzer is required or claimed.

Power-of-Ten rule 3 deviation: CPython and Fraction allocate managed objects
during elimination. This is confined to the validated solver domain above,
with two adjacent layers, at most 26 elimination rows per key and the
polynomial rational-size bound in PROOF.md. Capacity rejection and maximum
frontier/gate/label/coefficient fixtures verify the bounds. A fixed-allocation
implementation would be a separate lower-level port; no constant-RSS claim
is made. Rule 8/9 deviation: the verifier loads the single package-local
solver via a fixed importlib path, and rejection controls use bounded local
callbacks. No external path or callback is accepted. Normal and optimized
replay exercise every such target.

## Open next questions

1. Does a useful emitted caller in this subclass have small k after legal
   reordering? Extract labels and their first/last occurrences from one exact
   word before attempting reordering. A source-bound extraction contract and
   preservation of every dirty return are still needed.
2. Can one correlated family avoid explicit enumeration of its live signs?
   Begin with a precise replacement invariant. Large k remains exponential
   here; generic hardness is not contradicted.

[TASK.json](TASK.json) records the relevance, first step and blockers for both.
