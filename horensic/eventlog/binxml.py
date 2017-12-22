from .evtx import *
from .defines import *
from .types import *
from .error import *
from xml.etree.ElementTree import Element, dump


def indent(elem, level=0):
    i = "\n" + level*"  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i


class BinXML(object):

    def __init__(self, buf, chunk_start, s_table, t_table):
        # self.offset = offset
        self.buf = buf
        self.chunk_start = chunk_start
        self.s_table = s_table
        self.t_table = t_table
        self.start_sarray = int()
        self.sarray = []
        self.template_instance = None
        # Read the template and register it in the template table
        self.read_template()
        self.root = self.make_xml()

    def __repr__(self):
        return "BinXML"

    def read_template(self):
        tid = ord(self.buf.read(1))

        if TOKEN_LOOKUP_TABLE[tid] is 'FragmentHeader':
            FragmentHeader(self.buf)
            tid = ord(self.buf.read(1))

        if TOKEN_LOOKUP_TABLE[tid] is 'TemplateInstance':
            self.template_instance = TemplateInstance(self.buf, self.t_table)
            ret_address = self.buf.tell()
            self.template_instance.update(self.chunk_start, ret_address)
            
            if self.template_instance.define():
                td_ofs = self.buf.tell()
                template_def = TemplateDefinition(td_ofs, self.buf)

                self.start_sarray = self.buf.tell() + template_def.size
                self.read_sarray()
            else:
                self.start_sarray = ret_address
                self.read_sarray()

                td_ofs = self.template_instance.def_offset
                self.buf.seek(td_ofs)
                template_def = TemplateDefinition(td_ofs, self.buf)

            tid = ord(self.buf.read(1))

            if TOKEN_LOOKUP_TABLE[tid] is 'FragmentHeader':
                FragmentHeader(self.buf)
            else:
                raise InvalidBinXMLException
        else:
            raise InvalidBinXMLException

    def read_sarray(self):

        slookup = list()
        ret_address = self.buf.tell()
        self.buf.seek(self.start_sarray)
        count = struct.unpack('I', self.buf.read(4))[0]

        if count == 0:
            self.buf.seek(ret_address)
            return

        for i in range(count):
            slookup.append(list((struct.unpack(SUBSTITUTION_ARR_FORMAT, self.buf.read(4)))))

        for size, type, _ in slookup:

            if type is 0x21:  # binXML type
                e = BinXML(self.buf, self.chunk_start, self.s_table, self.t_table).root
            else:
                if (type & 0x80) == 0x80:
                    v = self.buf.read(size)
                    e = VALUE_TYPES[type ^ 0x80](v, size, True)
                else:
                    v = self.buf.read(size)
                    e = VALUE_TYPES[type](v, size, False)

            self.sarray.append(e)
        self.buf.seek(ret_address)

    def read_token(self):
        pass

    def make_xml(self):
        stack = ['I']  # initialize
        root = None

        while True:
            token = Token(self.buf, self.chunk_start, self.s_table, self.sarray)
            if token.EOF:
                return root

            if stack[-1] is 'I':
                stack.pop()
                root, child = self.make_element(token)

                if child:
                    stack.append('R')
                else:
                    return root

            elif stack[-1] is 'R':

                if token.end:
                    stack.pop()
                else:
                    tmp, child = self.make_element(token)
                    if child:
                        stack.pop()
                        stack.append(tmp)
                    root.append(tmp)

            else:
                if token.end:
                    stack.pop()
                    stack.append('R')
                else:
                    tmp, child = self.make_element(token)
                    pre_elem = stack.pop()
                    pre_elem.append(tmp)  # TODO: pre_elem is Element,
                    if child:
                        stack.append(pre_elem)
                        stack.append(tmp)
                    stack.append(pre_elem)
        # return root

    @staticmethod
    def make_element(tk):
        token = tk
        children = None
        elem = Element(token.name)

        if not token.attribute:
            pass
        else:
            for a, v in zip(token.attribute, token.value):
                if v is not 'NULL':
                    elem.attrib[a] = v

        if (token.content is None) and not isinstance(token.content, Element):
            elem.text = None
            if not token.empty:
                children = True
        else:
            if isinstance(token.content, Element):
                if token.name == "SubRoot":
                    elem = token.content
                else:
                    elem.append(token.content)
            else:
                elem.text = token.content

        return elem, children

    def print_xml(self):
        indent(self.root)
        dump(self.root)


class Token(object):

    name = ""
    content = None
    empty = None
    child = False
    end = False
    EOF = False

    def __init__(self, buf, chunk_start, s_table, sarray):
        self.buf = buf
        self.chunk_start = chunk_start
        self.s_table = s_table
        self.sarray = sarray
        self.attribute = []
        self.value = []
        self.parser()

    def __repr__(self):
        return "BinXML_Token"

    def parser(self):
        tid = ord(self.buf.read(1))

        if TOKEN_LOOKUP_TABLE[tid] is 'OpenStart':
            name_id = self.open_start()
            ret_address = self.buf.tell()
            self.name = self.get_name(name_id, ret_address)
            if self.has_attribute(tid):
                for a, v in self.get_attribute(False):
                    self.attribute.append(a)
                    self.value.append(v)

            if self.has_content():
                self.get_content()

        elif TOKEN_LOOKUP_TABLE[tid] is 'End':
            self.end = True

        elif TOKEN_LOOKUP_TABLE[tid] is 'EOF':
            self.EOF = True

        elif TOKEN_LOOKUP_TABLE[tid] is 'OptionalSubstitution':
            self.name = "SubRoot"
            self.content = Content(self.buf, self.sarray, False).text

        else:  # Not Found Start Token
            raise InvalidBinXMLException

    def open_start(self):
        open_token = self.buf.read(ELEMENT_START_SZ)
        token_info = dict(zip(ELEMENT_START_FIELDS, struct.unpack(ELEMENT_START_FORMAT, open_token)))
        return token_info['name_offset']

    def get_name(self, name_id, ra):

        if name_id in self.s_table.keys():
            name_offset = self.s_table[name_id]
        else:
            name_offset = self.chunk_start + name_id

        name = NameString(name_offset, self.buf).name

        if not ra == name_offset:
            self.buf.seek(ra)

        return name

    @staticmethod
    def has_attribute(tid):
        return tid == 0x41

    def get_attribute(self, flag):

        if not flag:
            attribute_sz = struct.unpack('I', self.buf.read(4))[0]

        tid = ord(self.buf.read(1))

        if TOKEN_LOOKUP_TABLE[tid] is 'Attribute':
            name_id = struct.unpack('I', self.buf.read(4))[0]
            ra = self.buf.tell()
            attribute_name = self.get_name(name_id, ra)
            value = Content(self.buf, self.sarray, True).text  # TODO

            if tid == 0x46:  # has more attributes
                yield attribute_name, value
                for a, v in self.get_attribute(True):
                    yield a, v
            else:
                yield attribute_name, value
        else:
            raise InvalidBinXMLException

    def has_content(self):
        tid = ord(self.buf.read(1))
        if 'Close' in TOKEN_LOOKUP_TABLE[tid]:
            return tid == 0x02
        else:
            raise InvalidBinXMLException

    def get_content(self):
        # preview
        ra = self.buf.tell()
        check = ord(self.buf.read(1))
        self.buf.seek(ra)
        if TOKEN_LOOKUP_TABLE[check] is not 'OpenStart':

            if check == 0x04:
                self.content = None
            else:
                self.content = Content(self.buf, self.sarray, True).text

            end = ord(self.buf.read(1))

            if TOKEN_LOOKUP_TABLE[end] is 'End':
                pass
            else:
                self.child = True


class Content(object):

    text = None

    def __init__(self, buf, sarray, flag):
        self.buf = buf
        self.sarray = sarray
        if flag:
            cid = ord(self.buf.read(1))
        else:
            self.buf.seek(-1, 1)
            cid = ord(self.buf.read(1))
        ContentDispatchTable = {
            0x05: ValueText,
            0x07: CDATASection,
            0x08: CharRef,
            0x09: EntityRef,
            0x0a: PITarget,
            0x0b: PIData
        }
        SubstitutionDispatchTable = {
            0x0d: NormalSubstitution,
            0x0e: OptionalSubstitution
        }
        if cid in ContentDispatchTable.keys():
            self.content = ContentDispatchTable[cid](self.buf)
        elif cid in SubstitutionDispatchTable.keys():
            self.content = SubstitutionDispatchTable[cid](self.buf, self.sarray)
        else:
            raise InvalidBinXMLException
        self.text = self.content.data
