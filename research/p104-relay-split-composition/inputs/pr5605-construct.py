"""Reconstruct the shared587 relay from the frozen PR5580 word.

Prepared for flyingviper with substantial OpenAI Codex assistance and
independent agents. Source word: Ali Romman and the retained P104 lineage.
Apache-2.0.
"""
from copy import deepcopy


def need(ok, why):
    if not ok:
        raise ValueError(why)


def construct(base):
    old = base['program']
    need(len(old) == 25140, 'Pinned PR5580 event count')
    expected = {
        13413: ['ADD',159,738,'-1',565],
        13414: ['MOVE',738,565,564,True],
        13415: ['ADD',203,738,'2',564],
        13416: ['MOVE',148,467,596,False],
        13417: ['MOVE',738,564,596,True],
        13418: ['ADD',148,738,'2',596],
        13420: ['MOVE',738,596,597,True],
        14010: ['ADD',165,21,'-1/2',652],
        14017: ['MOVE',148,596,655,False],
        14633: ['MOVE',587,3,597,False],
        14634: ['ADD',587,734,'-4',597],
        14635: ['MOVE',587,597,773,False],
    }
    need(all(old[i] == e for i,e in expected.items()), 'Pinned changed source events')
    affected = {123: '1/2',148: '-1/2',175: '-1/2',182: '-1/2',203: '1/2',223: '-1/2'}
    # Q = I-uN, N=e587-4e734. Supports are disjoint, so these ADDs
    # implement the exact nilpotent inverse without implementation feedback.
    from fractions import Fraction as Q
    out = [['ADD',r,s,str(-Q(u)*v),3]
           for r,u in sorted(affected.items()) for s,v in ((587,Q(1)),(734,Q(-4)))]
    remove = {13414,13415,13416,13417,13418,13420,14633,14634}
    for i,e in enumerate(old):
        if i == 24461:
            # Undo the shared residual while all six targets and three
            # unmodified sources coexist at the full frame.
            for r,sign in ((21,-1),(47,-1),(434,1),(435,1),(436,1),(437,1)):
                out += [['ADD',r,133,str(sign),127],
                        ['ADD',r,587,str(Q(sign,2)),127],
                        ['ADD',r,734,str(-2*sign),127]]
        if i not in remove:
            out.append(['MOVE',587,652,773,False] if i == 14635 else
                       ['MOVE',148,467,655,False] if i == 14017 else deepcopy(e))
        if i == 13413:
            out.append(['MOVE',738,565,597,True])
        if i == 13610:
            out.extend(deepcopy([old[14633],old[14634]]))
        if i == 14010:
            out.extend([['MOVE',587,597,652,False],['ADD',21,587,'1',652]])
    word=deepcopy(base)
    word['program']=out
    need(len(out) == 25167, 'Exact reconstructed event count')
    return word
