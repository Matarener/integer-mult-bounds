"""Verify a complete P104 representation construction and unbounded dual.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
Source P104 credits remain in inputs/NOTICE. No optimizer is imported.
"""
import argparse
from copy import deepcopy
from fractions import Fraction as Q
import gzip
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from construct import graph,verify_dual,build,canonical,need


def run(emit):
    for pin in json.loads((HERE/'SOURCES.json').read_text())['vendored_inputs']:
        need(sha256((HERE/pin['path']).read_bytes()).hexdigest()==pin['sha256'],'frozen source '+pin['path'])
    source=json.loads(gzip.decompress((HERE/'inputs/WORD.json.gz').read_bytes()))
    certificate=json.loads((HERE/'CERTIFICATE.json').read_text());data=graph(source)
    powers,optimum=verify_dual(data,certificate)
    adapted=(HERE/'inputs/local.py').read_text().replace(
        'def replay(w):','def replay(w, *, operation_bound=26000):').replace(
        "    need(len(w['program']) < 26000, 'Fixed operation bound')",
        "    need(type(operation_bound) is int and operation_bound > 0, 'Positive operation bound')\n"
        "    need(len(w['program']) < operation_bound, 'Declared operation bound')")
    need((HERE/'local.py').read_text()==adapted,'only the declared operation-bound API differs')
    spec=importlib.util.spec_from_file_location('complete_gauge_local',HERE/'local.py')
    local=importlib.util.module_from_spec(spec);spec.loader.exec_module(local)
    word,edits,boundaries,native=build(source,data,powers,local)
    operation_bound=len(source['program'])+2*source['public']+1
    before,after=local.replay(source),local.replay(word,operation_bound=operation_bound)
    transpose=local.reverse_columns(word)
    for key in ('paid','helpers','owned_fields','peak_owned_fields','public_inputs','paid_rank_mass'):
        need(before[key]==after[key],'retained profile '+key)
    baseline=sum(w*abs(e) for a,b,e,w in data['edges'])
    old_signs=sum(e[0]=='SCALE' and Q(e[-2])<0 for e in source['program'])
    new_signs=sum(data['signs'][a]<0 for a in data['final'].values())
    saving=2*(baseline-optimum)+2*(old_signs-new_signs)
    need(before['real_scalar_allowance']-after['real_scalar_allowance']==saving>0,'complete scalar allowance and all boundary costs')
    norms=[Q(1)]*(source['public']+source['owned_fields']);peak=Q(1)
    for event in word['program']:
        op,r=event[:2]
        if op in ('INIT','CLEAR'):norms[r]=0
        elif op=='SCALE':norms[r]*=abs(Q(event[-2]))
        elif op=='COPY':norms[r]=abs(Q(event[-2]))*norms[event[2]]
        elif op=='ADD':norms[r]+=abs(Q(event[-2]))*norms[event[2]]
        peak=max(peak,norms[r])
    need(peak<=Q(2)**(16*26000),'retain the source scalar-growth envelope')
    inherited=json.loads((HERE/'inputs/CALLER-RESULT.json').read_text())
    native_counts=inherited['native']
    helper_normalizers=2*sum(after['helpers'].values())
    main_adapters=2*len(source['live'])
    need(helper_normalizers==native_counts['helper_normalizers'] and
         main_adapters==native_counts['main_adapters'],'source interface multiplicities')
    for key in ('paid','helpers'):
        need(canonical(after[key])==canonical(inherited['local'][key]),'complete inherited '+key)
    routes=(sum(after['paid'].values())+helper_normalizers+
            main_adapters+4*104+4*after['owned_lifetimes'])*1000
    need(after['real_scalar_allowance']+routes<10**7,'source complete local nonrecursive allowance')
    controls=[]
    bad=deepcopy(certificate);bad['objective']-=1
    try:verify_dual(data,bad)
    except ValueError as error:controls.append(['false optimum',str(error)])
    else:raise ValueError('false optimum accepted')
    bad=deepcopy(certificate);bad['dual'][0]=data['edges'][0][3]+1
    try:verify_dual(data,bad)
    except ValueError as error:controls.append(['excess dual capacity',str(error)])
    else:raise ValueError('bad capacity accepted')
    bad=deepcopy(word);entry=next(e for phase,e in boundaries if phase=='entry');bad['program'].remove(entry)
    try:local.replay(bad,operation_bound=operation_bound)
    except ValueError as error:controls.append(['uncharged missing entry',str(error)])
    else:raise ValueError('free boundary accepted')
    result={'schema':'p104-complete-dyadic-gauges/1','before':before,'after':after,'transpose':transpose,
            'gauge_nodes':data['count'],'graph_edges':len(data['edges']),
            'baseline_exponent_cost':baseline,'optimal_exponent_cost':optimum,
            'old_sign_scales':old_signs,'minimal_sign_scales':new_signs,
            'saved_local_primitives':saving,'saved_18_call_primitives':18*saving,
            'source_instructions':len(source['program']),'instructions':len(word['program']),
            'strict_operation_bound':operation_bound,'positive_scalar_majorant':str(peak),
            'retained_scalar_growth_exponent':16*26000,
            'local_route_allowance':routes,'local_combined_allowance':routes+after['real_scalar_allowance'],
            'entry_scales':sum(phase=='entry' for phase,e in boundaries),
            'exit_scales':sum(phase=='exit' for phase,e in boundaries),
            'all_boundary_scales':boundaries,'edit_count':len(edits),
            'edits_sha256':sha256(canonical(edits)).hexdigest(),
            'native_gauge_sha256':sha256(canonical(native)).hexdigest(),
            'graph_sha256':sha256(canonical(data)).hexdigest(),
            'word_sha256':sha256(canonical(word)).hexdigest(),'controls':controls}
    payload={'RESULT.json':json.dumps(result,indent=1,sort_keys=True).encode()+b'\n',
             'WORD.json.gz':gzip.compress(canonical(word),mtime=0)}
    if emit:
        for name,raw in payload.items():(emit/name).write_bytes(raw)
    else:
        for name,raw in payload.items():
            stored=(HERE/name).read_bytes()
            need(gzip.decompress(stored)==gzip.decompress(raw) if name.endswith('.gz') else stored==raw,'complete retained '+name)
    print('PASS_P104_COMPLETE_DYADIC_GAUGES',saving,'primitives per call;',len(word['program']),'instructions')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--emit',type=Path)
    run(p.parse_args().emit)
