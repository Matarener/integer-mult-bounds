# P104 phase-uniform gauge and forced completion tag

**Scoped ideal-operator result; no new supplier or kappa.** For the 104 binary
labels published in [PR3954](https://github.com/CrocSwap/integer-mult-bounds/pull/3954)
at `f1e2839819959cd0534d008be91ed5b79ec55a6a`, the explicit orthogonal involution

```
z=420,   O x=x+(x dot z)z,
O columns=[1,2,416,8,16,388,64,292,164]
```

sends every label to weight 3 modulo 4. All 10,816 tensor product lines then have
weight 1 modulo 4: the predecessor's 5,376 gauge-dependent normalization
mismatches disappear. This answers one coordinate-gauge question left open by
PR3954, without claiming to complete its physical caller.

## What is proved

[PROOF.md](PROOF.md) gives the arbitrary-dimension/operator arguments and the
source-bound finite premises. Every orthogonal nine-dimensional gauge applied identically to both tensor
factors and making these product phases constant has the **same nonzero input quadratic defect**
`z=420`. The alternative character `91` would violate preservation of the
all-ones characteristic vector. This class cannot preserve the standard full
native transform F; the result is not an enumeration of the orthogonal group.

For the explicit involution `K=O tensor O`, the completion translation is

```
a=z tensor 511 + 511 tensor z
 =430582246074561917307300,   wt(a)=40,   Ka=a.
```

With `R_K f(x)=f(K^-1 x)`, exact uniform completed-F encodings are
`E_in=R_K` and `E_out=X_a R_K`, with
`F E_in=E_out F` and `F E_out=E_in F`. These identities hold on independently
arbitrary functions in all 280 local roles, including 72 dirty helpers. They do
not assume zero helper input. General non-involutive gauges distinguish the
input defect a from its output image K_G a.

If a consumer forces a return to the original tag, its translation has exact
minimum length four in the **restricted one-bank alphabet** of odd-line
`C_u` and `C_u^-1`, one call each. The proof allows no other gates, role mixing,
ancillas or free translations. This is a word tariff, not native compiler,
rank-unit or cross-role optimality admission.

The inherited favorable 81-dimensional scaffold still has lower mass
3,009,344 versus capacity 2,965,248: **excess 44,096 even when all new gauge and
tag work is free**. A chosen isolated correction on all 36,608 banks adds
146,432 primitive calls. Its excess would be 190,528 only if those primitives
were additionally admitted at one rank unit each in the same ledger. No such
admission is inferred here. Stop expansion of this unchanged scaffold.

## Evidence and reproduction

The only live scientific inputs are the three package-local source exports in
`source/`, pinned by origin commit, Git blob and SHA256 in [SOURCES.json](SOURCES.json).
Both checkers independently hardcode/authenticate the hashes. No predecessor
executable or unmerged foreign Git object is needed to replay this package.
The selected record/catalogue are historical base-commit provenance only.

From the repository root, with Python 3.12 and its standard library:

```sh
python3.12 -B scripts/research_package.py --package research/p104-phase-uniform-gauge --check-only
python3.12 -B scripts/research_package.py --package research/p104-phase-uniform-gauge
```

For a Git-free directory copy of this package, run `verify.py`, `independent.py`
and `test_verify.py` directly, with `-B`; repeat with `-O -B` to check assertion
independence. Explicit exceptions, rather than Python assertions, enforce the
scientific checks. The registered commands are in [VERIFY.json](VERIFY.json).

`verify.py` checks 104 labels, 10,816 product lines, 512 possible defect
characters, 81 tensor coefficients and 22,680 role/basis conditions. Polarization
extends those coefficient checks to all frequencies; no enumeration of 2^81
addresses is claimed. The separate checker uses binary RREF and 262,144 dot
pairs, checks a non-involutive gauge convention, and corroborates the operator
identities with four-bit literal matrices. Those small complex-matrix entries
and bounded fixtures are exactly representable dyadics; no numerical tolerance
accepts an equality. Its 585 three-bit words corroborate the written universal
four-call lower bound. `test_verify.py` runs 60 primary API/CLI rejection cases
and eight independent damaged-source rejections across normal/optimized Python,
plus a read-only Git-free positive fixture. These finite checks accompany the
written proofs; they are not a proof-assistant or full multiplication audit.

The source's isometry/full verifier, native-channel and selected cold replay
are not rerun. The theorem binds to the explicitly retained published labels
and conventions, without re-admitting the predecessor's physical hypotheses.

## Open next questions

The structured questions and blockers are in [TASK.json](TASK.json). This is a
**changed-scope** follow-up to the released PR3954 gauge question, not completion
of the catalogue's chronological correction program or the latest handoff's
missing adjacent physical producer/consumer pair.

Concurrent PR3961 studies the physical cross-axis encoding mismatch; PR3962
studies whole-fiber coverage and helper sharing. Their refreshed PR bodies
identify distinct contracts; this package does not claim to replay them or
remove those obstructions by changing address coordinates.

The consequential next step is one actual adjacent row/column pair: write its
all-role entrance, intermediate and exit encodings at a named chronological
cut, and reconcile the fiber-dependent tags `z tensor q_j` and `r_i tensor z`
on shared data and helper owners. The uniform completed-F lemma does not do
that. First require a changed complete invoice that clears the 44,096 deficit;
do not expand the rejected scaffold merely because its phase mismatch is fixed.

A physically viable changed contract would still need actual source frames,
R_K routing, native/binary-hyperplane orientation and global phase, compatible
tariffs, finite-width/signed-floor precision and recovery, physical dirty
return, owners/holding/control/tapes, opposite orientation, all-size transfer
and complete supplier admission. These obligations remain unknown or inherited.

## Credit and license

Chris R / Clear1nsight's PR3954 owns the retained P104 labels, two-axis setup,
operator conventions and conditional scaffold gate, following PR3882/3940/3943.
Retain the source README/PROOF attribution: 1337isnot1337 PR3894; Rohan Arun
PR1972; Chafik Boukhalfa PR1991; Adam Gall PR1940; Josie Elliston PR1071/E8;
Aurel Prosz/Paureel, Zhihao Chen, Dominik Scholz, icekylinx, Sagar Thakrar PR1012,
Douglas Colkitt, Jose Manuel and Vasek PR2744, plus the retained native,
compiler, coverage, terminal-floor and caller lineage. PR3943 owns its
960-addition adapter; this package does not reassign that construction.

The new explicit gauge, orthogonal-class character obstruction, completed-F
boundary and restricted translation tariff are by ToikY with substantial
OpenAI Codex assistance. Separate AI contexts implemented/reviewed the proof
checks and failure controls; this is not independent human or kernel review.
New work and retained source exports are under the repository's Apache-2.0
license. No merge or selected-frontier change is requested.
