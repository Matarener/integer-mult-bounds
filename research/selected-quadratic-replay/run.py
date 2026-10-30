"""Run the complete selected scientific check with explicit state adapters."""
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import binding
from pins import authenticate
import verify_source


def main():
    if sys.argv[1:]:
        raise ValueError('No arguments are accepted')
    authenticate()
    binding.check()
    verify_source.main([])


if __name__ == '__main__':
    main()
