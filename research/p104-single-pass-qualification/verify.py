"""Full qualification plus inherited source-custody and new observation controls."""
import sys
import custody
from candidate import main
from source import require
if __name__=='__main__':
 require(len(sys.argv)==1,'No wrapper arguments')
 custody.main()
 main()
