# Source adapter boundary

The adapter reuses the authenticated original Gaussian implementation and its
minimal original Python import closure: gaussian, full, generator, triangular,
engine and exact. The original intervals.py and source evaluator bytes are
supplied through the Gaussian class's raw mapping. It is not an independent
implementation of those routines.

A subclass intercepts exponential requests and delegates to the unchanged
original method. A temporary wrapper at the original exp_negative backend
entry also delegates unchanged, recording its actual input interval and the
source shortcut predicate `x.lo >= x.bits * x.scale`. Both wrappers restore
the original callable. Exact zero bypasses that backend. Thus the reported
11 shortcut, 141 nonshortcut and 34 exact-zero calls are actual observations,
not conclusions inferred merely from output shape.

Initial checks exercise f=0 returning exact one and the normalized scalar
fixture first. All nine saved fixtures then instantiate the actual Gaussian
class using their saved parameters and preserve automatic versus explicit
cutoff selection. They execute the actual retained Tsec function and its
astype(complex) method. Root/table hashes, conditioning boxes, scalar bit
allocations, coefficients and their receipts, cutoff/tail values, and finer
scalar references match the saved source receipt. In particular, both closed
half shifts, nonzero finite truncation and requested precisions 8 and 36 are
covered. Incoming precision 512 is passed to and retained by the constructor;
no 512-bit input-vector or online-grid execution is performed here.

The source compile, compile_root, Full constructor, admission and gate programs
are never called. The complete gate receipt is neither regenerated nor
accepted. The adapter recomputes the scalar coefficient/tail/error sums outside
compile_root and compares them with the saved scalar fields. This is frontend
coefficient preparation, not execution of the adjacent full-plan call.

QUERY.json contains only the actual factor/bits inputs, with no source interval
answers. Its first version was preserved before adding 15 explicit near-shortcut
or tiny-factor inputs. The independent oracle's implementation and proof were
frozen before it read either query version, and it did not see source outputs.
The adapter has read the certified result schema and output, not copied the
independent implementation. All 128 independent certified intervals are
contained in all 186 actual source interval observations. Forty-three retained
quantization receipts and all 61 finite offsets are checked, including positive
omitted-tail lower bounds. Each actual qbar reciprocal uses the source's
positive conditioning lower bound and is independently enclosed.

Three deliberately faulty source paths calibrate semantic rejection. Temporary
dependency patches, restored in finally blocks, omit pi, forge a zero
quantization error while retaining the actual quantized value, or make every
tail zero so automatic truncation chooses W=0. Actual original scalar/Tsec
methods are called. Independent certificates reject a disjoint exponential
interval, a demonstrably nonzero coefficient error, and a certified positive
dropped finite coefficient. These are constructed controls, not defects found
in the predecessor. No mutant constructs Full or runs gates.

The conclusion is finite and pinned. The independent enclosure algorithm and
written proofs retain their mathematical review obligations; this adapter does
not certify the predecessor's all-size width estimate, universal Gaussian
conditioning, all infinite tail formulas, raw gauges, circuit correctness,
physical delivery, proof-kernel acceptance or a new kappa. Component and
canonical JSON hashes are named explicitly; canonical-object hashes differ
from indented JSON file-byte hashes.

Default execution compares the complete computed typed JSON object against
INTEGRATION-RESULT.json and the complete canonical scalar capture against
SOURCE-CAPTURE.json. An integer zero substituted for the stored Boolean false
is rejected. --expected and --capture-expected permit explicit alternate input
paths. --output is explicit receipt regeneration and bypasses stored-receipt
equality; default execution writes no files. Isolated normal and optimized
warning-as-error executions pass and print bytes identical to the stored
integration receipt.

Credit Jose Manuel and substantial OpenAI assistance for the normalized
Gaussian caller and circuits, Mason Hale for the retained interval backend,
Jeremy Kothe/IdeaOuter for Tsec, and Vlado Vojdanovski and the retained
q-LDU/circuit lineage. The adapter was prepared with OpenAI Codex assistance.
