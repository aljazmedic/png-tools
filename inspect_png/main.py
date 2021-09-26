#!/usr/bin/env python3
from .chunk_types import *
from .chunks import PNGChunk, IHDR_PNGChunk,tIME_PNGChunk,txt_PNGChunk,ztxt_PNGChunk,chunk_from_file
from .image import PNGImage
from .argparsing import get_parser
from logging import getLogger
import logging, coloredlogs, sys

def main():
    import sys
    parsed = get_parser().parse_args()

    # Print logs to stderr if piping bytes to stdout
    coloredlogs.install(level=parsed.loglevel, stream=(sys.stderr if parsed.to_stdout else sys.stdout))
    logging.debug(parsed)

    with open(parsed.pngfile, "rb") as rf:
        logging.debug(f"Reading file from {parsed.pngfile}")
        p = PNGImage.from_file(rf)

    if parsed.brutedim:
        from .fixing import bruteforce_wh
        bruteforce_wh(p)

    ## Apply the filters
    while len(parsed.filters):
        f = parsed.filters.pop(0)
        p.chunks = list(filter(f, p.chunks))
        for i, c in enumerate(p.chunks, start=1):
            c.index = i
    
    all_data = b''.join([c.data for c in p.chunks])

    # Check wether user wants to output data to stdout
    # If so, no output shall be provided
    if parsed.to_stdout:
        sys.stdout.buffer.write(all_data)
    else:
        if parsed.only_raw:
            # Only display chunk data
            for c in p.chunks:
                print(c.data)
        else:
            present_options = {k: getattr(parsed, k, False) for k in ["show_length", "show_crc"]}
            ## Present chunks
            for c in p.chunks:
                print(c.present(**present_options))
        
    if parsed.file is not None:
        with open(parsed.file, "wb") as wf:
            logging.debug(f"Writing out to {parsed.file}")
            wf.write(all_data)
            wf.flush()
        
    if parsed.pngout is not None:
        logging.debug(f"Writing png out to {parsed.pngout}")
        p.save_as(parsed.pngout, calc_crc=parsed.recalc, calc_size=parsed.recalc)

if __name__ == "__main__":
    main()
