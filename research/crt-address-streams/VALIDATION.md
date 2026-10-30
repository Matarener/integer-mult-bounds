# Author replay receipts

Base: `20ecf2891d80b5acf18d980b2164fb44ea7faa90`.
Scientific code freeze: `bfa957212107a9c772ce9ca3f96dade8efdbe988`.
External cohort: PR3935, `240597ed313fc2854c0462b23c89dc3bae72aaf5`;
all eight files have size, SHA256 and Git blob pins in NETWORK-SOURCES.json.
Python: CPython 3.12.14, Linux. No scientific input or predecessor was changed.

Passed the direct cold replay using the authenticated offline source tree:

```sh
python3.12 -B research/crt-address-streams/verify.py --source-root /path/to/dependencies
```

Result: `PASS_CRT_ADDRESS_STREAMS {"columns": 138, "controls": 20,
"inverse_cases": 2176, "wrapper_peak": 39}`. EXPECTED.json is the complete
replay receipt, including the actual typed TensorPlan and finite domains.

The committed scientific export passed the repository's export integrity check.
The same replay passed with `-O -B`, an empty executable PATH, no Git repository,
a read-only package/dependency tree, and a deliberate unpinned `crt_shape.py`
import-shadow trap in the dependency tree. All 33 frozen files, including the
trap and unrelated cached predecessor bytecode, were unchanged afterward.
This checks the source isolation as well as the finite numerical obligations.

The ready registered command uses `--fetch` and independently authenticates the
same source bytes. Fresh local network attempts encountered a truncated large
response and TLS handshake timeouts before completing the source download.
They did **not** reach or fail a mathematical check. The bounded range downloader
retains exact per-range checks, complete hashes and failure propagation. Hosted
CI transport/replay status must be read separately; it is not asserted here.
An authenticated offline source-tree replay is supported for this reason.

The metadata/pin check passed. No repository-wide historical suite was needed:
this isolated package changes neither shared runtime nor selected construction.
Finite certificates and the scoped argument do not prove the inherited universal
router/native premises or the complete integer multiplication theorem.
