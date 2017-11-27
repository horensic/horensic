from datetime import datetime, timedelta


def filetime(v, bias=None):
    """
    :param v: little-endian binary data in long(integer) type (ex. 131210007740281591)
    :param bias: timezone option
    :return: YYYY-MM-DD hh:mm:ss.micros
    """
    dt = "{0:x}".format(v)
    us = int(dt, 16) / 10.
    return datetime(1601, 1, 1) + timedelta(microseconds=us)

def format_convert(t):
    pass