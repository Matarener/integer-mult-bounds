"""Exact pinned first-provider specialization; standard library only.

Apache-2.0. Chris R / Clear1nsight with substantial OpenAI Codex assistance.
No source emitter or predecessor verifier is executed.
"""
import argparse
from collections import Counter
from copy import deepcopy
from fractions import Fraction as F
import gzip
import hashlib
import json
from pathlib import Path
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
ARCHIVE = 'research/community-frontier1042-audit/selected-replay.tar.gz'
PACKET = 'research/joint-query/certificate.json.gz'
PREFIX = 't16/global/base/providers/gauge44/'


def need(ok, message):
    if not ok:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def canon(obj):
    return json.dumps(obj, sort_keys=True, separators=(',', ':')).encode()


def add(a, b, c=F(1)):
    out = a.copy()
    for j, v in b.items():
        out[j] = out.get(j, F(0)) + c*v
        if not out[j]:
            del out[j]
    return out


def rank(rows):
    pivots = {}
    for original in rows:
        row = original.copy()
        while row:
            j = min(row)
            if j not in pivots:
                c = row[j]
                pivots[j] = {k: v/c for k, v in row.items()}
                break
            row = add(row, pivots[j], -row[j])
    return len(pivots)


def register(token):
    kind, i = token
    need(kind in ('L', 'C') and type(i) is int and 0 <= i < (704 if kind == 'L' else 8), 'register namespace')
    return i + (704 if kind == 'C' else 0)


def replay(events):
    # All 712 symbols, including arbitrary incoming private values. Their
    # final zero rows prove independence from those discarded private inputs.
    rows = [{i: F(1)} for i in range(712)]
    for event in events:
        kind = event[0]
        if kind != 'scalar':
            need(kind in ('climb', 'center', 'phase', 'adapter', 'residual_adapter', 'native_line'), 'unknown native event')
            # Constant-character/common-cover specialization. The inherited
            # operator convention fixes that character, including all phases.
            continue
        gate = event[1]
        op, target = gate[:2]
        at = register(target)
        if op == 'clear':
            need(at >= 704, 'only private cells may be cleared')
            rows[at] = {}
        elif op == 'scale':
            c = F(gate[2], gate[3])
            need(c != 0, 'invertible scalar scale')
            rows[at] = {j: c*v for j, v in rows[at].items()}
        else:
            need(op in ('copy', 'add'), 'known scalar gate')
            source = register(gate[2])
            need(at != source, 'distinct scalar operands')
            rows[at] = rows[source].copy() if op == 'copy' else add(rows[at], rows[source], F(gate[3], gate[4]))
    return rows


def expanded(packet):
    out = []
    for event in packet['programs']['F_0']:
        if event[0] == 'retained_core':
            need(event[1:3] == ['forward', 0], 'F0 forward retained core')
            out.extend(packet['core_words']['forward'])
        else:
            need(event[0] in ('cover_sweep', 'private_sweep'), 'known F0 wrapper')
            out.extend(event[2])
    return out


def scalar_cost(events):
    total = 0
    for event in events:
        if event[0] != 'scalar':
            continue
        gate = event[1]
        if gate[0] in ('clear', 'copy'):
            total += 2
            continue
        c = F(gate[3], gate[4]) if gate[0] == 'add' else F(gate[2], gate[3])
        a, b = abs(c.numerator), c.denominator
        need(a > 0 and b & (b-1) == 0, 'nonzero dyadic scalar')
        if gate[0] == 'add':
            total += 2*(2+a.bit_length()+a.bit_count()+b.bit_length()-1)
        else:
            need(a & (a-1) == 0, 'signed power-of-two scale')
            total += 2*(abs(a.bit_length()-b.bit_length())+(c < 0))
    return total


def validate(source, packet):
    g, q = replay(source), replay(expanded(packet))
    basis = [{i: F(1)} for i in range(712)]
    expected = basis[:112]+[add(basis[112+i], basis[i]) for i in range(112)]+basis[224:704]+[{} for _ in range(8)]
    need(g == expected, 'selected gauge44 is the unit forward shear at specialization')
    need(q[224:704] == basis[224:704] and q[704:] == [{} for _ in range(8)], 'QQ16 restores all helpers and private outputs')
    need(all(j < 224 for row in q[:224] for j in row), 'data independent of helper/private inputs')
    r = [{int(j): F(v) for j,v in row.items()} for row in packet['R_rows']]
    k = [{int(j): F(v) for j,v in row.items()} for row in packet['K_rows']]
    A, T, U = (packet[key] for key in ('A_ports','T_ports','U_ports'))
    need(A == [0,7,20,27,36,46,57,111] and T == [21,37,47,76,81,87,92,110], 'selected role sets')
    need(sorted(A+T+U) == list(range(112)), 'partition')
    ru_ku = [{j: sum(row.get(p,0)*k[p].get(j,0) for p in U) for j in range(8)} for row in r]
    need(ru_ku == [{j:F(12 if i==j else 0) for j in range(8)} for i in range(8)], 'R_U K_U = 12 I')
    def combination(row, values):
        out = {}
        for j,v in row.items():
            out = add(out, values[j], v)
        return out
    x, y = basis[:112], basis[112:224]
    f = [combination(row, x) for row in r]
    rt = [combination({j:v for j,v in row.items() if j in T}, x) for row in r]
    kf, kt = ([combination(row, vals) for row in k] for vals in (f, rt))
    xx = [add(x[p], kf[p], -1) if p in U else kt[p] if p in A else kf[p] for p in range(112)]
    yy = [add(y[p], xx[p]) if p in U else add(add(y[p], x[p]),xx[p],-1) for p in range(112)]
    need(q[:224] == xx+yy, 'literal QQ16 equals independent source-matrix formula')
    need(rank(q[:224]) == 224, 'QQ16 data map invertible')
    delta_rank = rank([add(a,b,-1) for a,b in zip(q[:224],g[:224])])
    traces = [sum(rows[i].get(i,0) for i in range(704)) for rows in (g,q)]
    need(delta_rank == 24 and traces == [704,600], 'exact conjugacy obstruction')
    need(q[0] == {76:F(1,2),81:F(-1,2),87:F(1,2),92:F(1,2)} and g[0] == {0:F(1)}, 'first direct row mismatch')
    return {'data_traces': [224,120], 'persistent_traces': list(map(int,traces)), 'first_mismatch': {'output':'X_0','selected':'X_0','QQ16':'(X_76-X_81+X_87+X_92)/2'}, 'data_difference_rank':delta_rank, 'post_adapter_rank_minus_identity':delta_rank, 'minimum_rank_one_factors_for_post_adapter':delta_rank, 'independent_input_symbols':712, 'arbitrary_helpers_returned':480, 'private_outputs_zero':8, 'source_scalar_real_primitives':scalar_cost(source), 'QQ16_scalar_real_primitives':scalar_cost(expanded(packet)), 'source_center_ranks':[e[4] for e in source if e[0]=='center'], 'QQ16_added_native_lines':sum(e[0]=='native_line' for e in expanded(packet))}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true')
    parser.add_argument('--controls', action='store_true')
    args = parser.parse_args()
    if args.write:
        need(not (HERE/'RESULT.json').exists(), 'refusing to overwrite existing RESULT.json')
    pins = json.loads((HERE/'SOURCES.json').read_text())
    for item in pins['files']:
        if item['usage'] == 'input':
            need(digest((ROOT/item['path']).read_bytes()) == item['sha256'], 'source SHA256: '+item['path'])
    member_hashes = {}
    with tarfile.open(ROOT/ARCHIVE,'r:gz') as archive:
        def member(name):
            entries = [x for x in archive.getmembers() if x.name == name]
            need(len(entries)==1 and entries[0].isfile(), 'unique regular source member')
            payload = archive.extractfile(entries[0]).read()
            member_hashes[name] = digest(payload)
            return json.loads(gzip.decompress(payload))
        template = member('t16/global/hosted/GLOBAL-TEMPLATE.json.gz')
        programs = member(PREFIX+'LOCAL-PROGRAMS.json.gz')
        word = member(PREFIX+'CANONICAL-WORD.json.gz')
    packet = json.loads(gzip.decompress((ROOT/PACKET).read_bytes()))
    call = template['calls'][0]
    need((call['provider_id'],call['orientation'],call['replica'],call['stage'],call['time']) == ('gauge44','forward',0,0,0), 'literal first source call')
    need(template['local_providers']['gauge44']['local_programs'] == programs, 'embedded selected provider bytes')
    need(digest(canon(programs['forward'])) == call['local_program_sha256'], 'literal forward program hash')
    need(len(call['owners']) == 704 and len(set(owner[0] for owner in call['owners'])) == 704, '704 distinct physical owners')
    need(call['owners'][:224] == [[p,[1,0,p%112]] for p in range(224)], 'first data role owners')
    need(len(word['start']) == len(word['final']) == 704, '704 source frame entries')
    native = ('climb', 'adapter', 'residual_adapter')
    need([e for e in programs['forward'] if e[0] in native] == [e for e in packet['core_words']['forward'] if e[0] in native], 'unchanged persistent native events')
    receipt = validate(programs['forward'],packet)
    receipt.update({'schema_version':1,'scope':'Exact first source call and constant-character common-cover specialization; fixed invertible role conjugacy only. No physical adapter, B1 match, or supplier is constructed.', 'source_call':{k:v for k,v in call.items() if k!='owners'},'source_owner_list_sha256':digest(canon(call['owners'])),'source_start_frames_sha256':digest(canon(word['start'])),'source_final_frames_sha256':digest(canon(word['final'])),'archive_member_sha256':member_hashes,'scalar_delta':12444,'status':'scoped obstruction; no frontier change'})
    need(receipt['QQ16_scalar_real_primitives']-receipt['source_scalar_real_primitives']==receipt['scalar_delta'], 'complete scalar delta')
    if args.controls:
        bad = deepcopy(programs['forward'])
        first = next(e for e in bad if e[0]=='scalar' and e[1][0]=='add')
        first[1][3] *= -1
        try:
            validate(bad,packet)
        except ValueError:
            pass
        else:
            raise ValueError('source coefficient mutation accepted')
        badp = deepcopy(packet)
        first = next(e for e in badp['programs']['F_0'][1][2] if e[0]=='scalar')
        first[1][3] *= -1
        try:
            validate(programs['forward'],badp)
        except ValueError:
            pass
        else:
            raise ValueError('QQ16 coefficient mutation accepted')
        print('PASS provider and QQ16 coefficient mutation controls')
    if args.write:
        with (HERE/'RESULT.json').open('x') as output:
            output.write(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    else:
        need(canon(json.loads((HERE/'RESULT.json').read_text())) == canon(receipt), 'complete typed receipt')
    print('PASS first selected provider binding; trace704 !=600; rank24; source198766 QQ16211210')


if __name__ == '__main__':
    main()
