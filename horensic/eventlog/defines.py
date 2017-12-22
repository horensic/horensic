import struct
from .error import *


# EVTX File Header
EVTX_HDR_FORMAT = '<8sQQQIHHHH76xII'
EVTX_HDR_FIELDS = ['signature',
                   'first_chunk_number',
                   'last_chunk_number',
                   'next_record_identifier',
                   'header_size',
                   'minor_version',
                   'major_version',
                   'header_block_size',
                   'number_of_chunks',
                   'unknown',
                   'file_flags',
                   'checksum']
EVTX_HDR_SZ = struct.calcsize(EVTX_HDR_FORMAT)  # 128

# Chunk Header
EVTX_CHNK_HDR_FORMAT = '<8sQQQQIIII64x4xI'
EVTX_CHNK_HDR_FIELDS = ['signature',
                        'first_record_number',
                        'last_record_number',
                        'first_record_id',
                        'last_record_id',
                        'header_size',
                        'last_record_data_offset',
                        'free_space_offset',
                        'event_records_checksum',
                        'unknown1',
                        'unknown2',
                        'checksum']
EVTX_CHNK_HDR_SZ = struct.calcsize(EVTX_CHNK_HDR_FORMAT)  # 512

EVTX_CHNK_STRT_SZ = 256
EVTX_CHNK_TPL_SZ = 128

# Event record Header
RECORD_HDR_FORMAT = '<4sIQQ'
RECORD_HDR_FIELDS = ['signature',
                     'record_size',
                     'event_record_id',
                     'timestamp']
RECORD_HDR_SZ = struct.calcsize(RECORD_HDR_FORMAT)  # 24

# Level

EVENT_LEVELS = {
    0x00000000: "LogAlways",
    0x00000001: "Critical",
    0x00000002: "Error",
    0x00000003: "Warning",
    0x00000004: "Informational",
    0x00000005: "Verbose",
    0x00000006: "ReservedLevel6",
    0x00000007: "ReservedLevel7",
    0x00000008: "ReservedLevel8",
    0x00000009: "ReservedLevel9",
    0x0000000A: "ReservedLevel10",
    0x0000000B: "ReservedLevel11",
    0x0000000C: "ReservedLevel12",
    0x0000000D: "ReservedLevel13",
    0x0000000E: "ReservedLevel14",
    0x0000000F: "ReservedLevel15"
}

# Keywords

EVENT_KEYWORDS = {
    0x0000000000000000: "AnyKeyword",
    0x0000000000010000: "Shell",
    0x0000000000020000: "Properties",
    0x0000000000040000: "FileClassStoreAndIconCache",
    0x0000000000080000: "Controls",
    0x0000000000100000: "APICalls",
    0x0000000000200000: "InternetExplorer",
    0x0000000000400000: "ShutdownUX",
    0x0000000000800000: "CopyEngine",
    0x0000000001000000: "Tasks",
    0x0000000002000000: "WDI",
    0x0000000004000000: "StartupPref",
    0x0000000008000000: "StructuredQuery",
    0x0001000000000000: "Reserved",
    0x0002000000000000: "WDIContext",
    0x0004000000000000: "WDIDiag",
    0x0008000000000000: "SQM",
    0x0010000000000000: "AuditFailure",
    0x0020000000000000: "AuditSuccess",
    0x0040000000000000: "CorrelationHint",
    0x0080000000000000: "Classic",
    0x0100000000000000: "ReservedKeyword56",
    0x0200000000000000: "ReservedKeyword57",
    0x0400000000000000: "ReservedKeyword58",
    0x0800000000000000: "ReservedKeyword59",
    0x1000000000000000: "ReservedKeyword60",
    0x2000000000000000: "ReservedKeyword61",
    0x4000000000000000: "ReservedKeyword62",
    0x8000000000000000: "ReservedKeyword63"
}

# Fragment header
FRAGMENT_HDR_FORMAT = '<BBB'
FRAGMENT_HDR_FIELDS = ['major_version',
                       'minor_version',
                       'flags']
FRAGMENT_HDR_SZ = struct.calcsize(FRAGMENT_HDR_FORMAT)

# Name
NAME_FORMAT = '<IHH'
NAME_FIELDS = ['unknown',
               'hash',
               'length']
NAME_STRING_SZ = struct.calcsize(NAME_FORMAT)

# Element start
ELEMENT_START_FORMAT = '<HII'
ELEMENT_START_FIELDS = ['identifier',
                        'data_size',
                        'name_offset']
ELEMENT_START_SZ = struct.calcsize(ELEMENT_START_FORMAT)  # 6

# Template Instance
TEMPLATE_IST_FORMAT = '<BII'
TEMPLATE_IST_FIELDS = ['unknown',
                       'id',
                       'offset']
TEMPLATE_IST_SZ = struct.calcsize(TEMPLATE_IST_FORMAT)

# Template definition
TEMPLATE_DEF_FORMAT = '<I16sI'
TEMPLATE_DEF_FIELDS = ['unknown',
                       'guid',
                       'data_size']
TEMPLATE_DEF_SZ = struct.calcsize(TEMPLATE_DEF_FORMAT)

# Substitution Array
SUBSTITUTION_ARR_FORMAT = '<HBB'


class FragmentHeader(object):

    def __init__(self, buf):
        fragment_hdr = buf.read(FRAGMENT_HDR_SZ)
        fields = dict(zip(FRAGMENT_HDR_FIELDS, struct.unpack(FRAGMENT_HDR_FORMAT, fragment_hdr)))
        for key in fields:
            setattr(self, key, fields[key])


class TemplateInstance(object):

    def __init__(self, buf, table):
        self.ret = None
        self.table = table
        t_inst = buf.read(TEMPLATE_IST_SZ)
        self.template = dict(zip(TEMPLATE_IST_FIELDS, struct.unpack(TEMPLATE_IST_FORMAT, t_inst)))
        self.t_id = self.template['id']
        self.t_ofs = self.template['offset']

    def update(self, chunk_start, ret):
        self.ret = ret

        if self.t_ofs not in self.table.keys():
            self.table[self.t_ofs] = {self.t_id: self.ret}

        if self.t_id not in self.table[self.t_ofs].keys():

            real_offset = chunk_start + self.t_ofs

            if self.ret == real_offset:
                self.table[self.t_ofs].update({self.t_id: self.ret})
            else:
                raise InvalidBinXMLException

    def define(self):
        return self.ret == self.table[self.t_ofs][self.t_id]

    @property
    def def_offset(self):
        return self.table[self.t_ofs][self.t_id]


class TemplateDefinition(object):

    def __init__(self, offset, buf):
        buf.seek(offset)
        t_def = buf.read(TEMPLATE_DEF_SZ)
        fields = dict(zip(TEMPLATE_DEF_FIELDS, struct.unpack(TEMPLATE_DEF_FORMAT, t_def)))
        for key in fields:
            setattr(self, key, fields[key])

    @property
    def size(self):
        return getattr(self, 'data_size')


class NameString(object):

    def __init__(self, offset, buf):
        self.buf = buf
        self.buf.seek(offset)
        ns = self.buf.read(NAME_STRING_SZ)
        fields = dict(zip(NAME_FIELDS, struct.unpack(NAME_FORMAT, ns)))
        for key in fields:
            setattr(self, key, fields[key])

    @property
    def name(self):
        name = str()
        length = getattr(self, 'length')
        for i in range(length + 1):
            name_char = self.buf.read(2)
            name += name_char.decode('utf16')
        return name[:-1]
    
    
class ValueText(object):

    def __init__(self, buf):
        self.buf = buf
        self.value_type = ord(self.buf.read(1))
        if self.value_type == 0x01:
            self.data = UnicodeTextString(self.buf).uni_text
        else:
            print(self.buf.tell(), self.value_type)
            raise NotImplementedError


class UnicodeTextString(object):

    uni_text = str()

    def __init__(self, buf):

        self.buf = buf
        length = struct.unpack('<H', self.buf.read(2))[0]
        for i in range(length):
            uni_char = self.buf.read(2)
            self.uni_text += uni_char.decode('utf16')


class CharRef(object):

    def __init__(self):
        raise NotImplementedError


class CDATASection(object):

    def __init__(self):
        raise NotImplementedError


class EntityRef(object):

    def __init__(self):
        raise NotImplementedError


class PITarget(object):

    def __init__(self):
        raise NotImplementedError


class PIData(object):

    def __init__(self):
        raise NotImplementedError


class NormalSubstitution(object):

    def __init__(self, buf, sarray):
        self.buf = buf
        self.sid = struct.unpack('<H', self.buf.read(2))[0]
        self.value_type = ord(self.buf.read(1))
        try:
            self.data = sarray[self.sid]
        except IndexError:
            print("{0}".format("NormalSubstitution"))
            print("buf.tell: {0}".format(self.buf.tell()))
            print("sid: {0}, value_type: {1}".format(self.sid, self.value_type))
            print("sArray")
            print(sarray)
            print("=" * 30)
            exit(-1)


class OptionalSubstitution(object):

    def __init__(self, buf, sarray):
        self.buf = buf
        self.sid = struct.unpack('<H', self.buf.read(2))[0]
        self.value_type = ord(self.buf.read(1))
        try:
            self.data = sarray[self.sid]
        except IndexError:
            print("{0}".format("OptionalSubstitution"))
            print("buf.tell: {0}".format(self.buf.tell()))
            print("substId: {0}, value_type: {1}".format(self.sid, self.value_type))
            print("sArray")
            print(sarray)
            print("=" * 30)
            exit(-1)
