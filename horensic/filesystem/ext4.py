import os
from .defines import *


class EXT4(object):

    EXT_SIGNATURE = b'\xEF\x53'

    def __init__(self, volume=None):

        self.volume = None
        self.volume_path = volume

        try:
            self.volume = open(self.volume_path, 'rb')
        except:
            exit(-1)
        else:
            self.volume.seek(1024)  # skip reserved area
            self.super_block()
            self.group_descriptor_table()
            self.root_inode()
            self.root_dir()

    def __repr__(self):
        return 'EXT4'

    def __iter__(self):
        for key in dir(self):
            if not key.startswith('_'):
                yield key, getattr(self, key)

    def __del__(self):
        self.volume.close()

    def super_block(self):
        # sb_data = self.volume.read(SB_SZ)
        # self.sb = dict(zip(SB_FILED, struct.unpack(SB_FORMAT, sb_data)))
        sb = self.volume.read(1024)

        self.total_inode = struct.unpack_from('<I', sb, 0x0)[0]
        self.total_block = struct.unpack_from('<I', sb, 0x4)[0]
        self.block_size = pow(2, 10 + struct.unpack_from('<I', sb, 0x18)[0])
        self.blocks_per_group = struct.unpack_from('<I', sb, 0x20)[0]
        self.inodes_per_group = struct.unpack_from('<I', sb, 0x28)[0]
        self.signature = struct.unpack_from('<H', sb, 0x38)[0]
        self.inode_size = struct.unpack_from('<I', sb, 0x58)[0]
        self.gdt_size = struct.unpack_from('<H', sb, 0xFE)[0]
        if self.gdt_size == 0:
            self.gdt_size = 32

    def group_descriptor_table(self):
        # gdt_data = self.volume.read()
        # self.gdt = dict(zip(GDT_FILED, struct.unpack(GDT_FORMAT, gdt_data))
        gdt = self.volume.read(self.gdt_size)

        self.start_block_bitmap = struct.unpack_from('<I', gdt, 0x0)[0]
        self.start_inode_bitmap = struct.unpack_from('<I', gdt, 0x4)[0]
        self.start_inode_table = struct.unpack_from('<I', gdt, 0x8)[0]

    def inode_table(self):
        inode_table_offset = self.start_inode_table * self.block_size
        self.volume.seek(inode_table_offset)

    def root_inode(self):
        inode_table_offset = self.start_inode_table * self.block_size
        self.volume.seek(inode_table_offset + self.inode_size)
        root_ino = self.volume.read(self.inode_size)
        root_hi = struct.unpack_from('<H', root_ino, 0x3A)[0]
        root_lo = struct.unpack_from('<I', root_ino, 0x3C)[0]
        self.start_root = struct.unpack('>Q', b'\x00\x00' + struct.pack('>HI', root_hi, root_lo))[0]

    def root_dir(self):
        dir_list = []

        root_dir_offset = self.start_root * self.block_size
        self.volume.seek(root_dir_offset)
        ino = self.volume.read(EXT_DIR_ENTRY_SZ)
        entry = dict(zip(EXT_DIR_ENTRY_FILED, struct.unpack(EXT_DIR_ENTRY_FORMAT, ino)))

        while entry['inode'] > 0:
            name_buf = self.volume.read(entry['rec_len'] - EXT_DIR_ENTRY_SZ)
            entry['name'] = struct.unpack(str(entry['name_len']) + 's', name_buf[:entry['name_len']])[0].decode('utf8')
            dir_list.append(entry)
            ino = self.volume.read(EXT_DIR_ENTRY_SZ)
            entry = dict(zip(EXT_DIR_ENTRY_FILED, struct.unpack(EXT_DIR_ENTRY_FORMAT, ino)))

        for dl in dir_list:
            print(dl)

    def inode(self):
        pass

