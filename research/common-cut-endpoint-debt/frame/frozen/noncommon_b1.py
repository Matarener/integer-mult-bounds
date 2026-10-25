#!/usr/bin/env python3
"""All-input ordered B1 clearance with legal-cut insertions H,Z.
Apache-2.0. Substantial OpenAI Codex assistance.
"""
import argparse,json
from pathlib import Path
from o2_composition import ident,left,add,serial,iw,gate_apply
HERE=Path(__file__).resolve().parent

def need(b,m):
 if not b:raise ValueError(m)
def replay(word,rows=None,reverse=False):
 z=ident(2)if rows is None else rows
 for g in reversed(word)if reverse else word:z=gate_apply(z,g,reverse)
 return z

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--write',action='store_true');a=ap.parse_args()
 word=[]
 def L(dst,w):word.append({'op':'LEFT','dst':dst,'word':w})
 def A(dst,src,q):word.append({'op':'ADD','dst':dst,'src':src,'q':q})
 # A0,A1,A2,H,Z are independent noncommuting invertible operators1..5.
 L(0,[-1]);L(0,[1]);A(1,0,1);L(0,[-1]);L(1,[4,-1])
 L(0,[-2,4]);L(1,[-2]);A(0,1,-1);L(1,[2]);L(1,[5,-2])
 L(0,[-3,5]);L(0,[3]);A(1,0,1);L(0,[-3]);L(1,[-3]);word.append({'op':'EXCHANGE','pair':0})
 z=replay(word);E=(-3,5,-2,4,-1);want=[left(r,E)for r in ident(2)]
 need(z==want,'two arbitrary input columns with independent ordered operators')
 need(replay(word,z,True)==ident(2),'complete literal reverse-inverse')
 bad=word[:];del bad[9];need(replay(bad)!=want,'omit current V1 pullback rejected')
 out={'status':'PASS_NONCOMMUTING_B1_COMMONCUT_INSERTION_WORD','generators':{'1':'A0','2':'A1','3':'A2','4':'H','5':'Z'},'word':word,'endpoint_rows':serial(z),'endpoint':'diag(E,E), E=A2^-1 Z A1^-1 H A0^-1',
 'all_size_scope':'Written exact identity over the integer group algebra of five freely noncommuting invertible operators, hence valid on arbitrary fields whenever the declared local boxes and cut insertions are supplied.',
 'cuts':'Same pre-X/post-Y pattern on both orientations. H must be unary native0 on both bank fronts afterstage0; Z similarly afterstage1. The remaining A_s^-1 factors require Xfuture/Ypast admission. No native gate is free merely because the algebra closes.',
 'limits':['No full-native terminal endpoint or favorable paid invoice is supplied by this free-word identity.','The bounded current-cut searches are separate rank screens, not proof for all H/Z.'],'attribution':'This lane derives ordered clearance and exact reverse-inverse; complex supplies actual OPEN inverse alphabet; root requests noncommon-code escape beyond the disjoint principal-block model.'}
 out=json.loads(json.dumps(out));p=HERE/'NONCOMMON-B1.json'
 if a.write:p.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
 else:need(json.loads(p.read_bytes())==out,'stored B1 word differs')
 print(out['status']);print('2 arbitrary columns,5 free operators; inverse/control PASS')
if __name__=='__main__':main()
