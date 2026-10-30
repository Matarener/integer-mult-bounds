#!/usr/bin/env python3
"""First hosted-query copy and a source-bound physical ABI obstruction.
Chris R / Clear1nsight with substantial OpenAI Codex assistance. Apache-2.0.
No predecessor executable is loaded.
"""
import argparse
from collections import Counter
import hashlib
from itertools import permutations
import json
from pathlib import Path
HERE = Path(__file__).resolve().parent
PIN_HASH = '86a9b5d16c31a55ba14e656379cade0c1d6f764cff9d582847a539206ab7c8ea'

def need(ok, message):
    if not ok:
        raise ValueError(message)

def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)

def authenticate():
    raw = (HERE / 'PREDECESSORS.json').read_bytes()
    need(hashlib.sha256(raw).hexdigest() == PIN_HASH, 'predecessor manifest hash')
    pins = json.loads(raw)
    for item in pins['files']:
        data = (HERE / item['local']).read_bytes()
        need(hashlib.sha256(data).hexdigest() == item['sha256'], 'source hash: ' + item['local'])
        need(hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest() == item['git_blob'], 'source blob')
    return pins

def parameters(n, lam, owners, width, gap=0):
    need(all(type(x) is int for x in (n, lam, owners, width, gap)), 'integer parameters')
    need(n >= 1 and lam >= 1 and 1 <= owners <= (1 << (n*n)) and width >= 2 and gap >= 0, 'parameter range')
    d = n*n + n*lam
    records = owners * (1 << (n*lam))
    length = d + 2*width + 2
    window = records*length + 2
    return d, records, length, window, window+gap

def payload_positions(d, records, length, width):
    return [1 + j*length + d + 1 + b for j in range(records) for b in range(2*width)]

def expected_bill(d, records, width, displacement):
    p = 2*records*width
    return {'READ': p, 'WRITE': p, 'MOVE': 2*p*displacement + 2*(d+2),
            'TOTAL': 2*p*(displacement+1)+2*(d+2)}

class Tape:
    def __init__(self, cells, origin, allowed):
        self.cells = dict(cells)
        self.head = origin
        self.origin = origin
        self.allowed = allowed
        self.count = Counter()
    def move(self, position):
        while self.head != position:
            self.head += 1 if position > self.head else -1
            need(self.allowed[0] <= self.head <= self.allowed[1], 'exterior move')
            self.count['MOVE'] += 1
    def read(self):
        need(self.allowed[0] <= self.head <= self.allowed[1], 'exterior read')
        self.count['READ'] += 1
        return self.cells[self.head]
    def write(self, bit):
        need(self.allowed[0] <= self.head <= self.allowed[1], 'exterior write')
        self.count['WRITE'] += 1
        self.cells[self.head] = bit

def fixture(n, lam, owners, width, gap=0, origin=0, redundant_read=False, mutant=None):
    d,s,l,c,h = parameters(n,lam,owners,width,gap)
    positions = payload_positions(d,s,l,width)
    # Literal finite-alphabet tagged records; no header/tag is read.
    cells = {origin+j: '_' for j in range(h+c)}
    cells[origin-1] = '$'
    cells[origin+h+c] = '^'
    for base in (origin,origin+h):
        cells[base]='^';cells[base+c-1]='$'
        for j in range(s):
            start=base+1+j*l
            for bit in range(d):cells[start+bit]=(j >> (d-1-bit)) & 1
            cells[start+d]=':';cells[start+l-1]=';'
    for k,x in enumerate(positions):
        cells[origin+x] = (k*k+3*k+k//3+1) % 2
        cells[origin+h+x] = 0
    before = dict(cells)
    machine = Tape(cells,origin,(origin,origin+h+c-1))
    for x in positions:
        machine.move(origin+x)
        bit = machine.read()
        machine.move(origin+h+x+(1 if mutant=='wrong destination offset' else 0))
        if redundant_read:
            need(machine.read() == 0, 'source-proved initial zero')
        machine.write(bit)
    if mutant != 'omit head return':
        machine.move(origin)
    if mutant == 'overwrite source':
        machine.cells[origin+positions[0]] ^= 1
    if mutant == 'overwrite tag':
        machine.cells[origin] = 0
    expected = dict(before)
    for x in positions:
        expected[origin+h+x] = before[origin+x]
    need(machine.cells == expected, 'source/tags/exterior or destination mismatch')
    need(machine.head == origin, 'head return')
    bill = expected_bill(d,s,width,h)
    if redundant_read:
        bill['READ'] += len(positions)
        bill['TOTAL'] += len(positions)
    actual = dict(machine.count)
    actual['TOTAL'] = sum(machine.count.values())
    need(actual == bill, 'literal action invoice')
    return bill

def act(columns, x):
    y = 0
    for i,c in enumerate(columns):
        if (x >> i) & 1:
            y ^= c
    return y

def source_boundary(word, receipt):
    expected = [
        ['clear','Z10','current'], ['add','Z10','W1','1'],
        ['map','Z10',2,1,False], ['line','Z10',1,-1],
        ['add','Z2','Z10','1'], ['add','Z3','Z10','1'],
        ['add','Z5','Z10','-1'], ['add','Z9','Z10','-1']]
    need(word[1704:1712] == expected, 'first query event slice')
    need(word[1697] == ['clear','Z2','query2'], 'paid Z2 initialization')
    need(not any('Z2' in e[1:3] for e in word[1698:1708]), 'Z2 used before first query copy')
    need(receipt['hosting']['aliases']['D']=='Z10' and receipt['hosting']['aliases']['Q1']=='Z2', 'actual hosted roles')
    recipe = [r for r in receipt['native_lowering']['signed_rank_one_recipes'] if 1707 in r['events']]
    need(len(recipe)==1, 'unique actual native recipe')
    r=recipe[0]
    columns=[19,2,4,8,16,32,64,128,256]
    need(r['q']==19 and r['sign']==-1 and r['left_offset']==19 and r['left_columns']==columns and r['right_columns']==columns, 'signed source recipe')
    # Integer numerators are even for 2*delta_x, W>=3. Compare the actual
    # signed kernel to its supplied positive-axis/permutation realization.
    for x in range(512):
        right=act(columns,x)
        wrapped={act(columns,right)^19:(1,1),act(columns,right^1)^19:(1,-1)}
        intended={x:(1,-1),x^19:(1,1)}
        need(wrapped==intended, 'actual native wrapper relation')
    direct_axis={0:(1,-1),1:(1,1)}
    intended={0:(1,-1),19:(1,1)}
    need(direct_axis != intended, 'bare-axis substitution witness')
    return {'source_events':list(range(1704,1712)), 'copy_event':1708,
            'paid_zero_event':1697,'role':'Q1 in Z2','work_bank':'Z10',
            'aligned_add_frame':'F16, axes9 through24',
            'native_q':19,'native_sign':-1,'native_recipe_columns_checked':512,
            'bare_axis_witness':{'input':'2*real delta_0, W>=3', 'correct_nonzero_coordinates':[0,19], 'bare_axis_nonzero_coordinates':[0,1]}}

def compute():
    pins=authenticate()
    word=json.loads((HERE/'vendor/pr4015/WORD.json').read_text())
    receipt=json.loads((HERE/'vendor/pr4015/RESULT.json').read_text())
    need(len(word)==3813,'whole source word length')
    boundary=source_boundary(word,receipt)
    cases=0; totals=0
    for n,lam,owners,width,gap,origin in [(1,1,1,2,0,0),(2,1,1,3,0,-13),(2,1,2,4,7,29),(3,1,1,5,11,101),(2,1,3,3,2,-7)]:
        new=fixture(n,lam,owners,width,gap,origin)
        old=fixture(n,lam,owners,width,gap,origin,True)
        _,s,_,_,_=parameters(n,lam,owners,width,gap)
        need(old['TOTAL']-new['TOTAL']==2*s*width,'zero-destination read saving')
        cases+=2;totals+=new['TOTAL']+old['TOTAL']
    direction_paths=0
    for order in permutations((2,3,7,8)):
        head=0;motion=0
        for x in order:
            motion+=abs(x-head)+12;head=12+x
        motion+=head
        need(motion==2*4*12+2*order[0], 'one-bit shuttle control identity')
        direction_paths+=1
    rejected=[]
    for mutant in ('wrong destination offset','omit head return','overwrite source','overwrite tag'):
        try:fixture(2,1,1,3,2,13,mutant=mutant)
        except ValueError:rejected.append(mutant)
        else:raise ValueError('accepted physical mutant '+mutant)
    bad=[list(e) for e in word];bad[1699]=['add','Z2','Z10','1']
    try:source_boundary(bad,receipt)
    except ValueError:rejected.append('intervening destination use')
    else:raise ValueError('accepted nonzero-query source mutation')
    d,s,l,c,h=parameters(73,1,1,4)
    # Sparse address witness needs no astronomical full-cover allocation.
    first=d+2
    second_tagged=first+l
    second_bare=first+4
    need(second_bare==first+4 and second_bare!=second_tagged,'record-stride obstruction')
    return {'status':'PASS_SCOPED_PHYSICAL_COPY_AND_ABI_OBSTRUCTION',
        'source_boundary':boundary,
        'contract':{'n':'>=1','lambda':'>=1','M':'>=1','W':'>=2 stored bits/component',
          'S':'M*2^(n*lambda)','d':'n*n+n*lambda','L':'d+2*W+2','C':'S*L+2',
          'H':'C+gap, gap>=0','P':'2*S*W',
          'source_window':'[a,a+C-1]','destination_window':'[a+H,a+H+C-1]',
          'initial_and_final_head':'a','owned_gap':'included in traversable envelope',
          'buffers':0,'other_five_tapes':'arbitrary unchanged spectators'},
        'exact_cell_actions':{'READ':'P','WRITE':'P','MOVE':'2*P*H+2*(d+2)','TOTAL':'2*P*(H+1)+2*(d+2)'},
        'saving_against_identical_copy_with_destination_read':'P=2*S*W READ actions, no movement credit',
        'finite_meter':{'cases':cases,'cell_actions':totals,'paired_transfer_orders':direction_paths,'controls':rejected},
        'abi_obstruction':{'first_symbol':'^ rather than a two-complement bit',
          'n73_lambda1_W4':{'d':d,'L':l,'first_real_payload_offset':first,
                            'second_tagged_real_offset':second_tagged,'second_bare_real_offset':second_bare,
                            'misread_field':'first imaginary component, e.g. 1 instead of second real component0'},
          'independent_origin_translation':'cannot change stride L to W or split one payload tape into two heads',
          'native_wrapper':'q19 negative recipe cannot be replaced by a bare coordinate axis'},
        'scope':{'proved':'one conditional local physical copy and direct-composition obstruction',
          'unknown':['actual caller windows/head placement','signed-grid and range at1707','tag/raw reformat','native wrapper movement','map1706 full physical admission','remaining accumulations/consumer/whole supplier'],
          'no_new_kappa':True,'no_global_optimality':True},
        'predecessor_heads':{str(r['pr']):r['head'] for r in pins['files']}}

def main():
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');args=p.parse_args()
    out=HERE/'RESULT.json'
    if args.write:need(not out.exists(),'refuse overwrite')
    result=compute()
    if args.write:
        need(not out.exists(),'refuse overwrite');out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    else:need(canonical(json.loads(out.read_text()))==canonical(result),'typed complete receipt')
    print('PASS_QQ16_PHYSICAL_TRANSITION no_new_kappa')
if __name__=='__main__':main()
