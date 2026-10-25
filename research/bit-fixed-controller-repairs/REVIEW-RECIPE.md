# Independent mathematical review of the fixed recipe

Verdict: the fixed-recipe repair theorem and its stated finite certificates
pass this review. No mathematical acceptance by a maintainer or independent
human reviewer is claimed. This review and its extension were prepared by a
separate OpenAI Codex mathematical worker.

## What was inherited, and what is new

The historical `bit_nilpotent_recipe.py` evaluated B=1,...,6 in
\(\mathbb F_2[N]/(N^2-1)\). Its rank sequence 2,3,6,7,10,11, trace-one
observation and B4 lower bound of seven were conditional claims about that
fixed word. This review does not use their recorded PASS status as proof.
It independently replays all six complete case records and derives the
endpoint from the actual source recipe.

The new mathematical content is a closed form valid for every B, a rank and
trace proof, explicit attaining decompositions for both parities, and the
extension to every finite number of independently dirty restored spectator
banks. Thus the historical lower screen becomes an exact formal minimum:
\(2B+1\) added calls for odd B and \(2B-1\) for even B.

The unchanged source `recipe` function is extracted from an authenticated
full source file. Its imports, module state and main routine are not executed.
The independent checker uses separate constant and epsilon bit matrices;
it does not import the historical coefficient-ring arithmetic.

## Assumptions checked

- The coefficient field is F2. The theorem is not an integer-lift result.
- The same nonidentity involution N acts on every original bank.
- N+I is nonzero and squares to zero, so the dual-number model is injective.
  An identity N is explicitly excluded from the obstruction.
- The original local interfaces, bridge order, bank pairing and final
  exchange are fixed. Changing scalar topology can change the endpoint.
- A paid additional event is a rank-one idempotent coupling
  \(I+(N+I)uv^T\), with \(v^Tu=1\), equivalently a scalar-conjugated
  single-bank application of N.
- All input banks and all added spectator banks are independently dirty.
  The spectator endpoint is literal identity.
- Scalar GL changes of basis are free only in this formal event-count model.
  Their physical access and implementation costs remain unpaid here.

## Derivation audit

The t-recurrence is obtained by expanding the four literal operations on a
nonterminal pair. The x input of the next pair is still its original input;
only its y input is changed. Descending terminal bridges update each x bank
from its as-yet unchanged preceding p bank, while they telescope the q banks.
This confirms the event order used in the written endpoint derivation.

The block formula gives C=L^T L and invertible lower bidiagonal D, so A is
invertible. For M=A+I the Schur reduction is an invertible block row operation.
Every row after its first becomes a coordinate row; the first row has leading
entry B mod2. This proves the rank formula without extrapolating a finite table.
Only A's y0 diagonal is one, yielding trace(M)=1.

For even B, the displayed kernel relation removes exactly the y0 column.
Its contribution is folded into the duals of odd x columns. The resulting
dual/image pairings remain one because the y0 row of D only touches x0,
whose index is even. For odd B, the only trace-zero column is split into two
rank-one idempotents. Every asserted projector is nonzero and their sum is
exactly M. The corresponding scalar basis and inverse make the word explicit.

Rank and trace bounds apply to M direct-sum zero on any number of spectators.
They therefore permit repair projectors that mix data and dirty spectators;
the attainment uses no spectator. Conjugating an inserted repair through an
unchanged fixed-word suffix uses only the scalar part of that suffix, because
epsilon squared is zero. This preserves the same projector rank and trace.
This argument covers complete constant-identity repair gates, not arbitrary
new scalar wiring around existing query calls.

## Executed finite coverage

`CHECKS.json` is a full deterministic receipt. Normal and optimized CPython
3.12 executions produce identical bytes.

- B=1,...,12: literal recipe endpoint, closed-form coefficient, Schur rows,
  rank, trace, kernel for even B, exact attaining count, all projectors and
  explicit scalar conjugators.
- B=1,...,6: every field of each historical case, including its event list
  and full endpoint matrices, is regenerated and compared.
- B=1,...,8: 72 full arbitrary-input binary matrix instantiations from three
  nonidentity involutions and spectator counts zero, one and three.
- Twelve intended controls: changed local orientation, omitted bridge,
  omitted exchange, omitted repair, a trace-zero coupling, wrong even kernel,
  a non-involution, identity N, duplicate or missing source function, changed
  coefficient formula, and an incorrect nonidentity spectator endpoint.
  Every control requires a specific ValueError message.
  The spectator control runs the actual B4 complete repair word on a passing
  two-port involution and one dirty spectator, changes that spectator's target
  block from identity to N, and fails the same exact spectator-restoration
  gate used by all positive instantiations.

These are finite checks of the identities used in the proof. They are not
an exhaustive search over all B, all N, all scalar words, or all spectators.
The all-parameter statement is the written proof. No formal-kernel check
was run.

## Cost and publication limits

For B4, exactly seven formal repairs are necessary and sufficient in this
alphabet. Seven separately admitted 111-port N implementations would have
777 rank-one child calls if each costs 111 such children. The proof does not
admit that implementation or compare the result with a distinct controller's
planning allowance. It does not certify a full supplier, owner schedule,
fresh-frame controller, recursive moment improvement, or new kappa.

The seeded-star contribution changes the topology and is outside this
fixed-recipe theorem. Published three-bit idempotent counts and trace-zero
commutator floors have different target contracts; they were read for
context only and are not imported as proof dependencies.

The reviewer owns only this review directory. No staging files, Git branches,
PRs, external comments, shared configuration or other workers' files were
modified.
