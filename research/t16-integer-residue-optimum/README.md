# Sharp pooled T16 integer packing near the moment root

This package answers the quantitative integer-gap question left open by
[PR1914](https://github.com/CrocSwap/integer-mult-bounds/pull/1914),
[the selected T16 pattern audit](../selected-t16-pattern-dual/README.md).
For every real saving

`0.00167689 <= a <= 0.00167690`,

put `p = 1-a`. The exact minimum idle cost in the fixed-inventory **integer**
pattern relaxation is

`2431 + 17^p + 4887*48^p`.

The predecessor fractional optimum is
`89952/37 + (180832/37)*48^p`. The sharp positive integer gap is therefore

`17^p - 5/37 - (13/37)*48^p`.

At the lower root endpoint below, this gap lies strictly between
`0.02854988` and `0.02854989`. This is an unnormalized idle-cost difference,
not a percentage or a change in the selected exponent.

Adding every fixed paid local child gives the adjacent exact root bounds

`0.001676895884165954931459 < a_integer < 0.001676895884165954931460`.

Consequently, under the retained balanced conversion, every physical packing
that satisfies this fixed pattern contract has the necessary cap

`kappa < 83844794208297746573/50083844794208297746573`

which is less than `0.001674088611862993`. The predecessor fractional cap is
about `0.001674097969905391`. The new cap is tighter by about `9.358e-9`.
This is a sharp aggregate integer relaxation, **not an attaining physical owner
map, a new supplier, an improved selected kappa, or a multiplication theorem**.
No selected record or predecessor file changes.

## Fixed model and source binding

The source is selected PR1094's T16 word and disjoint whole-helper reservation
contract. The verifier recounts capacities and helper widths from the literal
PLAN and SPEC, and checks both against the selected source manifest. The
predecessor's original owner-map replay and physical admissibility are reused,
not rerun here. This theorem concerns the aggregate integer inventories:

| Bin capacity | Bins | Helper width | Occurrences |
| ---: | ---: | ---: | ---: |
| 8 | 10752 | 4 | 8064 |
| 16 | 7168 | 5 | 4608 |
| 32 | 7168 | 7 | 4320 |
| 48 | 7168 | 8 | 17568 |
| | | 9 | 34560 |

A pattern is a capacity `C` and five nonnegative integer counts `n_w`, with
`sum(w*n_w) <= C`. Its residual is `r=C-sum(w*n_w)` and its cost is `r^p`,
with `0^p=0`. Pattern multiplicities must be nonnegative integers and satisfy
all nine inventory equations. There are exactly 1,163 patterns. Timing,
per-call family conflicts, owner identity and offset constraints are relaxed.
Splitting helpers or reusing reservations changes this contract.

The 144 fixed calls each pay the local profile
`{1:2412, 2:418, 3:432, 4:142, 5:82, 8:8}`.
The normalized native moment in this relaxation is

`[144*sum(local_n_r*r^(1-a)) + idle_cost] / [14336*73^(1-a)]`.

All counted ranks are below 73. Every nonzero normalized term is strictly
increasing in `a`; hence failure of the minimum at one exponent excludes
all larger exponents for every packing, even outside the certified window.
Additional physical charges can only lower the resulting necessary cap.
Finite precision, outer inequalities, the bit supplier, all-size/compiler,
stock, tape, exact recovery and analytic obligations are not recertified.

## Proof by a 37-state residue potential

Reuse the predecessor dual numerator vectors, in capacity-then-width order:

```text
A = (8,16,32,0, -4,-41,-19,-8,3)
B = (6,12,24,37, -3,-3,-5,-6,-7)
```

For each pattern, add its capacity coefficient and its helper-count
coefficients to obtain `A_j,B_j`. Direct integer arithmetic checks
`A_j+48*B_j = 37*r_j` for every pattern. The inventories force
`sum multiplicity*A_j=89952` and `sum multiplicity*B_j=180832`.
Thus every integer solution has total `B` residue **13 modulo 37**.

Define the scaled reduced cost

`g_j = 37*r_j^p - A_j - B_j*48^p`.

On residues `s=0,...,36`, pattern `j` gives the directed edge
`s -> (s+B_j) mod 37` with cost `g_j`. The certificate provides an explicit
path from zero to each residue, using at most 36 patterns. Its cost is the
potential `P_s`, expressed as an integer linear combination of `r^p`.
The verifier checks `P_0=0` and every one of the **43,031** inequalities

`P_s + g_j >= P_((s+B_j) mod 37)`.

Of these, 829 are symbolic zero identities and 42,202 have strictly positive
certified slack throughout the entire stated real interval. Monotonicity of
each `r^(1-a)` encloses its value using the two rational interval endpoints;
signed interval arithmetic then checks each polynomial. The smallest strict
slack exceeds `0.022` in these scaled units. There is no assumption that the
stored paths are shortest: the checked inequalities are the lower-bound proof.

List the patterns of any integer packing in any order, repeating a pattern
according to its multiplicity. They form a walk from residue 0 to residue 13.
Summing the checked inequalities cancels every intermediate potential. Hence
`sum g_j >= P_13 = 37*17^p - 5 - 13*48^p`. Substitution gives

```text
37*idle_cost - 89952 - 180832*48^p
    >= 37*17^p - 5 - 13*48^p
idle_cost >= 2431 + 17^p + 4887*48^p.
```

The following integer inventory attains this bound. Counts are ordered by
helper width `(4,5,7,8,9)`:

| Capacity | Helper counts | Multiplicity | Residual |
| ---: | --- | ---: | ---: |
| 8 | 0,0,0,1,0 | 10752 | 0 |
| 16 | 0,0,0,2,0 | 1301 | 0 |
| 16 | 0,0,1,0,1 | 4191 | 0 |
| 16 | 2,0,0,1,0 | 1676 | 0 |
| 32 | 0,0,1,2,1 | 128 | 0 |
| 32 | 0,1,0,0,3 | 4608 | 0 |
| 32 | 1,0,0,0,3 | 2431 | 1 |
| 32 | 0,0,1,1,0 | 1 | 17 |
| 48 | 0,0,0,0,0 | 4887 | 48 |
| 48 | 1,0,0,1,4 | 2281 | 0 |

All nine equations and idle mass 237,024 are checked as integers. Adding all
paid local work gives total rank mass 1,041,408. The exact moment is negative
at the lower root endpoint and positive at the upper endpoint, which differ
by `10^-24`. These signs and monotonicity prove the root and necessary cap.

## Reproduce and verification

From the repository root, with Python 3.12 and the declared inputs materialized:

```sh
python3.12 -I -Werror -B scripts/research_package.py --package research/t16-integer-residue-optimum
python3.12 -I -O -Werror -B research/t16-integer-residue-optimum/verify.py
python3.12 -I -O -Werror -B research/t16-integer-residue-optimum/test_verify.py
```

`verify.py --write` deliberately regenerates only this package's RESULT.json.
Ordinary replay compares the whole fresh receipt against its frozen bytes.
Acceptance uses standard-library integers and Fractions, with binary square-root
products at 160 exponent bits and 256 fractional bits. No optimizer or floating
point enters acceptance. Exact rational-power tests check all ranks 0 through
73 at exponents 1/2, 2/3 and 6/7 by integer powering. A separate width-frontier
enumeration verifies the complete pattern domain.

Six behavioral groups reject omitted, nonintegral, overfull or changed-width
inventories, a wrong residue destination, an inflated potential with a valid
residue path, a changed dual coefficient, a changed source width, omitted paid
work and a false root sign. Checks remain active under `-O`. Source-byte drift
is rejected before arithmetic, and metadata pins bind the original task card
and selected record. Source-package integrity checks do not certify physical
admission.

Discovery used CPython 3.13.16, NumPy 2.5.4 and SciPy 1.18.1 / HiGHS to find
one integer witness after a floating residue probe. The frozen integer witness
and potential paths suffice for replay. CPython 3.12.15 and 3.13.16 were used
for verification. No proof assistant or independent human review is claimed.

## Open next questions

- Can a chronological T16 owner map attain this integer profile, or does a
  source-bound timing/family cut force a larger cost? Start by assigning the
  ten displayed patterns to literal selected bins, then bind actual helper
  occurrences and conflicts. The blocker is compatibility omitted by this
  relaxation. This is separate from the current PR3338 three-helper cycle task.
- Does a larger exponent interval admit the same integer optimum? Start with
  the existing potential polynomials and certified derivative bounds. The
  present proof only certifies `0.00167689 <= a <= 0.00167690`; failure of a
  wider interval enclosure would not disprove optimality there.

## Credit and engineering scope

Ali Romman's PR1129 supplies the fractional optimum and dual. Hanson Sun's
PR1914 independently binds it to the selected T16 model, extends its interval
proof and asks the quantitative integer-gap question answered here. Rohan
Arun's PR1094 and the retained PR1087, PR1018/987 and Hao Yan PR858 lineage
supply the selected packing inputs. Their original notices remain unchanged.
New material is Apache-2.0. Preparation used automated mathematical and code
assistance; no authorship or independent human review is assigned to a tool.

Build the Lever led to a stored residue certificate and executable verifier.
Prove It Works led to exact source checks, semantic rejection controls and
fresh receipt comparison. Separate Before Serializing Shared State led to
worker-owned outputs and OS locks for shared Git and task reservations.

Power of Ten scope is this package's verifier and tests. Every new function is
under 60 physical lines. Enumeration, paths and numerical precision have fixed
bounds; input failures use explicit exceptions that survive optimization.
Rule 3 has a managed-runtime deviation: Python integer/Fraction objects allocate
inside the bounded loops. Live state is limited to 1,163 patterns, 37 potentials,
74 power intervals and a 160-root chain per evaluated rank. The library's
allocation strategy is not inspected. Rule 8/9 has a test-only deviation for
`runpy`: it loads exactly this package's verifier into a read-only test namespace;
there are no plugin hooks, callbacks, recursion or external code targets.
Tests, optimized replay and static diagnostics cover these bounded paths.
Native code would be reconsidered only if this small finite checker became a
long-lived service. Discovery scripts and the solver environment are disposable.
