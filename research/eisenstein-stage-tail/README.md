# A uniform tail bound for the Eisenstein stage census

This scoped written proof was produced by Nick Petalas. Apache-2.0.

In the historical `B_K` forced-slot model of Rohan Guliani / Rohansguliani's
[PR #801](https://github.com/CrocSwap/integer-mult-bounds/pull/801), put
`h/k=4` and `x/k>=25/40`. For **every odd stage count `s>=15`**, the
positive saving ceiling satisfies

```text
X(s,4,25/40) < 9/1000.
```

This closes the tail in the cost-25 case of #801's first Open next question.
Together with its cited, unreplayed `s=3,5,...,13` enclosures, it gives
`X(s,4,25/40)<1/99` for every allowed stage count. Increasing the copy cost
can only lower this ceiling. Thus more stages cannot rescue the historical
cost-at-least-25 route at that target. This is a necessary bound under a
declared accounting model. It supplies no decoder or multiplication theorem.

The new result is the infinite tail inequality and its short rational
certificate. The earlier finite census, geometry, copy-cost floors and
slot-domination theorem are cited premises, not new verification work.

## Exact model

Normalize `k=1`, so `h=4`, the active climb is `a=3`, and the copy charge
per port is `x=5/8`. Write `s=2K+1`, `K>=7`, and `m=6K+4`.
The pressure at saving `q>=0` is

```text
F_K(q) = sum_slots mass * ((m/cap)^q - 1),
D_K = (6K-5)/8.
```

The ceiling `X` is the unique positive solution `F_K(X)=D_K`.
All masses are positive and every cap is strictly between zero and `m`,
so the pressure is strictly increasing from zero to infinity.

There are two active wires at every stage, each with a rank-three climb.
The copy slot has cap four. The idle stretches are those of the retained
`B_K` schedule. Pair zero is active at stages `0,1,2`. Pair `p>=1` is
active at `2p+1,2p+2`; its initial idle stretch is cut by the bridge read
after `2p` stages. Both bank copies are charged. Grouping these slots gives

| Cap | Total mass |
|---|---:|
| `3` | `12K+6` |
| `4` | `(58K-43)/8` |
| `6p`, for each `1<=p<K` | `24p` |

For the last row, the pair-zero tail and the other pairs' initial/final
stretches give two copies of each length `6p`, each with mass `2*6p`.
The `K-1` bridge fragments each have rank three and mass six, hosted with
cap four. They combine with copy mass `5(2K+1)/8` in the second row.
These are exactly the `thm` slots of the pinned `skel.py` specification.
No helper can be counted as a free productive target in this model.

## Proof of the infinite tail

For `z>=1` and `q>=0`,

```text
z^q - 1 >= q log(z),
log(z) >= 2(z-1)/(z+1).
```

The first inequality is `exp(t)>=1+t`. For the second, subtract its
right side from `log(z)`. The difference vanishes at one and has derivative
`(z-1)^2 / (z(z+1)^2)>=0`.

Apply these inequalities separately to every slot. Let `L_K` be the sum
of `mass * 2(m-cap)/(m+cap)`. Then `F_K(q)>=q L_K`.
For the idle slots, the positive weights are `24p`, their sum is
`12K(K-1)`, and their weighted mean cap is

```text
sum(24p * 6p) / sum(24p) = 4K-2.
```

The function `f(t)=2(m-t)/(m+t)` has second derivative
`8m/(m+t)^3>0` for `t>0`. Jensen's inequality therefore bounds the idle
part of `L_K` from below by

```text
24K(K-1)(K+3)/(5K+1).
```

Keep the active and cap-four terms exactly. This proves `L_K>=J_K`, where

```text
J_K = 12(2K+1)(6K+1)/(6K+7)
    + 3K(58K-43)/(4(3K+4))
    + 24K(K-1)(K+3)/(5K+1).
```

The following exact identity finishes the proof:

```text
9 J_K - 1000 D_K = P(K) / [4(3K+4)(5K+1)(6K+7)],

P(7+t) = 15552 t^5 + 469044 t^4 + 5264496 t^3
       + 26053149 t^2 + 48011339 t + 476748.
```

Every coefficient is positive, so `P(K)>0` for every real `K>=7`.
The denominator is positive too. Consequently

```text
F_K(9/1000) >= (9/1000) L_K >= (9/1000) J_K > D_K.
```

Strict monotonicity of `F_K` gives `X<9/1000`, as claimed.
For `x>=5/8`, the copy mass increases and the deficit decreases, so the
same exclusion holds whenever the positive root exists. If the deficit
is nonpositive, there is no positive saving in this model.

At `K=7`, `J_K=2519527/4900` and `D_K=37/8`. These exact values are a
control on the new tail proof. The displayed polynomial is negative at
`K=6`; this proof intentionally starts at fifteen stages. It does not
replace the cited lower-stage census.

## Reproduction and evidence

From the worktree root, CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/eisenstein-stage-tail/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -O -B research/eisenstein-stage-tail/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/eisenstein-stage-tail
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/eisenstein-stage-tail --check-source-history
```

Any CPython 3.12 installation can replace that local interpreter path.
The last command needs the publication commit and full source history.
Expected markers are `PASS_EISENSTEIN_STAGE_TAIL`,
`PASS_REGISTERED_RESEARCH_PACKAGE` and `PASS_RESEARCH_COMMIT_BYTES`.

`verify.py` expands the rational identity by integer polynomial arithmetic,
then translates its coefficients by seven using the binomial theorem.
`oracle.py` imports no grouped profile or polynomial. It walks each bank's
literal stage activity and bridge boundary to reconstruct every idle
stretch. A second lower bound integrates `1/t` with four exact midpoint
pieces per slot. The two implementations agree on all grouped slots at
`1<=K<=128`; both pressure lower bounds exceed the deficit for all 122
tail cases. The rational identity is checked at all 128 values as a
finite control, in addition to its exact symbolic coefficient check.

The verifier rejects malformed/beyond-budget inputs and six separately
altered polynomial coefficients. It distinguishes omitted bridge mass,
an unpaid bank copy and a missing active wire, and checks the `K=6`
scope boundary. Checks use explicit exceptions and remain enabled under
optimized Python. Its stdout is a generated receipt bound to SHA256
hashes of all seven package files. No receipt is handwritten or stored.
Both registered commands have a 120-second limit and write no files.

## Scope, sources and credit

Scientific base is canonical main
`19fdb086ea96af9a9f87936a2b888e10af4ed810`, priority revision 8.
The selected binding-only positive control passed. The selected conditional
`kappa=0.00310045` is context, not an input to this inequality.
[SOURCES.json](SOURCES.json) pins the source question, model specification,
earlier finite evidence, original task card and selected context as
historical provenance. No predecessor executable is imported or replayed.

The `complex-rank-shape-decoder` card is changed to this narrow accounting
side result. Its physical-construction acceptance gate is not claimed.
The [advance CLAIM](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19221564)
predicted an exclusion below `1/99`; the proved tail bound is below
`9/1000`. Entry overlap covered 341 open PRs and 5,521 Discussion records
with complete remote pagination. Local notes were sparse, with 225 of
8,136 tracked note paths searched. Targeted main and merged-PR searches
were also read. This coverage does not establish absence of unpublished work.

Credit Rohansguliani / Rohan Guliani #801 for the finite label-field census
and tail question; DreamingOfClouds for `format-limits-corrected`, the
`B_K` forced-slot framework and its retained #446/#386 lineage; Jonathan
Lam #798 for the Eisenstein decoder setting; GamingPuzzled / Joel Pulikkan
#620 for the extension-ring geometry; and the Gaussian, Hurwitz and
pairing-rank predecessors credited in #801. Maximooch #1794 supplies a
different all-stage screen for complex windows `h>=7` at a historical
selected target. It is not the `h=4`, `1/99` result proved here.
The logarithm, Jensen and exponential inequalities are classical.

Field-to-rational and residue-field realization, changed coverage laws,
physical delivery, native operators, ownership, restoration, compilation,
precision/tape, stock and outer admission remain outside this result.
The historical `a/(1+a)` conversion is not applied to today's assembly.
No supplier or selected-frontier change follows. Independent human and
formal proof-kernel review are unclaimed. Lean, Docker and selected-operator
replay were not run.

## Open next questions

The remaining part of #801's tail question covers its other copy costs
and label windows. A useful first step is a complete signed-slot formula
for one of those rows, followed by its own tail certificate. This matters
for a valid all-stage ceiling rather than a finite-stage extrapolation.
No further census or construction expansion is justified by this package.
An actual extension-field supplier still needs its physical and native
interface before any such ceiling has an algorithmic consequence.

## Implementation bounds

The exact polynomial certificate, literal schedule and separate integral
lower bound are retained in the two new Python files. There is no recursion
or generated code; functions are below
60 lines. The APIs enforce `K<=128`, polynomial degree at most five and
at most sixteen integration pieces. Every loop is bounded by these limits.
State is local apart from immutable constants. File reads use a fixed
seven-file inventory and propagate failures. CPython allocation is a
managed-runtime deviation from fixed allocation within these finite bounds.
Python iterator dispatch is a language-level deviation from a literal ban
on indirect calls. Rejection callbacks have four fixed targets and execute
once per control; there are no extensible callback or plugin targets.
Warning-strict normal/optimized runs provide diagnostics without changing
repository-wide configuration.

Local CPython 3.12.15 normal and optimized registered commands passed in
0.259 seconds each. Metadata/pins and the registered package replay pass.
Three disposable source mutations reject an altered certificate coefficient,
an underpriced idle term and a shifted bridge boundary. Both direct modes
also pass in a read-only Git-free package copy with an empty `PATH`.
An unexpected CLI argument rejects. Hosted CI is separate from these local
checks. No external Python linter was available locally.
