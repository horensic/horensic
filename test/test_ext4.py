import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath('../horensic/filesystem')))
sys.path.insert(0, os.path.dirname(os.path.abspath('../utils')))
from horensic.filesystem.ext4 import *

if __name__=='__main__':

    sample = 'sample/ext4.dd'
    ext4fs = EXT4(sample)
    # for k, v in iter(ext4fs):
    #    print(k, v)
