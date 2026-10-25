"""Consumer-column sign test for staged544 helpers 600 and 601."""

import gzip
import hashlib
import json
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
HELPERS = (600, 601, 602, 604)
FRAME = (45,)
ORDER = (123, 175, 183, 202)
SIGNS = {
    600: (-1, 1, 1, -1),
    601: (1, 1, 1, 1),
    602: (-1, 1, 1, 1),
    604: (-1, -1, 1, -1),
}
HASHES = {
    "WORD-base.json.gz": "08e6c96fbe3dfec96cb8451b3867ef8c1a214109ecd1e5af7fcc28e0f05728d0",
    "WORD-extra.json.gz": "d83c2ec9cecc0ad092d34ea4080b28a4fd7199579356b6d5a8fc6cd53ff93299",
}
LEMMA = (
    "On both frozen PR3945 words, the frame-(45,) consumer columns of "
    "helpers 600 and 601 are neither equal nor opposite."
)


def require(ok, why):
    if not ok:
        raise SystemExit(why)


def load_word(name):
    raw = (PACKAGE / "frozen" / name).read_bytes()
    require(hashlib.sha256(raw).hexdigest() == HASHES[name], "word hash changed: " + name)
    return json.loads(gzip.decompress(raw))


def consumer_adds(word, helper):
    found = []
    for section, rows in word.items():
        if not isinstance(rows, list):
            continue
        for index, row in enumerate(rows):
            if not isinstance(row, list) or not row or row[0] != "add":
                continue
            require(len(row) >= 6, "short add")
            if row[2] == helper:
                require(isinstance(row[3], int), "non-integer coefficient")
                require(isinstance(row[5], list), "frame is not a list")
                found.append((section, index, row[1], row[3], tuple(row[5])))
    return found


def frame_column(adds, frame):
    column = {}
    for _section, _index, destination, coefficient, row_frame in adds:
        if row_frame == frame:
            column[destination] = column.get(destination, 0) + coefficient
    require(set(column) == set(ORDER), "frame-(45,) consumers changed")
    return tuple(column[destination] for destination in ORDER)


def single_sign(left, right):
    ratios = []
    for x, y in zip(left, right):
        require(x != 0 and y != 0 and abs(x) == abs(y), "column is not a sign pattern")
        ratios.append(y // x)
    return len(set(ratios)) == 1


def main():
    require(LEMMA in (PACKAGE / "README.md").read_text(encoding="utf-8"), "README dropped the lemma")
    columns = []
    for name in HASHES:
        word = load_word(name)
        one = {}
        for helper in HELPERS:
            adds = consumer_adds(word, helper)
            require(len(adds) == 7, "expected 7 consumer adds for " + str(helper))
            column = frame_column(adds, FRAME)
            require(column == SIGNS[helper], "frame column changed for " + str(helper))
            one[helper] = column
        columns.append(one)
    require(columns[0] == columns[1], "the two words disagree on these columns")
    require(not single_sign(SIGNS[600], SIGNS[601]), "600 and 601 unexpectedly match")
    for left in HELPERS:
        for right in HELPERS:
            if left < right:
                require(not single_sign(SIGNS[left], SIGNS[right]), "pair unexpectedly matches")
    flipped = (1, 1, 1, -1)
    # Consumers 123 and 202 are the disagreements. Flipping both makes 601 equal 600.
    repaired = (-1, 1, 1, -1)
    require(repaired == SIGNS[600] and single_sign(SIGNS[600], repaired), "sign-flip control failed")
    require(not single_sign(SIGNS[600], flipped), "partial flip must stay unmatched")
    print("PASS_STAGED544_HELPER600_SIGN_COLUMNS")


if __name__ == "__main__":
    main()
