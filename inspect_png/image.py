from typing import List
from .chunks import PNGChunk, IHDR_PNGChunk,tIME_PNGChunk,txt_PNGChunk,ztxt_PNGChunk,chunk_from_file

class PNGImage:
    HEADER = bytes(
        [
            # First byte, so txt files starting with "PNG" are correctly interpreted
            0x89,

            # Letters PNG
            # 50 4E 47,
            *b"PNG",

            # A DOS-style line ending (CRLF) to detect DOS-Unix line ending conversion of the data.
            0x0D, 0x0A,

            # A byte that stops display of the file under DOS when the command type has been used—the end-of-file character.
            0x1A,

            # A Unix-style line ending (LF) to detect Unix-DOS line ending conversion.
            0x0A
        ]
    )
    LEN_HEADEAR = len(HEADER)

    def __init__(self, header: bytes, chunks: List[PNGChunk]):
        self.header = header
        self.chunks = chunks
        self.IHDR = None
        for c in chunks:
            if isinstance(c, IHDR_PNGChunk):
                self.IHDR = c
                break
        assert self.IHDR != None, "Missing IHDR Chunk"

    def save_as(self, filename, **options):
        with open(filename, "wb") as wf:
            wf.write(self.header)
            for c in self.chunks:
                b = c.get_bytes(**options)
                wf.write(b)
            wf.flush()

    def get_next_chunk_id(self):
        return len(self.chunks)

    def present(self, **options):
        if options["only_raw"]:
            return b"\n".join([c.present(**options) for c in self.chunks])
        chunks_str = '\n'.join([c.present(**options) for c in self.chunks])
        return f"""PNGImage\nHeader: {self.header}\n\nChunks:\n{chunks_str}\n"""

    @staticmethod
    def from_file(f):
        header = f.read(PNGImage.LEN_HEADEAR)
        if header != PNGImage.HEADER:
            print("Header missmatch!")
            print("Expected:", PNGImage.HEADER)
            print("Got     :", header)
            raise Exception("Not a valid PNG file!")
        chunks = []
        c = None
        while c is None or c.ctype != b"IEND":
            c = chunk_from_file(f)
            c.index = len(chunks)+1
            chunks.append(c)
        return PNGImage(header, chunks)
