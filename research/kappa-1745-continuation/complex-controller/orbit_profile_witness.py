#!/usr/bin/env python3
"""Directed full-GL F2 clock-orbit traceback for one prescribed idle profile.

This is a necessary-condition search for integral dual-bridge controllers,
not a search over bounded bridge words and not an integer or dyadic lift.
The orbit reduction and rank pruning are credited to the sibling
bit-geometry/controller_clock_orbits.py. Apache-2.0; OpenAI assistance.
"""
from argparse import ArgumentParser
from collections import Counter
from functools import lru_cache
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
from time import monotonic


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SOURCE = HERE.parent / 'bit-geometry/controller_clock_orbits.py'
PIN = '243c049319312cb3ff548d500c22b5d96b40a2096ddd62d1310bfe0e976dc073'


def load_orbits():
    assert sha256(SOURCE.read_bytes()).hexdigest() == PIN
    spec = importlib.util.spec_from_file_location('source_clock_orbits', SOURCE)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.K = 4
    mod.canonical.cache_clear()
    mod.split_pairs.cache_clear()
    return mod


def search(profile, max_states):
    orbit = load_orbits()
    counts = tuple(Counter(profile)[j] for j in range(1, 7))
    assert len(profile) == 9 and sum(profile) == 27
    assert all(1 <= j <= 6 for j in profile)
    started = monotonic()
    statistics = {'orbit_nodes': 0, 'clock_rejections': 0,
                  'rank_local_edges': 0, 'idle_edges': 0}
    last_report = started
    stopped = False

    @lru_cache(None)
    def clock_viable(stage, levels, remaining):
        """Exact scalar-free clock scheduling screen, with final three climbs."""
        if stage == 9:
            final = Counter(8 - x for x in levels if x < 8)
            return remaining == tuple(final[j] for j in range(1, 7)) and not final.get(0)
        if sum(remaining) < 3:
            return False
        if stage - 1 in levels:
            nxt = list(levels)
            nxt[nxt.index(stage - 1)] = stage
            if clock_viable(stage + 1, tuple(sorted(nxt)), remaining):
                return True
        if sum(remaining) == 3:
            return False
        for low in sorted(set(levels)):
            for high in sorted(set(levels)):
                delta = high - low
                if delta <= 0 or delta > 6 or not remaining[delta - 1]:
                    continue
                nxt = list(levels)
                nxt[nxt.index(low)] = high
                left = list(remaining)
                left[delta - 1] -= 1
                if clock_viable(stage, tuple(sorted(nxt)), tuple(left)):
                    return True
        return False

    @lru_cache(None)
    def visit(stage, groups, remaining):
        nonlocal last_report, stopped
        statistics['orbit_nodes'] += 1
        if statistics['orbit_nodes'] > max_states:
            stopped = True
            raise RuntimeError('STATE_CAP')
        if monotonic() - last_report > 30:
            print(json.dumps({**statistics, 'stage': stage,
                              'seconds': monotonic() - started}), flush=True)
            last_report = monotonic()
        levels = tuple(sorted(level for level, top, _ in groups for _ in top))
        if not clock_viable(stage, levels, remaining):
            statistics['clock_rejections'] += 1
            return None
        if stage == 9:
            assert orbit.potential(groups) == 0
            return ()
        for nxt, event in orbit.local_successors(groups, stage):
            statistics['rank_local_edges'] += 1
            answer = visit(stage + 1, nxt, remaining)
            if answer is not None:
                return ({'kind': 'local', 'event': event,
                         'before': groups, 'after': nxt},) + answer
        if sum(remaining) == 3:
            return None
        for nxt, event in orbit.idle_successors(groups, max_jump=6):
            low, high, _, _ = event
            delta = high - low
            if not remaining[delta - 1]:
                continue
            statistics['idle_edges'] += 1
            left = list(remaining)
            left[delta - 1] -= 1
            answer = visit(stage, nxt, tuple(left))
            if answer is not None:
                return ({'kind': 'idle', 'event': event,
                         'before': groups, 'after': nxt},) + answer
        return None

    start = orbit.state([(0, (1,), (17,)),
                         (-1, (2, 4, 8), (32, 64, 128))])
    try:
        path = visit(1, start, counts)
    except RuntimeError as exc:
        if str(exc) != 'STATE_CAP':
            raise
        path = None
    status = 'F2_PROFILE_WITNESS' if path is not None else (
        'STOPPED_STATE_CAP' if stopped else 'NO_F2_CONTROLLER_WITH_THIS_PROFILE')
    result = {'status': status, 'profile': profile, 'K': 4,
              'initial_state_after_F0': start,
              'statistics': statistics,
              'clock_cache': clock_viable.cache_info()._asdict(),
              'orbit_cache': visit.cache_info()._asdict(),
              'seconds': monotonic() - started,
              'scope': 'Arbitrary equal-clock GL(F2) dual bridges; integral '
                       'necessary condition only. Non-integral dyadic and '
                       'rational bridges are outside this search.'}
    if path is not None:
        final = path[-1]['after']
        final_events = [(level, 8, x, y)
                        for level, top, bottom in final
                        for x, y in zip(top, bottom) if level < 8]
        actual = sorted([row['event'][1] - row['event'][0]
                         for row in path if row['kind'] == 'idle'] +
                        [8 - row[0] for row in final_events])
        assert actual == sorted(profile)
        result['events_after_F0'] = path
        result['final_idle_events'] = final_events
        result['profile_recomputed'] = actual
    return result


def main():
    ap = ArgumentParser(description=__doc__)
    ap.add_argument('--profile', default='1,1,1,2,2,3,5,6,6')
    ap.add_argument('--max-states', type=int, default=2_000_000)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    result = search([int(x) for x in args.profile.split(',')], args.max_states)
    result['source_sha256'] = {
        str(SOURCE.relative_to(ROOT)): PIN,
        str(Path(__file__).resolve().relative_to(ROOT)):
            sha256(Path(__file__).read_bytes()).hexdigest()}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, sort_keys=True, indent=2) + '\n')
    print(json.dumps({k: v for k, v in result.items()
                      if k not in ('events_after_F0', 'initial_state_after_F0')}), flush=True)


if __name__ == '__main__':
    main()
