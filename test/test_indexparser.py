import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath('../horensic/filesystem')))
sys.path.insert(0, os.path.dirname(os.path.abspath('../utils')))
from horensic.filesystem.ntfs import *

def file_ref(addr):
    ref = bytearray(struct.pack('<Q', addr))
    return struct.unpack('<Q', ref[:6] + b'\x00\x00')[0]

def search_idx_a(ntfs, mft, vcn, name):
    """

    :param ntfs:
    :param mft:
    :param vcn:
    :param name:
    :return: MFT number
    """
    if 'IndexAllocation' in mft.attributes:
        records = list()

        for r in ntfs.get_index_list(mft):
            records.append(r)

        for record in records:
            if record.vcn != vcn:
                continue
            for entry in record.index_entry:
                if 'filename' in entry:
                    if entry['filename'].name == name:
                        return entry['file_ref_addr']
                    else:
                        continue
                else:
                    continue
        # raise ~~
        print("...File Name Not Matching")
        return -1
    else:
        return -1

def search_idx_r(ntfs, mft, name):
    """

    :param ntfs:
    :param mft:
    :param name:
    :return: MFT number
    """
    if 'IndexRoot' in mft.attributes:
        for entry in mft.attributes['IndexRoot'].index_entry:
            if 'filename' in entry:
                if entry['filename'].name == name:
                    return entry['file_ref_addr']
                elif entry['filename'].name > name:  # Go to index allocation and find the record that matches the vcn value
                    if (entry['flags'] & 0x1) != 0x1:
                        return -2
                    return search_idx_a(ntfs, mft, entry['vcn'], name)
            else:
                if (entry['flags'] & 0x2) == 0x2:
                    if (entry['flags'] & 0x1) == 0x1:
                        return search_idx_a(ntfs, mft, entry['vcn'], name)
                    else:
                        break
        return -1
    else:  # NOT directory's mft
        return -1


if __name__ == '__main__':
    # path split
    target_dir = 'Program Files (x86)'  # C:\Program Files (x86)\Microsoft.NET
    path_list = target_dir.split('\\')
    mft_list = list()
    # use drive path
    test = NTFS()
    mft0 = test.read_mft()
    root = test.get_root()
    for mft in test.get_mft_list(mft0):
        mft_list.append(mft)
    # use next path list
    dir_mft = root
    for dir_name in path_list:
        addr = search_idx_r(test, dir_mft, dir_name)
        if addr > 0:
            mft_idx = file_ref(addr)
            mft_addr = mft_list[mft_idx]
            dir_mft = test.read_mft(mft_addr)

    for r_r in dir_mft.attributes['IndexRoot'].index_entry:
        if 'filename' in r_r:
            print(r_r['filename'].name, r_r['filename'].created_time)

    if 'IndexAllocation' in dir_mft.attributes:
        for a_r in test.get_index_list(dir_mft):
            for r in a_r.index_entry:
                if 'filename' in r:
                    print(r['filename'].name, r['filename'].created_time)
