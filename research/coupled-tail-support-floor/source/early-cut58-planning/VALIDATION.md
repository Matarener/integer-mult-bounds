# Validation

Commands, sequentially, in this owned directory:

- `python3 -B cut58.py --write` — PASS.
- `python3 -B cut58.py` — PASS exact saved receipt.
- `python3 -B -O cut58.py` — PASS identical optimized result.

Checks cover all six independent current input columns, both literal inverse
orders, source unary signed circuits/Gaussian phases, selected recipe pool
and physical embeddings in both directions, exact RP=-T and K=A identities,
commutation with freshT, the displayed full6x6 matrix, a rank-neutral simpler
network, both inverse orders for that network, native bill54+22=76, and the
omitted-source-reader/wrong-minus controls. No enumeration or optimizer ran.
The simpler network's complete selected-native serialized schema is not newly
admitted; this is explicitly planning-only. No background process remains.
