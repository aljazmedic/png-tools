
from inspect_png.chunk_types import *
from inspect_png.image import *
import struct, re
import time, os, subprocess
import pickle

from logging import getLogger
logger = getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
def relative_file(f):
    return os.path.abspath(os.path.join(BASE_DIR, f))

PICKLE_FILE = relative_file("tmp/cache.pickle")
SRC_C = relative_file("cr.c")

def read_cache(f):
    if not os.path.exists(f):
        logger.debug("Cache not found")
        return {}
    else:
        with open(f, "rb") as rf:
            return pickle.load(rf)

def write_cache(cache, f):
    with open(f, "wb") as wf:
        pickle.dump(cache, wf)

def check_cache(ihdr, crc):
    return read_cache(PICKLE_FILE).get((ihdr, crc), None)

def update_cache(ihdr, crc, w, h):
    c = read_cache(PICKLE_FILE)
    c[(ihdr, crc)] = (w, h)
    write_cache(c, PICKLE_FILE)

def bruteforce_wh(png:PNGImage):
    logger.debug("Beginning bruteforce")
    ihdr = png.IHDR
    c_formatted_ihdr = ''.join(["\\x%02x"%x for x in (b'IHDR'+ihdr.data)])
    c_formatted_crc = hex(struct.unpack(">I", ihdr.crc)[0])
    logger.debug(f"IHDR     {c_formatted_ihdr}")
    logger.debug(f"IHDR crc {c_formatted_crc}")
    W, H = None, None
    res = check_cache(c_formatted_ihdr, c_formatted_crc)
    if res is not None:
        logger.info("Hit in cache")
        W, H = res
    else:
        logger.info("Creating C brute forcer:")
        with open(SRC_C) as rf:
            c_code = rf.read()
        c_code = c_code.replace("\\xDE\\xAD\\xBE\\xEF\\xDE\\xAD\\xBE\\xEF\\xDE\\xAD\\xBE\\xEF\\xDE\\xAD\\xBE\\xEF\\xDE", c_formatted_ihdr)
        c_code = c_code.replace("0x69696969", c_formatted_crc)
        try:
            exec_name = relative_file("tmp/cr{}".format(c_formatted_crc))
            tmp_name = exec_name+".c"
            with open(tmp_name, "w") as wf:
                wf.write(c_code)
            gcc_proc = subprocess.run(["gcc", tmp_name, "-o", exec_name])
            if gcc_proc.returncode != 0:
                raise Exception("Cannot compile .c file")
            process = subprocess.run([exec_name],stdout=subprocess.PIPE)
            if process.returncode != 0:
                raise Exception("Cannot find correct dimensions")
            else:
                output = process.stdout.decode("utf-8")
                m = re.match(r"W:([0-9]+) H:([0-9]+)", output)
                if m:
                    W, H = int(m[1]), int(m[2])
                    update_cache(c_formatted_ihdr,c_formatted_crc,W,H)
                else:
                    raise Exception("Cannot find correct dimensions")
        except Exception as e:
            logger.exception(e)
        finally:
            try: os.remove(tmp_name)
            except OSError: pass
            try: os.remove(exec_name+".exe")
            except OSError: pass
            try: os.remove(exec_name)
            except OSError: pass
    
    if W is not None and H is not None:
        logger.info(f"Found dimensions: {W} x {H}")
        ihdr.w = W
        ihdr.h = H
        ihdr.data = struct.pack(">II", W, H) + ihdr.data[8:]
        return True
    else:
        return False

if __name__=="__main__":
    with open("C:\\tools\\inspect-png\\art.png","rb") as rf:
        pi = PNGImage.from_file(rf)
    bruteforce_wh(pi)
