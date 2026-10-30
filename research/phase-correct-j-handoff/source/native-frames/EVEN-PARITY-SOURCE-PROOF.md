# A changed native response that retains an already-full source

Source pin `20ecf2891d80b5acf18d980b2164fb44ea7faa90`. This is the actual
local interface in `even_parity_source.py` / `EVEN-PARITY-SOURCE.json`.
It does not complete a caller or replace an existing N response.

Let E be the actual product of N_i=`i Hp_f Hq_f` on L>=2 old planes,
already full native on all 2Lf address bits. This is a paid incoming
premise. In particular an arbitrary dirty field u cannot be reinterpreted
as E*(E^-1 u) and then credited with free full progress: its actual
entrance/terminal residual must still be charged.

For each bit position take q_k=p0_k+q0_k and let
`C_even=product_k C_qk`, where `C_q=((1+i)I+(1-i)X_q)/2`.
The q_k are independent and pairwise orthogonal, including self-products.
The query has exact native arity f and `C_even^2=X_all_p0+q0`, with that
ADDRESS translation retained. Its native lowering is a bitwise CNOT
conjugation of one selected rank-f C child. The two ADDRESS adapters are
paid.

The binary symplectic E has A=D=I, C=0, B=I. If
`Gamma=sum q_k q_k^T`, then `Gamma^2=0`, so the B block of C_even E is
`I+Gamma`, invertible with inverse itself. Thus this query preserves an
isolated full-native source endpoint. It does not leave the source
operator equal to E.

A useful quadratic response has two selected even parities per bit:

    v_k=p0_k+p1_k,   w_k=q0_k+q1_k,
    U=product_k C_vk C_wk,
    Z=Z_all_p0 Z_all_q0,
    J_f=i^(f+1) Z U.

The mandatory phase identity is `Z C_v Z=i C_v^-1` when Z anticommutes
with X_v. Hence `ZUZ=i^(2f) U^-1` and `J_f^2=-I` for every f. The
incorrect constant-i normalization squares to `(-1)^(f+1) I` and is
rejected for odd f. These phase identities retain the source convention
and are consistent with the prior phase discipline of PR3987/4002, not
a new generic phase-normalization claim.

J_f has arity 2f. Its parity vectors are mutually orthogonal, so the same
`I+Gamma` argument shows that J_f E remains full native. More concretely,
let A be bitwise CNOT p0->p1 and q0->q1, and put

    M_f=X_all_p0 Z_all_p0 P_A.

Then `J_f=M_f N0 M_f^-1` exactly. M is one affine ADDRESS plus one Pauli-Z
scan. Thus the existing one-H2 native query can expose the changed J
response through two explicit monomial adapters. The source frame
relative to the unchanged incoming E matters: globally conjugating E as
well would reproduce the old deficit. The literal source response is J,
not N0, and the right/left gauges cannot be omitted inside a mixed caller.

For K=C_even or J, the complete two-bank word is simply

    source=K source; target+=source.

On two independent original fields in the E chart this gives
`(K E*x, E*y+K E*x)`. Its literal inverse subtracts the current source
from the target and then applies K^-1. No zero helper, private field,
COPY promise or untouched target is used. This full two-column identity
and both inverse orders are checked in the exact all-f tensor algebra.
It is a source/delivery primitive; the target is not yet isolated.

The retained source operator K E has explicit full-native monomial
left/right gauges in the receipt. For L=3 they are independently checked
at f=1,2; the exact tensor identity proves the all-f phase. Native query
recipes and J^2=-I are additionally checked at f=3. The phase formula is
`J_f=i^(1-f) J_1^tensor f` and
`E_f=i^(L(1-f)) E_1^tensor f`, so endpoint gauges carry the combined
Gaussian unit `i^((L+exponentK)(1-f))`. The native response bill is one
H1 or one H2 respectively, plus one delivery ADD and both monomial
adapters. All bank reads, address/phase passes, endpoint adapters,
precision and physical head-return work remain paid.

There is a necessary limitation. Every even C_q commutes physical Z_all
and X_all. A binary orthogonal A fixes the all-ones vector; its typed
correction z has z.dot1=0, so P_A Z_z also commutes both global Paulis.
Any bank word made only from these even queries and those corrected
orthogonal controllers commutes diag(Z_all). A full-native Clifford
with invertible B cannot fix nonzero Z_all. Thus that restricted grammar
cannot create the full target from raw inputs. An already-paid odd/full
anchor or a genuinely different controller is necessary. Arbitrary
nonorthogonal ADDRESS adapters are outside this commutant assertion.
For our even-size E the X_all test alone would be insufficient: E itself
commutes X_all but does not commute Z_all.

The useful next obligation is a complete independent-column caller
requiring the J or even-C response and accepting its actual isolated
endpoint, with the incoming anchor and every owner residual priced.
No current reader is silently replaced, and no new exponent is claimed.
