## inspect-png
---
A CTF tool for PNG file inspection

For installation of the tool run
`python setup.py install`

Usage:
```
Usage: inspect_png.py [-h] [-t TYPE [TYPE ...]] [-i INDEX] [-s SIZE] [--text]
                      [--weird] [--crc] [--length] [--raw] [-o FILE]
                      [-p PNGOUT] [-] [--brute-dim] [--recalc] [-q | -v]
                      pngfile

positional arguments:
  pngfile               PNG input file

optional arguments:
  -h, --help            show this help message and exit
  -q, --quiet
  -v, --verbose

Filters:
  -t TYPE [TYPE ...], --type TYPE [TYPE ...]
                        Filter by type
  -i INDEX, --index INDEX
                        Filter by index
  -s SIZE, --size SIZE  Filter by size
  --text                Include only text chunks
  --weird               Include non-specified chunks

Chunk info display:
  --crc                 Show chunk crc
  --length              Show chunk length
  --raw                 Only show chunk bytes

Output options:
  -o FILE, --output-file FILE
                        Output file for chunk data
  -p PNGOUT, --output-png PNGOUT
                        Output PNG file
  -                     Output binary data to console

Fixes:
  --brute-dim           Bruteforces dimensions based on known CRC
  --recalc              Recalculates CRCs of PNG Chunks
```
