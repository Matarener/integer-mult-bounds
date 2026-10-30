# SPDX-License-Identifier: Apache-2.0
"""Install a completed whole-cover recovery service in the actual parent.

Only encoded Counts and source Tape operations inspect input-sized quantities.
Finite source bindings and the three exclusive engines are compiled first.
Chris R / Clear1nsight, substantial OpenAI Codex assistance.
"""

def need(ok,why):
    if not ok:raise ValueError(why)


def owned_tapes(owner):
    """Compile-time census of fixed physical roles, excluding control bindings.

    No Tape body or input-sized descriptor is traversed. The separately shared
    original child is inventoried once, rather than mistaken for an alias.
    """
    import types
    from records import Tape
    seen=set();tapes={}
    skip={'binding','catalogue','group','data','source','native_child','at_fence',
          'observe','codes','recipes','template','packet','core','events','word'}
    def visit(v):
        if id(v) in seen:return
        seen.add(id(v))
        if isinstance(v,Tape):tapes[id(v)]=v;return
        if isinstance(v,dict):
            for item in v.values():visit(item)
        elif isinstance(v,(tuple,list)):
            for item in v:visit(item)
        elif not isinstance(v,(type,types.ModuleType,types.FunctionType,types.MethodType)) and hasattr(v,'__dict__'):
            for k,item in vars(v).items():
                if k not in skip:visit(item)
    visit(owner)
    return tuple(tapes.values())


class Installation:
    def __init__(self, parent_binding, service_machine, native_child,
                 PacketCompiler, CallerStorage, ServiceBank, fields=224, adopt=True):
        from bank_packets import BankPackets
        from cardinal_counts import Count
        from machine import transfer
        from records import Tape
        from scalar_words import require_zero
        from scratch_pool import ScratchPool
        from session import OuterScope
        from stream import Counter
        from words import BLANK
        need(service_machine is not native_child and service_machine.native_child is native_child,
             'one exclusive original C backend for the sequential service')
        self.binding=parent_binding
        self.service,self.native_child=service_machine,native_child
        self.fields=fields
        need(type(adopt) is bool,'compiled publication choice')
        self.adopt=adopt
        self.acquisition=BankPackets(parent_binding.families,1,fields)
        self.compiler=PacketCompiler()
        self.bundle=ServiceBank(Tape,Counter,BLANK,fields)
        self.pool=ScratchPool(256);self.scope=OuterScope(self.pool)
        self.engine_roles=(owned_tapes(service_machine),owned_tapes(native_child))
        need(not ({id(t) for t in self.engine_roles[0]} & {id(t) for t in self.engine_roles[1]}),
             'separate complete native and service Ordinary/Compact inventories')
        auxiliary=(*self.compiler.roles.values(),*self.compiler.snapshots,*self.compiler.pool.tapes,
                   self.bundle.bank,*self.pool.tapes)
        self.storage=CallerStorage(Tape,Count,Counter,BLANK,transfer,require_zero,
            outputs=fields,private=16,expected_event=parent_binding.global_fence,
            engines=(service_machine,native_child),
            external_roles=(*self.engine_roles[0],*self.engine_roles[1],*auxiliary))
        self.calls=0
        self.completed=False

    def discard(self):
        """Retire owned partial service backing after a controlled rejection.

        The enclosing source Machine owns its current bank and performs its
        own discard. Borrowed original root input and descriptors are untouched.
        Arbitrary asynchronous interruption recovery is not asserted.
        """
        from session import erase_marker
        from words import LEFT,BLANK
        def retire(tape):
            # Successful/controlled-return contracts place these fixed roles
            # at their canonical origins, sometimes with the marker erased.
            tape.step(-1)
            marker=tape.read()
            need(marker in (LEFT,BLANK),'controlled discard at canonical role origin')
            if marker==BLANK:tape.write(LEFT)
            tape.step(1)
            tape.clear()
            if marker==BLANK:erase_marker(tape)
        for engine in (self.service,self.native_child):engine.discard()
        for roles in self.engine_roles:
            for tape in roles:retire(tape)
        for tape in (*self.storage.roles,*self.acquisition.packets,
                     self.acquisition.output,*self.acquisition.pool.tapes,
                     self.bundle.bank,*self.compiler.roles.values(),*self.compiler.snapshots,
                     *self.compiler.pool.tapes,*self.pool.tapes):
            retire(tape)
        self.acquisition.source=self.acquisition.selection=None
        self.acquisition.state='closed'
        self.bundle.state='closed';self.compiler.closed=True
        self.storage.stage='closed'
        self.storage.parent=self.storage.cut=self.storage.targets=self.storage.acquisition=None
        self.completed=False

    def __call__(self,parent):
        from cardinal_counts import Count
        from session import borrowed_count,sealed_constructors
        from words import BLANK
        from qq16_decoder import service_descriptors
        need(parent.binding is self.binding and parent is not self.service
             and parent is not self.native_child,'literal caller and separate engines')
        need(parent.fence_calls==1 and self.storage.stage=='closed'
             and self.bundle.state=='closed','one closed caller installation per root invocation')
        parent_roles={id(t) for t in owned_tapes(parent)}
        need(not parent_roles.intersection(id(t) for roles in self.engine_roles for t in roles),
             'active producer and original/service engines have distinct fixed inventories')
        self.calls+=1
        self.completed=False
        owned=[]
        def keep(v):owned.append(v);return v
        try:
            with sealed_constructors(),self.scope.installed():
                full_row=keep(Count(parent.c('row_bits')))
                full_row.multiply_small(parent.binding.cover.size)
                prefix_extent=keep(Count.product(parent.c('unused'),full_row))
                full_extent=keep(Count.product(parent.c('prefixes'),prefix_extent))
                self.acquisition.select(tuple((i,0) for i in range(self.fields)))
                with self.scope.suspended():
                    fields=self.acquisition.gather(parent.roles['current'],
                        *(borrowed_count(v) for v in
                          (parent.c('prefixes'),parent.c('unused'),full_row)))
                    self.compiler.compile_global(parent,fields[0],self.binding.global_fence)
                self.storage.begin(parent,self.acquisition,tuple(range(self.fields)))
                payload=self.bundle.assemble(fields,parent.c('prefixes'),prefix_extent)
                descriptors=service_descriptors(parent,Count,self.service.binding.families)
                try:
                    with self.scope.suspended():returned=self.service.run(payload,descriptors)
                    self.bundle.extract(returned,fields,self.storage.outputs,
                                        parent.c('prefixes'),prefix_extent)
                finally:
                    for value in descriptors.values():value.close()
                self.storage.decoded(full_extent)
                self.storage.ready(full_extent,True)
                with self.scope.suspended():
                    self.storage.commit(*(borrowed_count(v) for v in
                        (parent.c('prefixes'),parent.c('unused'),full_row)),adopt=self.adopt)
                self.compiler.close()
                need(self.service.closed and self.native_child.closed and
                     self.service.output.read()==BLANK and self.native_child.output.read()==BLANK,
                     'completed engines and consumed protected outputs')
                need(self.bundle.state=='closed' and self.storage.stage=='closed',
                     'service banks and caller output generation retired')
                self.completed=True
        except BaseException:
            self.discard()
            raise
        finally:
            for value in reversed(owned):value.close()
            self.pool.empty()


def attach_root(root_layer, producer_machine):
    """Compile-time replacement of the actual RootLayer.fast_core Machine.

    Retain its former original Machine as the producer's separate child engine.
    No payload, fixed public input/output port or root-plan field is rebound.
    """
    from words import BLANK
    need(root_layer.closed and producer_machine.closed and
         root_layer.current.read()==BLANK and root_layer.output.read()==BLANK,
         'closed root construction before numerical input')
    need(producer_machine.native_child is root_layer.machine,
         'retain the root original C engine rather than an endpoint double')
    need(root_layer.machine.closed and root_layer.machine.output.read()==BLANK,
         'closed inherited exact C endpoint')
    original=root_layer.machine.binding
    replacement=producer_machine.binding
    need(all(getattr(original,k)==getattr(replacement,k)
             for k in ('dimension','maximum_rank','families')) and
         original.cover.size==replacement.cover.size,
         'unchanged root-plan dimension rank family and cover geometry')
    root_layer.machine=producer_machine
    return root_layer
