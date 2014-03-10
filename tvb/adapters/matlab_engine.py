
"""
This module provides an interface to part of the MATLAB Engine API. 

Startup is a little slow as with the existing MATLAB adapter, but the subsequent calls
complete very quickly, making this suitable for interactive use.

Note: this code isn't yet adapted for use in TVB, and requires cross-platform adaptation
as well.

"""

# import the FFI
from ctypes import *

# open the engine library
lib = CDLL('libeng.so')

class MATLABEngine(object):

    _buffer, _buffer_size = None, 0

    def _set_buffer_size(self, val):
        self._buffer_size = val 
        self._buffer = create_string_buffer(val + 1)

    def _get_buffer_size(self):
        return self._buffer_size

    buffer_size = property(_get_buffer_size, _set_buffer_size)

    @property
    def output(self):
        b = self._buffer
        out = b.raw.split(b.raw[-1])[0]
        if len(out) == self._buffer_size:
            print 'MLEng output buffer filled'
        return out

    def __init__(self, startcmd="", bufsize=100*1024):
        self._eng = lib.engOpen(startcmd)
        self.buffer_size = bufsize
        lib.engOutputBuffer(self._eng, self._buffer, self.buffer_size)

    def __del__(self):
        lib.engClose(self._eng)

    def __call__(self, cmd, out='print'):
        if not type(cmd) in (str,):
            cmd = str(cmd)

        print '>> ', cmd
        lib.engEvalString(self._eng, cmd)

        if out == 'print':
            print self.output
        elif out == 'return':
            return self.output
        else:
            pass
