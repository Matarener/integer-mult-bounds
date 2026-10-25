"""Source-bound completed-word internal error transfer; Apache-2.0.
Chris R/Clear1nsight with OpenAI Codex assistance. No predecessor evaluator imports.
"""
import argparse,gzip,hashlib,json,time
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter,defaultdict
P=Path(__file__).resolve().parent
N=704

def need(x,msg):
    if not x: raise ValueError(msg)
def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def digest(x):return hashlib.sha256(canonical(x)).hexdigest()
def reduce_word(a,b):
    z=list(a)
    for x in b:
        if z and z[-1]==-x:z.pop()
        else:z.append(x)
    return tuple(z)
def opdual(x):return (1 if x>0 else -1)*(abs(x)+1000000)
def program(w,dual=False):
    seq=[]
    for c in w['initial_corrections']:seq.append(('add',c['target'],c['source'],Q(c['coefficient']),tuple(c['operator_word']),'correction'))
    def append(g,phase):
        if g[0]=='add':seq.append(('add',g[1],g[2],Q(g[3],g[4]),(),phase))
        elif g[0]=='scale':seq.append(('scale',g[1],Q(g[2],g[3]),phase))
        else:
            need(g[0]=='warp','opcode');seq.append(('warp',g[1],g[2],phase))
    for phase in ('precondition','compensation','A','cut'):
        for g in w[phase]:append(g,phase)
    at=defaultdict(list)
    for i,g in enumerate(w['warps'],1):at[g[0]].append(('warp',g[1],i,'B-native'))
    for i in range(len(w['B'])+1):
        seq.extend(at[i])
        if i<len(w['B']):append(w['B'][i],'B')
    for phase in ('restore','cleanup'):
        for g in w[phase]:append(g,phase)
    if dual:
        out=[]
        for g in seq:
            if g[0]=='add':out.append(('add',g[2],g[1],-g[3],tuple(-opdual(o) for o in reversed(g[4])),g[-1]))
            elif g[0]=='scale':out.append(('scale',g[1],1/g[2],g[-1]))
            else:out.append(('warp',g[1],opdual(g[2]),g[-1]))
        seq=out
    for g in seq:
        if g[0]!='warp':
            q=g[3] if g[0]=='add' else g[2];need(q.denominator&(q.denominator-1)==0,'non-dyadic scalar')
            if g[0]=='scale':need(q!=0,'zero scale')
    return seq

def update(dst,src,q,word=(),right=False):
    for (r,wd),a in list(src.items()):
        k=r,reduce_word(wd,word) if right else reduce_word(word,wd)
        v=dst.get(k,Q(0))+q*a
        if v:dst[k]=v
        elif k in dst:del dst[k]
def norm(row):return sum(map(abs,row.values()),Q(0))
def max_bits(x):
    need(x>=0,'negative bound');b=0
    while Q(2)**b<x:b+=1
    return b

def forward(regs,seq):
    rows={r:{(r,()):Q(1)} for r in regs};peak=Q(1);witness=None;phases={}
    trace=hashlib.sha256();positive_error={r:Q(0) for r in regs};error_peak=Q(0);operand_peak=Q(0);local_lipschitz=Q(1)
    for i,g in enumerate(seq):
        kind,t=g[:2]
        if kind=='add':
            q=abs(g[3]);operand_peak=max(operand_peak,norm(rows[t])+q*norm(rows[g[2]]));local_lipschitz=max(local_lipschitz,1+q);positive_error[t]+=q*positive_error[g[2]]+1
        elif kind=='scale':
            q=abs(g[2]);operand_peak=max(operand_peak,q*norm(rows[t]));local_lipschitz=max(local_lipschitz,q);positive_error[t]=q*positive_error[t]+1
        else:operand_peak=max(operand_peak,norm(rows[t]));positive_error[t]+=1
        error_peak=max(error_peak,positive_error[t])
        if kind=='add':update(rows[t],rows[g[2]],g[3],g[4])
        elif kind=='scale':rows[t]={k:g[2]*a for k,a in rows[t].items()}
        else:rows[t]={(r,reduce_word((g[2],),wd)):a for (r,wd),a in rows[t].items()}
        bound=norm(rows[t]);trace.update(canonical([i,t,str(bound)]))
        phases[g[-1]]=max(phases.get(g[-1],Q(1)),bound)
        if bound>peak:peak=bound;witness=[i,g[-1],t]
    return rows,{'all_cut_l1_bound':str(peak),'all_cut_guard_bits':max_bits(peak),'peak_witness':witness,'phase_touched_register_max':{k:str(v) for k,v in phases.items()},'cut_stream_sha256':trace.hexdigest(),'positive_path_all_cut_fault_gain':str(error_peak),'exact_operand_l1_bound':str(operand_peak),'max_local_lipschitz':str(local_lipschitz)}

def backward(regs,seq):
    cols={r:{(r,()):Q(1)} for r in regs};fault={r:Q(0) for r in regs};byphase=defaultdict(lambda:defaultdict(Q));maxfault=Q(0);witness=None;trace=hashlib.sha256()
    for i in range(len(seq)-1,-1,-1):
        g=seq[i];kind,t=g[:2];per=defaultdict(Q)
        for (out,wd),a in cols[t].items():per[out]+=abs(a)
        for out,a in per.items():fault[out]+=a;byphase[g[-1]][out]+=a
        m=max(per.values(),default=Q(0));trace.update(canonical([i,[[r,str(a)] for r,a in sorted(per.items())]]))
        if m>maxfault:maxfault=m;witness=[i,g[-1],t]
        if kind=='add':update(cols[g[2]],cols[t],g[3],g[4],True)
        elif kind=='scale':cols[t]={k:g[2]*a for k,a in cols[t].items()}
        else:cols[t]={(r,reduce_word(wd,(g[2],))):a for (r,wd),a in cols[t].items()}
    return cols,fault,{'max_single_fault_gain':str(maxfault),'single_fault_witness':witness,'fault_stream_sha256':trace.hexdigest(),'phase_output_error_bounds':{p:str(max(v.values())) for p,v in byphase.items()}}

def inverse_prefix(regs,seq,capture=None):
    # Columns of L_k^{-1}; right multiplication by each next inverse gate.
    cols={r:{(r,()):Q(1)} for r in regs};bounds={r:Q(1) for r in regs};total=Q(len(regs));peak=total;full_cut_sum=total;fault_sum=Q(0);trace=hashlib.sha256()
    def column_bound(row):
        per=defaultdict(Q)
        for (r,wd),a in row.items():per[r]+=abs(a)
        return max(per.values(),default=Q(0))
    for i,g in enumerate(seq):
        kind,t=g[:2]
        if kind=='add':
            s=g[2];update(cols[s],cols[t],-g[3],g[4],True);new=column_bound(cols[s]);total+=new-bounds[s];bounds[s]=new
        elif kind=='scale':
            cols[t]={k:a/g[2] for k,a in cols[t].items()};new=bounds[t]/abs(g[2]);total+=new-bounds[t];bounds[t]=new
        else:cols[t]={(r,reduce_word(wd,(-g[2],))):a for (r,wd),a in cols[t].items()}
        if capture is not None:capture(i,cols)
        peak=max(peak,total);full_cut_sum+=total;h=bounds[t];fault_sum+=h;trace.update(canonical([i,str(h)]))
    return {'inverse_prefix_column_sum_bound':str(peak),'inverse_prefix_fault_column_sum':str(fault_sum),'inverse_prefix_full_state_cut_sum':str(full_cut_sum),'inverse_prefix_stream_sha256':trace.hexdigest()}

def analyze(w,dual=False):
    live=sorted(set(range(N))-set(w['removed']));buffers=[r+N for r in sorted(map(int,w['helper_final']))];regs=live+buffers
    seq=program(w,dual);rows,fwd=forward(regs,seq);cols,fault,rev=backward(regs,seq)
    for r,row in rows.items():
        other={(s,wd):a for s,col in cols.items() for (o,wd),a in col.items() if o==r}
        need(row==other,'forward/reverse operator disagreement')
    categories={'all':regs,'live':live,'sources':list(range(112)),'targets':list(range(112,224)),'helpers':[r for r in live if r>=224],'private_buffers':buffers}
    end={k:max(norm(rows[r]) for r in v) for k,v in categories.items()}
    err={k:max(fault[r] for r in v) for k,v in categories.items()}
    leakage={r:{k:a for k,a in rows[r].items() if k[0]>=N} for r in live}
    leakmax=max(map(norm,leakage.values()));need(leakmax==0,'private buffer leakage');leakrow=next(r for r in live if norm(leakage[r])==leakmax)
    leakproof=[[s,list(wd),str(a)] for (s,wd),a in sorted(leakage[leakrow].items())]
    buffer_identity=all(rows[r]=={(r,()):Q(1)} for r in buffers)
    need(buffer_identity,'private buffer identity')
    target_zero=[]
    for r in live:
        expected={(r,()):Q(1)}
        if not dual and 112<=r<224:expected[(r-112,())]=Q(1)
        if dual and r<112:expected[(r+112,())]=Q(-1)
        if {k:a for k,a in rows[r].items() if k[0]<N}!=expected:target_zero.append(r)
    need(not target_zero,'live-input shear contract')
    inv=inverse_prefix(regs,seq)
    fwd['inverse_prefix_all_cut_fault_gain']=str(Q(fwd['all_cut_l1_bound'])*Q(inv['inverse_prefix_fault_column_sum']))
    fullA=Q(fwd['all_cut_l1_bound'])*Q(inv['inverse_prefix_full_state_cut_sum']);fullB=2*Q(inv['inverse_prefix_full_state_cut_sum'])
    need(Q(fwd['all_cut_l1_bound'])+Q(fwd['inverse_prefix_all_cut_fault_gain'])/8192<1024,'absolute range allowance')
    need(18*Q(fwd['inverse_prefix_all_cut_fault_gain'])<2**27 and 2*err['all']*Q(fwd['exact_operand_l1_bound'])<2**27,'relative allowance')
    counts=Counter(g[0] for g in seq)
    coeffbits=max(max(abs(x.numerator).bit_length(),x.denominator.bit_length()) for g in seq for x in ([g[3]] if g[0]=='add' else [g[2]] if g[0]=='scale' else []))
    return {'orientation':'dual' if dual else 'primal','registers':len(regs),'live':len(live),'private_buffers':len(buffers),'instructions':len(seq),'instruction_counts':dict(counts),'max_scalar_coefficient_bits':coeffbits,**fwd,**rev,**inv,'endpoint_l1_bounds':{k:str(v) for k,v in end.items()},'uniform_instruction_fault_gains':{k:str(v) for k,v in err.items()},'sufficient_extra_fraction_bits':{k:max_bits(v) for k,v in err.items()},'uniform_relative_error_guard_bits':max(max_bits(2*err['all']*Q(fwd['exact_operand_l1_bound'])),max_bits(2*Q(fwd['max_local_lipschitz'])*min(Q(fwd['positive_path_all_cut_fault_gain']),Q(fwd['inverse_prefix_all_cut_fault_gain'])))),'full_state_cut_error':{'all_cut_gain':str(fullA),'final_gain':str(fullB),'absolute_guard_bits':max_bits(fullB),'relative_guard_bits':max_bits(36*fullA),'includes_initial_cut':True},'private_buffer_identity_checked':buffer_identity,'dirty_buffer_to_live_l1_bound':str(leakmax),'dirty_buffer_max_row':leakrow,'dirty_buffer_max_row_terms':leakproof,'zero_buffer_live_shear_checked':True,'forward_reverse_all_rows_checked':len(rows),'endpoint_rows_sha256':digest([[r,[[s,list(wd),str(a)] for (s,wd),a in sorted(row.items())]] for r,row in sorted(rows.items())])}

def run():
    source=json.loads((P/'FROZEN-SOURCES.json').read_text());out={}
    for name,meta in source['files'].items():
        b=(P/name).read_bytes();need(hashlib.sha256(b).hexdigest()==meta['sha256'],'source hash '+name)
        w=json.loads(gzip.decompress(b));out[Path(name).name]=[]
        for d in (False,True):
            out[Path(name).name].append(analyze(w,d));print('checked',Path(name).name,'dual' if d else 'primal',flush=True)
    return {'schema':1,'arithmetic':'exact Fraction; free group reduction; maximum block Hilbert norm','rounding_model':'one arbitrary additive block error after every literal instruction; scalar and native realization obligations external','providers':out}

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--emit');args=a.parse_args();t=time.monotonic()
    if args.emit:
        target=Path(args.emit).resolve();need(target!=P and P not in target.parents,'emit destination must be outside frozen package');need(not target.exists(),'emit destination already exists')
    result=run()
    if args.emit:
        target=Path(args.emit).resolve();need(target!=P and P not in target.parents,'emit destination must be outside frozen package');
        with target.open('x') as out:out.write(json.dumps(result,indent=2,sort_keys=True)+'\n')
    else:need(result==json.loads((P/'RESULT.json').read_text()),'receipt mismatch')
    print('PASS all providers/orientations',round(time.monotonic()-t,3),'seconds',flush=True)
