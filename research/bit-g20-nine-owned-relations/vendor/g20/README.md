# Private G20/G23 native candidate

This packet materializes the one genuine shadow-assisted retiming window
already certified in G20/G22/G23. It is a private restart point, not a new
ordinary BIT exponent, whole-kappa result, or publication candidate.

Cold replay, from any working directory (standard Python 3.12 or later):

```powershell
python -I -B provider/verify.py --provider <absolute-path-to-provider> --output <fresh-output-directory>
python -I -O -B provider/verify.py --provider <absolute-path-to-provider> --output <another-fresh-output-directory>
```

The script uses only the standard library and local byte-pinned files.
`INPUT-PINS.json` records origins for attribution; runtime verification never
follows those paths. `provider/MANIFEST.json` pins all runtime code, input
bytes and generated native data. No network, Git checkout or old cache is
needed. Rebuilding generated files is not part of verification.

The literal 446,436-event global stream is `provider/data/GLOBAL.jsonl.gz`.
Its decompressed SHA-256 is
`0cb03eb11c2d8f511d495f3767e55e48156ed31094697d4e58a82f15be33c203`,
exactly the former G23 digest. Each of the 57,321 paid queries has a fresh
current-function descriptor in `SOURCE-DESCRIPTORS.jsonl.gz`.

The 18 local calls use 658 arbitrary original functions each, with fresh
helper owners. The global original count remains 11,400. Two owned whole
arrays are allocated per live compiled unit and returned to zero; neither
receives independent-input or productive-output credit. The raw profile has
18 fewer query occurrences than the frozen partial436 baseline, with the
same rank mass and target profile. The local proper-rank request remains
at most 7; the new rank-4 request is explicitly normalized rather than
inheriting the old rank-3 ticket.

`PROOF.md` explains the function/coframe argument, inverse and rawdual.
`provider/data/FULL-FEES.json` counts the new scans, copies, clears,
whole-fiber routes, conservative parent parking and owned reserve. The
normalizer and ROW costs are positive fixed-program costs, not free rank
admission. In particular, the old raw-record cap of 1e9 is not asserted to
bound all new parking/normalizer passes.

The historical raw root is approximately .003476110419631239, a
.01877034747% improvement over the same raw baseline. It is below the
.1% publication guard and is not an ordinary saving. The new three-tail,
finite-compiler, prime-fallback and finite-bootstrap certificate is a
separate pending gate. Frozen PR4760/PR4814 inputs are unchanged.
