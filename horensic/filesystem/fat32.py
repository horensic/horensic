import os, sys
from .defines import *
sys.path.insert(0, os.path.dirname(os.path.abspath('../utils')))
from utils.timestamp import fat32time


class FAT32(object):

    OEM_ID = [b'MSWIN4.0', b'MSWIN4.1', b'MSDOS5.0', b'mkdosfs']

    def __init__(self, volume=None, image=None):

        self.volume = None
        self.volume_path = str()
        self.cluster = int()

        self.fat1 = []
        self.fat2 = []

        self.root_offset = int()
        self.root_dir = []
        self.data_area_offset = int()

        if not volume:
            self.volume_path = "\\\\.\\" + os.getenv("SystemDrive")
        else:
            self.volume_path = "\\\\.\\" + volume.split('\\')[0]

        try:
            self.volume = open(self.volume_path, 'rb')
        except PermissionError:
            print("Requires administrator privileges")
            exit(-1)
        else:
            self.reserved_area()
            self.fsinfo()
            self.fat()

    def __repr__(self):
        return 'FAT32'

    def __del__(self):
        self.volume.close()

    def reserved_area(self):
        self.volume.seek(0)
        fat32_bpb = self.volume.read(FAT32_BPB_SZ)
        self.fat32 = dict(zip(FAT32_BPB_FILED, struct.unpack(FAT32_BPB_FORMAT, fat32_bpb)))

        for key in self.fat32:
            setattr(self, key, self.fat32[key])

        self.cluster = self.fat32['bps'] * self.fat32['spc']

    def fsinfo(self):
        fsinfo_offset = self.fat32['fsinfo_s'] * self.fat32['bps']
        self.volume.seek(fsinfo_offset)

        fat32_fsinfo = self.volume.read(FSINFO_SZ)
        fsinfo = dict(zip(FSINFO_FILED, struct.unpack(FSINFO_FORMAT, fat32_fsinfo)))

        # check signature

        setattr(self, 'num_of_free_cluster', fsinfo['num_of_free_cluster'])
        setattr(self, 'next_free_cluster', fsinfo['next_free_cluster'])

    def fat(self):
        self.fat1_offset = self.fat32['reserved_sc'] * self.fat32['bps']

        self.volume.seek(self.fat1_offset)
        self.fat_sz = self.fat32['fat_size32'] * self.fat32['bps']
        fat1 = self.volume.read(self.fat_sz)

        for i in range(0, len(fat1), 4):
            self.fat1.append(struct.unpack('<I', fat1[i:i+4])[0])

    def get_root(self):
        root_run = []
        self.data_area_offset = self.fat1_offset + (self.fat_sz * self.fat32['num_fats'])
        self.root_offset = self.data_area_offset + (self.fat32['root_dir_cluster'] - 2) * self.cluster
        self.read_fat(root_run, self.fat32['root_dir_cluster'])

        self.volume.seek(self.root_offset)
        root = self.volume.read(len(root_run) * self.cluster)
        self.root_dir = DirectoryEntry(root).dir_list

    def next_dir(self, parent, name):

        child_entry = None

        for entry in parent:
            if name in entry['name']:
                child_entry = entry
                break

        dir_run = []
        dir_offset = self.data_area_offset + (child_entry['start_cluster'] - 2) * self.cluster
        self.read_fat(dir_run, child_entry['start_cluster'])

        self.volume.seek(dir_offset)
        child = self.volume.read(len(dir_run) * self.cluster)
        child_dir = DirectoryEntry(child).dir_list

        return child_dir

    def read_fat(self, c_run, cluster):
        next_cluster = self.fat1[cluster]
        if next_cluster == 0x0FFFFFFF:
            c_run.append(cluster)
            return
        else:
            c_run.append(cluster)
            self.read_fat(c_run, next_cluster)
        return


class DirectoryEntry(object):

    def __init__(self, buf):

        self.dir_list = []
        lfn_stack = []
        lfn_count = 0

        for i in range(0, len(buf), DIR_ENTRY_SZ):
            entry = buf[i:i + DIR_ENTRY_SZ]
            dir_entry = dict(zip(DIR_ENTRY_FILED, struct.unpack(DIR_ENTRY_FORMAT, entry)))

            if dir_entry['name'][0] == 0x00:  # end of directory entry
                break
            elif dir_entry['name'][0] == 0xE5:  # deleted file(directory)
                continue

            if dir_entry['attribute'] == 0x0F:  # Long File Name
                if dir_entry['name'][0] & 0x40 == 0x40:
                    lfn_count = dir_entry['name'][0] ^ 0x40
                lfn_stack.append(entry)
                lfn_count -= 1
                continue
            elif len(lfn_stack) > 0 and lfn_count == 0:
                lfn_stack.append(entry)
                dir_entry = self.long_file_name(lfn_stack)
                lfn_stack = []
            else:
                dir_entry['name'] = dir_entry['name'].decode('utf8')

            self.timestamp(dir_entry)
            self.start_cluster(dir_entry)
            self.dir_list.append(dir_entry)

    @staticmethod
    def long_file_name(lfn_stack):

        meta_entry = None
        name = str()
        for i in range(len(lfn_stack)):
            entry = lfn_stack.pop()
            dir_entry = dict(zip(DIR_ENTRY_FILED, struct.unpack(DIR_ENTRY_FORMAT, entry)))

            if dir_entry['attribute'] == 0x0F:
                lfn_entry = dict(zip(LFN_ENTRY_FILED, struct.unpack(LFN_ENTRY_FORMAT, entry)))
                lfn = lfn_entry['name1'] + lfn_entry['name2'] + lfn_entry['name3']
                lfn = lfn.decode('utf16')
                end_of_name = lfn.find(b'\xFF\xFF'.decode('utf16'))

                if end_of_name > 0:
                    lfn = lfn[:end_of_name]
                name += lfn
            else:
                meta_entry = dir_entry

        meta_entry['name'] = name
        return meta_entry

    @staticmethod
    def timestamp(entry):
        created = struct.pack('HHB', entry['cdate'], entry['ctime'], entry['ctimet'])
        entry['created_time'] = fat32time(created)

        modified = struct.pack('HH', entry['mdate'], entry['mtime'])
        entry['modified_time'] = fat32time(modified)

        accessed = struct.pack('H', entry['adate'])
        entry['accessed_time'] = fat32time(accessed)

    @staticmethod
    def start_cluster(entry):
        cluster = struct.pack('>HH', entry['start_cluster_hi'], entry['start_cluster_lo'])
        entry['start_cluster'] = struct.unpack('>I', cluster)[0]
