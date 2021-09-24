#!/usr/bin/env python3

import argparse
from .chunk_types import *

def get_filter_by_type(vals):
    byte_vals = [v.encode("ASCII") for v in vals]
    def f(p):
        return p.ctype in byte_vals
    return f

def get_gt_lt_filter_for(prop, cmp_str):
    """ Returns function that compares integer prop of chunk """
    if cmp_str[0:3] == "gte":
        return lambda o: getattr(o, prop) >= int(cmp_str[3:])
    elif cmp_str[0:2] == "gt":
        return lambda o: getattr(o, prop) > int(cmp_str[2:])
    elif cmp_str[0:3] == "lte":
        return lambda o: getattr(o, prop) <= int(cmp_str[3:])
    elif cmp_str[0:2] == "lt":
        return lambda o: getattr(o, prop) < int(cmp_str[2:])
    return lambda o: getattr(o, prop) == int(cmp_str)

class GenerateFilterAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if not 'filters' in namespace:
            setattr(namespace, 'filters', [])
        current_filters = namespace.filters
        if '--type' in self.option_strings:
            current_filters.append(get_filter_by_type(values))
        elif '--index' in self.option_strings:
            current_filters.append(get_gt_lt_filter_for('index', values))
        elif '--size' in self.option_strings:
            current_filters.append(get_gt_lt_filter_for('length', values))
        elif '--text' in self.option_strings:
            current_filters.append(is_txt_chunk)
        elif '--weird' in self.option_strings:
            current_filters.append(is_not_specified)
        setattr(namespace, 'filters', current_filters)

def get_parser():
    ap = argparse.ArgumentParser()
    ap.set_defaults(filters=[])
    ap.add_argument("pngfile", type=str, help="PNG input file")
    
    # Filters
    filter_group = ap.add_argument_group("Filters")
    filter_group.add_argument("-t","--type", help="Filter by type",type=str, nargs="+",action=GenerateFilterAction)
    filter_group.add_argument("-i","--index", help="Filter by index",type=str, action=GenerateFilterAction)
    filter_group.add_argument("-s","--size", help="Filter by size",type=str, action=GenerateFilterAction)
    filter_group.add_argument("--text", help="Include only text chunks", type=str, action=GenerateFilterAction, nargs=0)
    filter_group.add_argument("--weird", help="Include non-specified chunks", type=str, action=GenerateFilterAction, nargs=0)
    
    # Which info to show
    present_group = ap.add_argument_group("Chunk info display")
    present_group.add_argument("--crc", help="Show chunk crc", default=False, action="store_true", dest="show_crc")
    present_group.add_argument("--length", help="Show chunk length", default=False, action="store_true", dest="show_length")
    present_group.add_argument("--raw", help="Only show chunk bytes", default=False, action="store_true", dest="only_raw")

    # Raw chunk bytes to file
    output_group = ap.add_argument_group("Output options")
    output_group.add_argument("-o","--output-file", help="Output file for chunk data", type=str, default=None, dest="file")
    
    # Chunk data with PNG header
    output_group.add_argument("-p","--output-png", help="Output PNG file", type=str, dest="pngout", default=None)
    
    # Raw chunk bytes to stdout
    output_group.add_argument("-", help="Output binary data to console", default=False, action="store_true",dest="to_stdout")
    
    # Fixing
    fix_options = ap.add_argument_group("Fixes")
    fix_options.add_argument("--brute-dim", help="Bruteforces dimensions based on known CRC", dest="brutedim",action="store_true", default=False)
    fix_options.add_argument("--recalc", help="Recalculates CRCs of PNG Chunks", dest="recalc",action="store_true", default=False)
    return ap

if __name__ == "__main__":
    parsed= get_parser().parse_args()
    print(parsed)
