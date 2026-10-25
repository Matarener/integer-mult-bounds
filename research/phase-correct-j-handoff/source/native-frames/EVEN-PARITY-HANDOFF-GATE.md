# The new full-source J does not inherit the old free handoff

This is the scoped gate in `even_parity_handoff_gate.py`. Its quantitative
drift observation was supplied by the parent/root and independently
checked here. The underlying source resource and its phase-correct J
remain unchanged and separately verified by the q4 lane.

Let E be the full native operator on the ambient old planes containing
both J and a standard Nj. The actual source resource has full arity
`arity(J E)=mf`, whereas `arity(Nj E)=(m-2)f`: the latter cancels the
already-completed Nj plane, with its scalar minus retained.

Suppose invertible monomials P,Q provided the desired handoff conversion
`P J Q^-1=Nj`, and the right chart transported through E for free,
`E^-1 Q E` monomial. Then

    Nj E = P (J E) (E^-1 Q^-1 E).

Both outside factors are monomial. They preserve the row support of the
middle operator. But J E has exactly `2^(mf)` nonzeros per row, while
Nj E has `2^((m-2)f)`. This is impossible. This argument does not assume
P or Q is Clifford, and retains their actual phases. The old commuting
source swap relation, with P=Q and `[P,E]=0`, is a special case.

At the Clifford binary level this has a simple geometric witness. E has
symplectic blocks `[[I,I],[0,I]]`. A commuting monomial Clifford has
blocks `[[A,0],[C,A^-T]]`; comparing the two products forces C=0 and
`A=A^-T`, so A is orthogonal. Our even-parity J has nilpotent B block
`Gamma_J^2=0`. Standard Nj has a nonzero idempotent B block. Orthogonal
conjugation preserves these squares and cannot send one to the other.

For a quantitative single-bank statement, assume a monomial Clifford P
does conjugate Nj to J but permits a changed E frame. Define

    F=P^-1 E P,       D=E^-1 F.

Then `arity(Nj F)=arity(JE)=mf`. Since F=E D, native B-rank
subadditivity gives

    mf <= (m-2)f + arity(D),   hence arity(D)>=2f.

Any unary repair word needs at least that much additional native rank.
For the explicit M from the source resource, the actual drift is 4f,
checked at f=1,2,3 and lifted by its bitwise binary block formula. This
does not prove that 4f is universally necessary.

If Nj is an untouched fresh plane outside a partial old E, use a different
simple gate: a commuting monomial Clifford preserves the image of that
old Fourier block, so it cannot export an old active J to the untouched
plane. This should not be conflated with the full-E statement above.

No statement here excludes coupled-bank controls, cross-cut native
cancellation, changing the future common frame, or a fully priced new
source/delivery contract. Those are the remaining constructive choices.
It does exclude carrying the old free swap along merely because J has
the same native arity and quadratic spectrum as N.
