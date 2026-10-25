# Alternating row-section codes cannot close the common endpoint

This is an all-parameter written matrix proof, with the actual R438 premise
checked from frozen matrices. It is not a lower bound on paid decoding or on
changed controllers. The ratio argument was proposed by the root lane and
checked here. Prepared with substantial OpenAI Codex assistance.

Let J be n-by-n over a field. Let A_0,...,A_(2k) be invertible, with A_s
agreeing with J outside physical row set P_s. Define

```
E=A_(2k) A_(2k-1)^-1 ... A_2 A_1^-1 A_0,
P=union_s P_s.
```

Then E agrees with J in every row outside P. For i=1,...,k,

```
A_(2i) A_(2i-1)^-1
  = I + (A_(2i)-A_(2i-1)) A_(2i-1)^-1.
```

The second term has nonzero rows only in P_(2i) union P_(2i-1). A product
of matrices each agreeing with I outside its row set agrees with I outside
the union: each other coordinate row is unchanged by left multiplication.
Grouping E into k ratios followed by A_0 proves E_row_p=J_row_p outside P.

The actual R438 binary J=I+KR has all111 diagonal entries zero. Its retained
recipe is exactly F0,B1,F2,B3,F4,B5,F6,B7,F8. Thus the common code augmentation
is (A8 A7^-1)(A6 A5^-1)(A4 A3^-1)(A2 A1^-1)A0. Any three-row repair
J=(I+Q_s)A_s with Q_s supported on P_s has A_s=J outside P_s. At most27
rows are selected, leaving at least84 rows p where E_pp=J_pp=0 rather than1.
No RW=0, involution, fixed section, or quotient-order premise is needed.

An explicit binary witness is a VALUE function constantly1 on one uncovered
physical family p and constantly0 on every other family of one bank.
ADDRESS permutations act trivially on constant functions, so this is an
actual source specialization. Its p output coefficient is0 instead of1.
This is a diagonal-entry witness, not a rank-at-least84 claim.

The theorem concerns the alternating common-E schedule and terminal identity
target. Paid terminal decoding, changed final codes/controllers, row repairs
whose union covers every physical row, and changed recursive observer
contracts remain outside it. Finite quotient order may still improve growth.
