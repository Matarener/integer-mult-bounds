# Current-output query factor for the first QQ16 pair

This note constructs one logical repair of the selected first pair, using
queries of its **current QQ16 outputs**. It repairs ordinary ports as well
as selected ports and matches both X and Y. Exact replay proves the entire
factor on the full cover with constant payload. Its declared logical word
is not yet an admitted native word: each owner-view addition still needs
a paid physical phase and frame lift. The independent native check in
`NATIVE.md` identifies that distinction concretely. No supplier improvement
or global multiplication constant is claimed.

New derivation and code: Chris R / Clear1nsight with OpenAI Codex assistance,
Apache-2.0. Sparse rational arithmetic, local scalar replay and source-route
helpers are adapted from the retained #4105 primary verifier, with its
attribution preserved. No predecessor executable is imported or run.
The retained QQ16 packet, source archive and other inherited contracts are
pinned by `SOURCES.json` and `PREDECESSORS.json`.
In particular, the retained `CONSERVED-QQ16.md` states the complete
ordered full-cover maps, their invertibility on arbitrary data, restoration
of all 480 arbitrary borrowed helpers, and return of all eight owned
private fields to zero. Those native/global-source contracts remain
inherited; this package's new exact replay is explicitly restricted to
the payload-constant domain until a physical lift is supplied.

## 1. Exact endpoint and domain

The source remains replica 0, pair 0, selected `gauge44` calls[0] and
calls[4], respectively forward stage 0 and backward stage 1, in the pinned
selected replay archive. Their literal program hashes and 224 data owner
records are checked again. The next full bridge is hosted event 6, source
event 3, with src=1, dst=0 and coefficient +1. Its two legs at every port
are

    X^0_p += X^1_p,       Y^1_p -= Y^0_p.           (1)

Thus a successful replacement must supply both current pair-0 data banks,
and preserve pair-1 bridge inputs. The factor here never reads or writes
pair 1 or any borrowed helper. All its persistent data writes are to
pair 0. The same-replica idle transition and intervening replicas are the
unchanged continuation already bound in the retained #4105 evidence.

Let G be the selected source pair and Q=Q_B Q_F the actual QQ16
`F_0; B_1_2` pair. The target is H Q=G. No use is made of the #4015 decoder
word, and H is not confused with Q inverse or with a decoder that merely
recovers original data.

A cover field has independent values at every d in O(73,2). The owner
operator is

    (D_g v)(d)=v(d g),       D_g D_h=D_(g h).       (2)

Matrix order is retained. Every payload array is initially allowed to
vary independently with d. For the executable exact identity we specialize
the payload address to its constant character, on which native lines,
translations and frame factors are identity. This is the declared legal
module subspace used by #4105, not a proof that every such state is reached
from a particular outer integer-multiplication input.

The algebra below also describes a logical factor when the inherited
all-payload QQ16 contracts and selected boundary gauges are used. A physical
realization must implement the corresponding conjugated operations; the
logical equations alone do not authorize treating D_g as a raw uncorrected
physical map or adding differently framed physical fields.

## 2. Query notation and exact selected inverses

Use the actual packet's 8 by 112 matrix R and 112 by 8 matrix K. The port
sets A and T each have eight elements; U contains the other 96. For stage
s, let D_s be the diagonal port-owner routing with entries D_(rho_s(p)),
where rho_s(p) is the actual orthogonal involution from DATA-PHASES.
D_0=I. Define

    R_s = R D_s,       K_s = D_s K,
    ell_s,V = R_s Pi_V,       P_s,V = Pi_V K_s,

for V=A,T, where Pi_V is coordinate restriction/extension on the same
port space. The packet's exact coefficients give

    ell_s,A P_s,A = ell_s,T P_s,T = I_8,
    P_s,A ell_s,A = Pi_A,
    P_s,T ell_s,T = Pi_T,
    R_s Pi_U K_s = 12 I_8.                        (3)

These identities use cancellation of the same port's route, not
commutation of different owners. All three coefficient products are
checked exactly from R and K. In particular the stage-change query map
ell_1,T P_0,T is invertible, with inverse ell_0,T P_1,T:

    (ell_0,T P_1,T)(ell_1,T P_0,T) = I_8.          (4)

Equation (4) follows from the same T support and (3). It is not inferred
from a constant-cover matrix or an assumed eight-channel compression.

The future-stage selected-A operator used by the actual B1_2 contract is

    E_2 = I + P_2,A (R_2-ell_2,A),
    E_2^-1 = I - P_2,A (R_2-ell_2,A).             (5)

The cross term squares to zero because (R_2-ell_2,A) P_2,A=0. E_2 is
not identity on the constant-payload, owner-varying domain.

## 3. Recover only the queries needed by the current endpoint

Write x,y for the original pair inputs and xF,yF for the intermediate
forward outputs. Write X,Y for the current QQ16 pair outputs. These are
logical coefficients in their declared boundary frames, not a claim that
all physical fields share one frame.

The packet's forward contract is

    f=R_0 x,
    xF_U=x_U-K_0,U f,
    xF_A=P_0,A ell_0,T x,
    xF_T=P_0,T f,
    yF_U=y_U+xF_U,
    yF_S+xF_S=y_S+x_S,           S=A union T.      (6)

For the actual backward contract set a=ell_1,T xF, u=E_2 yF and b=R_1 u.
It gives

    Y_A=u_A,
    Y_U=yF_U+K_1,U a,
    Y_T=u_T-P_1,T(b+11a),
    X_U=xF_U-yF_U,
    X_A=xF_A+yF_A-u_A,
    X_T=P_1,T(b+12a).                             (7)

From (3) and (7), the query a is **available from current outputs**:

    R_1 Y = b+12a-(b+11a)=a.                      (8)

The following five eight-field records are enough:

    a = R_1 Y,
    f = ell_0,T P_1,T a,
    u = Y-K_1,U a+P_1,T(ell_1,T X-a),
    n = (R_2-ell_2,A)u,
    t = ell_0,A(X_A+P_2,A n),
    c = R_0 Pi_U(X_U+Y_U-K_1,U a).               (9)

Here u is only notation: the literal word expands (9) and never allocates
an entire u bank. Its five records are a,f,n,t,c. The same is true of any
intermediate xF expression below; no hidden 112-field scratch bank exists.
The formula for f is justified by xF_T=P_1,T a followed by (6), or by the
actual chart inverse (4). Nothing retains f for free through the pair.

Equations (5), (7) and (9) yield

    xF_U=X_U+Y_U-K_1,U a,
    xF_A=X_A+P_2,A n,
    xF_T=P_1,T a,
    x_T=P_0,T t,
    x_A=P_0,A(-11f-c-t).                         (10)

For the last identity, apply R_0 to x and use
R_0 Pi_U K_0=12I, R_0 x=f, and ell_0,T x=t. This gives
ell_0,A x=-11f-c-t.

On the payload-constant source specialization, literal selected replay
proves G(x,y)=(-y,x+y) at every owner. The desired repaired endpoint is
therefore

    Y*_U = Y_U-K_1,U a+K_0,U f,
    Y*_S = X_S+Y_S,
    X*_U = X_U,
    X*_T = P_0,T t-Y*_T,
    X*_A = P_0,A(-11f-c-t)-Y*_A.                 (11)

Both selected sums in (11) follow from conservation in (6) and (7).
There is no extra P_1,T a term in the selected Y endpoint. The X formula
is essential: matching only ordinary Y would not suffice for (1).

These equations establish a genuine current-output factor. They do not
claim that the original input, intermediate forward queries, or cleared
private centres remain available at the repair boundary.

## 4. The literal logical word and storage

`CANDIDATE-WORD.json` contains the full emitted logical operation list.
Its operation

    add_view(target,source,coefficient,g)

means target(d) += coefficient * source(d g). Every matrix g is recorded
as 73 actual binary columns. The route registry includes I, rho_1(p),
rho_2(p), and the ordered product rho_2(p)rho_1(p). No formal label is
silently identified with another matrix.

The word contains 6,112 such additions and 104 owned CLEARs. It uses
33 owned physical fields, with these exact lifetimes:

- q0..q7 hold a, and q8..q15 hold f.
- q16..q23 initially hold n. After the last read forming t, they are
  cleared and reused for c.
- q24..q31 hold t.
- q32 is one selected-output delta temporary, cleared before and after
  each of its 16 uses.

The five query records therefore do not mean 40 simultaneously allocated
fields. Conversely, the 33 owned fields are real stock obligations; they
are not supplied by the source pair's eight cleared private fields without
an explicit allocation contract. Every field is cleared before its first
read and ends zero. No borrowed helper is used as free scratch.

After gathering all queries, the word updates Y_U and Y_S as in (11).
For each selected port it forms in q32

    desired_original_x_p - updated_Y_p - old_X_p,

adds this delta to X_p, and clears q32. It never clears a persistent data
field, never uses a zero scale, and never overwrites unavailable old data
before its last required read. X_U stays unchanged. The untouched pair-1
inputs make equality of both current banks sufficient for equality after
both bridge legs, for arbitrary pair-1 data in this module comparison.

The owned gauge F17(d) in the word is a proposed type for a physical lift.
It is not a proof that every add_view can be executed at that gauge for
free. `NATIVE.md` treats the required native corrections separately.

## 5. What the executable identity checks

The primary verifier authenticates the source archive and packet, then
replays the literal F0 scalar word with all 712 independent local input
columns. It checks the 480 borrowed helper identities, eight private
outputs zero, and no helper/private dependence in the 224 data outputs.
It applies every B1_2 prefix event, including all 528 actual owner maps,
to those 224 free data columns over the exact ordered owner algebra.
Every scalar gate, owner map and native line in that prefix is separately
checked to avoid all 480 borrowed helper registers. Its zero-helper replay
is therefore not being used as a proof about arbitrary helper dirt.
The final backward core is independently checked on all 712 local scalar
columns to equal the I-KR data factor with the required Y identities;
its actual stage-1 owner lift is then applied in that factored form.
This yields 288,040 nonzero symbolic terms in the full Q endpoint.

The verifier first checks the equations (9)-(11) against all 224 source
input fields, at every formal actual owner path, and then separately
replays the emitted operation list on that literal Q endpoint. The latter
replay initializes all 33 owned fields with independent arbitrary dirty
columns. It checks exact equality to the selected G endpoint on every X
and Y field and verifies that all owned outputs are zero. A string claim
of helper return or a numerical test at one owner is not substituted for
these checks.

A further check starts with 224 independent **current** X,Y fields. It
applies the ordered inverse formulas (5)-(10), reapplies the actual B and
F contracts to the recovered data, and checks both resulting identities.
It then compares the literal emitted H on these free current fields with
G applied to the recovered originals. Thus the current-output claim does
not rely solely on H Q=G or on #4105's common-cover scalar inverse test.

The source pair itself is invertible on persistent data; private CLEARs
are not included in an inverse domain. The QQ16 contracts likewise admit
the selected inverses (3)-(5). The 712-coordinate clearing word is never
inverted. Current-output attainability follows from the displayed inverse
relations and literal composition, rather than from a rank test alone.

## 6. Native and budget boundary

A physical add_view between source gauge S(d) and target gauge T(d)
requires the conjugated operation

    T(d) D_g S(d)^-1.                             (12)

At the completed stage-1 boundary, current X has frame F17(d), whereas
current Y has frame F17(d) C_(d q_p)^-1. Thus even a same-owner scalar
addition between X and Y needs a native frame conversion. Owner routing
can create an additional phase difference, especially for the future
stage-2 routes that move axes outside the completed stage-1 frame.
An ADD count alone does not pay (12).

The independent native check supplies concrete nonzero-payload failures
of uncorrected physical additions/alignment. They reject those proposed
lifts; they do not refute the logical factor (9)-(11), and they do not
establish a lower bound against all possible native lifts.

The selected pair's sixteen rank-eight centre children can be credited
as removed only once, against a fully compatible QQ16-plus-repair word.
The logical repair has a finite scalar ledger and a 33-field ownership
obligation. Native conversion, map realization, precision, movement,
allocation and complete caller incidence remain separate obligations.
The retained #4003 or #4030 constants do not automatically apply to this
changed producer pair and five-record repair. `COST.md` states the exact
comparison and any conditional tariff screen.

The achieved result is the full-owner current-output factor and its
literal restored-workspace word on the checked payload subspace. A paid
native realization and affordable complete supplier remain open. This
session does not switch to standalone decoder optimization or a different
consumer endpoint.
