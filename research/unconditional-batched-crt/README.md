# An unconditional route through batched CRT

This package submits a written unconditional construction of a fixed
finite-tape integer multiplication machine with

    T(n) = O(n (log n)^(1-kappa)),
    kappa = 0.00173097911567079247276057.

The claimed exponent exceeds PR4088's published conditional exponent by
more than 5.7e-25. The numerical increase comes from a sharper exact root
interval and smaller, explicitly paid outer losses. The main contribution
is the proposed discharge of the transfer premises, including a different
nonlinear CRT algorithm. It is not another improvement to the finite word.

This is an author-submitted mathematical proof, with substantial AI
assistance. Independent acceptance and formal verification are not claimed.
The executable checks prove the finite statements they report; none is an
all-size theorem checker. The selected repository frontier is unchanged.

## Proof and scope

[PROOF.md](PROOF.md) states the complete algorithm, fixed rational parameters,
all paid exponents, rounding and exact integer recovery. Its dependencies are:

| Part | Argument |
| --- | --- |
| Completed ordinary interchange | [BIT.md](BIT.md), [NORMAL-FORM.md](NORMAL-FORM.md), [FALLBACK.md](FALLBACK.md) |
| Balanced nonlinear CRT, dirty switches and sparse repair | [CRT.md](CRT.md) |
| Actual mixed native words, arbitrary-width lift and recursion | [COMPLEX.md](COMPLEX.md) |
| Fine primes, Gaussian circuits and current sparse values | [GAUSSIAN.md](GAUSSIAN.md) |
| Uniform inverse conditioning and conservative local corrections | [INVERSE-CONDITIONING.md](INVERSE-CONDITIONING.md), [HALO.md](HALO.md) |
| Premise-by-premise audit and execution limits | [AUDIT.md](AUDIT.md) |

The CRT bound is O(V p^(1-a2) ell^2 polylog(p)), where
a2=0.001733394791695384296 and ell=Theta(p^(1-epsilon)). It replaces
the O(Vd) route that fails when epsilon is this close to one. Guard sizes
pay the exponential-in-ell switch preparation on both complete fibers and
exceptional records. Cached chirp tables also remove a hidden d-factor scan.
The broad Gaussian inverse argument uses the capped shifted symbol directly;
it does not assume invertibility of arbitrary broad principal sections.

All hypotheses of the auxiliary lemmas are established at their call sites.
No GRH, unproved prime-interval assertion, fast computed-key sort, RAM lookup,
uninitialized scratch contract, or unpriced numerical oracle is a premise.
Small sizes use an elementary fallback. The eventual threshold and constants
are enormous; this is an asymptotic construction, not a practical multiplier.

Original card: `uniform-transfer-audit`; the explicit user assignment expands
its scope to the complete transfer. [TASK.json](TASK.json) records that change.
[SOURCES.json](SOURCES.json) pins 354 live inputs; seven byte-identical historical
exports have additional pins in [EXPORTED-SOURCES.json](EXPORTED-SOURCES.json).
The retained conditional documents keep their original status and credit.
Their premises are addressed by the new arguments, not erased from the sources.

## Reproduce

From the repository root, with Python 3.12 and numpy 2.3.5:

```sh
python3.12 -B scripts/research_package.py --package research/unconditional-batched-crt --check-only
python3.12 -B scripts/research_package.py --package research/unconditional-batched-crt
```

[VERIFY.json](VERIFY.json) declares every input and seven bounded commands.
They authenticate sources and fresh native receipts, certify the prime and
exact moments, check every strict cost margin, reject obsolete cost routes,
and exercise complete finite CRT/compact/union cases. The composed compact
fixture checks every one of 4,096 addresses through ten repaired layers,
with dirty controls and spectators. Normal and optimized arithmetic checks
must agree. Longer native and local-ring replays are retained as evidence;
their actual coverage and incomplete physical simulations are in AUDIT.md.

The exact cost ledger has positive slack in every row, including the
Strassen boundary, enlarged halos, membership arithmetic and tensor guards.
A passing ledger is necessary but does not validate the written constructions.

## Open next questions

1. Independent review of the all-size construction, beginning with CRT.md's
   total repair and COMPLEX.md's free-algebra lift. This is needed for external
   acceptance; no independent review is claimed here.
2. Formalize the compact-switch theorem and refine the fixed-tape construction
   to a checked implementation. The earlier Lean baseline proves a different,
   smaller exponent. Formalization is further validation, not a hypothesis in
   the written theorem.

## Credit

Prepared by Cinna Davis with substantial OpenAI Codex assistance. New work is
Apache-2.0. [NOTICE.md](NOTICE.md) and the unchanged predecessor notices retain
the source-specific attribution and boundaries.
