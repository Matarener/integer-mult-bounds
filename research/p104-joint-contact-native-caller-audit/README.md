# Independent native, caller and funding audit of PR5551

**Result (scoped audit, no new κ).** Every native map of the PR5551 coupled-contact word passes a dense
all-column check with absolute phase: 2,940 distinct MOVE maps, 40 distinct helper endpoint pairs and
208 intrinsic main adapters, 3,188 operators in total (3,187 distinct, since one helper pair is also a MOVE map), each compared on all 512 columns. Earlier dense
audits checked only the maps new to each word (three for PR5545 in PR5548, four for PR5551 in its own
native peer). The remaining maps were an inherited premise. On the same word, Chris R's PR5550 caller and
target-binding checker passes, an own exact replay reproduces the six ADD contact edits and the paid delta,
and an own decimal interval engine reproduces the author's raw crossing exactly.

Base: canonical main `5e0052ca0aa3036a3afa8b0438927377c8d97d53`, which already contains the PR5551 package
`research/p104-joint-contact` (author thu-nmrc). All inputs are pinned by Git blob and SHA-256 in
[SOURCES.json](SOURCES.json). This follows the PR5551 intake note: review the P104 producer/caller and the
coupled-contact delta together, recheck the native paid-map inventory, the compiler/consumer obligations,
all productive targets and complete funding, and use a serial bounded replay.

## What is checked

| Layer | Check | Result |
|---|---|---|
| 1. Own replay (no source imports) | Both words replayed from scratch: strict span nesting of every MOVE, common chart of every ADD/COPY, rational rows of all 743 endpoints, owned lifetimes | PASS on PR5551 and PR5545 |
| | Delta PR5545 → PR5551 | Scalar program identical up to frame labels; 6 ADD + 15 SCALE chart edits; local paid delta 2H1 − 3H2 + H3 − H4 + H5; all public endpoint spans and the helper profile {4:51, 5:36, 7:24, 8:122, 9:294} unchanged |
| 2. PR5550 caller checker | Byte-pinned checker, four input lines changed in a temporary copy (as in PR5567); positive control reproduces the complete PR5550 output on PR5545, SHA-256 `b51a7d19…4009` | PASS on PR5551: 69,912 paid / 12,814 productive, 288 exact signed-Pauli and phase-anchor checks, 9,486 fresh helper checks, ordinary passes 127,292,680 ≤ 184,647,552; all ten PR5550 controls reject; a changed invoice is rejected |
| 3. Dense native inventory | PR5548's credited exact Gaussian-dyadic interpreter compares the lowered circuit with the literal frame circuit on all 512 columns: exact equality, norm and support size 2^rank | PASS on all 3,188 operators (`--full`); ranks match the paid transition ranks; a second, separately written driver gave the same 3,187 digests |
| 4. Own funding engine | 80-digit decimal ln/exp with 10⁻⁷⁰ relative padding, bisection on a 10⁻¹⁴ grid | Raw crossing (152076558357/5·10¹³, 60830623343/2·10¹³) = (.00304153116714, .00304153116715), equal to the author interval; .00304117, .00304153 and .0030415305 positive, .00304154 negative |

Native fault controls on the new map 615 → 207: a global phase fault with an unchanged signed tableau and a
flipped child sign are both rejected by the dense comparison.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3.12 -B research/p104-joint-contact-native-caller-audit/verify.py
```

The default run is serial and takes about five minutes. It checks layers 1, 2 and 4 completely and a fixed
deterministic subset of layer 3: all four new maps, every helper endpoint pair, all 208 adapters and every
32nd MOVE map. Each subset matrix digest must equal the digest in [FULL-CHECK.json](FULL-CHECK.json). The
complete inventory runs with

```sh
python3.12 -B research/p104-joint-contact-native-caller-audit/verify.py --full --jobs 4
```

in about eleven minutes on four cores; it recomputes all 3,188 digests and compares them with FULL-CHECK.json.
The marker is `PASS_P104_JOINT_CONTACT_NATIVE_CALLER_AUDIT`. [PROOF.md](PROOF.md) explains each layer.

## Scope and limits

This audits the finite 9-qubit local word and its complete invoice. It does not materialize the uniform word,
so the uniform compiler, owned erasure, precision and tape costs and analytic recovery remain inherited premises,
as in PR5551 and PR5550. The selected record stays .003027288235; PR5551's certified endpoint is the author's
checker constant. This is an agent check, not human or proof-kernel acceptance. The checked native maps cover the
"native all-column implementation" premise only for this fixed word.

## Open next questions

- Binding the uniform-compiler contract of PR5550 to the FULL-CHECK.json digests, so the finite native check
  carries to every recursion level. This is the remaining inherited native premise.
- Maintainer admission of PR5551, after which PR5553, PR5561 and PR5569 can be judged on an admitted parent.

## Credit

thu-nmrc (PR5551 construction and word). Chris R / Clear1nsight (PR5550 checker, used unchanged except four
input lines; PR5548 dense interpreter, imported unchanged). Ali Romman (PR5544/PR5545 and the P104 caller).
The P104 lineage and all retained native, Clifford, compiler and analytic contributors are credited in the
cited packages. This package was prepared for Matarener with Claude (Anthropic), via Claude Code. Apache-2.0.
