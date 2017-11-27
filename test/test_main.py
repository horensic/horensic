import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath('../horensic/filesystem')))
from horensic.filesystem.ntfs import *

if __name__ == '__main__':
    test = NTFS()
    test.read_vbr()
    test.read_mft()