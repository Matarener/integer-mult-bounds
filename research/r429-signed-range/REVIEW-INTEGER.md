# Independent mathematical review of B04

**Disposition: pass for a narrow fixed-witness audit and the stated
all-sign-family transfer theorem.** No precision, native-vector, supplier or
kappa admission is established.

The reviewed word is the unchanged historical
`BIT-SIGNED-QUOTIENT-WORD.json.gz`, SHA256
`e802611104c61fc8477837b4ab41abc4f13cf41fbca6ef3de60d0b5e768fb949`.
Its immediate parent is the exact word published by PR3645 at
`99b901c9b5ac70cf441b3d7e585cc7b8744b5359`, SHA256
`1a6841fccba51fa922993c77b4b296e659c2c538252e5e06113d0438c5edb870`.
Their 23 changed coefficients are all phase-23 \(+1\)-to-\(-1\) changes.
All other records, metadata apart from the format name, and boundary arrays
are identical.

The candidate's historical `parent_word_gzip_sha256` field still names the
support-code ancestor `6e4e79c3...`; it was inherited unchanged. The immediate
sign-variant parent is authenticated separately, as above.

## Independent method and results

[check_integer.py](frozen/reviews/integer/check_integer.py) is a fresh
standard-library implementation using dense integer coefficient rows and a
parallel F2 bit-row interpreter. It does not import or execute the original
producer, optimizer, sparse integer replayer or native checker. Those sources
and the exact PR3645 proof were read to establish the intended contract.

The checker authenticates all four explicit inputs, derives R and K directly
from the original R438 D/A/scatter data, derives \(A=I+WR\), and checks its
two-sided binary inverse. It rederives rational frame ranks using exact integer
elimination and checks actual entrance-line/target-cap bindings.

The full replay establishes:

- Every one of the 651 arbitrary public input columns in both rings and both
  orientations; 429 literal integer helper restorations and identity target
  self blocks; closed private snapshots.
- Both forward-then-inverse and inverse-then-forward integer roundtrips for
  both parent and signed words.
- The complete profile with rank mass 4,989, including all 2,873 MOVEs and
  all three rank-one COPY children; unchanged costs and frame paths.
- Exact scalar prefix maxima 80,639 / 239,014 for the candidate versus
  34,285 / 5,839,860 for the parent, each with a concrete attaining input.
- The actual integer endpoint, with nonzero even helper leakage. In
  particular \(A_{\mathbb Z}[0,0]=-23\), \(T_{\mathbb Z}[0,0]=-125\), and
  \(E_{\mathbb Z}[0,4]=2\); the integer target is not \(y+A_{\mathbb Z}x\).

The useful expansion is a finite prefix/suffix transfer certificate and its
written proof. For every assignment of the 47 existing quotient signs,

\[
 \Delta A_{\mathbb Z}=U\Delta QB,\quad
 \Delta T_{\mathbb Z}=P_3L\Delta QB,\quad
 \Delta E_{\mathbb Z}=0,
\]

with \(BU=I_9\), and \(L\) a displayed rank-three 3-by-9 matrix. Thus source
changes are confined to the nine pivots, target changes to rows 0,1,2, dirty
leakage is unchanged, and helpers remain literally restored. The ranks are
at most 9 and 3 throughout the family. For this particular pair,
\(\det(\Delta Q)=1024\), giving exact ranks 9 and 3.
[PROOF-INTEGER.md](PROOF-INTEGER.md) proves the distinction between those
universal bounds and the current pair's exact ranks.

## Controls that reach mathematical failure gates

All mutations are applied to in-memory records after valid inputs have passed
authentication. Four exception controls require their exact intended error;
an unrelated exception or ineffective control fails the audit.

| Mutation | Mathematical detection |
|---|---|
| Stale private COPY value | ERASE differs from original unchanged snapshot |
| Mutate physical copied source | Immutable-source lifetime violation |
| Write to the private snapshot | Immutable-private destination violation |
| Wrong MOVE rank | Exact frame-containment/rank violation |
| Wrong inverse ADD sign | F2 roundtrip stays identity; integer roundtrip has coefficient \(-58\) at row 0, column 59 |
| Flip one quotient sign | F2 endpoint stays fixed; integer source changes at row 0, column 59 |
| Wrong helper-cleanup sign | F2 stays fixed; helper 222 gains \(2x_0\) |
| Source code reads dirty helper 222 | Source 0 acquires coefficient 1 of that arbitrary helper |
| Omit one compensation term | Target 111 has odd coefficient 1 of dirty input 226 |

The complete deterministic receipt is
[CHECKS.json.gz](frozen/reviews/integer/CHECKS.json.gz).
Source hashes and inherited obligations are in
[SOURCE-DEPENDENCIES.json](frozen/reviews/integer/SOURCE-DEPENDENCIES.json).
Actual local command and portability evidence are in
[VALIDATION.md](frozen/reviews/integer/VALIDATION.md).

## Covered domain and remaining obligations

The fixed integer identities cover every integer input and, by coefficient
identities, every module over a commutative ring, with the private register
initially zero. The F2 endpoint is stated only modulo two. The exact induced
infinity norms cover the scalar lift on real inputs.

The family theorem covers all \(2^{47}\) sign assignments in the existing
ordered quotient alphabet. It does not establish a sign optimum, common
prefix bound for the whole family, or equal costs for arbitrary coefficient
or arbitrary matrix substitutions.

The original native ADDRESS/copied-total interface and full parent
construction ancestry are inherited under their precise PR3645 assumptions.
The current audit does not rerun the parent's complete reconstruction.
Its scalar prefix bounds do not admit a native vector implementation or
charged precision theorem. Global decoder, source access, dirty ownership,
storage, tape, recursive caller and complex/BIT assembly obligations remain
open. This is independent AI-assisted mathematical work, not human review or
formal-kernel verification.
