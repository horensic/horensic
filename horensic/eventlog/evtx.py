from .binxml import *
from .defines import *
from .error import *
import mmap


class Evtx(object):

    EVTX_SIGNATURE = b'ElfFile\0'  # EVTX Signature

    def __init__(self, path):
        self.evtx_path = path
    
    def __enter__(self):
        self.evtx_file = open(self.evtx_path, 'rb')
        self.buf = mmap.mmap(self.evtx_file.fileno(), 0, access=mmap.ACCESS_READ)
        self.offset = 0x0

        ef_hdr = self.buf.read(EVTX_HDR_SZ)
        fields = dict(zip(EVTX_HDR_FIELDS, struct.unpack(EVTX_HDR_FORMAT, ef_hdr)))
        for key in fields:
            setattr(self, key, fields[key])

        if not self.check_signature():
            raise InvalidEvtxException

        return self

    def __exit__(self, type, value, traceback):
        self.evtx_file.close()

    def __repr__(self):
        return "EVTX File"

    def chunks(self):
        ofs = self.offset + getattr(self, 'header_block_size')
        while ofs + 0x10000 <= len(self.buf):
            try:
                yield Chunk(ofs, self.buf)
            except InvalidChunkException:
                print("Evtx::Chunks")
                exit(-1)
            ofs += 0x10000

    def records(self):
        for chunk in self.chunks():
            for record in chunk.records():
                yield record

    def check_signature(self):
        return self.EVTX_SIGNATURE == getattr(self, 'signature')

    def check_error(self):
        raise NotImplementedError


class Chunk(object):

    EVTX_CHNK_SIGNATURE = b'ElfChnk\0'  # Chunk Signature

    def __init__(self, offset, buf):
        self.offset = offset
        self.buf = buf
        self.string_table = dict()
        self.template_table = dict()

        self.buf.seek(self.offset)
        chnk_hdr = self.buf.read(EVTX_CHNK_HDR_SZ)
        fields = dict(zip(EVTX_CHNK_HDR_FIELDS, struct.unpack(EVTX_CHNK_HDR_FORMAT, chnk_hdr)))
        for key in fields:
            setattr(self, key, fields[key])

        if not self.check_signature():
            raise InvalidChunkException

        self.strings()
        self.templates()

    def __repr__(self):
        return "EVTX Chunk"

    def strings(self):
        start = self.offset + EVTX_CHNK_HDR_SZ
        for i in range(int(EVTX_CHNK_STRT_SZ / 4)):
            ofs = start + i * 4
            self.buf.seek(ofs)
            str_id = struct.unpack('<I', self.buf.read(4))[0]
            if str_id > 0:
                str_ofs = self.offset + str_id
                self.string_table[str_id] = str_ofs

    def templates(self):
        start = self.offset + EVTX_CHNK_HDR_SZ + EVTX_CHNK_STRT_SZ
        for i in range(int(EVTX_CHNK_TPL_SZ / 4)):
            ofs = start + i * 4

            self.buf.seek(ofs)
            tpl_ofs = self.offset + struct.unpack('<I', self.buf.read(4))[0]

            self.buf.seek(tpl_ofs - 8)
            tpl_id = struct.unpack('<I', self.buf.read(4))[0]

            self.template_table[tpl_ofs] = tpl_id

    def records(self):
        start = self.offset + 0x200
        record = Record(start, self)
        free_space_offset = getattr(self, 'free_space_offset')

        while (record.offset < start + free_space_offset) and (record.size > 0):
            yield record
            try:
                record = Record(record.offset + record.size, self)
            except InvalidRecordException:
                return

    def check_signature(self):
        return self.EVTX_CHNK_SIGNATURE == getattr(self, 'signature')

    def check_error(self):
        raise NotImplementedError


class Record(object):

    RECORD_HDR_SIGNATURE = b'\x2a\x2a\x00\x00'  # Event record Signature

    def __init__(self, offset, chunk):
        self.offset = offset
        self.chunk_start = chunk.offset
        self.buf = chunk.buf
        self.string_table = chunk.string_table
        self.template_table = chunk.template_table
        self.root = None

        self.buf.seek(self.offset)
        rcd_hdr = self.buf.read(RECORD_HDR_SZ)
        fields = dict(zip(RECORD_HDR_FIELDS, struct.unpack(RECORD_HDR_FORMAT, rcd_hdr)))

        for key in fields:
            setattr(self, key, fields[key])

        if not self.check_signature():
            raise InvalidRecordException

    def __repr__(self):
        return "EVTX Record"

    @property
    def size(self):
        return getattr(self, 'record_size')

    @property
    def binxml_size(self):
        return self.size - RECORD_HDR_SZ

    @property
    def binxml_offset(self):
        return self.offset + RECORD_HDR_SZ

    def binxml(self):
        self.root = BinXML(self.buf, self.chunk_start, self.string_table, self.template_table)

    def check_signature(self):
        return self.RECORD_HDR_SIGNATURE == getattr(self, 'signature')


class LogMessage(object):

    def __init__(self):
        pass
