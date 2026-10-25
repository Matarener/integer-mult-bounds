# write the 112 F2^9 labels (one integer per line of P112) for cntsub.c
import sys,os; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from base import LAB
open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'labels.txt'),'w').write(' '.join(map(str,LAB)))
print('labels.txt written',len(LAB))
