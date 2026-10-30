# Source binding and execution boundary

This is a source-reusing integration adapter. It reads the eight unchanged
PR4211 exports pinned at ca0002008b497428f0b651501c4a220a9d2785e7. Its packed
address arithmetic, normalized paid update and full regular-action checker are
the actual predecessor implementations. It does not claim independent authorship
of those implementations or of the predecessor's normalization argument.

The raw scalar interleaver is newly written adapter code. The source implements
normalized paid steps only; it has no raw scalar-interleaved circuit to execute.
The adapter applies free scalar matrices to role rows, preserves each paid
coordinate/address call in chronological order, and checks Raw = Pn Fn...F1
using the original paid-step implementation. Scalar role mixing is distinguished
from a group-algebra address monomial throughout.

All 504 literal P^-1 E_r P conjugacies are computed with both original packed
and original row-tuple matrix arithmetic. Their inverse/u/v/projector rows equal
the independently frozen complete oracle table; the canonical triple digest is
computed from literal rows, not accepted merely from oracle metadata. Every one
of the 504 independent converse-basis witnesses is checked against actual source
arithmetic. The fibers contain 18 witnesses for each of 28 projectors.

To bind the second implementation's selector admission, the adapter extracts
only its unique actual cnf.add(cnf.xors(cnf.both(u[k],v[k])...)) expression and
executes that unchanged expression using the original CNF helper methods.
Exhaustive 64-pair scalar assignments admit exactly the expected 28 pairs. The
actual six source PAIRS constants and the packed source's full 168-factor set
then agree with those pairs. This is **not** a build() execution, complete
one-hot-label check, transition/endpoint/Tseitin equivalence audit, SAT call,
UNSAT claim or RUP replay. No support-pruning result is claimed here.

Each of the 168 one-factor normalized source gates is realized by an adapter
raw word using a basis [u,ker(v)] and identity terminal free frame. The resulting
source formal endpoint, exact normalized gate chronology and paid count agree;
all 168 actual normalized factors also augment to identity. The unchanged
DIRECT_NINE witness is replayed on the predecessor's full 3*168 regular basis
inputs. Its raw realization normalizes back to exactly the same nine gates and
attains the same full source group-algebra endpoint, including arbitrary dirty
third-input dependencies.

After the independent oracle's code/proof/table were frozen before source
access, its actual free-word normalizer and symbolic evaluator were bound to
the direct-nine realization and three adapter raw examples, including n=0 with
a nonidentity residual. Its separate converse compiler also realizes the
direct-nine endpoint through actual source paid steps. Free symbolic addresses
are evaluated in the actual source GL3 address group with word order preserved.
The adapter's paid calls use only the six source labels; the independent core's
generic identity-address diagnostic is not treated as an allowed source call.

Five constructed controls detect replacing an order-three frame's inverse by
itself, reversing conjugacy orientation, dropping a nonidentity terminal frame,
confusing scalar role mixing with an address action, and reversing two
noncommuting source address calls. They are countercontrols, not defects found
in the predecessor. Their exact row/mask/endpoint witnesses are retained in
INTEGRATION-RESULT.json and duplicated in MUTATIONS.json.

Default execution compares the complete computed typed integration receipt and
complete retained source table using canonical JSON. Integer/Boolean changes
remain distinguishable. --output is explicit receipt regeneration, while
--table-output explicitly writes the computed table. Ordinary default execution
writes no files. Independent oracle files retain their original names; the
source directory is resolved relative to this script and added explicitly to
the authenticated import path, including in isolated mode.

This finite binding corroborates the separate all-n normalization proof in the
declared fixed scalar-linear grammar. It does not enlarge that grammar, certify
adaptive or nonlinear free operations, price free scalar work physically,
certify minimum nine, run SAT/RUP, establish a supplier/multiplication theorem,
provide independent human/formal-kernel acceptance or improve kappa. The known
direct-nine construction is predecessor credit, not a new upper bound.

Credit Brian Ross and substantial OpenAI Codex assistance for the original model
and normalization argument, Hanson Sun's seed18 work, Josie Elliston's length10
and three-register work, and retained licenses/notices. The new integration and
independent-oracle contributions use substantial OpenAI Codex assistance;
classical conjugation and augmentation are not claimed new general mathematics.
