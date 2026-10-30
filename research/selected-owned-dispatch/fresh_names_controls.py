#!/usr/bin/env python3
"""Finite name-discipline controls, not a P104/all-size/physical proof.

No producer imports. The written proof is FRESH-NAMES.md.
"""
from dataclasses import dataclass
import json


def need(ok, message):
    if not ok:
        raise ValueError(message)


class Arena:
    def __init__(self, width):
        self.program = ('program', 0)
        self.inputs = [('INPUT', i) for i in range(width)]
        self.stack = {f: [self.program] for f in self.inputs}
        self.used_sources = set()
        self.used_owned_names = set()

    def source(self, i):
        need(i not in self.used_sources, 'source slot consumed twice')
        f = self.inputs[i]
        need(self.stack[f][-1] == self.program, 'source already borrowed')
        self.used_sources.add(i)
        return f, self.program

    def enter_class(self, specs):
        # Specs give unit tag, public bindings (field, current issuer),
        # and proposed names for that unit's owned bank labels.
        visible = [f for _, bindings, _ in specs for f, _ in bindings]
        proposed = [f for _, _, banks in specs for f in banks]
        need(len(set(visible)) == len(visible), 'duplicate child arguments')
        need(len(set(proposed)) == len(proposed), 'same bank for live units')
        need(not set(proposed) & (set(self.stack) | self.used_owned_names),
             'owned name captures existing field')
        units = []
        for tag, bindings, banks in specs:
            for f, issuer in bindings:
                need(self.stack.get(f, [None])[-1] == issuer,
                     'not the exact current issuer')
            u = Unit(self, tag, tuple(f for f, _ in bindings), tuple(banks))
            for f, _ in bindings:
                self.stack[f].append(tag)
            for f in banks:
                self.stack[f] = [tag]
                self.used_owned_names.add(f)
            units.append(u)
        return units


@dataclass
class Unit:
    arena: Arena
    tag: tuple
    public: tuple
    owned: tuple

    def __post_init__(self):
        self.live = set()

    def init(self, field):
        need(field in self.owned and field not in self.live,
             'INIT requires nonlive own bank')
        need(self.arena.stack[field][-1] == self.tag, 'INIT while child live')
        self.live.add(field)

    def clear(self, field):
        need(field in self.owned and field in self.live,
             'CLEAR requires live own bank')
        need(self.arena.stack[field][-1] == self.tag, 'CLEAR while child live')
        self.live.remove(field)

    def borrow(self, field):
        need(field in self.public or field in self.live, 'uninitialized operand')
        need(self.arena.stack[field][-1] == self.tag, 'issuer still suspended')
        return field, self.tag

    def finish(self):
        need(not self.live, 'unclosed owned lifetime')
        for f in self.public + self.owned:
            need(self.arena.stack[f][-1] == self.tag, 'return is not LIFO')
        for f in self.public + self.owned:
            self.arena.stack[f].pop()


def fixture():
    a = Arena(2)
    p, = a.enter_class([(('unit', 'parent'), [a.source(0)],
                        [('OWN', 'parent', 'z')])])
    z = p.owned[0]
    p.init(z)
    return a, p, z


def legal_nested_private_argument():
    a, p, z = fixture()
    c, = a.enter_class([(('unit', 'child'), [p.borrow(z), a.source(1)],
                        [('OWN', 'child', 'z')])])
    c.init(c.owned[0])
    c.clear(c.owned[0])
    c.finish()
    # The child finished without erasing the parent's private field.
    need(z in p.live, 'parent lost its owned field')
    p.clear(z)
    p.finish()
    need(all(not s or s == [a.program] for s in a.stack.values()),
         'stale live permission')


def duplicate_child_arguments():
    a, p, z = fixture()
    a.enter_class([(('unit', 'child'), [p.borrow(z), p.borrow(z)],
                   [('OWN', 'child', 'z')])])


def child_bank_captures_parent():
    a, p, z = fixture()
    a.enter_class([(('unit', 'child'), [p.borrow(z)], [z])])


def child_clears_borrowed_parent():
    a, p, z = fixture()
    c, = a.enter_class([(('unit', 'child'), [p.borrow(z)],
                        [('OWN', 'child', 'z')])])
    c.clear(z)


def one_bank_per_depth():
    a = Arena(2)
    bank = ('OWN_DEPTH', 0)
    a.enter_class([(('unit', 0), [a.source(0)], [bank]),
                   (('unit', 1), [a.source(1)], [bank])])


def reused_missing_source():
    a, _, _ = fixture()
    a.source(0)


def early_parent_erase():
    a, p, z = fixture()
    a.enter_class([(('unit', 'child'), [p.borrow(z)],
                   [('OWN', 'child', 'z')])])
    p.clear(z)


def main():
    legal_nested_private_argument()
    controls = {}
    for f in (duplicate_child_arguments, child_bank_captures_parent,
              child_clears_borrowed_parent, one_bank_per_depth,
              reused_missing_source, early_parent_erase):
        try:
            f()
        except ValueError as exc:
            controls[f.__name__] = str(exc)
        else:
            raise AssertionError(f'{f.__name__} was accepted')
    print(json.dumps({'status': 'PASS', 'positive': 'ancestor-owned field borrowed by child',
                      'scope': 'six finite name/lifetime controls, not physical allocation',
                      'rejected': controls}, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
