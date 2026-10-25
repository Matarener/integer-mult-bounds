# B11 independent proof audit

Verdict: **the all-subset partition proof is valid under the explicit fixed
model.** Complete, correctly rebound partitions suffice to establish the
273-plane statement. No proof repair is required. The independent numerical
verification of all masks and partition predicates belongs to the other
reviewer; this audit does not claim to have repeated that replay.
Substantial OpenAI Codex assistance; Apache-2.0.

The reviewed source is `SELECTIVE-UNIONS.md` and its partition, batch,
propagation and checker implementations in the changed-endpoints lane, with
scientific pin `20ecf2891d80b5acf18d980b2164fb44ea7faa90`. Exact SHA256 pins and
the lightweight structural checks are in `SOURCE-AND-MODEL.json`. Original
files were not modified. Relevant helper-boundary and observation-kernel
premises were retained.

The principal derivation is in `PROOF-PARTITION.md`: restrict each independent
color class to a chosen helper subset S, bound it by rank(D_S), restrict each
resource class to S, and count its at-most-eight members. Disjoint ownership
and complete coverage give r|S|<=r rank(D_S)+8 exposure_E(S). This holds for
every S without enumerating subsets or trusting augmenting-path termination.
For the lambda-8 receipts, g=0 and S=empty already supplies the matching lower
bound zero. “All-subset” is justified; “all-plane” is not.

The actual source geometry contains 120 distinct full E8 root lines and 153
distinct rank-two R438 frame spans. All source terminal frames are FULL;
all target caps and all nine original copied-total source cuts have rank
seven. The A phase has no target incidence, and the explicit old-word phase
ordering puts all copied scatters before B. These facts justify the rank-one
target/COPY exposure interpretation and the separation of fixed ZERO private
scatters from helper-seed promotion. The lightweight check did not regenerate
all 273 causal masks.

The forward Boolean process is particular to the prescribed common-frame
join algorithm: at a below-E ADD, either promoted actor forces both to the
join; reaching an old frame containing E ends the distinction. COPY/private
scatters stay at ZERO and do not transmit promotion. Initial compensation is
excluded because it occurs before the prospective helper-basis setup. Its
semantic D is still the full old helper-to-target matrix over F2. There is no
cold-row quotient in the theorem. Source-path changes are allowed but are
not among the 120 exposure resources.

The historical `verify_union_partition.py` is independent of augmentation
code, but it imports the original propagation and semantic-binding helpers.
That is a narrower independence claim than a fresh reconstruction of D and
the Boolean chronology. The other reviewer's new checker owns that stronger
computational obligation. Source-byte checks must cover the transitive raw
word, geometry, old-word compiler and propagation inputs, not just a receipt's
top-level hash fields. The general proof remains independent of how the
certificate was constructed.

Publication should retain four boundaries prominently:

- The 273 planes are a complete specified finite family, while S ranges over
  every subset of the fixed 438 helpers. Neither arbitrary rational planes
  nor all input sizes are covered.
- The coefficient 8 is an auxiliary weight, not each exposure's physical
  tariff. Even a zero weighted optimum does not reject a rank-mass saving,
  determine stock credit or imply a complete moment/rate inequality.
- The copied private field remains ZERO. The global-E private-at-E caller
  from B10 has different COPY costs and is not an instance of this model.
- Full D kernels, one E, fixed chronology and scalar binary coefficients are
  essential. Cold-row quotients, mixed planes sharing resources, operator
  kernels, retiming or new private/readout contracts need new certificates.

The proof document includes explicit abstract countermodels for transferring
the inequality to a cold-row quotient or combining independent plane bounds
under shared exposure. They do not contradict the original fixed fixture;
they identify why those extensions cannot be inferred from it.

The saved batches have the expected 120/153 run counts, common weight eight,
438/876 colored-node counts, zero claimed unassigned nodes, and empty selected
cuts. This metadata read is not substituted for checking all actual rank,
incidence, capacity, ownership and complement predicates. Upon the independent
computational review passing those predicates and source bindings, the finite
receipts plus the written counting lemma establish the requested all-subset
inequality. No native construction, owner, precision/tape or kappa claim is
approved by this proof audit.
