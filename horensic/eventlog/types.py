import io
import os, sys
import struct
sys.path.insert(0, os.path.dirname(os.path.abspath('../utils')))
from utils.timestamp import *


TOKEN_LOOKUP_TABLE = {
    0x00: 'EOF',
    0x01: 'OpenStart',      # '<'name>
    0x41: 'OpenStart',      # + attribute
    0x02: 'CloseStart',     # <name'>'
    0x03: 'CloseEmpty',     # <name'/>'
    0x04: 'End',            # '</name>'

    0x05: 'ValueText',             # attribute = 'value'
    0x45: 'ValueText',
    0x06: 'Attribute',             # 'attribute' = value
    0x46: 'Attribute',             # more attribute
    0x07: 'CDATASection',
    0x47: 'CDATASection',
    0x08: 'CharRef',               #
    0x48: 'CharRef',               #
    0x09: 'EntityRef',
    0x49: 'EntityRef',
    0x0a: 'PITarget',              # PI: Processing Instruction
    0x0b: 'PIData',

    0x0c: 'TemplateInstance',
    0x0d: 'NormalSubstitution',
    0x0e: 'OptionalSubstitution',
    0x0f: 'FragmentHeader'
}

SID_LOOKUP_TABLE = {
    b'\x00\x00\x00\x00\x00\x00': 'NULL_SID',
    b'\x00\x00\x00\x00\x00\x01': 'WORLD_SID',
    b'\x00\x00\x00\x00\x00\x02': 'LOCAL_SID',
    b'\x00\x00\x00\x00\x00\x03': 'CREATOR_SID',
    b'\x00\x00\x00\x00\x00\x04': 'NON_UNIQUE',
    b'\x00\x00\x00\x00\x00\x05': 'SECURITY_NT',
    b'\x00\x00\x00\x00\x00\x0F': 'SECURITY_APP_PACKAGE',
    b'\x00\x00\x00\x00\x00\x10': 'SECURITY_MANDATORY_LABEL',
    b'\x00\x00\x00\x00\x00\x11': 'SECURITY_SCOPED_POLICY_ID',
    b'\x00\x00\x00\x00\x00\x12': 'SECURITY_AUTHENTICATION'
}


def null_type(v, s, flag):
    return "NULL"


def string_type(v, s, flag):
    uni_str = str()
    value = io.BytesIO(v)
    for i in range(len(v)):
        uni_char = value.read(2)
        uni_str += uni_char.decode('utf16')
    return uni_str


def ansi_type(v, s, flag):
    ansi_str = str()
    value = io.BytesIO(v)
    for i in range(len(v)):
        ansi_str += value.read(1)
    return ansi_str


def int8_type(v, s, flag):
    value = list()
    buf = io.BytesIO(v)
    for i in range(s):
        value.append(str(struct.unpack('b', buf.read(1))[0]))
    return ','.join(value)


def uint8_type(v, s, flag):
    value = list()
    buf = io.BytesIO(v)
    for i in range(s):
        value.append(str(struct.unpack('B', buf.read(1))[0]))
    return ','.join(value)


def int16_type(v, s, flag):
    value = list()
    buf = io.BytesIO(v)
    for i in range(s / 2):
        value.append(str(struct.unpack('<h', buf.read(2))[0]))
    return ','.join(value)


def uint16_type(v, s, flag):
    value = list()
    buf = io.BytesIO(v)
    for i in range(int(s / 2)):
        value.append(str(struct.unpack('<H', buf.read(2))[0]))
    return ','.join(value)


def int32_type(v, s, flag):
    value = struct.unpack('<i', v)[0]
    return str(value)


def uint32_type(v, s, flag):
    value = struct.unpack('<I', v)[0]
    return str(value)


def int64_type(v, s, flag):
    value = struct.unpack('<q', v)[0]
    return str(value)


def uint64_type(v, s, flag):
    value = struct.unpack('<Q', v)[0]
    return str(value)


def real32_type(v, s, flag):
    value = struct.unpack('<f', v)[0]
    return str(value)


def real64_type(v, s, flag):
    value = struct.unpack('<d', v)[0]
    return str(value)


def bool_type(v, s, flag):
    value = uint32_type(v, s, flag)
    if value is '0':
        return 'true'
    elif value is '1':
        return 'false'
    else:
        raise NotImplementedError


def binary_type(v, s, flag):
    temp = list()
    buf = io.BytesIO(v)
    for i in range(len(v)):
        temp.append(hex(ord(buf.read(1))))
    value = "".join(temp)
    return value


def guid_type(v, s, flag):
    temp = list()
    buf = io.BytesIO(v)
    for i in range(len(v)):
        temp.append(hex(ord(buf.read(1))).lstrip('0x'))
    value = "-".join(temp)

    return value


def sizet_type(v, s, flag):
    if len(v) == 4:
        value = hex_int32_type(v, s, flag)
    elif len(v) == 8:
        value = hex_int64_type(v, s, flag)
    else:
        raise NotImplementedError
    return value


def filetime_type(v, s, flag):
    value = struct.unpack('<Q', v)[0]
    return str(filetime(value))


def systime_type(v, s, flag):
    return "systime_type"


def sid_type(v, s, flag):
    sid = list()
    sid.append('S')
    buf = io.BytesIO(v)
    revision, count, id_authority = struct.unpack('BB6s', buf.read(8))
    sid.append(str(revision))
    sid.append(SID_LOOKUP_TABLE[id_authority])
    for i in range(count):
        subAuthority = str(struct.unpack('<I', buf.read(4))[0])
        sid.append(subAuthority)

    value = "-".join(sid)
    return value


def hex_int32_type(v, s, flag):
    value = hex(struct.unpack('<I', v)[0]).rstrip('L')
    return str(value)


def hex_int64_type(v, s, flag):
    value = hex(struct.unpack('<Q', v)[0]).rstrip('L')
    return str(value)


def evt_handle(v, s, flag):
    return "NOT_USING(EVT_HANDLE)"


def binxml_type(v, s, flag):
    return "binxml_type"


def evtxml(v, s, flag):
    return "NOT_USING(EVTXML)"


VALUE_TYPES = {
    0x00: null_type,
    0x01: string_type,
    0x02: ansi_type,
    0x03: int8_type,
    0x04: uint8_type,
    0x05: int16_type,
    0x06: uint16_type,
    0x07: int32_type,
    0x08: uint32_type,
    0x09: int64_type,
    0x0a: uint64_type,
    0x0b: real32_type,
    0x0c: real64_type,
    0x0d: bool_type,
    0x0e: binary_type,
    0x0f: guid_type,
    0x10: sizet_type,
    0x11: filetime_type,
    0x12: systime_type,
    0x13: sid_type,
    0x14: hex_int32_type,
    0x15: hex_int64_type,
    0x20: evt_handle,
    0x21: binxml_type,
    0x23: evtxml
}
