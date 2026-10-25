#!/usr/bin/env python3
"""A 24-decimal packing ceiling for the new receiver-sharing word.

The idle inventory is unchanged, but the local paid bill is smaller. Recheck
the credited PR3815 pattern basis at the new exact upper endpoint; a successful
dual bounds every clock and replica count for this new fixed supplier.
Apache-2.0; substantial OpenAI Codex assistance under the user's direction.
"""
from collections import Counter
from fractions import Fraction as F
from pathlib import Path
import importlib.util
import json
from packing_certificate import certify

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]


def main():
    inv_path = REPO/'research/kappa-global-continuation/invoice-analysis/invoice.py'
    spec = importlib.util.spec_from_file_location('receiver_ceiling_invoice', inv_path)
    I = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(I)
    invoice_path = HERE/'receiver-sharing/RESULT.json'
    invoice = I.read(invoice_path)
    I.need(invoice['status'] == 'PASS_LITERAL_CHANGED_NATIVE_OWNERS_AND_TWO_ENGINE_INVOICE', 'actual new supplier allocation')
    I.need(invoice['script_sha256'] == I.digest(HERE/'native_owner_invoice.py'), 'physical invoice source pin')
    for paths in invoice['supplied_native_inputs'].values():
        for rel, expected in paths.items():
            I.need(I.digest(REPO/rel) == expected, 'actual native input binding')
    local = {int(r): n for r, n in invoice['provider_local_profiles']['gauge44'].items()}
    I.need(local == {int(r): n for r, n in invoice['provider_local_profiles']['extra'].items()}, 'same paid bill for both providers')
    package = HERE.parent/'sources/PR3815/research/staged544-clock-ceiling'
    C = I.module(package/'ceiling_certificate.py', 'receiver_ceiling_basis')
    geometry = I.read(package.parent/'staged544-producer-return/inputs/TEMPLATE.json.gz')
    bins = Counter(child['rank'] for child in geometry['idle_children'])
    common = dict(dimension=73, productive=896, calls=9, local=local, bins=bins,
                  supply={4: 26, 5: 2, 6: 18, 7: 53, 8: 96, 9: 213}, basis=C.BASIS)
    low, high = map(F, invoice['root']['rational'])
    upper = certify(I, endpoint=high, **common)
    lower = certify(I, endpoint=low, **common)
    I.need(upper['patterns_checked'] == 2551 and upper['strictly_excludes_endpoint'], 'global new-word packing ceiling')
    I.need(not lower['strictly_excludes_endpoint'], 'lower endpoint control')
    bad = certify(I, endpoint=high, perturb_width9=F(1, 10**30), **common)
    I.need(not bad['dual_feasible'], 'dual perturbation control')
    result = {'status': 'PASS_NEW_NATIVE_FIXED_INVENTORY_CEILING_TO_24_DECIMALS',
              'script_sha256': I.digest(Path(__file__)), 'physical_invoice_sha256': I.digest(invoice_path),
              'exact_dual_implementation_sha256': I.digest(HERE/'packing_certificate.py'),
              'upstream_basis_source_sha256': I.digest(package/'ceiling_certificate.py'),
              'root': invoice['root'], 'new_local_profile': local, 'upper_dual': upper,
              'certified_gap_between_attained_lower_and_global_upper': str(high-low),
              'controls': ['root_lower_not_excluded', 'width9_perturbation_rejected'],
              'scope': ('The actual receiver-sharing native word and inherited PR3815 fill have '
                        'a root strictly above the lower endpoint. Every packing in this fixed '
                        'local profile, helper inventory, idle template and one-remainder-per-bin '
                        'model is strictly excluded at the adjacent upper endpoint. Therefore '
                        'the attained root and the all-clock ceiling agree to 24 decimal places; '
                        'this receipt does not prove equality of unrounded transcendental optima. Every '
                        'clock, replica count and owner rearrangement in that model is covered. '
                        'Changed native words, bins or payment rules remain outside this ceiling. '
                        'The complete conditional multiplication release is a separate gate.')}
    (HERE/'RECEIVER-PACKING-CEILING.json').write_text(json.dumps(result, indent=2)+'\n')
    print(result['status'], invoice['root']['decimal'])


if __name__ == '__main__':
    main()
