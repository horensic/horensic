from .defines import *
from utils.output import HexView


class PE(object):

    MZ_SIGNATURE = b'MZ'
    PE_SIGNATURE = b'PE\x00\x00'

    def __init__(self, pe):
        self.pe = None
        self.pe_path = pe

        if not self.pe_path:
            raise NotImplementedError
        else:
            try:
                self.pe = open(self.pe_path, 'rb')
            except IOError:
                print("Can't open the PE File. Please Check the file path")
                exit(-1)
            else:
                self.dos_header()
                self.dos_stub()
                self.nt_header()

    def __repr__(self):
        return 'PE FILE'

    def __iter__(self):
        for key in dir(self):
            if not key.startswith('_'):
                yield key, getattr(self, key)

    def dos_header(self):
        dos_hdr_buf = self.pe.read(DOS_HDR_SZ)
        HexView(dos_hdr_buf)
        self.dos_hdr = dict(zip(DOS_HDR_FILED, struct.unpack(DOS_HDR_FORMAT, dos_hdr_buf)))

        if not self.check_mz_signature(self.dos_hdr['e_magic']):
            print("MZ signature is not matched")
            return -1

    def dos_stub(self):
        pass

    def nt_header(self):
        self.pe.seek(self.dos_hdr['e_lfanew'])
        pe_magic_buf = self.pe.read(4)
        pe_magic = struct.unpack('<4s', pe_magic_buf)[0]

        if not self.check_pe_signature(pe_magic):
            print("PE signature is not matched")
            return -1

        img_file_buf = self.pe.read(IMG_FILE_HDR_SZ)
        self.img_file_hdr = dict(zip(IMG_FILE_HDR_FILED, struct.unpack(IMG_FILE_HDR_FORMAT, img_file_buf)))

        img_opt_buf = self.pe.read(IMG_OPT_HDR_SZ)
        self.img_opt_hdr = dict(zip(IMG_OPT_HDR_FILED, struct.unpack(IMG_OPT_HDR_FORMAT, img_opt_buf)))

    def section_header(self):
        pass

    def check_mz_signature(self, magic):
        return self.MZ_SIGNATURE == magic

    def check_pe_signature(self, magic):
        return self.PE_SIGNATURE == magic
