#!/usr/bin/env python3
"""Independent primitive-call census for the literal unary stencil producer.

No primary verifier or semantic oracle is imported. A read-accounting fault
executes the same program and cell semantics but omits exactly one billed READ.
The observer trace must reject that one-action invoice discrepancy.
"""
import argparse
import ast
from hashlib import sha256
import json
from pathlib import Path

CONSUMER_SHA = '1cb27312932914eb631078bd56e85feb1dc6c4191e9d1962b2cc3a7e1cfb8df7'

def need(test, message):
    if not test:
        raise RuntimeError(message)

def load_code(path):
    raw=path.read_bytes()
    scope={'__file__':str(path),'__name__':'cost_review_component'}
    exec(compile(raw,str(path),'exec',dont_inherit=True,optimize=0),scope)
    return raw,scope

def inspect_control(raw):
    tree=ast.parse(raw)
    need(not any(isinstance(n,(ast.Import,ast.ImportFrom,ast.Subscript,ast.BinOp,ast.AugAssign)) for n in ast.walk(tree)),
         'program acquired imports, indexing or host arithmetic; re-review finite control')
    attrs={n.attr for n in ast.walk(tree) if isinstance(n,ast.Attribute)}
    need(attrs <= {'read','write','move'},'program acquired an observer or nonprimitive attribute')
    direct_calls={n.func.id for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name)}
    need(not direct_calls & {'len','range','enumerate','zip','int','float','sum','min','max','getattr','setattr','eval','exec','compile'},
         'program acquired host data operations')
    return {'primitive_attributes':sorted(attrs),'syntactic_guardrail_only_not_formal_compilation':True}

class World:
    def __init__(self, base_tape, undercharge_one_read=False):
        self.roles=[]
        self.omissions=1 if undercharge_one_read else 0
        world=self
        class ObservedTape(base_tape):
            def __init__(self,cells=None):
                super().__init__(cells)
                self.primitive_reads=self.primitive_writes=self.primitive_moves=0
                self.visited={0}
                world.roles.append(self)
            def read(self):
                self.primitive_reads+=1
                self.visited.add(self.head)
                symbol=super().read()
                if world.omissions:
                    self.reads-=1
                    world.omissions-=1
                return symbol
            def write(self,symbol):
                self.primitive_writes+=1
                self.visited.add(self.head)
                super().write(symbol)
            def move(self,direction):
                self.primitive_moves+=1
                super().move(direction)
                self.visited.add(self.head)
        self.Tape=ObservedTape

    def census(self):
        reads=sum(t.primitive_reads for t in self.roles)
        writes=sum(t.primitive_writes for t in self.roles)
        moves=sum(t.primitive_moves for t in self.roles)
        return {'reads':reads,'writes':writes,'moves':moves,'primitive_actions':reads+writes+moves,
                'reported_actions':sum(t.actions for t in self.roles),
                'visited_cells':sum(len(t.visited) for t in self.roles),'roles':len(self.roles)}

def execute(geometry,producer,base_tape,fault=False):
    world=World(base_tape,fault)
    inputs=[world.Tape(['<']+['1']*n+['>','_']) for n in geometry]
    before=[list(t.cells) for t in inputs]
    work,stencil=producer(*inputs,world.Tape)
    g,h,k,y,j,b=geometry
    length=2*h+y+b
    expected_actions=33*h+25*k+38*y-6*g-j+12*b+335
    expected_space=4*h+2*k+4*y-g+2*b+38
    census=world.census()
    need(census['roles']==15,'producer role inventory')
    need(census['primitive_actions']==expected_actions,'exact macro-composed action invoice')
    need(census['visited_cells']==expected_space,'exact visited-cell invoice')
    need(all(t.head==0 for t in world.roles),'all producer heads return')
    need([t.cells for t in inputs]==before,'protected input changed')
    need(all(t.cells[0]=='<' and all(s=='_' for s in t.cells[1:]) for t in work),'private data/END not blank')
    need(len(stencil.cells)==length+2 and stencil.cells[0]=='<' and stencil.cells[-1]=='>','owned stencil shape')
    if fault:
        need(census['reported_actions']==expected_actions-1,'one READ omission failed to change invoice')
    else:
        need(census['reported_actions']==expected_actions,'nominal observer bill')
    return census,[t.cells[:] for t in world.roles]

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--producer',type=Path,default=Path(__file__).resolve().parent/'producer.py')
    parser.add_argument('--consumer',type=Path,default=Path(__file__).resolve().parent/'source'/'predecessor_machine.py')
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    consumer_raw=args.consumer.read_bytes()
    need(sha256(consumer_raw).hexdigest()==CONSUMER_SHA,'retained consumer immutable hash')
    producer_raw,program=load_code(args.producer)
    _,consumer=load_code(args.consumer)
    control=inspect_control(producer_raw)
    fixtures=[(1,1,5,5,0,0),(1,3,5,9,2,2),(1,1,7,8,1,0),
              (2,2,6,6,0,0),(2,5,9,15,3,4),(3,3,7,7,0,1),
              (3,4,10,16,6,0),(4,8,8,15,7,3),(8,10,12,20,8,4),
              (15,17,21,30,9,2),(31,32,35,40,5,0),(1,80,5,9,4,90),
              (1,1,100,120,20,3),(100,120,104,140,36,20)]
    cases=[]
    for geom in fixtures:
        census,_=execute(geom,program['produce'],consumer['Tape'])
        cases.append({'geometry_G_H_K_Y_J_B':list(geom),**census})
    baseline,baseline_cells=execute(fixtures[0],program['produce'],consumer['Tape'])
    fault,fault_cells=execute(fixtures[0],program['produce'],consumer['Tape'],True)
    need(baseline_cells==fault_cells,'READ billing fault unexpectedly changed semantics/ownership')
    need(fault['primitive_actions']==baseline['primitive_actions'] and fault['reported_actions']!=baseline['reported_actions'],
         'READ billing fault not independently rejected')
    result={'status':'PASS_INDEPENDENT_PRODUCER_ACTION_AND_OWNERSHIP_CENSUS',
            'scope':'Exact affine formulas justified by separate macro proof; finite actual-program primitive-call instrumentation corroborates them. No duplicate semantic oracle or complete caller theorem.',
            'producer_sha256':sha256(producer_raw).hexdigest(),'consumer_sha256':CONSUMER_SHA,
            'code_sha256':sha256(Path(__file__).read_bytes()).hexdigest(),
            'action_formula':'33H+25K+38Y-6G-J+12B+335',
            'visited_cell_formula':'4H+2K+4Y-G+2B+38','cases':cases,'control_guardrail':control,
            'underbilled_READ_control':{'same_actual_program':True,'same_final_cells_and_ownership':True,
                  'primitive_actions':fault['primitive_actions'],'reported_actions':fault['reported_actions'],
                  'omitted_READ_actions':1,'invoice_rejected':True},
            'limits':['finite-control AST check is a guardrail, not a formal compiler certificate',
                      'canonical distinct protected unary role inputs with blank tails are an interface premise',
                      'no full many-target/transformed-descriptor/caller E evaluation or outer theorem']}
    payload=json.dumps(result,sort_keys=True,indent=2)+'\n'
    if args.output is not None:args.output.write_text(payload)
    print(json.dumps({k:v for k,v in result.items() if k!='cases'},sort_keys=True))

if __name__=='__main__':main()
