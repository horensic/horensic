import sys


# utf-8, euc-kr, cp949
def korean(msg):

    stdin_encoding = sys.stdin.encoding
    stdout_encoding = sys.stdout.encoding
    res = None

    try:
        res = msg.decode('utf-8').encode(stdout_encoding)
    except UnicodeEncodeError:
        res = msg.decode(stdin_encoding).encode('utf-8')
    except UnicodeDecodeError:
        # TODO
        pass

    return res
