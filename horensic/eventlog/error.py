class InvalidEvtxException(Exception):

    def __init__(self, offset=None):
        super(InvalidEvtxException, self).__init__('Invalid EVTX File Exception')


class InvalidChunkException(Exception):

    def __init__(self, offset=None):
        super(InvalidChunkException, self).__init__('Invalid Chunk Exception')


class InvalidRecordException(Exception):

    def __init__(self):
        super(InvalidRecordException, self).__init__('Invalid Record Exception')


class InvalidBinXMLException(Exception):

    def __init__(self):
        super(InvalidBinXMLException, self).__init__('Invalid BinXML Exception')


def set_verbose(flag):
    global verbose
    verbose = flag


def VerboseMessage(*args):
    if verbose is True:
        print("{0:<30}: {1}".format(args[0], args[1]))
