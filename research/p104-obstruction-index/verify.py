#!/usr/bin/env python3
"""Index the two P104 obstruction replays the live map does not name.

The family record points at the support map. The map separates event-touch
order from the frame-support cut. This checker confirms that separation and
the two replay notes. It does not import either package.
"""

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
MARKER = "PASS_P104_OBSTRUCTION_INDEX map_omits_replays=true no_new_kappa"
TOUCH = "research/p104-channel-touch-restoration-audit"
POOLED = "research/p104-pooled-cut-independent"


def fail(message):
    raise SystemExit("FAIL_P104_OBSTRUCTION_INDEX " + message)


def require(condition, message):
    if not condition:
        fail(message)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def omitted(text, name):
    return name not in text


def authenticate():
    sources = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    pinned = {row["path"]: row for row in sources["files"] if row["usage"] == "input"}
    expected = {
        "docs/research/research-family-status.md",
        "docs/research/p104-live-support-map.md",
        "research/p104-channel-touch-restoration-audit/README.md",
        "research/p104-pooled-cut-independent/README.md",
    }
    require(set(pinned) == expected, "input inventory changed")
    for path, row in pinned.items():
        require(sha256(ROOT / path) == row["sha256"], "input drift " + path)


def evaluate():
    authenticate()
    family = (ROOT / "docs/research/research-family-status.md").read_text(encoding="utf-8")
    support_map = (ROOT / "docs/research/p104-live-support-map.md").read_text(encoding="utf-8")
    touch = (ROOT / "research/p104-channel-touch-restoration-audit/README.md").read_text(encoding="utf-8")
    pooled = (ROOT / "research/p104-pooled-cut-independent/README.md").read_text(encoding="utf-8")
    require(
        "see the [Oct. 17 fixed-cover support and chronology map](p104-live-support-map.md)" in family,
        "the family record no longer points at the map",
    )
    require(
        "The event-touch result in #3242 and the frame-support result in #3259 have\n"
        "different meanings." in support_map,
        "the map no longer separates the two claims",
    )
    require(omitted(support_map, TOUCH) and omitted(support_map, POOLED), "the map now names a replay")
    require(
        "The #3259 support cut is already certified on pinned main by\n"
        "`research/p104-pooled-cut-independent`." in touch,
        "the touch note no longer names the support replay",
    )
    require(
        "every target is first touched at or before\n"
        "event 410, every source is first touched at or after event 488" in touch,
        "the event-touch bound moved",
    )
    require(
        "precisely `(Y71,X102)` is absent from the\n"
        "necessary relaxation on all 2,309 compatible endpoint pairs. Its required\n"
        "coefficient is `-1/2`." in pooled,
        "the missing pair moved",
    )
    require(
        "This does not\n"
        "exclude changed covers, changed helper contracts, added storage or an altered\n"
        "original channel." in pooled,
        "the support exclusion moved",
    )
    return {
        "family_points_at_map": True,
        "map_names_touch_replay": False,
        "map_names_support_replay": False,
        "touch_replay_names_support": True,
        "missing_pair": "Y71,X102",
        "missing_coefficient": "-1/2",
        "event_touch_bound": "410<488",
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    expected = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == expected, "RESULT.json does not match the execution")
    print(MARKER)


if __name__ == "__main__":
    main()
