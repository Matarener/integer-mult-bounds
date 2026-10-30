# Conditional kappa 0.00308520 from a P104 commuting-contact cascade

This construction increases complete conditional kappa from `0.00308189` in [PR #5580](https://github.com/CrocSwap/integer-mult-bounds/pull/5580) to **0.00308520** (`+3.31e-6`, raw crossing gain `+3.31558335e-6`). It also ships the fixed-endpoint supporting word `WORD-FIXED-ENDPOINTS.json.gz` reaching **0.00308415** (`+2.26058214e-6` raw over PR #5580) with all 735 `initial` and `final` frames and all 527 helper targets unchanged. The selected record remains `0.003027288235`.

PR #5561, PR #5569, and PR #5580 kept the linear execution order of all 21,686 scalar operations fixed. Reordering independent `ADD` instructions within commuting write epochs on main ports `198` and `113` eliminates seven local `MOVE` transports per call (`-126` paid calls globally, `66,852 -> 66,726`) while preserving all 208 main endpoints, all 12,814 productive fields, rank-mass surplus `760`, and all eight owned lifetimes.

Read [the proof](PROOF.md), [the construction](construct.py), [the complete receipt](RESULT.json), [the source pins](SOURCES.json), and [the verification record](VALIDATION.md). The exact raw crossing of the headline word lies in `(0.00308521055201, 0.00308521055202)` and is tested at `0.0030852005`.

## Reproduction

Python 3.10+ and the standard library suffice. No external solver is needed to reconstruct or verify both published words:

```sh
python3 -B scripts/research_package.py --package research/p104-commuting-contact
```

Both registered modes print:

```text
PASS_P104_COMMUTING_CONTACT_KAPPA_00308520
```

and the launcher prints `PASS_REGISTERED_RESEARCH_PACKAGE`. It authenticates all 33 retained PR #5545 source payloads and the pinned PR #5580 inputs, regenerates both `WORD-FIXED-ENDPOINTS.json.gz` and `WORD.json.gz` from `construct.py`, runs forward arbitrary-input replay on the base, fixed-endpoint, and headline words, verifies all 552,049 dense transpose coefficients, checks all 2,918 signed native Pauli maps, runs the full physical caller, verifies both rational moment engines (`(0.00308415555080, 0.00308415555081)` for Stage A and `(0.00308521055201, 0.00308521055202)` for Stage A+B), and checks the compiler, all 58 outer predicates, and negative controls.

## Credits

- Ali Romman (`@aliromman`) supplied [PR #5580](https://github.com/CrocSwap/integer-mult-bounds/pull/5580) (`research/p104-event-contact-step`) and the complete caller/source closure in [PR #5544](https://github.com/CrocSwap/integer-mult-bounds/pull/5544) and [PR #5545](https://github.com/CrocSwap/integer-mult-bounds/pull/5545).
- Joel Pulikkan (`@GamingPuzzled`) supplied [PR #5569](https://github.com/CrocSwap/integer-mult-bounds/pull/5569) (`research/p104-priced-handoff`).
- `@DreamingOfClouds` supplied [PR #5561](https://github.com/CrocSwap/integer-mult-bounds/pull/5561) and [PR #5568](https://github.com/CrocSwap/integer-mult-bounds/pull/5568).
- `@thu-nmrc` supplied [PR #5551](https://github.com/CrocSwap/integer-mult-bounds/pull/5551).
- Retained source notices credit Gareth Davidson, David Arias, Cinna Davis, Jacob Alan Sussman, zxv, and Cao Yifan.
- New commuting-contact cascade construction, proof, and verification by Pierre-Loic Doulcet (`@hexapode`). Apache-2.0.

## Open next questions

Independently review the commuting-contact cascade (`Stage A` and `Stage B`) and the inherited helper-endpoint contract, then recompute the complete invoice from `WORD-FIXED-ENDPOINTS.json.gz` and `WORD.json.gz`. Exhaustive commuting-epoch screening on the resulting word leaves zero remaining negative-cost commuting-epoch moves without crossing owned-register `COPY` boundaries (`13401: COPY 737, 146`), so pushing further requires coupling owned-register lifetime timing or multi-register scalar algebraic rewrites. Structured questions are recorded in [TASK.json](TASK.json).
