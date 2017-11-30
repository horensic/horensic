import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath('../horensic/filesystem')))
sys.path.insert(0, os.path.dirname(os.path.abspath('../utils')))
from horensic.filesystem.ntfs import *

if __name__ == '__main__':
    test = NTFS()
    root = test.get_root()
    test.get_index_list(root)
    #f = open(os.path.abspath('../test/index.txt'), 'wb')
    #for ofs in test.get_index_list(root):
    #    f.write(ofs)
    #f.close()
