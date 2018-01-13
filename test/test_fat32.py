import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath('../horensic/filesystem')))
sys.path.insert(0, os.path.dirname(os.path.abspath('../utils')))
from horensic.filesystem.fat32 import *


if __name__=='__main__':
    fs = FAT32('E:\\')
    fs.get_root()
    for i in fs.root_dir:
        print("{0:<30} | {1:>20} | {2:>20} | {3:>20}".format(i['name'].strip(), i['created_time'], i['modified_time'], i['accessed_time']))


