# Independent review of the free-group lift

Reviewed independently from the proposed package implementation. The review
read PR4100 at `337d04939571a637aeab54a0f58f54fde811663a`,
`research/unconditional-batched-crt/COMPLEX.md`, and PR4088 at
`72d7efc181edb21806a878f174847c96dd410ab0`, particularly the retained
`vendor/audit_core.py`, `vendor/audit_verify.py`, native transport/emitter and
exact recipe checker. No primary-agent reasoning or implementation was imported.

## Verdict

The narrow free-group-algebra specialization asserted in COMPLEX.md is valid.
There is no obstruction from the failure of tensor power to preserve addition:
the proposed map is the linear extension of a group homomorphism on unary
generators, not the tensor power of an arbitrary operator sum. The actual
retained checker uses precisely the stronger formal semantics needed for this
argument. This verdict is confined to this algebraic link. It does not certify
the complete asymptotic machine, cost, precision, hosting or recovery theorem.

## Exact source assertion and what its checker proves

COMPLEX.md, source binding and endpoint, says the source semantics is a matrix
over the free group algebra of the warp symbols and that the complete
723-column certificate cancels its words formally. This premise is substantiated
by the implementation, rather than by a selected numerical realization:

- `audit_core.py:298-392` represents a linear expression by a dictionary keyed
  by an independent input register and a tuple of signed unary operator ids.
  Coefficients are exact `Fraction` values.
- `_left` and `_right` at lines 321-326 reduce only an adjacent id and its
  inverse. They do not collapse distinct warps using binary frame equality,
  realize them as Gaussian matrices, or use a relation particular to the
  nine-bit representation.
- `forward_rows` starts every live input and every declared private buffer as
  an independent symbol. Corrections distribute over these sparse expressions;
  scalar ADD and SCALE act linearly on exact coefficients.
- `audit_verify.py:116-143` checks the intended scalar shear endpoint, unchanged
  helpers/private buffers and no buffer-to-live leak on 632+91=723 inputs.
  It also checks inverse-transpose symbols, independent reverse pullback and
  both cleanup-boundary views. These are statements in the free group algebra.
- Native transport `bw_transport.py:71-85,229-284` independently retains this
  free-word semantics, although its own private-buffer replay starts buffers at
  zero. The stronger arbitrary-dirty claim belongs to the separate 723-input
  checker; the two scopes should not be conflated.

## Why specialization works for every positive tensor multiplicity

Let F be the free group on generator symbols g_k. A word is a product of
generators and inverses. For any field K containing the exact scalar
coefficients, any finite-dimensional K-space E, and any choice of invertible
A_k on E, freeness gives a homomorphism F -> GL(E), g_k -> A_k. Its unique
K-linear extension K[F] -> End_K(E) is a unital K-algebra homomorphism.
Consequently it extends entrywise to matrices and carries a proved formal
identity between register-program matrices to a true identity on E-valued
registers.

Now take E=(K^512) tensor f and A_k=G_k tensor f. Inverses map to the tensor
power of inverses and products map in their original order. For every word
w, its specialization is G_w tensor f. Thus each scalar-weighted correction
term c*w specializes to c*(G_w tensor f), while an identity word specializes
to the identity of dimension 512^f. No property of the input values is needed:
arbitrary correlated live and dirty register values satisfy the same identity.

In particular c*(G-I) becomes c*(G tensor f-I), not c*(G-I) tensor f.
Likewise a separately declared scalar coefficient remains c, while a global
phase inside a unary matrix is repeated with that matrix and becomes its
f-th power. These distinctions are requirements of the specialization, and
COMPLEX.md explicitly preserves them.

No faithfulness of the realized unary representation is needed. Even if
different words happen to give the same 512-column matrix, the checker proves
the stronger equality before this quotient is taken. Conversely, numerical
equality at f=1 alone would not suffice and is not the premise used here.

## Native boundary of this result

For a physical event with exact f=1 identity

    M = T_to * G_k^(+/-1) * T_from^-1,

Kronecker multiplicativity gives

    M tensor f = (T_to tensor f) * (G_k tensor f)^(+/-1)
                 * (T_from tensor f)^-1.

The native recipe checker `bw_check_recipes.py` states and implements exact
512-column equality, including global phase, for every emitted directed warp
class. Its source does not replace equality with a binary frame check or a
projective equality. Native frame transitions that contain a rank-r child need
the corresponding exact left/child/right factorization as a separate interface.
The algebraic lift preserves any such exact identity; this independent review
does not freshly execute all native stages or prove their cost.

Remaining obligations therefore include verifying or importing the pinned
exact native recipe receipts at their stated coverage, realizing all repeated
monomials and frame/child interfaces on the chosen physical tapes, and paying
the common-cover, precision, recursion, outer assembly and recovery costs.
None is a counterexample to the free-group specialization itself.

## Distinct finite implementation cross-check

`independent_real.py` imports neither the audited evaluator nor the primary-agent
implementation. It authenticates the four actual gzip input Git blobs, parses
the literal correction/wrapper/A/cut/B-warp/restore/cleanup ordering, and
evaluates their action using exact rational vectors. The generator assignment
uses a ternary cycle, signed transposition, diagonal reflection and unary -I.
The assigned operators do not commute at any tested multiplicity.

The oracle checks all four providers, multiplicities 1, 2 and 3, and forward
and inverse-transpose orientations: 24 concrete specializations, with 3, 9 or
27 coordinates in each of 632 live registers and 91 private dirty buffers.
Every input coordinate is populated by a deterministic nonzero value and
different register vectors are correlated. All endpoints agree with the
declared scalar shear, helper identity and dirty-buffer identity. This is one
concrete dirty input assignment per specialization, not an independent
723-symbol basis proof. The source free-word proof supplies the generality.

Controls check 216 generator/inverse products and noncommutativity at all
three multiplicities. Four semantic distinctions are explicit: unary -I
repeats its phase while scalar -1 stays scalar; a separately declared scalar
1/2 is not exponentiated; a sum is not tensorized as a whole; and the accidental
f=1 relation (-I)+I=0 fails under termwise f=2 substitution. The last control
demonstrates why numerical f=1 correctness alone would be insufficient.

Normal and optimized CPython 3.12 replays both passed with byte-identical
JSON receipts. Run from the package, using its authenticated source inputs:

    python3.12 -B independent_real.py --inputs source/inputs
    python3.12 -B -O independent_real.py --inputs source/inputs

The command is read-only and writes its deterministic receipt to stdout.

## Credit and scope

The free-word representation, complete-input audit, native transport and
source construction are predecessor work. Retain the source notices for
Cinna Davis/PR4100 and PR4088, Sagar Thakrar's retained audit, Arham Tahir's
shared structural interpretation, the PR2226 and original native/compiler
lineage, and the other credited source authors. This review contributes a
bounded independent assessment of the algebraic implication; it claims no new
supplier, kappa, selected frontier, full machine or formal-kernel theorem.

All three agents are OpenAI Codex agents; this is not independent human review.

The native source observations above refer to the directly tracked `native/vendor/native/new/code/borrow/bw_transport.py` (blob `08248542b18864c94a5ac050c8669f68519838e1`) and `bw_check_recipes.py` (blob `6db8ad50eb2562700432a852501aad720aa34816`) inside the PR4088 package. `SOURCES.json` pins both as provenance through canonical main. They are inspected source, not execution dependencies or freshly replayed native certificates.
