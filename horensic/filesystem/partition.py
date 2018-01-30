import os, sys
from .defines import *
sys.path.insert(0, os.path.dirname(os.path.abspath('../utils')))
from utils.error import *


class MBR(object):

    DISK_SIGNATURE = b'\x55\xAA'

    def __init__(self, image):
        self.disk_image = None
        self.partitions = []
        mbr = []

        if isinstance(image, str):
            self.image_path = image
            try:
                self.disk_image = open(self.image_path, 'rb')
            except IOError as e:
                print("Check Image file or file path", e)
                exit(-1)
            else:
                mbr = self.disk_image.read(512)
                self.disk_image.close()
        elif isinstance(image, bytes):
            mbr = image
        else:
            raise InvalidInputTypeError('bytes or str(path)', type(image))

        # boot_code = mbr[:445]
        partition = mbr[446:509]
        signature = mbr[510:511]
        self.partition_table(partition)
        self.check_signature(signature)

    def __repr__(self):
        return 'MBR'

    def partition_table(self, pt):

        for i in range(4):
            ofs = i*PT_ENTRY_SZ
            entry = dict(zip(PT_ENTRY_FILEDS, struct.unpack(PT_ENTRY_FORMAT, pt[ofs:ofs + PT_ENTRY_SZ])))
            self.partitions.append(entry)

    def check_signature(self, sig):
        return self.DISK_SIGNATURE == sig


class GPT(object):

    SECTOR = 512
    GPT_SIGNATURE = b'EFI PART'

    def __init__(self, image):
        self.disk_image = None
        self.gpt_entries = []
        self.image_path = image

        try:
            self.disk_image = open(self.image_path, 'rb')
        except:
            exit(-1)
        else:
            self.protective_mbr()
            self.get_entries()

    def __repr__(self):
        return 'GPT'

    def protective_mbr(self):
        p_mbr = self.disk_image.read(512)
        self.p_mbr = MBR(p_mbr)

    def get_entries(self):
        # GPT Header
        buf = self.disk_image.read(512)
        hdr = buf[:GPT_HDR_SZ]
        self.gpt_hdr = dict(zip(GPT_HDR_FILEDS, struct.unpack(GPT_HDR_FORMAT, hdr)))

        # GPT Entry
        self.disk_image.seek(self.SECTOR * self.gpt_hdr['start_lba_pt'])

        for i in range(self.gpt_hdr['num_of_pe']):
            entry = self.disk_image.read(self.gpt_hdr['size_of_entry'])
            gpt_e = dict(zip(GPT_ENTRY_FILEDS, struct.unpack(GPT_ENTRY_FORMAT, entry)))

            if gpt_e['type_guid'] == b'\x00' * 10:
                break

            gpt_e['name'] = gpt_e['name'].decode('utf8')
            self.gpt_entries.append(gpt_e)

    def check_signature(self, sig):
        return self.GPT_SIGNATURE == sig
