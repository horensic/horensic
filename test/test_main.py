import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath('../horensic/filesystem')))
sys.path.insert(0, os.path.dirname(os.path.abspath('../utils')))
from horensic.filesystem.ntfs import *
from utils.timestamp import *

if __name__ == '__main__':
    test = NTFS()
    mft = test.read_mft()