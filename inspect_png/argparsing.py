#!/usr/bin/env python3

import argparse

def get_filter_by_type(vals):
    byte_vals = [v.encode("ASCII") for v in vals]
    def f(p):
        return p.ctype in byte_vals
    return f

def get_gt_lt_filter_for(prop, cmp_str):
    if cmp_str[0:2] == "gt":
        return lambda o: getattr(o, prop) > int(cmp_str[2:])
    if cmp_str[0:3] == "gte":
        return lambda o: getattr(o, prop) >= int(cmp_str[3:])
    if cmp_str[0:2] == "lt":
        return lambda o: getattr(o, prop) < int(cmp_str[2:])
    if cmp_str[0:3] == "lte":
        return lambda o: getattr(o, prop) <= int(cmp_str[3:])
    return lambda o: getattr(o, prop) == int(cmp_str)

class GenerateFilterAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if not 'filters' in namespace:
            setattr(namespace, 'filters', [])
        previous = namespace.filters
        if '--type' in self.option_strings:
            previous.append(get_filter_by_type(values))
        if '--index' in self.option_strings:
            previous.append(get_gt_lt_filter_for('index', values))
        if '--size' in self.option_strings:
            previous.append(get_gt_lt_filter_for('length', values))
        setattr(namespace, 'filters', previous)

def get_parser():
    ap = argparse.ArgumentParser()
    ap.set_defaults(filters=[])
    subparsers = ap.add_subparsers(dest="command", help="Choose what do you want to do with inspect-png",required=True)

    fix_parser = subparsers.add_parser("fix", help="Fixes the PNG by recalculating CRC32-s")
    fix_parser.add_argument("pngfile", type=str, help="PNG input file")
    fix_parser.add_argument("pngout", help="Output PNG file", type=str)
    #fix_parser.add_argument("--remove-text", help="Removes all text chunks", default=False, action="store_true", dest="removetxt")

    chunk_parser = subparsers.add_parser("chunk", help="Analyze PNG chunks")
    chunk_parser.add_argument("pngfile", type=str, help="PNG input file")
    chunk_parser.add_argument("-t","--type", help="Filter by type",type=str, nargs="+",action=GenerateFilterAction)
    chunk_parser.add_argument("-i","--index", help="Filter by index",type=str, action=GenerateFilterAction)
    chunk_parser.add_argument("-s","--size", help="Filter by size",type=str, action=GenerateFilterAction)
    chunk_parser.add_argument("--crc", help="Toggle print crc", default=False, action="store_true", dest="show_crc")
    chunk_parser.add_argument("--length", help="Toggle print length", default=False, action="store_true", dest="show_length")
    chunk_parser.add_argument("--raw", help="Toggle raw print bytes", default=False, action="store_true", dest="only_raw")

    extract_parser = subparsers.add_parser("extract", help="Extract data from PNG chunks")
    extract_parser.add_argument("pngfile", type=str, help="PNG input file")
    extract_parser.add_argument("-t","--type", help="Filter by type e.g. IHDR, ...",type=str, nargs="+",action=GenerateFilterAction)
    extract_parser.add_argument("-i","--index", help="Filter by index e.g. gt2, ...",type=str, action=GenerateFilterAction)
    extract_parser.add_argument("-s","--size", help="Filter by size e.g. lt30, gte40, ...",type=str, action=GenerateFilterAction)
    extract_parser.add_argument("-o","--output-file", help="Output file for chunk data", type=str, default=None, dest="file")
    extract_parser.add_argument("-p","--output-png", help="Output PNG file", type=str, dest="pngout", default=None)
    extract_parser.add_argument("-", help="Output binary data to console", default=False, action="store_true",dest="to_stdout")
    return ap

if __name__ == "__main__":
    parsed= get_parser().parse_args()
    print(parsed)
