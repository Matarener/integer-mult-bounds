"""Portable environment reporting around PR6204's unchanged benchmark.

AAAmirinu with substantial OpenAI Codex assistance. Apache-2.0.
Nick Petalas's measurement functions and the retained exporter authors' source
bytes remain unchanged. Unsupported load averages are metadata, not failed runs.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import sys
import types

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE_HEAD = '9889f94b6ed045c1069b2e6f7e4471d0322f2f16'
VENDOR = 'research/windows-export-benchmark/vendor/root/'
BENCHMARK = VENDOR + 'research/export-single-scan/benchmark.py'
RETAINED = {
    BENCHMARK,
    VENDOR + 'research/export-single-scan/baseline/export_research_package.py',
    VENDOR + 'research/export-single-scan/baseline/research_package.py',
    VENDOR + 'research/export-single-scan/BENCHMARK-toolkit.json',
    VENDOR + 'scripts/export_research_package.py',
    VENDOR + 'scripts/research_package.py',
}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def load_source():
    """Authenticate every retained file before executing the frozen module."""
    rows = [row for row in json.loads((HERE / 'SOURCES.json').read_bytes())['files']
            if 'retained_path' in row]
    require(len(rows) == 6 and {row['retained_path'] for row in rows} == RETAINED,
            'retained benchmark source inventory')
    raw = {}
    for row in rows:
        require(row['pin'] == 'head:' + SOURCE_HEAD + ':' + row['path'],
                'retained benchmark source pin')
        path = ROOT / row['retained_path']
        require(not path.is_symlink(), 'retained benchmark source symlink')
        value = path.read_bytes()
        require(hashlib.sha256(value).hexdigest() == row['sha256'], 'retained source SHA256 mismatch')
        blob = b'blob ' + str(len(value)).encode('ascii') + b'\0' + value
        require(hashlib.sha1(blob).hexdigest() == row['git_blob'], 'retained source Git blob mismatch')
        raw[row['retained_path']] = value
    module = types.ModuleType('_frozen_export_single_scan_benchmark')
    module.__file__ = str(ROOT / BENCHMARK)
    exec(compile(raw[BENCHMARK], module.__file__, 'exec', optimize=0), module.__dict__)
    return module


def environment_info(os_module=os):
    """Collect optional load telemetry without discarding completed measurements."""
    load, status, reason = None, 'unavailable', 'api_absent'
    getloadavg = getattr(os_module, 'getloadavg', None)
    if getloadavg is not None:
        try:
            load = getloadavg()
        except (NotImplementedError, OSError) as error:
            reason = type(error).__name__
        else:
            status, reason = 'available', None
    return {'python': sys.version, 'platform': platform.platform(),
            'logical_cpus': os_module.cpu_count(), 'load': load,
            'load_status': status, 'load_reason': reason}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--pairs', type=int, default=9, choices=range(5, 21))
    parser.add_argument('--batch', type=int, default=5, choices=range(1, 11))
    args = parser.parse_args(argv)
    archive, output = args.archive.resolve(), args.output.resolve()
    if output.is_relative_to(ROOT) or output.exists():
        raise ValueError('output must be a new external file')
    frozen = load_source()
    result = frozen.benchmark(archive, args.pairs, args.batch, output.parent)
    result['environment'] = environment_info()
    with output.open('x') as stream:
        json.dump(result, stream, indent=2, sort_keys=True)
        stream.write('\n')
    print(json.dumps({key: result[key] for key in ('median_ns', 'wall_time_reduction',
                                                'successful_commands', 'errors')}))


if __name__ == '__main__':
    main()
