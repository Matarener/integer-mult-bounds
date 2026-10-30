# Sharp spectral envelopes for shared BIT blocks

This contribution was produced by Nick Petalas. Apache-2.0.

**Scoped algebraic proof with exact finite corroboration.** For every
characteristic-two field, idempotent D of rank k in dimension r, and matrices
A+B=D, the sharp maximum of the total algebraic zero multiplicity is

```text
r       when k=r;
2r-1    when 0<k<r is odd;
2r      when 0<=k<r is even.
```

Explicit binary witnesses attain every case. When r>=3 is odd and k=r-1,
every maximizer consists of two single full-length nilpotent Jordan blocks.
The [proof](PROOF.md) gives the construction, upper bounds and rigidity argument.

JoyboyBrian's [PR #5507](https://github.com/CrocSwap/integer-mult-bounds/pull/5507)
handles shared blocks of size at most three in its complete four-support BIT
obstruction. Its triple exception is genuine. This new local law shows that
larger blocks can exceed the ordinary 2r-k bound by an unbounded amount.
Already at r=5,k=4 the exact maximum is 10 rather than 6, with a literal
coordinate witness in PROOF.md. The forced chain length is an additional
constraint for anyone trying to realize these local extremes.

The new contribution is this source-scoped spectral envelope and its chain
consequence. General nilpotent-sum theory and zero-diagonal splitting are
classical and credited in PROOF.md. This is not a larger-support global funding
theorem, a physical word, a complete invoice or a new kappa.

## Reproduce

Use CPython 3.12 and its standard library. From the repository root:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/shared-block-spectral-envelope/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/shared-block-spectral-envelope/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/shared-block-spectral-envelope
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/shared-block-spectral-envelope --check-source-history
```

Any CPython 3.12 path can replace the displayed local interpreter. The direct
marker is `PASS_SHARED_BLOCK_SPECTRAL_ENVELOPE`. The registered commands run
normally and under optimization, with admission checks enabled in both modes.

The complete finite evidence is 594 constructed (r,k) witnesses through r=33,
329,780 binary ordered matrix pairs through r=4, 66,066 independent
characteristic-polynomial comparisons, and ten domain/witness rejection
controls. The JSON stdout includes every census maximum and maximizer count.
Use `--receipt /absolute/external/new.json` for a generated receipt binding
all package files by SHA256. It refuses an existing receipt or a path inside
the package. Ordinary replay is read-only and creates no artifacts.

## Scope and predecessor credit

Base `de5ec2e7a6074068452f45b1a191b5c72832df4a`, priority revision 8.
The `bit-helper-contract` card changes to this local spectral side result,
rather than another G20 word search. The current baseline command passed
`PASS_RESEARCH_BASELINE_BINDINGS_ONLY`; it is metadata orientation, not a
scientific replay. Live PRs, handoff claims, local reservations and main's
formula/object terms were checked before claiming and are refreshed before
publication. Cached search is a lead, not a novelty certificate; unpublished
work and exhaustive older Discussion coverage remain outside that search.

Credit JoyboyBrian #5507 for the larger-support boundary, the genuine triple
exception and its global compensation; Ali Romman #5456 for the early-helper
support model; and the retained #5452/#5388/#589/#555 BIT, native, owner and
compiler lineage. Their results are cited at their stated scopes. No
predecessor scientific replay or audit is the deliverable. The classical
trace, primary decomposition, Jordan and triangular-splitting methods retain
their mathematical attribution. No claim of general linear-algebra priority
is made. Exact provenance hashes are in [SOURCES.json](SOURCES.json).

## Limitations and unrun obligations

Only characteristic two is covered. The binary census is complete only through
dimension four; higher dimensions and other fields rely on the written proof.
Local attaining matrices are not chronological native controllers. Higher-support
global compensation, independent-symbol constraints, native chains, helper
ownership, physical coefficient realization, dirty restoration, tape, precision,
compiler and supplier/outer accounting remain unproved. No selected frontier
record changes. Independent human and formal proof-kernel review are unclaimed.
No Lean, Docker, heavy selected replay or predecessor replay is needed or run.
Every registered check runs locally; hosted CI is reported separately in the PR.

## Open next questions

- Can a larger-support caller compensate the exact local surplus using its
  native chain and ownership constraints? Start with one declared support size
  and its chronological block decomposition. The missing completed word and
  full target/paid invoice block a supplier claim.
- With a fixed upper bound on native nilpotent chain length, what is the sharp
  local envelope? Start at r=5,k=4 with chains of length at most four, which
  the proved corank-one rigidity already excludes from attaining 10. This
  package does not determine the next-best value or a global caller budget.

Structured questions and their blockers are in [TASK.json](TASK.json).

## Implementation bounds

The new code is confined to verify.py, with no external runtime inputs or
predecessor imports. All loops are bounded by r<=33, the binary r<=4 census,
its at most 4! permutations, or the at most sixteen receipt files. Functions
are below sixty physical lines. Admission uses explicit exceptions and remains
active under optimization. Normal replay writes only stdout; optional external
receipts use exclusive creation and scoped file closure.

Power of Ten rules 3 and 9 have managed-runtime deviations. Python integers,
tuples, lists and iterator objects allocate during computation; their capacities
are bounded by the fixed dimensions, at most 65,536 entries per census array,
and receipt files of at most 1 MiB each. Python's ordinary builtin iterator and
argument-parser dispatch are retained; callable targets are explicit and no
plugins or dynamic code are loaded. A fixed-memory native implementation would
be needed to remove those deviations. Warning-strict normal and optimized
execution, independent algebraic oracles and rejecting controls are the local
verification. Repository-wide diagnostic configuration is unchanged by this
isolated standard-library package.
