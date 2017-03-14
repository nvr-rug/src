#!/usr/bin/env python

from sys import argv
import os
import codecs
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-d",required = True, type=str, help="folder that contains the amrs")
parser.add_argument("-out_folder",required = True, type=str, help="Output folder for the sentences")
parser.add_argument("-input_ext",required = False, default = ".sent", type=str, help="Input extension (default .sent)")
parser.add_argument("-extension",required = False, default = ".txt", type=str, help="AMR extension (default .txt)")
args = parser.parse_args()

'''Takes all AMR-files in a folder and extracts the sentences'''

def process_line(line):
    fields = line.split()
    if fields[0] == '#' and (fields[1] == '::snt' or fields[1] == '::tok'):
    #if fields[0] == '#' and (fields[1] == '::tok'):
        # Skip first (sent. id) and last (?) fields
        return ' '.join(fields[2:])

def process_file(in_path, out_path, fname):
    output = []
    with codecs.open(in_path, 'r') as in_f:
        for line in in_f:
            if len(line) <= 2: 
				continue
            result = process_line(line)
            if result:
                output.append(result)
                
    with codecs.open((out_path + fname).replace(args.extension, args.input_ext),'w') as out_f:
        for line in output:
            out_f.write(line + '\n')
        
    return output

if __name__ == '__main__':
    for root, dirs, files in os.walk(args.d):
        for fname in files:
            if fname.endswith(args.extension):
				f_path = os.path.join(root, fname)
				process_file(f_path, args.out_folder, fname.replace('alignments', 'amrs'))
