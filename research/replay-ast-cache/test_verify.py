#!/usr/bin/env python3
"""Predicate checks for a changed producer missing the stage cache."""

from verify import cached_stages, stage_names


def main():
    data = b"def run(name):\n    return name\nrun('one')\n"
    fresh = stage_names(data)
    cache = {}
    assert cached_stages(data, cache) == fresh == ["one"]
    stale = {"digest": b"stale", "stages": ["missing"]}
    changed = data + b"run('two')\n"
    assert cached_stages(changed, stale) == ["one", "two"]
    assert stale["stages"] != ["missing"]
    print("PASS_REPLAY_AST_CACHE_TEST")


if __name__ == "__main__":
    main()
