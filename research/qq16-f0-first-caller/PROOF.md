# Admission lattice of the first F0 Gaussian child

Chris R / Clear1nsight, with substantial OpenAI assistance. Apache-2.0.
An ordinary mathematical argument with finite source checks; no formal-kernel
verification or global QQ16 impossibility claim.

## 1. Literal caller and domain

Fix canonical base `20ecf2891d80b5acf18d980b2164fb44ea7faa90`. The pinned
joint-query contract allows arbitrary ordinary helper payloads. The first
rank-positive F0 child is zero-based event 9894:

```text
['climb','A',546,0,4,1]
```

Its exact prefix and recipe hashes are in RESULT.json. The source frame table
gives frame 0 as I and frame 4 as `[459]`. Before this event, L546 is only read
by eight ADDs, at indices 262,335,408,482,555,628,701,774. No scalar instruction
writes it. Its adapter at index 7948 is `old_to_new` on an ordinary helper in
frame I; the pinned native evaluator applies endpoint monomials only to data
ports, so this helper's value remains unchanged. The executable additionally
replays the entire actual prefix for the witness, rather than assuming that
unrelated fields remain zero after reading L546.

We use a 512-coordinate nine-axis native slice at lambda=1. The inherited
native embedding has identity spectators; setting every other spectator slice
to zero embeds this witness in the full payload. The full producer extent is
N=2^(73*lambda), not 512 in general. No full payload is allocated here.

## 2. Exact divisibility domain

On a chosen dyadic grid write components as `2^-q r[x]`, `2^-q i[x]` with
integer mantissas. The recipe's right monomial is a coordinate permutation
with quarter-turn phases. On real component variables it is a signed
permutation, hence preserves the integer grid and lattice indices.

For a pair after that monomial, put `(a,b,c,d)=(r[x],i[x],r[x xor 1],i[x xor 1])`.
The pinned positive-axis formula has the four numerators

```text
a-b+c+d,  b+a+d-c,  c-d+a+b,  d+c+b-a.
```

Modulo two, all four equal `a+b+c+d`. Same-grid exact division by two is
therefore possible exactly when that sum is even. This is one independent
index-two constraint on each disjoint block of four variables. The 256 pairs
on this slice give an index-2^256 sublattice of Z^1024, also after pullback
through the right monomial. Signed numerator range is a separate condition.
Nothing in the arbitrary-helper source contract imposes this sublattice.

## 3. Reachable counterexample

Set every initial field zero except `Re L546[0]=1`, in frame I, with grid q=0.
Section 1 establishes its reachability. The right monomial fixes address 0
with phase 0. Thus the first pair is `(1,0,0,0)` with numerators `(1,1,1,-1)`.
They fit all signed widths W>=2, but are odd. The axis returns `(1+i)/2` at
0 and `(1-i)/2` at 1. The actual left monomial fixes address 0 with phase 0
and sends address 1 to 459 with phase 3, giving the complete child outputs

```text
address   0: (1+i)/2
address 459: (-1-i)/2.
```

Neither belongs to the original integer grid. Scaling by 2^-q gives the same
relative obstruction on any original dyadic grid. Increasing W does not
change parity. This is outside the tape kernel's explicit contract, and its
`nonexact half` rejection occurs after scratch packing; no atomic precheck
is claimed. It is not a defect of that conditional kernel.

## 4. Conditional sharp repair and range

Store the same physical input on grid q+1, using doubled mantissas. Every
numerator is even for every integer input. There is one axis factor in this
rank-one native recipe at lambda=1, and the left monomial is a signed
permutation, so the entire child is exact on the finer grid. The witness proves
that zero additional fractional bits do not suffice for all inputs; this
construction proves that one suffices for the child's arithmetic.

If each original component has magnitude at most integer M>=1, the refined
input components have magnitude at most 2M and each numerator at most 8M.
For `b=bit_length(M)`, `M<2^b`; with W=b+4,

```text
|numerator| <= 8M < 2^(b+3) = 2^(W-1).
```

Thus every numerator lies in signed W-bit range. This is a conditional
sufficient width; it does not bound arbitrary unbounded dirty inputs.
Evenness alone is insufficient: refined pair `(2,-2,2,2)` has numerator +8.
W=4 violates range and the program returns -4 instead of +4; W=5 works.
The inverse right monomial pulls that pair back to a valid original helper
with components in {-1,0,1}, so this is relevant to the actual recipe.

## 5. Existing PR3303 grid is a genuine escape

The existing all-depth format proposes quantum `h*2^-G`,
`G=71+19*(lambda-1)`, and signed width `W=P+215+38*(lambda-1)`, for input
components in h Z of magnitude strictly below `2^P h`. It does not admit the
physical caller's entry protocol. At lambda=1, L546 is unchanged, so its stored
entry mantissas are multiples of 2^71. The right monomial preserves this.
Every numerator is even and has magnitude strictly below `2^(P+73)`, far below
the signed threshold `2^(P+214)`. The first axis therefore meets the arithmetic
premises on that proposed format, conditional on its original input bound.

This implication uses only the identified untouched helper and those stated
format parameters. It does not independently replay the whole PR3303 theorem.
The half-integral witness is not a counterexample to that already finer grid.
A caller preallocated on such a grid can avoid a local re-encoding step.

## 6. Cost and stopping boundary

Conditional on two encoded data tapes and four disposable scratch tapes at
their supplied origins, the credited kernel has READ=6NW, WRITE=6NW,
MOVE=20NW. The N=512, W=5 accepting fixture costs 81,920 cell actions. Fixture
preparation and right/left monomials are unmetered; this is not an invoice for
the full owner payload or physical producer connection.

The source names eight owned private fields. Their last scalar writes before
the cut are CLEARs at indices 8185,8259,8337,8412,8484,8557,8628,8702, respectively.
There are no subsequent scalar accesses to them in the retained core. Thus
their zeros at the cut do not depend on assuming their initial values zero.
The four component half-slices `Re C0[0:N/2]`, `Im C0[0:N/2]`,
`Re C1[0:N/2]`, `Im C1[0:N/2]` give an abstract allocation of four NW/2-bit
scratch windows with no additional logical fields. They are owned and zero;
the kernel returns the used halves zero while leaving the unused halves
untouched. The native child is atomic at this source boundary, so this does
not conflict with a simultaneous source scalar access to C0/C1.

This abstract assignment is not a physical embedding into four independently
based tapes: separate physical tapes, origins, head positions and paid
acquisition/return still need to be supplied. Nor does the source bind
L546's real/imaginary data to the required physical intervals and grid. The
next actual event is `L546 -= L561` in frame 4; its alignment and movement are
unpriced. Complete borrowed-helper return and F17 consumption are also open.

The result is a precise obstruction to unconditional **unchanged-grid**
substitution, together with a sharp arithmetic escape and a check that PR3303's
finer format passes this local arithmetic test. Physical caller admission
remains unestablished; missing costs are unknown. No statement here rules out
a paid layout/encoding adapter or another actual caller.
