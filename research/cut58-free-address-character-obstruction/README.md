# A cut58 relation obstructs free-ADDRESS tariff characters

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: scoped mathematical proof with exact finite corroboration.
For the actual cut58 families, at every positive tensor multiplicity f,

```text
P W K P W = -T W K P K.
```

Consequently every scalar-fixing sign character satisfies
`chi(K) chi(W) chi(T) chi(P)=1`. Two of the three characters used in Ross
Richardson's separable 22f proof, `chi_W` and `chi_T`, therefore cannot
extend while keeping the rank-zero ADDRESS swap P even. Any extension of
either, if it exists, must be odd on P. Its odd-response count would then
have nonzero defect on a zero-native-rank adapter.

This answers a concrete part of Open next question 1 in unpaidmoon's
[PR #4149](https://github.com/CrocSwap/integer-mult-bounds/pull/4149).
That package leaves extension of the three characters to the enlarged
alphabet open. The new relation blocks the two stated extensions under
the free-adapter condition that native tariff counting requires. The
remaining `chi_KW` is not excluded by this relation; its extension is not
established here. No complete character classification is claimed.

[PROOF.md](PROOF.md) derives the relation by six-bit polynomial algebra,
with the scalar i factors kept outside the tensor powers. The minus sign
is independent of f. The relation holds with all six original spectator
bits and arbitrary further identity spectators.

This result changes the available proof strategy for the enlarged menu.
It supplies no cheaper six-bank cleanup and does not refute #4086's
separable 22f theorem. Physical ADDRESS costs, a complete native invoice,
BIT compatibility, ownership, compiler, precision/tape and analytic
obligations remain open. There is no new kappa or selected-frontier change.
Independent human and formal proof-kernel review are unclaimed.

## Reproduce

From the repository root with CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -I -B research/cut58-free-address-character-obstruction/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -I -O -B research/cut58-free-address-character-obstruction/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/cut58-free-address-character-obstruction
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/cut58-free-address-character-obstruction --check-source-history
```

Any CPython 3.12 installation can replace the local interpreter path.
Expected marker: `PASS_CUT58_FREE_ADDRESS_CHARACTER_OBSTRUCTION`.
The new verifier independently composes both words in two ways:

- Boolean multilinear polynomial arithmetic over Z/4Z derives their exact
  coordinate maps and phase coefficients.
- Literal action visits all 4,096 twelve-bit basis columns, including every
  spectator setting, and compares the complete address and Gaussian phase.

All 16 generator sign assignments are enumerated. Exactly eight satisfy
this relation, including four with P even. These are assignments not
excluded by this relation, not a count of actual group characters.
Boundary controls reject unsigned equality, omission of P, and moving the
outer phases inside even tensor powers. They also show why allowing P to
be odd escapes the specific obstruction. Checks remain active under -O.

Each run emits a generated JSON receipt bound to SHA256 hashes of all six
package files and the sole source input. It writes no files. No receipt is
handwritten. No predecessor executable, old group census, 22f endpoint,
selected cold replay, Lean or Docker check is run.

## Provenance and task scope

The base is canonical main `721c03822c421b7f7fcbb2598993b947c4d88419`,
priority revision 8. Source bindings are in [SOURCES.json](SOURCES.json).
The literal operator JSON from #4149 is the sole live input. Its README
and Ross Richardson's #4086 proof are historical provenance. No frozen
predecessor file or selected record is changed.

The picker suggested verifier engineering. The mathematical contribution
assignment instead takes a distinct explicit handoff under
`joint-query-controller`, with changed scope recorded in TASK.json. The
selected orientation passed `PASS_RESEARCH_BASELINE_BINDINGS_ONLY` after
materializing its sparse inputs. That is metadata orientation only.
The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19241949)
precedes the relation search. The first exact relation ended that search.

Overlap checks read live open PRs, this account's 200 latest PRs, recent
handoffs and active Discussions, current-main READMEs, merged PRs and the
card's cached overlap report. Sparse local-note coverage was incomplete;
direct Git searches supplemented it. Arbitrary diffs and unpublished work
are outside that coverage. No equivalent relation was found in those checks.

Credit unpaidmoon / #4149 for the ADDRESS menu and explicit character
extension question; Ross Richardson / #4082 and #4086 for the actual
operators, physical family conventions and separable tariff proof; and
icekylinx / #531, Rohan Arun / kernel92, Chris R / Clear1nsight and ToikY
for the retained native, phase and interface lineage. The predecessor
results are cited, not independently rechecked as the deliverable.

## Open next questions

1. Does `chi_KW` extend with P even and fix every represented-algebra
   relation at the needed tensor multiplicities? Start with a structural
   formula for that character or one new relation that excludes it.
   This matters because it is the retained test unexcluded here. Equation
   (3) alone is only a necessary condition, and tensor faithfulness remains
   a separate issue.
2. Can another invariant or an explicit word settle the enlarged six-bank
   cleanup price? Start with the exact cut58 matrix and a fully charged
   alphabet containing P. The present relation supplies no shorter word,
   complete enlarged-alphabet floor or physical implementation.

## Implementation bounds

Build the Lever supplies the rerunnable relation verifier. Prove It Works
supplies its separate polynomial and complete basis-action paths. The
Power of Ten scope is this one Python file. It has no recursion, external
process, dynamic source import or persistent mutable state. Loops have
fixed bounds: five letters per compared word, 12 address bits, 4,096 basis
columns, six symbolic variables with at most 64 monomials, and 16 sign
assignments. Functions are below 60 physical lines.

Python's managed allocation is an explicit rule 3 deviation. The fixed
polynomial, word and basis domains bound live collections; basis columns
are streamed. Source reads are limited to the fixed hash-bound input and
six package files. Warning-strict normal and optimized registered checks
provide diagnostics. No separate static type analyzer or formal proof
kernel is configured or claimed.
