#!/usr/bin/env python3
"""A source-bound 896-H1 terminal inverse with explicit common-FULL work.

The native lines and finite phase normalization are checked. Complete all-size
hosting, precision, address/tape realization and supplier admission remain open.
Apache-2.0. Substantial OpenAI Codex assistance under the user's direction.
"""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
from importlib.util import module_from_spec, spec_from_file_location
import argparse
import gzip
import json
import modern_native_component as c

PHASE_SHA = 'c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa'
AXES = tuple(1 << i for i in range(73))


def read_module(path, name):
    spec = spec_from_file_location(name,path)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def bits(x):
    while x:
        b = x & -x
        yield b.bit_length()-1
        x ^= b


def act(cols,x):
    out = 0
    for i in bits(x):
        out ^= cols[i]
    return out


def signature(lines, shift=0):
    linear = [2*((shift >> i)&1) for i in range(73)]
    cross = [0]*73
    for axis,sign in lines:
        support = tuple(bits(axis))
        for i in support:
            linear[i] = (linear[i]+sign)%4
            if sign % 2:
                for j in support:
                    if j > i:
                        cross[i] ^= 1 << j
    return tuple(linear),tuple(cross)


def native_routes(phases, ports):
    """Reconstruct all nine routes and check every literal native alignment."""
    c.need(phases['m'] == 73 and phases['ports'] == len(phases['recipes']) == 112,'phase dimensions')
    routes, checked, nonzero, side_equal = {},0,0,0
    for p,record in enumerate(phases['recipes']):
        q = ports[p]
        c.need(record['port'] == p and record['q'] == q,'modern normal/phase binding')
        chart = tuple(record['idle_children'][0]['orthogonal_axes'][:8])
        basis = (q,)+chart
        c.need(all((a&b).bit_count()%2 == (i==j) for i,a in enumerate(basis) for j,b in enumerate(basis)), 'orthonormal nine-axis chart')
        beta = sum(1<<i for i,v in enumerate(chart) if (v.bit_count()-1)//2 % 2)
        for stage in range(9):
            if stage == 0:
                cols,entry,exit_ = AXES,0,0
            else:
                swaps = [v ^ AXES[9+8*(stage-1)+i] for i,v in enumerate(chart)]
                cols = tuple(x ^ act(swaps,sum(((x&s).bit_count()%2)<<i for i,s in enumerate(swaps))) for x in AXES)
                entry = q ^ act(chart,beta)
                exit_ = act(chart,beta) ^ (beta << (9+8*(stage-1)))
            c.need(all(act(cols,act(cols,x)) == x for x in AXES) and act(cols,q)==q,'route inverse and fixed normal')
            c.need(all((a&b).bit_count()%2 == (i==j) for i,a in enumerate(cols) for j,b in enumerate(cols)), 'orthogonal owner route')
            alignment = record['stage_alignment'][stage]
            c.need(alignment == {'entry_X':entry,'entry_Y':entry,'exit_X':exit_,'exit_Y':exit_}, 'literal source translations')
            side_equal += 1
            nonzero += 2*int(entry!=0)+2*int(exit_!=0)
            ext = [(x,1) for x in AXES[9:9+8*stage]]
            old_x = [(q,1)] if stage==0 else [(x,1) for x in AXES[:1+8*stage]]
            old_y = [] if stage==0 else old_x+[(q,-1)]
            new_x = [(x,1) for x in AXES[:9+8*stage]]
            new_y = new_x+[(q,-1)]
            local_in = ([(q,1)]+ext,ext)
            local_out = ([(x,1) for x in AXES[:9]]+ext,
                         [(x,1) for x in AXES[:9]]+ext+[(q,-1)])
            for side,(old,new) in enumerate(((old_x,new_x),(old_y,new_y))):
                c.need(signature([(act(cols,x),s)for x,s in old],act(cols,entry)) == signature(local_in[side]), 'native entry phase identity')
                c.need(signature(local_out[side],act(cols,exit_)) == signature([(act(cols,x),s)for x,s in new]), 'native exit phase identity')
                checked += 2
            # Preserve native alignments separately from the logical owner map.
            routes[f'{stage}:{p}'] = {'stage':stage,'port':p,'owner_right_matrix_columns':list(cols),
                'logical_payload_translation':0,'entry_payload_translation':entry,'exit_payload_translation':exit_,
                'action':'out(d,z_1,...,z_lambda)=in(d*g,z_1 XOR d*delta,...,z_lambda XOR d*delta)',
                'amplitude_phase':0}
    c.need(checked == 4032 and side_equal == 1008,'full phase coverage')
    return routes,{'native_phase_identities':checked,'actual_routes':len(routes),
        'nonzero_alignment_translations':nonzero,'equal_X_Y_source_alignment_pairs':side_equal,
        'normalization':'A_entry D_old=D_local_entry D(rho,0); A_exit D_new=D_local_exit D(rho,0). Source codes act at a port-independent local I/exterior or FULL/exterior gauge.'}


def monomial_record(rows,offset=0):
    return {'matrix_rows':list(rows),'quadratic_rows':[0]*9,'linear_Z4':[0]*9,'offset':offset,'phase':0}


def all_lines(ports,native):
    out,columns,compositions = {},0,0
    for p,q in enumerate(ports):
        matrix = native.transpose(native.extend((q,),9))
        inv = native.inverse(matrix)
        c.need(native.mul(matrix,1)==q,'line chart image')
        for sign in (1,-1):
            recipe = {'rank':1,'left':monomial_record(matrix,0 if sign==1 else q),
                      'right':monomial_record(inv)}
            actual,expected = native.recipe(recipe),(('C',q,sign),)
            native.equal(actual,expected,'all-port signed native line')
            for col in range(512):
                c.need(native.state(actual,col)==native.state(expected,col),'all-port Gaussian column')
                columns += 1
            c.need(native.state(actual+(('phase',1),)) != native.state(expected),'native phase control')
            c.need(native.state(actual) != native.state((('C',q,-sign),)),'native sign control')
            native.equal(native.fourier(9)+actual,actual+native.fourier(9),'native FULL commutation')
            compositions += 1
            out[f'{p}:{sign}']={'port':p,'label':q,'sign':sign,'recipe':recipe,
                'extension':'Tensor over lambda layers; identity on the other64 axes of the73-axis cover.'}
    c.need(columns == 114688,'complete signed line columns')
    return out,{'signed_recipes':224,'exact_Gaussian_columns':columns,
                'native_FULL_commutations':compositions,'phase_controls_rejected':224,'sign_controls_rejected':224}


def bank_word(events, backwards=False):
    out = []
    for event in (reversed(events) if backwards else events):
        if event['kind']=='local':
            pair,back = event['pair'],event['reverse']
            dst,src,coeff = (2*pair,2*pair+1,-1) if back else (2*pair+1,2*pair,1)
            changes = [(dst,src,coeff)]
        else:
            c.need(event['kind']=='bridge','ordinary prefix event')
            d,s,a = event['dst'],event['src'],event['coefficient']
            changes = [(2*d,2*s,a),(2*s+1,2*d+1,-a)]
        for dst,src,coeff in changes:
            for p in range(112):
                out.append(c.scalar(('L',112*dst+p),('L',112*src+p),Q(-coeff if backwards else coeff),1))
    return out


def bank_matrix(events):
    """Read the emitted portwise scalar word as an exact eight-bank matrix."""
    rows = [{j:Q(1)} for j in range(8)]
    c.need(len(events)%112==0,'bank word complete port sweeps')
    for i in range(0,len(events),112):
        first=events[i]
        c.need(first[0]=='scalar' and first[1][0]=='add' and first[2]==1,'bank prefix literal grammar')
        gate=first[1]
        d,s=gate[1][1]//112,gate[2][1]//112
        value=Q(gate[3],gate[4])
        c.need(events[i:i+112]==[c.scalar(('L',112*d+p),('L',112*s+p),value,1)for p in range(112)],'all112 prefix ports')
        c.add(rows[d],rows[s],value)
    return rows


def terminal_types(program,routes,lines):
    cur={('L',r):('HOLE' if r//112 in (0,2,4,6) else 'FULL')for r in range(896)}
    private={}
    lines_seen=[]
    for e in program:
        if e[0]=='native_line':
            _,reg,key,old,new=e
            reg=tuple(reg)
            item=lines[key]
            c.need(reg[0]=='L' and reg[1]%112==item['port'] and reg[1]//112 in (0,2,4,6),'line actual bank/port')
            c.need(cur[reg]==('HOLE' if old=='FULL_HOLE' else 'FULL'),'native line entry gauge')
            c.need((old,new)==(('FULL_HOLE','FULL')if item['sign']==1 else('FULL','FULL_HOLE')),'native line orientation')
            c.need(not private,'native line with live query scratch')
            cur[reg]='HOLE' if new=='FULL_HOLE' else 'FULL'
            lines_seen.append((reg,item['sign']))
        elif e[0]=='cover_map':
            _,reg,key,shift=e
            reg=tuple(reg)
            c.need(cur[reg]=='FULL' and not private,'route outside uniform FULL')
            c.need(reg[1]%112==routes[key]['port'] and shift==routes[key]['logical_payload_translation']==0,'logical route binding')
        else:
            c.need(e[0]=='scalar','unknown terminal event')
            gate,frame=e[1:]
            target=tuple(gate[1])
            if gate[0]=='clear':
                c.need(target==('C',0),'unowned terminal scratch clear')
                if frame==0:private.pop(target,None)
                else:
                    c.need(frame==1,'query FULL reset')
                    private[target]='FULL'
            else:
                c.need(gate[0]=='add' and frame==1,'terminal scalar grammar')
                for r in (target,tuple(gate[2])):
                    c.need((cur if r[0]=='L' else private).get(r)=='FULL','terminal scalar crosses gauges')
    expected=[(('L',112*b+p),sign)for sign in (1,-1)for b in(0,2,4,6)for p in range(112)]
    c.need(lines_seen==expected and not private,'terminal native inventory and cleanup')
    c.need(all(t==('HOLE' if r//112 in(0,2,4,6)else'FULL')for (_,r),t in cur.items()),'terminal restores all896 bank gauges')
    return {'live_data_fields':896,'persistent_helper_contacts':0,'owned_query_fields':1,
            'line_events':len(lines_seen),'terminal_gauges_restored':True}


def right_code(R,A,pair,back):
    target = 2*pair+(1 if back else 0)
    out=[]
    for k,row in enumerate(R):
        out.append(c.clear(1))
        for p,v in sorted(row.items()):
            out.append(c.scalar(('C',0),('L',112*target+p),v,1))
        for p,image in enumerate(A):
            if k in image:
                if back:
                    out.append(c.scalar(('L',224*pair+p),('C',0),image[k],1))
                out.append(c.scalar(('L',112*target+p),('C',0),image[k],1))
        out.append(c.clear(0))
    return out


def local_right_check(R,A):
    G=c.matmul(A,R)
    for p,row in enumerate(G):c.add(row,{p:Q(1)})
    for back in (False,True):
        events=right_code(R,A,0,back)
        actual=c.replay(events)
        doubled=c.replay(events+events)
        for p in range(632):
            want={(p,()):Q(1)}
            if not back and p<112:
                want={(j,()):v for j,v in G[p].items()}
            elif back and p<112:
                c.add(want,{(112+j,()):v for j,v in G[p].items()})
                c.add(want,{(112+p,()):Q(-1)})
            elif back and p<224:
                want={(112+j,()):v for j,v in G[p-112].items()}
            c.need(actual['L',p]==want,'right-code exact endpoint')
            c.need(doubled['L',p]=={(p,()):Q(1)},'right-code complete square')
        c.need(all(not row for (kind,_),row in actual.items() if kind in 'CZ'),'right-code scratch zero')
    return G


def decoder_program(recipe,R,A,routes):
    prefixes,seen = {},[]
    stages={}
    for event in recipe:
        if event['kind']=='exchange':break
        if event['kind']=='local':
            prefixes[event['stage']]=seen.copy()
            stages[event['stage']]=event
        seen.append(event)
    out=[]
    for bank in (0,2,4,6):
        for p in range(112):
            out.append(['native_line',['L',112*bank+p],f'{p}:1','FULL_HOLE','FULL'])
    blocks=[]
    for stage in range(8,-1,-1):
        event=stages[stage]
        prefix=bank_word(prefixes[stage])
        unprefix=bank_word(prefixes[stage],True)
        pmat,ipmat=bank_matrix(prefix),bank_matrix(unprefix)
        eye=[{i:Q(1)}for i in range(8)]
        c.need(c.matmul(pmat,ipmat)==c.matmul(ipmat,pmat)==eye,'literal ordinary prefix both inverse orders')
        # P_j = D(rho_j,0) times the complete ordinary bank prefix. Route both
        # active banks so the backward right factor's two image banks agree.
        maps=[]
        if stage:
            for bank in (2*event['pair'],2*event['pair']+1):
                for p in range(112):
                    maps.append(['cover_map',['L',112*bank+p],f'{stage}:{p}',0])
        core=right_code(R,A,event['pair'],event['reverse'])
        block=prefix+maps+core+list(reversed(maps))+unprefix
        out.extend(block)
        blocks.append({'stage':stage,'pair':event['pair'],'reverse':event['reverse'],
            'ordinary_prefix_events':len(prefixes[stage]),'scalar_bill':c.scalar_bill(block),
            'inplace_owner_maps':2*len(maps),'conjugation':'E_j=P_j^-1 C_j P_j; execute P_j, C_j, P_j^-1',
            'right_factor':'I+(ex+ey)ey^T tensor(G-I)' if event['reverse'] else 'I+ex ex^T tensor(G-I)'})
    for bank in (0,2,4,6):
        for p in range(112):
            out.append(['native_line',['L',112*bank+p],f'{p}:-1','FULL','FULL_HOLE'])
    c.need(sum(e[0]=='native_line' for e in out)==896,'terminal recursive line count')
    c.need([x['stage'] for x in blocks]==list(range(8,-1,-1)),'inverse factor order')
    return out,blocks


def main():
    here=Path(__file__).resolve().parent
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--repo',type=Path,default=here.parent/'integer-mult-bounds')
    ap.add_argument('--inputs',type=Path,default=here/'modern-source/inputs')
    ap.add_argument('--out',type=Path,default=here/'terminal-native-results')
    a=ap.parse_args()
    a.out.mkdir(exist_ok=True)
    phase_path=a.repo/'research/pr3190-independent-operator-audit/vendor/DATA-PHASES.json'
    c.need(c.digest(phase_path)==PHASE_SHA,'phase source pin')
    controller_path=a.repo/'research/kappa-consumer-followup/controller/check_controller.py'
    controller=read_module(controller_path,'source_bound_controller')
    bank_result=controller.bank_check()
    receipt=c.read(a.inputs/'NATIVE-RECEIPT.json')
    c.need(c.digest(a.inputs/'NATIVE-RECEIPT.json')==c.NATIVE_RECEIPT_SHA,'modern source pin')
    native,_,_=c.load_native(a.repo/'research/native-source-codes')
    result={'status':'PASS_NATIVE_TERMINAL_OPERATOR_NOT_SUPPLIER_ADMISSION',
        'phase_source_sha256':PHASE_SHA,'controller_source_sha256':c.digest(controller_path),
        'bank_factor_check':bank_result,'providers':{},
        'terminal_convention':'After the final signed exchange: X0,X1,X2,X3 have FULL C_q^-1; Y banks have FULL. Use input-normalized prefix factors.'}
    for name,item in receipt['providers'].items():
        loc=a.inputs/'native-cache'/item['word_sha256']/'local'
        for file in ('CANONICAL-WORD.json.gz','LOCAL-PROGRAMS.json.gz'):
            c.need(c.digest(loc/file)==item['complete_native_files']['local/'+file],'modern local word pin')
        word,programs=c.read(loc/'CANONICAL-WORD.json.gz'),c.read(loc/'LOCAL-PROGRAMS.json.gz')
        R,K,P,J,clean,dirty=c.clean_reconstruction(word,programs)
        A=[]
        for k,p in zip(K,P):
            row={j:-v for j,v in k.items()};c.add(row,p,Q(12));A.append(row)
        c.need(c.matmul(R,A)==[{k:Q(-2)}for k in range(8)],'serial query noninterference')
        local_right_check(R,A)
        routes,phase_result=native_routes(c.read(phase_path),word['ports'])
        lines,line_result=all_lines(word['ports'],native)
        program,blocks=decoder_program(controller.recipe(),R,A,routes)
        type_result=terminal_types(program,routes,lines)
        try:
            terminal_types(program[1:],routes,lines)
        except ValueError:
            type_result['missing_flatten_line_rejected']=True
        else:
            c.need(False,'missing flatten line accepted')
        profile=Counter({1:896})
        result['providers'][name]={'word_sha256':item['word_sha256'],
            'phase_check':phase_result,'native_line_check':line_result,
            'literal_type_check':type_result,
            'recursive_profile':dict(profile),'rank_mass':896,'scalar_bill':c.scalar_bill(program),
            'inplace_owner_maps':sum(x['inplace_owner_maps']for x in blocks),
            'new_helper_fields':0,'reused_serial_zero_query_fields':1,'blocks':blocks}
        payload={'program':program,'routes':routes,'native_lines':lines}
        (a.out/f'DECODER-{name}.json.gz').write_bytes(gzip.compress(json.dumps(payload,sort_keys=True,separators=(',',':')).encode(),mtime=0))
        print('PASS_NATIVE_TERMINAL_DECODER',name,'lines=896 exact_line_columns=114688 phase_identities=4032',flush=True)
    result['complete_child_delta_per_replica']={'1':968,'8':-72}
    result['raw_rank_mass_increase_per_replica']=392
    result['operator_proof']={
        'changed_residual':'D_hole M D_hole^-1, M=E8...E0',
        'flatten':'Q=D_in on X holes, Q D_hole=C_full on every bank',
        'commutation':'Every logical owner map and every physical alignment M(g,delta) changes owner and translates payload without an amplitude phase; it commutes with the same owner-independent convolution C_full.',
        'middle':'Execute E8,E7,...,E0. Each is P_j^-1 C_j P_j, where the finite prefix and actual route inverse are explicit and C_j^2=I is checked on632 columns.',
        'restore':'Apply Q^-1, giving D_hole M^-1 D_hole^-1. This restores ordinary baseline content in the postexchange gauge. Retain any remaining baseline end adapter unchanged; the signed exchange has already been executed once.',
        'tensor_scope':'Line identities tensor over every layer; phase-polynomial identities hold on all73 address bits; scalar/mapped involution identities apply to arbitrary full-cover fields.'}
    result['limitations']=['Positive-child and finite native operator invoice only; no full supplier admission.',
        'Group-route and scalar work is explicit but its physical tape/address and recursive hosting realization is not newly admitted.',
        'The reused single query field must follow the existing owned scratch convention; no additional persistent helper field is assumed.',
        'A complete global precision recurrence and error margins are not supplied.']
    (a.out/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')


if __name__=='__main__':main()
