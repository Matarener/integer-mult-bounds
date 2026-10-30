# Remove three outer routing calls from the physical convolution

This contribution is produced by Nick Petalas. Apache-2.0.
Independent human and formal proof-kernel review are unclaimed.

The complete physical normalized convolution in Jose Manuel's
[PR3709](https://github.com/CrocSwap/integer-mult-bounds/pull/3709) can omit
its three materialized endpoint bit reversals. A small adapter keeps the same
bit-reversed record convention across both forward transforms, the polynomial
product and the opposite transform. The complete rounded output, widened
return descriptor, final scale and borrowed-port contract are unchanged.

The claim is a scoped program-refinement proof with finite corroboration.
For axis bit lengths a_i and P=p+sum a_i, it removes exactly

    3 ceil(sum_i floor(a_i/2) / 2^floor(.997 floor(log2 P)))

outer sparse-router invocations, plus their descriptors and materialized
returns. The four-address p=3 fixture removes exactly three. This is an exact
operation reduction, not a measured runtime factor or a new kappa.

[PROOF.md](PROOF.md) proves equality including the actual rounding, disk/grid
preconditions and ownership state. [adapter.py](adapter.py) changes only the
private Fourier reversal method supplied to the unchanged Convolution class.
It is imported inside the source package's authenticated cohort. Its raw
Fourier convention is internal to the complete convolution; a standalone
natural-order transform must continue to use the original Fourier API.

## Reproduce

From the repository root, using CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/reversal-free-convolution/verify.py --mode algebra
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/reversal-free-convolution/verify.py --mode physical
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/reversal-free-convolution
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/reversal-free-convolution --check-source-history
```

Any CPython 3.12 executable can replace that local path. Checks print a generated
JSON stdout receipt with status `PASS_REVERSAL_FREE_CONVOLUTION`, exact counts
and SHA256 bindings for all package files. Normal verification writes no files
in the checkout. The inherited authenticated loader uses temporary directories.
No receipt is handwritten.

The algebra mode checks 24 exact rounded packets with 4,248 output coefficients,
record-product equivariance on 4,248 coefficients, six failing asymmetric
omission patterns, 25 enumerated batching cases and five invalid geometries.
The physical mode executes the changed complete caller on one length-four
axis, ell=2, p=3 and 16 Gaussian coefficients. B exchanges records 1 and 2.
A nonzero character input and an imaginary second input give a nonzero rounded
output. The first physical replay passed in 298.24 seconds on macOS arm64,
CPython 3.12.15. It returned 224 bits at width 7, with SHA256
`ad81a1219dc838dd3cd05b2aa4fb93aa80b7dee0edc77c4e0fb3b149482da8e9`. The independent unfactored polynomial-Fourier and quadratic-product
reference computes the original natural-order output. The check includes
encoded-metadata preservation, scratch erasure and protected width-port
rejection. Host-decoding guards remain active during the physical execution.

## Scope and credit

This answers Open next question 2 of Jose Manuel / jmbarrancoml's
[PR3640](https://github.com/CrocSwap/integer-mult-bounds/pull/3640), using his
later PR3709 record-local consumer. Their complete transform/product theorems
and native, tape, exact-grid and arithmetic premises are cited dependencies.
They are not re-audited deliverables. Frozen source notices and predecessor
credit remain unchanged. Exact live inputs and historical task provenance are
in [SOURCES.json](SOURCES.json).

Compatible DIF/DIT order is classical. The retained upstream synthetic
interface and androolloyd's indexed-read
[PR673](https://github.com/CrocSwap/integer-mult-bounds/pull/673) already use
bit-reversed-order convolution. PR3709 applies it inside its coefficient FFT.
The new work applies the cancellation to the three still-paid outer reversals
in this actual fixed-tape composition. It does not claim a new FFT identity.

The base is canonical main `19fdb086ea96af9a9f87936a2b888e10af4ed810`, priority
revision 8. The selected binding baseline passed after materializing its sparse
inputs. Live open PRs, recent account contributions, the handoff discussion,
merged PR bodies and main README terms were checked before the
[advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19228351).
The cached overlap scan covered 393 open PRs and 5,629 Discussion records;
sparse local-note coverage was incomplete. Direct main Git searches supplemented
it. No search proves novelty against unpublished work or arbitrary code diffs.
The card scope changes from a selected assumption audit to this enabled
physical consumer improvement; no selected assumption is discharged.

The physical fixture uses the inherited direct/literal q2 child and reduced
test guards. Production GL64/O73 execution, Lean, Docker, the selected cold
replay and the full Gaussian/CRT/integer join were not run. All selected
framework assumptions and predecessor admission limitations remain. The
conditional asymptotic exponent and selected frontier are unchanged.

## Open next questions

- Bind this alternative intermediate convention to one complete physical
  Gaussian or CRT caller. First replace its Convolution owner and prove all
  input disk margins and output narrowing bounds at that call. The remaining
  field-layout, precision and integer-recovery obligations block a full join.
- Count the removed routing work for one production-sized encoded shape.
  First obtain its exact axis lengths and b, then retain the supplier's full
  cost ledger. A measured runtime factor needs a separately budgeted experiment;
  this exact invocation reduction does not supply one.

## Implementation limits

The new adapter adds no payload state, recursion or data-dependent loop. The
reference is bounded to three axes, six address bits, ell<=4 and two rows.
Each exact transform has at most 2*64*64*16 coefficient terms; each local
product has at most 2*64*16^2 terms. Batch examples use at most 64 axes of
256 bits each. Input and output invariants use explicit exceptions under -O.
The finite physical fixture is fixed and inherits the bounded encoded loops
and temporary-owner cleanup of the cited source implementation.

Power of Ten deviations: Python integers, Fraction and lists allocate during
bounded verification; no fixed-allocation runtime claim is made for the new
reference. The inherited physical engine uses its existing recursive Karatsuba
multiplier and dynamic cohort imports; neither is newly implemented or claimed
compliant here. The adapter uses one inherited method dispatch with a fixed
concrete target. Warning-strict normal/optimized execution, AST inspection and
package/source-history checks provide diagnostics; no separate type checker,
linter or proof kernel was run. Frozen predecessors remain unchanged.

The managed-runtime deviation is limited to `reference.py`, `checks.py` and
`physical.py`: Python requires dynamic integers and containers. Enforced small
reference geometry and fixed physical inputs bound live state; normal and
optimized algebra checks exercise the bounds. A future native reference would
need fixed-capacity arithmetic before claiming Rule 3. The frozen Karatsuba
recursion and cohort loader are unchanged Rule 1/8 dependencies, scoped to the
authenticated predecessor contract. Source SHA256 checks and the complete new
physical execution are the compensating controls. Replacing those mechanisms
requires a separately reviewed predecessor change, rather than a mutation of
pinned evidence. No fixed-allocation or recursion-free physical backend claim
is made. All new functions fit within 60 physical lines.
