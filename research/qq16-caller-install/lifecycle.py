# SPDX-License-Identifier: Apache-2.0
"""Dedicated finite caller storage and paid immutable-port return.

Chris R / Clear1nsight, OpenAI Codex assistance. The Tape, Count, Counter,
copy/transfer and primitive-boundary bodies are inherited, injected sources.
No numerical address or packet length is decoded into Python control.
"""

def need(ok, reason):
    if not ok:
        raise ValueError(reason)


class CallerStorage:
    """One exclusive 224-output / 16-private inventory outside active Machine.

Only the fixed role alphabet and finite stage enter control. A suspended
caller's primitive pools are never used as recovery storage. This class
implements storage ownership, not the arithmetic meaning of outputs.
"""
    def __init__(self, Tape, Count, Counter, blank, transfer, require_zero,
                 external_roles=(), outputs=224, private=16, expected_event=4, engines=()):
        need(type(outputs) is int and outputs > 0 and type(private) is int and private > 0,
             'fixed positive caller role alphabet')
        self.outputs = tuple(Tape() for _ in range(outputs))
        self.private = tuple(Tape() for _ in range(private))
        self.Count, self.Counter = Count, Counter
        self.blank, self.transfer, self.require_zero = blank, transfer, require_zero
        self.external_roles = tuple(external_roles)
        need(type(expected_event) is int and expected_event >= 0, 'fixed producer fence event')
        self.expected_event = expected_event
        self.engines = tuple(engines)
        self.stage = 'closed'
        self.parent = self.cut = self.targets = self.acquisition = None
        self._distinct()

    @property
    def roles(self):
        return (*self.outputs, *self.private)

    def _distinct(self):
        acquired = () if getattr(self, 'acquisition', None) is None else (
            *self.acquisition.packets, self.acquisition.output, *self.acquisition.pool.tapes)
        all_roles = (*self.roles, *acquired, *self.external_roles)
        need(len({id(t) for t in all_roles}) == len(all_roles),
             'exclusive physical caller/native/wrapper inventory')

    def _parent_cut(self):
        p = self.parent
        need(p is not None and not p.closed and p.mode == 'group' and p.group is None
             and p.bank.state == 'closed' and p.event == self.expected_event
             and p.subgroup == 0 and p.pc == 0
             and p.cover_index == p.binding.cover.size,
             'completed whole-cover parent fence')
        need((p.event, p.subgroup, p.cover_index, p.pc, id(p.roles['current'])) == self.cut,
             'same immutable parent continuation and bank binding')
        p.primitive_boundary()
        self._distinct()
        service_roles = (*self.roles, *self.acquisition.packets, self.acquisition.output,
                         *self.acquisition.pool.tapes)
        need(not any(t is x for t in service_roles for x in
                     (*p.parked, *p.capsule.values(), p.output, p.bank.output,
                      p.parking.stack, p.parking.reverse)),
             'dedicated recovery roles disjoint from all live parent roles')
        need(self.acquisition.state == 'gathered'
             and self.acquisition.source is p.roles['current']
             and self.acquisition.selection == {(family, 0): i
                                               for i, family in enumerate(self.targets)},
             'actual whole-family acquired source and owner binding')
        need(not any(t is x for t in self.roles for x in
                     (*self.acquisition.packets, self.acquisition.output,
                      *self.acquisition.pool.tapes)), 'outputs separate from borrowed acquired fields')

    def begin(self, parent, acquisition, targets):
        need(self.stage == 'closed', 'previous output generation retired')
        need(type(targets) is tuple and len(targets) == len(self.outputs)
             and len(set(targets)) == len(targets)
             and all(type(i) is int and 0 <= i < parent.binding.families for i in targets),
             'distinct finite persistent destination families')
        need(acquisition.families == parent.binding.families and acquisition.covers == 1
             and acquisition.slots == len(targets), 'whole-cover family acquisition layout')
        self.parent, self.acquisition, self.targets = parent, acquisition, targets
        self.cut = (parent.event, parent.subgroup, parent.cover_index, parent.pc,
                    id(parent.roles['current']))
        self._parent_cut()
        # The service owns these tapes exclusively. Arbitrary old contents are
        # disposable, but erasure is an actual paid tape operation.
        for tape in self.roles:
            tape.clear()
        self.stage = 'decode'

    def output(self, index):
        need(self.stage in ('decode', 'reconnect') and type(index) is int
             and 0 <= index < len(self.outputs), 'live output role')
        return self.outputs[index]

    def temporary(self, index):
        need(self.stage in ('decode', 'reconnect') and type(index) is int
             and 0 <= index < len(self.private), 'live private role')
        return self.private[index]

    def _close_private(self, extent):
        for tape in self.private:
            tape.rewind()
            if tape.read() != self.blank:
                self.require_zero(tape, extent)
            tape.clear()

    def decoded(self, extent):
        need(self.stage == 'decode', 'completed decoder before reconnection')
        self._parent_cut()
        self._close_private(extent)
        self.stage = 'reconnect'

    def ready(self, extent, engines_closed):
        need(self.stage == 'reconnect', 'completed reconnection before publication')
        need(engines_closed, 'native and wrapper completed outputs consumed')
        for engine in self.engines:
            need(engine is not self.parent and engine.closed
                 and engine.output.read() == self.blank, 'separate closed engine and consumed output')
            engine.pool.empty()
            if hasattr(engine, 'compact'):
                need(engine.compact.closed and engine.compact.binary.native.closed,
                     'closed wrapper Compact and ordinary engine')
            if hasattr(engine, 'primitive_boundary'):
                engine.primitive_boundary()
                engine.parking.empty()
        self._parent_cut()
        self._close_private(extent)
        # Preflight every output before the first destructive parent write.
        # The Count remains encoded and borrowed; countdown owns its copy.
        for tape in self.outputs:
            tape.rewind()
            counter = self.Counter(extent)
            try:
                while not counter.finished:
                    need(tape.read() in (0, 1), 'complete returned binary output')
                    tape.step(1)
                    counter.decrement()
                need(tape.read() == self.blank, 'exact returned output extent')
            finally:
                tape.rewind()
                counter.close()
        self.stage = 'ready'

    def commit(self, prefixes, unused_rows, full_cover_row_bits, adopt=False):
        need(self.stage == 'ready', 'all decoder and continuation reads completed')
        self._parent_cut()
        # D and reconnection have completed every borrowed acquired-field read.
        # Each source transfer clears that old field, consumes its owned result,
        # and returns heads. The immutable parent current bank is still untouched.
        for tape, target in zip(self.outputs, self.acquisition.packets):
            self.transfer(tape, target)
        # Source BankPackets copies every unselected family unchanged, replaces
        # all selected fields, then performs its paid fixed-current-bank commit.
        self.acquisition.scatter(self.parent.roles['current'], prefixes,
                                 unused_rows, full_cover_row_bits)
        if adopt:
            adopt_bank(self.parent, self.acquisition, self.blank, self.external_roles)
        else:
            self.acquisition.commit(self.parent.roles['current'])
        self.stage = 'closed'
        self.parent = self.cut = self.targets = self.acquisition = None
        need(all(t.read() == self.blank for t in self.roles), 'all caller work retired')


def current_bindings(parent):
    """Finite source role tables must agree; no body/head observations."""
    expected = (*parent.roles.values(), *parent.bank.packets, *parent.private)
    need(tuple(parent.parked) == expected and tuple(parent.parking.roles) == expected,
         'complete current-role/parked/parking binding correspondence')
    need(len({id(t) for t in expected}) == len(expected), 'distinct parent role table')
    return expected


def adopt_bank(parent, acquisition, blank, external_roles=()):
    """Opt-in finite role exchange at a completed, closed-bank caller fence.

    Public parent.output and the borrowed run input retain their physical
    identities. No current/output aliases may escape this compiled boundary.
    Replaces only the final BankPackets.commit interval, after scatter.
    """
    from words import LEFT
    from session import erase_marker
    old = parent.roles['current']
    new = acquisition.output
    previous = current_bindings(parent)
    need(not parent.closed and parent.group is None and parent.mode == 'group'
         and parent.bank.state == 'closed' and parent.bank.source is None,
         'closed parent bank before internal role adoption')
    need(acquisition.state == 'returned' and acquisition.source is old
         and not acquisition.pool.live, 'completed owned replacement bank')
    need(old is not new and new not in previous
         and new not in (*parent.capsule.values(), parent.output,
                         parent.bank.output, parent.parking.stack, parent.parking.reverse),
         'replacement disjoint from all parent roles')
    need(old not in external_roles and new not in external_roles,
         'no cached external binding to exchanged current/output roles')
    need(new.read() in (0, 1), 'complete nonempty replacement bank')
    # These are actual head-relative origin checks, not numeric head resets.
    for tape in (old, new):
        tape.step(-1)
        try: need(tape.read() == LEFT, 'canonical exchange origin')
        finally: tape.step(1)
    new.rewind()
    try:
        while True:
            symbol = new.read()
            if symbol == blank: break
            need(symbol in (0, 1), 'opaque binary replacement alphabet')
            new.step(1)
    finally:
        new.rewind()
    # A single finite-control transposition updates every source role table.
    # Ancestor frames contain encoded bodies in logical-role order, not aliases.
    replacement = tuple(new if tape is old else tape for tape in previous)
    parent.roles['current'] = new
    parent.parked = replacement
    parent.parking.roles = replacement
    acquisition.output = old
    acquisition.source = None  # All reads of this borrowed source have ended.
    current_bindings(parent)
    old.clear()                # Discarding the old current bank is still paid.
    erase_marker(old)
    acquisition.release()


def parent_source_audit(sources, original_sources):
    """Byte-level compatibility with Sagar Thakrar's #3464 source boundary."""
    import hashlib
    names = ('machine.py', 'parking.py', 'bank_packets.py', 'selected_binding.py')
    need(all(sources[n] == original_sources[n] for n in names),
         'exact #3464 principal source compatibility')
    return {n: hashlib.sha256(sources[n]).hexdigest() for n in names}


def fixture(families=224, adopt=False):
    """Actual Tape/BankPackets/Machine execution of the whole-cover fence.

    The service's payload transformation is an identity storage witness, not
    QQ16 arithmetic. The integrated continuation checker must separately bind
    D/G and the current-value endpoint. All 224 destination families and 16
    private roles are exercised; geometry and native backend remain reduced.
    """
    width = 2
    from types import SimpleNamespace
    from cardinal_counts import Count
    from fixture_binding import FixtureBinding
    from selected_binding import Group
    from machine import Machine, copy_symbols, transfer
    from bank_packets import BankPackets
    from macro_code import Code
    from ordinary import Ordinary
    from records import Tape
    from stream import Counter
    from scratch_pool import ScratchPool
    from session import OuterScope, sealed_constructors
    from scalar_words import require_zero
    from words import BLANK
    from hashlib import sha256

    need(families >= 4, 'bounded lifecycle fixture domain')
    family_count = families
    class Binding(FixtureBinding):
        families, slots, private = family_count, 4, 1
        events = ('complete_tensor', 'both_bridge_legs')
        def group_count(self, event):
            need(event in (0, 1), 'fixture event')
            return 1
        def group(self, event, subgroup, cover):
            if event == 0:
                old = super().group(0, subgroup, cover)
                code = []
                for operation in old.code:
                    op = list(operation)
                    positions = (2, 3) if op[0] in ('scalar', 'copy', 'exchange') else (2,)
                    for i in positions:
                        if op[i] == 2: op[i] = 4
                    code.append(tuple(op))
                return Group(old.keys, tuple(code), old.recipes)
            need(event == 1 and subgroup == 0, 'fixture bridge event')
            return Group(tuple((i, cover) for i in range(4)),
                         (('scalar', -1, 0, 1, ('add', 1, 1)),
                          ('scalar', -1, 2, 3, ('add', -1, 1))), {})

    def body(t): return bytes(t.cells[1:]).rstrip(bytes([BLANK]))
    def native():
        return Ordinary(2, SimpleNamespace(codes=SimpleNamespace(q=2)),
                        SimpleNamespace(families=0), (Code((('unreachable',),), 0),), capacity=64)
    transfer_controls = []
    for old_length, new_length in ((0, 0), (1, 1), (5, 5), (17, 17), (3, 11)):
        source_tape, target_tape = Tape(), Tape()
        for i in range(new_length): source_tape.append(i & 1)
        for i in range(old_length): target_tape.append((i + 1) & 1)
        source_tape.rewind(); target_tape.rewind()
        before_pair = [t.meter.record() for t in (source_tape, target_tape)]
        transfer(source_tape, target_tape)
        paid = {k: sum(t.meter.record()[k]-old[k] for t, old in
                       zip((source_tape, target_tape), before_pair))
                for k in ('reads', 'writes', 'moves')}
        expected_cost = dict(reads=2*old_length+5*new_length+7,
                             writes=old_length+2*new_length,
                             moves=2*old_length+4*new_length+10)
        need(paid == expected_cost, 'literal immutable-transfer tariff')
        transfer_controls.append(dict(old_bits=old_length, new_bits=new_length, actions=paid))
        source_tape.clear(); target_tape.clear()
    binding = Binding()
    acquisition = BankPackets(binding.families, 1, families)
    service = CallerStorage(Tape, Count, Counter, BLANK, transfer, require_zero, outputs=families, expected_event=0)
    pool = ScratchPool(64)
    scope = OuterScope(pool)
    observations, rejections, meters = [], [], []
    def reject(name, operation):
        try: operation()
        except ValueError: rejections.append(name)
        else: raise ValueError('accepted lifecycle mutation: ' + name)

    class Installed(Machine):
        def finish_group(self):
            super().finish_group()
            if self.event != 0 or self.cover_index != binding.cover.size:
                return
            # The original outer allocation scope is suspended; the external
            # service has its own fixed64 descriptor pool. Native engines, if
            # called by the integrated service, must suspend this scope too.
            with self.scope.suspended():
                with sealed_constructors(), scope.installed():
                    rowbits = Count(self.c('row_bits'))
                    rowbits.multiply_small(binding.cover.size)
                    extent = Count.product(self.c('prefixes'), self.c('unused'))
                    extent2 = Count.product(extent, rowbits)
                    extent.close()
                    try:
                        protected = tuple(t for t in (*self.parked, *self.capsule.values(),
                            self.output, self.bank.output, self.parking.stack, self.parking.reverse)
                            if t is not self.roles['current'])
                        image = [(body(t), t.head) for t in protected]
                        bank_image = body(self.roles['current'])
                        all_tapes = tuple(dict.fromkeys((*service.roles, *acquisition.packets,
                            acquisition.output, *acquisition.pool.tapes, *pool.tapes,
                            self.roles['current'], rowbits.tape, extent2.tape)))
                        before = [t.meter.record() for t in all_tapes]
                        acquisition.select(tuple((i, 0) for i in range(families)))
                        with scope.suspended():
                            acquisition.gather(self.roles['current'], self.c('prefixes'),
                                               self.c('unused'), rowbits)
                        # Own dirty state is discardable; borrowed source is not.
                        for i, tape in enumerate(service.roles):
                            tape.append(i & 1); tape.rewind()
                        service.begin(self, acquisition, tuple(range(families)))
                        reject('premature fixed-bank commit', lambda: service.commit(
                            self.c('prefixes'), self.c('unused'), rowbits))
                        saved = service.outputs
                        service.outputs = (self.roles['current'], *saved[1:])
                        reject('parent/output alias', service._parent_cut)
                        service.outputs = saved
                        for i in range(families):
                            copy_symbols(acquisition.packets[i], service.output(i))
                        # Nonzero private state must be restored by the decoder.
                        service.private[0].append(1); service.private[0].rewind()
                        reject('unrestored private dirt', lambda: service.decoded(extent2))
                        service.private[0].clear()
                        service.decoded(extent2)
                        reject('unclosed native output', lambda: service.ready(extent2, False))
                        # Exact extent rejects before any source-bank mutation.
                        service.outputs[-1].clear()
                        reject('short final output', lambda: service.ready(extent2, True))
                        need(body(self.roles['current']) == bank_image,
                             'all output preflight precedes destructive parent writes')
                        copy_symbols(acquisition.packets[-1], service.outputs[-1])
                        service.ready(extent2, True)
                        with scope.suspended():
                            service.commit(self.c('prefixes'), self.c('unused'), rowbits, adopt=adopt)
                        need(body(self.roles['current']) == bank_image,
                             'whole-bank identity storage publication')
                        need([(body(t), t.head) for t in protected] == image,
                             'all parent roles and suspended ancestor stack preserved')
                        reject('retired output access', lambda: service.output(0))
                        reject('double commit', lambda: service.commit(
                            self.c('prefixes'), self.c('unused'), rowbits))
                        meters.append({k: sum(t.meter.record()[k]-old[k] for t, old in
                                      zip(all_tapes, before)) for k in ('reads', 'writes', 'moves')})
                        observations.append(dict(ancestor=not self.root, event=self.event))
                    finally:
                        rowbits.close(); extent2.close()
                pool.empty()

    rows = 2*families
    compact = width//2-1
    desc_values = dict(prefixes=2, rows=rows, front=0, compact_bits=compact, before=0,
        width=width, after=0, back=0, spacing=1, guard=1, residue=0,
        component_bits=12, coefficients=1, root_width=width)
    descriptors = {n: Count.literal(v) for n, v in desc_values.items()}
    values = [(16*((7*i)%11-5), 16*((3*i)%7-3)) for i in range(2*rows*(1<<(width+3*compact)))]
    raw = bytes((x >> bit) & 1 for pair in values for x in pair for bit in range(12))
    source = Tape()
    for bit in raw: source.append(bit)
    source.rewind()
    source_image = body(source)
    desc_images = {n: body(v.tape) for n, v in descriptors.items()}
    baseline = Machine(binding, native(), binding.catalogue)
    expected = baseline.run(source, descriptors)
    expected_raw = body(expected); expected.clear()
    boundary_counts = {'enter': 0, 'return': 0}
    def observe(machine, event):
        boundary_counts[event] += 1
        current_bindings(machine)
    installed = Installed(binding, native(), binding.catalogue, observe)
    result = installed.run(source, descriptors)
    need(body(result) == expected_raw, 'actual two bridge legs and root return unchanged')
    if adopt:
        result.clear()
        result = installed.run(source, descriptors)
        need(body(result) == expected_raw, 'second root and original recursive returns after adoption')
    need(len(observations) == (2 if adopt else 1), 'one chosen full-cover fence per root generation')
    need(body(source) == source_image and all(body(v.tape) == desc_images[n]
        for n, v in descriptors.items()), 'borrowed root payload and encoded descriptors preserved')
    need(service.stage == 'closed' and acquisition.state == 'closed'
         and all(t.read() == BLANK for t in (*service.roles, *acquisition.packets,
                                            acquisition.output)), 'all full-output backing retired')
    receipt = dict(status='PASS_ACTUAL_FULL_BANK_LIFECYCLE_AND_BRIDGE', outputs=families, private=16,
        geometry_dimension=2, whole_cover_families=families, covers=2, outer_prefixes=2,
        producer_width=width, reached_fences=len(observations),
        root_invocations=2 if adopt else 1, actual_recursive_boundaries=boundary_counts,
        ancestor_frames_preserved_at_fences=sum(int(r['ancestor']) for r in observations),
        complex_values=len(values), actual_bridge_legs_per_cover=2,
        internal_bank_adoption=adopt,
        endpoint_sha256=sha256(expected_raw).hexdigest(), mutation_rejections=rejections,
        exact_transfer_tariff_checks=transfer_controls,
        control_inclusive_service_cell_actions={k: sum(m[k] for m in meters) for k in ('reads','writes','moves')},
        fixed_service_tapes=2*families+97,
        all_parent_roles_preserved=True, cleanup=True,
        scope='Actual source Machine, BankPackets, Tape/Count and both bridge scalar legs; identity service tests storage only, not QQ16 arithmetic, selected O73 execution or complete supplier.')
    result.clear(); source.clear()
    for value in descriptors.values(): value.close()
    return receipt


def adoption_fixture():
    """Exact paired commit meters and source Parking's nonempty-frame codec.

    Boundary payloads/ancestor frames are fixture oracles. The full fixture()
    separately reaches the fence through actual Machine execution.
    """
    from types import SimpleNamespace
    from fixture_binding import FixtureBinding
    from machine import Machine, origin
    from bank_packets import BankPackets, arm_empty
    from macro_code import Code
    from ordinary import Ordinary
    from words import BLANK
    def body(t): return bytes(t.cells[1:]).rstrip(bytes([BLANK]))
    def make(size, ancestor):
        binding = FixtureBinding()
        native = Ordinary(2, SimpleNamespace(codes=SimpleNamespace(q=2)),
            SimpleNamespace(families=0), (Code((('unreachable',),), 0),), capacity=64)
        parent = Machine(binding, native, binding.catalogue)
        parent.closed = False; parent.mode = 'group'; parent.group = None
        original_ancestor = None
        if ancestor:
            for i, tape in enumerate(parent.parked):
                origin(tape)
                for digit in (i & 1, 12, 13): tape.append(digit)
                tape.rewind()
            original_ancestor = tuple(body(t) for t in parent.parked)
            parent.parking.park()
        for i in range(size): parent.roles['current'].append(i & 1)
        parent.roles['current'].rewind()
        acquired = BankPackets(2, 1, 1)
        for tape in (acquired.output, *acquired.packets): arm_empty(tape)
        for i in range(size): acquired.output.append((i+1) & 1)
        acquired.output.rewind()
        for i in range(size//2): acquired.packets[0].append(i & 1)
        acquired.packets[0].rewind()
        acquired.source = parent.roles['current']; acquired.state = 'returned'
        return parent, acquired, original_ancestor
    cases = []
    mutations = []
    def reject(name, action):
        try: action()
        except ValueError: mutations.append(name)
        else: raise ValueError('accepted adoption mutation: ' + name)
    for size in (2, 6, 18, 66):
        costs = []
        for adopt in (False, True):
            parent, acquired, ancestor = make(size, adopt)
            old = parent.roles['current']; new = acquired.output
            public = parent.output
            stack_image = (body(parent.parking.stack), parent.parking.stack.head)
            expected = body(new)
            tapes = (old, new, *acquired.packets)
            before = [t.meter.record() for t in tapes]
            if adopt: adopt_bank(parent, acquired, BLANK)
            else: acquired.commit(old)
            costs.append({k: sum(t.meter.record()[k]-b[k] for t,b in zip(tapes,before))
                          for k in ('reads','writes','moves')})
            need(body(parent.roles['current']) == expected and parent.output is public,
                 'adoption completed value and immutable public output')
            need((body(parent.parking.stack), parent.parking.stack.head) == stack_image,
                 'encoded ancestor frame untouched by adoption')
            if adopt:
                good = parent.parked
                parent.parked = tuple(old if t is new else t for t in good)
                reject('omitted parked binding', lambda: current_bindings(parent))
                parent.parked = good
                parent.parking.roles = tuple(old if t is new else t for t in good)
                reject('omitted parking binding', lambda: current_bindings(parent))
                parent.parking.roles = good
                for tape in parent.parked: origin(tape); tape.clear()
                parent.parking.restore()
                need(tuple(body(t) for t in parent.parked) == ancestor,
                     'actual Parking restores ancestor bodies into rebound logical roles')
                parent.parking.empty()
            for tape in (*parent.parked, acquired.output): origin(tape); tape.clear()
        saving = {k: costs[0][k]-costs[1][k] for k in ('reads','writes','moves')}
        need(saving == dict(reads=5*size+2, writes=2*size, moves=4*size+2),
             'exact current-bank adoption action difference')
        need(sum(saving.values()) == 11*size+4, 'exact whole-bank adoption saving')
        cases.append(dict(bank_bits=size, baseline=costs[0], adopted=costs[1], saved=saving))
    for mutation in ('cached external current alias', 'invalid returned binary symbol'):
        parent, acquired, _ = make(6, False)
        old = parent.roles['current']; new = acquired.output
        old_image, old_binding = body(old), parent.parked
        if mutation == 'cached external current alias':
            reject(mutation, lambda: adopt_bank(parent, acquired, BLANK, (old,)))
        else:
            new.write(3)
            reject(mutation, lambda: adopt_bank(parent, acquired, BLANK))
        need(parent.roles['current'] is old and parent.parked == old_binding
             and parent.parking.roles == old_binding and body(old) == old_image
             and old.head == new.head == 1, 'rejected adoption preserves source and bindings')
        for tape in (*parent.parked, acquired.output, *acquired.packets):
            origin(tape); tape.clear()
    return dict(status='PASS_EXACT_BANK_ADOPTION_AND_REBOUND_PARKING', cases=cases,
                mutations=mutations, nonempty_ancestor_codec_cases=4,
                saving='11*B+4 tape cell actions; plus separately charged finite role-control cost',
                scope='Actual source commit, Tape and Parking at synthetic admitted body boundaries; full actual controller adoption/continuation is fixture(adopt=True).')
