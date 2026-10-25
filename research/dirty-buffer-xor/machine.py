"""Dirty-buffer XOR permutations, compiled to literal two-tape tables.
Dugongue, with substantial OpenAI Codex assistance. Apache-2.0.
Only the compiler uses address arithmetic; the preserved predecessor runner
executes finite control, scanned symbols, writes and unit head moves.
"""
from dataclasses import dataclass
from inputs.pr3879_machine import (Machine, ALPHABET, ZERO, ONE, SEP, BLANK,
                                  encode, decode, run, need, integer)


def parameters(h, delta, r):
    integer(h, 0, 'dimension'); integer(delta, 0, 'mask'); integer(r, 0, 'scratch exponent')
    need(delta < 1 << h, 'mask range')
    need(r <= h, 'scratch exponent range')


def invoice(h, delta, r):
    parameters(h, delta, r)
    n = 1 << h
    factor = sum(5 + (1 << max(k-r, 0)) for k in range(h) if (delta >> k) & 1)
    single = sum(n*(2 + (1 << max(k-r, 0))) for k in range(h) if (delta >> k) & 1)
    paired = 3*n*delta.bit_count()
    used = min(1 << r, 1 << (delta.bit_length()-1)) if delta else 0
    return {'time_factor': n*factor, 'single_macros': single,
            'paired_macros': paired, 'macros': single+paired,
            'states': 2*(single+paired)+1,
            'transitions': 16*single+6*paired, 'used_records': used}


def compile_machine(h, delta, r):
    """Trade a restored dirty prefix of at most 2**r records for tape travel."""
    parameters(h, delta, r)
    n = 1 << h
    operations = []
    for k in range(h):
        if not ((delta >> k) & 1):
            continue
        half, chunk = 1 << k, 1 << min(k, r)
        position = 0

        def move(target):
            nonlocal position
            difference = target-position
            operations.extend(['R0' if difference > 0 else 'L0']*abs(difference))
            position = target

        def swap_chunk():
            # Exchange chunk records in one forward pass, then rewind both heads.
            operations.extend(['S']*chunk)
            operations.extend(['L']*chunk)

        for base in range(0, n, 2*half):
            for offset in range(0, half, chunk):
                a = base+offset
                move(a)
                swap_chunk()
                move(a+half)
                swap_chunk()
                move(a)
                swap_chunk()
        move(n)  # Explicit paid end sweep makes the closed invoice uniform.
        move(0)
    table = {}
    for index, op in enumerate(operations):
        entry, scan, next_state = 2*index, 2*index+1, 2*index+2
        for a in ALPHABET:
            for b in ALPHABET:
                if op in ('S', 'L'):
                    direction = 1 if op == 'S' else -1
                    if a == b == SEP:
                        table[(entry,a,b)] = (scan,None,None,direction,direction)
                        table[(scan,a,b)] = (next_state,None,None,0,0)
                    elif a in (ZERO,ONE) and b in (ZERO,ONE):
                        table[(scan,a,b)] = ((scan,b,a,1,1) if op == 'S'
                                             else (scan,None,None,-1,-1))
                else:
                    direction = 1 if op == 'R0' else -1
                    if a == SEP:
                        table[(entry,a,b)] = (scan,None,None,direction,0)
                        table[(scan,a,b)] = (next_state,None,None,0,0)
                    elif a in (ZERO,ONE):
                        table[(scan,a,b)] = (scan,None,None,direction,0)
    machine = Machine(h, delta, tuple(operations), table, 2*len(operations), 'inplace')
    bill = invoice(h, delta, r)
    need(len(operations) == bill['macros'], 'closed macro invoice')
    need(len(table) == bill['transitions'], 'literal transition inventory')
    return machine


def tape_cost(h, delta, r, width):
    integer(width, 0, 'record width')
    return invoice(h, delta, r)['time_factor']*(width+2)
