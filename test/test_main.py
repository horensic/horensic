import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath('../horensic/filesystem')))
sys.path.insert(0, os.path.dirname(os.path.abspath('../utils')))
from horensic.filesystem.ntfs import *

if __name__ == '__main__':
    test = NTFS()
    root = test.get_root()
    mft0 = test.read_mft()
    f = open(os.path.abspath('../test/mftlist.txt'), 'wt')
    for mft in test.get_mft_list(mft0):
        f.write(str(mft) + '\n')
    f.close()