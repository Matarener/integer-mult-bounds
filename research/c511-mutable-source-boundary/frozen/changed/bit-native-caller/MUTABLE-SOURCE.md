# Exact C511 native interfaces

Scientific pin: `20ecf2891d80b5acf18d980b2164fb44ea7faa90`.
Producer: `mutable_source_caller.py`; receipt: `MUTABLE-SOURCE-FIVE.json`.
Normal and `python3 -O` compare the complete saved receipt. This is a local,
source-bound operator construction and failed budget, with no new kappa.

The frozen source is the predecessor's
`recursive/BIT-THREE-COPY-INPUT-WORD.json.gz`, gzip SHA256
`ac8a6dcd5957f49eefd6fc945332b1c31afa26c48fc301d37bfb1338beea6847`.
It has 438 arbitrary ordinary helpers, one reused zero private field,
three rank1 COPY queries, and a 1487-ADD source-only integer code C. Exact
binary replay gives rank(C)=111, rank(C-I)=9 and order(C)=511. This C is
different from the later pruned order28 code A. All 661 endpoint columns,
including the private zero column, are replayed over integers; all binary
VALUE columns are checked separately. The raw literal inverse restores all
438 helper rows and erases its private field as well.

For one native local stage let F be its full rank8 head/tail exchange, N
the diagonal rank1 source-line exchange, and G=F*N its rank7 cap exchange.
They are commuting involutions. The actual physical source code C commutes
with F, but an explicit routed coefficient witnesses that it does not
commute with N. The forward and inverse physical blocks are exactly

```
B_C      = [[F C N, 0], [G C N, G]],
B_C^-1   = [[G C^-1,0], [F,     G]].
```

In particular, the inverse target cross term is F independently of C.
Direct multiplication proves both identities. The inverse reverses the
literal typed MOVE/ADD/COPY/ERASE word; its helpers have reverse endpoint
frames. Arbitrary physical helper inputs can be interpreted in those
frames, giving the same rank8 paired residual. No initially executed FULL
helper query is inferred from this interpretation. Chronological whole
owner routing for these reverse boundaries is still a separate obligation.

Its complete local histogram, for either direction, is
`{1:1325,2:1342,3:79,4:44,5:102,6:11,7:9}`, rank mass5061. This includes
all three rank1 private copies. No rank9 scalar defect is substituted for
the actual native word or its port adapters.

For stage s>=1, the actual upstream Weyl-BFS chart rho_(s,p) obeys
`rho G0,p rho=E_s` and `rho F_s,p rho=I_core8` on every one of the111 ports.
Thus routed C_s commutes with the old cap G0 and every fresh G_t with t!=s.
The receipt checks both rational projector equations at all111 ports and
covers all nonzero C coefficients. A common full parent exchange T also
commutes with every head/tail-separate routed code and its literal inverse.
These facts justify the native composition below; commuting C with N would
not justify it and is explicitly rejected.

## Five-call restored caller

Two arbitrary input banks use CLEAN forward, CLEAN backward, CLEAN forward,
then an ordinary bank swap. The normalized result is `diag(N,N)`.
At a fresh stage apply the C3-coded forward call, then at the next stage
one CLEAN forward call. In the universal noncommutative binary operator
ring, using only N^2=I and exact C inverses,

```
F_clean * F_C * diag(N,N) = diag(N C,N).
```

The product of the five fresh cap exchanges is Gamma. With parent width
36, `Gamma*N=T_parent`; hence the physical output is
`T_parent*diag(C,I)`. Its source code is removed at the full parent cut by
the actual1487-ADD inverse. The ordinary bank swap costs333 scalar ADDs.
Every ordinary helper occurrence remains independent:2190 occurrences of
width8. The private field is reused, with total COPY rank `4*63+3=255`.

The complete five-call histogram is
`{1:6613,2:6710,3:395,4:220,5:510,6:55,7:81}`; rank mass25545.
Public progress is `2*111*36=7992`, ordinary helper progress17520, so
the uncovered deficit is `7992+17520-25545=-33`. Source decoding and the
swap bring the scalar ADD total to112095. This fails already at zero rate;
owner padding, source scans or rounded errors cannot rescue this invoice.

Replacing the first, middle or last CLEAN call of the three-call seed by
the coded call without further intermediate code gates does not give this
conclusion: the resulting matrices have a wrong-side C*N term or an
additional C+I block. Multiplying a scalar source code by a formal N is not
a free decoder across this physical cut.

## Source-consuming inverse interface

Precode the inverse's source by its free code C. Its exact map is
`(x,y) -> (G*x, F*C*x+G*y)`. If the caller supplies111 additional zero
target fields, a free target C^-1 decoder gives `(G*x,F*x)`. All438 ordinary
helpers and the one internal private field have the stated return contract.

This leaves111 consumed source streams containing G*x and uses111 caller
zero output fields. The two outputs are linked functions of the same111
inputs, so they cannot receive two independent public query credits.
Crediting only the FULL output gives `111*8+438*8-5061=-669`, before pricing
the zero output stock. The receipt therefore keeps this as a one-carrier
interface rather than a restored-source supplier.

For repeated raw inverse calls with the same source bank and fresh native
stages, let B_i=C_i^-1*...*C_0^-1 and B_-1=I. The normalized inverse is
`[[C_i^-1,0],[N,I]]`, and actual interstage commutation gives

```
source = Gamma_L * B_(L-1) * x,
target = Gamma_L*y + T_L*(sum_(i=0)^(L-1) B_(i-1))*x.
```

The target cross is a full exchange followed by a free head/tail code, but
the source remnant lacks its common N. A zero target or restored source
does not follow from this equation. A coupled rolling bank word closing
all independent source remnants remains open.

The independent finite code-cut search in `mutable_cut_search.py` permits
legal intermediate C codes before the sole coded cut and N*C*N codes
afterward. At depth3 its500 cut gates give1,500,000 pairs, with no accepted
three-call identity. `mutable_rolling_search.py` separately uses distinct
C0,C1,C2 and all forward/inverse choices:575 gates per cut at depth2,
2,645,000 pairs, no universal identity. Normal and `-O` agree. These are
bounded alphabet/depth searches, not all-word obstructions.

The raw source-consuming inverse F/B/F word is expanded and independently
tested in `mutable_rolling_boundary.py`:

```
R3 = [[I+a1*C0, N*C1],
      [N*(C2+C2*a1*C0+C0), I+a2*C1]],   a_i=N*C_i*N.
```

Exact neighboring cancellation a_(i+1)*C_i=I is incompatible with the
unchanged fresh stage family: C_i commutes G_(i+1), and C_(i+1) commutes
F_(i+1)=N*G_(i+1); substitution forces C_i to commute N, contrary to the
actual coefficient witness. This excludes that exact cancellation only.

After factoring off parent FULL, the bank0 diagonal is
Phi=N+C1*N*C0. The actual ADDRESS F101 input delta at source port0,
HEAD=e0,TAIL0 produces3131 nonzero output deltas, including port0,
HEAD0,TAIL=e0. All111 Weyl-BFS rho hashes match the fresh C511 receipt.
These15 coordinates embed in parent width22 with the last fresh7 zero.
Free head/tail-separate codes preserve the subspace of impulses with TAIL0,
so a terminal invertible code in that alphabet cannot close the raw word.
Its arithmetic deficit213 is only a failed-candidate diagnostic.

`mutable_rolling_quotient.py` fixes HEAD=e_j,TAIL0 for each j=0..7 and lets
all111 source-port VALUE coefficients vary. Every actual output impulse
with nonzero TAIL gives a binary coefficient row. Their exact rank is111;
the receipt stores111 independent row witnesses and a digest of all rows.
The control C0=C1=I cancels Phi=N+N on all111*8 sampled impulses.

For Phi=H_free+sum_i A_i*(c_i^T tensor I_ADDRESS), each projected row lies
in span{c_i}: H_free emits no nonzero TAIL from these inputs, and the i-th
response depends on source coefficients only through c_i. Thus at least111
ADDRESS-independent common scalar source readouts are necessary. This
excludes a common rank9 scalar quotient repair of this actual raw word.
It gives no native tariff, and permits routed/ADDRESS-dependent readers,
direct source access, extra native source queries and changed coupled words.

No chronological owner, all-size source/tape bound, rounded error theorem
or outer exponent is supplied by these interfaces or screens.
