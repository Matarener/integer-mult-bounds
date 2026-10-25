# A width-296 exclusion and error floor for the actual negative E decoder

This source-bound application lowers the ordinary-decoder exclusion threshold
in JoyboyBrian's [PR #5508](https://github.com/CrocSwap/integer-mult-bounds/pull/5508)
from width 4198 to 296. It also gives a nonzero approximation-error floor.
It uses the pointwise Clifford Gram theorem in
[PR #5526](https://github.com/CrocSwap/integer-mult-bounds/pull/5526).
The complete kappa calculation and selected frontier are unchanged.

## Exact scope and conclusion

Use the fixed source endpoint chart and negative-bank observation contract of
PR #5508. There are 73 binary address axes. At width f the required postdecoder is

```text
J_f = Q_f^-1 E_(1,f)^-1 E_(2,f) E_(3,f)^-1 Q_f.
```

The only available dependent input is the emitted negative bank. Other owned
or dirty inputs are independent. Ordinary address operations are tensor lifts
of one-column monomial Cliffords. Arbitrary scalar owner mixing, instruction
count, independent workspace and f-dependent coefficients are permitted.

For every integer f>=296, no such ordinary program implements J_f. More
strongly, for every such ordinary endpoint O_f, in the fixed source chart,

```text
||J_f-O_f||_op >= 1541/1255956.
```

This is a worst-case unit-input error floor, not an error on every input. It
also applies to any larger endpoint required to contain the specified decoder
block, by restriction to its original input and projection onto its output.
It is not invariant under arbitrary nonunitary rescaling of that chart.

No minimum width is asserted. At smaller widths the new argument gives no
decision. Paid calls, correlated original-input histories, operations mixing
tensor columns, nonlinear rounding and changed target contracts remain outside
scope. This is not a paid-child lower bound or a physical completion invoice.

## Pinned premises and their roles

The package keeps byte-exact copies of three public files. INPUTS.json records
their repositories, commits, Git objects and SHA256 values. The verifier checks
those bytes before using the consumed data. Frozen predecessor files are not
edited and no predecessor executable is imported.

1. [PR #5508 proof](https://github.com/JoyboyBrian/integer-mult-bounds/blob/7e6824d560337e2b2e49da8b98727183491f6ecf/research/odd-e8-negative-exit-algebra/PROOF.md):
   the actual owner code, negative endpoint, ordered fresh-stage path uniqueness
   and unique nonzero path class are cited premises.
2. Its [exact result](https://github.com/JoyboyBrian/integer-mult-bounds/blob/7e6824d560337e2b2e49da8b98727183491f6ecf/research/odd-e8-negative-exit-algebra/RESULT.json):
   the selected owner endpoints, signed 25-axis map, source coefficient and
   sparse conjugated column are checked independently below.
3. [PR #5526 proof](https://github.com/aliromman/integer-mult-bounds/blob/32e014bec9206f3987857e6153ec0fd8058f04e3/research/clifford-pointwise-faithfulness/PROOF.md):
   projective Clifford tensor independence and its dimension-uniform Gram
   bounds are cited premises. The consumed rational row bounds are recomputed.

These pending written proofs are not declared independently accepted by this
application. Source authentication and the checks below do not replace their
full mathematical review or the source producer's physical admission.

## Verify the full alphabet premise

Each stage source factor is a scalar owner matrix conjugated by block-diagonal
signed linear address permutations L_i. Expanding the fixed owner block gives

```text
(J_f)_(i,j) = sum_path c_path (Q^-1 M_path Q)^(tensor f),
```

where M_path is a product of signed linear binary permutations. The scalar
owner coefficients c_path are applied once; they are not raised to f.
A binary invertible linear permutation is a CNOT Clifford, and a linear sign
is a Pauli Z product. Thus every M_path is unitary Clifford. The source Q is
the one-central-axis square root of X,

```text
Q = ((1+i)/2) I + ((1-i)/2) X.
```

It is unitary, Q squared is X, and it conjugates Paulis to Paulis. Hence every
conjugated path is a 73-axis unitary Clifford with Gaussian-dyadic entries.
This checks the actual expanded alphabet; the sum J itself need not be a
Clifford. The distinction is required for applying PR #5526.

The source's ordered path separation says that distinct paths between the
fixed owner endpoints have distinct linear maps. Therefore they are not
projectively equal, before or after conjugation by Q. At each width, folding a
representative phase changes a path coefficient only by a unit phase. It does
not cancel the chosen coefficient with another path.

For each original-input/output block, any ordinary program in the stated
alphabet lies in the scalar span of lifted monomial Cliffords. Composition,
addition, scalar multiplication, COPY and CLEAR preserve this property, for
any number of independent workspace fields. This also holds for each specified
f when the word and its scalars depend on f.

## The actual path is outside the ordinary alphabet

The retained endpoints are j=(0,0,0) and i=(1,0,0). The source root rows have
squared norm four and mutual dot product two. The inverse-stage cross entry
is therefore 1/4, while the diagonal inverse entry is one. The middle-stage
entry is

```text
39*98/(2744*97) + 1078/(2744*1079) = 1541/104663.
```

The selected path coefficient is

```text
c_star = (1/4)*(1541/104663)*1 = 1541/418652.
```

These rational identities are recomputed from the consumed source data.
The complete path map reduces to the signed 25-axis map supplied in the
source result, extended by identity on the other 48 axes. Its first binary
column is 657934, so it moves the central direction e0.

If a signed monomial M has linear map G with Ge0 different from e0, expansion
of Q^-1 M Q gives four distinct output addresses on every basis input x:
Gx, Gx+e0, Gx+Ge0 and Gx+e0+Ge0. Their coefficient magnitudes are 1/2.
The four destinations are distinct because G is invertible and Ge0 is neither
zero nor e0. Thus the chosen Clifford class is nonmonomial, even after a global
phase. At input zero the exact consumed column is

```text
0       :  1/2
1       :  i/2
657934  :  i/2
657935  : -1/2.
```

The independent sparse interpreter reconstructs this column and 146 further
basis columns, checks invertibility of the binary map, and checks Q inverse
and square identities. The all-input conclusion follows from the four distinct
addresses, not extrapolation from the finite sample.

## Apply the pointwise Gram theorem

Put D=2^73. For distinct projective unitary Clifford classes, PR #5526 gives,
at every f>=4*73+4=296,

```text
D^(-f) ||sum_g b_g U_g^(tensor f)||_HS^2 >= (1/9) sum_g |b_g|^2.
```

Subtract any ordinary block O from the selected decoder block. Its monomial
classes cannot change the chosen nonmonomial coefficient. After all projective
classes are combined, that coefficient still has magnitude c_star. Therefore

```text
D^(-f) ||(J_f)_(i,j)-O||_HS^2 >= c_star^2/9
                                    = 2374681/1577425473936.
```

Since the normalized Hilbert-Schmidt norm is at most the operator norm, this
proves the error floor and exact nonmembership. Restricting the complete
endpoint to this input block and projecting onto this output block cannot
increase operator norm, which gives the stated complete-endpoint consequence.

The later source bound also gives normalized squared error at least
(125/126)*c_star squared for every f>=308. It is a stronger sufficient constant,
not a claim of optimal distance. The source's old support argument first
passes at f=4198 because 2f-216 must exceed 8178. Its ADD-count lower bound and
broader cross-column exclusions retain their original scopes.

## Verification and limitations

```sh
python3.12 -B scripts/research_package.py --package research/negative-e-decoder-gram-bound
```

Use Python 3.12 and the standard library. Registered warning-strict normal and
optimized runs print `PASS_NEGATIVE_E_DECODER_GRAM_BOUND` and the launcher prints
`PASS_REGISTERED_RESEARCH_PACKAGE`. Each run authenticates three immutable
inputs and checks 147 sparse columns, 36 finite rational Gram row bounds,
complete dimension-uniform geometric tails and nine rejecting or semantic
controls. It checks changed coefficients, source axes, owner endpoints, signs,
unproved width, projective phase cancellation and external-scalar placement.

The complete source owner-path family and general Clifford counting theorem
are credited written premises. Their full scientific suites, independent human
review, proof-kernel verification, selected cold replay, physical emission,
precision application and complete paid invoice were not run here. No native
supplier, new kappa or change to the five selected framework assumptions follows.

## Open next questions

Bind a changed paid decoder or a correlated-history interface to the complete
caller and its remaining invoice. That change can evade the present observation
contract. State the new original-input identity first, then check every paid
call, helper lifetime and precision budget. The present floor must not be
subtracted as a paid-call count.

## Credit

JoyboyBrian supplies PR #5508, its actual E-code/path binding, signed normalizer
and support consequence, with the source producer and helper lineage retained
in the copied proof. Ali Romman (@aliromman) supplies PR #5526 and the earlier
fresh-stage separation lineage. The retained sources credit their native,
Clifford, stabilizer and compiler predecessors. The new contribution is this
source-bound width and error application. Proof and checks by Ali Romman with
substantial OpenAI Codex assistance; Apache-2.0. No global novelty claim is made.
