"""Deterministic cold-cache workload from the selected caller's invoice."""
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
import json

HERE = Path(__file__).resolve().parent
INVOICE_SHA256 = 'b86b86f840e27acf1c56ae43a0b779f9708ec04c3ccaf3061d9034ed6288c401'


def profiles():
    raw = (HERE / 'inputs/invoice.json').read_bytes()
    if sha256(raw).hexdigest() != INVOICE_SHA256:
        raise ValueError('frozen invoice changed')
    data = json.loads(raw)
    return [{int(r): n for r, n in data[key].items()} for key in ('paid', 'productive')]


def run(engine):
    paid, targets = profiles()
    ranks = sorted(set(paid) | set(targets))
    rows = []
    for j in range(12):
        exponent = F(9969727117 + j, 10**10)
        powers = {r: engine.power(r, exponent) for r in ranks}
        margin = engine.minus(engine.moment(targets, exponent), engine.moment(paid, exponent))
        allowance = engine.homogeneous_limit((F(1000), F(1001)), 145, exponent)
        rows.append({'exponent': exponent, 'powers': powers,
                     'margin': margin, 'allowance': allowance})
    return engine.encode(rows)


def digest(result):
    return sha256(json.dumps(result, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
