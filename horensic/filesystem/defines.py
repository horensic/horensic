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
ATTR_COMMON_HDR_FORMAT = '<IIcBHHH'
ATTR_COMMON_HDR_FIELDS = [
    'type',
    'length',
    'non_resident',
    'name_len',
    'name_offset',
    'flags',
    'id'
]
ATTR_COMMON_HDR_SZ = struct.calcsize(ATTR_COMMON_HDR_FORMAT)

RESIDENT_ATTR_HDR_FORMAT = '<IHcc'
RESIDENT_ATTR_HDR_FIELDS = [
    'size',
    'offset',
    'flag',
    'unused'
]
RESIDENT_ATTR_HDR_SZ = struct.calcsize(RESIDENT_ATTR_HDR_FORMAT)

NON_RESIDENT_ATTR_HDR_FORMAT = '<QQHHIQQQ'
NON_RESIDENT_ATTR_HDR_FIELDS = [
    'start_vcn',
    'end_vcn',
    'offset',
    'comp_unit_size',
    'unused',
    'alloc_size',
    'real_size',
    'init_size'
]
NON_RESIDENT_ATTR_HDR_SZ = struct.calcsize(NON_RESIDENT_ATTR_HDR_FORMAT)

STANDARD_INFO_FORMAT = '<QQQQIIIIIIQQ'
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
STANDARD_INFO_SZ = struct.calcsize(STANDARD_INFO_FORMAT)

ATTR_LIST_FIELDS = [
    'type',
    'length',
    'name_len',
    'name_offset',
    'start_vcn',
    'reference_addr',
    'id'
]

FILENAME_FORMAT = '<QQQQQQQIIBc'
FILENAME_FIELDS = [
    'file_Ref_Address',
    'create_time',
    'modified_time',
    'mft_modified_time',
    'last_accessed_time',
    'file_alloc_size',
    'file_real_size',
    'flags',
    'reparse_value',
    'name_len',
    'namespace',
]
FILENAME_SZ = struct.calcsize(FILENAME_FORMAT)

INDX_R_HDR_FORMAT = '<IIIB3s'
INDX_R_HDR_FIELDS = [
    'type',
    'rule',
    'index_record_size',
    'index_record_cluster_size'
]
INDX_R_HDR_SZ = struct.calcsize(INDX_R_HDR_FORMAT)

INDX_N_HDR_FORMAT = '<IIII'
INDX_N_HDR_FIELDS = [
    'start_offset',
    'real_size',
    'alloc_size',
    'flags'
]
INDX_N_HDR_SZ = struct.calcsize(INDX_N_HDR_FORMAT)

INDX_ENTRY_FORMAT = '<QHHI'
INDX_ENTRY_FIELDS = [
    'file_ref_addr',
    'entry_size',
    'content_size',
    'flags'
]
INDX_ENTRY_SZ = struct.calcsize(INDX_ENTRY_FORMAT)
INDX_ENTRY_VCN_FORMAT = '<Q'
INDX_ENTRY_VCN_SZ = struct.calcsize(INDX_ENTRY_VCN_FORMAT)

INDX_REC_HDR_FORMAT = '<4sHHQQ'
INDX_REC_HDR_FIELDS = [
    'signature',
    'fixup_offset',
    'fixup_entries',
    'lsn',
    'vcn'
]
INDX_REC_HDR_SZ = struct.calcsize(INDX_REC_HDR_FORMAT)


# Attribute Class list


class StandardInformation(object):

    def __init__(self, buf):
        fields = dict(zip(STANDARD_INFO_FIELDS, struct.unpack(STANDARD_INFO_FORMAT, buf)))
        for key in fields:
            setattr(self, key, fields[key])

    def __repr__(self):
        return 'StandardInformation'

    def __iter__(self):
        for key in dir(self):
            if not key.startswith('-'):
                yield key, getattr(self, key)


class AttributeList(object):

    def __init__(self, buf):
        raise NotImplementedError


class FileName(object):

    def __init__(self, buf):
        fields = dict(zip(FILENAME_FIELDS, struct.unpack(FILENAME_FORMAT, buf[:FILENAME_SZ])))
        for key in fields:
            setattr(self, key, fields[key])
        self.name = buf[FILENAME_SZ:].decode('utf16')

    def __repr__(self):
        return 'FileName'

    def __iter__(self):
        for key in dir(self):
            if not key.startswith('-'):
                yield key, getattr(self, key)


class ObjectId(object):

    def __init__(self, buf=None):
        # raise NotImplementedError
        pass


class SecurityDescriptor(object):

    def __init__(self, buf=None):
        raise NotImplementedError


class VolumeName(object):

    def __init__(self, buf=None):
        # raise NotImplementedError
        pass


class VolumeInformation(object):

    def __init__(self, buf=None):
        raise NotImplementedError


class Data(object):

    flag = False

    def __init__(self, buf=None):
        if isinstance(buf, dict):
            # non-resident
            self.flag = True
            for key in buf:
                setattr(self, key, buf[key])
        else:
            # resident
            self.data = buf

    def __repr__(self):
        return 'Data'

    def __iter__(self):
        if self.flag:
            for key in dir(self):
                if not key.startswith('-'):
                    yield key, getattr(self, key)
        else:
            # raise or output one by one
            raise NotImplementedError


class IndexRoot(object):

    FOLDER_TYPE = 0x30

    def __init__(self, buf):
        idx_root = buf
        # Index root header
        r_hdr = dict(zip(INDX_R_HDR_FIELDS, struct.unpack(INDX_R_HDR_FORMAT, idx_root[:INDX_R_HDR_SZ])))
        for r_key in r_hdr:
            setattr(self, r_key, r_hdr[r_key])

        # Index node header
        idx_node = idx_root[INDX_R_HDR_SZ:]
        n_hdr = dict(zip(INDX_N_HDR_FIELDS, struct.unpack(INDX_N_HDR_FORMAT, idx_node[:INDX_N_HDR_SZ])))
        for n_key in n_hdr:
            setattr(self, n_key, n_hdr[n_key])

        # Index entry list
        self.index_entry = list()
        if n_hdr['flags'] == 1:
            idx_entry_buf = idx_node[n_hdr['start_offset']:n_hdr['alloc_size']]

            while len(idx_entry_buf) > 0:
                e_hdr = dict(zip(INDX_ENTRY_FIELDS, struct.unpack(INDX_ENTRY_FORMAT, idx_entry_buf[:INDX_ENTRY_SZ])))
                idx_entry = idx_entry_buf[:e_hdr['entry_size']]
                idx_entry = idx_entry[INDX_ENTRY_SZ:]


                if e_hdr['content_size'] > 0:  # file name exists
                    filename_buf = idx_entry[:e_hdr['content_size']]
                    idx_entry = idx_entry[e_hdr['content_size']:]
                    filename = FileName(filename_buf).name
                    e_hdr['filename'] = filename

                if e_hdr['flags'] & 0x1 == 0x1:  # child node exists
                    padding_size = len(idx_entry) - INDX_ENTRY_VCN_SZ
                    idx_entry_vcn = idx_entry[padding_size:padding_size + INDX_ENTRY_VCN_SZ]
                    e_hdr['vcn'] = struct.unpack(INDX_ENTRY_VCN_FORMAT, idx_entry_vcn)[0]

                self.index_entry.append(e_hdr)

                idx_entry_buf = idx_entry_buf[e_hdr['entry_size']:]

                # end of node
                if e_hdr['flags'] & 0x2 == 0x2:
                    break

    def __repr__(self):
        return 'IndexRoot'

    def __iter__(self):
        for key in dir(self):
            if not key.startswith('-'):
                yield key, getattr(self, key)

    def check_node_child(self):
        return getattr(self, 'flags') == 1


class IndexAllocation(object):

    flag = False
    INDX_SIGNATURE = b'INDX'

    def __init__(self, buf):

        if isinstance(buf, dict):
            # non-resident
            self.flag = True
            for key in buf:
                setattr(self, key, buf[key])
        else:
            # When followed the runlist
            idx_record = buf

            # Index record header
            r_hdr = dict(zip(INDX_REC_HDR_FIELDS, struct.unpack(INDX_REC_HDR_FORMAT, idx_record[:INDX_REC_HDR_SZ])))
            for r_key in r_hdr:
                setattr(self, r_key, r_hdr[r_key])

            if r_hdr['signature'] != self.INDX_SIGNATURE:
                print(r_hdr['signature'])
                print("check")
                # raise Invalid~
                pass

            # Index node header
            idx_node = idx_record[INDX_REC_HDR_SZ:]
            n_hdr = dict(zip(INDX_N_HDR_FIELDS, struct.unpack(INDX_N_HDR_FORMAT, idx_node[:INDX_N_HDR_SZ])))
            for n_key in n_hdr:
                setattr(self, n_key, n_hdr[n_key])

            # Index entry list
            self.index_entry = list()
            idx_entry_buf = idx_node[n_hdr['start_offset']:n_hdr['alloc_size']]

            while len(idx_entry_buf) > 0:
                e_hdr = dict(zip(INDX_ENTRY_FIELDS, struct.unpack(INDX_ENTRY_FORMAT, idx_entry_buf[:INDX_ENTRY_SZ])))
                idx_entry = idx_entry_buf[:e_hdr['entry_size']]
                idx_entry = idx_entry[INDX_ENTRY_SZ:]

                if e_hdr['content_size'] > 0:  # file name exists
                    filename_buf = idx_entry[:e_hdr['content_size']]
                    idx_entry = idx_entry[e_hdr['content_size']:]
                    filename = FileName(filename_buf).name
                    e_hdr['filename'] = filename

                if e_hdr['flags'] & 0x1 == 0x1:  # child node exists
                    padding_size = len(idx_entry) - INDX_ENTRY_VCN_SZ
                    idx_entry_vcn = idx_entry[padding_size:padding_size + INDX_ENTRY_VCN_SZ]
                    e_hdr['vcn'] = struct.unpack(INDX_ENTRY_VCN_FORMAT, idx_entry_vcn)[0]

                self.index_entry.append(e_hdr)

                idx_entry_buf = idx_entry_buf[e_hdr['entry_size']:]

                # end of node
                if e_hdr['flags'] & 0x2 == 0x2:
                    break

    def __repr__(self):
        return 'IndexAllocation'

    def __iter__(self):
        if self.flag:
            for key in dir(self):
                if not key.startswith('-'):
                    yield key, getattr(self, key)
        else:
            for key in dir(self):
                if not key.startswith('-'):
                    yield key, getattr(self, key)
            # raise NotImplementedError


class Bitmap(object):

    def __init__(self, buf=None):
        pass

    def __repr__(self):
        return 'Bitmap'


class SymbolicLink(object):

    def __init__(self, buf=None):
        raise NotImplementedError


class EAInformation(object):

    def __init__(self, buf=None):
        raise NotImplementedError


class EA(object):

    def __init__(self, buf=None):
        raise NotImplementedError


class LoggedUtilityStream(object):

    def __init__(self, buf=None):
        # raise NotImplementedError
        pass


# Attribute dispatch table


attribute_table = {
    0x10: StandardInformation,
    0x20: AttributeList,
    0x30: FileName,
    0x40: ObjectId,
    0x50: SecurityDescriptor,
    0x60: VolumeName,
    0x70: VolumeInformation,
    0x80: Data,
    0x90: IndexRoot,
    0xA0: IndexAllocation,
    0xB0: Bitmap,
    0xC0: SymbolicLink,
    # 0xC0: RepasePoint,
    0xD0: EAInformation,
    0xE0: EA,
    0x100: LoggedUtilityStream
}
