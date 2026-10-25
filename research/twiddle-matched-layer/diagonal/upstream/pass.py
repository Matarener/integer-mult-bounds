"""Encoded fixed-round twiddle diagonal pass on one complete physical cube.

SPDX-License-Identifier: Apache-2.0
Sagar Thakrar, with substantial OpenAI Codex assistance.
Nick Petalas supplied the unchanged PR3593 producer; the unchanged PR3611
consumer retains its source notices. No inherited execution body is edited.
"""
from collections import Counter


def require(ok, why):
    if not ok:
        raise ValueError(why)


class DiagonalPass:
    """Valid-admission, one-shot pass; successful return is the proved contract.

    Constructor dimensions provision blank storage and admitted input only.
    Runtime extents come from descriptors, framed packets and the unary guide.
    Malformed-input recovery and exceptional interruption are not promised.
    """
    def __init__(self, producer_module, consumer_module, descriptor, width, source):
        # Admission/allocation only. No host dimensions are retained by Pass.
        ell, _, _, axes, _ = producer_module.admit(descriptor, tuple(
            0 for axis in descriptor.split('#')[3]
            for _ in range(len(descriptor.split('#')[0]) - (axis == 'S'))))
        A = sum(ell if axis else ell-1 for axis in axes)
        L = 2 * (1 << ell) * width
        self.producer = producer_module.Controller(descriptor, (0,)*A)
        self.consumer = consumer_module.Consumer(ell, width)
        T = consumer_module.Tape
        self.tapes = dict(fullinput=T(source), fulloutput=T((0,)*(2+(1 << A)*(L+2))),
                          unaryA=T((0,)*(A+2)), unaryell=T((0,)*(ell+2)),
                          width=T('^'+'1'*width+'$'), packet=T((0,)*(L+2)),
                          descriptor=self.producer.descriptor,
                          address=self.producer.data['address'], header=self.producer.data['output'])
        self.gates = Counter()
        self.actions = Counter()
        self.used = False

    def test(self, value):
        self.gates['test'] += 1
        return value

    def read(self, role):
        self.actions[role+'.read'] += 1
        return self.tapes[role].read()

    def write(self, role, value):
        self.actions[role+'.write'] += 1
        self.tapes[role].write(value)

    def move(self, role, direction):
        self.actions[role+'.move'] += 1
        self.tapes[role].move(direction)

    def home(self, role, marker='^'):
        while self.test(self.read(role) != marker):
            self.move(role, -1)

    def clear_frame(self, role):
        self.home(role)
        self.move(role, 1)
        while self.test(self.read(role) != '$'):
            self.write(role, 0)
            self.move(role, 1)
        self.write(role, 0)
        self.move(role, -1)
        while self.test(self.read(role) != '^'):
            self.write(role, 0)
            self.move(role, -1)
        self.write(role, 0)

    def address_home(self):
        # Guide and raw address point to corresponding bits, except '^' at0.
        while self.test(self.read('unaryA') == '1'):
            self.move('unaryA', -1)
            if self.test(self.read('unaryA') != '^'):
                self.move('address', -1)

    def initialize(self):
        require(self.test(self.read('descriptor') == '^'), 'descriptor start')
        self.write('unaryell', '^')
        self.move('unaryell', 1)
        self.move('descriptor', 1)
        while self.test(self.read('descriptor') == '1'):
            self.write('unaryell', '1')
            self.move('unaryell', 1)
            self.move('descriptor', 1)
        require(self.test(self.read('descriptor') == '#'), 'ell delimiter')
        self.write('unaryell', '$')
        self.home('unaryell')
        # Skip the two remaining unary fields; fixed finite control sequence.
        for _field in ('K', 'h'):
            self.move('descriptor', 1)
            while self.test(self.read('descriptor') != '#'):
                self.move('descriptor', 1)
        self.move('descriptor', 1)
        self.write('unaryA', '^')
        self.move('unaryA', 1)
        first = True
        while self.test(self.read('descriptor') != '#'):
            flag = self.read('descriptor')
            require(self.test(flag in ('L', 'S')), 'axis flag')
            self.move('unaryell', 1)
            if self.test(flag == 'S'):
                self.move('unaryell', 1)
            while self.test(self.read('unaryell') == '1'):
                self.write('unaryA', '1')
                self.move('unaryA', 1)
                if self.test(not first):
                    self.move('address', 1)
                self.write('address', 0)
                first = False
                self.move('unaryell', 1)
            self.home('unaryell')
            self.move('descriptor', 1)
        self.write('unaryA', '$')
        self.move('unaryA', -1)
        self.address_home()
        self.home('descriptor')
        require(self.test(self.read('fullinput') == '@'), 'full input start')
        self.move('fullinput', 1)
        self.write('fulloutput', '@')
        self.move('fulloutput', 1)

    def rearm_producer(self):
        for name in self.producer.NAMES:
            tape = self.producer.c[name].tape
            self.tapes['counter'] = tape
            self.write('counter', 2)
            self.move('counter', 1)
            while True:
                token = self.read('descriptor')
                self.write('counter', 0)
                self.move('counter', 1)
                if self.test(token == '$'):
                    break
                self.move('descriptor', 1)
            self.write('counter', 3)
            while self.test(self.read('counter') != 2):
                self.move('counter', -1)
            self.home('descriptor')
        self.gates['reset-first'] += 1
        self.producer.first = True

    def clear_header(self):
        self.write('header', 0)
        self.move('unaryell', 1)
        while self.test(self.read('unaryell') == '1'):
            self.move('header', 1)
            self.write('header', 0)
            self.move('unaryell', 1)
        self.move('unaryell', -1)
        while self.test(self.read('unaryell') == '1'):
            self.move('header', -1)
            self.move('unaryell', -1)

    def load_packet(self):
        require(self.test(self.read('fullinput') == '^'), 'next complete packet')
        self.write('packet', '^')
        self.move('packet', 1)
        self.move('fullinput', 1)
        while self.test(self.read('fullinput') != '$'):
            value = self.read('fullinput')
            require(self.test(value in (0, 1)), 'packet bit')
            self.write('packet', value)
            self.move('packet', 1)
            self.move('fullinput', 1)
        self.write('packet', '$')
        self.move('fullinput', 1)
        self.home('packet')

    def append_packet(self, output):
        self.tapes['returned'] = output
        require(self.test(self.read('returned') == '^'), 'returned packet origin')
        self.write('fulloutput', '^')
        self.move('fulloutput', 1)
        self.move('returned', 1)
        while self.test(self.read('returned') != '$'):
            self.write('fulloutput', self.read('returned'))
            self.move('fulloutput', 1)
            self.move('returned', 1)
        self.write('fulloutput', '$')
        self.move('fulloutput', 1)
        self.home('returned')

    def increment(self):
        # Reach the raw final address bit using the unary guide only.
        self.move('unaryA', 1)
        first = True
        while self.test(self.read('unaryA') == '1'):
            if self.test(not first):
                self.move('address', 1)
            first = False
            self.move('unaryA', 1)
        self.move('unaryA', -1)
        carry = True
        while self.test(self.read('unaryA') == '1'):
            old = self.read('address')
            self.gates['flip'] += 1
            self.write('address', 1-old)
            if self.test(old == 0):
                carry = False
                break
            self.move('unaryA', -1)
            if self.test(self.read('unaryA') != '^'):
                self.move('address', -1)
        self.address_home()
        return carry

    def run(self):
        require(not self.used, 'one-shot full pass')
        self.used = True
        self.initialize()
        first = True
        while True:
            if self.test(not first):
                self.rearm_producer()
            first = False
            self.load_packet()
            self.producer.execute()
            result = self.consumer.run(self.tapes['header'], self.tapes['descriptor'],
                                       self.tapes['width'], self.tapes['packet'])
            self.append_packet(result)
            self.consumer.clear('output')
            self.gates['consumer-rearm'] += 1
            self.consumer.used = False
            self.clear_frame('packet')
            self.clear_header()
            if self.test(self.increment()):
                break
        require(self.test(self.read('fullinput') == '!'), 'full cube packet extent')
        self.write('fulloutput', '!')
        self.home('fullinput', '@')
        self.home('fulloutput', '@')
        self.clear_frame('unaryA')
        self.clear_frame('unaryell')
        return self.tapes['fulloutput']
