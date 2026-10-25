# Independent review of constructive free-scalar normalization

## Domain and conclusion

The selected normalization implication is correct. Let A=F2[G], with G the stated GL3(F2) address group and the six stated coordinate-CNOT labels. Binary3x3 scalar matrices act on the OUTER register index; group coefficients act on the address basis. These are distinct actions even though both use3x3 binary matrices in their descriptions. Scalar entries commute with A coefficients. Equality below is in M3(A), not merely in the possibly aliasing natural9x9 representation.

At each paid call choose a role i and address label g and let C(g,i)=I+([g]+[e])E_i, with E_i=e_i e_i^T. Free matrices W_j range over scalar GL3(F2), without any restriction on dirty intermediate registers. A length-n chronological raw program is

    W0, C1, W1, C2, ..., Cn, Wn,

with new operations multiplying on the left, so its full operator is

    Raw = Wn Cn W(n-1) ... W1 C1 W0.

The normalized alphabet consists of F(g,N)=I+([g]+[e])N for all rank-one idempotent binary N. The following proof preserves the number and chronological sequence of paid address labels exactly. It does not prove that any other physical operation is free, normalize arbitrary address changes, or certify a lower bound/SAT encoding.

## 1. Exact telescoping with the correct inverse order

Set P_j=W_j W_(j-1) ... W0 for0<=j<=n. For1<=j<=n put

    F_j = P_(j-1)^(-1) C_j P_(j-1).

Then

    Raw = P_n F_n ... F_1.                         (1)

For example the adjacent factors telescope as

    P_n [P_(n-1)^(-1) C_n P_(n-1)]
        [P_(n-2)^(-1) C_(n-1) P_(n-2)] ...

and P_j P_(j-1)^(-1)=W_j. No paid factors are reordered and no overlapping operators are commuted. Equivalently, induction on j proves W_j C_j ... C_1 W0=P_j F_j ... F1. The conjugation is P^(-1) C P, not P C P^(-1), for this definition of cumulative P and this left-multiplication chronology.

Conjugation leaves the address label unchanged:

    F_j = I+([g_j]+[e]) P_(j-1)^(-1) E_(i_j) P_(j-1).

Write u=P^(-1)e_i and v^T=e_i^T P. Then N=u v^T, v^T u=1, and N is a nonzero rank-one idempotent. This establishes that every normalized paid factor is in exactly the specified alphabet.

## 2. Why the residual may disappear at the stated target

Augmentation epsilon:A->F2 sends sum a_g[g] to sum a_g. It is a ring homomorphism, and entrywise matrix augmentation preserves multiplication. Each paid coordinate call has epsilon(C_j)=I because [g]+[e] augments to1+1=0. Every scalar free matrix augments to itself. Hence

    epsilon(Raw)=P_n.                             (2)

The target D=diag([T0],[T1],[T2]) has epsilon(D)=I. Therefore a raw word ATTAINING this full formal diagonal has P_n=I, and (1) becomes

    Raw=F_n ... F1=D.

This is a conditional consequence of formal target attainment. AugmentationI by itself is not sufficient for attaining the target.

For an arbitrary raw target M, the residual is P_n=epsilon(M), and the correct normalized operator is P_n^(-1)M. It is generally false that Raw=F_n...F1 without the identity-augmentation hypothesis. An empty paid word with a single nonidentity free W0=H gives Raw=H, residualH and normalized empty productI. This is already a concrete countercontrol to unconditionally dropping the residual. Any attaining raw word necessarily has invertible epsilon(M); a target with singular augmentation cannot be attained in this grammar.

## 3. Constructive converse and exact paid length

Let N=u v^T with v^T u=1 be any allowed normalized projector. Since v is nonzero, ker(v^T) has dimension2, and u is outside that kernel. Choose an ordered basis k1,k2 of the kernel and form the matrix with COLUMNS

    S=[u,k1,k2].

It is invertible. The coordinate of an arbitrary x along its first column is v^T x, so

    S E0 S^(-1)=u v^T=N.

Equivalently, P=S^(-1) satisfies P^(-1)E0P=N. This column construction must not be silently interpreted as literal rows in a row-tuple implementation.

Given any normalized chronological word F1,...,Fn with n>=1, choose S_j for its N_j and prescribe P_(j-1)=S_j^(-1). Set

    W0=P0,
    W_j=P_j P_(j-1)^(-1)       for1<=j<n,
    W_n=P_(n-1)^(-1),

and let C_j use physical role0 and the SAME g_j. The cumulative products are exactly the prescribed P values, with final P_n=I. Substituting into (1) constructs a legal raw word with endpoint F_n...F1, exactly n paid calls and unchanged address chronology. Intermediate free matrices may mix any arbitrary dirty register; endpoint equality restores precisely whichever dependencies the normalized endpoint restores.

For n=0 the converse is separate: the empty normalized word isI and is realized by W0=I. Conversely, a raw zero-paid word is just W0; if it attains an identity-augmentation target then W0=I. Thus zero-length edge cases require no access to P_(-1) or a nonexistent last projector.

## 4. Finite alphabet and source boundary

There are7 nonzero u and4 choices of v with v^T u=1, so28 projectors; over F2 each nonzero rank-one projector has a unique such pair. A fixed coordinate projector has6 scalar conjugators per image, corresponding to GL2(F2) changes of basis on its kernel. Thus all168 scalar matrices and3 coordinate roles give504 conjugacy pairs, with28 images each occurring18 times. These counts and the normalization strategy are already present in the predecessor; checking them is corroboration and source binding, not a novelty claim.

The original ENCODING_AUDIT.md lines99-110 gives the free-mixing/augmentation argument; its original contribution and lineage must remain credited. The authenticated model.py lines63-76 implements normalized left multiplication by I+([g]+[e])u v^T. Original source code need not implement an entire raw scalar interleaver; any new adapter must distinguish its own scalar-mixing replay from reuse of original paid-step/checker code. Claiming an unmodified source raw-word factory would require such a factory actually to exist.

Formal operator equality acts identically on all three arbitrary-input registers and all group-basis addresses. In particular, a target with third diagonal[e] and off-diagonal zero restores the arbitrary third register; the proof does not assume it starts at zero. Natural representation equality is insufficient because it can alias distinct group-algebra coefficients.

## Limits and remaining review

No gap was found in this quantified algebraic implication under its exact grammar. Independent code, constructive conversions, source paid-step bindings, typed records and negative controls still require review once their implementations are frozen. Full CNF/Tseitin equivalence, proof-certificate replay, minimum-length certification, changed free-operation models, physical cost, supplier/native/outer or human/formal-kernel acceptance remain excluded.

Credit Brian Ross/OpenAI for the original fixed-target model, support and normalization argument; Hanson Sun/Josie Elliston and retained NOTICE/license/model lineage; and classical change-of-basis/augmentation algebra. This is independent constructive verification of an existing strategy, not a new general theorem claim.
