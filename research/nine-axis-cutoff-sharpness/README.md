# Sharp nine-axis native test window 21–24

The fixed affine-quadratic monomial grammar has sharp nine-axis tensor
cutoff 21 and residue thresholds (24,21,22,23). The same proof gives sharp
cutoff 2n+3 for every n>=5 with n=1 modulo four. Four matching residue tests
are necessary. PROOF.md contains the complete argument and citations.
No physical paid profile or kappa changes.

A doubly-even code obstruction rules out short zero-phase full-span tuples.
A genuine cuspidal character gives an affine cancellation element, which
turns that absence into a nonzero representation-kernel witness. Explicit
E8 code blocks give the first visible tuple. This closes the distinction
between a character-realization bound and representation sharpness.

Run `python3 -B scripts/research_package.py --package research/nine-axis-cutoff-sharpness`.
Python 3.12 and the standard library suffice. RESULT.json records exact
code, Gauss-sum, coset, constructor and corruption controls.

## Sources and credit

SOURCES.json pins PR5529's upper proof and constructor and Joseph Anglada's
PR5542 three-axis proof. PROOF.md cites Green's character theorem and its
explicit formulation in Prasad's published paper. Credit PR5369, PR5522,
PR5521, PR5622 and the retained native/phase contributors. The code and
character theory are classical; this application and proof are the new work.

## Open next questions

Other axis-count residues need separate sharpness arguments. An efficient
way to apply the cutoff to large straight-line programs is still needed;
this proof does not expand GL(9,2) or the diagonal phase group. Actual
native callers need exact source bindings, all returned fields and a full
paid bill. No human or formal-kernel acceptance is claimed.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
