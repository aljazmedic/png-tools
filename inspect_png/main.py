#!/usr/bin/env python3
from .chunk_types import *
from .chunks import PNGChunk, IHDR_PNGChunk,tIME_PNGChunk,txt_PNGChunk,ztxt_PNGChunk,chunk_from_file
from .image import PNGImage
from .argparsing import get_parser

def main():
    import sys
    parsed = get_parser().parse_args()
    #print(parsed.pngfile)
    #print(parsed)
    with open(parsed.pngfile, "rb") as rf:
        p = PNGImage.from_file(rf)

    if parsed.command == "chunk":
        present_options = {k: getattr(parsed, k, False) for k in ["only_raw", "show_length", "show_crc"]}

        ## Apply the filters
        while len(parsed.filters):
            f = parsed.filters.pop(0)
            p.chunks = list(filter(f, p.chunks))
            for i, c in enumerate(p.chunks, start=1):
                c.index = i
            
        ## Present chunks
        for c in p.chunks:
            print(c.present(**present_options))

    elif parsed.command == "extract":
        while len(parsed.filters):
            f = parsed.filters.pop(0)
            p.chunks = list(filter(f, p.chunks))
            for i, c in enumerate(p.chunks, start=1):
                c.index = i
        
        all_data = b''.join([c.data for c in p.chunks])

        if parsed.file is None and parsed.pngout is None and not parsed.to_stdout:
            ## Present chunks
            print(all_data)
            return
        
        if parsed.file is not None :
            with open(parsed.file, "wb") as wf:
                wf.write(all_data)
                wf.flush()
        
        if parsed.pngout is not None:
            p.save_as(parsed.pngout)
        
        if parsed.to_stdout:
            sys.stdout.buffer.write(all_data)
    
    elif parsed.command == "fix":
        if not parsed.pngout:
            raise Exception("Please provide output filename")
        p.save_as(parsed.pngout, calc_crc=True, calc_size=True)

    elif parsed.command == "brute_dim":
        from .fixing import bruteforce_wh
        if not parsed.pngout:
            raise Exception("Please provide output filename")
        bruteforce_wh(p)
        p.save_as(parsed.pngout, calc_crc=True, calc_size=True)


if __name__ == "__main__":
    main()
