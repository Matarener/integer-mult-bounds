"""Explicit composition: shared587 relay, PR5565 cascade, 13 PR5599 splits.

The source is Ali Romman's PR5580 word. The commuting cascade is Pierre-Loic
Doulcet's PR5565; the independent helper splits and split operation are Ali
Romman's PR5599. The shared relay and this checked composition were prepared
for flyingviper with substantial OpenAI Codex and independent-agent assistance.
Apache-2.0. Retain the complete predecessor notices in publication.

No search or heuristic event matching is used. The supplied thirteen witnesses
are the frozen adapted cascade-relay-13splits-SPLITS.json. `split` is the pinned
PR5599 split function, which verifies each full prefix and suffix over Q.
"""
from copy import deepcopy
from fractions import Fraction as Q


def need(ok,why):
    if not ok:raise ValueError(why)


def construct_parent(base):
    old=base['program']
    need(base['public']==735 and len(old)==25140,'Exact PR5580 source inventory')
    need(base['initial'][531]==597 and base['final'][531]==127,'Original531 endpoints')
    replacement={
        13413:[old[13413],['MOVE',738,565,597,True]],
        13414:[],13415:[],13416:[],13417:[],13418:[],13420:[],
        13524:[['ADD',113,531,'1',3],['MOVE',113,3,597,False]],
        13528:[['ADD',198,648,'1/2',3],['ADD',198,649,'-1/2',3],
               ['ADD',198,650,'1/2',3],['ADD',198,652,'1/2',3],
               ['MOVE',198,3,597,False]],
        13610:[old[13610],['MOVE',587,3,597,False],['ADD',587,734,'-4',597]],
        13624:[],13625:[],13627:[],13628:[],13630:[],13631:[],13633:[],13634:[],
        13770:[['MOVE',648,3,120,False]],13772:[['MOVE',649,3,120,False]],
        13774:[['MOVE',650,3,120,False]],13778:[['MOVE',652,3,120,False]],
        13806:[],13842:[],13843:[['ADD',197,531,'-1',3]],
        13844:[['MOVE',197,3,355,False]],13845:[],13846:[['ADD',197,319,'1',355]],
        14010:[old[14010],['MOVE',587,597,652,False],['ADD',21,587,'1',652]],
        14017:[['MOVE',148,467,655,False]],
        14378:[['MOVE',319,355,728,False]],14403:[],
        14404:[['ADD',507,531,'-1',3]],14405:[['MOVE',507,3,728,False]],
        14477:[['MOVE',531,3,741,False]],14633:[],14634:[],
        14635:[['MOVE',587,652,773,False]],14684:[['MOVE',197,355,788,False]],
    }
    # The immutable source is byte-authenticated by the caller. These sentinel
    # checks also make the cut conventions explicit and catch wrong indexing.
    expected={13413:['ADD',159,738,'-1',565],
              13610:['ADD',147,587,'1/2',3],
              14010:['ADD',165,21,'-1/2',652],
              14635:['MOVE',587,597,773,False]}
    need(all(old[i]==event for i,event in expected.items()),'Exact source sentinel events')
    affected={123:Q(1,2),148:Q(-1,2),175:Q(-1,2),182:Q(-1,2),203:Q(1,2),223:Q(-1,2)}
    program=[['ADD',r,s,str(-u*v),3] for r,u in sorted(affected.items())
             for s,v in ((587,Q(1)),(734,Q(-4)))]
    for i,event in enumerate(old):
        if i==24461:
            for r,sign in ((21,-1),(47,-1),(434,1),(435,1),(436,1),(437,1)):
                program.extend([['ADD',r,133,str(sign),127],
                                ['ADD',r,587,str(Q(sign,2)),127],
                                ['ADD',r,734,str(-2*sign),127]])
        program.extend(deepcopy(replacement.get(i,[event])))
    word=deepcopy(base)
    word['initial'][531]=3
    word['program']=program
    need(len(program)==25160,'Exact composed pre-split event inventory')
    return word


def construct(base,witnesses,split):
    need(len(witnesses)==13,'Thirteen retained explicit split witnesses')
    word=construct_parent(base)
    for witness in witnesses:
        word=split(word,witness)
    need(word['public']==748 and len(word['program'])==25502,'Exact final composed inventory')
    return word
