import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath('../horensic/eventlog')))
from horensic.eventlog.evtx import *


if __name__ == '__main__':

    for root, dirs, files in os.walk('sample'):
        for file in files:
            ext = os.path.splitext(file)[-1]
            if ext == '.evtx':
                evtx_file = os.path.join(root, file)
                with Evtx(evtx_file) as eventlog:
                    for r in eventlog.records():
                        r.binxml()
