# referenced Python forensics

import os, sys
import time
import hashlib
import argparse
sys.path.insert(0, os.path.dirname(os.path.abspath('../utils')))
from utils.output import CSVWriter


def parse_command_line():

    global args
    global hashtype

    parser = argparse.ArgumentParser('Python file system hashing')
    parser.add_argument('-v', '--verbose', help='allows progress messages to be displayed', action='store_true')

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--md5', help='specifies MD5 algorithm', action='store_true')
    group.add_argument('--sha1', help='specifies SHA1 algorithm', action='store_true')
    group.add_argument('--sha256', help='specifies SHA256 algorithm', action='store_true')
    group.add_argument('--sha512', help='specifies SHA512 algorithm', action='store_true')

    parser.add_argument('-d', '--dir', type=ValidateDirectory, required=True, help='specify the directory for hashing')
    parser.add_argument('-o', '--output', type=ValidateDirectoryWritable, required=True, help='specify the directory '
                                                                                              'for reports will be written')
    args = parser.parse_args()

    if args.md5:
        hashtype = 'MD5'
    elif args.sha1:
        hashtype = 'SHA1'
    elif args.sha256:
        hashtype = 'SHA256'
    elif args.sha512:
        hashtype = 'SHA512'
    else:
        raise argparse.ArgumentTypeError("Invalid hash type")

    VerboseMessage("Command line processed: Successfully")

    return


def walk_path():

    success = 0
    error = 0
    report = CSVWriter('report.csv', args.output)
    header = ('File', 'Path', 'Size', 'Modified Time', 'Access Time', 'Create Time', hashtype, 'Owner', 'Group', 'Mode')
    report.set_row(header)

    for root, dirs, files in os.walk(args.dir):
        for file in files:
            fpath = os.path.join(root, file)
            result = hash_file(fpath, file, report)

            if result is True:
                success += 1
            else:
                error += 1

        del report
        return success


def hash_file(fpath, name, report):

    if os.path.exists(fpath):
        if not os.path.islink(fpath):
            if os.path.isfile(fpath):
                try:
                    f = open(fpath, 'rb')
                except IOError:
                    # log
                    return
                else:
                    try:
                        rd = f.read()
                    except IOError:
                        f.close()
                        # log
                        return
                    else:
                        (mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime) = os.stat(fpath)

                        VerboseMessage("Processing File: " + fpath)

                        fsize = str(size)
                        modtime = time.ctime(mtime)
                        acstime = time.ctime(atime)
                        crtime = time.ctime(ctime)

                        ownerid = str(uid)
                        groupid = str(gid)
                        fmode = bin(mode)

                        hash_value = None

                        if args.md5:
                            h = hashlib.md5()
                            h.update(rd)
                            md5 = h.hexdigest()
                            hash_value = md5.upper()
                        elif args.sha1:
                            h = hashlib.sha1()
                            h.update(rd)
                            sha1 = h.hexdigest()
                            hash_value = sha1.upper()
                        elif args.sha256:
                            h = hashlib.sha256()
                            h.update(rd)
                            sha256 = h.hexdigest()
                            hash_value = sha256.upper()
                        elif args.sha512:
                            h = hashlib.sha512()
                            h.update(rd)
                            sha512 = h.hexdigest()
                            hash_value = sha512.upper()

                        f.close()

                        report.write_row(name, fpath, fsize, modtime, acstime, crtime,
                                         hash_value, ownerid, groupid, fmode)
                        return True
            else:
                # log
                return False
        else:
            # log
            return False
    else:
        # log
        pass

    return False


def ValidateDirectory(path):

    if not os.path.isdir(path):
        raise argparse.ArgumentTypeError('Directory does not exist')

    if os.access(path, os.R_OK):
        return path
    else:
        raise argparse.ArgumentTypeError('Directory is not readable')


def ValidateDirectoryWritable(path):

    if not os.path.isdir(path):
        raise argparse.ArgumentTypeError('Directory does not exist')

    if os.access(path, os.W_OK):
        return path
    else:
        raise argparse.ArgumentTypeError('Directory is not writable')


def VerboseMessage(msg):
    if args.verbose:
        print(msg)
    return


if __name__=='__main__':

    parse_command_line()
    walk_path()