# The integer-shear supplier inequality fails on faithful words

**Negative result. No new κ, no supplier admission, no selected-frontier change.**
The selected conditional exponent remains 0.001672660197076918.

PR #3905 proves that the integer matrix \(B=X^2Y^2\) costs exactly four calls in
its formal shear alphabet, and that the two-role diagonal word restores the
second role with no extra call. PR #3937 shows every commutative algebra
carrier sends \(B\) to the identity. PR #3947 gives a three-bit noncommutative
quotient in which \(\rho(B)\) is one XOR, and stops before the
supplier/recurrence inequality. This package supplies that inequality for the
faithful shear-word bill, and shows why the one-XOR moment cannot replace it.

## Charging

Address width \(m=2\), role count \(W=2\), and each letter of
\(\{X,X^{-1},Y,Y^{-1}\}\) is one rank-1 paid child. This is the PR #3905
model: every legal label differs from the identity by a rational rank-one
matrix, and the displayed endpoint uses two roles. The repository moment is

\[
M(a)=\frac{L}{W}\left(\frac{1}{m}\right)^{1-a}=\frac{L}{W}\,m^{a-1}
=\frac{L}{Wm}\,m^{a},
\qquad a\in[0,1].
\]

For \(m>1\), \(M\) is strictly increasing in \(a\). Its minimum on the interval
is \(M(0)=L/(Wm)\) and its maximum is \(M(1)=L/W\). The strict supplier test
is \(M(a)<1\).

## Faithful length

Let \(u_k=(B^k)_{11}\). Direct multiplication gives \(B^2=6B-I\), so
\(u_0=1\), \(u_1=5\) and \(u_{k+1}=6u_k-u_{k-1}\). If \(u_k\ge 5u_{k-1}\ge 0\),
then

\[
u_{k+1}-5u_k=(6u_k-u_{k-1})-5u_k=u_k-u_{k-1}\ge 4u_{k-1}\ge 0.
\]

The two linear forms \((6x-y)-5x\) and \(x-y\) agree on the basis pairs
\((1,0)\) and \((0,1)\), hence for every integer pair. Starting from
\(u_1=5u_0\), induction gives \(u_k\ge 5^k\) for every \(k\ge 0\).

Right multiplication by any one of the four generators replaces each entry by
an integer linear form whose coefficients have \(\ell_1\) norm at most 2
(explicitly: sums or differences of at most two previous entries). Therefore
every product of \(L\) letters has max-absolute entry at most \(2^L\). Since
\(u_k\ge 5^k>4^k=2^{2k}\) for every \(k\ge 1\), every shear word for \(B^k\)
has length at least \(2k+1\).

The same Cayley graph, searched through length 4, contains \(B\) and contains
no shorter word. The positive word \(X^2Y^2\) has length 4, so that minimum
is sharp. In particular the growth bound's \(2\cdot 1+1=3\) is not sharp at
\(k=1\); the enumeration is the \(k=1\) input to the moment.

## The inequality

Let \(L_k\) be the minimum letter count of \(B^k\). Then \(L_1=4\) and
\(L_k\ge 2k+1\) for \(k\ge 2\), so \(L_k\ge 2k+1\) for every \(k\ge 1\) and the
\(k=1\) count is one larger.

- For \(k=1\), \(M(0)=4/(2\cdot 2)=1\) and \(M(a)=2^a>1\) for every
  \(a\in(0,1]\). The strict test \(M(a)<1\) fails for every \(a\in[0,1]\).
- For \(k\ge 2\), \(M(0)\ge(2k+1)/4>1\), so \(M(a)>1\) for every
  \(a\in[0,1]\).

Raising the rank of a letter above 1 only increases \(M\), because
\(r\mapsto(r/m)^{1-a}\) is increasing for \(1\le r\le m\) and \(a\in[0,1)\).
The rank-1 charging is the most favorable per-letter reading, and it still
fails.

## What the three-bit quotient does not transfer

Reducing the integer matrices modulo 3 and passing to the sum-zero subspace
of \(\mathbb F_2^4\) reproduces the PR #3947 matrices. The image of \(B\) is
the single XOR \(b\oplus=c\), and that matrix squares to the identity, so
\(\rho(B^k)\) costs at most one XOR for every \(k\). On width 3 and two roles
that one rank-1 child has \(M(a)\le 1/2<1\).

There is still no constant \(C\) with \(L_k\le C\) for every \(k\), because
\(L_k\ge 2k+1\). The quotient moment is an upper screen for a different
operation. It is not an upper bound on the faithful supplier moment, and it
does not make the unknown conversion cost zero. The same obstruction applies
to the separate 18-bit matrix boundary in PR #3947: three XORs are still
\(O(1)\) in \(k\), while the faithful letter count is not.

## Dirty restoration inside the diagonal model

For \(N=E_{11}\), each paid factor left-multiplies only the first role. The
ordered product \(D([X])^2D([Y])^2\), applied rightmost first, sends an
arbitrary dirty pair \((u,v)\) to \((Bu,v)\). The spectator is not written, so
the four-call bill has no cleanup term to add back. The moment failure above
is the letter count itself. The quotient likewise leaves its second three-bit
block untouched. Neither restoration clause repairs \(M(a)<1\).

The formal output of \(B^k\) is an integer matrix whose \((1,1)\) entry is
\(u_k\ge 5^k\). The quotient output is three bits. No decode map between them
is priced here, and none is claimed to be free.

## Evidence

The length, growth, doubling, moment comparison, diagonal endpoint and
quotient identity are proved above. `verify.py` checks the finite algebraic
steps those proofs use: the matrix for \(B\), Cayley–Hamilton, the linear-form
identity, powers through \(B^{24}\), the length-4 Cayley ball, doubling on
every word through length 6, four dirty pairs, and the three-bit matrices.
`test_verify.py` repeats the strict-failure receipt and rejects an \(\ell_1\)
factor of 1, a length-3 witness, a passing four-letter moment, and a length-4
witness for \(B^2\). These checks do not replace the induction.

```sh
python3.12 -B scripts/research_package.py --package research/sl2z-shear-recurrence-inequality
```

Python 3.12, standard library only. A direct run of the two scripts is the
same check. No selected cold replay, Lean proof, native bit-supplier
admission, or full group-algebra multiplication was run.

## Scope

Card `bit-new-register-model`, scope **changed**. The card asks for a new
register identity. This package does not construct one. It prices the
released supplier/recurrence question on the shear alphabet already fixed by
PR #3905, PR #3937 and PR #3947. Span-four and span-six dirty-auxiliary
censuses are a different question on the same card and are not refined here.

**Expansion decision: stop.** A passing quotient moment is not acceptance.
Another formal-word search in this alphabet is not justified by a bill that
already fails \(M(a)<1\).

## Open next questions

1. Does one explicitly larger legal alphabet, still implementing the integer
   matrix \(B\) rather than a quotient, have a paid bill with \(M(a)<1\) at
   some \(a>0\)? This is the only nearby route that could make the shear
   target a supplier primitive. First name the alphabet, the rank of each
   paid gate, and the role count, then apply the same moment test to a proved
   letter lower bound. The blocker is that free maps between the present
   shear letters are outside this charging; they need their own lemma before
   they can be treated as unpaid.

## Credit

- **1337isnot1337 / OpenAI Codex (macbook-02)**, PR #3905 at
  `b27bf4c72a822b21f483e08cb3241ad9d165b66f`: the shear alphabet, the target
  \(B\), the four-call minimum and the diagonal dirty-role bill.
- **ToikY with OpenAI Codex**, PR #3937 at
  `5ee1c9cee717e682db01bff4c398b87011a135a2`: the commutative-carrier
  obstruction and the request to price a noncommutative bill and the
  supplier/recurrence inequality.
- **ToikY with OpenAI Codex**, PR #3947 at
  `4026d068981e6e2d5e9f0b96c3cb1ba9957b841f`: the three-bit quotient, the
  one-XOR endpoint, and the explicit statement that no supplier inequality
  was proved. The matrices checked here are recomputed from the integer
  action, not copied as a source archive.
- **eumemic** and **huxint** remain the register-model predecessors cited by
  PR #3905. The moment shape is the repository supplier test
  \((1/W)\sum n_r(r/m)^{1-a}\).

New inequality, proofs and checks by **unpaidmoon** with substantial AI
assistance (Cursor Grok 4.7). Apache-2.0. No independent human or
formal-kernel review is claimed.
