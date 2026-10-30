"""Fresh complete qualification; no saved acceptance receipt is reused."""
import sys

from candidate import run
from retained import baseline
from setup_cache import require


if __name__ == '__main__':
    require(not sys.argv[1:], 'No verification arguments')
    with baseline() as base:
        run(base)
