# Cubic scalar caller bounds

Scalar bank words in the full algebra `Q[N]/(N^3-1)` need at least five paid
queries on three independent banks when their directions are constant rational
rank-one nilpotents. This three-bank bound permits arbitrary scalar-polynomial
coefficients. For the narrower paid alphabet `E_ij(±N)` and `E_ij(±N^2)`, with
arbitrary constant `GL_n(Q)` bridges, the complete target `N I_n` requires

```
3 | n,
k >= n + ceil((n+1)/3),
max(0,2n-k) <= a,b <= min(k,2(k-n)),
```

where `a+b=k` counts the two powers. A homogeneous word needs `k>=2n`.
Three matching layers are impossible. Four layers are impossible if each is
pure in one power; four internally mixed layers remain open. These are
necessary bounds, with no positive scalar synthesis claimed.

[The proof](cubic/PROOF.md) gives the all-word arguments, including the strict
equality case and completed four-pure-layer proof. The power-balance interval
adds a useful screen: at `n=3,k=5` both powers must occur, and at `n=6,k=9`
each must occur between three and six times. [The independent check](independent/PROOF-INDEPENDENT.md)
uses ordinary rational matrices and imports none of the candidate arithmetic.

The full algebra premise matters. A primitive-only operator satisfying
`N^2+N+I=0` does not automatically inherit this full-ring obstruction. Fresh
checks retain augmentation, all arbitrary input columns and an excluded
four-factor word with operator-dependent directions. The wide two-power
proof is not extended to arbitrary polynomial coefficients.

## Conditional cost screen

For the stipulated optimistic OPEN profile on `n` banks of twelve fields and
`k` calls in `s` legal matching layers, the complete histogram is
`H={1:8k,2:40k,3:16k,5:12(ns-2k)}`, with `m=2+5s` and `W=12n`.
Inactive banks remain charged. The deficit `mW-mass=24n-16k` is conditional
on an actual matching schedule (`k<=s floor(n/2)`) and that profile. The
query bounds make three- and six-bank cases fail every positive exponent
under strict child contraction. A positive optimistic deficit at a larger
width does not supply a caller or its missing costs.

Constant bridges are free only in the lower-bound relaxation. Native source
access, admission, scalar/address work, restored helper endpoints, precision,
ownership, storage and tape execution remain separate. No selected result or
new kappa is claimed.

## Reproduction

Run `python3.12 -B scripts/research_package.py --package research/cubic-scalar-caller-bounds`.
`VERIFY.json` lists direct standard-library commands for a Git-free read-only
export:

```
python3.12 -I -O -B verify.py --stage cubic
python3.12 -I -O -B verify.py --stage independent
python3.12 -I -B controls.py --package .
```

Every executed component and expected receipt is authenticated. The wrapper
executes captured source with optimization disabled and uses fresh external
scratch. Both complete historical receipts are compared with exact JSON types
and no omitted fields. The independent stage retains its full implementation;
the wrapper supplies only the fixed historical-receipt argument. Retained
mathematical code is never imported through a filesystem or bytecode cache.

The candidate executes 27 actual defects and named-guard deletions; the
independent stage executes twelve more. Normal and optimized Python 3.12
component receipts agree completely. Finite examples check identities and
sensitivity; the universal bounds are written proofs, not a finite search or
formal-kernel result. Compact integration controls separately test source
execution, complete typed records, stage coverage and real production gates.

## Sources and related work

Current guidance and the exact task card are pinned to
`12fa8c5c844be21bfefb38a19503fbd867a11244`, priority 7. The historical cubic
lane retains scientific snapshot `20ecf2891d80b5acf18d980b2164fb44ea7faa90`
and unchanged sources and receipts. This assigned scope does not solve the
current installed QQ16 caller task. Original notes mention a quadratic
continuation; that context is preserved, but no quadratic-caller files or
claims are included.

Normalization, rank and specialization methods retain credit to eumemic's
PR288 source and Ali Romman's PR468. [PR4023](https://github.com/CrocSwap/integer-mult-bounds/pull/4023)
uses a distinct order-four/quartic unary-query alphabet.
[PR4081](https://github.com/CrocSwap/integer-mult-bounds/pull/4081) treats an
actual Gaussian Clifford satisfying a primitive cubic relation and fixed
response interfaces. Neither is identified with this full cubic-ring
constant-direction model. `SOURCE-AUDIT.md` gives exact links and boundaries;
the methods are not claimed as new.

Ross Richardson with substantial OpenAI Codex assistance in the proof,
checker, integration and separate mathematical review contexts. Apache-2.0.
AI review is distinct from independent human acceptance and formal proof.

## Open next questions

Specify one bounded four-layer mixed-power alphabet and test its complete
full-ring target against the power-balance constraints. Before applying a
bound to a native operator, prove the required algebra representation rather
than merely order three. Wider synthesis or supplier construction still needs
that bridge and a complete favorable invoice; `TASK.json` records the gates.
