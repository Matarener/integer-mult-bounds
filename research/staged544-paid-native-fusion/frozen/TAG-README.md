# Explicit phase tags for canonical native lifts

For the exact canonical lift used in [PR3987](https://github.com/CrocSwap/integer-mult-bounds/pull/3987),
this package gives an explicit phase tag, a compositional certificate for any
signed word of those lifts, and the compensation required inside a native frame.
The result is an elementary source-bound normalization lemma and tool.

Let `D|x>=i^wt(x)|x>` and `J_G=D P_G D^-1`. Then

```
K_G = J_G Z_tG,                  J_H J_G = J_HG,
ell(G,H) = tG + G^t tH + tHG,
(tG)_j = [q_G(G e_j)-wt(G e_j)+1]_4 / 2.
```

The bracket is always 0 or 2. [PROOF.md](PROOF.md) proves the formula for every
invertible binary G in every positive dimension using the exact polar form and
parity, then derives arbitrary signed-word certificates without enumerating
the whole state space. The implementation obtains tags from n coordinate
evaluations and tracks their pullbacks in chronological order. `word_certificate`
returns the binary product and both the residual canonical tag and normalized
section tag; optional signs distinguish a canonical binary-inverse lift from
the actual adjoint.

Chris R / Clear1nsight's PR3987 already proves the general even-linear cocycle
and supplies the actual inverse-defect witness. Those are predecessor results.
The addition here is its explicit coboundary/normalization, signed-word rule and
required central-frame compensation. For its actual witness the input tags are
144 and 68, recovering the credited defect256. The original source already
uses correct adjoints; no author bug or compiler replacement is claimed.

## The compensation is part of the result

For `T=K_B C_[r] K_B^adjoint`, the same operator is
`J_B (Z_tB C_[r] Z_tB) J_B^adjoint`. Dropping the middle tags generally changes
T. For the source primitive `C_u=((1+i)I+(1-i)X_u)/2`, an anticommuting tag
gives **`Z_t C_u Z_t=i C_u^adjoint`**, including the necessary global i.
For commuting coordinate primitives, k flipped directions contribute i^k.
The checks include exact calibration counterexamples to the untagged frame
and to omission of this global phase. They are not claimed source occurrences.

Switching to J therefore requires compensating tags, rebinding the actual
recipes and a paid physical contract. No Pauli pass, global phase, owner change,
precision bound or native implementation is priced as free. No supplier or κ
improvement follows here.

## Reproduce and evidence

Standard-library Python3.12, from the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/native-lift-phase-tags
```

`verify.py` authenticates all six retained source exports, extracts only the
four changed-interface maps in the frozen recipe subset, constructs the new
tags/certificates and checks the formulas on all512 states,16 ordered pairs and
a six-gate signed word. These pair/word fixtures are algebraic controls, not
asserted supplier adjacencies. `CERTIFICATE.json` is checked with exact types.
No predecessor executable is imported.

`independent.py` uses separate rows, exhaustive permutation inversion and direct
weight phases. It checks all168 elements of GL(3,2), all28,224 ordered pairs on
all8 states,5,376 compensated frame columns, the actual maps on512 states and
eight signed-word prefixes. It finds2,688 differing columns when middle tags
are deliberately dropped and checks both central-C branches on1,024 columns.
Finite corroboration and the general proof have distinct scopes. Neither is
human or proof-kernel acceptance.

`test_verify.py` adds semantic and actual CLI damaged-input controls, normal
and optimized execution, and a read-only Git-free positive export. The package
is self-contained: no pending commit, canonical live fixture, network or
third-party dependency is needed for the three standalone commands. The source
notice's original CRLF bytes are preserved by package-local Git attributes.

## Open next questions

1. **One priced physical interface.** Pin an actual K/adjoint/frame sequence,
   attach all input/output tags, and compare the compensated word against its
   original action. This tests whether the algebra helps compilation. A complete
   signed native recipe, caller/helper return and nonzero physical tariff are
   not supplied here; stop before expansion if the full bill is unfavorable.
2. **Broader recipe alphabet.** A serialized Clifford word may include
   translations and nonmonomial children. Start with one exact such boundary
   and state the extra relations and global phase before applying this tag rule.
   The proved alphabet is only K_G and its adjoint; the complete PR3945 native
   inventory and emitted program are outside the retained four-map subset.

## Credit

New normalization proof, word certificates and tests: ToikY with substantial
OpenAI Codex assistance, including separate AI math/test contexts. Apache-2.0.
Chris R / Clear1nsight's PR3987 at
`fc536202fdaa924158789a5ef59ac079bbe21922` owns the audited source convention,
general cocycle proof, inverse witness and finite interface audit. Six source
files are retained byte-for-byte. Credit Dugongue PR3945/3929, dataisfire PR3734,
Cinna Davis PR2226, Tekalign, icekylinx, DreamingOfClouds, Sagar Thakrar,
roger-sato, Arham Tahir and the retained native/compiler/phase/owner lineage in
`source/SOURCE-CREDITS.md` and `source/NOTICE-PR3945.md`. Those broader claims
were not replayed or admitted here. Frozen sources and selected frontier remain
unchanged. TASK records handoff-first selection and changed catalogue scope.
