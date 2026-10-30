# Implement framed XOR endpoint corrections on two tapes

PR3480 can cancel P112's 23 residual translations only if they act on one
shared address register. This package supplies a different complete primitive:
correct every residual separately with an explicit finite-alphabet tape
program. It preserves natural record order and restores both tape heads.
The copy variant preserves its borrowed input; the in-place variant restores
one arbitrary dirty scratch record. Both preserve arbitrary exterior data.

[PROOF.md](PROOF.md) proves the construction for every fixed h-bit XOR mask,
every record width B and every payload. The online executor uses a literal
four-symbol transition table, two tapes and unit moves, with no counters,
address jumps, arithmetic oracle or recursive Fourier calls. The compiler
and the resulting control size are charged explicitly.

| Variant | Storage contract | Exact time for one N=2^h instance |
|---|---|---|
| Borrowed-input copy | Full owned destination, no clean interior required | `2NB+4N+(B+2)Q`, where `Q=V_h(δ)+1+2 rev_h(δ) ≤ (h+1)N` |
| In place | One arbitrary dirty B-bit scratch record, restored | `(3N/2)(2B+3)+(B+2)H`, where `H=(N−2)2^k+2N−2` for highest set bit k; identity costs zero |

For the literal 23 PR3480 masks at h=9, separate copy instances sum to
**82,936 B + 165,872** unit transitions. In-place formulas sum to
**2,033,554 B + 4,049,444**. The larger in-place bill is deliberate and
visible. These are standalone tape costs, not recursive rank prices.
Native stream acquisition, ABI/framing conversion, ownership and full
caller restoration still need an actual integration invoice. No new κ
or selected-frontier change is claimed.

## Evidence and reproduction

The exact replay executes **1,168,046 unit transitions** across 252 copy
parameter cases, 85 full small-space basis cases, all 23 literal h=9 masks
and 94 in-place cases. The in-place h=9 execution is δ=19; other large
in-place entries use the universal proved formula. Eight semantic control
groups include actual complex C_E² correction on separate streams, missing
third scratch swap, wrong masks, failed restoration, invalid moves/writes,
malformed framing, bounded failure and exported source/receipt corruption.

Python 3.12, standard library only, from the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/xor-endpoint-tapes
```

The standalone exported commands are:

```sh
python3.12 -B research/xor-endpoint-tapes/verify.py
python3.12 -B research/xor-endpoint-tapes/test_machine.py
```

`machine.compile_machine(h,delta)` returns the copy table;
`compile_inplace(h,delta)` returns the in-place table. `run` executes one
literal transition at a time. `encode`/`decode` expose the declared
delimiter representation. `verify.execute` and `execute_inplace` demonstrate
complete framed calls at nonzero origins with dirty exterior and exact bills.
The compiler is finite for each h and δ, and its control works for every B;
it is not an unpriced fixed-control interpreter for arbitrary online h.

## Current context and overlap

Canonical base `20ecf2891d80b5acf18d980b2164fb44ea7faa90`, priority revision 6.
The selected baseline binding check passes; the unrelated selected cold
replay was not run. This round fetched main, read its contribution guides,
scanned 583 open PR bodies, refreshed 100 recent/updated all-state records
through PR3878, and read relevant actual predecessor sources and partial
Discussion HTML. Coverage is bounded and does not establish novelty.

Recent PR3876 reports closure of the exact five-frame *scalar* decoder class,
and PR3873 reports a generic causal scalar-sharing bound. Those packages
were not independently replayed here. This result changes neither
contract: it implements a known operator-valued endpoint translation.
PR3878 reports a physical Gaussian expansion tile; the present
package develops the separate P112 endpoint route rather than rebuilding it.

The merged high-route permutation-frame package already carries field
permutations through BIT route factors and pays final restoration; the
coordinate-CNOT and integer-address-SWAP packages use different paid native
alphabets. Their exact scope and credit are recorded in SOURCES.json and
NOTICE.md. This package neither assumes their address operations are free
nor presents ordinary permutation compilation as a new general idea.
The added artifact is the concrete two-tape record ABI, explicit finite
transition tables, exact XOR travel formulas, restored dirty-record swap
variant and source-bound P112 bills.

## Open next questions

1. Which actual P112 native return exposes the translated address factor
   as a contiguous framed record bank? First bind one producer output to
   these exact input records and test every address. The missing owner,
   layout and representation map is not inferred from PR3480's algebra.
2. Which variant wins after complete placement and framing costs? First
   price the full destination of the copy variant against the in-place
   scratch and longer seek bill. Required buffer lifetimes and any frame
   conversion must remain charged.
3. Can one complete native caller absorb the standalone correction bill
   while improving its whole recursive moment? First combine the actual
   return, correction, cleanup and consumer in one frozen schedule. There
   is no conversion from these transition counts to a new rank tariff here.

## Credit

Prepared by Dugongue with substantial OpenAI Codex assistance. Gonzalo
Mier's PR3480 supplies the immediate endpoint-cancellation handoff and
literal mask list; Cinna Davis's PR2297 supplies the five-plane C_E²
construction and its predecessor credit. Sagar Thakrar's PR3876 identifies
the scalar-contract boundary. The shared MathProof translation/commuting
phase and frame/locality modules guide the algebra and restoration proof.
Tekalign's high-route permutation frames and the retained native routing,
decoder, Harvey–van der Hoeven/OpenAI and community lineages retain credit.
Exact sources and limits are in [NOTICE.md](NOTICE.md). No independent
human or formal-kernel review is claimed.
