# Sharp cubic-query boundary with an original-b correction

Prepared by **apoursh** with substantial OpenAI Codex assistance. Apache-2.0.
**Scoped proof with exact finite corroboration; no new kappa.**

For the fixed cubic-reader program of Nick Petalas's
[PR6200](https://github.com/CrocSwap/integer-mult-bounds/pull/6200), retain all
r children `y += a^3; a += b`, then restore the arbitrary incoming sources
and reproduce the eager output. [PR6212](https://github.com/CrocSwap/integer-mult-bounds/pull/6212)
left the general three-versus-four dyadic query question open.

This contribution completely classifies the family that **contains a nonzero
cube of the original entry b**. This is a source-line requirement, not merely
the name of the register read while frames are changing. For every r>=3:

| r modulo 9 | Exact minimum appended cube queries in this family |
|---|---:|
| 0, 1, 2, 5, 8 | 3 |
| 3, 4, 6, 7 | 4 |

The lower bound allows arbitrary nonmonic dyadic forms and all invertible
dyadic source frames. All attaining programs have integer coefficients.
[PROOF.md](PROOF.md) gives the modular obstruction and explicit restoration.

The key obstruction is small. Modulo nine, two weighted cubes whose summed
a³ and a²b coefficients vanish must also have zero ab² coefficient.
A pure original-b cube cannot affect any of those three coefficients.
The forbidden residue classes have projected defect (0,0,3) or (0,0,6).

The new construction covers residues 0,1, where nonmonic source forms are
useful. For example,
`f_10=5(3a+10b)^3-135(a+3b)^3+670b^3`.
Starting at the actual deferred sources (a_entry+10b,b), its repair is

```
a -= 7*b
y += 135*a^3
(a,b) = (3*a+b, a)       # simultaneous source frame
y -= 5*a^3
(a,b) = (b, a-3*b)       # simultaneous inverse frame
a -= 3*b
y -= 670*b^3
```

Both sources temporarily mix and then return exactly to their entry values.
The two source frames and their implementation costs are explicit paid work.
The program retains all ten original child calls; it is not a runtime-saving
claim. The older three-query class and universal four-query construction are
credited to PR6212.

The unrestricted question remains open. In particular r=3 has a three-query
repair without a pure-b read, so the four-query entry in the table cannot be
reinterpreted as an unrestricted lower bound. That example is a checked scope
control. The theorem starts at r=3; PR6212's unrestricted r=2 result is separate.

## Reproduce

CPython 3.12 and the standard library, from the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/cubic-pure-b-boundary
python3.12 -I -W error -B research/cubic-pure-b-boundary/verify.py
python3.12 -I -O -W error -B research/cubic-pure-b-boundary/verify.py
python3.12 -I -W error -B research/cubic-pure-b-boundary/independent_check.py
python3.12 -I -O -W error -B research/cubic-pure-b-boundary/independent_check.py
python3.12 -B scripts/check_research_commit.py --package research/cubic-pure-b-boundary --check-source-history --check-modes
```

The runner registers both checkers in normal and optimized isolated,
warning-strict execution. All checks are bounded and read-only. The primary
checker follows exact cubic coefficients and source matrices, retaining every
child, restoring both sources and checking literal inverse programs. Its
obstruction certificate uses divided moments modulo three.
It replays 254 complete programs for r=3..256 (56 new three-query, 84 older
three-query and 114 four-query programs), plus nine explicitly separate
closed-defect fixtures near one million. All 729 physical two-form assignments
modulo three are checked; 249 satisfy the first two zero-moment premises.
Seventeen semantic and scope controls include singular/nonunit frames,
incorrect inverses, missing readers/restoration and entry-source classification.

The independent checker derives the child ladder by binary concatenation of
sparse polynomials and fits query weights by exact elimination. It enumerates
all 729 physical coefficient triples modulo nine: 33 weighted tensors,
21 projected tensors, and 57 distinct sums from 441 ordered projection pairs.
It checks 135 arities (3..128 and all nine residues near 9*2^80), including
30 nonmonic three-query schedules, 45 older three-query schedules and 60
four-query schedules. Mutation controls and the r=3 scope control exercise
the distinction between current-register b and the original-b line.

The finite quotient calculation is exhaustive for its modulus. The written
reduction explains why that finite obstruction applies at every arity in the
listed residue classes; the arity tests alone do not prove a universal theorem.
Separate AI derivations are not independent human or formal-kernel acceptance.
All four registered commands passed on CPython 3.12.14, macOS arm64. Actual
copies with a corrupted retained proof or a changed predecessor-head label are
rejected. Committed bytes/modes/source history, official export integrity and
read-only Git-free normal/optimized replays are the publication checks; their
results are reported in the PR separately from hosted CI.

## Scope, coordination and provenance

This is an explicitly changed algebraic side scope of `joint-query-controller`.
The initial unrestricted investigation was refined publicly to the exact
original-b family after the modular obstruction and attainment were found.
The [canonical claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19276156)
records that refinement. No selected-supplier acceptance gate is claimed.

Canonical base is `a5bff3bf133e482541c09eba4e773884bdb2b1b7`, priority revision 8.
Entry overlap covered the newest twenty PRs through #6212, the all-state
`cubic dyadic` search and newest fifteen visible handoffs. The sparse local
helper searched 30 of 8,623 HEAD note paths with no usable remote cache.
Coverage is bounded, not a novelty certificate.

[SOURCE-PINS.json](SOURCE-PINS.json) identifies PR6212 at
`9c159482e0495b6a97e17e629debe66a0ceb9466`. The
[retained proof](sources/pr6212-PROOF.md) preserves its exact interface,
constructions and attribution offline; its bytes match both the published
Git object and immutable GitHub raw URL, and are hash-checked during replay.
No predecessor executable is imported. The pending head is not asserted to
be an ancestor of this branch or authenticated by the source-history preflight;
that preflight covers the base provenance in [SOURCES.json](SOURCES.json).
All scientific runtime inputs are package-local and trigger package replay.

A prior binding-only baseline pass is reused after finding all 1,227 covered
Git paths unchanged. This is not a scientific cold replay. The selected
PR6030 record, kappa=781451/250000000 and its five framework assumptions remain
unchanged. Only this isolated research package is added.

The model excludes intermediate observations, output feedback, nonlinear
source changes, child fusion and approximate queries. Modulo nine is a
necessary image of exact dyadic arithmetic, not a substituted execution model.
An actual caller, native realization, source-frame implementation, precision,
routing, storage, dispatch and complete favorable paid bill are not supplied.
No Lean, Docker, selected cold replay or full multiplication proof is claimed.

## Credit

Nick Petalas retains PR6200's fixed-reader chronology, defect, rational theorem
and repair interface. PR6212 retains its dyadic results, earlier upper formulas
and open question. Sricharan Vagvala / theon199's PR1532, Adam Gall / PR1205
and Hanson Sun / PR1246 retain the quadratic and linear interface lineage.
Modular reduction and binary-form decomposition are classical; no historical
priority is claimed. Prepared for apoursh with substantial OpenAI Codex
assistance in derivation, bounded exploration, proof, separately authored
verification, mathematical audit, documentation and publication.

## Open next questions

1. **Unrestricted three-query repair:** classify the remaining arities when
   every query may involve entry a. Start with arbitrary nonmonic mixed forms
   in residues 3,4,6,7 and construct legal restoring frames, or prove a new
   obstruction. The present pure-b floor does not settle this.
2. **An actual caller and tariff:** determine whether a real fixed-reader
   interface requires the pure-b correction and whether the framed program
   beats eager restoration after every cost is charged. The missing backend
   and favorable complete bill block supplier expansion.

[TASK.json](TASK.json) records relevance, first steps and blockers.
