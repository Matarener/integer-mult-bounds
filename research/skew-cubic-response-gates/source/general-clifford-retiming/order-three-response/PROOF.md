# Whole-field cubic quadratic-response gate

No complete caller or positive cost proposal is claimed here. The pilot tested whether an exact cubic one-qubit Gaussian response could replace skew J while retaining the two-reader inverse identity on every whole field. It fails that premise. A three-power caller remains open and requires a separately constructed complete word, target, all-input cleanup and bill.

The parent's suggested matrix is

J = [[-1+i, 1+i],[-1+i,-1-i]] / 2.

With C=((1+i)I+(1-i)X)/2 and S=diag(1,i), the actual identity is J=i C S C S^-1, including its Gaussian phase. J has trace -1, determinant 1, J^3=I and J^2+J+I=0; its Clifford native B rank is 1. The exact producer verifies every matrix entry of this primitive circuit.

For the scaled family U_f=J^tensor f, every member is a Gaussian Clifford with U_f^3=I and native B rank f. The factor i in the base circuit appears once per tensor coordinate, giving i^f in the actual family. At f=2, the quadratic relation already fails. In fact I,U_2,U_2^2 are linearly independent, so no scalar-reader formula U_2^-1=alpha I+beta U_2 exists, even over C. The serialized exact 4-by-4 residual U_2^2+U_2+I is nonzero. Its trace is 6 (each U_2 power has trace 1, while I has trace 4). Thus the one-qubit inverse identity cannot be extrapolated to arbitrary fields. The tensor family has all three order-three eigenvalues at f>=2. Retaining three powers or paying for another query is a different interface, and no lower bound against that interface is asserted.

There is a general gate against repairing the same quadratic premise while retaining unbounded native width. Let U be an actual unitary Clifford on M qubits, with matrix entries in Q(i), satisfying U^2+U+I=0 on its entire bank. Let d=2^M. The only eigenvalues are omega and omega^2, with multiplicities p and d-p. Therefore

Tr(U) = -d/2 + (2p-d) i sqrt(3)/2.

Since this trace lies in Q(i), irrationality of sqrt(3) forces 2p=d and Tr(U)=-d/2. In particular its squared modulus is 2^(2M-2), which is nonzero.

Let S_U be the binary symplectic action on Pauli labels, and K=ker(S_U-I), of dimension e. Use Hermitian Pauli representatives P_v. Clifford conjugation permutes these with signs. On a fixed label v in K, U P_v U^-1=epsilon(v) P_v, where epsilon(v) is +/-1. Multiplying two Pauli representatives and comparing both sides cancels the same Pauli multiplication phase, so epsilon(v+w)=epsilon(v)epsilon(w) on K. Thus epsilon is a character of the additive binary space K. Its sum is either zero (nontrivial character) or 2^e (trivial character).

The trace of conjugation Ad_U is this fixed-label signed sum. Independently, vectorization gives Tr(Ad_U)=Tr(U) conjugate(Tr(U))=|Tr(U)|^2. The latter is nonzero and equals 2^(2M-2). Hence e=2M-2 and rank(S_U-I)=2. The physical native B block is a submatrix of S_U-I, because the identity has zero off-diagonal block. Consequently

native_rank(U) <= 2.

This proof does not assume a support restriction, tensor structure or Pauli-sign cancellation without checking it. It applies to any Gaussian-rational Clifford satisfying the full quadratic identity on every input. Therefore a response family with native rank r f for fixed r>0 cannot satisfy that quadratic for all f. It does not rule out order-three responses with a full three-dimensional power span, non-Clifford responses, restricted-input quotients or complete words that use more stored information.

Exact receipts check f=1,2,3,4: order three always holds, native ranks are 1,2,3,4, symplectic defects are 2,4,6,8, traces are -1,1,-1,1, and the power spans have dimensions 2,3,3,3. Every tested Ad trace equals the independently enumerated fixed-Pauli character sum. Normal and -O receipts are identical. The all-M trace argument above is written mathematics, not a finite computation or formal-kernel certificate.

Source pins and literal circuits are retained. No q=2 complete cubic caller was constructed after the scaling gate failed; therefore no endpoint, native/owner bill, physical controller, borrowed-axis normalization, inverse cleanup, precision or recursive transfer is certified for a cubic caller. BIT and all frozen earlier packages remain untouched. There is no kappa claim.

Reproduce with python3.12 -B cubic_gate.py, then python3.12 -B -O cubic_gate.py.
