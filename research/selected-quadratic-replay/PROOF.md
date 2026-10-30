# Exact selected-state adapter

This package reuses the quadratic-state engine and proof from PR 5704. It does
not change the native compiler, controller, local word or invoice. Its new
claims concern the state-format conversion, bounded cache and complete source
integration.

## State-format conversion

The retained engine returns `(n,o,C,p,a,b,d)`. Its nonzero support is
`o + span(C)` over F2. The columns C are independent. For a coefficient vector
z, the amplitude at `o + C*z` is `(a+ib)*i^p(z)/2^d`. Its proof covers each gate
in the retained P/D/X/C/phase grammar and includes the absolute phase.

The adapter enumerates every z in `{0,1}^len(C)`. Independence makes each address
unique, so assignment to the output map cannot overwrite another amplitude.
All other addresses have amplitude zero. The dense result fills those addresses
with `(0,0)`; the sparse result omits them. Both use the same denominator d.
The engine divides the scalar pair by every common factor of two. Every nonzero
amplitude is a rotation of that pair, so it has the same common factor of two.
Thus this denominator is the same minimal denominator used by both original
literal interpreters. The returned vectors and maps are exactly equal to the
original representations, not merely scalar multiples or the same support.

The selected native width is 9. Dense conversion therefore retains all 512
entries. This adapter does not claim polynomial storage for its dense public
interface. The reused engine avoids literal state evolution at each gate;
the final dense result remains available to every original caller check.

## Bounded cache and invalidation

Each key contains width, the complete ordered circuit, and the initial basis
address. The key builder copies lists and tuples to nested immutable tuples.
Its only scalar types are exact integers and strings. It rejects booleans,
floats and other objects before cache lookup, so Python numeric aliases cannot
turn a malformed input into a hit on a valid integer key.

On a miss, the unchanged engine validates and evaluates that exact key. The
result contains only immutable tuples and integers. The function is pure with
respect to these inputs, so a hit has the same value as another evaluation.
Changing a gate, gate order, matrix entry, width or initial address changes the
key. Equal list and tuple forms have the same gate semantics. Each output vector
or map is constructed anew; a caller cannot mutate the cached signature.

The process holds at most 8192 keys. Eviction removes only a reusable answer;
a later request recomputes it. No entry is saved between processes. The cache
contains neither a selected result nor a claimed invoice. Source authentication
runs before the scientific replay. Every caller check still executes and every
new exact state input is evaluated. This is checked reuse of a pure function,
not reuse of a scientific acceptance decision.

## Complete source binding

`binding.py` constructs the expected syntax tree from four exact retained files.
It changes only these sites:

- The compiler's `Op.zero_state` calls the dense adapter.
- The independent native interpreter's `state` calls the sparse adapter.
- The local verifier loads those two explicit derived modules.
- The top-level verifier uses the derived local module, keeps all original input
  paths, accepts an explicit argument list, and rejects its source-write option.
- Every remaining assertion becomes `if not condition: raise AssertionError`.
  Its condition and optional message stay unchanged. This retains the check
  when Python runs with `-O`.

All other source syntax must match. A missing native-phase check, a missing
public-row check and an omitted complete pricing call each fail this binding.
The only 13 assertions in the declared Python input closure are in the retained
Clifford compiler. All 13 are retained as explicit failures in its derived copy.
The original files and classes are never patched at runtime. Comments are not
part of the syntax comparison; source files and attribution stay in the export.

The derived main runs the same selected scientific obligations and compares
both the complete RESULT and regenerated WORD with the retained artifacts.
It preserves all 13 helper cuts, arbitrary rational input rows, dense reverse
columns, native maps and phases, productive target checks, physical contacts,
query and idle work, two moment engines, compiler and all outer inequalities.
The original rejected input/output/target/cost mutations still run.

## Independent checks and claim boundary

The small adapter corpus compares 1522 exact states and 22700 amplitude entries
with the original interpreters. Separate controls check type aliases, key
invalidation, mutable outputs, bounded capacity, eviction and source-proof
omissions. `cross.py` reruns the complete selected check and collects every
actual state input. It then compares each distinct input against both original
literal interpreters, including every numerator, zero and denominator.
Repeated equal inputs need one independent comparison; the fresh full replay
still records every call. The trace hash and counts are checked on replay.

The source's signed Pauli checks stay unchanged. Equality of a valid Clifford
operator's signed Pauli action and one nonzero state fixes its absolute phase;
the adapter does not substitute a zero-column test for those Pauli checks.
The saved selected receipt must stay identical. This retains the existing
conditional kappa statement and its five assumptions. It proves no new supplier,
physical runtime improvement, precision theorem or selected-frontier change.
The engine proof and scientific predecessor results remain credited dependencies.
