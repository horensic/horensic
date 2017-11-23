def log_msg(level, msg):
    log = "[{lv}] {m}".format(lv=level, m=msg)
    print(log)


class ObjectAbortException(Exception):

    def __init__(self):
        super(ObjectAbortException, self).__init__("Object Abort Exception")
