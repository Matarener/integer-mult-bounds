# Complete binary refinement of the fixed CRT repair program

Prepared by JoyboyBrian with substantial OpenAI Codex assistance. Apache-2.0.

## Statement and inherited hypotheses

Let P be the exact 8,242-instruction program assembled by the pinned PR5105
`machine.py` and `compiler.py`, with its 31 distinct tape roles. Assume the
successful input contract in its pinned PROOF.md: unary geometry
(G,H,K,Y,J,B)=(2,2,6,8,2,0); a framed, target-independent 32-bit ROM;
4,096 opaque 12-bit record labels in the supplied raw post-S order; zero
heads; and private blank tapes. We inherit its source-algorithm correctness,
allocation and successful-domain theorem. We do not infer those from one run.

The program emitted by `lower.py` operates through the unchanged PR4982
`Machine` and `BitTape`: one-bit reads/writes, unit bit-head movement,
one-bit Boolean gates, one-bit assignments, branches, jumps and halts.
Neither a runtime decoded symbol nor a runtime host tape-role selection is
an instruction. The instruction's tape name is always a literal fixed role.
Program counters and emulated head coordinates are configuration machinery.

The emitted program refines every source step on the stated successful
domain and therefore returns the same ideal-T payload order. It preserves
borrowed geometry/ROM, erases the same private roles, returns every physical
head, and clears all 14,839 finite-control bits. It has 557,123 static
instructions. If the source executes T instructions, including its halt,
then the complete binary invocation costs at most

    101391 T + 29679

charged bit/control actions. This includes initialization and final control
erasure. The source theorem's symbolic bound for T can be substituted
without running the full binary layer. This is a fixed-program refinement,
not a variable-geometry E(p,ell), a complete physical multiplier, or a
claim that the full binary layer was executed.

## Finite closure and encoding

`closure` starts each source register at {None}; every tape contains blank,
the six headers also contain `<`, `>`, `1`, ROM contains its markers/bits,
and data contains `<`, `>` and all 4,096 records. It propagates possible
values monotonically through **every** source instruction, including loop
back edges implicitly by repeated saturation. Reads take the union of the
possible named tapes; writes enlarge those tapes; copies and finite tuple
expressions propagate their values; field projection propagates each
defined tuple component; comparisons/record/not yield Boolean values;
bit-string gates yield `0` or `1`. Branches and jumps produce no values.
All constants and nested operand expressions are included in the codebook.
Unsupported operations, large Cartesian products or exhausted code space
fail compilation; they do not silently truncate the domain.

The saturation terminates after four rounds for this exact P. By induction
on executed steps, registers and tapes remain in the saturated domains.
This is an overapproximation, including transient None alternatives that
are not reachable at many instruction sites. In the successful source
execution all tape operands are actual roles and all field operands are
tuples of the appropriate length. The latter follows specifically from
the producer's returned role products and the scanner's producer-owned
stencil: after the END test, each token is an admitted five-field atom.
We do not claim string indexing or malformed arbitrary source states are
refined by the tuple-field blocks. Undefined/unadmitted dispatch and field
values reject. This preserves the original successful-domain restriction.

Python equality identifies False with 0 and True with 1, recursively in
tuples. `canon` makes precisely that identification. The source uses no
Boolean identity/type test; its only type-sensitive operation is `record`.
Every reachable record is `('R', n)` with integer 0<=n<4096; canonicalization
preserves this predicate, truthiness, equality, tuple construction and
projection. Thus the canonical state is a sufficient source-state quotient.

There are 4,932 canonical values. Blank `_` has code zero. Records have
code 4096+n; all other values have distinct codes below 4096. Codes use
13 little-endian bits. In particular record recognition is exactly the
high code bit, and all 4,096 payload labels remain distinct. There is no
record-pair lookup table. Unused bit patterns are outside the entry
contract. Source cell j occupies positions 13j through 13j+12. At source
instruction boundaries each physical head is at 13 times its source head.

## Instruction simulation

Each source register is a 13-bit finite-control word. Temporary control
bits are reused between source instructions: names beginning `$` are
disjoint from the actual source register namespace. No temporary is read
before its block assigns it. At entry, explicit set instructions initialize
source words to code(None) and scratch to zero. Both successful and
rejecting exits share explicit all-zero control tails; rejecting exits
have no data rollback promise.

* **Constants, copies and products.** A constant writes its 13 code bits.
  Copies preserve every bit, including when source and destination alias.
  A finite product evaluates all component words before its decision chain.
  For each statically enumerated tuple, conjunction of component equalities
  selects its unique code; injectivity proves exactly one match for an
  admitted operand. This includes nested role products and five-field
  stencil atoms. Static enumeration is compilation, not execution.
* **Equality, inequality, membership and truth.** XOR each pair of code
  bits, OR the differences, then negate: this is equality of canonical
  values. Inequality reverses the result. Membership ORs the finitely many
  element comparisons. Truth excludes exactly the finitely encoded falsy
  values (None and zero here). Boolean results are encoded as canonical
  integer zero/one. Inputs are evaluated before an aliased destination is
  overwritten.
* **Field and record.** The field block compares the whole input code
  against every admitted tuple alternative and emits the chosen component
  code. Its defined branches therefore implement tuple projection. Record
  uses the high bit, whose exactness follows from the entire code inventory.
  This does not decode a payload integer into a runtime address.
* **String-bit gates.** Compare each operand against the code of string
  `1`; apply XOR/AND/OR to those Boolean flags; emit the code of string
  `0` or `1`. This is the precise source semantics, including its treatment
  of operands other than string `1`. It does not confuse integer one with
  string `1`.
* **Tape role dispatch.** A literal role chooses its fixed tape directly.
  A role register is compared against its statically possible fixed roles;
  each matching arm names a literal tape in every emitted instruction.
  For this P each role register's valid role set is a singleton (None may
  also occur in the overapproximation); the validation chain remains
  explicit. No host lookup uses the runtime role word. Role selection
  finishes before a read can overwrite an aliased operand register.
* **Read/write/move.** A read or write visits the 13 consecutive bits and
  then rewinds twelve positions to the cell start. It realizes exactly one
  source symbol access without altering other cells. A source unit move
  emits thirteen unit bit moves. Thus the head invariant is preserved,
  including append/blank regions and arbitrary existing payload contents.
* **Control.** Internal decision chains have forward edges only and leave
  at the designated block end. Source branch/jump targets are relocated
  to exact source-block starts, including backward loop edges. A source
  halt goes to its shared erase tail and corresponding final halt.

These cases cover all sixteen opcodes actually emitted by P. They also
explain operand aliasing: every value needed for a result or role arm is
read before a destructive result write. The verifier executes alias
controls, but the cases above establish the quantified step relation.
Induction through arbitrary repeated source loops composes the relation;
finite tests are corroboration, not the induction argument.

## Cost, storage and composition

The exact generated source-block intervals have maximum length 101,391.
Every internal edge goes forward; the only source back edges terminate a
block at another source boundary. Therefore every simulated source step
uses at most this many binary actions, regardless of the runtime branch.
Initialization writes 14,839 control bits; the terminal tail writes them
again and executes one halt. Consequently the bound is
101391*T + 2*14839 + 1. The block maximum is deliberately conservative,
dominated by overapproximated aggregate alternatives, not an optimization
or observed maximum for a production input. Shared exit tails avoid
replicating all control erasure at every rejecting source site.

If the source's visited retained tape backing is B cells, its bit encoding
uses 13B cells, plus 14,839 finite-control bits and the fixed program.
Moving through a source cell's encoding visits only its own 13 bits;
there is no hidden record gather or payload transpose. Private source
blanks become actual zero bits; source marker disposal thus erases the
entire corresponding codeword. All heads zero at source exit implies all
physical heads zero. The ambient/private blank-storage grant is inherited;
we do not establish initialization of arbitrary dirty exterior storage.

Input serialization, fixed program construction, the ROM producer and raw-S
production remain external prerequisites. Static compilation here takes no
input payload, ROM contents or runtime address. It emits one fixed program
for the specified source, not a program regenerated per payload.

## Executed evidence and its limits

`verify.py` authenticates every declared source before assembly. Its
microchecks use the **original PR5105 executor** as the reference, including
aliased destinations, all operator classes, typed equality, stencil fields,
dynamic role selection, bit strides and complete exit-control cleanup.
Three executable faults omit a bit stride, retain control, or route to the
wrong physical tape. The code inventory covers all 4,096 record labels.

Two longer comparisons run the complete fixed-program blocks on persistent
encoded tape objects, checking each source boundary's changed register,
write and head plus the complete endpoint. One executes the actual producer
through its scanner handoff. The other starts at the key-entry state
obtained from the actual complete source producer/scanner/split and executes
its whole current-inverse key to the real continuation. That cut is encoded
once at entry; it is not evidence of binary scanner execution. No borrowed
or output stream is reconstructed between the bit instructions in a cut.

We did not execute the full binary mask, all 2,944 keys, all sorting passes
or whole-layer endpoint. Their binary correctness follows conditionally
from the source theorem and the step proof above, not a claimed full replay.
No independent human or formal-kernel acceptance is asserted.

## Attribution

PR5105 supplies complete finite control and the source caller proof. PR4982
supplies the unchanged binary executor and earlier key simulation; PR5015
supplies the isolated radix refinement. We preserve the CRT/key/scanner/
repair lineage of Cinna Davis, Hiroki KUMAZAKI, ToikY, Jose Manuel, Ryanson
Jonathan, unpaidmoon, codyw912, Douglas Colkitt and the retained notices.
