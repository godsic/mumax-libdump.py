#!/usr/bin/python3

import struct
import sys
import numpy as np
from collections import namedtuple
from ctypes import c_ulonglong

header = '@8s4Q3d8sd8s8s8sQ'
headersize = struct.calcsize(header)

MAGIC = '#dump002'
prec = 4

DUMPHDR = namedtuple('DUMPHDR', ['magic', 'comp', 'sx', 'sy', 'sz',
                                 'csx', 'csy', 'csz',
                                 'meshunit', 'arg', 'argunit',
                                 'quant', 'quantunit', 'prec'])


def load(filename):
    try:
        file = open(filename, 'rb')
        h = file.read(headersize)
        dumphdr = DUMPHDR._make(struct.unpack(header, h))
        magic_t = dumphdr.magic.decode('utf-8')
        if magic_t != MAGIC:
            raise ValueError("dump: bad magic number: ", magic_t,
                             " expecting: ", MAGIC)
        if dumphdr.prec != prec:
            raise ValueError(
                "dump: unsupported data precission: ",
                dumphdr.prec, " bytes; expecting :", prec, " bytes")
        framesize = dumphdr.comp * dumphdr.sx * \
            dumphdr.sy * dumphdr.sz

        data = np.fromfile(file, dtype=np.float32, count=framesize)
        data = data.reshape(dumphdr.comp, dumphdr.sx,
                            dumphdr.sy, dumphdr.sz)
        crc = struct.unpack('@Q', file.read(8))[0]
        print("# crc: ", hex(crc), file=sys.stderr)
    except ValueError:
        raise
    finally:
        file.close()

    return dumphdr, data


def save(filename, dumphdr, data):
    try:
        file = open(filename, 'wb')
        file.write(struct.pack(header, *dumphdr))
        data.tofile(file)
        # to my bigest surprise Python does not have crc64 module
        file.write(c_ulonglong(0))
    finally:
        file.close()
    return


# main body
if __name__ == "__main__":
    fn = sys.argv[1]
    dump, m = load(fn)
    print(dump.csx, dump.csy, dump.csz, m.shape)
    print(m[2, :, :, :])
    save(fn + '.new.dump', dump, m)
