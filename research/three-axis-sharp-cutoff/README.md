# Sharp three-axis native monomial cutoff: seven

This resolves the least-three-axis-cutoff question explicitly left open in
[PR #5529](https://github.com/CrocSwap/integer-mult-bounds/pull/5529): the
sufficient tensor window **7,8,9,10 is sharp**. The addition is a nonzero
fixed group-algebra residual invisible at widths 1..9 and visible at ten,
plus the four exact central-residue kernel thresholds `(8,9,10,7)`.
The complete multiplication exponent **does not change**.

## Scope and evidence

The [proof](PROOF.md) uses classical binary coding theory and an explicit
168-term GL(3,2) cancellation. Zero phase forces a doubly even code. Three
independent rows would have seven nonzero codewords of total weight at
least 28, impossible below seven columns. A finite integer coset certificate
then kills every remaining low-width tuple; a full-span tuple exposes the
residual at each threshold. No modular-rank experiment is used as a lower proof.

The monomial grammar, Fourier separation and sufficient upper bound remain
Ali Romman's contributions. Fixed external coefficients and complete dirty
inputs/returns are essential. This excludes Hadamards, width-dependent
programs and physical supplier costs. It is a written computer-assisted
proof with separately implemented finite checks, not human or proof-kernel
acceptance or a complete multiplication proof.

[RESULT.json](RESULT.json) binds the primary result. Checks cover 168 linear
maps, all 294 plane cosets, an integer idempotent identity, all 43758
multiplicity vectors through width ten, all 2048 phase characters, literal
Gaussian phase sums, four threshold diagonal entries and six semantic
coefficient/quadratic-phase rejection controls. A separately written audit
reconstructs the group from permutations, solves the coefficient equations
over rationals, checks all 65536 residue vectors and all 299593 ordered
words through width six (784 zero-phase words and 27496 output fibers).
Both implementations were written in the same agent context, not by an
independent reviewer.

The user explicitly requested a mathematical attempt after a tooling round.
[TASK.json](TASK.json) changes the `formal-interface-lemma` card to this
written interface theorem; no Lean formalization is claimed. Canonical
base is `32890bc5de034ab8fc93ac88ead7279a6a416d04`, priority revision 7.
[SOURCES.json](SOURCES.json) pins the original native grammar proof at that
base. [SOURCE-CONTEXT.json](SOURCE-CONTEXT.json) identifies the byte-exact
pending PR5529 README snapshot and its immutable Git blob. Neither predecessor
executable is imported or changed.

## Reproduce

Python 3.12, standard library only, from repository root:

```sh
python -B scripts/research_package.py --package research/three-axis-sharp-cutoff --check-only
python -B scripts/research_package.py --package research/three-axis-sharp-cutoff
```

The registered commands run each implementation normally and with `-O`,
isolated and warning-strict, with a 60-second cap per command. Expected
lines: `PASS_THREE_AXIS_SHARP_CUTOFF`, `PASS_THREE_AXIS_SEPARATE_AUDIT`,
then `PASS_REGISTERED_RESEARCH_PACKAGE`. Direct verifiers also work in an
official Git-free export containing the declared grammar source.

Selected baseline bindings remain unchanged. No selected cold replay,
physical native supplier, compiler/stock/precision/outer admission, Lean
or Docker execution is part of this package.

## Open next questions

For a higher axis count, look for a similarly explicit stabilizer-kernel
witness at the last pre-threshold residue. This would distinguish sufficient
character realizations from a sharp representation threshold; the blocker
is the absent higher-dimensional annihilator, not numerical root precision.

A physical application should first bind one complete source program and
all its dirty inputs/returns to this exact three-axis grammar. The theorem
alone supplies no physical invoice or compiler admission. Structured first
steps and blockers are in TASK.json.

## Credit

Prepared for Joseph Anglada (@fluorine), with substantial OpenAI Codex
assistance in derivation, programming, checking and writing. New work is
Apache-2.0. Credit Ali Romman for PR5369/PR5529 and the open question;
Hiroki KUMAZAKI for PR5522's two-axis sharpness and representation-kernel
distinction; Mihir Srivastava for PR5521; Jose Manuel, ywz65, Chris R and
the retained native/phase/compiler source lineage. The finite Fourier,
GL(3,2), doubly-even-code and simplex-code ingredients are classical.
No global literature-priority claim is made.
