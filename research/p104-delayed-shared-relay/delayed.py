"""Explicit shared-component preparation and cleanup, with exact source pins.

Prepared for flyingviper with substantial OpenAI Codex assistance and independent
agent derivations. Apache-2.0. The source word retains the P104 authorship in
PR5580. PR5605 supplies the shared587 relay; the optional commuting parent
also includes Pierre-Loic Doulcet's PR5565 cascade. No search is performed.
"""
from copy import deepcopy
from hashlib import sha256
import json

SOURCES={
 '95078b95bae0c56927f6daaa4430457cc43862c24a9db3b015bb1366e3381055':
   ('PR5605',25167,'56425e27d8f115a6d5ad80ae207947172fbe65aab6712b633ebbd26f18a98f96'),
 '3539111e4b2b5b1316746058bf25d973c4f0b9d91ed577a4d004975eb67320db':
   ('PR5605 with the explicit PR5565 commuting cascade',25160,
    'd920c1c5dc31aedf9ed8ca5174adf7c9364993f9a003be1f2a033d23186636a3'),
}

def digest(word):
 return sha256(json.dumps(word,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def need(ok,why):
 if not ok:raise ValueError(why)

def construct(source):
 pin=digest(source)
 need(pin in SOURCES,'Exact frozen source word')
 _,events,expected=SOURCES[pin]
 need(source['public']==735 and len(source['program'])==events,'Source inventory')
 need(all(source['initial'][r]==3 for r in [159,222,696,700,734]),'Zero-frame boundary roles')
 need(all(source['final'][r]==127 for r in [133,696,697,698,700,703]),'Full-frame cleanup roles')
 original=source['program']
 removed=[['MOVE',696,3,1031,False],['ADD',696,699,'-1',1031],
          ['ADD',696,701,'1',1031],['ADD',696,702,'1',1031],
          ['MOVE',738,591,565,True],['ADD',159,738,'-1',565]]
 late_move=['MOVE',738,565,597,True]
 zero_marker=['ADD',222,696,'1/2',3]
 line_marker=['ADD',734,738,'1',597]
 cleanup_marker=['ADD',133,288,'1/2',127]
 need(all(original.count(e)==1 for e in removed+[late_move,zero_marker,line_marker,cleanup_marker]),
      'Unique literal edit markers')
 program=[['ADD',r,s,str(c),3]for r,c in [(159,-1),(222,1)]for s in [696,700]]
 for event in original:
  if event==cleanup_marker:
   for r,c in [(697,'-1/2'),(698,'1/2'),(703,'-1/2')]:
    program.extend([['ADD',r,696,c,127],['ADD',r,700,c,127]])
   program.extend([['SCALE',700,'1/2',127],['ADD',700,696,'-1/2',127],['ADD',696,133,'1/2',127]])
  if event not in removed:
   program.append(['MOVE',738,591,597,True] if event==late_move else deepcopy(event))
  if event==zero_marker:
   program.extend([['ADD',696,700,'1',3],['ADD',696,734,'-1',3]])
  if event==line_marker:
   program.extend([
    ['MOVE',696,3,597,False],['ADD',696,734,'1',597],
    ['MOVE',696,597,1031,False],['ADD',696,699,'-1',1031],['ADD',696,700,'-1',1031],
    ['ADD',703,696,'1',1031],['ADD',703,700,'1',1031],['ADD',703,699,'1',1031],
    ['SCALE',700,'2',1031],['ADD',700,696,'1',1031],['ADD',700,699,'1',1031]])
 word=deepcopy(source);word['program']=program
 need(len(program)==events+20 and digest(word)==expected,'Exact constructed payload')
 return word
