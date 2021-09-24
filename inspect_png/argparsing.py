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
    ap.add_argument("pngfile", type=str, help="PNG input file")
    
    # Filters
    filter_group = ap.add_argument_group("Filters")
    filter_group.add_argument("-t","--type", help="Filter by type",type=str, nargs="+",action=GenerateFilterAction)
    filter_group.add_argument("-i","--index", help="Filter by index",type=str, action=GenerateFilterAction)
    filter_group.add_argument("-s","--size", help="Filter by size",type=str, action=GenerateFilterAction)
    
    # Which info to show
    present_group = ap.add_argument_group("Chunk info")
    present_group.add_argument("--crc", help="Show chunk crc", default=False, action="store_true", dest="show_crc")
    present_group.add_argument("--length", help="Show chunk length", default=False, action="store_true", dest="show_length")
    present_group.add_argument("--raw", help="Only show chunk bytes", default=False, action="store_true", dest="only_raw")

    # Raw chunk data
    output_group = ap.add_argument_group("Output options")
    output_group.add_argument("-o","--output-file", help="Output file for chunk data", type=str, default=None, dest="file")
    
    # Chunk data with PNG header
    output_group.add_argument("-p","--output-png", help="Output PNG file", type=str, dest="pngout", default=None)
    
    # Raw chunk data
    output_group.add_argument("-", help="Output binary data to console", default=False, action="store_true",dest="to_stdout")
    
    # Fixing
    fix_options = ap.add_argument_group("Fixes")
    fix_options.add_argument("--brute-dim", help="Bruteforces dimensions based on known CRC", dest="brutedim",action="store_true", default=False)
    fix_options.add_argument("--recalc", help="Recalculates CRCs of PNG Chunks", dest="recalc",action="store_true", default=False)
    return ap

if __name__ == "__main__":
    parsed= get_parser().parse_args()
    print(parsed)
