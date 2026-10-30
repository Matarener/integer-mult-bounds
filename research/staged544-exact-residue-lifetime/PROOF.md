# Exact residue arithmetic through the actual helper277 lifetime

Chris R / Clear1nsight, substantial OpenAI Codex assistance. Apache-2.0.
This changes the numerical representation contract. It does not replace or
admit the selected supplier, improve kappa, or establish a recursive tariff.

## 1. The source boundary and correction to PR4017

The source is both PR3945 words at91f81d131252db704f945891da1ea54e29d46b8b.
Their helper277 has empty entrance,49 touching scalar instructions, no native
warp, and terminal U=[388,74,40,26,1]. The literal instructions are recorded
with zero-based addresses in RESULT.json. There are43 additions and6 negative
scales. The last two are B[529]:277-=281, B[530]:277*=-1.

The actual paid frame chronology has FIVE rank-one climbs, at A[2340],A[2381],
A[2391],A[2409],end; the frame dimensions are0,1,2,3,4,5. CLIMBS.json retains
all five phase-bearing L C_[1] R recipes, generated using the credited frozen
compiler and checked on all512 Gaussian basis columns each. They are distinct
from the single completed rank-five residual T_U=L C_[5] R. The latter is also
checked on all512 columns against the source canonical frame.

PR4017 PROOF.md's phrase "The source's charged object is a rank-five recursive
child" conflated this residual/owner width with the chronological calls. The
correct paid chronology is five rank-one climbs. Its finite macro construction,
gate counts, error theorem and generic nonadditivity witness remain valid.
That witness alone is not an actual whole-lifetime failure certificate.
The old published head and frozen sources are preserved; CORRECTION.md records
the explicit clarification.

The source's canonical logical program restores helper277 BEFORE inverse
cleanup. The cleanup operates on buffer981=704+277 instead, with49 touching
instructions,43 additions and6 scales, at the FULL frame. The frozen credited
independent auditor checks all arbitrary-input symbolic rows in both primal
and dual orientations, plus the boundary and exact inverse-cleanup derivation.
In particular, row277 is its initial symbol at the boundary and endpoint,
row981 is its initial symbol at endpoint, and no private buffer leaks to a live
register. The original zero-buffer numerical domain is included; the symbolic
buffer identity additionally holds for arbitrary dirty buffer symbols. These
are exact source algebra checks, not an assumption that the generic h+s example
occurs at a particular source address.

## 2. Change the arithmetic contract to an odd ring

Fix b>=2 and M=2^b-1. Store each real component as a canonical residue0,...,M-1;
a complex coordinate belongs to R_M=(Z/MZ)[i]. This ring need not be a field.
Its element2 is a unit, and i is a unit. Consequently all dyadic source scalars,
all monomial phases, and C=((1+i)I+(1-i)X)/2 have exact ring meanings. C is
invertible with inverse obtained by replacing i by-i.

Reduction Z[i,1/2] -> R_M is a ring homomorphism. Every coefficient identity
in the audited free-operator program therefore survives reduction, including
all intervening additions, private-buffer recovery and the physical frame
relations. The native warps are monomial maps with coefficients±1,±i; they also
reduce exactly. Same-frame scalar operations commute with the exact linear
frame maps over this ring. Physical register277 at its terminal is T_U times
its unchanged logical input. Other provider operations remain inherited;
this statement does not synthesize or price the entire provider.

The specific PR4017 witness now obeys Q_M(2e0)=2Q_M(e0) moduloM. In fact
Q_M(h+s)=Q_M(h)+Q_M(s) for all ring inputs, by linearity of every factor. No
rounding-error record or saved input copy is required. This is an algebraic
repair of the missing additivity premise under a changed representation, not
a claim that the original fixed-grid rounded implementation was linear.

## 3. Total finite reversible implementation, including unused bit codes

There are2^b bit strings but onlyM canonical residues. CodeM (all ones) is
reserved. Define addition with source x and target y as

    if y=M: y stays M;
    otherwise: y <- (y+x) mod M.

SourceM therefore acts as zero and every source is preserved. For each fixed
source this is a permutation of all target bit strings. This total extension
is meaningful as a Boolean circuit, but the ring identities and numerical
contract apply to canonical residues. Arbitrary dirty canonical residues cover
every ring element; arbitrary b-bit strings are a larger domain. We do not
claim source cleanup identities on mixed invalid-code states. Every complete
circuit and its reversed gate list are nevertheless inverses on ALL bit states.

An explicit controlled increment moduloM is ordinary controlled increment
modulo2^b, followed by a controlled transposition of target codes0 andM. The
latter fixes the ordinary overflow error, leaving codeM fixed. Realize the
transposition along the Gray path0,1,3,...,M, then return along all but the last
edge. Each edge is one generalized controlled-X. There are b ordinary increment
gates plus2b-1 transposition gates; the largest has b controls.

Multiplication by2^j moduloM is cyclic bit rotation and fixes codeM. Conjugate
the controlled increment by this rotation to add the j-th source bit with
weight2^j. Telescoping rotations between consecutive source bits gives b
controlled increments and b one-bit right rotations. Each rotation takes b-1
bit swaps, each three CNOTs. Thus the adder has3b^2-b generalized increment/
transposition gates, plus3b(b-1) CNOTs. Connectivity may read a rotated source
without physically moving it; no geometric-locality assumption is made.

Positive controls use exactly the PR4017 reconstruction of Barenco et al.,
Lemma7.2, with4n-8 Toffoli gates for n>=3 controls. The n-2 temporary borrowed
bits are selected outside the current controls and target and restored. Here
n<=b and a two-word adder has2b existing bits, leaving at leastb-1 available,
which is sufficient. Negative controls are conjugated by X. No extra clean or
dirty workspace is allocated. The same reasoning applies inside the four-word
C pair and to phase negations using other existing coordinate bits.

Modular negation is bitwise complement followed by the transposition0<->M;
it fixes both canonical zero and unused codeM. A quarterturn is a real-word
swap and one such negation. Modular half is the read-only cyclic right shift.
The exact C lifting is

    x -= y;
    y.real += half(x.real) + half(x.imag);
    y.imag += half(x.imag) - half(x.real);
    x *= i;
    x += y.

It uses8 modular real additions and one quarterturn, with no rounding. Its
literal reversed circuit is its total inverse; on canonical states this is C^-1.
The verifier checks all small adder bit states, including codeM, complete pair
permutations/inverses, and literal borrowed-bit decompositions. The argument
above supplies arbitrary-b correctness beyond those finite tests.

## 4. Numerical recovery and its real price

A residue alone is not a fixed-grid approximation. For example atM=255,
half(1)=128, whose centered representative is-127, not numerical1/2.
We reject that interpretation explicitly.

Suppose input real components are integers z with |z|<=A, representing Delta*z.
The exact helper residual has denominator dividing32. Since each C layer has
real-component sup norm at most2 and monomials only permute/sign/quarterturn,
the completed output has real-component magnitude at most32A. Its integer
numerator at common denominator32 has magnitude at most1024A. Therefore

    M > 2048A

suffices to recover every output numerator uniquely: multiply the output residue
by32 moduloM, take its centered representative n, and interpret Delta*n/32.
For A<=2^p, b=p+12 is sufficient. This is exact numerical output on the finer
grid Delta/32. Returning it to the old gridDelta would require a separately
paid rounding/recovery mechanism; it is not included or silently discarded.

The output decoder is itself reversible. Multiplication by32 is a cyclic bit
rotation. Converting the canonical residue to its centered two's-complement
numerator increments the lower b-1 bits conditioned on the high bit. This
fixes positive residues and maps negative residues to r-M. The unused codeM
is mapped to the otherwise-unused most-negative two's-complement code; reversing
the circuit recovers it. No record is erased. The exponent5 is public fixed
metadata, not per-input garbage. Decode costs and data width are in LEDGER.json.
The decoder runs inside the existing1024-real-word physical register. Its largest
controlled gates borrow spectator bits from another existing coordinate word,
restoring them after each gate; a truly isolated b-bit word would not supply
that workspace. No additional coordinate word is allocated.

Intermediate modular wraps are exact. Endpoint reconstruction does not require
recovering intermediate rational numerators, because the complete algebraic
identities hold moduloM before decoding. For logical inputs on a common integer grid, users who require decoding every
completed physical cut can use a conservative positive-path bound from EVERY
literal source instruction: logical denominator exponent44 and real-component
amplification B=202390250292243154284173890571/512 in both providers. Adding a
physical frame of rank at most9 gives exponentD=53 and amplification512B.
The sufficient all-cut modulus is M>2^(D+10)BA. This is a positive-path upper
bound for logical input coordinates, not a minimal modulus or an observed worst
input. Physical caller inputs with nonempty entrance frames require their own
entry-adapter denominator/amplitude conversion, which is not supplied here. It is much more costly
than endpoint-only recovery. Endpoint-only recovery is the chosen contract.

## 5. Complete scoped invoice and stopping decision

Every bill is per512-coordinate spectator lane; multiply by f lanes. Data
storage is1024bf bits per physical register. Workspace and saved recovery
records are zero beyond those data words. Initializing a valid canonical input
and external input quantization are caller obligations; codeM is not silently
accepted as a numerical value. The source private zero buffers are inherited
resources, not removed by this construction.

The actual five rank-one climbs contain1280 C pairs in total, plus ten
phase-bearing monomial wrappers. At b=32 they cost3,128,231,936 Toffoli,
661,471,232 X, and32,076,800 CNOT gates. The49 helper touches and49 buffer
cleanup touches contain86 complex-vector additions and12 negative scales,
four of which also rotate by one bit. Their explicit implementation adds
26,638,630,912 Toffoli,5,615,779,840 X and265,277,440 CNOT gates. Total for this
scoped lifetime invoice is29,766,862,848 Toffoli,6,277,251,072 X and297,354,240
CNOT, before the optional final numerical decoder. These gates serialize safely;
five abstract layers are not five clock steps. Neighboring provider operations,
all other helper lifetimes, input/output transport and global owner scheduling
are additional inherited costs, not zero.

For comparison ONLY at the same b, the isolated completed residue macro uses
3,103,910,912 Toffoli versus PR4017's442,109,184 rounded-macro Toffoli. These are
different numerical contracts, and numerical precision generally requires a
different b. The comparison is not a speed improvement or full-provider
benchmark. Removing a rounding record does not make this circuit affordable.

The actual caller supplies five rank-one recursive charges and a rank-five
terminal/owner width, not an authenticated scalar-gate allowance. No source
conversion of that allowance into this finite bit tariff is available here.
The numerical consumer's acceptance of Delta/32, recursive denominator growth,
all-size tensor multiplicity, source-valid input encoding, global stock/tape and
full owner ledger remain unresolved. We stop further implementation expansion:
exact linear finite arithmetic and complete helper lifecycle algebra are now
provided; recursive numerical adoption remains unproved. No universal barrier
or selected-frontier claim follows from this scoped cost stop.
