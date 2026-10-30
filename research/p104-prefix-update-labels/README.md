# Optimal prefix labels that keep their length under P104 updates

This contribution was produced by Nick Petalas. Apache-2.0.

The rank-two, step-two defect signatures in Ross Richardson's
[PR3070](https://github.com/CrocSwap/integer-mult-bounds/pull/3070) admit an
exact binary prefix code with mean length **39/8 bits**, under a uniform
initial distribution on the 64 period cosets. This saves **9/8 bits** against
six fixed-width bits. Every permitted source update preserves the length
of the particular label being updated, so adjacent packed labels need not
move merely because this label changes. The maximum length remains six.

Claim type: a scoped coding proof with an exact finite certificate, conditional
on the cited signature/fiber description. The state counts, floor word and
minimal-state theorem are predecessor results. They are not rechecked here.
This is an average-storage side result, with no new kappa or paid supplier.

## Contract and code

Fix one real coordinate j of the historical rank-two signed-floor word.
Updates are integer multiples of 2e_j, supplied as instructions to a code-only
update operation. PR3070 gives 33 minimal signature states on 64 period
cosets, with eight fibers of size one, twenty-four of size two and one of size
eight. Its exact signature is S(x)=(D(x+h)) for the permitted update subgroup H.
We use that published profile and signature contract as premises.

Assign a stable ordering within each fiber-size class. The code is:

| Fiber size | Number of states | Codewords | Length |
|---:|---:|---|---:|
| 8 | 1 | `000` | 3 |
| 2 | 24 | five-bit integers 4 through 27 | 5 |
| 1 | 8 | six-bit integers 56 through 63 | 6 |

These 33 words are prefix-free, with Kraft sum one. A source coset is not
encoded individually; each word identifies its entire minimal signature
state. The mean is `(8*3 + 24*2*5 + 8*6)/64 = 39/8`.

Translation permutes signature fibers bijectively and preserves their sizes.
Since length depends only on fiber size, every permitted update preserves
length pointwise. This remains true for adaptively selected update instructions.
The initial distribution determines the expected length; no claim that an
adaptive update preserves the uniform distribution is needed. The inverse
instruction gives the inverse encoded update. [PROOF.md](PROOF.md) proves
these statements and mean-length optimality among binary prefix codes and,
using the classical Kraft bound, uniquely decodable state codes.

The mapping from an actual signature to its stable within-class index is a
mathematical labeling, not a supplied fast encoder. A length-preserving
permutation is not a free reversible gate.

## Evidence and reproduction

From the repository root:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/p104-prefix-update-labels/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/p104-prefix-update-labels/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/p104-prefix-update-labels
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/p104-prefix-update-labels --check-source-history
```

Another CPython 3.12 executable may replace the local path. Standard library
only. Both registered commands have a 60-second timeout. The checker emits
`PASS_P104_PREFIX_UPDATE_LABELS mean_bits=39/8 max_bits=6` and a generated
receipt bound to package and source hashes. It writes no files.

The finite certificate checks all 33 codewords, the 64-element weighted
source model, every same-weight state transition, concatenated label boundaries,
and fifteen rejecting controls. Coverage includes all 641 same-weight state
pairs and 21,153 packed two-label updates. These pairs cover the length property
for a superset of possible source updates; the actual P104 update tables are
not reconstructed or checked. It reads the published
fiber profile without importing or executing predecessor mathematics. The
universal update/optimality statements rest on the written proof.

## Limitations and next decision

The mean assumes an initially uniform distribution on period cosets. There
is no improvement in worst-case label width, no rank-seven result, and no
physical encoder, update circuit, source distribution mechanism or complete
consumer. Dictionary/instruction storage, code acquisition, output, movement,
exact numerator and dirty restoration remain charged or unknown. The next
construction round is not justified until those costs and an actual input
contract are supplied. No selected cold replay, Lean, Docker, framework
assumption discharge or complete multiplication theorem is claimed.
Independent human and formal proof-kernel review are unclaimed.

## Open next questions

1. Can one physical retained-source consumer generate and update these labels
   at a favorable complete cost? First bind a literal caller and charge every
   encoder, lookup, bank, instruction, output and restoration. Those physical
   implementations are missing.
2. Does an actual input contract justify uniform period cosets or another
   paid distribution model? First specify its source distribution and all costs
   of enforcing it. The selected worst-case contract supplies no such promise.

## Credit and provenance

Ross Richardson's PR3070 supplies the exact signature-state description,
fiber profile and update contract, following his PR3059. Tekalign's PR3025/3033
supplies the floor word; Nick Petalas's PR3035/3037 supplies the earlier period
lattice; Arham Tahir's PR3046, ywz65's PR2586 and the retained P104/native
lineage retain credit. Prefix coding, Kraft's inequality and the entropy bound
are classical. The new step is this exact finite code and its pathwise
length-preserving update consequence for the cited P104 profile.

Canonical base is `a5bff3bf133e482541c09eba4e773884bdb2b1b7`, priority revision 8,
selected conditional kappa .003125804. `SOURCES.json` pins the published input
bytes. `TASK.json` records the change from the original side-correction card.
The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19279684)
followed live overlap, account-history, local-reservation and distinctive
main/merged searches. Sparse notes, unpublished work and a complete historical
literature search remain coverage limits. No predecessor result was audited.

## Implementation bounds

The new checker has 33 labels, 64 weighted source points, 12-bit parsed test
streams and a 200,000-byte limit per published input. Its largest function has
35 physical lines. Loops have finite bounds from these fixed domains. Managed
Python allocation is a Power of Ten deviation; live code/test structures are
bounded by the declared sizes, and the checker writes no files. Warning-strict
normal and optimized execution provide the available diagnostics; Ruff is not
installed. No shared verifier or predecessor code is changed.
