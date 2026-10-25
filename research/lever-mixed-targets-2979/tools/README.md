# The programs

All are Python 3 with the standard library only. `verify.py` (one folder up) runs them with `python3 -I -B`.

| program | what it does | where it comes from |
|---|---|---|
| `transport.py` | rebuilds the community's native canonical form of a borrowed word (frame ids, register compaction, zero buffers, warps, twisted additions) and replays it exactly in the free algebra of warps on every input column, in both orientations | my own implementation, written from the documented semantics of the community's `bw_transport.py` (read, never run); the construction it transports is Cinna Davis's anticipatory dirty borrowing (#2226), and the transport stage of the community's native chain is the GK / #433 lineage. On #3945's words it reproduces the community's own canonical words exactly (equal content hashes). |
| `lower_w.py` | lowers a canonical word to my certificate format (gcert/1w, and gcert/1b with `--to-1b`) and checks it: frames, warps, residual widths helper by helper, the local profile, the invoice, the full program replayed to the endpoint, and seven wrong versions rejected (`--mutants`) | mine; it extends my earlier lowering, itself adapted from Ryan Shea's `canonical_to_gcert_probe.py` |
| `g0_staged.py` | the head test: follows every array of a staged unit through my nine-stage hosted network (step order read from the Lean source in `../network/`), with the word's ORDER, DISPATCH, PLAN, TEMPLATE and FILL rows; classifies every remainder block as a literal head, a literal tail or neither | mine |
| `pricer.py` | an exact re-implementation (not a copy) of the community's moment engine: the largest b on the 10^-24 grid with the moment sum below 1, certified by rational enclosures | mine; the engine it re-implements is the community's (`research/native-complex-moment552/engines/moment.py`, `outer.py`; `research/gauge44-frames-x/code/assemble.py`) |
| `mixed.py` | the balance of a recursion with several job sizes, solved with 60-digit decimals | mine |
| `lever_price.py` | the variants of the lever (uniform, half cut, full cut, best separated cut, break-even); on import it also prints a table of the lever on several community words | mine |
| `price_ours.py` | prices the head test's output: the uniform root against the stated root, and the lever variants with the measured head count | mine |
| `rate_cert.py` | the exact rational certificate of the mixed rate inequality at N/10^10, and its refusal at (N+1)/10^10 | mine; the same enclosures as the Lean rate module |

Changes against the copies that produced the recorded results: absolute import paths replaced by the program's
own folder (`lever_price.py`, `price_ours.py`), and an option `--xhost` added to `g0_staged.py` (the folder of the
network's Lean files). Nothing else differs. The same files are in my public repository (README section 5).
