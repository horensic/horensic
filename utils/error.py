def log_msg(level, msg):
    log = "[{lv}] {m}".format(lv=level, m=msg)
    print(log)


class ObjectAbortException(Exception):

    def __init__(self):
        super(ObjectAbortException, self).__init__("Object Abort Exception")


# Korean encoding/decoding problem exception class
# cp949-utp8/cp949-euckr/cp949-cp949
# utp8-cp949/utp8-euckr/utp8-utp8
# euckr-utp8/euckr-cp949/euckr-euckr
