#!/usr/bin/env python3
"""Exact clock-independent price ceiling for the literal seven-call geometry.

No scipy is used. The nine-pattern primal was nominated by an unrestricted
LP; the rational equations, every dual inequality and root signs are checked
here. This rules out this fixed inventory, including asynchronous clocks.
Apache-2.0; substantial OpenAI Codex assistance under the user's direction.
"""
from collections import Counter
from fractions import Fraction as F
from pathlib import Path
import importlib.util
import json
from packing_certificate import WIDTHS, certify

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]

PRIMAL = [
    (8, (0, 0, 0, 0, 1, 0), F(448)),
    (16, (0, 0, 0, 0, 2, 0), F(175, 3)),
    (16, (0, 0, 0, 1, 0, 1), F(371)),
    (16, (0, 0, 1, 0, 0, 1), F(56, 3)),
    (32, (0, 0, 0, 0, 0, 0), F(406, 9)),
    (32, (0, 0, 0, 0, 0, 3), F(896, 9)),
    (32, (0, 0, 1, 0, 1, 2), F(322, 3)),
    (32, (0, 1, 0, 0, 0, 3), F(14)),
    (32, (1, 0, 0, 0, 0, 3), F(182)),
]


def main():
    path = REPO/'research/kappa-global-continuation/invoice-analysis/invoice.py'
    spec = importlib.util.spec_from_file_location('p3_exact_invoice', path)
    I = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(I)
    geometry_path = HERE.parent/'architecture/evidence/SEVEN57-GEOMETRY.json.gz'
    geometry = I.read(geometry_path)
    bins = Counter(child['rank'] for child in geometry['idle_children'])
    supply = Counter(geometry['helper_widths'])
    local = {int(r): n for r, n in geometry['local_profile'].items()}
    calls = sum(event['kind'] == 'local' for event in geometry['schedule'])
    dimension = geometry['dimension']
    productive = 2*geometry['ports']*geometry['pairs']
    I.need((dimension, productive, calls) == (57, 672, 7), 'literal p3 dimensions')
    I.need(bins == {8: 448, 16: 448, 32: 448}, 'literal idle child rank census')
    I.need(supply == {4: 26, 5: 2, 6: 18, 7: 53, 8: 96, 9: 213}, 'native helper census')
    I.need(local == I.LOCAL, 'unchanged native complete local bill')
    bin_used, helper_used, idle = Counter(), Counter(), Counter()
    for cap, pattern, count in PRIMAL:
        I.need(count >= 0, 'nonnegative fractional primal')
        rem = cap-sum(w*n for w, n in zip(WIDTHS, pattern))
        I.need(rem >= 0, 'finite bin capacity')
        bin_used[cap] += count
        for w, n in zip(WIDTHS, pattern):
            helper_used[w] += n*count
        if rem:
            idle[rem] += count
    I.need(bin_used == bins, 'every aggregate bin equation')
    I.need(helper_used == {w: calls*n for w, n in supply.items()}, 'every aggregate helper equation')
    I.need(idle == {1: F(602, 3), 5: F(896, 9), 32: F(406, 9)}, 'aggregate ideal remainder profile')
    profile = Counter({r: calls*n for r, n in local.items()})
    profile.update(idle)
    I.need(sum(r*n for r, n in profile.items()) == 38080, 'complete raw rank mass')
    root = I.root(profile, dimension, productive)
    common = dict(dimension=dimension, productive=productive, calls=calls, local=local,
                  bins=bins, supply=supply, basis=[(c, p) for c, p, _ in PRIMAL])
    points = {'root_lower': F(root['rational'][0]), 'root_upper': F(root['rational'][1]),
              'attached_actual': I.BASE_ROOT, 'target': I.TARGET, 'bit_cap': I.BIT_ROOT}
    certificates = {name: certify(I, endpoint=a, **common) for name, a in points.items()}
    for name in ('root_upper', 'attached_actual', 'target', 'bit_cap'):
        I.need(certificates[name]['strictly_excludes_endpoint'], 'exact dual excludes '+name)
    I.need(not certificates['root_lower']['strictly_excludes_endpoint'], 'root-lower control')
    control = certify(I, endpoint=points['root_upper'], perturb_width9=F(1, 10**30), **common)
    I.need(not control['dual_feasible'], 'perturbed dual is rejected')
    sources = [Path(__file__), Path(__file__).with_name('packing_certificate.py'), path,
               I.ENGINE_PATH, geometry_path, HERE.parent/'architecture/seven_geometry.py']
    result = {
        'status': 'PASS_EXACT_CLOCK_INDEPENDENT_P3_PACKING_CEILING',
        'input_sha256': {str(p.relative_to(REPO)): I.digest(p) for p in sources},
        'dimension': dimension, 'productive_per_replica': productive, 'calls_per_replica': calls,
        'bins_per_replica': dict(bins), 'helpers_per_call': dict(supply),
        'raw_rank_mass_per_replica': 38080, 'raw_deficit_per_replica': 224,
        'fractional_primal': [{'rank': c, 'pattern': p, 'count': str(n)} for c, p, n in PRIMAL],
        'idle_profile': {str(r): str(n) for r, n in idle.items()},
        'root': root, 'dual_certificates': certificates,
        'controls': ['root_lower_does_not_clear', 'width9_dual_perturbation_rejected'],
        'scope': ('For the authenticated seven-call native supplier and twelve-window geometry, '
                  'every packing, at every replica count and under every clock, has its root '
                  'below the stated upper endpoint. The dual drops all chronological and '
                  'per-call uniqueness constraints, so they cannot evade this ceiling. '
                  'The fractional primal is an aggregate pattern packing, not a physical '
                  'owner allocation. Added external banks or changed local words are different inventories.')
    }
    (HERE/'P3-CEILING.json').write_text(json.dumps(result, indent=2)+'\n')
    print(result['status'], 'root', root['decimal'], 'patterns', certificates['root_upper']['patterns_checked'])


if __name__ == '__main__':
    main()
