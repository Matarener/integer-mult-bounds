"""Complete unchanged PR5831 baseline command."""
import sys
from replay import main
from source import require

if __name__ == '__main__':
    require(len(sys.argv) == 1, 'No wrapper arguments')
    sys.argv = [sys.argv[0], '--baseline']
    main()
