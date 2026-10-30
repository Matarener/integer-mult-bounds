#!/usr/bin/env python3
"""Independent bounded audit of baseline centre lifetimes and QQ16 removal.

Reads pinned data only; imports no predecessor executable. Apache-2.0.
The existing corrected-word construction is credited to research/joint-query.
This checker establishes source provenance and scalar/frame contracts, not
global coverage, a complete native kernel proof, or a new retirement schedule.
"""
import argparse
from collections import Counter
from fractions import Fraction as Q
import gzip
import hashlib
import io
import json
from pathlib import Path
import tarfile

PINS = {
    'research/community-frontier1042-audit/selected-replay.tar.gz':
    '22c3f4dce4b897a1d423d1388801933e288b6a6b1906cb15e1b16a5eb68db754',
    'research/joint-query/certificate.json.gz':
    'a5ed85fac5ebf3c091482a113ab0d351eb5a7892fe2841a35e16017ec1ff49f7',
}
MEMBERS = {
    'slots/local/CANONICAL-WORD.json.gz':
    '16bc0ebb04b4be6c0ade74badc6a0c0cdba4215eda86e4ff9f13abf8ecebd219',
    'slots/local/LOCAL-PROGRAMS.json.gz':
    '241fde27d4e43f5a9cb6b128f9f76c5131a53d09f0371676163f914d0b0fef3a',
}


def need(condition, why):
    if not condition:
        raise ValueError(why)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def reg(field):
    return field[1] + (704 if field[0] == 'C' else 0)


def add(dst, src, scale):
    for j, value in src.items():
        dst[j] = dst.get(j, Q(0)) + scale * value
        if dst[j] == 0:
            del dst[j]


def replay(events):
    """Scalar projection only: native frame transformations are checked apart."""
    rows = [{j: Q(1)} for j in range(712)]
    for event in events:
        if event[0] != 'scalar':
            continue
        op = event[1]
        at = reg(op[1])
        if op[0] == 'clear':
            rows[at] = {}
        elif op[0] == 'copy':
            rows[at] = dict(rows[reg(op[2])])
        elif op[0] == 'scale':
            rows[at] = {j: v * Q(op[2], op[3]) for j, v in rows[at].items()}
        elif op[0] == 'add':
            need(at != reg(op[2]), 'self addition outside audit grammar')
            add(rows[at], rows[reg(op[2])], Q(op[3], op[4]))
        else:
            raise ValueError('unknown scalar gate')
    return rows


def scalar_allowance(events):
    allowance = 0
    for event in events:
        if event[0] != 'scalar':
            continue
        op = event[1]
        if op[0] in ('clear', 'copy'):
            allowance += 1
            continue
        q = Q(op[3], op[4]) if op[0] == 'add' else Q(op[2], op[3])
        a, b = abs(q.numerator), q.denominator
        need(a > 0 and b & (b-1) == 0, 'dyadic scalar tariff')
        if op[0] == 'scale':
            need(a & (a-1) == 0, 'power-of-two scale')
            allowance += abs(a.bit_length()-b.bit_length()) + (q < 0)
        else:
            allowance += 3 + a.bit_length()-1 + a.bit_count() + b.bit_length()-1
    return 2 * allowance


def frames(events, word):
    state = word['start'][:] + [None] * 8
    for i, event in enumerate(events):
        if event[0] == 'climb':
            _, _, at, old, new, _ = event
            need(state[at] == old, f'climb frame {i}')
            state[at] = new
        elif event[0] == 'center':
            _, c, old, new, _ = event
            need(state[704+c] == old, f'centre frame {i}')
            state[704+c] = new
        elif event[0] == 'scalar':
            op, frame = event[1:]
            at = reg(op[1])
            if op[0] == 'clear':
                state[at] = frame
            else:
                need(state[at] == frame, f'target frame {i}')
                if op[0] in ('copy', 'add'):
                    need(state[reg(op[2])] == frame, f'source frame {i}')
    need(state[:704] == word['final'], 'persistent final frames')
    return state[704:]


def run(repo):
    raw = {}
    for path, expected in PINS.items():
        raw[path] = (repo/path).read_bytes()
        need(digest(raw[path]) == expected, 'source hash: '+path)
    packet = json.loads(gzip.decompress(raw['research/joint-query/certificate.json.gz']))
    decoded = {}
    with tarfile.open(fileobj=io.BytesIO(raw[next(iter(PINS))]), mode='r:gz') as archive:
        for name, expected in MEMBERS.items():
            matches = [m for m in archive.getmembers() if m.name == name]
            need(len(matches) == 1 and matches[0].isfile(), 'unique regular member')
            data = archive.extractfile(matches[0]).read()
            need(digest(data) == expected, 'member hash: '+name)
            decoded[name.rsplit('/', 1)[1]] = json.loads(gzip.decompress(data))
    word, programs = decoded['CANONICAL-WORD.json.gz'], decoded['LOCAL-PROGRAMS.json.gz']
    need(word['centers'] == [92,57,81,224,11,240,9,256], 'centre register order')
    pre = programs['forward'].index(['phase','centers'])
    rows = replay(programs['forward'][:pre])
    R = [{j:v for j,v in rows[c].items() if j < 112} for c in word['centers']]
    H = [{j:v for j,v in rows[c].items() if j >= 224} for c in word['centers']]
    need(all(rows[c] == R[k] | H[k] for k,c in enumerate(word['centers'])), 'centre source support')
    need(R == [{int(j):Q(v) for j,v in row.items()} for row in packet['R_rows']], 'packet centre matrix')
    D = [{} for _ in range(112)]
    for event in word['cut']:
        need(event[0]=='add', 'cut gate')
        add(D[event[1]-112], {word['centers'].index(event[2]):Q(event[3],event[4])}, Q(1))
    J = []
    for p in range(112):
        row = {p:Q(1)}
        for k in range(8):
            add(row,R[k],-R[k].get(p,Q(0))/4)
        J.append(row)
    result = {'status':'PASS_CENTRE_PROVENANCE_AND_EXISTING_REMOVAL',
              'canonical_main':'20ecf2891d80b5acf18d980b2164fb44ea7faa90',
              'index_convention':'zero-based JSON event indices',
              'sources':PINS,'members':MEMBERS,'orientations':{}}
    for name, source in programs.items():
        backward = name == 'backward'
        a = source.index(['phase','A'])
        begin = source.index(['phase','centers'])
        end = source.index(['phase','B'])
        baseline_private_frames = frames(source, word)
        need(baseline_private_frames == (word['center_frames'] if backward else [0]*8),
             'baseline final private frames')
        lifetimes = []
        for k,c in enumerate(word['centers']):
            touched=[]
            for i,event in enumerate(source):
                if event[0]=='center' and event[1]==k:
                    touched.append((i,event))
                elif event[0]=='scalar' and any(x==['C',k] for x in event[1][1:] if isinstance(x,list)):
                    touched.append((i,event))
            need(len(touched)==26,'exact centre lifetime event count')
            need(all(begin < i < end for i,_ in touched),'no C reference after centre phase')
            first,last=touched[0],touched[-1]
            need(first[1][1][0]=='clear' and last[1][1][0]=='clear','owned initial/final clear')
            child=next((i,e) for i,e in touched if e[0]=='center')
            logical=[(i,e) for i,e in touched if e[0]=='scalar' and e[1][0]=='add']
            reads=[(i,e) for i,e in logical if e[1][2]==['C',k]]
            writers=[(i,e) for i,e in logical if e[1][1]==['C',k]]
            lifetimes.append({'centre':k,'source_L_register':c if not backward else None,
                'accumulated_L_sources':[e[1][2][1] for _,e in writers],
                'entry_clear':first[0],'copy_event':None if backward else first[0]+1,
                'child_event':child[0],'child':child[1],
                'source_frame_basis':word['frames'][child[1][2]],
                'destination_frame_basis':word['frames'][child[1][3]],
                'consumer_L_registers':[e[1][1][1] for _,e in reads],
                'last_read':reads[-1][0],'final_clear':last[0],
                'zero_exit_frame':last[1][2],
                'reads':len(reads),'accumulation_adds':len(writers)})
        prefix=[]
        def emit(dst,src,q):
            prefix.append(['scalar',['add',dst,src,q.numerator,q.denominator],0])
        for k in range(8):
            private=['C',k]
            prefix.append(['scalar',['clear',private],0])
            if backward:
                for p,d in enumerate(D):
                    if k in d:emit(private,['L',112+p],d[k])
                for j,q in sorted(H[k].items()):emit(['L',j],private,-q)
            else:
                for j,q in sorted(H[k].items()):emit(private,['L',j],q)
                for p,d in enumerate(D):
                    if k in d:emit(['L',112+p],private,d[k])
            prefix.append(['scalar',['clear',private],0])
        fixed=source[:a]+[['phase','centre_dirty_correction']]+prefix+source[a:begin]+source[end:]
        need(fixed==packet['core_words'][name],'independently regenerated literal clean core')
        need(not any(e[0]=='center' for e in fixed),'all centre children removed')
        need(frames(fixed,word)==[0]*8,'private clean-core zero frames')
        native=lambda w:[e for e in w if e[0] in ('climb','adapter','residual_adapter')]
        need(native(fixed)==native(source),'persistent native events preserved')
        out=replay(fixed)
        expected=[{j:Q(1)} for j in range(704)]+[{} for _ in range(8)]
        for p,row in enumerate(J):
            if backward:add(expected[p],{112+j:q for j,q in row.items()},Q(-1))
            else:add(expected[112+p],row,Q(1))
        need(out==expected,'all 712 scalar outputs including helpers and scratch')
        bad=list(fixed)
        remove=next(i for i in range(a+1,a+1+len(prefix)) if bad[i][0]=='scalar' and bad[i][1][0]=='add')
        del bad[remove]
        changed=[j for j,(x,y) in enumerate(zip(replay(bad),expected)) if x!=y]
        need(changed,'missing correction must change exact output')
        badchild=next(i for i,e in enumerate(source) if e[0]=='center')
        try:frames(source[:badchild]+source[badchild+1:],word)
        except ValueError as exc:frame_failure=str(exc)
        else:raise ValueError('removed H8 did not fail frame check')
        profile=Counter(e[5] for e in fixed if e[0]=='climb')
        need(dict(profile)=={1:2412,2:418,3:432,4:142,5:82},'actual core child profile')
        result['orientations'][name]={'baseline_events':len(source),'lifetimes':lifetimes,
            'baseline_final_private_frames':baseline_private_frames,
            'baseline_last_C_clear':max(v['final_clear'] for v in lifetimes),
            'baseline_next_phase_B':end,'clean_core_events':len(fixed),
            'removed_centre_children':8,'removed_centre_rank_mass':64,
            'inserted_correction_ADDs':sum(e[1][0]=='add' for e in prefix),
            'inserted_correction_CLEARs':sum(e[1][0]=='clear' for e in prefix),
            'inserted_scalar_allowance':scalar_allowance(prefix),
            'removed_scalar_allowance':scalar_allowance(source[begin:end]),
            'baseline_scalar_allowance':scalar_allowance(source),
            'clean_core_scalar_allowance':scalar_allowance(fixed),
            'clean_core_child_profile':dict(sorted(profile.items())),
            'clean_core_rank_mass':sum(k*v for k,v in profile.items()),
            'clean_core_reconstruction_matches_packet':True,
            'exact_scalar_columns':712,'restored_helpers':480,'private_outputs_zero':8,
            'removed_child_mutant':{'result':'REJECT','reason':frame_failure},
            'removed_correction_mutant':{'result':'REJECT','deleted_event':remove,
                'changed_output_indices':changed}}
    def tagged(value, tag):
        if not isinstance(value,list):
            return []
        found=[value] if value and value[0]==tag else []
        for child in value:
            found.extend(tagged(child,tag))
        return found
    result['actual_QQ16_calls']={}
    for call,side,lines in [('F_0','forward',8),('B_1_2','backward',24)]:
        macro=packet['programs'][call]
        core=tagged(macro,'retained_core')
        need(len(core)==1 and core[0][1]==side,'actual macro resolves clean core')
        line_events=tagged(macro,'native_line')
        need(len(line_events)==lines,'complete added native line count')
        for event in line_events:
            recipe=packet['native_line_recipes'][event[2]]
            need(recipe['rank']==1 and recipe['recipe']['rank']==1,'actual added line is rank one')
        need(not tagged(macro,'center'),'macro contains no extra centre event')
        profile={1:2412+lines,2:418,3:432,4:142,5:82}
        result['actual_QQ16_calls'][call]={'core_orientation':side,
            'added_H1':lines,'total_literal_child_profile':profile,
            'literal_H8':0,'rank_mass':sum(k*v for k,v in profile.items())}
    result['scope']='Existing local replacement independently reconstructed; no remaining literal H8 centre children in QQ16, no new physical/global retirement credit.'
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--repo',required=True,type=Path)
    parser.add_argument('--out',required=True,type=Path)
    args=parser.parse_args()
    receipt=run(args.repo)
    args.out.write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    print(receipt['status'])
