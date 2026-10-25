# Exact memory at one-pass twiddle address cuts

A deterministic reader that scans the source's physical address once must distinguish an exact number N of suffix functions at each canonical round cut. [PROOF.md](PROOF.md) derives N for arbitrary finite axis counts and bit widths, including the low bits that the source moves into an early prefix. This adds a sharp memory boundary to the encoded-header handoff. It implements no producer or consumer.

For d participating axes, round h, a already extracted low bits and chunk bottom t, let R=2^a, L=2^t, M=2^(h-t), H=2^(h+1). When a<t,

    N = sum_(j=0)^d binom(d,j) c_j,

where c_j counts the residues of j sums from {s+L*z : 0<=s<R,0<=z<M}. The proof gives an exact two-case interval formula. With a=0, h>t and d>=3, the sharp cut-state requirement is d+h-t+1 bits. Degenerate rounds and cuts with no relevant unread bits are included.

The actual ell=6,K=2 mixed long/short layout at h=4 has eighteen residual classes and needs five state bits. Ignoring the early low prefix predicts only eight classes. A twelve-axis ell=8,K=3 mixed shape at h=5 has exactly 114439 classes and needs seventeen state bits, although its final modular accumulator has six bits. This larger example is evaluated by the proved formula, not exhaustive physical enumeration.

[RESULT.json](RESULT.json) records 600 complete small physical cut cases with 593228 address evaluations. Every residual-function count agrees. Separate literal modular sums check 1560 interval cases, and 1152 wide exact-integer cases check the simplified formula and sharp bit ceiling. Eleven invalid boundary cases reject. Eight actual optimized CLI fault groups and a valid retry test the scientific, layout, source and receipt gates. These finite checks corroborate the author-written proof. Independent human and formal proof-kernel review are unclaimed.

The reader must retain all input-dependent information until the cut. Its counted state includes work tapes, heads, finite control and readable early output. Prefix rereads, irrevocable input-dependent early output, a prefix-dependent supplied program, randomized error or consumer interaction change the contract. The result is an exact abstract state count at one cut, with no efficient transition encoding or total-machine upper bound. It alleges no defect in the source or earlier supplied-program interpreter. No supplier, kappa or selected-frontier change is claimed.

## Reproduce

From the repository root, using CPython 3.12 and an existing private external temporary directory:

    python3.12 -I -Werror -B research/twiddle-cut-state/verify.py
    TMPDIR=/absolute/private/run python3.12 -I -Werror -B research/twiddle-cut-state/test_controls.py
    TMPDIR=/absolute/private/run python3.12 -Werror -B scripts/research_package.py --package research/twiddle-cut-state
    python3 -B scripts/check_research_commit.py --package research/twiddle-cut-state --check-source-history
    python3 -B scripts/export_research_package.py export --package research/twiddle-cut-state --output /absolute/private/run/package.tar
    python3 -B scripts/export_research_package.py check /absolute/private/run/package.tar

The committed export runs verify.py and test_controls.py directly outside Git. The complete result receipt is read and checked; the optional --record flag deliberately replaces it. State cardinalities are decimal strings, preserving integers above 2^53 in JSON transports. [SOURCES.json](SOURCES.json) pins every runtime and inherited proof input in canonical-main ancestry. Scientific replay needs no foreign Git object or network. The bounded registered hook is not the complete selected cold replay.

## Open next questions

Implement an encoded physical-address header producer that retains or rereads the classified prefix information, then join one actual mixed-axis signed-packet/layer round. The ell=6,K=2,h=4 eighteen-state example is a small first fixture. Record all descriptor/program storage, transitions, spectators, heads, buffers, dirty-state restoration and the complete consumer bill. Efficient transitions and a physical implementation remain open. [TASK.json](TASK.json) records that handoff and its blockers.

## Credit

Nick Petalas's canonical PR3522 circuit proof supplies the named-slot/narrow-modulus premise, and its circuit.py supplies the layout comparison oracle. The retained transform source supplies the actual physical layout and combined exponent. PR3550 is contextual prior work with a different supplied-program/reread contract; no pending source from it is used. Credit Philipp/mightyOil's positional engine, Jose Manuel/jmbarrancoml's transform work, Douglas Colkitt and the retained Nussbaumer/Quandalle and Harvey/van der Hoeven lineage. Frozen notices are unchanged. New code and proof are by Nick Petalas under Apache-2.0.
