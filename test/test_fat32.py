import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath('../horensic/filesystem')))
sys.path.insert(0, os.path.dirname(os.path.abspath('../utils')))
from horensic.filesystem.fat32 import *


if __name__=='__main__':
    fs = FAT32('E:\\')
    fs.get_root()
    root = fs.root_dir
    for i in fs.next_dir(root, 'TEST'):
        print(i['name'])



