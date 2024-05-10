
import struct

def pack_float (float):
    return list(reversed(struct.pack("!f", float)))
