"""Source-bound rank-32 fitting construction and full-plane copy invoice.

Tekalign, substantial OpenAI Codex assistance. Apache-2.0.
"""
from collections import Counter
from hashlib import sha1, sha256
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
INPUT = 'research/adaptive-kernel-demotion/inputs/DATA-PHASES.json'


def need(ok, message):
    if not ok:
        raise ValueError(message)


def authenticate(raw, row):
    need(sha256(raw).hexdigest() == row['sha256'], 'source SHA256')
    need(sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest() == row['git_blob'],
         'source Git blob')


def inputs():
    meta = json.loads((HERE/'SOURCES.json').read_text())
    rows = [r for r in meta['files'] if r['usage'] == 'input']
    need(len(rows) == 1 and rows[0]['path'] == INPUT, 'source inventory')
    raw = (ROOT/INPUT).read_bytes()
    authenticate(raw, rows[0])
    rows = json.loads(raw)['recipes']
    need(len(rows) == 112 and sorted(r['port'] for r in rows) == list(range(112)),
         'complete selected ports')
    labels = [r['q'] for r in sorted(rows, key=lambda r:r['port'])]
    need(len(set(labels)) == 112 and all(type(x) is int and 0 < x < 512 for x in labels),
         'literal binary labels')
    previous = (HERE/'PREDECESSOR.json').read_bytes()
    authenticate(previous, meta['retained_predecessor'])
    return labels, json.loads(previous), meta


def rank2(rows):
    basis = {}
    for row in rows:
        while row:
            bit = row.bit_length()-1
            if bit not in basis:
                basis[bit] = row
                break
            row ^= basis[bit]
    return len(basis)


def evaluate(labels, cert):
    groups = cert['orthonormal_groups']
    need(len(groups) == 16 and all(type(g) is list and len(g) in (2,4,6,8) for g in groups),
         'sixteen nonempty even groups')
    need(all(type(i) is int for g in groups for i in g)
         and sorted(i for g in groups for i in g) == list(range(112)), 'exact port partition')
    dot = lambda i,j: (labels[i]&labels[j]).bit_count()%2
    need(all(dot(i,j) == int(i == j) for g in groups for i in g for j in g),
         'complete group Gram identity')
    pairs = [g[i:i+2] for g in groups for i in range(0,len(g),2)]
    owner = {p:i for i,pair in enumerate(pairs) for p in pair}
    allowed = [[all(dot(x,y) == 0 for x in pairs[i] for y in pairs[j])
                for j in range(56)] for i in range(56)]
    supports = [g[parity::2] for g in groups for parity in (0,1)]
    channel = {p:i for i,s in enumerate(supports) for p in s}
    matrix = [[int(channel[i] == channel[j]) for j in range(112)] for i in range(112)]
    forced = 0
    for i in range(112):
        for j in range(112):
            if i == j or not allowed[owner[i]][owner[j]]:
                forced += 1
                need(matrix[i][j] == int(i == j), 'complete ordered strict scalar mask')
    clique = cert['clique_planes']
    need(len(clique) == len(set(clique)) == 16 and
         all(type(i) is int and 0 <= i < 56 for i in clique), 'sixteen clique planes')
    need(all(not allowed[i][j] for i in clique for j in clique), 'forced identity minor')
    # Each channel reads both coordinate directions of each participating plane.
    tariffs = []
    for support in supports:
        ports = sorted({x for p in support for x in pairs[owner[p]]})
        rows = [sum(dot(i,j)<<k for k,j in enumerate(ports)) for i in ports]
        tariffs.append(rank2(rows))
    return dict(groups=groups,pairs=pairs,supports=supports,matrix=matrix,
                forced=forced,clique=clique,tariffs=tariffs)


def run():
    labels, old, meta = inputs()
    cert = json.loads((HERE/'CERTIFICATE.json').read_text())
    model = evaluate(labels, cert)
    removed = cert['removed_predecessor_frames']
    need(removed == [1,7], 'named predecessor repair')
    old_groups = old['orthonormal_groups']
    retained = [g for i,g in enumerate(old_groups[:13]) if i not in removed]
    replacement = cert['replacement_groups']
    need(model['groups'] == retained+replacement, 'eleven untouched predecessor frames')
    old_local = sorted(p for i,g in enumerate(old_groups) if i in removed or i >= 13 for p in g)
    need(sorted(p for g in replacement for p in g) == old_local, 'exact 24-port repair')
    need(Counter(map(len,replacement)) == {4:3,6:2}, 'replacement shape')
    return dict(group_count=16,group_sizes=dict(sorted(Counter(map(len,model['groups'])).items())),
                scalar_rank_upper=32,scalar_rank_lower=32,uniform_block_rank='32*d',
                checked_matrix_entries=112**2,forced_scalar_entries=model['forced'],
                clique_planes=model['clique'],
                copy_rank_histogram=dict(sorted(Counter(model['tariffs']).items())),
                full_port_copy_rank=sum(model['tariffs']),
                retained_eight_frames=11,repaired_ports=old_local,
                input_sha256=meta['files'][0]['sha256'],no_new_kappa=True)
