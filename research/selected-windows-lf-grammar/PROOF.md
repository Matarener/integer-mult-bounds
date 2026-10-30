# Outer-line grammar refinement

The predecessor is PR2477 at `0760e745c5d3b6e66dbfab1799be75abf01576ed`;
its complete composition proof is pinned in `SOURCES.json`. Its claim that only
LF/CRLF separates outer lines is too strong: inherited PR2101 uses
`raw.decode('utf-8').splitlines()`, accepting eight more Unicode separators.
Replacing the first LF by VT preserves the13 logical lines, same-side stage
times and final LF, so the old composed comparison accepts. This counterexample
was reproduced on authenticated archived output, not merely inferred.

Let L replace CRLF pairs by LF and reject remaining CR, as before. Define G(b)
to apply L, decode strictly as UTF-8, and reject U+000B, U+000C, U+001C, U+001D,
U+001E, U+0085, U+2028 and U+2029 anywhere in the decoded outer string. G returns
the same bytes as L whenever it accepts. These are all other splitlines
separators. Thus, on an accepted G result, splitlines separates only at LF.
The inherited validator still requires a final LF and exactly13 lines; extra
or missing lines and invalid contents continue to reject. Valid LF/CRLF-only
inputs retain identical normalized bytes and inherited validation results.

Both `prepare` calls first perform unchanged role adaptation and raw-edge
authentication. They then use G for the outer log, while the eleven inner logs
still use L and have their22 already-authenticated hash fields rebound exactly
as before. Every other byte and comparator predicate is unchanged. Therefore
new acceptance implies old acceptance, and additionally the intended outer
separator grammar. It cannot enlarge the old acceptance set. It preserves
valid LF/CRLF-only representations under the inherited semantic/time policy.

This is a proof of the caller's grammar refinement under the pinned parser and
predecessor contracts, not correctness of arbitrary scientific output. It does
not tighten Decimal token spellings, prove the supplier, establish cold ancestry,
or establish any current-frontier multiplication bound. The independent Unicode
scan and full-comparison mutations are finite implementation controls supporting
the argument; the fresh replay separately checks real execution composition.
