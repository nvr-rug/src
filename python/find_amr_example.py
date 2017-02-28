#!/usr/bin/env python

import os
import re
import sys
import argparse

'''Script lets you find good AMR examples'''

parser = argparse.ArgumentParser()
parser.add_argument('-f', required=True, type=str, help="AMR file")
parser.add_argument('-l', required=True, type=int, help="Max AMR len")

args = parser.parse_args()


def print_matching_amrs(input_f, max_lines):    
	cur_amr = []
	has_content = False
	var_present = False
	
	for line in open(input_f,'r'):
		if line.strip() == "":
			if not has_content:
				continue
			else: 
				if (len(cur_amr) <= max_lines) and var_present:
					print cur_sent
					for c in cur_amr:
						print c
					print '\n\n'
				cur_amr = []
				has_content = False
				var_present = False
				continue
		if line.strip().startswith("#"):
			if line.strip().startswith('# ::snt'):
				cur_sent = line.replace('# ::snt','').strip()
			continue
		else:
			has_content = True
			cur_amr.append(line.rstrip())
			if '/' not in line:
				var_present = True
	
if __name__ == '__main__':
	print_matching_amrs(args.f, args.l)
