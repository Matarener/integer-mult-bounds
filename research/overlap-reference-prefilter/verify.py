"""Exact search-equivalence and work controls for the numeric-reference prefilter."""
import hashlib
import importlib.util
from itertools import product
import json
from pathlib import Path
import re
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent


def need(ok, message):
    if not ok:
        raise ValueError(message)


def legacy_position(text, term, pattern):
    if pattern is None:
        return text.find(term)
    match = pattern.search(text)
    return match.start() if match else -1


def expression(term):
    return re.compile(r"(?<![\w.])(?:pr(?:\s*#)?\s*)?" + re.escape(term) + r"(?!\w|\.\d)")


def positions(module):
    checked = 0
    for width in range(6):
        for letters in product("12p# .é", repeat=width):
            text = "".join(letters)
            for term in ("1", "12"):
                pattern = expression(term)
                got = module.match_position(text, term, pattern)
                need(got == legacy_position(text, term, pattern), "numeric match offset")
                need(module.match_position(text, term, None) == text.find(term), "literal offset")
                checked += 1
    return checked


def corpus():
    texts = ["", "2977", "PR2977", "pr # 2977", "#2977", "0.0012977", "a2977b",
             "2977.5", "é2977", "x_2977", "29770", "12977", "XPR2977",
             "İ" * 130 + " PR2977", "a2977b " + "x" * 600 + " PR #2977",
             "https://github.com/CrocSwap/integer-mult-bounds/pull/2977", "01021323"]
    return [{"kind": "pr", "number": index, "title": title, "body": body,
             "url": "https://example.invalid/" + str(index)}
            for index, (title, body) in enumerate(product(texts, repeat=2))]


def reports(module):
    records = corpus()
    checks = 0
    for terms, references in ((["2977"], ["2977"]), (["2977"], []),
                              (["2977", "PR"], ["2977"]),
                              (["01021323", "2977", "2977"], ["2977"])):
        for all_terms in (False, True):
            got = module.search(records, terms, all_terms, references)
            with patch.object(module, "match_position", legacy_position):
                expected = module.search(records, terms, all_terms, references)
            need(got == expected, "full matches/scores/excerpts/order differ")
            checks += 1
    return {"records": len(records), "complete_search_comparisons": checks}


def work_controls(module):
    class Counted:
        def __init__(self):
            self.calls = 0
            self.pattern = expression("2977")

        def search(self, text):
            self.calls += 1
            return self.pattern.search(text)

    counter = Counted()
    need(module.match_position("absent " * 10000, "2977", counter) == -1, "absent reference")
    need(counter.calls == 0, "absent literal still scanned by regex")
    for text in ("a2977b", "0.0012977", "2977.5", "word_2977", "é2977"):
        need(module.match_position(text, "2977", counter) == -1, "false reference admitted")
    need(counter.calls == 5, "present literal skipped boundary check")
    need(module.match_position("pr #2977", "2977", counter) == 0, "prefix offset lost")
    need(module.match_position("a2977b", "2977", None) == 1, "explicit literal changed")
    return {"absent_regex_calls": 0, "present_regex_calls": counter.calls,
            "boundary_rejections": 5, "literal_and_prefix_controls": 2}


def main():
    source = ROOT / "scripts/find_overlap.py"
    spec = importlib.util.spec_from_file_location("overlap_prefilter_verify", source)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    result = {"position_comparisons": positions(module), **reports(module),
              "work_controls": work_controls(module)}
    files = [*sorted(PACKAGE.glob("*.py")), *sorted(PACKAGE.glob("*.json")),
             PACKAGE / "README.md", source, ROOT / "tests/test_research_overlap_terms.py"]
    result["sha256"] = {path.relative_to(ROOT).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
                        for path in files}
    print("PASS_OVERLAP_REFERENCE_PREFILTER")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
