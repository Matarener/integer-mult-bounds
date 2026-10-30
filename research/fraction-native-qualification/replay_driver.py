"""Explicit complete replay; includes all new checks and a cold native build."""
import sys
from frozen import require
import custody
from full import main
if __name__=='__main__':
    require(len(sys.argv)==1,'No replay arguments')
    custody.main()
    main(True)
