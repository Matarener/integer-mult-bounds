# Unequal-coordinate follow-up: integrality closes the four-register target

Douglas Colkitt, with OpenAI Codex assistance. 2026-10-10. Apache-2.0.

**No new finite supplier or multiplication exponent.** The proposed
`m=3, W=4, 11 rank-one calls` target fails a necessary integer covering test
in the specified alphabet. This happens before the determinant, scalar
mixing, chronological order, or full group-ring identities need solving.
The result is independently reproduced by exact finite enumeration.

The selected published conditional κ remains `0.000723571590007464` at
main commit `12a4934d15006e8c10f9b2264f13f8f341be802b`.
No publication or integration files were changed.

**Follow-up:** the [saturated-character matrix audit](../saturated-character-register/REPORT.md)
now excludes the specific 16-register, 40-call inventory in Section 5,
in every order and with arbitrary scalar idempotents in this model.
It still passes the scalar tests reported here. Sections 5–6 retain the
historical motivation; the later matrix obstruction supersedes their
proposal to synthesize that exact inventory.

## 1. The model being tested

Retain the common-target abelian register model of the
[first diagnostic](../small-width-register-diagnostic/REPORT.md):

`prod_j (I_W + ([A_j]-1) N_j) = [I_3] I_W`,

where `N_j` is any rank-one idempotent over F2. Every register carries
arbitrary input. Constant scalar mixing may be absorbed into the idempotents;
no register is uncounted clean workspace. A final scalar permutation is
normalized as in that model.

Allow

`A_j = alpha_j v_j v_j^T / (v_j^T v_j)`,

with **any integer amplitude** alpha and v on one of these 25 lines:

* three coordinate lines;
* six signed two-coordinate lines;
* four signed `(1,1,1)` lines;
* twelve signed permutations of `(1,1,2)`.

Opposite vectors describe the same line. Their squared norms are 1,2,3,6.
All nonzero moves have rational rank one. A common rational conjugation of
the complete alphabet does not change the conclusion.

This is not a result about arbitrary rank-one rational matrices, arbitrary
rational amplitudes, other vector directions, mixed-rank children, per-role
targets, or the non-abelian register model. It is not a lower bound for
integer multiplication.

## 2. Why the previous relaxation was insufficient

The previous round proved that the optimal weighted-character lower bound
for this enlarged alphabet is `s >= (5/2) W`. At W=4 it only requires 10
calls, so it did not exclude 11.

That is a real-valued relaxation. A physical word needs integer numbers of
each frame type. This round asks whether **any integer inventory** with at
most 11 calls satisfies all the individual character inequalities.

It does not. The exact integer minimum at W=4 is **12**. The ordinary
coordinate construction attains it, so this is a tight count obstruction
for W=4 within the tested alphabet.

## 3. Reduction to an exact integer cover

Clear denominators by `B=6A`. For every linear functional lambda with odd
diagonal coefficient sum, the target exponent `lambda(6I)` is 2 modulo 4.
The second-order group-ring rank lemma from the first diagnostic gives

`2W <= sum_j min(lambda(B_j) mod 4, -lambda(B_j) mod 4)`.

For clarity, the lemma maps `[A]` to `(1+t)^lambda(6A)` over
`F2[t]/(t^3)`. If k exponents are odd and l are 2 modulo 4, the first-order
coefficient forces `UV=0` for the odd-move scalar factors. Their second-order
contribution has rank at most `floor(k/2)`, and the remaining moves add at
most l. Since the target coefficient is `I_W`, one obtains
`W <= floor(k/2)+l`, and hence the displayed weaker inequality.
Using that weaker inequality makes a negative inventory result sufficient.

Symmetric B has six independent entries. Enumerate all **2,048** coefficient
vectors modulo 4 with odd diagonal sum. For each line:

* odd amplitudes have the same cost as amplitude 1;
* amplitude 2 modulo 4 gives the second cost profile;
* amplitude 0 modulo 4 contributes zero to all these inequalities.

The last kind of move can be discarded from this *necessary count test*;
we are not claiming it can be removed from an actual circuit. This
relaxation preserves the validity of rejection and covers unbounded integer
amplitudes, including negative amplitudes.

Duplicate inequalities collapse to **108 rows**. Duplicate nonzero frame
cost profiles collapse to **19 columns**. If x_c is the number of calls with
profile c, the question is exactly:

`x_c are nonnegative integers, sum_c x_c <= 11, and C x >= 8`.

`cover.txt` contains this matrix, its budget, and its required row score.
`audit.py` regenerates it from the rational projector definitions. It checks
the amplitude-residue reduction and retains a representative for every row
and column in `certificate.json`.

## 4. Independent rejection and controls

An initial Z3 integer query returned UNSAT. The retained certificate does
not depend on that result or on Z3.

The standalone C++ checker enumerates all column multiplicities with total
at most 11. At a partial assignment it prunes only if some inequality cannot
be met even by spending **all remaining calls on the best remaining column
for that inequality**. This is an optimistic upper bound; it cannot prune a
feasible completion. Otherwise it tries every remaining multiplicity of the
next column. Duplicate column removal loses no count solution.

The complete run visits **1,009,311 nodes**, with **812,446** branches pruned,
and finds no feasible inventory. It finishes well below its explicit node
and time caps. Reaching a cap produces UNKNOWN and fails the audit rather
than being interpreted as UNSAT.

Verification includes:

* a feasible 12-call inventory, independently checking its returned counts;
* 75 small covering problems compared against a separate exhaustive Python
  implementation, including feasible and infeasible cases;
* exact regeneration and hashing of the complete coefficient table;
* the earlier group's positive uniform-word and missing-child controls,
  retained unchanged in the preceding diagnostic.

This is a written reduction plus an exact computational certificate, not a
Lean formalization of the covering argument or the multiplication theorem.

## 5. A larger inventory passes the same tests

To check the scope of the obstruction, construct the following balanced
inventory algebraically. This is a calibration control, not a larger circuit
search.

| Directions | Copies of each line | Amplitude | Calls | Sum of frame matrices |
| --- | ---: | ---: | ---: | --- |
| 3 coordinate lines | 4 | 1 | 12 | `4I` |
| 6 signed pair lines | 2 | 1 | 12 | `4I` |
| 4 signed triple lines | 1 | 3 | 4 | `4I` |
| 12 unequal `(1,1,2)` lines | 1 | 1 | 12 | `4I` |
| Total | | | **40** | **`16I`** |

For W=16 this passes the determinant requirement `sum A_j=W I`. Every one
of the 2,048 character inequalities also holds: its minimum doubled cost is
32, exactly `2W`. The rank-one moment at coarse saving `0.08` is below one,
checked by the exact integer comparison `40^25 * 3^2 < 48^25`.

**None of this specifies a network.** No order, scalar idempotents, complete
second-order matrix solution, or uniform operator identity is supplied.
The determinant and scalar character counts forget these obligations.
No complex companion, finite compiler, or enlarged outer-domain theorem is
established.

The inventory explains why the four-register rejection must not be promoted
to an all-register impossibility theorem for the enlarged alphabet. It also
gives a concrete balanced object for a future mechanism discussion, rather
than an instruction to increase a solver budget blindly.

## 6. Decision after this bounded round

Stop the W=4, 11-call search in this alphabet. No chronological arrangement
or scalar mixing can repair a failure of its necessary count inequalities.
There is therefore no reason to run the full second-order matrix or uniform
identity search for that target.

The next useful design question is whether a balanced inventory like the
40-call control can be organized into a **shared register computation**.
Allocating independent moves to each register cannot help: each role's
three-dimensional target needs at least three rank-one moves by rank
subadditivity. A saving must use actual inter-register mixing and satisfy
all arbitrary-input restoration obligations.

Before starting a larger search, specify that interaction pattern. Then
require the complete second-order matrix equations and exact group-ring
identity, not merely their scalar rank bounds. A different four-register
alphabet is another option, but it should escape a named restriction with
an identifiable coding mechanism.

## Reproduction

Requires Python's standard library and a C++17 compiler:

```sh
python3 -B research/unequal-coordinate-register/audit.py
```

The compiler output is temporary and removed after the run. The script
recreates the input matrix, reruns both covering budgets and the brute-force
controls, and compares the exact results with `certificate.json`.
No source modifications, external solvers, or network access are needed.
