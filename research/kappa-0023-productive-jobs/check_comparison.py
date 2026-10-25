#!/usr/bin/env python3
"""Challenge metadata normalization on actual fresh scientific artifacts.

Uses an already completed temporary replay. Each mutation is restored in a
finally block; frozen source files are never modified. Apache-2.0; Codex-assisted.
"""
import argparse
import gzip
import json
from pathlib import Path
import verify as V


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, required=True)
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    root = args.repo.resolve()
    V.need(root.is_dir() and not root.is_relative_to(V.ROOT), 'Use the separate temporary replay')
    V.need(not args.report.resolve().is_relative_to(V.ROOT), 'Write control receipt outside source tree')
    outputs = set()
    for stage in V.load_stages():
        for pattern in stage['outputs']:
            found = [p for p in (root / V.SCOPE).glob(pattern) if p.is_file()]
            V.need(found, 'Complete replay output: ' + pattern)
            outputs.update(p.relative_to(root).as_posix() for p in found)
    V.need(len(outputs) == 59, 'All 59 outputs present')
    V.compare_outputs(root, outputs)
    outer = str(V.SCOPE / 'transfer-audit/OUTER-TRANSFER-AUDIT.json')
    helper = str(V.SCOPE / 'complex/fresh-certificates/RESULT-helpers.json')
    def wrong_kappa(d):
        d['conditional_assembly']['kappa'] = '24/10000'
    def wrong_gap(d):
        d['conditional_assembly']['functional_interface_gaps']['global_gamma_spare_power'] = '-1'
    def extra_environment(d):
        d['environment']['unexpected_scientific_field'] = 'must not be ignored'
    def wrong_host(d):
        d['environment']['python'] = 'fabricated interpreter'
    controls = []
    for name, filename, change in (
            ('altered_target_kappa', outer, wrong_kappa),
            ('negative_functional_gap', outer, wrong_gap),
            ('undeclared_environment_field', helper, extra_environment),
            ('false_fresh_host_metadata', helper, wrong_host)):
        path = V.checked(root, filename)
        original = path.read_bytes()
        data = V.read_payload(path)
        change(data)
        reason = None
        try:
            encoded = (json.dumps(data, sort_keys=True) + '\n').encode()
            path.write_bytes(gzip.compress(encoded, mtime=0) if path.suffix == '.gz' else encoded)
            try:
                V.compare_outputs(root, outputs)
            except ValueError as error:
                reason = str(error)
            V.need(reason is not None, 'Control must be rejected: ' + name)
        finally:
            path.write_bytes(original)
        controls.append({'control': name, 'path': filename, 'rejected': True, 'reason': reason})
        print('REJECTED ' + name, flush=True)
    V.compare_outputs(root, outputs)
    result = {'status': 'PASS_SCIENTIFIC_COMPARISON_CONTROLS', 'positive_artifacts': 59,
              'controls': controls, 'fresh_artifacts_restored': True,
              'comparator_sha256': V.digest(Path(V.__file__)),
              'control_source_sha256': V.digest(Path(__file__))}
    args.report.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(result['status'])


if __name__ == '__main__':
    main()
