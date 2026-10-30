# PR5908 rational binder: static CPython 3.12.15 compatibility review

**Finding: the shipped whole-file source pin rejects the fetched official
CPython 3.12.15 `fractions.py`, although its only difference from the accepted
local file is an unrelated `Fraction.__pow__` branch. Add only an explicitly
reviewed source/runtime identity; preserve all executable, slot, closure,
default, MRO, operator and gcd checks.**

The requested failing head is `ec0afa7633ff72e1c5ea26bb5726ec569a3f59ac`,
CI run `40505352497`. The parent reports the original registered verifier and
integer normal/optimized stages passed, with the rational probe failing at
`finite_probe.py:52` because `arithmetic_binding.bind()` returned None.
This review did not fetch CI, execute Python, import scientific modules,
compile code, run tests, perform arithmetic, use the network/browser, mutate
Git, or edit measured/published source. It read local source, compared bytes,
and wrote only this review document.

## Exact source difference

Inspected binding:
`repo/research/c-verification-feasibility/rational/arithmetic_binding.py`.

| Source | Observed SHA256 |
| --- | --- |
| Accepted local `/usr/lib/python3.12/fractions.py` | `cf33568f7b767f66896995a7a81cc662e8be226f2e58efb61d2028f64eb5d231` |
| Parent-fetched `ci-python/fractions-3.12.15.py` | `d52d1ab9d5be26924e4914a5e40069c992bbfa68f773694c2e5ee8452d0766a0` |

The second file was supplied by the parent as the official CPython v3.12.15
source. This reviewer verified its local hash and complete textual diff, not
its network provenance. Retain the parent's source URL/fetch receipt when
adding the new pin. Expected upstream provenance is the CPython v3.12.15
`Lib/fractions.py` source, with exact tag/URL retained by the parent.

The complete unified diff has one hunk, around local line 828:

```diff
-        else:
+        elif isinstance(b, (float, complex)):
             return float(a) ** b
+        else:
+            return NotImplemented
```

This is in `Fraction.__pow__`. The guarded batching methods `_add`, `_sub`,
`_mul`, `__abs__`, `__bool__`, `__new__`, `_from_coprime_ints` and the
`_operator_fallbacks` forward/reverse closures have unchanged text. The
Fraction base-class declaration, owned slots and constructor defaults are
also unchanged. The edit shifts later source line numbers, including
`__abs__` and `__bool__`, by two lines.

## Why the current guard rejects it

`SOURCE_SHA256` at arithmetic_binding.py line 18 contains only the accepted
local hash. `_codes()` at line 37 rejects any other full-file digest with
`ValueError('pinned Fraction source')`. `bind()` catches that ValueError and
returns None. `finite_probe.py:52` therefore reports only the generic
'supported pinned arithmetic binder' failure.

The first `DIRECT` method is `_add`. Once preceding runtime/slot checks pass,
its `_function()` comparison invokes `_codes()` and encounters this rejection.
Thus the official 3.12.15 source cannot pass the shipped binder, regardless of
whether its selected methods would otherwise pass every executable check.
This is a definite source-compatibility defect. The original hosted traceback
did not expose its actual stdlib path/hash or the swallowed reason, so this
review cannot prove that no later runtime condition would also fail after the
pin repair. The next fresh hosted run or a narrow diagnostic must show that.

## Why the other guards should remain unchanged

- **Slot binder:** `slot_binding.bind(strict=True)` authenticates pure getter
  executable shapes and exact owned member descriptors. It does not use the
  new rational whole-file hash. The inherited verifier passing is consistent
  with that separate contract. The fetched diff changes neither getter.
- **MRO:** both files declare `Fraction(numbers.Rational)`. No difference in
  the source suggests relaxing the exact `(Fraction, Rational, Real, Complex,
  Number, object)` identity chain. Hosted identities still need live checking.
- **Defaults:** `__new__(cls, numerator=0, denominator=None)` is unchanged.
  The two exact defaults and all no-default/no-kwdefault requirements remain.
- **Closures:** `_operator_fallbacks` and its forward/reverse bodies are
  unchanged. Preserve the exact two closure cells and identities of
  `fallback_operator` and `monomorphic_operator`, plus allowed `__class__`
  closures for direct/factory functions.
- **Gcd/operator identities:** those are live module/builtin identities, not
  the changed `__pow__` branch. No evidence supports weakening them.
- **Compiled code flags:** `_shape()` deliberately includes `co_flags` and
  the exception table. `_codes()` recompiles the authenticated file on the
  current interpreter with `optimize=sys.flags.optimize`. Preserve this
  check. It does not compare `co_firstlineno`, line tables, or filenames, so
  the two-line offset alone is not a reason to remove code-shape fields.
- **Future/compiler inheritance:** neither compared fractions source nor
  the inspected arithmetic binder has a future import. There is no observed
  future-flag mismatch. `dont_inherit=True` may make the compilation context
  explicit if the parent chooses that small hardening, but it is not the
  diagnosed source-pin fix and must not replace exact flag checking.
- **Materialization:** `_from_coprime_ints` remains a classmethod with the same
  source and allowed class closure. Preserve its drift rejection.

The fetched source therefore supplies no reason to accept unknown MROs,
foreign functions, alternate math/gcd implementations, arbitrary source
files, or masked bytecode differences.

## Minimal pin-preserving repair

Replace the single allowed source identity with an explicit reviewed mapping,
preferably recording both exact patch version and digest:

```text
CPython 3.12.3 / observed Ubuntu host source:
  cf33568f7b767f66896995a7a81cc662e8be226f2e58efb61d2028f64eb5d231
CPython 3.12.15 / reviewed official tagged source:
  d52d1ab9d5be26924e4914a5e40069c992bbfa68f773694c2e5ee8452d0766a0
```

Keep the CPython implementation requirement, reject all unlisted runtime/source
pairs, reject source symlinks, and compile only the authenticated bytes. Keep
all current `_function`, `_snapshot`, `fresh` and strict slot-binding checks.
A version-to-exact-digest mapping is preferable to treating every 3.12 patch
release as tested. Never use a wildcard version/hash, automatically enroll
the installed digest, accept a digest on first use, substitute AST equivalence
for source authentication, or bypass a failed binder in the finite probe.

This mapping makes a second reviewed input admissible; it does not change the
numerical algorithm or admit an unreviewed runtime. The source review must
record that the full difference is the separate power-dispatch change. The
fixed rational finite controls and all existing fallback/drift controls must
then run unchanged in fresh normal and optimized processes on the supported
hosts. The hosted exact-head run must pass before CI compatibility is claimed.
Retain the original failed head/run and its error as evidence.

The binder's `_expected` cache is process-local expected code data, not an
arithmetic answer cache. If refactoring it for multiple supported identities,
key or annotate it with the authenticated version/digest/optimization identity
so an old cache cannot stand in for an independently selected source. Do not
silently reuse a cached successful source check in a negative-source test.
No complete performance claim is affected or newly established by this repair;
the primary 15% target remains unmet.

## Narrow diagnostic proposal

The existing fallback-compatible `bind()` can continue returning either a token
or None. Add an internal strict path which labels the same existing rejection
predicates, then let the diagnostic surface report that result without changing
the acceptance decision. For example, an internal source predicate can expose:

```text
stage: source_identity
implementation: cpython
version: [3, 12, 15]
fractions_path: <actual loaded module source path>
actual_sha256: <actual file bytes digest>
supported_identities: <the explicit reviewed mapping>
reason: unlisted runtime/source identity
```

A successful diagnostic should report the selected source identity and that
the existing executable/default/closure/slot/MRO checks completed. If a later
predicate fails, report a stable stage label such as `slot_binding`, `mro`,
`arithmetic_defaults`, `arithmetic_executable_shape`, `operator_closure`,
`gcd_identity`, or `inplace_protocol`, plus the exception class where relevant.
Do not catch every unexpected exception and call it an unsupported runtime;
retain the existing narrow exception boundary or expose unexpected errors.

The probe should still fail when its token is None. It may include this
read-only diagnostic in that failure message; diagnostics must never turn
None into a successful token or skip the source/finite controls. The strict
path must be shared with normal binding so the diagnostic cannot drift into
a different acceptance rule. This needs no arithmetic experiment.

Useful bounded additional source-guard controls are rejection of an unlisted
version/digest pair and rejection of bytes changed from either reviewed source,
while the known pair is selected explicitly. Test a pure authentication helper
or use isolated temporary fixtures with restored binder state; do not modify
the installed stdlib file. Preserve every current arithmetic-code, factory,
closure, gcd, in-place-operation and fallback rejection.

## Status

The static source incompatibility is identified and a narrow repair is
specified. Hosted live binding after repair remains unverified by this worker.
No evidence supports changing the integer result, loosening rational guards,
skipping a finite control, admitting a speedup, or starting another numerical
route. Only this report was written.
