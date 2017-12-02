import os
import sys
import argparse
sys.path.insert(0, os.path.dirname(os.path.abspath('../utils')))
sys.path.insert(0, os.path.dirname(os.path.abspath('../horensic/filesystem')))
from utils.timestamp import *
from horensic.filesystem.ntfs import *


class InvalidFileNameException(Exception):

    def __init__(self):
        super(InvalidFileNameException, self).__init__("Invalid File Name Exception")


def parse_command_line():

    global args

    parser = argparse.ArgumentParser('NTFS Index Buffer Parser')
    parser.add_argument('-v', '--verbose', help='allows progress messages to be displayed', action='store_true')
    parser.add_argument('-d', '--dir', type=ValidateDirectory, required=True, help='Specify the directory to parse the index buffer')

    args = parser.parse_args()

    VerboseMessage("Command line processed: Successfully")

    return


def ValidateDirectory(path):

    if not os.path.isdir(path):
        raise argparse.ArgumentTypeError('Directory does not exist', path)
    else:
        return path


def VerboseMessage(msg):
    if args.verbose:
        print(msg)
    return


def file_ref(addr):
    ref = bytearray(struct.pack('<Q', addr))
    return struct.unpack('<Q', ref[:6] + b'\x00\x00')[0]


def search_idx_a(ntfs, mft, vcn, name):

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
        raise InvalidFileNameException
    else:
        return -1


def search_idx_r(ntfs, mft, name):

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

    parse_command_line()
    drive, paths = os.path.splitdrive(args.dir)
    paths = paths.split('\\')[1:]

    volume = NTFS(drive)
    mft = volume.read_mft()

    mft_list = []
    for mft_offset in volume.get_mft_list(mft):
        mft_list.append(mft_offset)

    root = volume.get_root()
    index_mft = root
    for path in paths:
        addr = search_idx_r(volume, index_mft, path)
        if addr > 0:
            idx = file_ref(addr)
            mft_address = mft_list[idx]
            index_mft = volume.read_mft(mft_address)

    print(index_mft.attributes['FileName'].name)

    for record in index_mft.attributes['IndexRoot'].index_entry:
        if 'filename' in record:
            print(record['filename'].name,
                  filetime(record['filename'].created_time),
                  filetime(record['filename'].modified_time))

    if 'IndexAllocation' in index_mft.attributes:
        for IndexAllocation in volume.get_index_list(index_mft):
            for record in IndexAllocation.index_entry:
                if 'filename' in record:
                    print(record['filename'].name,
                          filetime(record['filename'].created_time),
                          filetime(record['filename'].modified_time))