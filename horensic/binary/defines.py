import struct
# from collections import namedtuple

""" PE """

# DOS Header
DOS_HDR_FORMAT = '<2s13H8s2H20sI'
DOS_HDR_FILED = [
    'e_magic',   'e_cblp',     'e_cp',       'e_crlc',
    'e_cparhdr', 'e_minalloc', 'e_maxalloc', 'e_ss',
    'e_sp',      'e_csum',     'e_ip',       'e_cs',
    'e_lfarlc',  'e_ovno',     'e_res[4]',   'e_oemid',
    'e_oeminfo', 'e_res2[10]', 'e_lfanew'
]
DOS_HDR_SZ = struct.calcsize(DOS_HDR_FORMAT)

# NT Image File Header
IMG_FILE_HDR_FORMAT = '<'
IMG_FILE_HDR_FILED = []
IMG_FILE_HDR_SZ = struct.calcsize(IMG_FILE_HDR_FORMAT)

# NT Image Optional Header
IMG_OPT_HDR_FORMAT = '<'
IMG_OPT_HDR_FILED = []
IMG_OPT_HDR_SZ = struct.calcsize(IMG_OPT_HDR_FORMAT)

# Section Header


