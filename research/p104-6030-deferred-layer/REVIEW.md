# Internal review and independent argument

Two separate OpenAI Codex native agents reviewed the frozen base `721c03822c421b7f7fcbb2598993b947c4d88419`. They first derived conclusions without seeing the lead's verdict; later they reviewed the frozen proof and checkers. This is AI review, not independent human review or formal verification. No external Claude review was required or performed for this package.

## Independent derivation

The independent verifier used strong induction rather than the lead's weighted-frontier argument. Suppress the common polylogarithm. At phase width h let `S=max(N,h^eta)`, let `F_h(e)` be cost per current volume, and assume a node toll `A e^tau`, leaf cost `L e`, and total child multiplier `P/W` at width `floor(e/N)`. Put `B=A/(1-mu_tau)`.

The induction majorant is

    F_h(e) <= B e^tau + L S^(1-sigma) e^sigma.

For a leaf, `e<=S` gives `e<=S^(1-sigma)e^sigma`. At an internal node floor contraction and the induction hypothesis give

    F_h(e) <= (A+mu_tau B)e^tau + mu_sigma L S^(1-sigma)e^sigma.

Here `A+mu_tau B=B` and `mu_sigma<=1`. Every child has smaller positive width; zero width is trivial. Both cutoff endpoint conventions can be covered by assigning equality to either the elementary branch or the same valid internal bound. Remainders are bounded by the fixed `N-1` cost included in A. This proves the all-width majorant independently of a depth sum.

At the root `e<=h`, `S^(1-sigma)<=N^(1-sigma)+h^(eta(1-sigma))`. Selected `sigma<tau` and `sigma+eta(1-sigma)<tau` therefore give a complete phase bound `O(V_phase h^tau polylog p)`. Exact return and deletion keep every phase below twice original V. Summing geometric deferred widths and including the elementary polylogarithmic tail proves the requested bound. The independent argument can retain the stronger exponent tau with an enlarged polylogarithm; this package only claims the required `1-q` bound.

The independent script contains a separate exact rank-16 model with `P/W=2`, `sigma=1/2`, `tau=3/4`, all floor remainders, and no source engine imports. Its 4,152 root cases and 255 deferred schedules corroborate the argument. Three altered parameter cases reject. An eager-reservation family shows unbounded cost ratio to the toy sublinear envelope. Publication changed only the script's path selection and attribution; its output was compared byte-for-byte to the original independent output and matched.

## Skeptical findings and resolutions

- **Closest proof already exists.** Both reviewers located selected-pinned `OUTER-TRANSFER-AUDIT.md` §5, beyond the older citation in PR6110. README and PROOF credit the existing mechanism and state the narrower current specialization.
- **Wrong recurrence boundary would invalidate the result.** The ordinary tree uses compiled N/W/P, not raw P104 counts. All statements now use the uniform contract explicitly.
- **Historical atom is stale.** The current `1/250` is source-bound and tested; `0.003` is rejected. The stock law remains a named implementation premise.
- **Threshold is symbolic.** C and the full compiled counts remain unmaterialized; no numerical selected cutoff is claimed.
- **Geometric availability has a domain.** The all-root cost inequality is conditional on complete layout/router premises. PROOF clarifies that the actual selected geometry is supplied at sublinear polynomial group width, not every possible g=p address layout.
- **Independent proof must be public.** The induction above is retained here. The independent checker reports its source hash but does not authenticate it itself; the primary checker and registered metadata authenticate that shared RESULT input.
- **Portable commands.** README now distinguishes relative paths from the export root and absolute paths from an arbitrary working directory.

No blocking issue remained in the final review. The final scope/path clarifications change no arithmetic or checker logic.

## Actual review checks and dependencies

The frozen checker SHA256s were `0f76cd9af0224dd220bdeadd557dfc8998b42738cf73f774ae6ee228ffc6d51c` (primary) and `faf5be01baad34ce103834633454f2a56817fcb664da7fdba32c2741b9454730` (independent). They remain unchanged. The original reviewed PROOF SHA256 was `0f82cc98662ca83ac5d36b7c1c31e332eee7cde1aa4e8ec400e03751a4db1ac6`; the final scope clarification is described above.

Reviewers actually ran `python -I -B .../verify.py` and `python -I -B .../independent_check.py`, and the skeptical reviewer ran the independent checker with `-O` from an unrelated working directory using absolute paths. All passed. The lead's four registered commands and outputs are in [evidence/registered.txt](evidence/registered.txt). Source reads, SHA256 comparisons against the selected manifest, and separate Fraction calculations established the two moment exponents and strict margins.

Shared dependencies are the same selected RESULT, source contracts and Python integer/Fraction semantics. Agreement is corroboration; the explicit arguments and exact controls carry the evidence. Neither reviewer replayed the native implementation, supplied a physical dispatcher, proved the compiler batching premises, or certified rounded row disposal. Those limits are substantive.

The independent reviewer reread the final domain clarification and public induction. Final PROOF SHA256: `3a7ac6dae3b76d5f78849f521635da034fe99b1ea6c942175a3652b53f6262c2`; no blocking issue remained.
