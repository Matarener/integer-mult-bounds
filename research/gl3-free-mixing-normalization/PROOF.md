# Independent lossless free-mixing normalization

Author: Toik Y, with substantial OpenAI Codex assistance.

Classical conjugation, rank-one linear algebra, and augmentation are not claimed
as new. The source's original argument belongs to Brian Ross. This independent
construction was made from the stated mathematical contract, without reading
predecessor/source code, source proofs, S1/S2 implementations or receipts, source
integration files, or generated source queries before the freeze recorded in
`FREEZE.json`. Attribution is not a claim of access to the original argument.

## Exact setting and claim

Fix an integer r >= 1, a group G (not assumed commutative), and the unital group
algebra A = F2[G]. Embed binary r by r matrices as scalar matrices over A. Their
entries are central in A. A free operation is a fixed P in GL(r,F2), independent
of address state. A paid operation on coordinate i with address element g is

    C(i,g) = I + (g + 1) E_i,

where E_i has its only nonzero entry 1 at (i,i). This is the diagonal operation
with entry g on coordinate i and entries 1 elsewhere. Multiplication means
composition, with the rightmost operation acting first. The chronological raw
word is

    W_0, C_1, W_1, ..., C_n, W_n,

so its operator is R = W_n C_n W_(n-1) ... C_1 W_0. A word has literal paid cost
n; semantic simplification does not change that count in either converter.
All free operations are scalar, linear, fixed, and invertible. Adaptive,
nonlinear, and address-state-dependent mixing are outside this grammar.

The normalization is an exact equality in M_r(A), for every finite n, preserving
all paid addresses in chronological order and preserving paid cost. It is not a
claim about faithfulness of a particular address representation. In particular,
no natural three-by-three address action is used by the oracle.

## Forward normalization for every n

Define

    P_j = W_j W_(j-1) ... W_0            for 0 <= j <= n,
    F_j = P_(j-1)^(-1) C_j P_(j-1)     for 1 <= j <= n.

Then

    R = P_n F_n F_(n-1) ... F_1.                         (1)

For a proof, let R_0 = W_0 and R_j = W_j C_j R_(j-1). At j=0,
R_0=P_0. If R_(j-1)=P_(j-1) F_(j-1)...F_1, then

    R_j = W_j C_j P_(j-1) F_(j-1)...F_1
        = W_j P_(j-1) [P_(j-1)^(-1) C_j P_(j-1)]
                         F_(j-1)...F_1
        = P_j F_j F_(j-1)...F_1.

This induction proves (1), including n=0, where the normalized product is I and
R=W_0=P_0. The argument only inserts adjacent inverse pairs. It never commutes
paid address coefficients with each other or reverses their order.

Let epsilon:A -> F2 send every group basis element to 1 and extend linearly.
It is a unital algebra homomorphism because epsilon(gh)=1=epsilon(g)epsilon(h)
on basis elements, and multiplication is bilinear. Apply it entrywise to
matrices. Each C_j has epsilon(C_j)=I, while each free scalar W_j is unchanged.
Consequently

    epsilon(R) = P_n,   epsilon(F_j)=I.

For a target D=diag([T_c1],...,[T_cr]) with each [T_ci] a group basis element,
epsilon(D)=I. Thus R=D implies P_n=I. More generally this implication holds for
any target having augmentation I. Such a raw realization therefore has exactly
operator F_n...F_1 with exactly n paid factors. This implication is conditional
on attaining that target; arbitrary raw words may have P_n != I, and the
residual must then be retained. For n=0 the same statement forces W_0=I.

## Form of each normalized paid factor

For P=P_(j-1), i=i_j, put

    u = P^(-1) e_i,   v^T = e_i^T P,
    N = P^(-1) E_i P = u v^T.

Here u and v are binary column vectors. Both are nonzero and
v^T u=e_i^T P P^(-1)e_i=1. Hence N has rank one and
N^2=u(v^T u)v^T=N. Centrality of binary scalars gives

    F_j = I + (g_j + 1) N.

This is valid over the noncommutative group algebra; g_j need not commute with
any other paid address g_k. Neither the proof nor the converter combines or
reorders addresses.

## Every rank-one idempotent is obtainable

Conversely take binary nonzero u,v with v^T u=1. Let K=ker(v^T). Since v^T is a
nonzero functional, dim K=r-1, and u is not in K. Choose a basis k_2,...,k_r of K
and set Q=[u,k_2,...,k_r]. These columns form a basis: applying v^T to a relation
alpha*u+sum beta_i*k_i=0 gives alpha=0; independence of the k_i then gives all
beta_i=0. Thus Q is invertible. Since v^T Q=(1,0,...,0),

    Q E_0 Q^(-1) = u v^T.

Set P=Q^(-1). Then N=P^(-1) E_0 P and
I+(g+1)N=P^(-1) C(0,g) P. This constructs a free frame for every admissible
normalized factor using u,v only, independently of g. For r=1, K is zero,
u=v=1, Q=P=I, and the construction still applies.

For completeness, every rank-one idempotent N over F2 has this form. A nonzero
column u spans its one-dimensional image, so N=uv^T for a nonzero row v^T.
Then N^2=(v^T u)N=N and N!=0 force v^T u=1. In F2 the scalar choices are
unique, which also makes the oracle's u,v factorization canonical.

## Converse compilation of a whole word

Let a normalized chronological word be F_1,...,F_n, with
F_j=A_j^(-1) C(0,g_j) A_j obtained by the basis construction above. For n>=1,
choose the raw free maps

    W_0 = A_1,
    W_j = A_(j+1) A_j^(-1)       for 1 <= j < n,
    W_n = A_n^(-1).

The cumulative product before paid operation j is exactly A_j, by telescoping,
and the total free product W_n...W_0=I. Substitution in (1) gives exactly
F_n...F_1. There are exactly n coordinate paid operations, in unchanged address
order g_1,...,g_n. For n=0 use the single free map W_0=I and no paid operations.
The compiler rejects a supplied nonidentity residual because its contract is
net-free-I compilation; forward normalization records arbitrary residuals.

Thus raw words attaining any augmentation-I target and normalized rank-one
idempotent words are mutually realizable, with the same literal paid cost and
address order. These maps need not be inverse as descriptions: equivalent free
frames and coordinate choices may compile to different raw descriptions.

## Executable finite corroboration

The proof above establishes all n and all r>=1. Finite checks are corroboration,
not the proof. Actual finite focus is r=3.

There are (8-1)(8-2)(8-4)=168 invertible binary register frames. Each has three
coordinate projectors, giving 504 ordered conjugacies. There are 7 choices of
nonzero u and 4 choices of v with v^T u=1, giving 28 distinct projectors. The
oracle enumerates all frames lexicographically as row-mask tuples, then all
coordinates 0,1,2. Every one of the 504 records retains P, P^(-1), i, N, u, v,
and an explicit converse basis Q and frame Q^(-1). It independently enumerates
all 28 admissible uv^T matrices and verifies exact set equality. Every projector
has 18 conjugacies, verified directly in the full table.

The symbolic interpreter works in the free associative F2 algebra on tokens
'a','b','c'. A coefficient is a finite parity set of words; addition is symmetric
difference, multiplication concatenates words with parity cancellation. This
retains complete noncommuting coefficients, rather than evaluating them in an
address representation. Equality here survives specialization of the tokens to
any group elements. The interpreter evaluates the raw chronological operations
directly and separately evaluates the normalized factors. The tested lengths
are bounded; the algebraic proof supplies the all-n statement.

The reproducible selftest includes 672 raw symbolic cases: all 504 one-paid
conjugacies and 168 deterministic raw words at lengths 0 through 6. It also
checks 196 normalized converse compilations at lengths 0 through 6, retains
augmentation/residuals, verifies chronological addresses and paid counts, and
checks r=1 at lengths 0 through 4. Direct and dirty/restore positive examples,
including a mixed two-paid word restored to diag(a,a,1), are retained. An
identity-address paid occurrence still counts as one paid occurrence.

The first lexicographic noninvolutory inverse-order witness is
P=(1,3,6), P^(-1)=(1,3,7), coordinate 0. The correct projector has rows (1,1,1),
u=7,v=1; the wrong P E_0 P^(-1) has rows (1,1,0). Its full symbolic operators
are unequal. Other retained controls detect reversed factor multiplication,
reordered paid addresses, and omission of a nonidentity augmentation residual.
Invalid singular frames, v^T u=0, raw/normalized paid-count mismatches,
non-rank-one projectors, and nonidentity-residual net-free-I compilation are
explicitly rejected. No Python assert statement supplies correctness checks.

Normal execution and isolated optimized warning-strict execution must give
byte-identical JSON for both full table and selftest:

    python3 oracle.py selftest
    python3 -I -O -W error -B oracle.py selftest
    python3 oracle.py table
    python3 -I -O -W error -B oracle.py table

## CLI and API contract

The script uses the Python standard library only. Every command emits JSON to
stdout, and no command writes files. JSON input is read from stdin by default;
`--input PATH` reads an explicitly named file. Invalid contracts emit a JSON
error and return exit status 2. Successful commands return status 0.

    python3 oracle.py table [--r 1|2|3]
    python3 oracle.py selftest
    python3 oracle.py normalize --input RAW.json
    python3 oracle.py compile --input NORMALIZED.json
    python3 oracle.py evaluate-raw --input RAW.json
    python3 oracle.py evaluate-normalized --input NORMALIZED.json

All binary matrices are row masks: bit j of row i is entry (i,j). Coordinates
are zero-based. Vectors are r-bit integers with component i at bit i. An address
is a list of nonempty token strings; [] is the identity word. Tokens are formal
noncommuting symbols. Neither coefficient inverses nor group reductions are
needed for the universal identities checked here.

A raw object has `r`, `free` (n+1 binary matrices), and `paid` (n objects with
`coordinate` and `address`). An optional `paid_count` must equal n. A normalized
object has `r`, `factors` (objects with `projector` and `address`), and an optional
`residual` (default I). Optional u,v metadata must match the projector. Forward
normalization emits all these fields and `paid_count`. The API functions are
`conjugacy_table(r=3)`, `normalize_raw(raw)`, `compile_normalized(normalized)`,
`evaluate_raw(raw)`, `evaluate_normalized(normalized, include_residual=True)`,
`converse_basis(u,v,r)`, and `selftest()`.

For a later source adapter, compare the 504 triples `(frame,coordinate,projector)`
exactly, using the documented encoding and ordering. `binary_table_sha256` hashes
UTF-8 JSON of the list of objects with those three keys, with keys sorted and
separators (',',':'), with no trailing newline. The full table retains all
additional factorization and converse metadata separately.

## Scope boundary

This is one exact algebraic model reduction. It does not establish SAT, RUP,
UNSAT, any minimum-nine result, physical implementation, a supplier, a kappa
improvement, or kernel acceptance. No address-group census is inferred from the
binary register-frame enumeration. Source comparison occurs only after the
independent files and receipts have been frozen and hashed.
