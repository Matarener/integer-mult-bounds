"""Compose the exact PR5601 component with an already changed public word.

Adapted from Ali Romman's PR5601 constructor, using the event-lattice method
credited to DreamingOfClouds and the PR5565 cascade by Pierre-Loic Doulcet.
Literal unique scalar contacts replace stale source sequence offsets. All
other details of the public-anchor reassembly are retained. Prepared for
flyingviper with OpenAI Codex assistance; Apache-2.0.
"""
from collections import defaultdict
from copy import deepcopy


def need(ok,why):
    if not ok:raise ValueError(why)


def construct(source,declaration):
    need(len(declaration['changes'])==4,'Four retained PR5601 declarations')
    need(len(source['frames'])==1089,'Unchanged predecessor frame inventory')
    word=deepcopy(source)
    word['frames'].extend(declaration['frames'])
    old,new=source['program'],word['program']
    for change in declaration['changes']:
        if 'event' in change:
            need(old.count(change['old'])==1,'Unique retained scalar contact')
            i=old.index(change['old'])
            new[i][-1]=change['new_frame']
        else:
            key,r=change['endpoint'],change['register']
            need(word[key][r]==change['old_frame'],'Retained productive endpoint')
            word[key][r]=change['new_frame']
    anchors={r:[(-1,source['initial'][r],word['initial'][r])]
             for r in range(source['public'])}
    moves=defaultdict(list)
    for i,event in enumerate(old):
        op,r=event[:2]
        if op=='MOVE':moves[r].append(i)
        elif op in ('ADD','COPY','SCALE'):
            registers=event[1:3] if op!='SCALE' else event[1:2]
            for r in registers:
                if r in anchors:anchors[r].append((i,event[-1],new[i][-1]))
    remove,before=set(),defaultdict(list)
    for r,visits in anchors.items():
        visits.append((len(old),source['final'][r],word['final'][r]))
        for (i,a,x),(j,b,y) in zip(visits,visits[1:]):
            if (a,b)==(x,y):continue
            remove.update(k for k in moves[r] if i<k<j)
            if x!=y:before[j].append(['MOVE',r,x,y,False])
    program=[]
    for i,event in enumerate(new):
        program.extend(before[i])
        if i not in remove:program.append(event)
    program.extend(before[len(old)])
    word['program']=program
    need(len(program)==len(old)-1,'One fewer paid transport after composition')
    return word
