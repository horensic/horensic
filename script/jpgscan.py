import os
import glob
import struct


def jpg_end(data):

    if type(data) == str:
        data2 = [ord(c) for c in data]
    else:
        data2 = data

    i = 2

    while i + 2 <= len(data):
        if data2[i] == 0xff and data2[i+1] >= 0xc0:
            if data2[i+1] == 0xd9:
                return i + 2
            elif data2[i+1] == 0xd8:
                return i
            elif 0xd0 <= data2[i+1] <= 0xd7:
                i += 2
            else:
                if i + 4 > len(data):
                    return len(data)
                i += struct.unpack('>H', data[i+2:i+4])[0] + 2
        else:
            i += 1

    return min(i, len(data))


def image_end(data):
    magic = data[:8]
    if magic.startswith('\xFF\xD8'):
        return jpg_end(data)
    else:
        return len(data)


def scan(path, result):

    f = open(path, 'rb')
    try:
        rd = f.read()
    finally:
        f.close()

    eoi = image_end(rd)

    if eoi == len(rd):
        return False

    jpg_name = os.path.split(path)[1]
    data_name = os.path.join(result, jpg_name + '.data')

    if not os.path.exists(data_name):
        data_file = open(data_name, 'wb')
        try:
            data_file.write(rd[eoi:])
        finally:
            data_file.close()

    return True


if __name__ == '__main__':

    output = "./result"
    os.mkdir(output)

    jpg_list = []
    jpg_list = glob.glob("*.jpg")

    for jpg in jpg_list:
        hidden_data = scan(jpg, output)
