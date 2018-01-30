import os
import sys
import argparse
sys.path.insert(0, os.path.dirname(os.path.abspath('../utils')))
sys.path.insert(0, os.path.dirname(os.path.abspath('../horensic/binary')))
from horensic.binary.pe import *


def parse_command_line():

    global args

    parser = argparse.ArgumentParser('PE File Parser')
    parser.add_argument('-v', '--verbose', help='allows progress messages to be displayed', action='store_true')
    parser.add_argument('-f', '--pefile', type=ValidatePEFile, required=True, help='Specify the PE File to parse the PE Header')

    args = parser.parse_args()

    VerboseMessage("Command line processed: Successfully")

    return


def ValidatePEFile(path):

    if not os.path.isfile(os.path.abspath(path)):
        raise argparse.ArgumentTypeError('PE File does not exist', path)
    else:
        return path


def VerboseMessage(msg):
    if args.verbose:
        print(msg)
    return


if __name__ == '__main__':

    parse_command_line()
    pe_file = PE(args.pefile)
