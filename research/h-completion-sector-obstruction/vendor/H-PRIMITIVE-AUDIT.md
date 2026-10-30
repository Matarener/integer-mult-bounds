# Independent H-branch primitive audits

These files extend the research branch without changing the frozen
conditional `kappa=0.0023` supplier or its outer audit. The local completion
and signed-owner checks pass. None establishes a larger complete kappa. Apache-2.0;
substantial OpenAI assistance.

## BIT: the actual nine-row completion is admitted

`bit_h_completion_audit.py` independently reads the retained PR589 word and
the proposed `PR589-H-NATIVE.json.gz`; it does not import the producer's
binary matrix or replay code. It reconstructs the producer matrix `V`, the
consumer matrix `U`, the selected invertible minor `V_A`, and

```
M = inverse(V_A)*V*U,
Uprime = U + E_A*M,
H = I + Uprime*V.
```

These formulas are over `F2`. Exactly `V*Uprime=0`, hence `H^2=I`.
The original `J=I+UV` is not involutive. The completion changes precisely
the nine selected response rows. The independent replay also reconstructs
the dirty-helper compensation, rather than inheriting a clean-input test.

Both chronological native words pass all 661 independent input columns,
including every one of the 439 arbitrary helpers. All 636 rational frame
projectors are independently reconstructed, and each actual MOVE has its
declared nested projector and paid rank. At each of the nine new contacts,
the actual source line `P_q` is the complement of the actual target
hyperplane. The physical quotient from the full frame to that hyperplane
is therefore exactly `D_Pq`. This identity is checked with the complete
tail reversal at column counts one and two; the projector identity proves
it for every positive column count.

The complete paid local profile is

```
{1:1332, 2:1342, 3:79, 4:44, 5:102, 6:11, 7:10}.
```

Its rank mass is 5,075, saving 54 relative to the original word. There are
11,955 literal XOR ADDs, 2,920 paid MOVEs, nine owned clear operations and
nine owned erase operations. One explicitly owned workstream suffices.
The common-frame H factor is a separate exact 1,452-ADD program.

### The nonzero erase is legal and is not free

Each correction gathers a specified linear combination of completed,
immutable source streams into the owned workstream, transforms that
workstream once, lets exactly one target read it, then discards it. The
discarded value is generally nonzero. This uses the retained
copy/transform/read/discard interface in
`notes/copied-centers-lemma.tex`: copying, pointwise reads and erasure have
linear complete-stream cost. It does not require a reversible return
transform. The independent audit binds that source and checks that every
gathered original remains unchanged throughout the episode.

The owned stream has no independent input symbol and supplies no
productive output credit. If a different model required every temporary to
be reversibly uncomputed, this invoice would need revision. The retained
model explicitly permits the paid erasure used here.

## BIT follow-up: three modified rows are sufficient and minimal

`bit_minimum_completion_audit.py` independently verifies a further local
improvement. Invertibility suffices for the two orientations if their
common-frame wrappers use `G` and `G^-1`, respectively. An involution is not
required for the free noncommuting stage factorization.

The actual no-COPY matrix `J` has rank 108 on 111 ports. Replacing its rows
106, 109 and 110 by source coordinates 0, 1 and 2 yields an invertible `G`.
The independent checker reconstructs this choice from the native word,
checks its exact two-sided inverse, and verifies that its correction has
rank three. This attains the lower bound for row-supported completion:

```
rank(J+E) <= rank(J)+rank(E) <= 108 + number_of_modified_rows.
```

Omitting any of the three displayed changes produces rank 110. This is a
minimum statement about modified rows, not a lower bound on all possible
native constructions or boundary decoders.

All four literal native variants pass all 661 independent input columns:
bare forward, bare reverse, forward with its `G` wrappers, and reverse with
its `G^-1` wrappers. Every common-frame scalar operation, rational MOVE
rank and actual target-line contact is checked. The complete local paid
profile is

```
{1:1326, 2:1342, 3:79, 4:44, 5:102, 6:11, 7:10},
```

with rank mass 5,069. The bare words contain 11,625 XOR ADDs, 2,914 MOVEs,
and three owned clear/read/discard episodes on one private stream. The
fully lowered scalar factors cost 6,166 ADDs for `G` and 6,222 for `G^-1`,
including all three-ADD swaps. With two wrappers, the full native ADD
counts are 23,957 forward and 24,069 reverse.

The global p3 accounting is also independently checked. Its raw rank
surplus is 645. The direct boundary correction still needs 666 rank-one
calls, leaving a complete rank surplus of `-21`. Independently enclosed
moments at saving `0.004` are positive before this correction and negative
after it. Thus the local improvement is real, while its direct global
completion remains unfunded even at rank potential. No larger kappa is
claimed from this result.

## Complex: the signed owner is an exact native monomial

`gamma_phase_audit.py` independently reconstructs each owner from the
authenticated native phase data. For all 112 ports and each of eight fresh
stages, let `G` be the actual binary owner and `d` its even linear Gaussian
phase defect. The signed monomial

```
Gamma = Z_d G,
(Z_d f)(x) = (-1)^parity(d & x) f(x)
```

is exact. The owner is symmetric, orthogonal and involutive; `Gd=d` and
`d dot q=0`. Thus the physical operations `G` and `Z_d` commute, and their
Fourier action is unambiguously

```
y -> G*y+d = G*(y+d).
```

The independent audit verifies

```
Gamma^2 = I,
Gamma*C_q*Gamma = C_q,
Gamma*F_(old9+fresh8)*Gamma = F_(old9+fresh8),
Gamma*(F_old9*C_q)*Gamma = i*F_fresh8.
```

All 896 native recipes pass. There are 137,984 exact evaluations at zero,
basis vectors and basis pairs. This is a complete certificate for each
degree-at-most-two phase over `Z4`; every other coordinate is fixed.
There are 616 character masks of weight four and 280 of weight eight.
Each bare owner fails an absolute-phase control, so omitting `Z_d` is a
real error. A physical translation cannot replace this coefficient
character: the two have different Fourier actions.

The audit also lowers every owner into explicit finite native address
instructions. Across all 896 recipes there are 46,080 XOR-bit operations
and 7,168 bit swaps, plus one coefficient-character pass per recipe.
These operations require no recursive Fourier query. Their actual compact
movement and scalar costs must still be included by a whole-word caller.
At `f` columns every identity lifts independently by column; the displayed
constant `i` becomes `i^f` and must be retained as an explicit scalar phase.

## What remains outside these certificates

The serialized p3 role controller was independently replayed in a free
noncommuting operator algebra. All 36 entries agree with its factorization,
but there are three distinct interval monodromies. The signed-owner identity
does not identify them or eliminate the physical `Q` gauges around them.
The direct three-boundary correction therefore still costs 672 rank-one
requests. A hypothetical shared correction costing 224 requests is a
separate, unproved construction.

The remaining integration needs actual whole-word signed-owner contacts,
their complete movement/scalar costs, and a boundary decoder that restores
arbitrary data while meeting the complete recursive budget. An embedded
query logger can be useful only if its changed helper outputs are also
restored or explicitly accounted for. It cannot retain independent clean
helper credit while leaving their query defects behind.

Replay from the repository root:

```sh
python3 -B research/kappa-rebuild/transfer-audit/h-branch/bit_h_completion_audit.py
python3 -B research/kappa-rebuild/transfer-audit/h-branch/bit_minimum_completion_audit.py
python3 -B research/kappa-rebuild/transfer-audit/h-branch/gamma_phase_audit.py
```

The adjacent receipts bind the exact source versions, detailed primitive
programs and checks. The manifest in this subdirectory is separate from
the frozen stable-audit manifest.
