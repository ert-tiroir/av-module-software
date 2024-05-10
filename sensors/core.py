
#include "utils/string.h"
#include "utils/consts.h"
#include <unistd.h>

import os
import errno

HANDSHAKE = 0x42424242

def safe_read (fd, size):
    try:
        return os.read(fd, size)
    except OSError as exc:
        if exc.errno == errno.EAGAIN:
            return ""
        raise exc

def read_all (fd, size): 
    offset = 0
    S = []
    while offset != size: 
        str = safe_read(fd, size - offset)
        res = len(str)
        if res <= 0: 
            continue
        S.append(str)
        offset += res
    
    return b"".join(S)

def read_all_or_nothing (fd, size):
    string = safe_read(fd, size)
    if len(string) == 0:
         return b""

    res = read_all(fd, size-len(string))
    return string + res

def write_all (fd, buffer): 
    offset = 0
    size = len(buffer)

    while offset != size:
        res = os.write(fd, buffer[offset:])
        if res < 0:
             return res

        offset += res
    
    return size

def write_all_or_nothing (fd, buffer): 
    offset = os.write(fd, buffer)
    if offset <= 0:
         return 0

    res = write_all(fd, buffer[offset:])
    if res < 0:
         return res

    return len(buffer)


def read_string (fd): 
    size_buffer = read_all_or_nothing (fd, 4)
    if len(size_buffer) == 0:
        return (False, b"")
    size = size_buffer[0] + size_buffer[1]*256 + size_buffer[2]*256**2 +size_buffer[3]*256**3
    if(size>HANDSHAKE):
        size-=1
    if(size==HANDSHAKE):
        return(False, b"")
    return(True, read_all (fd, size))
    

def write_string (fd, str):
    buffer = [0, 0, 0, 0]
    size = len(str)
    if(size>=HANDSHAKE):
        size+=1
    buffer[0]=size % 256
    buffer[1]=(size // 256) % 256
    buffer[2]=(size // (256 ** 2)) % 256
    buffer[3]=(size // (256 ** 3)) % 256
    
    write_all(fd, bytes(buffer))
    write_all(fd, str)

    return True

class CoreTarget:

    def start (self):
        self.fd_logger        = os.open(self.path_logger, os.O_WRONLY | os.O_NONBLOCK)
        self.fd_module_output = os.open(self.path_module_output, os.O_WRONLY | os.O_NONBLOCK)
        self.fd_module_input  = os.open(self.path_module_input, os.O_RDONLY | os.O_NONBLOCK)

        if (self.fd_logger == -1 or self.fd_module_input == -1 or self.fd_module_output == -1):
            self.close()
            return
    

        buffer = bytes([0x42] * 4)

        write_all(self.fd_module_output, buffer)
    
    def close (self):
        if (self.fd_logger        != -1): os.close(self.fd_logger)
        if (self.fd_module_input  != -1): os.close(self.fd_module_input)
        if (self.fd_module_output != -1): os.close(self.fd_module_output)

        self.fd_logger        = -1
        self.fd_module_input  = -1
        self.fd_module_output = -1


    def __init__(self, path_module_output, path_module_input, path_logger):
        self.path_module_output = path_module_output
        self.path_module_input  = path_module_input
        self.path_logger        = path_logger

        self.fd_module_output = -1
        self.fd_module_input  = -1
        self.fd_logger        = -1

        self.start()

    def ready (self):
        return self.fd_logger != -1 and self.fd_module_input  != -1 and self.fd_module_output != -1

    def write_logger   (self, buffer):
        if not self.ready():
            return 0
        return os.write(self.fd_logger,buffer)
   

    def write_to_core  (self, buffer):
        if not self.ready():
            return 0
        return os.write(self.fd_module_output, buffer)
    

    def read_from_core (self, size):
        if not self.ready():
            return 0
        return safe_read(self.fd_module_input, size)
    

    def write_string_to_core (self, buffer):
        if not self.ready(): 
             return False
        return write_string(self.fd_module_output, buffer)
    

    def write_string_logger (self, buffer):
        if not self.ready(): 
            return False
        return write_string(self.fd_logger, buffer)
    
    def read_string_from_core (self):
        if not self.ready(): 
            return (False, b"")
        
        return read_string(self.fd_module_input)
