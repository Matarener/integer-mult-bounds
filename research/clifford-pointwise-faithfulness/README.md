# Pointwise Clifford tensor faithfulness and a complete frozen-repair obstruction

**Enabling proof and exact verification tools; no new kappa.**
For the full n-axis Clifford group, projectively distinct operators have
linearly independent tensor powers at **every width f>=4n+4**. Their
normalized tensor Gram matrix lies between **I/9 and 17I/9**. This holds
for arbitrary complex coefficients and finite words chosen separately at
each width. It gives a dimension-based threshold for the finite-alphabet
arguments used throughout the native-interface research.

For one fixed complete scalar register program over the Gaussian-dyadic
Clifford group, **four tests at 4n+4,...,4n+7 decide equality at all positive
widths**. Four tests are necessary because of scalar phases. At least one
of those four normalized squared residuals is at least M/9, where M is the
squared coefficient norm after equal exact operators are combined.

Read the [proof](PROOF.md), [exact result](RESULT.json), [source pins](SOURCES.json)
and [source-bound application](APPLICATION.md). The application strengthens
the retained passive saved-query ceiling: failure holds at every **f>=72**,
with worst-case operator error at least **1/3** in each affected coefficient.
At every f>=84 its normalized squared error is at least **125/126**.
The old observation contract and both source clarifications remain binding.

The [paid-repair extension](REPAIR.md) now proves that this caller needs
**at least 104 additional field returns**, even with feedback among new
calls. With q returns, the selected block has squared operator norm error
at least **(1-q/104)_+/9** from width 72. The cheapest possible 104-return
repair makes the complete frozen invoice adverse for **every r^p tariff,
0<p<=1**. Thus paying for added repairs cannot rescue this frozen word.
Changing an original paid input, capacity, free alphabet or target contract
requires a new analysis. The selected frontier does not change.
At the reference tariff from the pinned selected value, positive margin
permits at most 36 added returns. From width 84 every such approximate
repair has squared operator error at least **2125/3276**.

## What changes

| Class | New result | Boundary |
| --- | --- | --- |
| Projective n-axis Cliffords | Pointwise Gram lower bound 1/9 from f=4n+4 | Coefficients and finite word support may depend on f |
| One fixed dyadic Clifford register program | Four tests at 4n+4 through 4n+7 | Same program and exterior coefficients at every test |
| The same Clifford class at later widths | Lower bound 17/20 from 4n+8; 125/126 from 4n+16 | These also hold on four consecutive test widths |
| Projective pure stabilizer maps with N total input/output axes | Pointwise Gram lower bound 2/5 from f=2N+6 | Includes rectangular maps and projections; native scale is raised to f |

For n=9 the new complete test uses widths **40..43**, compared with
**69..76** in [PR #5376](https://github.com/CrocSwap/integer-mult-bounds/pull/5376).
For n=17 the windows are **72..75** and **133..140**. These are theorem bounds,
not benchmark speedups. The prior sharp one-axis window 5..8 remains better
than the new uniform window 8..11. The prior monomial-only theorem in
[PR #5369](https://github.com/CrocSwap/integer-mult-bounds/pull/5369) also keeps
its stronger cutoff for that smaller class. No optimal width is claimed here.

The proof counts all stabilizer overlaps by affine-support dimension.
The Clifford Choi states form a subset of the 2n-axis stabilizer states.
A signed-Pauli count halves their first overlap level. Exact rational tail
bounds then give the uniform positive Gram bounds. A separate residual-form
argument confirms the Clifford counting upper bound. Fourier inversion of
the four central phases gives the fixed-program test.

## Use the tools

Python 3.12 and the standard library suffice. From the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/clifford-pointwise-faithfulness
python3.12 -I -B research/clifford-pointwise-faithfulness/native_pointwise.py \
  research/clifford-pointwise-faithfulness/examples/native-9-identity.json
python3.12 -I -B research/clifford-pointwise-faithfulness/native_pointwise.py \
  research/clifford-pointwise-faithfulness/examples/native-9-phase-trap.json --width 40 --witness
python3.12 -I -B research/clifford-pointwise-faithfulness/stabilizer.py \
  research/clifford-pointwise-faithfulness/examples/projection-correct.json
```

The native tool reuses the pinned complete signed-word frontend and quadratic
sum kernel from PR #5376. It keeps every arbitrary input and every return.
Its input grammar is documented in the
[pinned predecessor](https://github.com/CrocSwap/integer-mult-bounds/blob/32890bc5de034ab8fc93ac88ead7279a6a416d04/research/clifford-tensor-gram/README.md#input-contract).
Without `--width`, read the `equal` field and `all-positive-widths` scope.
With `--width`, the result decides only that width and rejects widths below
the sufficient threshold. `--witness` returns a nonzero basis entry when
the endpoint fails. A successful process can report either equality or failure.

The projection frontend accepts a residual list of affine-quadratic maps.
Coordinates put output bits before input bits. A map gives an independent
binary support basis, offset, modulo-four linear phase, even quadratic
pairs and nonzero Gaussian rational scale. See the two projection examples.
It supports rectangular types, but it is not a complete nonunitary register
compiler. The native frontend still requires unitary operators.

No dense tensor matrices are built by these decision tools. Their cost is
polynomial in the expanded support, axis count, word length and width, with
exact scalar arithmetic. Program expansion may be exponential in program
length. The finite verification oracles do construct small literal arrays.

## Evidence and reproducibility

The registered normal and optimized isolated checks print:

```text
PASS_POINTWISE_CLIFFORD_AND_STABILIZER_NO_NEW_KAPPA
PASS_PASSIVE_CEILING_FROM_WIDTH_72_NO_NEW_KAPPA
PASS_104_RETURN_FLOOR_ERROR_TRADEOFF_AND_ADVERSE_REPAIR_INVOICE
```

The first check includes:

- Complete projective stabilizer orbits on 0..4 axes, ending at 36,720 states.
- Separate literal-Choi and signed-Pauli censuses of all 24 and 11,520
  one- and two-axis projective Cliffords, with matching overlap counts.
- Rational infinite-tail inequalities, 448 finite bound checks, and exact
  positive-definiteness checks of 6-by-6 and 24-by-24 shifted Gram matrices.
- 8,893 literal map entries, 3,837 pair inner products, 161 prefix sums,
  1,024 signed source C columns and 36 nonunitary residual decisions.
- Complete native examples at 1, 9 and 17 axes, all four central-phase
  counterexamples, 12 malformed/out-of-scope controls and a literal dirty
  return counterexample. The literal complete tensor oracle checks four
  columns; it does not exhaust the large tensor input spaces.

The application check runs the unchanged retained author and independent
grade/trace audits, matches their complete receipt and checks the two new
finite bounds. [PASSIVE-REPLAY.json](PASSIVE-REPLAY.json) and
[APPLICATION-RESULT.json](APPLICATION-RESULT.json) preserve those results.
Every consumed predecessor file is SHA-256 authenticated before import.
Ordinary replay compares results; it does not regenerate them.

The repair check binds the actual diagonal target and optimistic invoice
through the unchanged source loader. It checks all nine exact concave-order
hinges, 576 literal group products, 18,432 phase covariance identities,
48 history prefixes and 12 exact physical approximation cases. Controls
include cached targets, wrong input versions, singular targets that share
one return, and small-width dependence. [REPAIR-RESULT.json](REPAIR-RESULT.json)
and [REPAIR-INVOICE.json](REPAIR-INVOICE.json) retain the complete results.

The separate [mutation audit](audit_mutations.py) rejects six deliberate
scientific defects in both normal and optimized Python: the wrong first
overlap count, a native phase outside its tensor power, a projection scale
outside its tensor power, a fixed-Pauli count with signs omitted, a repair
phase outside its tensor power and a missing paid repair charge. The
[twelve rejection receipts](MUTATIONS.json) bind the checked Python sources.
Run it with `python3.12 -I -W error -B research/clifford-pointwise-faithfulness/audit_mutations.py`.

These are author checks using distinct computational paths. The all-axis
and all-width statements are written proofs, not proof-kernel results or
independent human acceptance. The inherited parser and scalar kernel are
shared. No selected cold replay, new provider run, Lean, Docker, physical
emission, constructive complete price, outer admission or changed frontier
is claimed. The repair result is a complete adverse optimistic invoice test.
The base selected conditional value remains 605457647/200000000000 =
0.003027288235, with the five framework assumptions unchanged.

## Scope, overlap and credit

Base: `32890bc5de034ab8fc93ac88ead7279a6a416d04`; priority revision 7.
[TASK.json](TASK.json) records the change from `formal-interface-lemma` to
a written native-interface theorem. The
[canonical claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/5236#discussioncomment-19169126)
records the scope. [RESEARCH-NOTES.md](RESEARCH-NOTES.md) records the selection,
derivation, overlap coverage and verification limits.

Ali Romman's PR #5376 supplies the consumed native grammar, complete endpoint
expansion and exact quadratic kernel. Its trace-polynomial proof, code
invariant, one-axis sharpness and complete-provider application remain prior
work. The retained [native lineage notice](https://github.com/CrocSwap/integer-mult-bounds/blob/32890bc5de034ab8fc93ac88ead7279a6a416d04/research/clifford-tensor-gram/vendor/NATIVE-LINEAGE-NOTICE)
credits the scalar/kernel sources. Chris R's
[PR #4978](https://github.com/CrocSwap/integer-mult-bounds/pull/4978) supplies
the consumed passive ceiling, based on Dugongue's PR #4948 and its credited
controller/native predecessors. Its complete package and notices are declared
inputs. No predecessor file is changed.

Chris R's [PR #5425](https://github.com/CrocSwap/integer-mult-bounds/pull/5425)
and [PR #5446](https://github.com/CrocSwap/integer-mult-bounds/pull/5446)
supply the paid-history method. Ali Romman's
[PR #5449](https://github.com/CrocSwap/integer-mult-bounds/pull/5449) supplies
the explicit relative-history quotient. The repair extension applies these
methods to the retained PR4948 caller. It does not assert the Clifford
premise for every alphabet in those papers. The exact invoice comparator
credits classical concave order, mightyOil and retained predecessors.
Krzysztof Wojt and Nick Petalas
supply related residual-form and partial-Pauli work, as credited in the
[retained singular-completion proof](https://github.com/CrocSwap/integer-mult-bounds/blob/32890bc5de034ab8fc93ac88ead7279a6a416d04/research/singular-rank-two-pauli/PROOF.md).
Those executables are not dependencies.

The stabilizer normal form is classical work of
[Dehaene and De Moor](https://arxiv.org/abs/quant-ph/0304125). The symplectic
residual form, character orthogonality, Gram bound and Fourier inversion
are classical tools. The contribution is the explicit quantitative theorem,
its exact frontends, source-bound repair floor, error tradeoff and complete
adverse invoice in this repository.
No global literature-priority claim is made.

New work by Ali Romman with substantial OpenAI Codex assistance; Apache-2.0.

## Open next questions

Determine the least pointwise width and best spectral bound, with central
phase residues kept explicit. A first step is the exact small-group Gram
spectrum; it does not by itself prove a general threshold.

Apply the pointwise theorem to one actual changed caller, with its paid
history, ownership and full invoice. First prove that its entire operator
alphabet satisfies the hypothesis. A nominal sum of Cliffords need not do so.
The frozen PR4948 word cannot be repaired profitably under the contract in
REPAIR.md. An active change to an original paid input changes that premise.

Bind the stabilizer-map frontend to one actual projection or rectangular
caller. Its native scales, complete endpoint and physical implementation
must be supplied. This package does not reserve those follow-ups.
