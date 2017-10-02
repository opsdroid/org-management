#!/bin/env python3

import sys, getopt

def parse_args(argv):
    args = {}
    inputfile = ''
    outputfile = ''
    try:
        opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
    except getopt.GetoptError:
        print 'test.py -i <inputfile> -o <outputfile>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'test.py -i <inputfile> -o <outputfile>'
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-o", "--ofile"):
            outputfile = arg
    print 'Input file is "', inputfile
    print 'Output file is "', outputfile

    return args

def load_tags():
    pass

def get_repos():
    pass

def update_tags(tags):
    pass

def main(argv):
    parse_args(argv)
    
    tags = load_tags()
    repos = get_repos()
    for repo in repos:
        update_tags(tags)

if __name__ == '__main__':
    main(sys.argv[1:])