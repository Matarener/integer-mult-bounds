# Fixed-PAIR common-subexpression elimination on the physical coefficient path

## Domain and theorem

Fix the authenticated `controller.py`, `children.py`, `records.py`, `matrices.py`
and binary-word arithmetic in SOURCES.json. Inputs, source specifications and raw
field bytes stay fixed during a call. Give both evaluators sufficient arena/tape
capacity. This is the actual `children.coefficient` entry point: it admits the
parent, serializes an extension, admits a leaf, evaluates its weight, optionally
negates its inverse, then disposes the leaf, parent and extended program.

For every input accepted by the original evaluator, the package-local adapter
returns the same residue and preserves borrowed Program/Fields bytes, public
heads and numerical ownership. It changes only `Callback.weight`; admission,
serialization, matrix preparation and cleanup remain the authenticated code.
The theorem is uniform over prime-power local rings and arbitrary admitted high
lifts. No assumption that a high lift leaves a permutation fixed is made: the
optimization tests the **actual prepared** `permutation[field] == field` and
`field < 64` at each visited PAIR node.

The checker-only `prepared_codes` set is unchanged: eliminating a duplicate
subtree removes only repeated insertions of the same source codes. Preparation
call counts intentionally change and are not an observable numerical result.

The returned value at a PAIR node is `d[field] * H(pi[field],j) / H(field,j)`,
where H is the prior coefficient on head rows and 1 on tail rows. Reversal maps
both occurrences to the same `f-1-coordinate`. If the actual permutation fixes a
head field, the two recursive requests have identical `(slot,position)`. Their
subcomputations are deterministic on stable borrowed inputs. Evaluating this
request once therefore yields the same value `v` as both old requests. The
new unary continuation still computes `inverse(v)`, requires it to exist, and
performs `d*v*inverse(v)`. It does **not** replace the expression by `d` before
checking the ancestor. This preserves all high-digit, preparation, matrix and
ancestor unit failures in the omitted duplicate subtree.

Induct on the descriptor depth. ROOT and UNIT (including half-unit) are unchanged.
GOOD retains preparation, pivot selection, one ancestor and multiplication.
Nonfixed PAIR and tail PAIR retain both operands and their order. A fixed head
PAIR uses the inductive result once and the same unit check and arithmetic as
above. Child extents strictly decrease under unchanged admission, so induction
terminates. The argument neither relies on root coefficients being one nor on
an all-fixed history. Finite tests supplement this source argument.

## Encoded continuation and resource simulation

The old Stack already accepts RETURN with one residue word. On the **pending**
stack, this previously unused tag now denotes the unary fixed-PAIR continuation.
The values stack continues using RETURN normally. The guarded source adapter
checks the complete original weight-method AST and exact three replacement
sites. There is no new dynamic dictionary, key decoder, descriptor cache or tape.
A variable index is never converted to a native Python integer. The only new
predicate compares bounded native row labels, already part of the finite control
alphabet. Its comparison cost must be charged; it is a fixed finite-control test.

The unary continuation pops one value, allocates inverse, product and result,
pushes a RETURN value and frees all five owned residues. The corresponding binary
continuation used a second owned value as well. Other numerical frees are
unchanged. Pending requests have the same arity and bit width as before; the
second identical VALUE is absent. Their pop/reverse/erase work is removed.
No extra record or numerical backing is needed for the successful simulation.
The high-water comparison is a consequence of removing a subtree and one stored
value, not a claim about the host Python container allocator.

For malformed data, the same first failing ancestor remains evaluated. Source
mutation is rejected by authentication/AST guard before adaptation. Byte-level
admission is unchanged. Under an allocation cap that is sufficient for one
implementation but not the other, acceptance need not match: the theorem compares
mathematical/encoded checks under sufficient capacity. Concurrent input mutation,
side-effectful external specifications, arbitrary forged continuation tapes and
asynchronous failures are outside the input contract. Rejection cleanup is still
performed by unchanged `children.coefficient` rollback; fixture controls check it.

## Exact recursive work and full coefficient bill

Let d be the depth of an all-fixed-head-PAIR evaluated history, including the
appended current child. The original preparation recurrence is
`B(0)=0, B(d)=1+2 B(d-1)`, hence `B(d)=2^d-1`. The adapted recurrence is
`C(0)=0, C(d)=1+C(d-1)`, hence `C(d)=d`. The number of root visits goes from `2^d`
to 1. This is exponential-to-linear **matrix-preparation count** on this stated
subclass. It does not assert linear total tape actions: the retained field and
program access methods repeatedly seek from the beginning.

For a general descriptor tree, replace each fixed head PAIR's two identical
subtrees by one; GOOD and UNIT stay as before and nonfixed PAIR may still branch.
No global linear-depth or global polynomial coefficient bound is proved.
For a chain of d fixed head PAIRs, sum the actual depth-dependent cost at each
level once, including `step`, Fields.read/prepare, full 64-dimensional preparation
and 128-dimensional fallback, unary continuation, word arithmetic and erase.
Their original multiplicities were `2^(d-l)` at level l; they become 1.
The remaining arithmetic inversions/multiplications still occur at every visited
level. Unknown bit-operation tariffs are not assigned zero.

Write A_parent and A_leaf for the two complete Callback admissions, E for extension
construction, D for disposal/erase, W_CSE for this complete weight evaluation and
N for optional negative inversion. The entire call is
`K_CSE = A_parent + E + A_leaf + W_CSE + N + D`, including prime-power checks,
all live field records, word lifetimes and restoration. Nothing here removes the
two admissions or their repeated scans. PR4011's independent admission cursor
can be composed later, but is not silently assumed or credited as this saving.

PR4008 establishes that a physical leaf atom/prefix uses three semantic ADDs but
**six** independent coefficient evaluations, because split and merge each prepare.
Its full coefficient contribution remains `4 K_CSE(positive) + 2 K_CSE(negative)`
(or `6 K_CSE + 2 J` when J is separately defined as the extra negative-inverse
work). The adapter introduces no cross-call cache. Source generation, GL64 payload
routing, packet traversal and stock/precision/lifetime obligations outside these
calls remain additional costs. The selected kappa does not change.

## Independent checks and scope

`check.py` invokes the real serialized entry point with Word.inspect disabled
inside runtime. Rank-seven synthetic but fully admitted source definitions have
identity preparation and a head/tail-permuted low matrix, with nonzero high lifts.
The independent native-integer oracle constructs the projector and full fallback
matrix over Z/9Z, then compares values. Good, ordinary nonfixed PAIR, reverse tail,
unit, half-unit and negative-inverse branches are covered. These fixtures prove
neither that all R437 sites use the fixed-field path nor a full physical payload
run. The full R437 source-plan catalogue is deliberately not reconstructed.

Preparation counts, all created record tapes, numerical word actions, public
heads/bytes and live ownership are measured after fixture creation. Thus the
receipt includes both admissions, extension serialization and erase, stacks and
complete coefficient evaluation. Python execution time is not a machine-step
claim. Finite controls reject a malformed ancestor high digit, nonunit root,
changed AST, false receipt and missing/changed/symlinked source input. A mutant
that treats nonfixed rows as fixed is detected by the field-57 root-unit-2 case.
