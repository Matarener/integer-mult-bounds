"""Binding, inventory mutation and exception-scope controls."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import patch

import bindings
bindings.activate()
import boundary_checks
import exchange
import ordinary
from records import Tape
from words import need


def run():
    count=boundary_checks.controls()
    original=exchange.exchange
    def broken(owner,lease):
        old=lease.pool.tapes
        original(owner,lease)
        lease.pool.tapes=old
    with patch.object(exchange,'exchange',broken):
        boundary_checks.rejects(lambda:boundary_checks.one([0,1,0,1],True),'fixed role permutation')
    before=ordinary.transfer
    try:
        with exchange.publication(SimpleNamespace(output=Tape())):
            raise RuntimeError('deliberate scope exit')
    except RuntimeError:pass
    need(ordinary.transfer is before,'publication hook restored on failure')
    row=next(r for r in json.loads((bindings.HERE/'SOURCES.json').read_text())['files'] if r['usage']=='input')
    with TemporaryDirectory() as td:
        path=Path(td)/row['path'];path.parent.mkdir(parents=True)
        path.write_bytes((bindings.ROOT/row['path']).read_bytes()+b'\n')
        boundary_checks.rejects(lambda:bindings.authenticate(Path(td)),'source changed')
    return dict(boundary_controls=count,inventory_mutant=1,exception_scope=1,source_corruption=1)
