import struct

# Volume Boot Record
VBR_FORMAT = '<3s8sHBH5sc10s8sQQQB3sB3sQI426sH'
VBR_FIELDS = [
    'jump_boot_code',  # 3bytes
    'oem_id',  # 8 bytes
    'bps',  # bytes per sector
    'spc',  # sectors per cluster
    'reserved',  # reserved sectors
    'unused1',
    'media',
    'unused2',
    'unused3',
    'total_sectors',
    'mft',
    'mft_mirror',
    'clusters_per_mft_record',
    'unused4',
    'clusters_per_index_buffer',
    'unused5',
    'vsn',  # volume serial number
    'unused5',
    'bootstrap_code',  # 426 bytes
    'eos'  # 2bytes, End of sector marker: \x55\xAA
]
VBR_SZ = struct.calcsize(VBR_FORMAT)


# Master File Table

# MFT Record
MFT_RECORD_HDR_FORMAT = '<4sHHQHHHHIIQHHI'
MFT_RECORD_HDR_FIELDS = [
    'signature',
    'fixup_offset',
    'fixup_entries',
    'lsn',  # $LogFile Sequence Number (LSN)
    'seq_num',  # Sequence Number
    'hardlink_cnt',  # Hard Link count
    'offset',  # offset to file attribute
    'flags',
    'real_size',
    'alloc_size',
    'base_record',
    'next_attr_id',
    'xp_boundary',
    'xp_num'
]
MFT_RECORD_HDR_SZ = struct.calcsize(MFT_RECORD_HDR_FORMAT)

# Attributes
ATTR_COMMON_HDR_FIELDS = [
    'type',
    'length',
    'non_resident',
    'name_len',
    'name_offset',
    'flags',
    'id'
]

RESIDENT_ATTR_HDR_FIELDS = [
    'size',
    'offset',
    'flag',
    'name'
]

NON_RESIDENT_ATTR_HDR_FIELDS = [
    'start_vcn',
    'end_vcn',
    'run_list',
    'comp_unit_size',
    'unused',
    'alloc_size',
    'real_size',
    'init_size',
    'name'
]

STANDARD_INFO_FIELDS = [
    'create_time',
    'modified_time',
    'mft_modified_time',
    'last_accessed_time',
    'flags',
    'max_version',
    'version',
    'class_id',
    'owner_id',
    'security_id',
    'quota',
    'usn'  # Update Sequence Number (UCN)
]

ATTR_LIST_FIELDS = [
    'type',
    'length',
    'name_len',
    'name_offset',
    'start_vcn',
    'reference_addr',
    'id'
]