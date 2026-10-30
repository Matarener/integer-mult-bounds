"""Share one completed source execution between the two unchanged entry points.

This is process-local orchestration, not a persistent acceptance cache.
Chris R / Clear1nsight with OpenAI Codex assistance; Apache-2.0.
"""


def require(condition, message):
    if not condition:
        raise ValueError(message)


def qualify(verify_main, cross_main, source, adapter):
    """Execute both original checkers, observing then handing off their trace.

    Production callers authenticate the complete source before importing it.
    Only source.main and adapter.TRACE are temporarily instrumented.
    """
    require(adapter.TRACE is None, 'Clean observer entry')
    original = source.main
    snapshot = {}
    captured = consumed = 0

    def observe(argv):
        nonlocal captured
        require(type(argv) is list and argv == [], 'Exact source arguments')
        require(captured == 0 and not snapshot, 'Exactly one source execution')
        require(adapter.TRACE is None, 'No control trace contamination')
        require(not adapter.COUNTS, 'Controls reset state counters')
        info = adapter.signature.cache_info()
        require(info.hits == info.misses == info.currsize == 0, 'Controls reset cache')
        captured += 1
        adapter.TRACE = set()
        try:
            returned = original(argv)
            snapshot['trace'] = tuple(sorted(adapter.TRACE))
            snapshot['calls'] = dict(adapter.COUNTS)
            snapshot['cache'] = adapter.signature.cache_info()
            require(snapshot['trace'], 'Nonempty actual input trace')
            return returned
        finally:
            adapter.TRACE = None

    def handoff(argv):
        nonlocal consumed
        require(type(argv) is list and argv == [], 'Exact cross source arguments')
        require(captured == 1 and consumed == 0 and snapshot, 'One trace handoff')
        require(type(adapter.TRACE) is set and not adapter.TRACE, 'Fresh cross observer')
        require(dict(adapter.COUNTS) == snapshot['calls'], 'Unchanged pre-oracle counters')
        require(adapter.signature.cache_info() == snapshot['cache'], 'Unchanged pre-oracle cache')
        adapter.TRACE.update(snapshot['trace'])
        consumed += 1

    try:
        source.main = observe
        verify_main()
        require(captured == 1 and snapshot, 'Complete verify entry point')
        require(adapter.TRACE is None, 'Observer restored before cross')
        source.main = handoff
        cross_main()
        require(consumed == 1, 'Complete cross entry point')
        require(adapter.TRACE is None, 'Cross observer closed')
        return {'source_executions': captured, 'trace_handoffs': consumed,
                'distinct_inputs': len(snapshot['trace']), 'actual_state_calls': snapshot['calls']}
    finally:
        source.main = original
        adapter.TRACE = None
