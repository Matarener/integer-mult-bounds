# Rounded-error admission for the complete P104 gauge word

The exact PR5830 public/private gauge word has a **sharp 20-bit final-output
guard** under the stated completed-operation relative-error contract. A finite
causal calculation gives final error below0.978B at u=2^-20 and intermediate
error below27B. With t additional bits, final error is below B*2^-t for all t>=0.
The ideal field norm plus error stays below2^17 B. B bounds each initial field's
Hilbert norm; this is not a dimension-free input-coordinate bit bound.

A direct uniform calculation gives25 guard bits for all prefixes and21 for
final public fields. The normalized gauge calculation gives26 and23. The new
causal bound retains signed cancellation and accounts for actual prior defects
at each site. It needs no global stability denominator. Its96-bit upward grid
is exact checker arithmetic, not a physical precision assumption. An admissible actual-input defect trace at 19 bits gives final error above
1.79B. Thus 20 is the least integer guard for this worst-case contract. A second
trace uses only native MOVE and ADD defects and gives error above 1.70B. Its
allowances and final error survive every field-constant signed scalar gauge of
the same word. Pure representation changes cannot remove this obstruction.
This is not a lower bound for a hardware rounding rule with stronger error
correlations. Both traces also pass with 32 extra bits and their scaled targets.

The covariance theorem explains how each homogeneous local allowance transforms
under a signed scalar gauge. The reference timeline retains all384 entry and399
exit conversions as noisy normalized identities. All395 omitted physical SCALEs
remain exact normalized transitions. The actual26,351 instructions are recovered
exactly after deleting those virtual identities. See [PROOF.md](PROOF.md).

The checker binds the source graph/word, full local invoice, frames and ownership;
replays all782 arbitrary input columns; compares every normalized prefix score,
all final signed error coefficients and witnesses; checks a separate physical
transpose; and executes an attaining normalized-defect fixture. Eight rejection
controls, over-budget defect controls, literal transport of both family witnesses,
and 36 independent exact rational causal-oracle checks pass. Exact
coefficients, source pins, guard certificates and limits are in `RESULT.json`.

Run `python3 -B scripts/research_package.py --package research/p104-gauge-error-covariance`.
The standalone command is `python3 -B research/p104-gauge-error-covariance/verify.py`.
Python3.12 and the standard library suffice. The registered replay, source
corruption, committed bytes/modes and read-only Git-free optimized checks are
separate from physical or scientific admission.

COPY, including its coefficient, INIT and CLEAR are exact premises here. Native
maps and gauges must be unitary before each completed defect. A rounded child,
exact reset/COPY implementation, final compiler and fixed-tape execution are not
supplied. The source's five assumptions and selected frontier retain their
status. No new kappa or optimal physical precision is claimed.

## Open next questions

- Bind an actual completed child and exact COPY/reset machine to these allowances,
  including all signed-record range and tape costs.
- Recompute the bound for a later gauge tradeoff word. Site presence and boundary
  conversions affect error; source names alone do not transfer guards.
- Prove a less conservative local error set if physical rounding correlations
  permit one. This package permits independently adverse completed defects.

The norm/cost optimization remains with the owner of Discussion5804. This
package neither searches for another gauge nor claims their optimum again.
Source PR5830 head dd3ffe4c1b391b8d757969a9aa9b2f7c02a32117 is frozen here.
Credit PR5830/5824/5822/5812, PR5819/5826/5831, Adam Gall, ywz65, PR2878 and
all retained P104/native/compiler authors in inputs/NOTICE. New proof and checks
by Ali Romman with substantial OpenAI Codex assistance; no subagents.
Apache-2.0. Independent scientific acceptance remains open.

The source manifest pins replay inputs to copies in this publication history.
Its `retained_predecessors` records keep each original head, path, blob and
SHA256, plus its exact retained file or archive member. Each source was checked
byte-for-byte before this rebind. This removes an unavailable side-commit
dependency from clean CI; no source bytes or scientific checks are changed.
