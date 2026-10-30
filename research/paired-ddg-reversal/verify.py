"""Pathwise paired-DDG reversal; JoyboyBrian with OpenAI Codex. Apache-2.0."""
from fractions import Fraction as Q
from hashlib import sha256
from itertools import product
from pathlib import Path
import importlib.util
import json

HERE = Path(__file__).resolve().parent

def need(ok, message):
    if not ok:
        raise ValueError(message)

def load_source():
    origin = json.loads((HERE/'vendor/ORIGIN.json').read_text())
    for row in origin['files']:
        need(sha256((HERE/'vendor'/row['retained']).read_bytes()).hexdigest() == row['sha256'], 'retained source bytes')
    spec = importlib.util.spec_from_file_location('paired_source', HERE/'vendor/paired_sampler.py')
    source = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(source)
    return source

def inverse(states, ids, digits, phase, target, bit):
    need(type(bit) is int and bit in (0,1) and 0 <= phase < 156, 'inverse domain')
    row = digits[phase]
    if target >= 312:
        out = target-312
        need(0 <= out < 4 and row[out] == 1, 'leaf exists at phase')
        slot = sum(row[:out])
    else:
        need(0 <= target < 312, 'internal target')
        next_phase, node = states[target]
        need(next_phase == (phase+1)%156, 'successor phase')
        slot = node + sum(row)
    need(slot % 2 == bit, 'edge coin parity')
    old = ids.get((phase, slot//2))
    need(old is not None, 'predecessor exists')
    return old

def sample(table, bits, start):
    state, phase, count, cursor = 0, 0, 0, start
    while cursor < len(bits):
        bit = bits[cursor]
        need(type(bit) is int and bit in (0,1), 'fair tape alphabet')
        state = table[state][bit]
        phase, count, cursor = (phase+1)%156, count+1, cursor+1
        if state >= 312:
            return state, phase, count, cursor
    raise ValueError('finite tape has no terminating prefix')

def cleanup(table, states, ids, digits, bits, start, terminal, accumulator):
    state, phase, count, cursor = terminal
    need(state >= 312 and count > 0 and cursor == start+count and cursor <= len(bits), 'terminal cursor/count')
    need(phase == count%156 and 0 <= accumulator < 4, 'terminal phase/output domain')
    retained = accumulator ^ (state-312)
    moves = wraps = 0
    while count:
        previous_phase = (phase-1)%156
        bit = bits[cursor-1]
        previous = inverse(states,ids,digits,previous_phase,state,bit)
        need(table[previous][bit] == state, 'erase scratch via forward edge')
        state, phase = previous, previous_phase
        cursor, count = cursor-1, count-1
        moves += 1
        wraps += state == 0 and count > 0
    need((state,phase,count,cursor) == (0,0,0,start), 'clean initial controller')
    return retained, moves, wraps

def reject(fn):
    try:
        fn()
    except ValueError:
        return
    raise ValueError('mutation was accepted')

def main():
    source = load_source()
    weights, counts, table, mean = source.make(1,1)
    states = [(p,j) for p,n in enumerate(counts) for j in range(n)]
    ids = {state:i for i,state in enumerate(states)}
    digits = [tuple(2*(w*pow(2,p,169)%169)//169 for w in weights) for p in range(156)]
    edges = leaves = 0
    for old,(phase,node) in enumerate(states):
        for bit,target in enumerate(table[old]):
            need(inverse(states,ids,digits,phase,target,bit) == old, 'every source edge has algebraic inverse')
            reject(lambda p=phase,t=target,b=bit: inverse(states,ids,digits,p,t,1-b))
            edges += 1
            leaves += target >= 312
    checked, outcomes = 0, set()
    tape_prefix = (1,0,1)
    for tail in product((0,1), repeat=10):
        out,used = source.run(table,tail)
        if out is None:
            continue
        bits = tape_prefix+tail+(0,1)
        terminal = sample(table,bits,3)
        need(terminal[0]-312 == out and terminal[2] == used, 'literal source agrees')
        for accumulator in range(4):
            retained,moves,wraps = cleanup(table,states,ids,digits,bits,3,terminal,accumulator)
            need(retained == accumulator^out and moves == used, 'retained XOR accumulator and reverse count')
        outcomes.add(out)
        checked += 1
    need(outcomes == set(range(4)), 'every leaf label reached')
    # Keep only at most three unresolved paths per depth; no exponential census.
    active = {0:()}
    witnesses = []
    for depth in range(1,315):
        nxt = {}
        for state,path in active.items():
            for bit,target in enumerate(table[state]):
                trail = path+(bit,)
                if target < 312:
                    need(target not in nxt, 'unresolved paths unique at depth')
                    nxt[target] = trail
                elif depth >= 156:
                    witnesses.append(trail)
        active = nxt
        need(1 <= len(active) <= 3, 'source survival width')
    need(any(len(path)>312 for path in witnesses), 'two phase wraps reached')
    unfinished = next(iter(active.values()))
    reject(lambda: sample(table,unfinished,0))
    wrap_returns = 0
    for path in witnesses:
        bits = tape_prefix+path
        terminal = sample(table,bits,3)
        retained,moves,wraps = cleanup(table,states,ids,digits,bits,3,terminal,2)
        need(moves == len(path) and retained == 2^(terminal[0]-312), 'wrap lifecycle')
        wrap_returns += wraps
    need(wrap_returns > 0, 'root may recur before counter is zero')
    bits = tape_prefix+(0,)*12
    terminal = sample(table,bits,3)
    state,phase,count,cursor = terminal
    for bad in [(state,phase,count+1,cursor),(state,phase,count,cursor-1),
                (state,(phase+1)%156,count,cursor),(312+((state-311)%4),phase,count,cursor)]:
        reject(lambda x=bad: cleanup(table,states,ids,digits,bits,3,x,0))
    # Dropping terminal phase makes source leaf transitions collide even with a coin.
    collisions = {}
    for old,row in enumerate(table):
        for bit,target in enumerate(row):
            if target >= 312:
                collisions.setdefault((target,bit),[]).append(old)
    key,parents = next((k,v) for k,v in collisions.items() if len(v)>1)
    need(states[parents[0]][0] != states[parents[1]][0], 'phase-free collision')
    need(mean == Q(9960277917013927549978,4649714690825496825793), 'exact selected mean')
    print(json.dumps({'status':'PASS_PAIRED_DDG_REVERSAL','pair':[1,1],'edges':edges,'leaf_edges':leaves,
      'literal_terminating_tapes':checked,'wrap_terminating_paths':len(witnesses),'max_tested_T':max(map(len,witnesses)),'nonterminal_root_returns':wrap_returns,
      'mean_draws':str(mean),'mean_forward_reverse_transitions':str(2*mean),
      'phase_free_collision':{'leaf':key[0]-312,'bit':key[1],'parents':parents[:2]},
      'controls':['624 wrong-bit edges','count','cursor','phase','output label','phase-free collision'],
      'scope':'pathwise logical cleanup for fixed(1,1), unbounded T; physical tariff conditional; no new kappa'},sort_keys=True))

if __name__ == '__main__':
    main()
