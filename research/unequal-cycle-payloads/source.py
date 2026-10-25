"""Authenticate and reconstruct the actual P112 core; import no predecessor code."""
from hashlib import sha1, sha256
from io import BytesIO
import json
from pathlib import Path
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ARCHIVE = 'research/community-frontier1094-audit/selected-replay.tar.gz'
MATCHING = 'research/paired-plane-scalar-mask-obstruction/PR1825-CERTIFICATE.json'
CERTIFICATE = 'research/paired-plane-minrank-bracket-audit/CERTIFICATE.json'
MEMBER = 'candidate/strict/global/base/work/complex-nine-native/DATA-PHASES.json'


def need(ok, message):
    if not ok:
        raise ValueError(message)


def inputs(root=ROOT):
    result = {}
    rows = [r for r in json.loads((HERE/'SOURCES.json').read_text())['files'] if r['usage'] == 'input']
    need({r['path'] for r in rows} == {ARCHIVE, MATCHING, CERTIFICATE}, 'complete source inventory')
    for row in rows:
        raw = (root/row['path']).read_bytes()
        need(sha256(raw).hexdigest() == row['sha256'], 'source SHA256: '+row['path'])
        need(sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest() == row['git_blob'],
             'source Git blob: '+row['path'])
        result[row['path']] = raw
    return result


def model(root=ROOT):
    raw = inputs(root)
    matching = json.loads(raw[MATCHING])
    with tarfile.open(fileobj=BytesIO(raw[ARCHIVE]), mode='r:gz') as archive:
        members = [m for m in archive.getmembers() if m.name == MEMBER]
        need(len(members) == 1 and members[0].isfile(), 'unique selected data member')
        payload = archive.extractfile(members[0]).read()
    need(sha256(payload).hexdigest() == matching['selected_payload_sha256'], 'selected payload binding')
    recipes = json.loads(payload)['recipes']
    by_port = {r['port']: r['q'] for r in recipes}
    need(len(recipes) == len(by_port) == 112 and sorted(by_port) == list(range(112)), 'exact selected port set')
    labels = [by_port[i] for i in range(112)]
    need(all(type(x) is int and 0 < x < 512 for x in labels) and len(set(labels)) == 112, 'distinct binary labels')
    pairs = matching['matching']
    need(len(pairs) == 56 and all(len(p) == 2 for p in pairs)
         and sorted(i for p in pairs for i in p) == list(range(112)), 'complete paired-port partition')
    dot = lambda a,b: (a & b).bit_count()%2
    for i,j in pairs:
        need(dot(labels[i],labels[i]) == dot(labels[j],labels[j]) == 1 and dot(labels[i],labels[j]) == 0,
             'Gram-I2 planes')
    allowed = [[all(dot(labels[i],labels[j]) == 0 for i in p for j in q) for q in pairs] for p in pairs]
    cert = json.loads(raw[CERTIFICATE])
    core, clique = cert['c5_core'], cert['clique22']
    validate_core(core,clique,allowed)
    return dict(labels=labels,pairs=pairs,allowed=allowed,core=core,clique=clique,
                payload_sha256=sha256(payload).hexdigest())


def validate_core(core,clique,allowed):
    need(len(core) == 5 and len(set(core)) == 5 and all(type(i) is int and 0<=i<56 for i in core),
         'five distinct actual core planes')
    need(len(clique) == 22 and len(set(clique)) == 22 and not set(core)&set(clique)
         and all(type(i) is int and 0<=i<56 for i in clique), '22 separate actual clique planes')
    need(all(allowed[x][y] == ((i-j)%5 in (1,4)) for i,x in enumerate(core) for j,y in enumerate(core)),
         'actual induced cycle mask')
    need(all(not allowed[x][y] for x in clique for y in clique+core), 'clique separation mask')
