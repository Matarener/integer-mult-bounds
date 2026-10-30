# Exact finite changes to scalar coefficients

## 1. A formula with chronological feedback

Consider a finite linear program over a field. Designate ADD gates in their
chronological order, numbered 1 through k. Gate i adds `q_i` times its source
to its destination. All other operations remain fixed. These operations can
include linear initialization, copy and erasure maps. Invertibility of the
whole program is not required.

Let `R_i` be the source row just before gate i in the original program. Let
`C_i` be the column that carries a unit change at that gate's destination to
the observed final outputs. Suppose

```text
C_i = c_i C,                 c_i != 0.
```

Let `m_ij`, for j < i, be the change at source i caused by a unit change at
destination j, propagated through the original operations between those gates.
These numbers include the effects of COPY and CLEAR. Let `delta_i` be the
change to coefficient i. The changed source rows satisfy

```text
R'_i = R_i + sum_(j<i) m_ij delta_j R'_j.                 (1)
```

To prove (1), subtract the original state from the changed state. Propagate
each earlier injected row through the fixed original operations. At gate j,
the extra injection is `delta_j R'_j`; the original coefficient acts on the
state difference as part of the original propagation.

The complete endpoint difference is therefore

```text
Delta T = C sum_i c_i delta_i R'_i.
```

Eliminate `R'_i` backwards with (1). If the resulting weights on the original
rows are `b_j`, they satisfy

```text
b_j = delta_j [c_j + sum_(i>j) b_i m_ij].                 (2)
```

Thus a relation `sum_i b_i R_i = 0` gives an exact endpoint-preserving edit when
all denominators below are nonzero:

```text
delta_j = b_j / [c_j + sum_(i>j) b_i m_ij].              (3)
```

This is an exact finite identity. It is not a first-order approximation.
A zero denominator is a failed construction under this formula. It cannot be
ignored because the derivative columns are dependent.

To remove gate r, start with a row relation `sum_i v_i R_i = 0` and set
`b_i = s v_i`. The requirement `delta_r = -q_r` gives

```text
s = -q_r c_r / [v_r + q_r sum_(i>r) v_i m_ir].           (4)
```

Check (4), then every denominator in (3), and then the required coefficient
ring. This package retains only dyadic coefficients. The analogous argument
can be applied to the transposed linear program. Transposition here is an
algebraic check, not permission to reverse an owned physical lifetime.

These are elementary linear propagation identities. No claim of a new general
linear-algebra theorem is made. The source application and its exact edited
word are the contributions in this package.

## 2. A nonzero-feedback control

Take two independent scalar inputs x and z and observe only the final z. Apply

```text
z += x;    x += 2z;    z += x.
```

The observed result is `4x + 3z`. Formula (3), with
`b=(-3,-6,3)`, `c=(3,1,1)` and
`m_21=1, m_31=2, m_32=1`, gives new coefficients `(0,1/2,4)`.
They give the same result. Setting `delta_j=b_j/c_j` omits the feedback term
and gives a different result. The verifier checks both statements exactly.
This fixture has one observed output; it is not a claim about both output rows.

## 3. The P104 construction

The source is the complete PR6144 word at the head in SOURCES.json.
CERTIFICATE.json has three passes. Each pass gives the exact old ADD record,
its new coefficient, and the required input and output hashes. After the
coefficient edits, zero ADDs are removed. One unread owned lifetime is then
removed. Its INIT, COPY and CLEAR are explicitly listed. No native MOVE is
removed from that lifetime or from the rest of the word.

One first-pass example removes original zero-based events 14603, 17482, 17483,
17484 and 18890. They update register 736. Their source rows obey

```text
R_14603 - R_18890 + R_17482 + R_17483 - R_17484/2 = 0.
```

The original coefficients are `-1/8, -1/8, -1/8, 1/16, 1/8`, in the event
order listed above. Their final response columns agree. The exact replay
checks this edit as part of the complete constructed word; it does not assume
that values of registers 5, 67, 80 or 100 stay constant between these events.

The discovery code used (3) and the transposed case to propose edits. The
published checker does not trust those proposals or their modular search.
It reconstructs the final word from the guarded certificate and checks the
full rational operator by two traversal directions. All 799 columns are
present. The 29 owned input columns are killed by their legal initializations;
none is silently treated as a public zero input. All 770 public inputs remain
independent.

## 4. Native interpretation and invoice equality

Use the predecessor's invariant: at frame W, a register with logical row a
has physical value `Gamma_W a z`. A scalar operation requires equal frames.
It therefore changes the logical row by the stated scalar operation. Every
native MOVE in the new word is the identical original operator at the same
field and between the same two frames. The checker verifies the full ordered
MOVE list, every scalar contact, strict native inclusion, each zero COPY
destination and each owned lifetime. The predecessor's native identities then
give the physical endpoint by induction. This implication inherits those
identities; it is not a new independent phase replay.

The final logical matrix is the required supplier matrix: each live target
gets its own input plus the corresponding source input; sources and public
helpers retain their own independent logical input. Every final frame agrees.
The separate transpose verifies this matrix again.

All paid native ranks and productive helper ranks are consequently unchanged.
The main boundary contract is unchanged. Substitution into the same caller
leaves its complete recursive paid and target histograms unchanged, including
its thin queries and idles. There is no strict signed-moment gain and no new
kappa. The reduction concerns ordinary finite operations only. A new complete
precision or runtime bound is outside this certificate.
