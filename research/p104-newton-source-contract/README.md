# Sharp source-local Newton entrance for the complete P104 word

The unchanged 5,398-event PR2586 word has the following sharp conditional
entrance among independent principal-ideal Gaussian Newton modules:

| Initial public role | Number | Required module |
| --- | ---: | --- |
| Y | 104 | 4 B_9 |
| N | 78 | 2 B_9 |
| X, D, G, Q | 176 | B_9 |

Here pi=1+i and B_9=E_9 Z[i]^512, with
E_9=[[1,0],[1,pi]] tensor nine. The statement concerns all event and native
stage prefixes, arbitrary independently dirty public inputs in the listed
modules, and eight owned private erasures. Multiplying the entire contract by
a fixed grid scale 2^-f preserves it. The requirements are sharp even against
lowering any single source's required exponent by one pi, including odd powers.

The result retains the ideal native change-of-chart identities as an explicit
source assumption. All 1,245 recipe records and their 2,070 occurrences are
bound to exact source bytes. Their 2,490 actual monomial wrappers have the
proved affine/quadratic phase alphabet. [PROOF.md](PROOF.md) gives the lattice
argument, exact scalar induction and lower bound. This is a restricted-state
contract, without an actual-caller admission or a supplier improvement.

## What this adds

Clear1nsight's [PR3382](https://github.com/CrocSwap/integer-mult-bounds/pull/3382),
exact `2834523b1cd4ea83ba7a043e2e2f5f3332cf9909`, establishes a phase-compatible
Newton domain for one complete local collector. The neighboring
[active producer/consumer claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/2750#discussioncomment-19008790)
examines that collector's actual 58-bank dependency cone, named downstream
uses and full bill. This contribution classifies a changed **global initial
product contract** for all 358 public roles and the entire unchanged word.
It does not claim the first-cone or consumer work, or physical preparation
of the stronger entrance. The distinction was recorded before continuing
computation in [our scoped claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/2750#discussioncomment-19008906).

The exact source-local criterion also avoids a false strengthening from
minimum-path propagation. That relaxation asks for 4 B_9 on N2 and N4.
Exact correlated coefficient collection proves that 2 B_9 suffices for both,
including all intervening transports and Y updates. This is a module-domain
improvement over that relaxation, with no new precision threshold or kappa.

## Evidence and replay

[RECEIPT.json](RECEIPT.json) is regenerated and compared in full. It contains
all 358 source exponents, the 182 attaining coefficients and their event cuts,
all eight erasure cuts, and the literal replay evidence. The implementation
imports no predecessor executable.

- An exact forward rational trace checks every scalar event and final logical
  dirty restoration. A separate backward adjoint trace checks all 182 lower
  witness coefficients.
- A complete dense signed fixture uses all 358 independently generated public
  inputs, checks Newton membership at 5,390 non-erasure event outputs and 7,682
  native wrapper/stage prefixes, compares all 358 outputs with a separate
  canonical chart oracle, and verifies all eight literal private erasures.
  Every actual pair is also compared with the credited signed-floor formula.
- All 182 literal one-source fixtures weaken that source by one pi, leave all
  other inputs zero, and fail membership or exact division by their witness
  cuts. These lower fixtures use actual native recipes and no chart oracle.
- Seven behavioral groups cover signed negative pairs, a component-integral
  nonmember, missing compensation, a changed half coefficient, singular
  wrappers, wrong occurrence binding, wrong-phase cleanup and reverse witnesses.
  Checks use explicit exceptions and remain active under optimized Python.

Standard-library Python 3.12 or later, from the repository root:

```sh
python3.12 -I -Werror -B scripts/research_package.py \
  --package research/p104-newton-source-contract
```

The registered commands run the full replay normally and with `-O`, plus the
behavioral suite under `-O`. For a source-complete export without Git/network:

```sh
python3.12 -I -Werror -B research/p104-newton-source-contract/verify.py
python3.12 -I -O -Werror -B research/p104-newton-source-contract/verify.py
python3.12 -I -O -Werror -B research/p104-newton-source-contract/test_contract.py
```

SOURCES.json pins the three actual live inputs from
`research/p104-rounded-collector/`. VERIFY.json lists them for export/CI
invalidation. To regenerate the receipt explicitly, use
`verify.py --write-receipt /path/to/RECEIPT.json` and review the resulting diff.
Ordinary verification writes no scientific artifact.

## Boundaries and next questions

The inherited equality of every native recipe to its ideal change of chart
has not been independently certified for every input column. The complete
fixture is finite evidence, not a replacement for that premise. No actual
input conversion, physical owners/routes/control, finite-width implementation,
fast recursive backend, consumer invoice, tensor-depth extension, selected
cold replay or formal proof-kernel check is supplied. Public restoration is
chart-aware; final physical frames differ from entry frames.

No new kappa, selected-frontier change, supplier admission, whole multiplication
theorem or claim of a free arbitrary-input implementation follows. The family
expansion decision is to retain one conditional contract and stop. Further
construction requires a compatible caller and a complete favorable bill.

## Open next questions

1. Can this exact global product domain be transported through an actual
   caller without paying back the benefit? This matters because conditional
   exactness is useful only when inputs are supplied. First compare the
   all-role criterion with the actual-caller investigation linked above.
   Entry encoding, physical availability and the full bill remain blockers;
   do not duplicate that active claim.
2. Can correlated initial conditions strictly enlarge the product domain?
   The theorem excludes correlations by hypothesis. First compute a small
   exact Newton-coordinate congruence kernel around the N2/N4 mixing pair.
   Any useful extension must retain every literal prefix and dirty endpoint,
   rather than test only completed-output equality. No broad search is
   justified before an actual consumer needs the changed contract.
3. Can all inherited native change-of-chart identities receive a compact,
   independently checkable exact certificate? Start with a stabilizer/phase
   representation and one recipe plus a wrong-global-phase control. The
   required universal native binding and review budget remain blockers.

## Scope, attribution and implementation limits

Task `p104-side-correction`, scope **changed** to the conditional whole-word
source-module question, scientific base
`6f100d4bb5083f8c35d96fd95a539811c62f245c`, priority revision 6. Entry overlap
covered 314 open PRs, 2,761 closed/merged PRs and 2,242 Discussion records, with
complete reported pagination and no warnings. Sparse local notes and unsearched
code diffs still limit that search. Exact source heads, the active neighboring
claim and current submission freshness are recorded in TASK.json/SOURCES.json.

Credit Clear1nsight for PR3382 and the active local-interface investigation;
ywz65 for PR2586's physical word and native recipes; Tekalign for PR3025's
signed-floor pair; Ross Richardson for PR3068 and the sharp Clifford-grid
work; Nick Petalas for earlier whole-word precision traces and canonical
chart code; Arham Tahir, Alejandro Zarzuelo Urdiales, Jose Manuel and the
retained P104/native/geometry/compiler/precision lineage. Classical Clifford
and Barnes-Wall constructions retain Nebe, Rains and Sloane's authorship.
Original input archives and source notices are unchanged. Nick Petalas.
Apache-2.0. Assistance disclosure is recorded in TASK.json.

The Python verifier is a bounded functional reference, not an allocation-free
or physical runtime. Managed allocation is the Power-of-Ten rule-3 deviation:
358 public arrays plus one private array have 512 complex entries each, source
bytes are hash-bound and bounded by 4 MB, the word has exactly 5,398 events,
and each native rank is at most nine. Intermediate verification copies and
exact integers are scoped and finite for these fixed fixtures. Recipe plans
have at most 1,245 pairs of 512 entries. All functions fit 60 lines, loops have
these explicit finite capacities, contracts survive `-O`, and no recursive
or dynamically evaluated predecessor code is used. A production backend
would need its own fixed capacities, bit-width proof and resource accounting.
