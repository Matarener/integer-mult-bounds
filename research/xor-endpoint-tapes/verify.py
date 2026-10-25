"""Exact transition-table replay and P112 predecessor-mask application.
Dugongue, with substantial OpenAI Codex assistance. Apache-2.0.
"""
from pathlib import Path
from itertools import product
import argparse
import ast
import hashlib
import json

from machine import (BLANK,SEP,compile_machine,compile_inplace,decode,encode,
                     exact_cost,inplace_travel,need,reverse_bits,run,variation)

ROOT=Path(__file__).resolve().parent


def authenticate():
    data=json.loads((ROOT/'INPUTS.json').read_text(encoding='utf-8'))
    for name,digest in data['sha256'].items():
        p=(ROOT/name).resolve()
        need(p.is_relative_to(ROOT) and p.is_file(),'source path')
        need(hashlib.sha256(p.read_bytes()).hexdigest()==digest,'source hash '+name)


def predecessor_masks():
    authenticate()
    tree=ast.parse((ROOT/'inputs/PR3480-verify.py').read_text(encoding='utf-8'))
    literals=[]
    for node in ast.walk(tree):
        if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='expected_deltas' for t in node.targets):
            literals.append(ast.literal_eval(node.value))
    need(len(literals)==1,'unique predecessor mask literal')
    values=literals[0]
    need(len(values)==23 and all(type(d) is int and 0<=d<512 for d in values),'P112 mask shape')
    return values


def check_table(machine):
    need(machine.halt==sum(3 if op=='W' else 2 for op in machine.operations),'finite state count')
    need(all(0<=s<machine.halt and a in range(4) and b in range(4)
             for s,a,b in machine.table),'transition domains')
    for target,w0,w1,m0,m1 in machine.table.values():
        need(0<=target<=machine.halt,'finite control destination')
        if machine.mode=='copy':need(w0 is None,'borrowed input never written')
        else:need(w0 is None or w0 in range(4),'four-symbol data write')
        need(w1 is None or w1 in range(4),'four-symbol alphabet')
        need(m0 in (-1,0,1) and m1 in (-1,0,1),'unit physical steps')
    need(not any(s==machine.halt for s,_,_ in machine.table),'genuine halt has no transition')


def execute(h,delta,records,input_origin=-13,output_origin=21):
    machine=compile_machine(h,delta);check_table(machine)
    source,end=encode(records,input_origin)
    extent=end-input_origin
    source[input_origin-7]=1;source[end+9]=SEP
    output={output_origin+i:(i*3+1)%4 for i in range(extent+1)}
    output[output_origin-8]=0;output[output_origin+extent+17]=1
    original0,original1=source.copy(),output.copy()
    invoice,crossings=exact_cost(machine,records)
    result=run(machine,source,output,input_origin,output_origin,limit=invoice+1)
    got,finish=decode(result['tapes'][1],len(records),output_origin)
    expected=[tuple(records[j^delta]) for j in range(1 << h)]
    need(got==expected,'literal XOR permutation')
    need(finish==output_origin+extent,'exact output framing')
    need(result['steps']==invoice,'exact physical time invoice')
    need(result['heads']==(input_origin,output_origin),'both heads restored')
    need(result['tapes'][0]==original0 and not result['writes'][0],'complete borrowed input preserved')
    need(result['minimum']==(input_origin,output_origin),'no exterior scan on left')
    need(result['maximum']==(end,output_origin+extent),'no exterior scan on right')
    need(result['writes'][1]==set(range(output_origin,output_origin+extent+1)),'exact owned output window')
    need(all(result['tapes'][1][x]==v for x,v in original1.items()
             if not output_origin<=x<=output_origin+extent),'arbitrary dirty exterior preserved')
    need(source==original0 and output==original1,'caller dictionaries preserved')
    return machine,result,crossings


def execute_inplace(h,delta,width):
    machine=compile_inplace(h,delta);check_table(machine)
    n=1 << h
    words=[tuple((j>>(width-1-k))&1 for k in range(width)) for j in range(n)]
    data,end=encode(words,-17)
    scratch,send=encode([tuple((3*k+1)%2 for k in range(width))],31)
    data[-24]=SEP;data[end+7]=1;scratch[22]=0;scratch[send+11]=SEP
    original_data=data.copy();original_scratch=scratch.copy()
    travel=inplace_travel(h,delta)
    invoice=0 if delta==0 else (3*n//2)*(2*width+3)+(width+2)*travel
    result=run(machine,data,scratch,-17,31,limit=invoice+1)
    got,_=decode(result['tapes'][0],n,-17)
    need(got==[words[j^delta] for j in range(n)],'in-place XOR permutation')
    need(result['tapes'][1]==original_scratch,'arbitrary dirty scratch restored')
    need(result['heads']==(-17,31),'in-place heads restored')
    need(result['steps']==invoice,'in-place exact time invoice')
    need(result['minimum'][0]>=-17 and result['maximum'][0]<=end,'in-place data scan window')
    need(result['minimum'][1]>=31 and result['maximum'][1]<=send,'in-place scratch scan window')
    need(all(result['tapes'][0][k]==v for k,v in original_data.items()
             if k < -17 or k > end),'in-place dirty exterior frame')
    need(all(-17<=k<=end for k in result['writes'][0]),'in-place write window')
    need(all(31<=k<=send for k in result['writes'][1]),'scratch write window')
    need(data==original_data and scratch==original_scratch,'caller storage preserved')
    return result['steps']


def run_checks():
    cases=steps=0
    for h in range(6):
        n=1 << h
        for delta in range(n):
            f=[j^delta for j in range(n)]
            direct=sum(abs(b-a) for a,b in zip(f,f[1:]))
            need(variation(h,delta)==direct,'independent variation recurrence')
            direct_q=f[0]+sum(abs(b-a-1) for a,b in zip(f,f[1:]))+f[-1]+1
            need(direct_q==direct+1+2*reverse_bits(delta,h),'bit-reversal travel identity')
            for width in (0,1,3):
                words=[tuple((j+3*k+(j>>1))%2 for k in range(width)) for j in range(n)]
                machine,result,cross=execute(h,delta,words)
                need(sum(cross)==machine.input_travel,'edge scan count')
                need(result['steps']==n*(2*width+4)+(width+2)*direct_q,'fixed-width exact time')
                need(result['steps']<=n*((h+3)*width+2*h+6),'universal time bound')
                cases+=1;steps+=result['steps']
            variable=[tuple((j+k)%2 for k in range(j%5)) for j in range(n)]
            _,result,_=execute(h,delta,variable)
            cases+=1;steps+=result['steps']
    # Full basis corroboration in every small address space.
    basis=0
    for h in range(4):
        n=1 << h
        for delta in range(n):
            for pos in range(n):
                words=[(int(j==pos),) for j in range(n)]
                _,result,_=execute(h,delta,words)
                steps+=result['steps'];basis+=1
    # Literal 23-mask P112 application: these are separate tape instances.
    # This authenticates source masks, not the complete original cover proof.
    literal=[]
    words=[tuple((j>>(8-k))&1 for k in range(9)) for j in range(512)]
    for block,delta in enumerate(predecessor_masks()):
        machine,result,_=execute(9,delta,words)
        literal.append({'block':block,'delta':delta,'input_record_travel':machine.input_travel,
                        'states':machine.halt+1,'transitions':len(machine.table),
                        'time_width_9':result['steps'],
                        'time_coefficient_B':1024+machine.input_travel,
                        'time_constant':2048+2*machine.input_travel,
                        'inplace_record_travel':inplace_travel(9,delta),
                        'inplace_time_coefficient_B':1536+inplace_travel(9,delta),
                        'inplace_time_constant':2304+2*inplace_travel(9,delta)})
        steps+=result['steps']
    inplace_cases=0
    for h in range(5):
        for delta in range(1 << h):
            for width in (0,1,4):
                steps+=execute_inplace(h,delta,width);inplace_cases+=1
    # One literal nine-bit mask, block 10's delta=19, is also fully executed
    # in place. Other nine-bit in-place bills are universal formulas, not runs.
    steps+=execute_inplace(9,19,9);inplace_cases+=1
    return {'schema_version':1,'status':'PASS_XOR_ENDPOINT_TAPES',
            'parameter_cases':cases,'full_small_basis_cases':basis,'literal_masks':23,
            'inplace_parameter_cases':inplace_cases,
            'executed_unit_transitions':steps,'p112':literal,
            'alphabet':['0','1','#','blank'],'tapes':2,
            'uniform_time_bound':'2^h*((h+3)*B+2*h+6)',
            'coverage':'Every transition is a literal finite-control, unit-move two-tape step. Universal proof is in PROOF.md; source/consumer identification and complete recursive invoice remain outside this result.'}


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--emit',action='store_true');args=ap.parse_args()
    result=run_checks()
    if args.emit:print(json.dumps(result,indent=2,sort_keys=True))
    else:
        need(result==json.loads((ROOT/'RESULT.json').read_text(encoding='utf-8')),'result receipt changed')
        print(f"PASS_XOR_ENDPOINT_TAPES parameter_cases={result['parameter_cases']} basis_cases={result['full_small_basis_cases']} literal_masks=23 steps={result['executed_unit_transitions']} RECEIPT_MATCH")


if __name__=='__main__':main()
