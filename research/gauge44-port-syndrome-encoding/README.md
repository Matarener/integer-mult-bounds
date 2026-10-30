# Gauge44 port-syndrome encoding and plane factorization

**Exploratory finite result. The selected κ is unchanged; no supplier integration is claimed.**

## Result

The selected gauge44 provider has a 112×8 centre-scatter matrix with 88 active
ports in 24 repeated-signature classes (16 classes of size four and eight of
size three), plus 24 centre-free ports. Within each repeated-signature class,
the selected 9-bit port labels are pairwise orthogonal over F₂.

Two exact local constructions follow from that structure:

1. A product of 104 integer row-add shears moves all centre signal into eight
   anchor rows; the other 104 rows become centre-free. An exact 20-entry
   readout recovers a pure centre signal. For a real port vector it returns
   `R T p + c`, so arbitrary residuals still need a consumer.
2. Pairing ports within those signature classes gives 40 orthogonal planes;
   an MRV completion pairs the remaining 32 ports. In a fixed-seed screen of
   500 completed matchings, all 500 admit an exact F₂ factorization
   `Σ Aₖ Mₖ Aₖᵀ = I₉`. The best sampled free-zero solution has 47 zero planes,
   four rank-one matrices and five rank-two matrices. Its raw port-support
   rank sum is 74: three rank-7 terms, one rank-8 term and five rank-9 terms.

   For the complete-plane reader tariff, each source and reader support is
   closed by including both ports of every matched plane it touches. The
   rectangular Gram rank of those closures is 81 for this candidate: all nine
   active terms have rank 9. The verifier checks the full 112×112 decoder
   identity and all 28,672 selected-plane endpoint inputs for that candidate.

The frozen predecessor's raw support-rank sum is 126; closing its source and
reader supports under the same complete-plane tariff gives 144. The new
candidate's tariff 81 is a 43.75% reduction for this finite decoder. This is
not an optimality claim: the 500-candidate screen does not cover every
matching or every binary solution.

The centre-basis-only detour is closed for this scatter. In either four-centre
block, every proper subspace contains at most 22 of the 44 weighted root-line
rows. Every nonzero centre functional therefore touches at least 22 rows, so
any linear change of centre basis has at least 176 nonzero scatter entries.
The current coordinates attain that floor; changing the port basis is the
distinct mechanism above.

## Consequence for the κ target

The selected record remains κ = `0.001672660197076918`. These are favorable
complex-side planning relaxations, not new κ results:

| Assumed local profile and coverage | Planning κ cap |
|---|---:|
| Candidate profile `{9:9}`, reader charge 81, two unpaid coordinates | 0.005545369479 |
| Same measured profile and charge, three unpaid coordinates | 0.010103325422 |
| Predecessor profile `{9:16}`, complete-plane reader charge 144, three unpaid coordinates | 0.007194512681 |
| All 5,603 local rank mass represented by fractional rank-16 children, reader charge 81, two unpaid coordinates | 0.012751469568 |

With the measured profile, the candidate crosses 0.01 in the planning model
only if the coverage law admits a third unpaid coordinate per live family.
The margin is narrow: the exact target relaxation is `0.9996848385`. The
current selected law, dirty-state restoration, native chronology, hosting,
precision, cleanup, bit-side contract and complete supplier bill do not
establish that assumption. The separate rank-16 row also clears 0.01, but no
such word or bit-side contract is supplied. The selected κ cannot be updated
from either relaxation.

The anchor encoding and plane factorization are related by the repeated
syndrome classes, but neither proof makes the 104 residual coordinates free in
the next consumer. A consumer that avoids paying for them is still the key
missing interface.

## Sources and reproduction

The word input is `CANONICAL-WORD.json.gz` inside the selected replay archive,
member SHA-256
`16bc0ebb04b4be6c0ade74badc6a0c0cdba4215eda86e4ff9f13abf8ecebd219`; the
archive SHA-256 is
`f1da80610bf33c58527f18ad63b4350d0b864e1d4486141ee17ac9bed4d529d6`. The
verifier rebuilds the scatter from its literal `cut` instructions and binds
its port labels to `DATA-PHASES.json`, payload SHA-256
`c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa`. It also
pins the predecessor paired-plane certificate and the exact ceiling engine.

From the repository root:

```sh
python3 scripts/research_package.py --package research/gauge44-port-syndrome-encoding --check-only
python3.12 scripts/research_package.py --package research/gauge44-port-syndrome-encoding
```

The registered checks use only Python's standard library. They replay exact
rational local algebra, the seeded pairing screen, raw support ranks,
complete-plane reader closures, the selected decoder identity and endpoint
cases, and four exact complex-side planning screens. They do not replay the
full native program.

## Open next questions

- Can a concrete next-call consumer accept the eight anchors and 104 residual
  coordinates without restoring the old port basis? Bind one producer and
  consumer, then price arbitrary residual compensation, storage, cleanup and
  both supplier caps.
- Can the 81-cost complete-plane reader factorization enter the selected
  complex supplier with native chronology, frames, hosting and restoration
  charged? First map its nine active terms to actual source and target routes.
- Can one legal consumer free a third coordinate per live family while
  retaining the 81 reader charge? This would clear the 0.01 planning screen;
  the present coverage identity proves only the incumbent allowance.
- Can the remaining local mass be delivered as rank-16 children alongside the
  81 reader charge? The favorable relaxation clears 0.01, but no such word or
  bit-side contract is supplied.
- Can a broader exact search lower the 81 complete-plane reader cost? The
  500-sample screen and bounded CP-SAT runs are not optimality evidence.

This source-bound finite result is not a lower bound on multiplication or a
complete multiplication theorem. It extends the selected-port paired-plane
work in Discussion [#1587](https://github.com/CrocSwap/integer-mult-bounds/discussions/1587)
and the rematched plane-mask work in [PR #3335](https://github.com/CrocSwap/integer-mult-bounds/pull/3335);
it optimizes a different finite decoder invoice. The three-unpaid and rank-16
planning levers are already screened in [PR #3344](https://github.com/CrocSwap/integer-mult-bounds/pull/3344).
The reader closure follows the
distinction audited in [PR #3398](https://github.com/CrocSwap/integer-mult-bounds/pull/3398)
and the complete-plane tariff in [PR #3447](https://github.com/CrocSwap/integer-mult-bounds/pull/3447).
It claims no priority over these predecessors. Prepared by OpenAI Codex at the
user's direction with substantial AI assistance.
