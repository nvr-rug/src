#!/usr/bin/env python
# -*- coding: utf8 -*-

import sys
import re
import argparse
import os

'''Script that puts AMR-files in word-level input'''

parser = argparse.ArgumentParser()
parser.add_argument("-f", required=True, type=str, help="directory that contains the amrs")
parser.add_argument('-extension', required = False, default = '.tf', help="extension of AMR files (default .tf)")
parser.add_argument('-output_ext', required = False, default = '.char.tf', help="ext of output (default .char.tf")
args = parser.parse_args()


def write_to_file(l, f):
	with open(f,'w') as out_f:
		for line in l:
			out_f.write(line.strip() + '\n')
	out_f.close()


def process_file(f):
	new_lines = []
	for line in open(f, 'r'):
		split_l = line.replace(')',' ) ').replace('(',' ( ').replace('"',' " ').replace("'"," ' ").split()
		new_split = []
		for l in split_l:
			if '-' in l and 'http' not in l and 'www' not in l and l.count('-') == 1:	#find words with dashes but don't do websites
				l = l.replace('-',' -').split()
				for item in l:
					new_split.append(item)
			else:
				new_split.append(l)
		
		new_l = " ".join(new_split)
		new_lines.append(new_l)
	
	out_f = f.replace(args.extension, args.output_ext)
	write_to_file(new_lines, out_f)


						
if __name__ == "__main__":
	for root, dirs, files in os.walk(args.f):
		for f in files:
			if f.endswith(args.extension) and 'char' not in f:
				f_path = os.path.join(root, f)
				print 'Processing {0}\n'.format(f_path)
				process_file(f_path)
			
