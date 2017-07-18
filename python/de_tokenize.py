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
	write_to_file(new_lines, f)


def de_tokenize(f):
	new_lines = []
	for line in open(f, 'r'):
		
		while ' )' in line and '( ' in line:
			line = line.replace(' )',')').replace('( ','(')
		line = re.sub(r':op([\d]+) " ([a-zA-Z-_]+) "',r':op\1 "\2"', line) #change :op1 " name " back to :op1 "name"
		
		new_spl = []
		for idx, item in enumerate(line.split()):
			if item.startswith('-') and len(item) > 1:
				new_spl[-1] += item
			else:
				new_spl.append(item)
		
		line = " ".join(new_spl)			
			
		new_lines.append(line)
	
	write_to_file(new_lines, f)	
		

						
if __name__ == "__main__":
	for root, dirs, files in os.walk(args.f):
		for f in files:
			if f.endswith(args.extension) and 'char' not in f:
				f_path = os.path.join(root, f)
				all_text = " ".join([x for x in open(f_path,'r')])
				if all_text.count(' ) ') > 100 and all_text.count(' ( ') > 100 and 'Backups' not in f_path:
					print 'Processing {0}'.format(f_path)
					de_tokenize(f_path)
