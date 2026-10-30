"""Regenerate the literal staged-entry fill from PR3945's literal fill and the declared role moves (standard library).

FILL = PR3945 owner/FILL.json.gz with each role in MOVES.json.gz re-homed to its declared (owner, child, port); every
offset is then the compact chronological prefix under the final canonical widths.  The regenerated payload must equal
FILL.json.gz exactly.  How the moves were found (class-level Hall integer program + per-width min-cost interval
transports) is recorded in build/ and is not needed to check the result.
Prepared by Rohan Arun with Anthropic Claude assistance. Apache-2.0.
"""
from pathlib import Path
from collections import defaultdict
import argparse, gzip, hashlib, json
ROOT = Path(__file__).resolve().parent; PACKAGE = ROOT.parent


def need(ok, why):
    if not ok: raise ValueError(why)
def read(p):
    b = p.read_bytes(); return json.loads(gzip.decompress(b) if p.suffix == '.gz' else b)
def dimension(rows):
    piv = {}
    for x in rows:
        while x:
            b = x.bit_length()
            if b in piv: x ^= piv[b]
            else: piv[b] = x; break
    return len(piv)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--output-dir'); a = ap.parse_args()
    pins = read(ROOT / 'SOURCES.json')['files']
    for rel, digest in pins.items(): need(hashlib.sha256((ROOT / rel).read_bytes()).hexdigest() == digest, 'source hash mismatch: ' + rel)
    order = read(ROOT / 'inputs/ORDER.json'); dispatch = {(s, r): pid for s, r, pid in read(ROOT / 'inputs/DISPATCH.json')}
    fill = read(ROOT / 'inputs/PR3945-FILL.json.gz'); full = [1 << i for i in range(9)]; widths = {}
    for tag, pid in [('base', 'gauge44'), ('extra', 'extra')]:
        word = read(PACKAGE / 'inputs' / f'NEW-{tag}.json.gz'); origin = read(ROOT / 'inputs' / f'old-NATIVE-{tag}.json.gz')['helper_origin']
        widths[pid] = [dimension(word['helper_final'].get(str(r), full)) - dimension(word['start_extra'].get(str(r), [])) for r in origin]
    moves = read(ROOT / 'MOVES.json.gz'); need(moves['columns'] == ['role_index', 'owner_replica', 'child', 'port'], 'moves schema')
    seen = set()
    for i, o, c, p in moves['moves']:
        need(i not in seen and fill['rows'][i][2:5] != [o, c, p], 'each declared move is a real, single re-homing'); seen.add(i)
        fill['rows'][i][2:5] = [o, c, p]
    used = defaultdict(int)
    for j, row in enumerate(fill['rows']):
        t, h, o, c, p, z = row; need((t, h) == divmod(j, 408), 'helper identity')
        key = (o, c, p); row[5] = used[key]; used[key] += widths[dispatch[tuple(order[t])]][h]
    need(fill == read(ROOT / 'FILL.json.gz'), 'regenerated role payload differs')
    payload = json.dumps(fill, separators=(',', ':')).encode()
    if a.output_dir:
        out = Path(a.output_dir); need(not out.exists(), 'output directory must be fresh'); out.mkdir(parents=True)
        (out / 'FILL.json.gz').write_bytes(gzip.compress(payload, compresslevel=6, mtime=0))
    print(json.dumps({'status': 'PASS_REGENERATED_LITERAL_FILL', 'roles': len(fill['rows']), 'moved_roles': len(seen), 'fill_payload_sha256': hashlib.sha256(payload).hexdigest()}, sort_keys=True), flush=True)


if __name__ == '__main__':
    main()
