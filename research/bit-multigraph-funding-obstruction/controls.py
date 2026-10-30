# SPDX-License-Identifier: Apache-2.0
"""Missing and typed-corrupt receipt tests in an isolated temporary directory."""
from pathlib import Path
import tempfile,sys,json,contextlib,io
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import verify
original=json.loads((HERE/'RESULT.json').read_text())
with tempfile.TemporaryDirectory(prefix='multigraph-receipt-') as tmp:
    p=Path(tmp);(p/'SOURCES.json').write_bytes((HERE/'SOURCES.json').read_bytes());verify.HERE=p
    for mode in ('missing','boolean-integer'):
        if mode!='missing':
            altered=dict(original);altered['new_kappa']=0;(p/'RESULT.json').write_text(json.dumps(altered))
        try:
            with contextlib.redirect_stdout(io.StringIO()):verify.main()
        except ValueError as e:
            wanted='required receipt missing' if mode=='missing' else 'typed exact receipt'
            verify.need(str(e)==wanted,'receipt rejected for wrong reason')
        else:raise ValueError('receipt fault accepted')
print('PASS_MULTIGRAPH_RECEIPT_CONTROLS missing=1 typed=1')
