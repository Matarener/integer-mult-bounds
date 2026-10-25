# One selected pair, its decoder, and the next ordinary bridge

This result is an exact obstruction for one declared interface. It does not
construct a paid replacement supplier or change the selected multiplication
constant. All source pins and inherited attribution are listed in
`SOURCES.json` and `PREDECESSORS.json`. New analysis and replay code are by
Chris R / Clear1nsight with OpenAI Codex assistance, Apache-2.0.

## 1. Actual caller and observation

The source is the selected replay archive with SHA256
`22c3f4dce4b897a1d423d1388801933e288b6a6b1906cb15e1b16a5eb68db754`.
Its `t16/global/hosted/GLOBAL-TEMPLATE.json.gz` calls the selected `gauge44`
provider in replica 0, pair 0, forward at stage 0 in **calls[0]**, and
backward at stage 1 in **calls[4]**. The corresponding execution-schedule
indices are 0 and 4; the same-replica source-event indices are 0 and 1.
The verifier checks the full local-word hashes and owner lists against
this source, rather than interpreting the first two serialized calls as
a pair. In fact calls[1] is replica 8, stage 0, forward. This wrong-pair
control is an executed assertion.

Execution events 1, 2, and 3 are forward calls in replicas 8, 1, and 9.
Their data endpoints are disjoint from replica-0 pair-0 and pair-1 data.
They borrow respectively 66, 123, and 149 of pair-1's fields as helpers;
they borrow none of pair-0's data fields. Their literal source word is
hash-checked and its full helper return is replayed on the test domain
below. Thus intervening use does not change either witness endpoint.
This is a preservation argument for these events, not their deletion from
the actual schedule.

Execution event 5 is replica-0 source-event 2, an idle cover sweep on
pair 1 from level -1 to level 1 with child indices [0,2]. Event 6 is
replica-0 source-event 3, the coefficient +1 bridge with dst=0 and src=1.
Writing a pair-bank index as a superscript and a port index as a subscript,
its two legs at every port p are

    X^0_p <- X^0_p + X^1_p,
    Y^1_p <- Y^1_p - Y^0_p.                         (1)

Both witnesses initialize pair 1 to zero. The idle transition consists
of homogeneous native operations and preserves zero. It therefore cannot
mask the difference in current Y^0 supplied to the second leg of (1).
The bridge observes all 112 ports; no selected port is silently dropped.

## 2. Domain, frames, and the invertible object

At a fixed port, the full cover consists of all d in O(73,2). Different
cover positions hold independent arbitrary arrays. The pinned
`QQ16-COVER-ACTION-ADDENDUM.md` defines

    (M_(g,a) f)(d,z) = f(d g, z + d a),
    M_(g,a) M_(h,b) = M_(g h, a + g b),             (2)

with binary address addition (and the same translation on every tensor
factor). Consequently a delta function of the owner d is an admissible
input, even when each payload array is constant in its address z.

This is the declared independent-cover module interface. We have not
authenticated an outer integer-multiplication entrance map or characterized
its reachable states at the first F0 call. The witness therefore rejects
replacement for all states permitted by this module interface; it does
not assert that this delta input is produced by a particular multiplication
input. A repair restricted to a smaller reachable subspace would need its
own entrance invariant and continuation proof. Reachability of this
witness from the outer algorithm is left unestablished.

We specialize only the payload to its constant character. This is a
physical invariant subspace. The native convention in the pinned
`BRIDGE-REVIEW.md` is

    C_a = ((1+i) I + (1-i) T_a)/2.

Every C_a, its inverse, every address translation T_a, and every product
of these native frame factors fixes the constant payload exactly. There
is no discarded phase. Initial X has frame C_(d q), initial Y has frame I;
completed stage-s frames are F_(d U_s) on X and
F_(d U_s) C_(d q)^-1 on Y. All are identity on this subspace. The completed
stage-1 boundary is conventionally F17. Thus the witness is simultaneously
a valid framed witness, without claiming an all-character replay.

Each local call has 704 persistent role coordinates: 224 data and 480
arbitrary borrowed helpers. Eight separately owned private coordinates
bring the scratch replay to 712 columns. `scalar_replay` starts with all
712 independent input columns and checks that every helper output is
its original column, every private output is zero, and every data output
is independent of helper and private inputs. It extracts the 224-data
block only after those checks. The 712-coordinate map clears private
state and is never inverted.

The physical helper owner sets of calls[0] and calls[4] have intersection
40 and union 920. Thus the pair's physical persistent union is 1144 fields
when the other events are held fixed; it is not one shared 704-field
physical bank. Inverse statements below concern the 224 data coordinates.
Helper identities can be extended on their actual physical union because
each call returns its arbitrary borrowed helpers. The intervening calls
are handled by the explicit preservation check above.

For source data, each call's X and Y role at port p has the same owner
route `[1,stage,p]`. The literal scalar net map on this payload subspace
has only same-port coupling. Gathering and scattering via that route
therefore cancel even on owner-varying inputs. Native and phase factors
fix the payload, and arbitrary helper values return. This justifies the
source formulas used below on arbitrary cover fields within this
payload-constant subspace; it is not a general native proof for arbitrary
payloads.

## 3. Keep G, Q, and D distinct

Let G_F and G_B denote the two literal selected source calls. Let Q_F and
Q_B denote literal `F_0` and `B_1_2` in the pinned QQ16 packet. For the
common-cover constant specialization, direct exact rational replay gives

    G_F(x,y) = (x,y+x),
    G_B(x,y) = (x-y,y),
    G = G_B G_F : (x,y) -> (-y,x+y).               (3)

Set Q=Q_B Q_F. Both G and Q are invertible 224-dimensional data maps.
Writing S=A union T, where |A|=|T|=8 and U is the other 96 ports, the
constant-specialization replay gives

    rank(Q-G) = 32,
    rank((Q-G)_X) = rank((Q-G)_Y) = 16.

The differing output ports in each leg are precisely S. All 192 ordinary
X_U and Y_U rows agree in this specialization. The separate forward and
backward differences have ranks 24 and 32, respectively. This is an
algebraic update-rank statement, not a lower bound on native calls.

The actual 3813-event decoder D is the vendored #4015 WORD with SHA256
`272d8c1bd172c29044eb227ec6d67a882501250978234685e035158f4479aa58`.
It leaves all 224 borrowed current inputs unchanged and places the
recovered original inputs into its 224 owned output fields. Direct replay
checks, on the stated specialization,

    D Q = Q D = I_224,       rank(D G-I_224) = 32.  (4)

Its inherited native contract recovers the pre-pair values in F17; it
does not claim to output the selected pair's current values. The all-native
#4015 correctness and allocation obligations remain inherited, not
re-proved by (4). The algebraic correction H=G D would have
rank(H-I)=32 in this specialization, but no paid physical implementation
of H is supplied here.

For original X_0=1 everywhere and all other input zero, literal Q gives
(X_0,Y_0)=(13,-12), whereas literal G gives (0,1). The next full bridge
therefore gives Y^1_0=12 under Q and Y^1_0=-1 under G. These numbers are
computed from the replay matrices and actual signed bridge.

A separate decoder misuse control starts with X_1=1 everywhere. Both G
and Q have current Y_1=1, so their actual bridge gives Y^1_1=-1. D Q
instead recovers the original Y_1=0. Treating that recovered original as
the current bridge source would give zero. Recovery alone does not match
the caller endpoint or eliminate the cost of computing it.

## 4. The sole pivot: owner dependence defeats selected-only post-repair

The agreement on U in section 3 invites a post-pair repair confined to
selected ports S. We test exactly this class, preserving the actual
cover routes rather than identifying independent owners.

Choose the legal input

    X^0_0(d,z) = 1 if d=I_73, and 0 otherwise,

constant in every payload address z. Every other data field, helper,
private field, and pair-1 field starts zero. Stage 0 has no owner maps,
so the literal Q_F scalar replay applies pointwise in d. In Q_B, replay
every prefix event, including all 528 cover maps. Represent a field as
a sparse exact rational sum of f(d h), where h is a full 73-column
binary matrix. A map g acting on an existing term h produces **g h**
by (2); order is retained. Native lines fix the constant payload. The
remaining final backward core preserves every Y coordinate, which is
checked by replaying all its 712 scalar input columns.

An independent expression for the ordinary Y residual is

    (Y_Q-Y_G)_U = (K_1,U ell_1,T P_0 - K_0,U) R_0 x.  (5)

Here R and K are taken from the actual packet; P_0 and the selected
intermediate coefficients are read from the literal F0 replay. The
stage-1 owner matrices rho_p are independently reconstructed from the
actual `DATA-PHASES.json` idle-child axes by swapping those eight axes
with the first external block. Each is checked orthogonal, involutive,
and fixing its port normal. They must also occur in the packet map
registry. Formula (5) and literal prefix replay agree for all 96 ordinary
Y rows on the original X_0 input column. This check is not a claim of
full operator equality on all input columns.

At ordinary port 1 the exact residual operator on that input is

    (Y_Q-Y_G)_1 = (D_(rho_1 rho_76) + D_(rho_1 rho_81))/4
                  - I/2,                         (6)
    (D_h f)(d) = f(d h).

The two products are distinct nonidentity members of O(73,2), checked as
full 73-column matrices. Their column-0 values are 448 and 460, whereas
I_73 has column-0 value 1. On the chosen delta input at d=I_73, the two
translated terms are zero and the identity term is one. Hence

    Y_G,1(I_73) = 0,       Y_Q,1(I_73) = -1/2.      (7)

After the real idle transition and bridge (1), pair-1 Y at this ordinary
port is zero under G and +1/2 under Q. All 96 ordinary Y operator rows
in (5) are nonzero on the original-X_0 field, although (7) alone suffices.
If all owner maps are deliberately collapsed to identity, each ordinary
residual vanishes. That executed control explains why section 3 misses
the obstruction.

**Excluded class.** After this exact Q pair, consider any adapter whose
writes to persistent fields are confined to pair-0 X_S and Y_S, followed
by the unchanged named full bridge. All nonselected pair-0 fields,
pair-1 bridge inputs, and other persistent bridge inputs remain unchanged;
only private work and those named selected pair-0 fields may change.
The adapter may read other fields, but it leaves current pair-0 Y_1 and
the pair-1 Y_1 bridge target unchanged. Equation (7) and the second bridge
leg therefore force the observed difference +1/2. Such an adapter cannot
realize this selected source-pair-to-bridge interface on every state
permitted by the declared module domain.

The statement does not exclude changes earlier in the selected word,
repairs that write U or other bridge inputs, factored query repairs outside
the declared write class, a different global endpoint or terminal consumer,
or repairs justified on a proved smaller reachable subspace. Other
representations or input domains require separate interface proofs.
Using nonconstant-payload intermediate operations does not evade this
obstruction if the adapter still has the declared write support and must
work on every permitted input, including this constant-payload witness.
No global
impossibility or best-possible repair price follows from this witness.

## 5. What is paid, and what is still missing

`COST.md` gives the independent literal ledger. In particular the
selected pair contains sixteen rank-eight centre children. QQ16 removes
those and introduces thirty-two rank-one children: +16 native calls,
-96 native rank sum, and +28,616 scalar real primitives under the declared
compiler allowance. These are counts, not comparable native costs.

Adding the actual retained decoder gives a raw subtotal relative to the
selected pair of +240 native calls, +128 native rank sum, and +55,560
scalar real primitives, before endpoint conversion or repair. Its owned
outputs, private work, cover maps, native wrappers, release obligations,
precision, movement, and source-caller incidence must be priced under
compatible contracts. The unchanged bridge is present on both sides of
a valid comparison. Its invoice cannot be removed by using an inverse
which supplies a different boundary value.

The result closes this single selected-only post-repair proposal by a
concrete first pair and its next consumer. A successful broader repair
and its paid local-to-global supplier contract remain open. No invocation
fraction, terminal cleanup assumption, or reduced global multiplication
constant is admitted by this package.
