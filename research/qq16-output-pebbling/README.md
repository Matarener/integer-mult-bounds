# Host QQ16 correction temporaries in eventual outputs

This is a constructive lifetime allocation for the complete PR3985 recovery
word. It removes all **112 extra full-cover temporary banks** while preserving
all 224 original outputs in F17 and all 224 borrowed current X/Y arrays.
The 224 H1 children, 448 wrappers and 352 cover maps are unchanged.
Paid CLEARs fall from 536 to 424, reducing scalar allowance from 27,184 to
**26,960**. Peak owner-private scratch remains 16.

The dependency analysis finds eight live Z_T outputs and 104 deferrable Z_(U+A)
outputs before the future logger. Those 104 slots hold its query copies.
After all queries have been captured in private F registers, eight query
slots become response slots. The deferred Z_A definitions run before W_A
changes; the deferred Z_U definitions run after response consumption. Every
clear and frame transition is paid. No borrowed dirty helper is erased and
no private value crosses a native boundary.

[PROOF.md](PROOF.md) states the complete local contract, operator/phase
argument, allocation and invoice. RESULT.json records all 104 physical-slot
lifetimes, exact source-definition indices and the full receipt; WORD.json
is the complete transformed word. The checker authenticates and regenerates
the retained PR3985 word as data, then checks the whole new word against the
canonical routed inverse. It imports no pending executable.

This eliminates temporary allocations **inside the existing 224-owned-output
contract**. It does not prove those outputs are free in the original gauge44
physical caller. The first-B1 source cut is pinned, while six-tape placement,
movement, precision, productive-family coverage and recursive admission
remain open. No supplier or kappa change is claimed.

## Reproduce

```sh
python3 -I -Werror -B research/qq16-output-pebbling/verify.py
python3 -I -O -Werror -B research/qq16-output-pebbling/test_verify.py
python3 -B scripts/research_package.py --package research/qq16-output-pebbling
```

Python 3.12, standard library only. Normal replay is read-only; explicit
regeneration refuses to overwrite either receipt. Tests cover optimized and
normal execution, Git-free read-only export, source authentication, whole-word
and type-sensitive receipt corruption, and meaningful lifetime/alias/frame/
dirty-return controls. Signed native kernels reuse the credited PR2707 method
through PR3985, cover 114,688 columns and bind all 224 native occurrences.
The source inverse theorem and native contracts are inherited, not claimed
as code-disjoint or formal verification.

## Scope, overlap and credit

User-assigned graph-pebbling/register-allocation follow-up of PR3985 at head
`400df7fca8f60c19bf163c77564fe3fbe9154b04`, on canonical main
`20ecf2891d80b5acf18d980b2164fb44ea7faa90`, priority revision 6.
The [shared claim](https://github.com/CrocSwap/integer-mult-bounds/pull/3985#issuecomment-6263114494)
coordinates distinct streaming, lifetime-hosting, reversible-workspace and
operator-representation investigations. Partial overlap checks include the
canonical scope map and [Discussion2617](https://github.com/CrocSwap/integer-mult-bounds/discussions/2617),
which records commdata2338's PR2651 early-record/output-bank coalescing and
Nick Petalas's PR2722 physical-access work. No novelty guarantee is claimed.

The prior PR2651 result coalesces sixteen early retained records in PR2540;
this result coalesces the 104 queries and eight responses of the zero-retention
PR3985 word. The paired streaming investigation uses a different full-cover
query schedule. Its independently reviewed local construction has 416 CLEARs,
26,944 scalar allowance, nine deferred output definitions and zero future-logger
private registers, compared with this construction's 424 CLEARs, 26,960 scalar
allowance, 104 deferred definitions and eight future private registers. It is
not an executable or scientific dependency. This owner-private alternative is not asserted
Pareto optimal. Compare actual movement/access before preferring either.

Credit PR3985, ywz65 / PR2707, Arham Tahir / PR2681, Ali Romman's QQ16 lineage,
commdata2338 / PR2651, Nick Petalas / PR2722 and PR3339, and all retained
native/geometry/supplier contributors. Exact source reuse is in
PREDECESSORS.json and SOURCES.json. New work: Chris R / Clear1nsight with
substantial OpenAI Codex assistance, Apache-2.0. No independent human or
proof-assistant review is claimed.

## Open next questions

- Bind the 224 already-owned output slots to an actual first-B1 caller's
  storage and owner streams. The local alias schedule removes 112 new banks
  only after that output contract is supplied; unknown placement is not free.
- Compare this owner-private last-use schedule with the separate streamed
  query schedule under one explicit physical access model. Count full-cover
  passes, tape movement, control and endpoint return rather than scalar
  operations alone.
- Bound intermediate magnitudes and rounded errors for the changed schedule,
  then combine exact invocation/family coverage and both supplier caps.
  Exact operator equality does not establish a new multiplication exponent.
