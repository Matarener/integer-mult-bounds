# Legal common-cut insertions: support check only

This supplement is separate from `FINAL-FREEZE.json` and does not modify
any previously frozen artifact. It checks the insertion alphabet in the
algebra lane's noncommon intermediate B1 investigation. It proves no B1
endpoint rank improvement or general endpoint obstruction.

At a current cut write

    DX=C_p G_past, DY=C_q G_past, K=C_q C_p^-1.

For a physical monomial M such that K M K^-1 is monomial, the logical
insertion H=DX^-1 M DX is admitted on both banks: its X pullback is M and
its Y pullback is K M K^-1. These are exact Clifford products; native rank
zero is not inferred merely from a binary subspace.

`insertion_supplement.py` uses two common axes p,q, one completed past
fresh axis u and one future fresh axis v. It gives two explicit checks:

* On the common plane, choose address matrix A=[[0,1],[1,1]] and quadratic
  chirp Q=[[1,1],[1,0]]. The address has order three. The actual monomial
  `diag(Q) perm(A)` and its K conjugate both have native rank zero, including
  phase. Removing Q makes that conjugate have positive native rank.
  Thus legal common-axis mixing need not be an orthogonal permutation.
* Let G_past=C_u and let M exchange physical fresh axes u,v. Its dressed
  logical H has native-zero pullbacks at both DX and DY. In phase-space
  coordinates it sends the completed-past vector (x,z)=(u,u) to the
  future vector (0,v). If one instead uses the undressed logical ADDRESS
  swap at that cut, its pullback has native rank two.

The second example is relevant to a proposed all-size bottleneck proof.
The two cut Lagrangians share an intersection W of dimension m-2. A legal
simultaneous insertion preserves W, but W contains both completed-past
F^-1Z directions and uncompleted-future Z directions. It need not preserve
these two summands individually. The example explicitly transfers between
them. Hence leakage into a past fresh block is not automatically absorbing:
a subsequent legal insertion may place it into a future local factor.
The earlier common-corner product proof, which used disjoint fresh support
and no such inserted mixing, cannot be extended using W-invariance alone.

This does not show that the particular D4 OPEN local factors can exploit
that transfer to increase Y's rank while preserving X's. A further
quadrature or whole-word invariant may still exist. The algebra lane's
finite address/chirp searches remain finite evidence, with no promotion to
an all-parameter obstruction here.

All examples are exact Gaussian Clifford identities and tensor columnwise
over every chunk parameter. They also embed into larger orthogonal fresh
blocks by identity on the unused directions. Native-zero maps still incur
their actual whole-array address/phase scan costs. There is no hidden
native child in the correctly dressed examples, and the ordinary/private
helper count for these insertions is zero.
