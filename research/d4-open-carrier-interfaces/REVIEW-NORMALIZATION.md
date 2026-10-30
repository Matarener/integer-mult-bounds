# Cross-review of the four C-port normalization package

**PASS within the stated local boundary.** This is a mathematical and source
review of the companion package, not a second execution of its complete
finite interpreter.

Reviewed immutable payloads:

| File in `carrier-normalizer/` | SHA256 |
|---|---|
| `check.py` | `5793faa7808220de3a84b5c9b6baaf1a9cbc224ee9de65de319c2d904316cf70` |
| `PROOF-NORMALIZATION.md` | `250142e505d462b3ca23e724c197a9da8d2a3c6d7339ce92e3c76323a67321a5` |
| `CHECKS.json` | `61f0e8c55c015a15ccfcd37a2086c17cb8e0735f28bea48cba789ea6151f8634` |
| `SOURCE-INVENTORY.json` | `56cfb693464e643fadd726691ba91d48b9d25eda71c5d69bb7c8c196717947cd` |

The companion uses the same full-phase gauge `F=X_33 F_7`, corrected
radical Walsh D, and C-port source channel `S=V_C C_p^-1` as the actual
OPEN word. The source/target diagonal `T=F C_p^-1 C_q^-1` and cross
`J=F X_p` also agree. Its four ports are exactly the C ports of the
fixed carrier geometry; there is no unnoticed transfer from a plain-F7
gauge or another block.

The split-Lagrangian argument has the correct directions. With
`L(U)=U^-1 Z`, the rank hypotheses give the dimensions of
`L(U) intersect Z` and `L(U) intersect F^-1 Z`. Their sum is n and the
two ambient Lagrangians are transverse, so L(U) is their direct sum.
Choosing B to map `L(T) intersect Z` to `L(S) intersect Z` and
`G=B^-T` gives the claimed monomial symplectic P. Its pairing-dual
action maps the other summand as required. Consequently
`post=T P^-1 S^-1` preserves Z. The lift
`P=Diag(I+G^-T G^-1) Perm(G)` gives lower-left block `G+G^-T`;
the proof fixes an actual phase representative before using exact
products. This establishes the stated all-dimension existence lemma,
while the rank-zero inverse-wrapper property remains a separate finite
fact about four witnesses.

The physical/logical distinction is correct. Since
`K=T^-1 J P=C_q C_p^-1 P`, stripping the actual source entrance C_p
and target frame C_q gives
`A=C_p^-1 P C_p`, and `H=A^-1`. Physical pre-X H is P^-1.
Physical post-Y H at `F C_p^-1` is
`F X_p P^-1 X_p F^-1`, equivalently the stated conjugated monomial.
The pre-X/post-Y identities hold for both logical orientations by direct
block multiplication. They do not require A to be an involution or
different stage codes to commute.

The backward wrapper has the right noncommutative order. For the
bank-swapped inverse
`R=[[T^-1,-K T^-1],[0,T^-1]]`, take
`AB=T K^-1 T^-1 K^-1` and `BB=T AB^-1 T^-1`. Then

```
T² K T^-1 AB = T K^-1,
BB T AB = T.
```

Thus `diag(I,BB) diag(T²,T²) R diag(I,AB)` is exactly
`[[T,-T K^-1],[0,T]]`. Both T² translations, AB and BB are required.
The code computes these ordered products independently and verifies
their actual phases. This wrapper is distinct from the whole-word
inverse-transpose dual audited by the carrier checker.

The fresh checker authenticates and executes the captured compiler
bytes, retains producer assertions under outer `-O`, reconstructs the
four supplied witness matrices without rerunning their search, and
compares every lowered monomial with its native history and frozen
recipe. Its separate sparse Gaussian interpreter checks every address
basis column of eight monomials at each port, matching the reported
4096 columns. The all-f statement is justified by tensoring exact
operator products, not by preserving a bounded expansion support.

The in-place permutation recipe has the correct push convention:
swapping a cycle's first location successively with its later locations
sends each old value to its successor. Its `N-c` swaps and their
three-ADD/one-NEG implementations are paid. Phase work, binary cycle
discovery and counters remain charged or explicitly bounded; no spare
complex array or physical tape implementation is silently assumed.
The four forward and eight inverse wrapper-map counts are unfused
local upper bounds and are not a total carrier bill.

The controls invoke actual production phase/equality or rank predicates,
with exact intended error matching and unexpected acceptance outside the
catch. The global-i defect keeps the signed Pauli data unchanged and
is accepted when the phase comparison is actually deleted. The native
carrier package separately exercises mutations in its complete scalar
and native word; this review does not substitute the normalizer's
boundary controls for that obligation.

No corrective mathematical change is requested. Preserve the explicit
limits on accumulated caller frames, ordered terminal codes, native
precision, source access, helper ownership and physical movement when
integrating the two packages.
