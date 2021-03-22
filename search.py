#!/usr/bin/env python3
import mmap
import re
import argparse
import logging
import csv


def do_regex(args, pattern):
    with open(args.inputFilePath, 'r') as file_handle:
        with mmap.mmap(file_handle.fileno(), 0, access=mmap.ACCESS_READ) as mmap_handle:
            matches = getattr(pattern, args.action)(mmap_handle)
            if args.output_file and pattern.groups:
                do_csv(matches)
            else:
                do_print(matches)

def do_csv(matches):
    with open(args.output_file, 'w') as outfile_handle:
        cw = csv.DictWriter(outfile_handle, fieldnames=list(pattern.groupindex.keys()), delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        cw.writeheader()
        for match in matches:
            md = match.groupdict()
            for k, v in md.items():
                if v:
                    md[k] = v.decode()
            print(md)
            cw.writerow(md)

def clean_matches(matches):
    for match in matches:
        yield clean_match(match)

def clean_match(match):
    t = type(match)
    if t == tuple:
        m = [m.decode() for m in match]
        return m
    elif t == bytes:
        m = match.decode()
        return m
    elif t == re.Match:
        md = match.groupdict()
        for k, v in md.items():
            if v:
                md[k] = v.decode()
        return md
    else:
        return match


def do_print(matches):
    for match in clean_matches(matches):
        if args.template:
            print(args.template.format(**match))
        else:
            print(match)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--action', dest='action', default='findall', help='The action to perform with the regexp', choices=['findall', 'finditer'])
    parser.add_argument('-f', '--flags', action='append', default=['MULTILINE'], help='<Required> Set flag(s)', required=False, choices=['A', 'ASCII', 'DEBUG', 'I', 'IGNORECASE', 'L', 'LOCALE', 'M', 'MULTILINE', 'S', 'DOTALL', 'X', 'VERBOSE'])
    parser.add_argument('-o', '--output-file', help='Output file name')
    parser.add_argument('-t', '--template', type=str, help='Output template for printing named groups. "Your {named_group} is printed" ')
    parser.add_argument('inputFilePath', type=str, help='File to run regex on.')
    parser.add_argument('regex', type=str, help='Regular expression to run.')

    args = parser.parse_args()

    flags = 0
    for flag in args.flags:
        flags |= getattr(re, flag)
    
    if (args.output_file or args.template) and args.action == 'findall':
        args.action = 'finditer'

    pattern = re.compile(bytes(args.regex, 'utf-8'), flags)

    do_regex(args, pattern)