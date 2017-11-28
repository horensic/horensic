import os
import _io
from .defines import *


class NTFS(object):

    NTFS_SIGNATURE = b"NTFS    "  # \x4E\x54\x46\x53\x20\x20\x20\x20

    def __init__(self, volume=None):

        self.volume = None
        self.volume_path = str()

        self.vbr = dict()
        self.cluster = int()
        self.mft = dict()

        if not volume:
            self.volume_path = "\\\\.\\" + os.getenv("SystemDrive")
        else:
            self.volume_path = "\\\\.\\" + volume.split('\\')[-1]

        self.read_vbr()

    def __repr__(self):
        return 'NTFS'

    def read_vbr(self):

        self.volume = open(self.volume_path, 'rb')
        self.volume.seek(0)
        vbr = self.volume.read(VBR_SZ)
        self.vbr = dict(zip(VBR_FIELDS, struct.unpack(VBR_FORMAT, vbr)))

        if not self.check_vbr():
            # raise InvalidNTFS~~Exception
            pass

    def read_mft(self):

        self.cluster = self.vbr['bps'] * self.vbr['spc']  # 4096
        mft_address = self.vbr['mft'] * self.cluster
        self.volume.seek(mft_address)
        mft = self.volume.read(self.vbr['clusters_per_mft_record'])

        return MFT(self.volume, mft)

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
        self.header = dict(zip(MFT_RECORD_HDR_FIELDS, struct.unpack(MFT_RECORD_HDR_FORMAT, self.mft[:48])))

        self.attributes = dict()
        self.attributes_size = self.header['real_size'] - self.header['offset']
        self.read_attribute(self.header['offset'])

        if not self.check_mft_entry():
            # raise InvalidNTFS~~Exception
            pass

    def __repr__(self):
        return 'MFT Entry'

    def fixup(self):
        pass

    def read_attribute(self, offset):
        c_hdr_end = offset + ATTR_COMMON_HDR_SZ
        if self.attributes_size == c_hdr_end:
            return
        c_hdr = self.mft[offset:c_hdr_end]
        common_hdr = dict(zip(ATTR_COMMON_HDR_FIELDS, struct.unpack(ATTR_COMMON_HDR_FORMAT, c_hdr)))

        # data run is processed externally
        if common_hdr['non_resident'] == b'\x01':  # non-resident
            nr_hdr_end = c_hdr_end + NON_RESIDENT_ATTR_HDR_SZ
            nr_hdr = self.mft[c_hdr_end:nr_hdr_end]
            non_resident_hdr = dict(zip(NON_RESIDENT_ATTR_HDR_FIELDS,
                                        struct.unpack(NON_RESIDENT_ATTR_HDR_FORMAT, nr_hdr)))
            # temp
            attribute = attribute_table[0x80]("Temp")
        else:  # resident
            r_hdr_end = c_hdr_end + RESIDENT_ATTR_HDR_SZ
            r_hdr = self.mft[c_hdr_end:r_hdr_end]
            resident_hdr = dict(zip(RESIDENT_ATTR_HDR_FIELDS, struct.unpack(RESIDENT_ATTR_HDR_FORMAT, r_hdr)))

            a_buf_start = r_hdr_end + resident_hdr['offset']
            a_buf_end = a_buf_start + resident_hdr['size']

            attribute = attribute_table[common_hdr['type']](self.mft[a_buf_start:a_buf_end])
            print(attribute)

        self.attributes[repr(attribute)] = attribute

    def logfile(self):
        pass

    def root(self):
        return INDX()

    def check_mft_entry(self):
        return self.header['signature'] == self.MFT_SIGNATURE


class INDX(object):

    INDX_SIGNATURE = b'INDX'

    def __init__(self):
        pass



