# Explicit source-custody revision acknowledgement before freeze

The first static attempt to assemble this new5580 request stopped on a
source-byte mismatch. No REQUEST.json had been created and no scientific
code was imported or executed. The inherited/historical eaf2ff request,
old source proof snapshots and existing Astra transfer were not changed.

The curator had replaced a shared derived-pretty PR5580-RESULT.json with
the exact captured author text after downstream hashes had been shared.
The two representations parse to identical JSON. Root explicitly required
preserving both versions and the drift record. Under that authority the
curator restored the original convenience path and added a separate raw
file with a custody revision manifest:

- PR5580-RESULT.json: original derived serialization SHA256
  `7962660bd5780b518be592aa7413e5534f50420e22ec6d27516c7ce409129a3c`.
- PR5580-RESULT-raw.json: exact author serialization SHA256
  `aab659f8cfed61fb5e2dca1f5bff1cdd7a493733a4b36d5433d7c332c5ccf78c`,
  Git blob `9eca7f2d6c2f09886ccd57a32fed8462bb539aa6`.
- custody-revisions/20261025T204435Z/CUSTODY-REVISION.json: SHA256
  `efe80b15d50743be5a2e0934bfb831f2eda7fde00a1362eba33d191a4089719f`.

This new request explicitly binds both immutable serializations and the
revision manifest. Its checker must join both representations to the exact
captured author bytes and verify their parsed-data equality. The prior
TRANSFER-ARITHMETIC.json remains byte-exact at ce501298... with its original
7962660... pin. No mathematical input, source head, word, cost coefficient,
target, controller law or numerical interval changed in this custody step.

This acknowledgement is not a successful scientific receipt, a silent
source-pin repair, or permission to replay a historical generation. The
new root-only5580 qualification remains unexecuted at preparation.
