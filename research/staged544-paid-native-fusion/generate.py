"""Optional reference recipe generation; not independent verification."""
import gzip,json,sys
from pathlib import Path
P=Path(__file__).resolve().parent
sys.path.insert(0,str(P/'vendor'))
import clifford_exact as c
w=json.load(gzip.open(P/'frozen/WORD-base.json.gz','rt'))
G,U,E=w['warps'][4][2:];V=w['B'][1097][-1]
items=json.loads((P/'frozen/RECIPES.json').read_text())['items']
M=next(x for x in items if x['kind']=='warp' and x['sign']==1 and x['entrance']==U and x['G_columns']==G)['recipe']['left']
child=c.lower_child(c.canonical_frame(9,E).adjoint().then(c.canonical_frame(9,V)))[0]
result=dict(warp_index_zero_based=4,register=333,pre_b_index=1081,consumers=[1081,1082,1083],next_b_index=1097,entrance=U,exit=E,next_frame=V,G_columns=G,warp=M,child=child)
if len(sys.argv)!=2:raise SystemExit('explicit output path required')
Path(sys.argv[1]).write_text(json.dumps(result,indent=2)+'\n')
