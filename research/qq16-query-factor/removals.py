"""Proposed source-event replacement record; Apache-2.0, Codex assisted.

No deletion is accepted without the missing paid native/interface construction.
This generator binds the exact centres and replacement line/map operations.
"""
import argparse,gzip,hashlib,json,tarfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def generate():
    for rel,pin in [('research/joint-query/certificate.json.gz','a5ed85fac5ebf3c091482a113ab0d351eb5a7892fe2841a35e16017ec1ff49f7'),('research/community-frontier1042-audit/selected-replay.tar.gz','22c3f4dce4b897a1d423d1388801933e288b6a6b1906cb15e1b16a5eb68db754')]:
        if hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()!=pin:raise ValueError('source SHA256: '+rel)
    packet=json.loads(gzip.decompress((ROOT/'research/joint-query/certificate.json.gz').read_bytes()))
    with tarfile.open(ROOT/'research/community-frontier1042-audit/selected-replay.tar.gz')as a:
        template=json.loads(gzip.decompress(a.extractfile('t16/global/hosted/GLOBAL-TEMPLATE.json.gz').read()))
    selected=template['local_providers']['gauge44']['local_programs']
    removed=[{'orientation':orientation,'source_event_index':i,'event':e}for orientation,events in selected.items()for i,e in enumerate(events)if e[0]=='center']
    def expand(events):
        result=[]
        for e in events:
            if e[0]=='retained_core':result.extend(expand(packet['core_words'][e[1]]))
            elif e[0] in ('cover_sweep','private_sweep'):result.extend(expand(e[2]))
            else:result.append(e)
        return result
    words={name:expand(packet['programs'][name])for name in ('F_0','B_1_2')}
    lines=[{'program':name,'expanded_event_index':i,'event':e}for name,events in words.items()for i,e in enumerate(events)if e[0]=='native_line']
    maps={name:[i for i,e in enumerate(events)if e[0]=='cover_map']for name,events in words.items()}
    if len(removed)!=16 or len(lines)!=32 or sum(map(len,maps.values()))!=528:raise ValueError('source replacement census')
    return {'status':'PROPOSED_ONLY_NOT_ADMITTED_DELETION','boundary':'same complete current pair0 X/Y before execution6 signed bridge; unchanged pair1 and borrowed state',
      'selected_program_sha256':{name:hashlib.sha256(canonical(events)).hexdigest()for name,events in selected.items()},
      'removed_centre_events':removed,'introduced_line_events':lines,'introduced_explicit_map_event_indices':maps,
      'logical_repair_word_sha256':hashlib.sha256((HERE/'CANDIDATE-WORD.json').read_bytes()).hexdigest(),
      'accepted_source_work_removed':0,'reason':'Logical endpoint equality holds only in checked payload specialization; native lift and full physical/precision/usage bill remain unestablished.',
      'retained_obligations':['all remaining selected work replaced by the fully invoiced QQ16 words, not presumed cancelled eventwise','528 owner maps and64 line wrappers','all6112 repair ADD-view and104 CLEAR operations','33 declared owned fields with exclusive physical stock still required','both bridge legs and intervening state restoration','native phase lift, movement, precision and actual recursive usage'],
      'no_double_credit':'No decoder3985/4015/4106 saving is credited at this different endpoint.'}
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--write',action='store_true');args=parser.parse_args();path=HERE/'REMOVALS.json';obj=generate()
    if args.write:
        with path.open('x')as f:f.write(json.dumps(obj,indent=2,sort_keys=True)+'\n')
    elif canonical(json.loads(path.read_text()))!=canonical(obj):raise ValueError('source-event record mismatch')
    print('PASS_PROPOSED_SOURCE_EVENT_REMOVAL_RECORD')
if __name__=='__main__':main()
