#!/usr/bin/env python3
"""Replay the arbitrary-plane extension of PR1996. Apache-2.0."""
from __future__ import annotations

import gzip
import hashlib
import importlib.util
import io
import json
import tarfile
from fractions import Fraction
from pathlib import Path

from model import chain_profile, event_model
from sweep import census

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
ARCHIVE = "research/community-frontier1094-audit/selected-replay.tar.gz"
MEMBER = "candidate/strict/global/base/providers/gauge44/FULL-WORD.json.gz"


def require(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def load_word() -> tuple[dict, str]:
    sources = json.loads((PACKAGE / "SOURCES.json").read_text())
    for item in sources["files"]:
        if item["usage"] == "input":
            raw = (ROOT / item["path"]).read_bytes()
            require(hashlib.sha256(raw).hexdigest() == item["sha256"], "live source hash mismatch")
    with tarfile.open(fileobj=io.BytesIO((ROOT / ARCHIVE).read_bytes()), mode="r:gz") as archive:
        stream = archive.extractfile(MEMBER)
        require(stream is not None, "word archive member missing")
        raw = stream.read()
    digest = hashlib.sha256(raw).hexdigest()
    require(digest == "49596aa4ed4fd36cd4582fd0e8ddeb09fd80370a7d8aea1ede52a135b536d289", "word hash")
    return json.loads(gzip.decompress(raw)), digest


def cost_comparison(baseline: tuple[int, ...], rows: list[dict]) -> dict:
    path = ROOT / "research/complex-local-word-ceiling/ceiling.py"
    spec = importlib.util.spec_from_file_location("historical_ceiling", path)
    require(spec is not None and spec.loader is not None, "interval engine load")
    engine = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(engine)
    lower, upper = Fraction(1690054109, 10**12), Fraction(169005411, 10**11)
    width = Fraction(896, 9)
    mass = sum(rank * count for rank, count in enumerate(baseline))
    idle = 72 * width + 64 - mass
    costs = {rank: engine.child_cost(rank, 73, lower) for rank in (*range(1, 10), 51)}
    baseline_cost = sum(count * costs[rank][1] for rank, count in enumerate(baseline) if count)
    require((baseline_cost + idle / 51 * costs[51][1]) / width < 1, "baseline lower endpoint")
    hist = {rank: count for rank, count in enumerate(baseline) if count}
    require(engine.relax(hist, 73, 896, 9, 64, upper)[0] > 1, "baseline upper endpoint")
    margins = []
    ties = 0
    for row in rows:
        profile = tuple(row["profile"])
        if profile == baseline:
            ties += 1
            continue
        paid = sum(count * costs[rank][0] for rank, count in enumerate(profile) if count)
        margin = (paid + idle / 51 * costs[51][0]) / width - 1
        require(margin > 0, "an arbitrary plane may improve the ceiling")
        margins.append(margin)
    require(ties == 1 and len(margins) == len(rows) - 1, "unique optimal profile")
    return {"baseline_ceiling": [str(lower), str(upper)],
            "other_profiles_rejected_at": str(lower),
            "minimum_other_moment_excess_lower_bound": str(min(margins))}


def compute() -> dict:
    word, digest = load_word()
    events, baseline, registers = event_model(word)
    chain = chain_profile(events)
    require({rank: baseline[rank] - chain[rank] for rank in range(1, 10)
             if baseline[rank] != chain[rank]} == {8: 8}, "fixed centre descents")
    result = census(events, baseline, registers, 2 * word["report"]["v"])
    result["word_sha256"] = digest
    result["events"] = len(events)
    result["registers"] = registers
    result["baseline_profile"] = list(baseline)
    result["cost_comparison"] = cost_comparison(baseline, result["profiles"])
    result["implementation_sha256"] = {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in sorted(PACKAGE.glob("*.py"))}
    result["status"] = "PASS_ARBITRARY_PLANE_FRAME_RAIL_CLOSURE"
    return result


def main() -> None:
    from controls import run_controls

    result = compute()
    expected = json.loads((PACKAGE / "RESULT.json").read_text())
    require(result == expected, "census differs from generated exact result")
    controls = run_controls(result)
    print(result["status"], "pairs=" + str(result["domain_pairs"]),
          "changed=" + str(result["changed_legal_pairs"]),
          "profiles=" + str(len(result["profiles"])), "controls=" + str(controls))


if __name__ == "__main__":
    main()
