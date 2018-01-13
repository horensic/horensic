import struct
from datetime import datetime, timedelta


def win64le(v, bias=None):
    """
    NTFS Timestamp format
    :param v: little-endian binary data in long(integer) type (ex. 131210007740281591)
    :param bias: timezone option
    :return: YYYY-MM-DD hh:mm:ss.us
    """
    dt = "{0:x}".format(v)
    us = int(dt, 16) / 10.
    return datetime(1601, 1, 1) + timedelta(microseconds=us)


def fat32time(v, bias=None):
    """
    FAT32 FS Timestamp format
    :param v:
    :param bias: timezone option
    :return: YYYY-MM-DD hh:mm:ss.ms
    """
    YEAR_MASK = 0xFE00
    MONTH_MASK = 0x01E0
    DAY_MASK = 0x001F

    HOUR_MASK = 0xF800
    MIN_MASK = 0x07E0
    SEC_MASK = 0x001F

    if len(v) == 5:  # Created Time
        date, time, ms = struct.unpack('HHB', v)
    elif len(v) == 4:  # Modified Time
        date, time = struct.unpack('HH', v)
        ms = 0
    else:  # Accessed Time
        date = struct.unpack('H', v)[0]
        time = 0
        ms = 0

    year = (date & YEAR_MASK) >> 9
    month = (date & MONTH_MASK) >> 5
    day = (date & DAY_MASK)
    hour = (time & HOUR_MASK) >> 11
    minute = (time & MIN_MASK) >> 5
    second = (time & SEC_MASK)

    return "{Y}-{M}-{D} {h}:{m}:{s}.{ms}".format(Y=1980 + year, M=month, D=day, h=hour, m=minute, s=second, ms=ms)


def format_convert(t):
    pass
