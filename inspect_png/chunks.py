#!/usr/bin/env python3
import struct
import zlib
from yachalk import chalk
import datetime as dt
from typing import List
from .chunk_types import *

class PNGChunk:
    def __init__(self, ctype:bytes, length:int, data:bytes, crc:bytes, file_pos:int, file_end:int, index:int):
        self.length = length
        self.ctype = ctype
        self.data = data
        if crc is not None and crc != self.calc_crc():
            print(f"[WARNING] CRCs of {ctype} differ!")
        self.crc = crc if crc is not None else self.calc_crc()
        self.file_pos = file_pos
        self.file_end=file_end
        self.index = index
    
    def calc_crc(self):
        return struct.pack(">I", zlib.crc32(self.ctype+self.data))
    
    def get_bytes(self, calc_crc=False, calc_size=False, new_ctype=None, **_):
        crc = self.crc if not calc_crc else self.calc_crc()
        size = self.length if not calc_size else len(self.data)
        ctype = self.ctype if new_ctype is None else str(new_ctype)[:4]
        fmt = '>I4s%ds4s'%size
        return struct.pack(fmt, size, ctype, self.data, crc)

    def present(self, show_crc=False, show_bytes=True, show_length=False, only_raw=False):
        if only_raw:
            return self.data
        s = chalk.green(f"{self.ctype.decode('ASCII')} ({self.index}):\n")
        s += chalk.blue(f"[{self.file_pos}-{self.file_end}]\n")
        if show_length:
            s+= f"Length: {chalk.cyan(str(self.length))}\n"
        if show_bytes:
            d_str = (self.data[:19] + b"...") if len(self.data)>20 else self.data
            s += f"Chunk: {d_str}\n"
        if show_crc:
            s += f"Crc: {chalk.yellow(str(self.crc.hex()))}\n"
        return s

class IHDR_PNGChunk(PNGChunk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.w,\
        self.h,\
        self.bit_depth,\
        self.color_type,\
        self.compression_method,\
        self.filter_method,\
        self.interlace_method = struct.unpack(">IIBBBBB", self.data)

    def present(self,**options):
        s = super().present(**options)
        if options.get("only_raw", False): return s
        s+=f"Width:              {self.w}\n"
        s+=f"Height:             {self.h}\n"
        s+=f"Bit depth:          {self.bit_depth}\n"
        s+=f"Color type:         {self.color_type}\n"
        s+=f"Compression method: {self.compression_method}\n"
        s+=f"Filter method:      {self.filter_method}\n"
        s+=f"Interlace method:   {self.interlace_method}\n"
        return s

"""     def get_bytes(self, calc_crc=False, calc_size=False, new_ctype=None, **_):
        data = struct.pack(">IIBBBBB", self.w, self.h, self.bit_depth, self.color_type, self.compression_method, self.filter_method, self.interlace_method)
        print(data)
        crc = self.crc if not calc_crc else self.calc_crc()
        size = self.length if not calc_size else len(data)
        ctype = self.ctype if new_ctype is None else str(new_ctype)[:4]
        fmt = '>I4s%ds4s'%size
        return struct.pack(fmt, size, ctype, data, crc) """

class tIME_PNGChunk(PNGChunk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        values = struct.unpack(">HBBBBB", self.data)
        self.datetime = dt.datetime(*values)
    
    def present(self,**options):
        s = super().present(**options)
        if options.get("only_raw", False): return s
        s+=f"DateTime:           {self.datetime}"
        return s

class txt_PNGChunk(PNGChunk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            key, text = self.data.split(b'\x00', 1)
            self.t_key = key.decode('utf-8', 'replace')
            self.t_text = text.decode('utf-8', 'replace')
        except ValueError:
            self.t_key = None
            self.t_text = self.data.decode('utf-8', 'replace')
    
    def present(self,**options):
        s = super().present(**options)
        if options.get("only_raw", False): return s
        if self.t_key is None:
            s+=f"Text:               {self.t_text}"
        else:
            s+=f"Text:               {self.key}={self.t_text}"
        return s

class ztxt_PNGChunk(PNGChunk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        key, rest = self.data.split(b'\x00', maxsplit=1)
        self.t_key = key.decode('utf-8')
        self.t_method = rest[0]
        self.t_text = zlib.decompress(rest[1:]).decode('utf-8', 'replace')
    
    def present(self,**options):
        s = super().present(**options)
        if options.get("only_raw", False): return s
        if self.t_key is None:
            s+=f"Text (zipped):      (Method:{self.t_method}){self.t_text}"
        else:
            s+=f"Text (zipped):      (Method:{self.t_method}){self.t_key}={self.t_text}"
        return s

def chunk_from_file(f):
    file_startpos = f.tell()
    length_b = f.read(4)
    name = f.read(4)
    length = struct.unpack(">I", length_b)[0]
    data = f.read(length)
    crc_r = f.read(4)
    file_endpos = f.tell()-1
    constructor_vals = (name,length,data,crc_r,file_startpos,file_endpos,None)

    classes = {
        TYPE_IHDR:IHDR_PNGChunk,
        TYPE_tIME:tIME_PNGChunk,
        TYPE_tEXt:txt_PNGChunk,
        TYPE_iTXt:txt_PNGChunk,
        TYPE_zTXt:ztxt_PNGChunk

    }
    constructor = classes.get(name, PNGChunk)
    return constructor(*constructor_vals)
