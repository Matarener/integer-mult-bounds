# The fixed C511 interface and its five-call invoice

The scientific pin is `20ecf2891d80b5acf18d980b2164fb44ea7faa90`.
The fixed local word is `BIT-THREE-COPY-INPUT-WORD.json.gz`, with gzip SHA256
`ac8a6dcd5957f49eefd6fc945332b1c31afa26c48fc301d37bfb1338beea6847`.
It uses111 source registers,111 target registers and438 ordinary helpers:
660 arbitrary independent ordinary inputs. One additional private register
is required initially zero and is erased after each of three copied totals.
The private register is not a661st arbitrary input. Its zero row is included
in every endpoint and roundtrip check.

The scalar code C has binary rank111, defect rank `rank(C-I)=9` and exact
order511. Its literal signed source code has1487 ADDs. This is the older
C511 word; it is not the later R429 order28 code with1499 ADDs.

## Exact local scalar contract

In logical frame coordinates the binary VALUE endpoint is

    (x,y,h,0) -> (C x, y+C x, h,0).

The literal inverse has binary endpoint

    (x,y,h,0) -> (C^-1 x, y+x, h,0).

The independent checker carries all660 arbitrary ordinary input columns
as dense integer rows, plus the zero private row. It verifies both endpoints,
every old-target identity coefficient, every helper row, all private
COPY/ERASE cuts and the full signed literal-inverse roundtrip. It also
reconstructs the1487 signed source ADDs separately and compares their
entire integer matrix with the source endpoint.

Over Z the precise endpoint has the form

    (x,y,h,0) -> (C_Z x, y+A_Z x+E_Z h, h,0),

where `C_Z` is the literal unimodular signed code, `A_Z=C mod2` and
`E_Z=0 mod2`. The integer target block is not inferred to equal `C_Z`.
Reversing all ADDs with opposite signs and reversing the typed COPY/ERASE
word restores every ordinary integer input. Forward and raw-inverse signed
prefix row-L1 maxima are64400 and1405988; these are finite scalar bounds,
not rounded precision or native-child error bounds.

At each COPY the source is at actual FULL and the private field is at its
actual rank-seven cap, costing rank1. The copied source remains unchanged
until ERASE, where the private and source rows are compared over Z. All
three episodes reuse the same zero private field. An omitted ERASE is
rejected when the word next attempts to modify the still-live copied source.
Changing one source-code sign preserves the full binary endpoint but changes
the integer source matrix, providing a separate signed-control witness.

The complete coded local histogram is

    H1=1325, H2=1342, H3=79, H4=44, H5=102, H6=11, H7=9.

It has native rank mass5061 and13283 scalar ADDs. These counts include all
three private rank-one COPY queries. The same positive rank invoice applies
to the literal inverse, whose frame path runs in the opposite direction.

The code order is checked independently by `C^511=I`, `C^73!=I` and
`C^7!=I`. Since511=7*73, these exclude every proper divisor of511. The
five-call proof below does not use finite order511; it uses only invertibility
of C and the actual intertwiners.

## Physical local blocks

Let F be the local full rank-eight head/tail exchange, N the diagonal
rank-one source-line exchange and `G=F N` the rank-seven cap exchange.
F and N are commuting involutions. The source code acts separately on HEAD
and TAIL and therefore commutes with F. It does not commute with N.

Converting the verified logical endpoint to the declared physical frames
gives, over binary VALUE operators,

    B_C = [[F C N, 0], [G C N, G]].

Its inverse is

    B_C^-1 = [[G C^-1,0], [F,G]].

For example, the lower-left inverse entry is
`G*(G C N)*(N C^-1 F) = F`; the signs disappear in characteristic two.
Both complete block products are the identity using only
`F^2=N^2=I`, `FN=NF`, `FC=CF` and `C C^-1=C^-1 C=I`.
No step commutes C with N.

These operator identities are statements about binary VALUE arrays. They
are distinct from the signed integer lift above. Ordinary helpers are
restored in logical frame coordinates. Forward helper frames run ZERO to
FULL; inverse helper frames run FULL to ZERO. For an arbitrary incoming
physical helper, interpreting its logical symbol in the declared entrance
frame gives the rank-eight physical residual in either direction. This
interpretation does not execute a free entrance query, nor does it establish
a chronological caller owner schedule matching those boundaries.

## The actual routed charts

The route matrices use the deterministic upstream Weyl-BFS tree on the
actual120 full E8 root lines. The independent checker selects that tree
from the root adjacency graph, reconstructs each reflection path over the
dyadic rationals and verifies all111 resulting rho hashes against the
frozen receipt. No producer geometry function is imported.

For a port root q of norm four, put `P=q q^T/4` and `K=I-P`.
The Weyl route supplies an8-by7 matrix A with `A A^T=K` and `A^T A=I7`.
On the common core8 and one fresh7 block the chart is

    rho = [[P,A],[A^T,0]].

It is symmetric and involutive. With `G0=diag(K,0)`, `E=diag(0,I7)` and
`F_s=diag(P,I7)`, the exact projector identities are

    rho G0 rho = E,       rho F_s rho = diag(I8,0).

The chart also preserves the source-line projector. The checker evaluates
all these equalities at every port. A code coefficient between ports q and p
is routed by `rho_p rho_q`, acting separately on HEAD and TAIL. Consequently
each of the6465 nonzero binary C coefficients intertwines the corresponding
old-cap operators and local full operators. Thus C_s commutes with G0 and
its local F_s. Every other fresh G_t is disjoint from this chart's active
coordinates and commutes with C_s. A common full parent exchange commutes
with every HEAD/TAIL-separated route and with its literal inverse.

The noncommutation with common N is concrete. For actual code edge(0,1),
the `(0,8)` entry of `P_0 rho_0 rho_1` is1, whereas the same entry of
`rho_0 rho_1 P_1` is0. This is an exact dyadic witness, not a formal naming
distinction. It remains nonzero in every odd ADDRESS field. The projector
equations likewise descend to odd ADDRESS fields because all denominators
are powers of two. The old local native MOVE/COPY implementations and
their guards remain inherited premises.

## Five calls and a paid terminal decoder

Normalize each local call by factoring out its fresh cap exchange G.
The two CLEAN orientations and the coded forward call become

    F_clean = [[I,0],[N,I]],
    B_clean = [[I,N],[0,I]],
    Q_C     = [[N C N,0],[C N,I]].

The universal identity uses two arbitrary banks. Execute CLEAN forward,
CLEAN backward, CLEAN forward, and then an ordinary bank swap. Since N is
an involution, the normalized output is `diag(N,N)`. Next execute the coded
forward call and one CLEAN forward call. Acting on that diagonal gives

    F_clean Q_C diag(N,N) = diag(N C,N).

One direct check starts with `(N x,N y)`. The coded call gives
`(N C x, C x+N y)`; the final CLEAN call adds `N(N C x)=C x` to its target,
leaving `(N C x,N y)`. This proves the identity for every invertible C;
no commutation of N and C is used.

Let the five cap exchanges be `G0,G1,G2,G3,G4`, with C coded at stage3.
The actual chart intertwiners allow all other fresh exchanges and G0 to
pass C3. Their product is Gamma. The parent has width
`8+4*7=36`, and `Gamma N=T_parent`. Therefore the physical five-call word
is

    T_parent diag(C3,I).

Because the full parent exchange commutes with the actual routed code,
the literal1487-ADD inverse on bank0 removes C3 at the final full parent
cut. The bank swap costs333 scalar ADDs. The word is restored on its two
arbitrary public banks in the binary VALUE/native sense, with all helper
occurrences retaining their declared logical return and physical residual
contracts.

The independent operator oracle uses normal forms in the group ring over
F2 of `C2(F) x (C2(N) * Z(C))`. It checks both local physical inverse
products and executes the five normalized bank updates on both input
columns. This is a symbolic all-operator identity, not a sample of small
numeric matrices. The actual source/geometry binding remains finite and
separate. A control replacing the first of the three seed calls by the
coded call gives `[[0,N],[C N,0]]`, exposing the wrong-side `C N` rather
than `N C`. The actual noncommutation witness makes this distinction physical.

## Complete failed cost invoice

One CLEAN local call has24248 ADDs and histogram

    H1=1322, H2=1342, H3=79, H4=44, H5=102, H6=11, H7=18,

including nine rank-seven private copies. The independent check reconstructs
that literal CLEAN word from the frozen R438 phases and verifies its
all-column endpoint and complete typed invoice.

Four CLEAN calls plus one coded call give

    H1=6613, H2=6710, H3=395, H4=220, H5=510, H6=55, H7=81.

The native rank mass is25545. Public progress is `2*111*36=7992`;
2190 independent ordinary helper occurrences contribute `2190*8=17520`.
The one reused private field incurs total COPY rank `4*63+3=255`.
The uncovered deficit is

    7992 + 17520 - 25545 = -33.

The complete scalar ADD count, including terminal decoding and the swap, is

    4*24248 + 13283 + 1487 + 333 = 112095.

The local five-call construction therefore fails already at zero rate.
This invoice does not become favorable by omitting the COPYs, the final
decoder or the target/source frame progress. Further owner padding and
physical costs are additional obligations, not improvements to this fixed
invoice. No positive-rate moment or exponent is supplied.

## Source-consuming inverse

Precode the inverse's source by C and then decode its target by C^-1.
For arbitrary source x and old target y, the exact binary physical map is

    (x,y) -> (G x, F x + C^-1 G y).

Here the inverse first gives `(G x,F C x+G y)`; the target decoder commutes
with F but not necessarily G. Consequently the desired full output `F x`
requires all111 caller-supplied target fields to be zero. The source is
consumed into Gx. These two linked outputs come from the same111 inputs
and do not supply two independent families of public query credit.

Crediting only the FULL output and the ordinary helper progress gives

    111*8 + 438*8 - 5061 = -669,

before charging the111 zero-output fields. The two1487-ADD codes and the
13283-ADD inverse total16257 scalar ADDs. Calling these codes free means
they add no native recursive query rank; it does not mean zero arithmetic,
source access or routing cost. The internal private field is separately
required zero and erased. No restored-source or restored-zero-output
interface follows from this construction.

## Covered domain and unresolved implications

The result comprises the exact finite C511 scalar word and lifecycle,
source-bound dyadic routes, a universal noncommutative binary composition,
and complete negative local invoices. It covers arbitrary ordinary inputs
with the stated zero-private/zero-output premises. It does not turn logical
helper restoration into physical identity restoration. No chronological
whole-owner allocation, rounded child-defect theorem, all-size source or
tape bound, formal-kernel proof or improved multiplication exponent is
claimed. The separate historical million-pair searches, rolling words and
quotient obstructions are not premises of this bounded interface result.
