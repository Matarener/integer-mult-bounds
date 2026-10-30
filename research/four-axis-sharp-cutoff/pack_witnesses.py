"""Pack the optional C++ witness output. Ali Romman with Codex assistance."""
from pathlib import Path
import gzip
import json
import sys

rows = [list(map(int, line.split())) for line in Path(sys.argv[1]).read_text().splitlines()]
if len(rows) != 65536 or [row[0] for row in rows] != list(range(65536)):
    raise ValueError('Complete ordered character inventory required')
if any(len(row) != 3 or not 0 <= row[2] < 2**64 for row in rows):
    raise ValueError('Malformed witness row')
raw = json.dumps([row[2] for row in rows], separators=(',', ':')).encode()
Path(sys.argv[2]).write_bytes(gzip.compress(raw, mtime=0))
