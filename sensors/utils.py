
import struct

def pack_int (value, count):
    L = []
    for i in range(count):
        L.append(value % 256)
        value //= 256
    return L
def pack_float (float):
    return list(reversed(struct.pack("!f", float)))
