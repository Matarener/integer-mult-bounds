# Exact counts of shortest unsigned connector words

This scoped proof gives a closed formula for the number of optimal schedules
at a one-source dirty-connector boundary, over every finite characteristic.
It also proves that the nonzero coefficient counts are equal exactly in prime
characteristic. The contribution was produced by Nick Petalas.

Let the only complete calls be `B: z += Bx` and `A: y += Az`, with arbitrary
dirty data, immutable source x and generic compatible linear maps over a
nonzero unital ring of exact characteristic m. For a nonzero integer residue
c modulo m, require `y += c ABx`, with x and z unchanged.

Every optimal word has m calls of each operator, hence length 2m. The new
result counts these words, rather than improving this elementary call floor:

```text
N_m(c) = (1/m) sum_{d | m} R_d(c) binom(2m/d, m/d),
R_d(c) = sum_{e | gcd(d,c)} e mu(d/e).
```

Here mu is the Mobius function and R is the integer Ramanujan sum. In prime
characteristic p every nonzero c has `(binom(2p,p)-2)/p` optimal words. Composite
characteristics have unequal nonzero counts. For example, the counts for c=1,2,3
at m=4 are 16,18,16. All residues with the same gcd(m,c) have equal counts.
Reversing any balanced word gives its same-length unsigned inverse.

[PROOF.md](PROOF.md) gives the complete all-characteristic proof from the
dirty-state action, a subset-position statistic and exact finite Fourier
inversion. It uses no finite census as a universal premise. N_m(0) is an
auxiliary **balanced-word** count; the zero target has empty optimal word.
The full zero-target length-2m count adds the two pure words to N_m(0).

## Evidence and reproduction

From the repository root, with CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/unsigned-connector-residue-count/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/unsigned-connector-residue-count
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/unsigned-connector-residue-count --check-source-history
```

Any CPython 3.12 path can replace the local interpreter path. The verifier prints
a generated JSON receipt with every package/input SHA256, followed by
`PASS_UNSIGNED_CONNECTOR_RESIDUE_COUNT moduli=31 residues=527`. It writes no
files. Both ordinary and optimized Python commands are registered.

The exact finite checks cover:

- All 527 residue counts at m=2,...,32, comparing the formula with a separate
  chronological dynamic program.
- All 250,950 balanced position subsets at m=2,...,10, plus literal dirty
  coefficient execution of all 17,574 balanced words at m=2,...,8.
- All 21,840 unrestricted length-2m words at m=2,...,7, finding 4,716 restored
  words. This includes the two pure zero-target words in each characteristic.
- 496 explicit nonzero-coefficient witnesses, 3,968 noncommuting two-coordinate
  dirty-input cases and 3,968 inverse roundtrips, through m=32.
- Eight controls for a missing position shift, a prime-only formula misused in
  composite characteristic, omitted source/readout cancellation, the wrong
  target coefficient, reversed AB order, a clean-only shortcut, and invalid
  executable-domain inputs.

The finite program restricts m to 2 through 32. The largest dynamic-programming
table has 34,848 integer slots. Subset enumeration visits at most binom(20,10)
objects per characteristic; literal words have at most 64 events. Functions
have no recursion, all scientific contracts use explicit exceptions, and
`-W error` diagnostics run in both registered modes. Python allocates dynamic
objects within those fixed finite bounds; fixed-memory execution is not claimed.

The card's first working control prints
`PASS_UNIVERSAL_CONNECTOR_BOUNDARY pairings=945 max_coverage=31 queries=74 leaves=182`.
The selected binding baseline also passes. These are orientation checks, not
part of the new counting proof or a cold replay of the selected construction.

## Attribution and scope

Ross Richardson's [#943/#934 lineage](../universal-connector-boundary/README.md)
supplies the complete-call dirty-connector interface and prefix viewpoint.
Riquelme Soares's [#4189](https://github.com/CrocSwap/integer-mult-bounds/pull/4189),
head `5fb3936dfc8082f438f21c72dd6ca49ff4366ae7`, supplies the unsigned F3
one-source problem, the mod-three count floor and its six optimal words.
Equation (2) of the new proof recovers that six-word count as its p=3 case.
The general count uses classical subset generating functions, finite Fourier
inversion and Ramanujan sums; no novelty is claimed for those tools themselves.
Concurrent [#4231](https://github.com/CrocSwap/integer-mult-bounds/pull/4231),
head `8a956cbc80dc55697fd3e214812ce567b5eca48f`, classifies the unsigned five-source
optimum by characteristic and also gives the one-source 2m call floor. That
floor is shared context; the new result here is its complete word-count law.
No pending executable or archived source is imported.

The `connector-alphabet-change` card is explicitly changed to this scheduling
side question. The characteristic-two coefficient premise changes; the
operations stay unsigned. This does not add a new connector operation or find
a selected-supplier saving. The neighboring five-source and signed-ring tasks
remain separate. Exact base and input pins are in [SOURCES.json](SOURCES.json).

All calls must include their complete implementation prices. Admission,
coefficient preparation, instruction storage, dispatch and word-dependent
physical routing remain additional. No concrete supplier caller, native/tape
implementation, precision analysis, outer multiplication theorem, formal-kernel
proof or new kappa is supplied. Independent human and formal proof-kernel review
are unclaimed. Apache-2.0.

## Open next questions

The structured questions in [TASK.json](TASK.json) give first steps and blockers.

1. Can these marginal coefficient spectra constrain simultaneous demands in a
   multi-source unsigned connector? A joint readout-position argument is needed;
   multiplying independent marginal counts would discard their correlations.
2. Can a concrete recursive caller choose among its minimum-length words to
   reduce fully charged routing? Start with one pinned caller and compare two
   schedules including all accesses and head returns. This package supplies no
   physical price for that choice.
