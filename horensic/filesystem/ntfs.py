import os
from .defines import *


class NTFS(object):

    NTFS_SIGNATURE = b"NTFS    "  # \x4E\x54\x46\x53\x20\x20\x20\x20
    MFT_SIGNATURE = b"FILE"

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
        self.mft = dict(zip(MFT_RECORD_HDR_FIELDS, struct.unpack(MFT_RECORD_HDR_FORMAT, mft[:48])))

        if not self.check_mft_entry():
            # raise InvalidNTFS~~Exception
            pass

    def check_vbr(self):
        return self.vbr['oem_id'] == self.NTFS_SIGNATURE

    def check_mft_entry(self):
        return self.mft['signature'] == self.MFT_SIGNATURE
