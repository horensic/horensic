import os
import _io
from .defines import *


class NTFS(object):

    NTFS_SIGNATURE = b"NTFS    "  # \x4E\x54\x46\x53\x20\x20\x20\x20
    MFT_ENTRY_SZ = 1024

    def __init__(self, volume=None):

        self.volume = None
        self.volume_path = str()

        self.vbr = dict()
        self.cluster = int()
        self.mft = dict()

        if not volume:
            self.volume_path = "\\\\.\\" + os.getenv("SystemDrive")
        else:
            self.volume_path = "\\\\.\\" + volume.split('\\')[0]

        self.read_vbr()

    def __repr__(self):
        return 'NTFS'

    def __del__(self):
        self.volume.close()

    def read_vbr(self):

        try:
            self.volume = open(self.volume_path, 'rb')
        except PermissionError as err_msg:
            print("Requires administrator privileges")
            print(err_msg)
            exit(-1)
        else:
            self.volume.seek(0)
            vbr = self.volume.read(VBR_SZ)
            self.vbr = dict(zip(VBR_FIELDS, struct.unpack(VBR_FORMAT, vbr)))

            if not self.check_vbr():
                # raise InvalidNTFS~~Exception
                pass

    def read_mft(self, address=None):

        self.cluster = self.vbr['bps'] * self.vbr['spc']  # 4096
        if not address:
            mft_address = self.vbr['mft'] * self.cluster
        else:
            mft_address = address
        self.volume.seek(mft_address)
        mft = bytearray(self.volume.read(self.MFT_ENTRY_SZ))

        return MFT(self.volume, mft)

    def get_mft_list(self, mft0):

        mft = mft0
        mft.data_run()
        mft_sz = mft.header['alloc_size']
        ofs = 0
        for length, offset in mft.data_c_run:
            ofs += offset
            for i in range(int((length * self.cluster) / mft_sz)):
                yield (ofs * self.cluster) + (mft_sz * i)

    def get_root(self):

        mft = self.read_mft()
        root = None
        mft_sz = mft.header['alloc_size']
        root_name = str(b'.\x00', 'UTF16')
        rn = 5  # record number
        for mft_ofs in self.get_mft_list(mft):

            if rn != 0:
                rn -= 1
                continue
            self.volume.seek(mft_ofs)
            mft_entry = MFT(self.volume, bytearray(self.volume.read(mft_sz)))

            if mft_entry.attributes['FileName'].name == root_name:
                root = mft_entry
                break

        return root

    def get_index_list(self, mft):

        root = mft
        root.index_run()
        record_sz = root.attributes['IndexRoot'].index_record_size
        ofs = 0

        for length, offset in root.index_c_run:
            ofs += offset
            for i in range(int((length * self.cluster) / record_sz)):
                # yield (offset * self.cluster) + (record_sz * i)
                record_ofs = (ofs * self.cluster) + (record_sz * i)
                self.volume.seek(record_ofs)
                rec_buf = self.volume.read(record_sz)
                record = IndexAllocation(rec_buf)
                yield record

    def check_vbr(self):
        return self.vbr['oem_id'] == self.NTFS_SIGNATURE


class MFT(object):

    MFT_SIGNATURE = b"FILE"

    def __init__(self, volume, mft):

        if not isinstance(volume, _io.BufferedReader):
            # raise InvalidNTFS~~Exception
            pass

        self.volume = volume
        self.mft = mft
        self.header = dict(zip(MFT_RECORD_HDR_FIELDS, struct.unpack(MFT_RECORD_HDR_FORMAT, self.mft[:MFT_RECORD_HDR_SZ])))

        if self.header['alloc_size'] != 1024:
            # raise InvalidNTFS~~Exception
            pass

        if not self.check_mft_entry():
            # raise InvalidNTFS~~Exception
            pass

        if self.header['real_size'] >= 0x200:
            self.fixup()

        self.attributes = dict()
        self.attributes_size = self.header['real_size'] - self.header['offset']
        self.read_attribute(self.header['offset'])

        self.data_c_run = list()
        self.index_c_run = list()

    def __repr__(self):
        return 'MFT Entry'

    def fixup(self):
        fixup = self.header['fixup_offset']
        fixup_entries = self.header['fixup_entries']
        for i in range(1, fixup_entries):
            self.mft[0x200*i-2] = self.mft[fixup+i*2]
            self.mft[0x200*i-1] = self.mft[fixup+i*2+1]

    def read_attribute(self, offset):

        # Common Header
        c_hdr_end = offset + ATTR_COMMON_HDR_SZ
        if self.attributes_size <= c_hdr_end:
            return
        c_hdr = self.mft[offset:c_hdr_end]
        common_hdr = dict(zip(ATTR_COMMON_HDR_FIELDS, struct.unpack(ATTR_COMMON_HDR_FORMAT, c_hdr)))
        next_hdr = offset + common_hdr['length']

        # Resident/Non-Resident Header
        if common_hdr['non_resident'] == b'\x01':
            # non-resident attribute
            nr_hdr_end = c_hdr_end + NON_RESIDENT_ATTR_HDR_SZ
            nr_hdr = self.mft[c_hdr_end:nr_hdr_end]
            non_resident_hdr = dict(zip(NON_RESIDENT_ATTR_HDR_FIELDS,
                                        struct.unpack(NON_RESIDENT_ATTR_HDR_FORMAT, nr_hdr)))

            if offset + non_resident_hdr['offset'] > nr_hdr_end:  # Attribute name exists
                nr_name_sz = (offset + non_resident_hdr['offset']) - nr_hdr_end
                non_resident_hdr['name'] = str(self.mft[nr_hdr_end:nr_hdr_end + nr_name_sz], encoding='UTF16')
                nr_hdr_end = offset + non_resident_hdr['offset']
                nr_data_end = nr_hdr_end + nr_name_sz
            else:
                nr_data_sz = common_hdr['length'] - (ATTR_COMMON_HDR_SZ + NON_RESIDENT_ATTR_HDR_SZ)
                nr_data_end = nr_hdr_end + nr_data_sz

            non_resident_hdr['data'] = self.mft[nr_hdr_end:nr_data_end]

            attribute = attribute_table[common_hdr['type']](non_resident_hdr)
            self.attributes[repr(attribute)] = attribute
        else:
            # resident attribute
            r_hdr_end = c_hdr_end + RESIDENT_ATTR_HDR_SZ
            r_hdr = self.mft[c_hdr_end:r_hdr_end]
            resident_hdr = dict(zip(RESIDENT_ATTR_HDR_FIELDS, struct.unpack(RESIDENT_ATTR_HDR_FORMAT, r_hdr)))

            # Attribute Header
            a_buf_start = offset + resident_hdr['offset']  # Offset of attribute header includes common header and attribute header
            a_buf_end = a_buf_start + resident_hdr['size']
            attribute = attribute_table[common_hdr['type']](self.mft[a_buf_start:a_buf_end])
            self.attributes[repr(attribute)] = attribute

        self.read_attribute(next_hdr)

    def data_run(self):

        if self.attributes['Data'].flag:

            cluster_run = bytearray(self.attributes['Data'].data)

            start = 0
            while True:
                end = start + 1
                if cluster_run[start:end] == b'\x00':
                    break
                head = cluster_run[start:end].hex()
                offset = int(head[0])
                length = int(head[1])
                # c is cluster
                c_len_end = end+length
                c_ofs_end = c_len_end+offset
                c_len = cluster_run[end:c_len_end]
                c_ofs = cluster_run[c_len_end:c_ofs_end]
                c_len.reverse(), c_ofs.reverse()

                if c_ofs[0] >> 7 == 1:
                    c_ofs = 0 - ((int(c_ofs.hex(), 16)^((1 << (offset*8)) -1)) +1)
                    run = [int(c_len.hex(), 16), c_ofs]
                else:
                    run = [int(c_len.hex(), 16), int(c_ofs.hex(), 16)]
                self.data_c_run.append(run)
                start = c_ofs_end
        else:
            # raise
            return

    def index_run(self):
        if self.attributes['IndexAllocation'].flag:

            cluster_run = bytearray(self.attributes['IndexAllocation'].data)

            start = 0
            while True:
                end = start + 1
                if cluster_run[start:end] == b'\x00':
                    break
                head = cluster_run[start:end].hex()
                offset = int(head[0])
                length = int(head[1])
                # c is cluster
                c_len_end = end + length
                c_ofs_end = c_len_end + offset
                c_len = cluster_run[end:c_len_end]
                c_ofs = cluster_run[c_len_end:c_ofs_end]
                c_len.reverse(), c_ofs.reverse()

                if c_ofs[0] >> 7 == 1:
                    c_ofs = 0 - ((int(c_ofs.hex(), 16)^((1 << (offset*8)) -1)) +1)
                    run = [int(c_len.hex(), 16), c_ofs]
                else:
                    run = [int(c_len.hex(), 16), int(c_ofs.hex(), 16)]
                self.index_c_run.append(run)
                start = c_ofs_end
        else:
            # raise
            return

    def get_index(self):
        pass

    def check_mft_entry(self):
        return self.header['signature'] == self.MFT_SIGNATURE
