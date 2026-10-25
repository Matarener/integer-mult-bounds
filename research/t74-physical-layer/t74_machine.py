# SPDX-License-Identifier: Apache-2.0
"""Extend the frozen physical controller with checked private-Z release.

I retain PR3385's one-active-node protocol and inherited physical primitives.
The run loop adds one opcode; the other transitions keep their source bodies.
"""
from predecessor import activate
activate()
import machine as base
from scalar_words import require_zero


class T74Machine(base.Machine):
    def release_zero_step(self, target):
        base.need(self.binding.slots + self.binding.centres <= target <
                  self.binding.slots + self.binding.private, "release only declared private Z")
        extent = self.packet_extent()
        try:
            require_zero(self.packet(target), extent)
            self.packet(target).clear()
        finally:
            extent.close()

    def run(self, payload, descriptors):
        base.need(self.closed and self.output.read() == base.BLANK and set(descriptors) == set(base.INPUTS),
                  "closed prepared complex entry and complete descriptors")
        self.parking.empty()
        source = base.borrowed_tape(payload)
        base.need(source not in self.parked and source is not self.output, "borrowed complex input is separate")
        base.need(all(isinstance(descriptors[name], base.Count) for name in base.INPUTS), "encoded prepared descriptor")
        self.root, self.closed, self.mode = True, False, "node"
        self.group = None
        try:
            base.copy_symbols(source, self.roles["current"])
            for name in base.INPUTS:
                base.copy_symbols(descriptors[name].tape, self.roles[name])
            while True:
                child = False
                with base.sealed_constructors(), self.scope.installed():
                    if self.mode == "node":
                        self.node()
                    elif self.mode == "group":
                        if self.group is None:
                            self.next_group()
                        elif self.pc == len(self.group.code):
                            self.finish_group()
                        else:
                            op = self.group.code[self.pc]
                            kind = op[0]
                            if kind == "scalar":
                                self.scalar_step(*op[2:])
                            elif kind == "zero":
                                self.zero_step(op[2])
                            elif kind == "release_zero":
                                self.release_zero_step(op[2])
                            elif kind == "copy":
                                self.copy_step(*op[2:])
                            elif kind == "monomial":
                                self.monomial_step(*op[2:])
                            elif kind == "exchange":
                                self.exchange_step(*op[2:])
                            elif kind == "child":
                                self.prepare_child(*op[2:])
                                child = True
                            else:
                                base.need(kind in ("identity", "marker"), "implemented physical instruction")
                            if not child:
                                self.pc += 1
                    else:
                        base.need(self.mode == "return", "finite complex controller state")
                self.pool.empty()
                if child:
                    self.enter_child()
                elif self.mode == "return" and self.return_node():
                    source.rewind()
                    return self.output
        except BaseException:
            for tape in (*self.roles.values(), *self.capsule.values()):
                tape.rewind()
            self.discard()
            source.rewind()
            raise
