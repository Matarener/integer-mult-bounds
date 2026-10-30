# SPDX-License-Identifier: Apache-2.0
"""Neutral fixed-frame first ADD at displacement exactly two, unrestricted second ADD.

Chris R / Clear1nsight, with substantial OpenAI assistance. The pinned
PR3886 trace, applier and sign criterion are reused, not independently authored.
Adapted from PR3942 with its retained source. The interaction reduction is reused.
"""
from bisect import bisect_left
from collections import Counter
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import types

P = Path(__file__).resolve().parent

def module(name, path):
    value = types.ModuleType(name)
    value.__file__ = str(path)
    exec(compile(path.read_bytes(), str(path), 'exec'), value.__dict__)
    return value

# The entry point authenticates these bytes before loading this module.
R = module('pinned_retiming', P / 'vendor/retiming.py')
PHASES = ('A', 'B', 'restore')
ZERO = (0,) * 10
R.all_power_nonnegative = lru_cache(maxsize=None)(R.all_power_nonnegative)

def require(ok, message):
    if not ok:
        raise ValueError(message)

def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()

def rows(histogram):
    result = []
    for delta, count in sorted(histogram.items()):
        caps = R.caps(delta)
        prefixes = [sum(caps[:j]) for j in range(1, 9)]
        require(sum(r*n for r,n in enumerate(delta))==0,'histogram rank mass')
        result.append({'delta': list(delta), 'count': count, 'caps': caps,
                       'prefixes': prefixes, 'certificate': R.all_power_nonnegative(delta)})
    return result

def geometry(word, section, trace=None):
    nodes, where, bill = R.tracing(word) if trace is None else trace
    gates = word[section]
    for lo, hi in R.segments(word, section):
        occurrences = {}
        for i in range(lo, hi):
            for r in R.touched(gates[i]):
                occurrences.setdefault(r, []).append(i)
        entries, exits, removal = {}, {}, {}
        for r, indices in occurrences.items():
            entries[r] = nodes[r][where[((section, indices[0]), r)]][2]
            exits[r] = nodes[r][where[((section, indices[-1]), r)] + 1][3]
        for i in range(lo, hi):
            if gates[i][0] != 'add':
                continue
            delta = [0] * 10
            for r in R.touched(gates[i]):
                seq = nodes[r]
                pos = where[((section, i), r)]
                _, _, before, frame = seq[pos]
                require(seq[pos + 1][1] != 'map', 'missing map-entry check')
                after = seq[pos + 1][3]
                delta[R.rank(frame) - R.rank(before)] -= 1
                delta[R.rank(after) - R.rank(frame)] -= 1
                delta[R.rank(after) - R.rank(before)] += 1
            removal[i] = delta
        yield lo, hi, occurrences, entries, exits, removal

def candidates(word, section, selected, first=False, window=None, trace=None, trusted=False, prepared=None):
    """Exact prices in the predecessor's fixed-check relaxation.

    First moves use cuts i-2 and i+3, hence final displacement exactly two.
    For second moves all permitted corridor cuts and all frame dimensions occur.
    """
    gates = word[section]
    for lo, hi, occurrences, entries, exits, removal in (geometry(word, section, trace) if prepared is None else prepared):
        for i in selected:
            if not lo <= i < hi or gates[i][0] != 'add':
                continue
            gate = gates[i]
            lower, upper = i, i + 1
            if trusted:
                require(window is not None, 'trusted reach requires window')
                lower, upper = max(lo, window[0]), min(hi, window[1])
            else:
                while lower > lo and R.crosses(gate, gates[lower - 1]):
                    lower -= 1
                while upper < hi and R.crosses(gate, gates[upper]):
                    upper += 1
            if window is not None:
                lower, upper = max(lower, window[0]), min(upper, window[1])
            cuts = [c for c in (i - 2, i + 3) if lower <= c <= upper] if first else range(lower, upper + 1)
            reduced = {r: [x for x in occurrences[r] if x != i] for r in R.touched(gate)}
            for cut in cuts:
                if cut == i + 1:
                    continue
                bounds = []
                for r in R.touched(gate):
                    indices = reduced[r]
                    j = bisect_left(indices, cut)
                    before = R.span(tuple(gates[indices[j - 1]][-1])) if j else entries[r]
                    after = R.span(tuple(gates[indices[j]][-1])) if j < len(indices) else exits[r]
                    bounds.append((before, after))
                low = R.join(bounds[0][0], bounds[1][0])
                high = bounds[0][1] & bounds[1][1]
                if not R.contained(low, high):
                    continue
                for dimension in range(R.rank(low), R.rank(high) + 1):
                    delta = removal[i].copy()
                    for before, after in bounds:
                        p, q = R.rank(before), R.rank(after)
                        delta[q - p] -= 1
                        delta[dimension - p] += 1
                        delta[q - dimension] += 1
                    delta[0] = 0
                    require(sum(r * n for r, n in enumerate(delta)) == 0, 'rank mass drift')
                    yield i, cut, dimension, low, high, tuple(delta)

@lru_cache(maxsize=None)
def frames(low, high, dimension):
    """All intermediate subspaces, not one representative per dimension."""
    require(R.contained(low, high), 'empty frame interval')
    require(R.rank(low) <= dimension <= R.rank(high), 'invalid frame dimension')
    require(R.rank(high) - R.rank(low) <= 4, 'first-frame resource bound exceeded')
    current = {low}
    for _ in range(dimension - R.rank(low)):
        expanded = set()
        for frame in current:
            for v in range(1, 512):
                if high >> v & 1 and not frame >> v & 1:
                    expanded.add(R.join(frame, R.span((v,))))
        current = expanded
    return tuple(sorted(current))

def first_moves(word, auditor=None):
    records, counts = [], Counter()
    for section in PHASES:
        gates=word[section]
        for lo,hi in R.segments(word,section):
            for i in range(lo,hi):
                g=gates[i]
                if g[0]!='add':continue
                for cut in (i-2,i+3):
                    if not lo<=cut<=hi:continue
                    crossed=gates[i+1:cut] if cut>i else gates[cut:i]
                    if not all(R.crosses(g,h) for h in crossed):continue
                    counts['scalar_legal_first_records']+=1
                    frame=R.span(tuple(g[-1]))
                    # The source and final sequences are monotone. Every event
                    # sharing a register with the moved gate changes order with
                    # it, hence their frames must agree in both orders.
                    if any(set(R.touched(g))&set(R.touched(h)) and frame!=R.span(tuple(h[-1])) for h in crossed):
                        counts['frame_rejected']+=1;continue
                    counts['legal_first_records']+=1
                    counts['by_'+section]+=1
                    counts['crossed_'+''.join(h[0][0].upper() for h in crossed)]+=1
                    records.append((section,i,cut,frame,ZERO,'neutral_fixed_displacement_two'))
    return records,counts,set()

def corridor_bounds(word):
    result={}
    for sec in PHASES:
        gates=word[sec]
        for lo,hi in R.segments(word,sec):
            for i in range(lo,hi):
                g=gates[i]
                if g[0]!='add':continue
                a,b=i,i+1
                while a>lo and R.crosses(g,gates[a-1]):a-=1
                while b<hi and R.crosses(g,gates[b]):b+=1
                result[sec,i]=(a,b)
    return result

def first_apply(word,section,i,cut):
    # Persistent-copy specialization: no shared source object is mutated.
    from fractions import Fraction
    g=word[section][i].copy()
    coeff=Fraction(g[3],g[4])
    crossed=word[section][i+1:cut] if cut>i else word[section][cut:i]
    for h in crossed:
        if h[0]=='scale' and h[1] in R.touched(g):
            power=(1 if h[1]==g[1] else -1)*(1 if cut>i else -1)
            coeff*=Fraction(h[2],h[3])**power
    g[3:5]=[coeff.numerator,coeff.denominator]
    g[-1]=list(R.basis(R.span(tuple(g[-1]))))
    new=word.copy();new[section]=word[section].copy()
    new[section].pop(i);new[section].insert(cut-(cut>i),g)
    return new

def first_trace(word,middle,baseline,section,i,cut):
    """Reindex just the three changed events, checking local containment."""
    old_nodes,old_where,bill=baseline
    nodes=old_nodes.copy();where=old_where.copy()
    lo,hi=min(i,cut),max(i+1,cut)
    regs={r for g in word[section][lo:hi] for r in R.touched(g)}
    for r in regs:
        old_positions=[j for j in range(lo,hi) if r in R.touched(word[section][j])]
        positions=[old_where[((section,j),r)] for j in old_positions]
        for j in old_positions:del where[((section,j),r)]
        sequence=old_nodes[r].copy();before=sequence[positions[0]][2]
        new_positions=[j for j in range(lo,hi) if r in R.touched(middle[section][j])]
        require(len(positions)==len(new_positions),'event inventory drift')
        for pos,j in zip(positions,new_positions):
            frame=R.span(tuple(middle[section][j][-1]))
            require(R.contained(before,frame),'incremental frame containment')
            sequence[pos]=((section,j),'climb',before,frame)
            where[((section,j),r)]=pos;before=frame
        require(before==old_nodes[r][positions[-1]][3],'block final frame drift')
        nodes[r]=sequence
    return nodes,where,bill

def first_geometry(word,middle,baseline_geometry,trace,section,i,cut):
    """Transport baseline event positions; recompute removals in the block."""
    lo,hi=min(i,cut),max(i+1,cut);nodes,where,_=trace
    out=[]
    for a,b,occ,entry,exit,removal in baseline_geometry:
        if not a<=i<b:out.append((a,b,occ,entry,exit,removal));continue
        new_occ=occ.copy();new_removal=removal.copy()
        regs={r for g in word[section][lo:hi] for r in R.touched(g)}
        for r in regs:
            new_occ[r]=sorted([j for j in occ[r] if not lo<=j<hi]+[j for j in range(lo,hi) if r in R.touched(middle[section][j])])
        for j in range(lo,hi):
            new_removal.pop(j,None)
            if middle[section][j][0]!='add':continue
            delta=[0]*10
            for r in R.touched(middle[section][j]):
                seq=nodes[r];pos=where[((section,j),r)]
                before,frame=seq[pos][2:4];after=seq[pos+1][3]
                delta[R.rank(frame)-R.rank(before)]-=1
                delta[R.rank(after)-R.rank(frame)]-=1
                delta[R.rank(after)-R.rank(before)]+=1
            new_removal[j]=delta
        out.append((a,b,new_occ,entry,exit,new_removal))
    return out

def variable_census(word, variable, auditor=None, progress=False):
    D=module('dirty_blocks',P/'dirty_blocks.py')
    baseline_trace=R.tracing(word);baseline=baseline_trace[2];bounds=corridor_bounds(word)
    baseline_geometry={sec:list(geometry(word,sec,baseline_trace)) for sec in PHASES}
    histogram, counts = Counter(), Counter()
    states, blocks, witnesses = [], [], {}
    for number,(section,i,cut,frame,first_delta,kind) in enumerate(variable):
        middle=first_apply(word,section,i,cut)
        trace=first_trace(word,middle,baseline_trace,section,i,cut)
        require(trace[2]==baseline,'fixed-frame first invoice not neutral')
        lo,hi=min(i,cut),max(i+1,cut)
        require(hi-lo==3,'not a three-instruction block')
        blocks.append(D.block_equal(word[section][lo:hi],middle[section][lo:hi]))
        local=Counter(); class_counts=Counter()
        # Every ADD belonging to the reordered block gets its complete corridor.
        prepared=first_geometry(word,middle,baseline_geometry[section],trace,section,i,cut)
        selected=[j for j in range(lo,hi) if middle[section][j][0]=='add']
        for j,target,d,L,H,delta in candidates(middle,section,selected,trace=trace,prepared=prepared):
            local[delta]+=1;class_counts['block_add_prices']+=1
            if not R.all_power_nonnegative(delta):witnesses.setdefault(delta,[section,i,cut,j,target,d,L,H])
        # For an ADD outside the block only its two interior cuts are new.
        # Reach from the original block edge is unchanged; explicitly check the
        # subset of the permuted block actually crossed to each interior cut.
        for target in (lo+1,lo+2):
            outside=[]
            for (sec,j),(a,b) in bounds.items():
                if sec!=section or lo<=j<hi:continue
                g=middle[section][j]
                if j<lo:
                    legal=b>=lo and all(R.crosses(g,h) for h in middle[section][lo:target])
                else:
                    legal=a<=hi and all(R.crosses(g,h) for h in middle[section][target:hi])
                if legal:outside.append(j)
            for j,t,d,L,H,delta in candidates(middle,section,outside,window=(target,target),trace=trace,trusted=True,prepared=prepared):
                local[delta]+=1;class_counts['outside_add_interior_cut_prices']+=1
                if not R.all_power_nonnegative(delta):witnesses.setdefault(delta,[section,i,cut,j,t,d,L,H])
        histogram.update(local);counts.update(class_counts);counts['first_words']+=1
        states.append({'first':[section,i,cut,list(R.basis(frame)),list(first_delta)],
          'profile':baseline,'prices':dict(class_counts),'second_cut_dimensions':sum(local.values()),
          'second_histogram_sha256':digest(sorted((list(d),n) for d,n in local.items()))})
        if progress and (number%100==0 or number+1==len(variable)):
            print('FIRST_AND_SECOND',number+1,'of',len(variable),'counts',dict(counts),flush=True)
    counts['second_cut_dimensions']=sum(histogram.values())
    return {'counts':dict(counts),'profiles':rows(histogram),'states':states,
      'dirty_block_checks':len(blocks),'dirty_block_stream_sha256':digest(blocks),
      'boundary_rejected':[],'uncertified_witnesses':list(witnesses.values())}

def compute(word,auditor=None,progress=False):
    variable,counts,_=first_moves(word,auditor)
    if progress:print('FIRST_DOMAIN',dict(counts),flush=True)
    return {'first_counts':dict(sorted(counts.items())),
      'first_digest':digest([[s,i,c,list(R.basis(f)),list(d),k] for s,i,c,f,d,k in variable]),
      'variable_frame':variable_census(word,variable,auditor,progress)}
